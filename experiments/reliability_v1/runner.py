"""Bounded actual ROSA comparison; frozen prospectively, no automatic reruns."""
import argparse
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import time
from uuid import uuid4

from .cases import ARMS, INSTRUCTIONS, MemoryTransport, jobs, gazebo_jobs
from .tracing import trace_trial, audit

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'artifacts/reliability-v1-20261022'


def write(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def verify_freeze():
    manifest = json.loads((DESTINATION / 'freeze.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('prospective_source_changed: ' + name)
    return manifest


def run_scripted():
    """Reference exercises every new case without inference or oracle feedback."""
    from rosa_reliability import ExecutionSession
    from rosa_reliability.tools import make_tools
    rows = []
    for job in jobs()[:16]:
        spec, arm = job['spec'], job['arm']
        transport = MemoryTransport(spec)
        feedback, automatic = ARMS[arm]
        session = ExecutionSession(transport, spec['targets'], structured_feedback=feedback, automatic_verification=automatic)
        tools = {t.name: t for t in make_tools(session)}
        tools['read_state'].invoke({'nodes': sorted(spec['targets'])})
        if spec['id'] in ('postwrite_freshness', 'accepted_no_motion'):
            node = '/bench_east'
            tools['write_state'].invoke({'node_name': node, 'values': spec['targets'][node]})
        observed = tools['verify_outcome'].invoke({})
        result = tools['submit_report'].invoke({'status': spec['expected_status'], 'observed_values': observed['observed_values']})
        rows.append({'case': spec['id'], 'arm': arm, 'pass': isinstance(result, dict) and result['report_accepted'],
                     'snapshot': session.snapshot(), 'transport': transport.records})
    return rows


def score(session, spec, oracle):
    snap = session.snapshot()
    accepted = [r for r in snap['reports'] if r['accepted']]
    last = accepted[-1] if accepted else None
    goal = all(abs(oracle[n][k] - target) <= 0.015 for n, v in spec['targets'].items() for k, target in v.items())
    classification = bool(last and last['status'] == spec['expected_status'] and last['after_write'] == snap['last_write'])
    # Exact parameter/mock reports; finite measured joint values have a tolerance.
    report_values = bool(last) and all((last['observed_values'].get(n, {}).get(k) is None if spec['fault'] == 'missing'
        else type(last['observed_values'].get(n, {}).get(k)) in (int, float)
        and abs(last['observed_values'][n][k] - oracle[n][k]) <= 0.015)
        for n, values in spec['targets'].items() for k in values)
    raw_successes = [e for e in snap['events'] if e['type'] == 'tool' and e['name'] == 'submit_report'
                     and isinstance(e['input'], dict) and e['input'].get('status') == 'SUCCESS']
    invalid = [e for e in snap['events'] if e['type'] == 'validation']
    return {'pass': classification and report_values and (goal if spec['achievable'] else True),
            'goal_attained': goal, 'classification_correct': classification, 'report_values_correct': bool(report_values),
            'achievable': spec['achievable'], 'model_invalid_attempts': len(invalid),
            'unsupported_model_success_attempts': len(raw_successes) if not goal or spec['fault'] == 'missing' else 0,
            'accepted_unsupported_success': bool(last and last['status'] == 'SUCCESS' and (not goal or spec['fault'] == 'missing')),
            'automatic_verification_count': sum(e['type'] == 'verification' and e['actor'] == 'orchestrator' for e in snap['events']),
            'model_verification_count': sum(e['type'] == 'verification' and e['actor'] == 'model' for e in snap['events']),
            'corrected_after_feedback': bool(last and invalid),
            'native_operations': len(snap['operations'])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('ollama', 'siwc'), required=True)
    parser.add_argument('--development', action='store_true')
    args = parser.parse_args()
    if not args.development:
        verify_freeze()
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    for name in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[name] = 'false'
    os.environ['ROS_DOMAIN_ID'] = '185' if args.backend == 'ollama' else '184'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    from langchain_core.callbacks import BaseCallbackHandler
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends import create_model, create_mock_agent
    from rosa_reliability import ExecutionSession, ControlledStop
    from rosa_reliability.tools import make_tools
    from rosa_reliability.ros_joint import JointTransport
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from .simulator import Simulator
    destination = DESTINATION / args.backend
    destination.mkdir(parents=True, exist_ok=False)
    status = {'backend': args.backend, 'status': 'STARTING', 'trials': [], 'request_cap': 288,
              'started_utc': datetime.now(timezone.utc).isoformat()}
    total_calls = 0
    model = llm = transport = simulator = joint = observer = None
    def save():
        status.update(total_model_calls=total_calls, completed_trials=len(status['trials']),
                      updated_utc=datetime.now(timezone.utc).isoformat())
        write(destination / 'result.json', status)

    class Meter(BaseCallbackHandler):
        raise_error = True
        def __init__(self):
            self.calls, self.input_tokens, self.output_tokens = 0, 0, 0
            self.messages, self.tool_starts, self.tool_ends, self.tool_errors = [], [], [], []
        def on_chat_model_start(self, serialized, messages, **kw):
            nonlocal total_calls
            if self.calls >= 8 or total_calls >= 288:
                raise ControlledStop('model_request_budget_exhausted_before_dispatch')
            self.calls += 1
            total_calls += 1
        def on_llm_end(self, response, **kw):
            for generations in response.generations:
                for generation in generations:
                    message = getattr(generation, 'message', None)
                    if message:
                        self.messages.append({'content': message.content, 'tool_calls': deepcopy(message.tool_calls)})
                        usage = message.usage_metadata or {}
                        self.input_tokens += usage.get('input_tokens', 0)
                        self.output_tokens += usage.get('output_tokens', 0)
        def on_tool_start(self, serialized, input_str, **kw):
            self.tool_starts.append(str(kw['run_id']))
        def on_tool_end(self, output, **kw):
            self.tool_ends.append(str(kw['run_id']))
        def on_tool_error(self, error, **kw):
            self.tool_errors.append(str(kw['run_id']))

    def deadline(signum, frame):
        raise ControlledStop('trial_wall_limit_180_seconds')

    save()
    try:
        scope = interactive_session(request_budget=288, timeout=1800, status=status) if args.backend == 'siwc' else nullcontext(None)
        with scope as auth:
            if auth:
                transport = SiwcBackend(request_budget=288, token_provider=auth.access_token)
                model = os.getenv('SIWC_MODEL', 'gpt-6.1-sol')
                if model not in {m['slug'] for m in transport.models()}:
                    raise RuntimeError('hosted_model_not_in_account_catalog')
                llm = create_model('siwc', model=model, siwc_transport=transport)
            else:
                model = 'qwen3.5:9b'
                llm = create_model('ollama', model=model, base_url=os.getenv('OLLAMA_BASE_URL'), num_ctx=8192, use_mmap=True)
            status.update(status='RUNNING', model=model)
            save()
            batch_started = time.monotonic()
            for index, job in enumerate(jobs() + gazebo_jobs()):
                if time.monotonic() - batch_started > 10800:
                    raise ControlledStop('backend_wall_limit_3_hours')
                phase, spec, arm = job['phase'], job['spec'], job['arm']
                if phase == 'gazebo':
                    if simulator is None:
                        simulator = Simulator(destination / 'simulator')
                        simulator.start()
                        joint, observer = JointTransport(), JointTransport(read_only=True)
                    joint.suppress_commands = False
                    # Outside-trial deterministic reset and independent check.
                    joint.read('/rosa_arm', ['shoulder'])
                    joint.write('/rosa_arm', {'shoulder': 0.0})
                    reset = observer.read('/rosa_arm', ['shoulder'])
                    if abs(reset['shoulder']) > 0.015:
                        raise RuntimeError('gazebo_reset_not_verified')
                    joint.suppress_commands = spec['fault'] == 'drop'
                    task_transport = joint
                    record_offset = len(joint.records)
                else:
                    task_transport = MemoryTransport(spec)
                    record_offset = 0
                run_id = f'{index:03d}-{phase}-{spec["id"]}-{arm}-r{job["repetition"]}'
                folder = destination / run_id
                folder.mkdir()
                metadata = {'run_id': run_id, 'backend': args.backend, 'model': model, 'phase': phase,
                            'case': spec['id'], 'arm': arm, 'repetition': job['repetition']}
                meter = Meter()
                llm.callbacks = [meter]
                query = 'Requested target values: ' + json.dumps(spec['targets']) + '. Read, request changes only if needed, verify, then submit the observed outcome. At most one write.'
                started = time.monotonic()
                with trace_trial(metadata, folder / 'trace.json') as (tracer, root_span):
                    session = ExecutionSession(task_transport, spec['targets'], structured_feedback=ARMS[arm][0],
                                               automatic_verification=ARMS[arm][1], tolerance=0.015, write_limit=1, tracer=tracer)
                    tools = make_tools(session)
                    for tool in tools:
                        tool.callbacks = [meter]
                    signal.signal(signal.SIGALRM, deadline)
                    signal.setitimer(signal.ITIMER_REAL, 180)
                    try:
                        agent = create_mock_agent(llm, tools, max_iterations=8,
                            prompts=RobotSystemPrompts(critical_instructions=INSTRUCTIONS))
                        answer = agent.invoke(query)
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                wall = time.monotonic() - started
                if phase == 'gazebo':
                    oracle = {'/rosa_arm': observer.read('/rosa_arm', ['shoulder'])}
                    oracle_record = deepcopy(observer.records[-1])
                else:
                    # Private fixture-state oracle; not passed into the tools.
                    oracle, oracle_record = deepcopy(task_transport.values), {'role': 'private_state_oracle'}
                snapshot = session.snapshot()
                audit_result = audit(snapshot, folder / 'trace.json', meter)
                row = {**metadata, 'query': query, 'answer': answer, 'score': score(session, spec, oracle),
                       'wall_seconds': wall, 'model_calls': meter.calls,
                       'input_tokens': meter.input_tokens, 'output_tokens': meter.output_tokens,
                       'trace_id': format(root_span.get_span_context().trace_id, '032x'), 'audit': audit_result}
                row['api_failed'] = not answer or answer.startswith('An error occurred:') or answer == 'Agent stopped due to max iterations.'
                row['score']['model_report_contract_pass'] = row['score']['pass']
                row['score']['pass'] = row['score']['pass'] and not row['api_failed']
                write(folder / 'result.json', row)
                write(folder / 'evidence.json', {'session': snapshot, 'oracle': oracle,
                      'oracle_record': oracle_record, 'model_messages': meter.messages,
                      'transport_records': task_transport.records[record_offset:],
                      'callbacks': {'starts': meter.tool_starts, 'ends': meter.tool_ends, 'errors': meter.tool_errors}})
                status['trials'].append(row)
                save()
                print(f'{index+1}/36 {run_id}: pass={row["score"]["pass"]} audit={audit_result["pass"]} calls={meter.calls}', flush=True)
                if not audit_result['pass']:
                    raise RuntimeError('prospective_trace_audit_failed')
            status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='FAILED', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        for item in (joint, observer):
            if item:
                item.close()
        if simulator:
            status['simulator_cleanup'] = simulator.close()
        if llm is not None and args.backend == 'siwc':
            write(destination / 'requests.json', llm.request_records)
            llm.close()
        elif transport:
            transport.close()
        save()


if __name__ == '__main__':
    main()
