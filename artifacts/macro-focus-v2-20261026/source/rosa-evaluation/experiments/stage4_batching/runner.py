"""One consent scope, bounded reliability and actual ROSA batching comparisons."""
import argparse
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import time
from uuid import uuid4

from ..config import ROOT, phoenix_project
from ..tracing import trace_run
from .tasks import batching_jobs, reliability_jobs, INSTRUCTIONS

CAMPAIGN = ROOT / 'artifacts/stage4-batching-completion-20261021'
REQUEST_CAP = 1056
PROJECT = 'rosa-stage4-batching-20261021'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', required=True, choices=('ollama', 'siwc'))
    args = parser.parse_args()
    from .protocol import verify
    verify()
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    for variable in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[variable] = 'false'
    from langchain_core.callbacks import BaseCallbackHandler
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends import create_model, create_mock_agent
    from rosa_auth.oauth import SafeError
    from rosa_auth.responses import SiwcBackend
    from rosa_auth.session import interactive_session
    from ..phase4.client import Client, InterventionStop
    from ..phase4.tools import make_tools as reliability_tools, instructions
    from .gateway import Gateway, make_tools
    from .environment import RealEnvironment
    destination = CAMPAIGN / args.backend
    destination.mkdir(exist_ok=False)
    status = {'backend': args.backend, 'status': 'STARTING', 'request_cap': REQUEST_CAP,
              'planned_trials': 80, 'trials': [], 'started_utc': datetime.now(timezone.utc).isoformat()}
    total_calls = total_tokens = 0
    inference_start = None
    llm = transport = environment = None

    def save():
        status.update(total_model_calls=total_calls, total_reported_tokens=total_tokens,
                      completed_trials=len(status['trials']), updated_utc=datetime.now(timezone.utc).isoformat())
        temporary = destination / 'status.tmp'
        temporary.write_text(json.dumps(status, indent=2) + '\n')
        temporary.replace(destination / 'result.json')

    class Meter(BaseCallbackHandler):
        raise_error = True

        def __init__(self, cap):
            self.cap = cap
            self.calls = self.input_tokens = self.output_tokens = self.tool_dispatches = self.truncated = self.tool_errors = 0
            self.elapsed_ms = 0.0
            self.raw_tool_calls = []
            self.started = None

        def on_chat_model_start(self, serialized, messages, **kwargs):
            nonlocal total_calls
            if self.calls >= self.cap or total_calls >= REQUEST_CAP or time.monotonic() - inference_start > 21600:
                raise SafeError('stage4_request_or_wall_cap_exceeded')
            self.calls += 1
            total_calls += 1
            self.started = time.perf_counter()

        def finish(self):
            if self.started is not None:
                self.elapsed_ms += (time.perf_counter() - self.started) * 1000
                self.started = None

        def on_llm_end(self, response, **kwargs):
            nonlocal total_tokens
            self.finish()
            for generations in response.generations:
                for generation in generations:
                    message = getattr(generation, 'message', None)
                    self.raw_tool_calls.extend(deepcopy(getattr(message, 'tool_calls', None) or []))
                    usage = getattr(message, 'usage_metadata', None) or {}
                    self.input_tokens += usage.get('input_tokens', 0)
                    self.output_tokens += usage.get('output_tokens', 0)
                    total_tokens += usage.get('total_tokens', 0)
                    self.truncated += int((getattr(message, 'response_metadata', None) or {}).get('done_reason') == 'length')

        def on_llm_error(self, error, **kwargs):
            self.finish()

        def on_tool_start(self, serialized, input_str, **kwargs):
            self.tool_dispatches += 1

        def on_tool_error(self, error, **kwargs):
            self.tool_errors += 1

        def metrics(self):
            return {k: getattr(self, k) for k in ('calls', 'input_tokens', 'output_tokens',
                     'tool_dispatches', 'truncated', 'tool_errors', 'elapsed_ms')}

    def deadline(*_):
        raise TimeoutError('trial_240_second_deadline')

    save()
    scope = interactive_session(request_budget=REQUEST_CAP, timeout=3600, status=status) if args.backend == 'siwc' else nullcontext(None)
    try:
        with scope as session:
            if session:
                transport = SiwcBackend(request_budget=REQUEST_CAP, token_provider=session.access_token)
                model = 'gpt-6.1-sol'
                if model not in {m['slug'] for m in transport.models()}:
                    raise SafeError('requested_model_not_in_account_catalog')
                llm = create_model('siwc', model=model, siwc_transport=transport)
                status['model_settings'] = {'stream': True, 'store': False, 'sampling': 'account defaults'}
            else:
                model = 'qwen3.5:9b'
                endpoint = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
                llm = create_model('ollama', model=model, base_url=endpoint, num_ctx=8192, use_mmap=True)
                status['model_settings'] = {'num_ctx': 8192, 'num_predict': 256, 'temperature': 0,
                    'seed': 42, 'reasoning': False, 'use_mmap': True, 'base_url': endpoint}
            status.update(model=model, status='RUNNING')
            inference_start = time.monotonic()
            jobs = reliability_jobs() + batching_jobs()
            for index, job in enumerate(jobs):
                spec = job['spec']
                if total_calls >= REQUEST_CAP or time.monotonic() - inference_start > 21600:
                    status['status'] = 'BUDGET_EXHAUSTED'
                    break
                if job['stage'] == 'batching' and environment is None:
                    environment = RealEnvironment(destination / 'ros', 174 if args.backend == 'siwc' else 175)
                    environment.start()
                if environment is not None and job['stage'] == 'batching':
                    environment.reset(spec)
                run_id = str(uuid4())
                folder = destination / 'trials' / run_id
                folder.mkdir(parents=True)
                metadata = {'run_id': run_id, 'campaign': CAMPAIGN.name, 'backend': args.backend,
                    'model': model, 'stage': job['stage'], 'policy': job['policy'],
                    'intervention': job['intervention'], 'scenario_id': spec['id'],
                    'repetition': job['repetition']}
                meter = Meter(14 if job['stage'] == 'reliability' else 12)
                llm.callbacks = [meter]
                context = Client(spec, 'none', job['intervention'], True) if job['stage'] == 'reliability' else nullcontext(None)
                answer, error_type, recovered = '', None, False
                with context as client:
                    if client:
                        tools = reliability_tools(client.call, 'none', True)
                        critical = instructions(job['intervention'], True)
                    else:
                        costs = json.loads((ROOT / 'artifacts/stage4-policy-20261021/ros-calibration/calibration.json').read_text())['cost_seconds']
                        gateway = Gateway(spec, job['policy'], environment.invoke, costs)
                        tools = make_tools(gateway.call)
                        critical = INSTRUCTIONS
                        native_start = len(environment.commands)
                    for tool in tools:
                        tool.callbacks = [meter]
                    started = time.perf_counter()
                    with trace_run(True, project=PROJECT, metadata=metadata) as span:
                        signal.signal(signal.SIGALRM, deadline)
                        signal.setitimer(signal.ITIMER_REAL, 240)
                        try:
                            if not client and spec['warm_type']:
                                from ..jtvr_policy.core import Action
                                for node in spec['groups']:
                                    gateway.native(Action('info', node), 'charged_warmup')
                            agent = create_mock_agent(llm, tools, max_iterations=meter.cap,
                                prompts=RobotSystemPrompts(critical_instructions=critical))
                            answer = agent.invoke(spec['query'])
                        except InterventionStop:
                            recovered = True
                            answer = 'Orchestrator stopped repetition and submitted its attributed report.'
                        except Exception as error:
                            error_type = type(error).__name__
                        finally:
                            signal.setitimer(signal.ITIMER_REAL, 0)
                        wall_seconds = time.perf_counter() - started
                        if client:
                            evidence = client.score(meter.raw_tool_calls)
                            strict = evidence['contract']['strict_contract_pass']
                        else:
                            oracle = environment.oracle(spec)
                            evidence = gateway.score(oracle, meter.raw_tool_calls)
                            strict = evidence['strict_contract_pass']
                        failed = bool(error_type or not answer or answer.startswith('An error occurred:') or answer == 'Agent stopped due to max iterations.')
                        row = {**metadata, 'answer': answer, 'api_failed': failed, 'error_type': error_type,
                            'orchestrator_recovery': recovered, 'strict_contract_pass': strict,
                            'combined_pass': strict and not failed, 'wall_seconds': wall_seconds,
                            'model_metrics': meter.metrics(), 'raw_model_tool_calls': meter.raw_tool_calls,
                            'model_visible_tool_names': [t.name for t in tools], 'query': spec['query']}
                        if client:
                            row.update(family=spec['family'], score=evidence['score'], contract=evidence['contract'])
                        else:
                            commands = environment.commands[native_start:]
                            row.update(template=spec['template'], cli_commands=len(commands),
                                server_rpcs=sum(len(c['server_rpcs']) for c in commands),
                                native_seconds=sum(c['seconds'] for c in commands),
                                selector_seconds=gateway.selector_seconds, manifest_requests=evidence['manifest_requests'],
                                valid_manifests=evidence['valid_manifests'], manifest_bypassed=evidence['manifest_bypassed'],
                                first_manifest_valid=evidence['first_manifest_valid'], native_commands=commands)
                        span.set_attribute('input.value', spec['query'])
                        span.set_attribute('output.value', answer)
                        row['trace_id'] = format(span.get_span_context().trace_id, '032x')
                    for name, data in (('result', row), ('evidence', evidence)):
                        (folder / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n')
                status['trials'].append(row)
                save()
                print(f"{index + 1}/80 {job['stage']} {spec['id']} {job['intervention']}/{job['policy']}: strict={strict} api_failed={failed} calls={meter.calls}", flush=True)
            else:
                status['status'] = 'COMPLETE'
            if session:
                status['refresh_count'] = session.refresh_count
    except KeyboardInterrupt:
        status['status'] = 'INTERRUPTED'
    except SafeError as error:
        status.update(status='FAILED', safe_error_code=error.code)
    except BaseException as error:
        status.update(status='FAILED', error_type=type(error).__name__)
        raise
    finally:
        if environment:
            environment.close()
        if args.backend == 'siwc' and llm is not None:
            (destination / 'requests.json').write_text(json.dumps(llm.request_records, indent=2))
            llm.close()
        elif transport:
            transport.close()
        status['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    return 0 if status['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
