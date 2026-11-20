"""Bounded stateful ROSA baseline and cache experiments, with an independent oracle."""
import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time
from uuid import uuid4
from urllib.request import ProxyHandler, Request, build_opener

from .config import ROOT, checkout, phoenix_project, run_dir
from .tracing import trace_run


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['scripted', 'ollama', 'siwc'], required=True)
    parser.add_argument('--suite', choices=['smoke', 'pilot', 'full'], default='pilot')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--policies', nargs='+', choices=['none', 'ttl', 'conservative'], default=['none', 'ttl', 'conservative'])
    parser.add_argument('--model')
    parser.add_argument('--request-budget', type=int, default=1200)
    parser.add_argument('--trial-seconds', type=int, default=240)
    parser.add_argument('--wall-seconds', type=int, default=7200)
    parser.add_argument('--timeout', type=int, default=900, help='Browser consent deadline')
    parser.add_argument('--tracing', choices=['on', 'off'], default='on')
    args = parser.parse_args()
    if not 1 <= args.repeats <= 10 or not 1 <= args.request_budget <= 2000:
        parser.error('Repetitions must be 1..10 and request budget 1..2000')
    sys.path.insert(0, str(checkout('research') / 'src'))
    from langchain_core.callbacks import BaseCallbackHandler
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends import create_model, create_mock_agent
    from rosa_auth.oauth import SafeError
    from rosa_auth.responses import SiwcBackend
    from rosa_auth.session import interactive_session
    from .stateful.bridge import WorldClient
    from .stateful.metrics import summarize
    from .stateful.scenarios import FAMILIES, engineering_pilot, manifest_hash, suite
    from .stateful.tools import INSTRUCTIONS, make_tools, scripted_policy

    for name in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[name] = 'false'
    batch_id = str(uuid4())
    destination = run_dir(batch_id)
    destination.mkdir(parents=True)
    fixtures = suite() if args.suite == 'full' else engineering_pilot()
    if args.suite == 'smoke':
        fixtures = [s for s in fixtures if s['variant'] == 0]
    plan = []
    for repetition in range(args.repeats):
        order = list(fixtures)
        random.Random(20261021 + repetition).shuffle(order)
        for spec in order:
            # All families get an unaided baseline. Live cache crossover is
            # limited to read/transfer families; scripted stress tests cover all.
            policies = list(args.policies)
            if args.backend != 'scripted' and spec['family'] not in ('repeat_read', 'transfer'):
                policies = [p for p in policies if p == 'none']
            shift = (repetition + spec['variant']) % max(1, len(policies))
            policies = policies[shift:] + policies[:shift]
            plan.extend((spec, repetition, policy) for policy in policies)
    source_hashes = {}
    for directory in (ROOT / 'experiments', checkout('research') / 'src'):
        for path in sorted(directory.rglob('*.py')):
            source_hashes[str(path.relative_to(ROOT.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    source_hashes['experiments/benchmark.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol = {'batch_id': batch_id, 'created_at': datetime.now(timezone.utc).isoformat(),
        'backend': args.backend, 'suite': args.suite, 'repeats': args.repeats,
        'manifest_sha256': manifest_hash(), 'source_sha256': source_hashes,
        'planned_trials': len(plan), 'request_budget': args.request_budget,
        'trial_request_budget': 14, 'trial_seconds': args.trial_seconds, 'wall_seconds': args.wall_seconds,
        'num_ctx': 8192, 'num_predict': 256, 'ttl_simulation_ticks': 5,
        'memory': False, 'jtvr': False, 'sampling_comparability': 'backend-specific settings recorded',
        'statistical_scope': 'engineering pilot; reserved templates are not independently authored held-out families',
        'inference_history': 'fresh ROSA agent per trial; provider prompt/KV caching remains backend-managed',
        'planned_trial_keys': [[s['id'], r, p] for s, r, p in plan]}
    (destination / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    (destination / 'scenario-manifest.json').write_text(json.dumps(suite(), indent=2) + '\n')
    report = {'batch_id': batch_id, 'status': 'RUNNING', 'protocol': protocol, 'trials': []}
    total_calls = 0
    total_tokens = 0
    inference_start = None
    llm = transport = None

    def save():
        report['summary'] = summarize(report['trials'])
        report['total_model_calls'] = total_calls
        report['total_reported_tokens'] = total_tokens
        (destination / 'result.json').write_text(json.dumps(report, indent=2) + '\n')

    class Meter(BaseCallbackHandler):
        raise_error = True

        def __init__(self):
            self.calls = self.input_tokens = self.output_tokens = 0
            self.elapsed_ms = 0
            self.started = None
            self.tool_errors = 0
            self.truncated_generations = 0

        def on_chat_model_start(self, serialized, messages, **kwargs):
            nonlocal total_calls
            if self.calls >= 14 or total_calls >= args.request_budget:
                raise SafeError('benchmark_request_budget_exceeded')
            if time.monotonic() - inference_start > args.wall_seconds:
                raise SafeError('benchmark_wall_budget_exceeded')
            self.calls += 1
            total_calls += 1
            self.started = time.perf_counter()

        def on_llm_end(self, response, **kwargs):
            nonlocal total_tokens
            if self.started is not None:
                self.elapsed_ms += (time.perf_counter() - self.started) * 1000
                self.started = None
            for group in response.generations:
                for generation in group:
                    message = getattr(generation, 'message', None)
                    usage = getattr(message, 'usage_metadata', None) or {}
                    self.input_tokens += usage.get('input_tokens', 0)
                    self.output_tokens += usage.get('output_tokens', 0)
                    total_tokens += usage.get('total_tokens', 0)
                    metadata = getattr(message, 'response_metadata', {}) or {}
                    if metadata.get('done_reason') == 'length':
                        self.truncated_generations += 1

        def on_llm_error(self, error, **kwargs):
            if self.started is not None:
                self.elapsed_ms += (time.perf_counter() - self.started) * 1000
                self.started = None

        def on_tool_error(self, error, **kwargs):
            self.tool_errors += 1

        def evidence(self):
            return {key: getattr(self, key) for key in ('calls', 'input_tokens', 'output_tokens',
                    'elapsed_ms', 'tool_errors', 'truncated_generations')}

    def alarm(signum, frame):
        raise TimeoutError('trial_wall_deadline_exceeded')

    save()
    print(f'Batch: {batch_id}; planned trials: {len(plan)}\nReport: {destination / "result.json"}', flush=True)
    context = (interactive_session(request_budget=args.request_budget, timeout=args.timeout, status=report)
               if args.backend == 'siwc' else nullcontext(None))
    try:
        with context as session:
            if args.backend == 'siwc':
                transport = SiwcBackend(request_budget=args.request_budget, token_provider=session.access_token)
                catalog = transport.models()
                model = args.model or (catalog[0]['slug'] if catalog else None)
                if model not in {item['slug'] for item in catalog}:
                    raise SafeError('requested_model_not_in_account_catalog')
                llm = create_model('siwc', model=model, siwc_transport=transport)
                report['model'] = model
                report['model_settings'] = {'stream': True, 'store': False, 'sampling': 'model defaults'}
            elif args.backend == 'ollama':
                model = args.model or os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
                base_url = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
                llm = create_model('ollama', model=model, base_url=base_url, num_ctx=8192, use_mmap=True)
                opener = build_opener(ProxyHandler({}))
                with opener.open(Request(base_url + '/api/tags'), timeout=10) as response:
                    installed = next(item for item in json.load(response)['models'] if item['name'] == model)
                report['model'] = model
                report['model_digest'] = installed['digest']
                report['model_settings'] = {'num_ctx': 8192, 'num_predict': 256, 'temperature': 0,
                                             'seed': 42, 'reasoning': False, 'use_mmap': True, 'base_url': base_url}
            else:
                report['model'] = 'scripted-public-observation-policy'
            inference_start = time.monotonic()
            for index, (spec, repetition, policy) in enumerate(plan):
                if (total_calls >= args.request_budget or time.monotonic() - inference_start > args.wall_seconds):
                    report['status'] = 'BUDGET_EXHAUSTED'
                    break
                trial_id = str(uuid4())
                trial_path = run_dir(trial_id)
                trial_path.mkdir(parents=True)
                metadata = {'run_id': trial_id, 'batch_id': batch_id, 'backend': args.backend,
                            'model': report['model'], 'scenario_id': spec['id'], 'policy': policy,
                            'repetition': repetition, 'mode': 'stateful-engineering-pilot'}
                meter = Meter()
                if llm is not None:
                    llm.callbacks = [meter]
                started = time.perf_counter()
                answer = ''
                error_type = None
                with WorldClient(spec, policy) as world:
                    with trace_run(args.tracing == 'on', project=phoenix_project(), metadata=metadata) as span:
                        try:
                            if llm is None:
                                scripted_policy(world, {key: spec[key] for key in ('query', 'object_id', 'target')})
                                answer = 'Scripted public-observation policy completed.'
                            else:
                                tools = make_tools(world.call)
                                prompts = RobotSystemPrompts(critical_instructions=INSTRUCTIONS)
                                agent = create_mock_agent(llm, tools, max_iterations=14, prompts=prompts)
                                signal.signal(signal.SIGALRM, alarm)
                                signal.setitimer(signal.ITIMER_REAL, args.trial_seconds)
                                try:
                                    answer = agent.invoke(spec['query'])
                                finally:
                                    signal.setitimer(signal.ITIMER_REAL, 0)
                        except Exception as error:
                            error_type = type(error).__name__
                        evidence = world.score()
                        failed = bool(error_type or not answer or answer.startswith('An error occurred:') or
                                      answer == 'Agent stopped due to max iterations.')
                        row = {'run_id': trial_id, 'scenario_id': spec['id'], 'family': spec['family'],
                            'split': spec['split'], 'repetition': repetition, 'policy': policy,
                            'answer': answer, 'api_failed': failed, 'local_error_type': error_type,
                            'wall_seconds': time.perf_counter() - started, 'score': evidence['score'],
                            'model_metrics': meter.evidence(), 'model_visible_tool_names': sorted(tool.name for tool in make_tools(world.call)),
                            'query': spec['query']}
                        if span is not None:
                            row['trace_id'] = format(span.get_span_context().trace_id, '032x')
                            span.set_attribute('input.value', spec['query'])
                            span.set_attribute('output.value', answer)
                            if failed:
                                from opentelemetry.trace import Status, StatusCode
                                span.set_status(Status(StatusCode.ERROR, 'benchmark_model_or_framework_failure'))
                    (trial_path / 'oracle.json').write_text(json.dumps(evidence, indent=2) + '\n')
                    (trial_path / 'result.json').write_text(json.dumps(row, indent=2) + '\n')
                    (trial_path / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
                report['trials'].append(row)
                save()
                print(f'{index + 1}/{len(plan)} {spec["id"]} r{repetition} {policy}: '
                      f'handling={row["score"]["correct_terminal_handling"]} goal={row["score"]["verified_task_success"]} '
                      f'api_failed={failed} calls={meter.calls}', flush=True)
                if (args.backend == 'siwc' and answer.startswith('An error occurred:') and
                        any(code in answer for code in ('subscription_sharing_', 'invalid_grant', 'invalid_token'))):
                    report['status'] = 'PROVIDER_BLOCKED'
                    break
            else:
                report['status'] = 'COMPLETE'
            if session is not None:
                report['refresh_count'] = session.refresh_count
    except KeyboardInterrupt:
        report['status'] = 'INTERRUPTED'
    except SafeError as error:
        report['status'] = 'FAIL'
        report['error'] = {'code': error.code, 'http_status': error.status}
    except Exception as error:
        report['status'] = 'FAIL'
        report['error'] = {'type': type(error).__name__}
    finally:
        if args.backend == 'siwc' and llm is not None:
            (destination / 'requests.json').write_text(json.dumps(llm.request_records, indent=2) + '\n')
            llm.close()
        elif transport is not None:
            transport.close()
        save()
        print(f'{report["status"]}: {destination / "result.json"}', flush=True)
    return 0 if report['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
