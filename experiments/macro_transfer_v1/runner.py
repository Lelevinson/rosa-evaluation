"""Checkpointed 18-cell UR5e macro comparison. No automatic consent or reruns."""
import argparse
from contextlib import contextmanager, nullcontext
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from urllib.request import Request, urlopen

from langchain_core.callbacks import BaseCallbackHandler
from rosa.prompts import RobotSystemPrompts
from rosa_reliability import ControlledStop
from rosa_reliability.reference import ReferenceWorkflowSession as WorkflowSession, make_reference_tools as make_workflow_tools
from .design import LIMITS, catalogue, PilotTransport, FaultTransport, jobs, query
from rosa_reliability.macro import MacroSession
from .inference import InferenceGate, LiveROSA
from .tracing import audit, trace_trial

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'artifacts/macro-transfer-v1-20261022'
PHOENIX_PYTHON = '/home/martin/.local/share/rosa-envs/phoenix/bin/python'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + f'.{os.getpid()}.tmp')
    pending.write_text(json.dumps(value, indent=2) + '\n')
    pending.replace(path)


def verify_freeze():
    manifest = json.loads((DESTINATION / 'freeze.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('frozen_source_changed:' + name)
    return manifest


def phoenix_audit(folder):
    run = subprocess.run([PHOENIX_PYTHON, '-B', '-m', 'experiments.macro_transfer_v1.persisted',
        '--folder', str(folder)], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (folder / 'phoenix-audit.log').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('persisted_phoenix_audit_failed')
    return json.loads((folder / 'phoenix-audit.json').read_text())


class Meter(BaseCallbackHandler):
    def __init__(self):
        self.tool_starts, self.tool_ends, self.tool_errors = [], [], []
        self.messages = []

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_starts.append(str(kwargs['run_id']))

    def on_tool_end(self, output, **kwargs):
        self.tool_ends.append(str(kwargs['run_id']))

    def on_tool_error(self, error, **kwargs):
        self.tool_errors.append(str(kwargs['run_id']))

    def on_llm_end(self, response, **kwargs):
        for group in response.generations:
            for generation in group:
                message = getattr(generation, 'message', None)
                if message is not None:
                    self.messages.append({'content': message.content, 'tool_calls': deepcopy(message.tool_calls),
                        'invalid_tool_calls': deepcopy(message.invalid_tool_calls),
                        'usage': deepcopy(message.usage_metadata),
                        'response_metadata': deepcopy(message.response_metadata)})


from .scoring import score


def unload_local():
    request = Request(os.environ['OLLAMA_BASE_URL'] + '/api/generate',
        data=b'{"model":"qwen3.5:9b","keep_alive":0}', headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def run_backend(backend, llm, phase, batch_counter, oauth_transport=None):
    verify_freeze()
    folder = DESTINATION / phase / backend
    folder.mkdir(parents=True, exist_ok=False)
    status = {'status': 'STARTING', 'backend': backend, 'model': llm.model, 'request_cap': 144,
        'total_model_calls': 0, 'limits': LIMITS, 'trials': [], 'current_trial': None,
        'started_utc': datetime.now(timezone.utc).isoformat()}
    skills = catalogue(phase)
    tolerance = .025 if phase == 'gazebo' else .01
    active_start = time.monotonic()
    simulator = controller = observer = None

    def save():
        status['updated_utc'] = datetime.now(timezone.utc).isoformat()
        if oauth_transport and oauth_transport.availability_error:
            status['authorization_or_service_unavailable'] = oauth_transport.availability_error
        write(folder / 'checkpoint.json', status)

    def reserve():
        if status['total_model_calls'] >= 144 or batch_counter['calls'] >= 144 or time.monotonic() - active_start >= LIMITS['backend_seconds']:
            raise ControlledStop('backend_resource_budget_exhausted_before_dispatch')
        status['total_model_calls'] += 1
        batch_counter['calls'] += 1

    def expired(signum, frame):
        raise ControlledStop('trial_wall_timeout_180_seconds')

    save()
    try:
        status['status'] = 'RUNNING'
        if phase == 'gazebo':
            from experiments.ur5e_transfer_v1.arm import ArmSimulator, ArmTransport
            simulator = ArmSimulator(folder / 'simulator')
            simulator.start()
            controller, observer = ArmTransport(), ArmTransport(read_only=True)
            from .controls import run_controls
            run_controls(folder / 'fresh-controls', controller, observer)
        for index, job in enumerate(jobs(phase)):
            verify_freeze()
            if oauth_transport:
                oauth_transport.raise_if_unavailable()
            spec, condition = job['case'], job['condition']
            program = condition != 'model'
            run_id = f'{index:02d}-{spec["id"]}-{condition}'
            trial = folder / run_id
            trial.mkdir()
            status['current_trial'] = {'run_id': run_id, 'state': 'STARTED_OUTCOME_UNKNOWN'}
            save()
            if phase == 'gazebo':
                from experiments.ur5e_transfer_v1.arm import reset, configure_fault, JOINTS
                reset_record = reset(controller, observer)
                configure_fault(controller, spec)
                controller.records.clear()
                transport = FaultTransport(controller, spec)
                oracle = lambda: {'/ur5e': observer.read('/ur5e', list(JOINTS))}
            else:
                transport = PilotTransport(spec)
                oracle = lambda: deepcopy(transport.values)
                reset_record = None
            meter, claims = Meter(), []
            gate = InferenceGate(backend, reserve)

            session_type = MacroSession if condition == 'macro' else WorkflowSession

            class EvaluatedSession(session_type):
                @contextmanager
                def tool_call(self, name, args):
                    if name == 'submit_report' and isinstance(args, dict):
                        available = {}
                        for observation in self.observations[self._read_floor:]:
                            available.update(observation['observed_values'])
                        actual = oracle()
                        claims.append({'status': args.get('status'), 'arguments': deepcopy(args),
                            'private_actual_state': deepcopy(actual),
                            'selected_goal_attained': all(abs(actual[n][k] - v) <= tolerance
                                for n, group in self.targets.items() for k, v in group.items()),
                            'fresh_known_evidence': set(available) == set(self.targets) and
                                all(v is not None for g in available.values() for v in g.values())})
                    with super().tool_call(name, args) as event:
                        yield event

            metadata = {'run_id': run_id, 'backend': backend, 'model': llm.model,
                'case': spec['id'], 'condition': condition, 'program_managed': program, 'protocol': 'macro-transfer-v1', 'phase': phase}
            request = query(spec, condition, phase)
            started = time.monotonic()
            llm.callbacks = []  # inherited invocation callbacks meter every nested call exactly once
            with trace_trial(metadata, trial / 'trace.json') as (tracer, root):
                session = EvaluatedSession(transport, skills, program_managed=program, tolerance=tolerance, tracer=tracer)
                tools = make_workflow_tools(session)
                agent = LiveROSA(2, llm, terminal_session=session, completion_gate=gate,
                    tools=tools, load_default_tools=False, accumulate_chat_history=False,
                    max_iterations=8, execution_callbacks=[meter],
                    prompts=RobotSystemPrompts(critical_instructions='Use only the bounded task tools and respect the provided task contract.'))
                signal.signal(signal.SIGALRM, expired)
                signal.setitimer(signal.ITIMER_REAL, 180)
                try:
                    answer = agent.invoke(request)
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed = time.monotonic() - started
            snap, inference = session.snapshot(), gate.snapshot()
            local_audit = audit(snap, trial / 'trace.json', meter)
            spans = json.loads((trial / 'trace.json').read_text())['spans']
            if sum(s.get('attributes', {}).get('openinference.span.kind') == 'LLM' for s in spans) != gate.calls:
                local_audit['errors'].append('llm_span_request_count_mismatch')
            returned = [e for e in gate.events if e['status'] == 'RETURNED']
            if len(meter.messages) != len(returned):
                local_audit['errors'].append('returned_generation_usage_count_mismatch')
            if any(e['status'] == 'RETURNED_USAGE_INVALID' for e in gate.events):
                local_audit['errors'].append('missing_returned_usage')
            unreturned = [e for e in gate.events if e['status'] == 'UNRETURNED']
            if unreturned and not ('trial_wall_timeout' in answer or
                                    (oauth_transport and oauth_transport.availability_error)):
                local_audit['errors'].append('unexpected_unreturned_generation')
            if gate.calls > 8 or len(snap['operations']) > 10 or session.write_count > 1:
                local_audit['errors'].append('hard_resource_ceiling_exceeded')
            local_audit['pass'] = not local_audit['errors']
            actual = oracle()
            scored = score(session, spec, transport, answer, claims, skills, tolerance, actual)
            row = {**metadata, 'query': request, 'answer': answer, 'score': scored,
                'audit': local_audit, 'inference': inference, 'wall_seconds': elapsed,
                'native_operations': len(snap['operations']), 'tool_attempts': snap['tool_calls'],
                'trace_id': format(root.get_span_context().trace_id, '032x')}
            write(trial / 'result.json', row)
            write(trial / 'evidence.json', {'session': snap, 'model_messages': meter.messages,
                'private_final_state': actual, 'claim_time_oracles': claims, 'reset_record': reset_record,
                'transport_records': transport.records,
                'callbacks': {'starts': meter.tool_starts, 'ends': meter.tool_ends, 'errors': meter.tool_errors}})
            status['trials'].append(row)
            status['current_trial'] = None
            save()
            print(backend, run_id, 'correct=' + str(scored['pass']), 'calls=' + str(gate.calls),
                  'local_audit=' + str(local_audit['pass']), flush=True)
            phoenix_audit(trial)
            if not local_audit['pass'] or scored['accepted_unsupported_selected_goal_success'] or scored['dispatch_violations']:
                raise RuntimeError('prospective_engineering_gate_failed_data_preserved')
            if oauth_transport:
                oauth_transport.raise_if_unavailable()
            if backend == 'ollama' and unreturned:
                write(trial / 'timeout-model-unload.json', unload_local())
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__,
                      error=str(error) if isinstance(error, (ControlledStop, RuntimeError)) else type(error).__name__)
        raise
    finally:
        for item in (controller, observer):
            if item:
                item.close()
        if simulator:
            status['simulator_cleanup'] = simulator.close()
        save()
    return status



@contextmanager
def gazebo_lock():
    import fcntl
    with (DESTINATION / 'gazebo.lock').open('a') as handle:
        deadline = time.monotonic() + 4500
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise RuntimeError('gazebo_serialization_wait_timeout')
                time.sleep(2)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('ollama', 'siwc'), required=True)
    args = parser.parse_args()
    verify_freeze()
    os.environ['ROS_DOMAIN_ID'] = '211' if args.backend == 'ollama' else '212'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    for key in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from rosa_backends import create_model
    auth_status = {}
    llm = transport = None
    try:
        scope = interactive_session(request_budget=144, timeout=1800, status=auth_status, require_renewal=True) if args.backend == 'siwc' else nullcontext(None)
        with scope as auth:
            if auth:
                transport = SiwcBackend(token_provider=auth.access_token, request_budget=144)
                if 'gpt-6.1-sol' not in {r['slug'] for r in transport.models()}:
                    raise RuntimeError('requested_model_not_in_account_catalog')
                llm = create_model('siwc', model='gpt-6.1-sol', siwc_transport=transport)
            else:
                from rosa_backends.chat_ollama import ConfiguredChatOllama
                llm = ConfiguredChatOllama(model='qwen3.5:9b', base_url=os.environ['OLLAMA_BASE_URL'],
                    num_ctx=8192, num_predict=1024, use_mmap=True, temperature=0, seed=42,
                    reasoning=False, streaming=False, client_kwargs={'timeout': 180}, cache=False)
            counter = {'calls': 0}
            with gazebo_lock():
                run_backend(args.backend, llm, 'gazebo', counter, transport)
    finally:
        if args.backend == 'siwc':
            if llm is not None:
                write(DESTINATION / 'hosted-request-records.json', llm.request_records)
                llm.close()
            elif transport:
                transport.close()
            write(DESTINATION / 'session-siwc.json', {'auth': auth_status, 'request_cap': 144})
        elif llm is not None:
            write(DESTINATION / 'local-model-unload.json', unload_local())


if __name__ == '__main__':
    main()
