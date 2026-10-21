"""Bounded v2 experiment runner; shares the actual ROSA executor and backend factory."""
import argparse
from copy import deepcopy
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import time
from uuid import uuid4
from ..config import ROOT, run_dir, phoenix_project
from ..tracing import trace_run
from .client import Client, InterventionStop
from .scenarios import suite, feature_subset, digest

CAMPAIGN = ROOT.parent / 'reports/phase4-v2'


def plan(scripted=False):
    from ..stateful.scenarios import suite as legacy_suite
    reliability = [s for s in legacy_suite() if s['family'] in ('transfer', 'accepted_failure', 'missing_sensor') and s['variant'] in (0, 1)]
    result = []
    for index, spec in enumerate(reliability):
        arms = ['original', 'clarified', 'bounded_recovery', 'enforce_verification']
        arms = arms[index % 4:] + arms[:index % 4]
        result.extend({'stage': 'reliability', 'spec': spec, 'policy': 'none', 'intervention': arm, 'legacy': True} for arm in arms)
    fixtures = suite()
    random.Random(20261022).shuffle(fixtures)
    selected = {s['id'] for s in feature_subset(fixtures)}
    for index, spec in enumerate(fixtures):
        policies = ['none', 'conservative', 'eager', 'jtvr'] if scripted or spec['id'] in selected else ['none']
        shift = index % len(policies)
        policies = policies[shift:] + policies[:shift]
        result.extend({'stage': 'information' if policy != 'none' else 'new_baseline',
                       'spec': spec, 'policy': policy, 'intervention': 'original', 'legacy': False} for policy in policies)
    return result


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    from langchain_core.callbacks import BaseCallbackHandler
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends import create_model, create_mock_agent
    from rosa_auth.oauth import SafeError
    from rosa_auth.responses import SiwcBackend
    from rosa_auth.session import interactive_session
    from .tools import make_tools, instructions, scripted
    from ..stateful.tools import scripted_policy as legacy_scripted
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['scripted', 'ollama', 'siwc'], required=True)
    parser.add_argument('--trial-seconds', type=int, default=240)
    parser.add_argument('--wall-seconds', type=int, default=21600)
    parser.add_argument('--request-budget', type=int, default=1680)
    parser.add_argument('--model')
    args = parser.parse_args()
    if args.trial_seconds != 240 or args.request_budget != 1680:
        parser.error('This frozen protocol requires 240 seconds/trial and 1680 requests/backend')
    frozen = json.loads((CAMPAIGN / 'freeze.json').read_text())
    for relative, expected in frozen['source_sha256'].items():
        if hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Frozen source changed: {relative}')
    fixtures = suite()
    if digest(fixtures) != frozen['manifest_sha256']:
        raise RuntimeError('Frozen manifest changed')
    for name in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[name] = 'false'
    jobs = plan(args.backend == 'scripted')
    batch_id = str(uuid4())
    destination = run_dir(batch_id)
    destination.mkdir(parents=True)
    report = {'batch_id': batch_id, 'status': 'RUNNING', 'backend': args.backend,
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'protocol': {'version': 'phase4-v2', 'planned_trials': len(jobs), 'manifest_sha256': digest(fixtures),
                           'freeze_sha256': hashlib.sha256((CAMPAIGN / 'freeze.json').read_bytes()).hexdigest(),
                           'request_budget': 1680, 'trial_seconds': 240, 'model_calls_per_trial': 14,
                           'wall_seconds': args.wall_seconds, 'fresh_agent_world_cache_each_trial': True,
                           'provider_kv_cache_reset_per_trial': False, 'memory_enabled': False},
              'planned_trials': [{'scenario_id': j['spec']['id'], **{k: j[k] for k in ('stage', 'policy', 'intervention')}} for j in jobs],
              'trials': []}
    (destination / 'scenario-manifest.json').write_text(json.dumps(fixtures, indent=2) + '\n')
    total_calls = total_tokens = 0
    inference_start = None
    llm = transport = None

    def save():
        report.update(total_model_calls=total_calls, total_reported_tokens=total_tokens)
        (destination / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        CAMPAIGN.mkdir(parents=True, exist_ok=True)
        (CAMPAIGN / f'{args.backend}-batch.json').write_text(json.dumps({'batch_id': batch_id, 'result': str(destination / 'result.json'),
            'status': report['status'], 'completed': len(report['trials']), 'planned': len(jobs)}, indent=2) + '\n')

    class Meter(BaseCallbackHandler):
        raise_error = True

        def __init__(self):
            self.calls = self.input_tokens = self.output_tokens = self.truncated = self.tool_errors = 0
            self.elapsed_ms = 0.0
            self.started = None
            self.max_input_tokens = 0
            self.tool_dispatches = 0
            self.raw_tool_calls = []

        def on_chat_model_start(self, serialized, messages, **kwargs):
            nonlocal total_calls
            if self.calls >= 14 or total_calls >= 1680 or time.monotonic() - inference_start > args.wall_seconds:
                raise SafeError('phase4_request_or_wall_budget_exceeded')
            self.calls += 1
            total_calls += 1
            self.started = time.perf_counter()

        def on_llm_end(self, response, **kwargs):
            nonlocal total_tokens
            self.finish()
            for group in response.generations:
                for generation in group:
                    message = getattr(generation, 'message', None)
                    self.raw_tool_calls.extend(deepcopy(getattr(message, 'tool_calls', None) or []))
                    usage = getattr(message, 'usage_metadata', None) or {}
                    self.input_tokens += usage.get('input_tokens', 0)
                    self.output_tokens += usage.get('output_tokens', 0)
                    self.max_input_tokens = max(self.max_input_tokens, usage.get('input_tokens', 0))
                    total_tokens += usage.get('total_tokens', 0)
                    self.truncated += int((getattr(message, 'response_metadata', None) or {}).get('done_reason') == 'length')

        def finish(self):
            if self.started is not None:
                self.elapsed_ms += (time.perf_counter() - self.started) * 1000
                self.started = None

        def on_llm_error(self, error, **kwargs):
            self.finish()

        def on_tool_error(self, error, **kwargs):
            self.tool_errors += 1

        def on_tool_start(self, serialized, input_str, **kwargs):
            self.tool_dispatches += 1

        def evidence(self):
            return {k: getattr(self, k) for k in ('calls', 'input_tokens', 'output_tokens', 'elapsed_ms', 'max_input_tokens', 'truncated', 'tool_errors', 'tool_dispatches')}

    def alarm(*_):
        raise TimeoutError('trial_wall_deadline_exceeded')

    save()
    print(f'Phase 4 batch {batch_id}; {len(jobs)} trials; result {destination / "result.json"}', flush=True)
    scope = interactive_session(request_budget=1680, timeout=1800, status=report) if args.backend == 'siwc' else nullcontext(None)
    try:
        with scope as session:
            if args.backend == 'siwc':
                transport = SiwcBackend(request_budget=1680, token_provider=session.access_token)
                catalog = transport.models()
                model = args.model or 'gpt-6.1-sol'
                if model not in {m['slug'] for m in catalog}:
                    raise SafeError('requested_model_not_in_account_catalog')
                llm = create_model('siwc', model=model, siwc_transport=transport)
                report['model_settings'] = {'stream': True, 'store': False, 'sampling': 'account model defaults'}
            elif args.backend == 'ollama':
                model = args.model or os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
                endpoint = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
                llm = create_model('ollama', model=model, base_url=endpoint, num_ctx=8192, use_mmap=True)
                report['model_settings'] = {'num_ctx': 8192, 'num_predict': 256, 'temperature': 0, 'seed': 42,
                                          'reasoning': False, 'use_mmap': True, 'base_url': endpoint}
            else:
                model = 'public-observation-deterministic-planner'
            report['model'] = model
            inference_start = time.monotonic()
            for index, job in enumerate(jobs):
                if total_calls >= 1680 or time.monotonic() - inference_start > args.wall_seconds:
                    report['status'] = 'BUDGET_EXHAUSTED'
                    break
                spec = job['spec']
                trial_id = str(uuid4())
                folder = run_dir(trial_id)
                folder.mkdir(parents=True)
                metadata = {'run_id': trial_id, 'batch_id': batch_id, 'backend': args.backend, 'model': model,
                            'scenario_id': spec['id'], **{k: job[k] for k in ('stage', 'policy', 'intervention')}}
                meter = Meter()
                if llm is not None:
                    llm.callbacks = [meter]
                answer, error_type, recovered = '', None, False
                started = time.perf_counter()
                with Client(spec, job['policy'], job['intervention'], job['legacy']) as client:
                    tools = make_tools(client.call, job['policy'], job['legacy'])
                    for tool in tools:
                        tool.callbacks = [meter]
                    with trace_run(llm is not None, project=phoenix_project(), metadata=metadata) as span:
                        signal.signal(signal.SIGALRM, alarm)
                        signal.setitimer(signal.ITIMER_REAL, 240)
                        try:
                            if llm is None:
                                public = {k: spec[k] for k in ('query', 'object_id', 'target')}
                                (legacy_scripted if job['legacy'] else scripted)(client, public)
                                answer = 'Deterministic public-observation planner completed.'
                            else:
                                agent = create_mock_agent(llm, tools, max_iterations=14,
                                    prompts=RobotSystemPrompts(critical_instructions=instructions(job['intervention'], job['legacy'])))
                                answer = agent.invoke(spec['query'])
                        except InterventionStop:
                            recovered = True
                            answer = 'Orchestrator stopped repetition and submitted its own attributed report.'
                        except Exception as error:
                            error_type = type(error).__name__
                        finally:
                            signal.setitimer(signal.ITIMER_REAL, 0)
                        evidence = client.score(meter.raw_tool_calls if llm is not None else None)
                        failed = bool(error_type or not answer or answer.startswith('An error occurred:') or answer == 'Agent stopped due to max iterations.')
                        row = {**metadata, 'family': spec['family'], 'split': spec['split'], 'answer': answer,
                               'api_failed': failed, 'local_error_type': error_type, 'orchestrator_recovery': recovered,
                               'wall_seconds': time.perf_counter() - started, 'score': evidence['score'],
                               'contract': evidence['contract'], 'model_metrics': meter.evidence(),
                               'model_dispatches': client.dispatches, 'model_visible_tool_names': sorted(t.name for t in tools),
                               'raw_model_tool_calls': meter.raw_tool_calls,
                               'query': spec['query']}
                        if span is not None:
                            row['trace_id'] = format(span.get_span_context().trace_id, '032x')
                            span.set_attribute('input.value', spec['query'])
                            span.set_attribute('output.value', answer)
                    for name, data in (('result', row), ('oracle', evidence), ('metadata', metadata)):
                        (folder / f'{name}.json').write_text(json.dumps(data, indent=2) + '\n')
                report['trials'].append(row)
                save()
                print(f'{index + 1}/{len(jobs)} {job["stage"]} {spec["id"]} {job["intervention"]}/{job["policy"]}: '
                      f'strict={evidence["contract"]["strict_contract_pass"]} operational_failure={failed} calls={meter.calls}', flush=True)
                if args.backend == 'siwc' and any(code in answer for code in ('subscription_sharing_', 'invalid_token', 'invalid_grant')):
                    report['status'] = 'PROVIDER_BLOCKED'
                    break
            else:
                report['status'] = 'COMPLETE'
            if session is not None:
                report['refresh_count'] = session.refresh_count
    except KeyboardInterrupt:
        report['status'] = 'INTERRUPTED'
    except SafeError as error:
        report.update(status='FAIL', error={'code': error.code, 'http_status': error.status})
    except Exception as error:
        report.update(status='FAIL', error={'type': type(error).__name__})
    finally:
        if args.backend == 'siwc' and llm is not None:
            (destination / 'requests.json').write_text(json.dumps(llm.request_records, indent=2) + '\n')
            llm.close()
        elif transport is not None:
            transport.close()
        report['ended_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(f'{report["status"]}: {destination / "result.json"}', flush=True)
    return 0 if report['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
