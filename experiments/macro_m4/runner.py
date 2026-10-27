"""M4 bounded execution. Freeze and zero-model gate precede live backends."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.request import Request, urlopen

from rosa_reliability.bounded_macro import MacroLimits
from rosa_reliability.capability_demo import deterministic_report
from rosa_reliability.gazebo_demo import GazeboDemo
from rosa_reliability.macro_agent import MacroROSA, InferenceLimits
from rosa_reliability.ros_arm import ArmTransport, JOINTS
from rosa_reliability.ros_readiness import ArmReadinessTransport
from experiments.macro_capabilities_v2.observability import Meter, audit, trace_check
from experiments.macro_capabilities_v2.runner import MissingSource, persisted, switch_trajectory, write
from .design import LIMITS, registry, cases, jobs, query
from .recovery import CampaignBudget, RecoveryGate, RecoverableSiwc
from .scoring import score

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'artifacts/macro-m4-20261027'
PROTOCOL = ROOT / 'docs/M4_MACRO_PROTOCOL_2026-10-27.md'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    BASE.mkdir(exist_ok=False)
    names = list((ROOT.parent / 'rosa-research/src').rglob('*.py'))
    names += list((ROOT.parent / 'rosa-research/src/rosa_reliability/sim').glob('*'))
    names += list(Path(__file__).parent.glob('*.py'))
    names += list((ROOT / 'experiments/macro_capabilities_v2').glob('*.py'))
    names += [ROOT.parent / p for p in ('rosa-research/uv.lock', 'rosa-research/pyproject.toml',
        'rosa-evaluation/tools/phoenix/uv.lock', 'rosa-evaluation/tools/phoenix/pyproject.toml')]
    names += [PROTOCOL, ROOT / 'tests/test_macro_m4.py']
    names += [ROOT.parent / 'reports/m4-ollama.ps1', ROOT.parent / 'reports/m4-service-preflight.json']
    source = {}
    for path in names:
        name = path.relative_to(ROOT.parent).as_posix()
        target = BASE / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        source[name] = digest(path)
    original = ROOT / 'artifacts/macro-capabilities-m2m3-20261027/archive-manifest.json'
    record = json.loads(original.read_text())
    for name, expected in record['files'].items():
        if digest(original.parent / name) != expected: raise RuntimeError('m2m3_evidence_changed:' + name)
    revisions = {name: subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT.parent / name),
        '-C', str(ROOT.parent / name), 'rev-parse', 'HEAD'], text=True).strip()
        for name in ('rosa-research', 'rosa-evaluation')}
    write(BASE / 'freeze.json', {'files': source, 'source_commits': revisions, 'limits': LIMITS, 'cases': cases(),
        'schedules': {b: jobs(b) for b in ('ollama', 'siwc')},
        'queries': {s['id']: {c: query(s, c) for c in ('primitives', 'macro')} for s in cases()},
        'previous_manifest_sha256': digest(original), 'previous_evidence_files_verified': len(record['files'])})
    print(json.dumps({'frozen_files': len(source), 'planned_trials': 80, 'previous_files_verified': len(record['files'])}))


def verify():
    value = json.loads((BASE / 'freeze.json').read_text())
    for name, expected in value['files'].items():
        if digest(ROOT.parent / name) != expected or digest(BASE / 'source' / name) != expected:
            raise RuntimeError('m4_frozen_source_changed:' + name)
    return value


@contextmanager
def alarm(seconds):
    def expired(signum, frame): raise TimeoutError('m4_external_wall_deadline')
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try: yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def reference(invocation, spec, condition, callbacks):
    if spec['kind'] == 'clarification':
        return 'Which task do you mean: inspect readiness or move to a specified permitted pose?'
    invocation.execute(spec['skill'], config=callbacks)
    if condition == 'primitives':
        observation = invocation._tool('read_state').invoke({'nodes': sorted(invocation.session.targets)}, config=callbacks)
        values, targets = observation['observed_values'], invocation.session.targets
        known = all(v is not None for group in values.values() for v in group.values())
        if spec['kind'] == 'movement' and known and any(abs(values[n][k] - v) > .025
                for n, group in targets.items() for k, v in group.items()):
            invocation._tool('write_state').invoke({'node_name': '/ur5e', 'values': targets['/ur5e']}, config=callbacks)
            invocation._tool('verify_outcome').invoke({}, config=callbacks)
    # Explicit classification of observed facts, not an LLM repair or oracle tool.
    observation = invocation.session.observations[-1]
    values, targets = observation['observed_values'], invocation.session.targets
    status = 'UNKNOWN' if any(v is None for group in values.values() for v in group.values()) else (
        'SUCCESS' if all(abs(values[n][k] - v) <= .025 for n, group in targets.items() for k, v in group.items()) else 'FAILURE')
    return invocation.submit_report(status, observation['observation_id'], config=callbacks)


def run(backend, *, model=None, transport=None, endpoint=None, control=False):
    verify()
    folder = BASE / ('controls' if control else backend)
    folder.mkdir(exist_ok=False)
    status = {'backend': backend, 'status': 'STARTING', 'trials': [], 'current_trial': None,
        'planned': 20 if control else 40, 'live_model_requests': 0}
    def checkpoint(budget=None):
        if budget:
            status['campaign'] = budget
            status['live_model_requests'] = budget['reserved_requests']
        write(folder / 'checkpoint.json', status)
    campaign = CampaignBudget(checkpoint)
    checkpoint()
    simulator = GazeboDemo(folder / 'simulator')
    movement = inspection = observer = readiness_observer = None
    inactive = False
    started = time.monotonic()
    try:
        simulator.start()
        movement, inspection = ArmTransport(), ArmReadinessTransport()
        observer, readiness_observer = ArmTransport(read_only=True), ArmReadinessTransport()
        plan = ([{'id': s['id'] + '-' + c, 'case': s, 'condition': c, 'repetition': 0}
            for s in cases() for c in ('primitives', 'macro')] if control else jobs(backend))
        status['status'] = 'RUNNING'
        for job in plan:
            verify()
            if transport: transport.raise_if_unavailable()
            spec, condition = job['case'], job['condition']
            trial = folder / job['id']
            trial.mkdir()
            status['current_trial'] = job['id']
            checkpoint(campaign.snapshot())
            setup_started = time.monotonic()
            with alarm(120):
                movement.suppress_commands = movement.partial_commands = movement.missing_observations = False
                movement.read('/ur5e', list(JOINTS))
                initial = registry().catalogue()[spec['initial']]['targets']['/ur5e']
                receipt = movement.write('/ur5e', initial)
                initial_observation = observer.read('/ur5e', list(JOINTS))
                if any(abs(initial_observation[k] - v) > .025 for k, v in initial.items()):
                    raise RuntimeError('m4_reset_not_independently_confirmed')
                management = None
                if spec['fault'] == 'inactive':
                    management = switch_trajectory(inspection, False)
                    inactive = True
                before_readiness = {**readiness_observer.read_group('controllers',
                    ['trajectory_controller_active', 'joint_state_broadcaster_active']),
                    **readiness_observer.read_group('joint_state', ['joint_sample_fresh'])}
            write(trial / 'outside-task-setup.json', {'trajectory_dispatches': 1, 'receipt': receipt,
                'independent_joints': initial_observation, 'independent_readiness': before_readiness,
                'controller_management': management, 'seconds': time.monotonic() - setup_started})
            movement.suppress_commands = spec['fault'] == 'ineffective'
            movement.partial_commands = spec['fault'] == 'partial'
            movement.missing_observations = spec['fault'] == 'missing_motion'
            reader = MissingSource(inspection, spec['fault']) if spec['fault'] in ('controllers', 'joint_state') else inspection
            offset = len(movement.records)
            meter, gate, agent = Meter(), None, None
            remaining = LIMITS['backend_seconds'] - (time.monotonic() - campaign.started)
            if remaining <= 0: raise RuntimeError('m4_backend_time_exhausted')
            task_started = time.monotonic()
            error = None
            with trace_check(trial / 'trace.json', {'stage': 'M4', 'backend': backend, 'condition': condition,
                    'case': spec['id'], 'repetition': job['repetition'], 'control': control}) as tracer:
                inv = registry().open({'state': movement, 'inspection': reader}, mode=condition,
                    allowed_skills=spec['allowed'], tracer=tracer,
                    limits=MacroLimits(seconds=LIMITS['trial_seconds']))
                try:
                    with alarm(min(LIMITS['trial_seconds'], remaining)):
                        if control:
                            answer = reference(inv, spec, condition, {'callbacks': [meter]})
                        else:
                            agent = MacroROSA(model, inv, backend=backend, callbacks=[meter])
                            gate = RecoveryGate(inv, backend=backend,
                                limits=InferenceLimits(), local_options=agent.inference_budget.local_options,
                                campaign=campaign, release=transport.release_transient_failure if transport else None,
                                journal=lambda inference: write(trial / 'inference-progress.json',
                                    {'inference': inference, 'snapshot': inv.snapshot()}))
                            agent.inference_budget = agent.completion_gate = gate
                            answer = agent.invoke(query(spec, condition))
                except Exception as exc:
                    error = type(exc).__name__
                    answer = 'Task interrupted: ' + error
                snapshot = inv.snapshot()
            wall = time.monotonic() - task_started
            observed = observer.read('/ur5e', list(JOINTS))
            readiness = {**readiness_observer.read_group('controllers',
                ['trajectory_controller_active', 'joint_state_broadcaster_active']),
                **readiness_observer.read_group('joint_state', ['joint_sample_fresh'])}
            records = deepcopy(movement.records[offset:])
            result = score(spec, snapshot, answer, records, observed, readiness)
            local = audit(snapshot, trial / 'trace.json', meter)
            inference = gate.snapshot() if gate else {'calls': 0, 'decision_calls': 0, 'infrastructure_failures': 0,
                'known_input_tokens': 0, 'known_output_tokens': 0, 'usage_complete': True, 'events': []}
            spans = json.loads((trial / 'trace.json').read_text())['spans']
            if sum(s.get('attributes', {}).get('openinference.span.kind') == 'LLM' for s in spans) != inference['calls']:
                local['errors'].append('physical_model_requests_do_not_match_llm_spans')
                local['pass'] = False
            recovered = inference['infrastructure_failures'] > 0
            row = {'job': {k: v for k, v in job.items() if k != 'case'}, 'case': spec['id'],
                'condition': condition, 'repetition': job['repetition'], 'request': spec['request'], 'answer': answer,
                'snapshot': snapshot, 'inference': inference, 'score': result, 'wall_seconds': wall,
                'independent_joints': observed, 'independent_readiness': readiness, 'movement_records': records,
                'error_type': error, 'local_audit': local, 'infrastructure_recovered': recovered,
                'primary_pass': result['pass'] and local['pass'] and not recovered,
                'completion_including_recovery': result['pass'] and local['pass']}
            write(trial / 'result.json', row)
            write(trial / 'audit.json', local)
            status['trials'].append(row)
            status['current_trial'] = None
            checkpoint(campaign.snapshot())
            row['phoenix_audit'] = persisted(trial)
            checkpoint(campaign.snapshot())
            if backend == 'ollama' and endpoint:
                try:
                    with urlopen(endpoint + '/api/ps', timeout=5) as response:
                        loaded = json.load(response)
                    write(trial / 'outside-task-ollama-status.json',
                        {'models': [item for item in loaded.get('models', []) if item.get('name') == 'qwen3.5:9b']})
                except Exception as exc:
                    write(trial / 'outside-task-ollama-status.json', {'error_type': type(exc).__name__})
            if inactive:
                restore = switch_trajectory(inspection, True)
                write(trial / 'outside-task-controller-restore.json', restore)
                inactive = False
            print(json.dumps({'backend': backend, 'done': len(status['trials']), 'planned': len(plan),
                'case': spec['id'], 'condition': condition, 'primary_pass': row['primary_pass'],
                'calls': inference['calls']}), flush=True)
            if not local['pass']: raise RuntimeError('m4_local_trace_audit_failed')
            if control and not row['primary_pass']: raise RuntimeError('m4_deterministic_gate_failed:' + job['id'])
            if transport: transport.raise_if_unavailable()
        verify()
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__, error=str(error)
            if type(error).__name__ in ('SafeError', 'ControlledStop', 'RuntimeError') else type(error).__name__)
        raise
    finally:
        errors = []
        if inactive and inspection:
            try: switch_trajectory(inspection, True)
            except Exception as error: errors.append('controller_restore_' + type(error).__name__)
        for item in (movement, inspection, observer, readiness_observer):
            if item:
                try: item.close()
                except Exception as error: errors.append(type(error).__name__)
        status['cleanup_errors'] = errors
        status['simulator_cleanup'] = simulator.close()
        status['total_elapsed_seconds'] = time.monotonic() - started
        status['primary_correct'] = sum(r['primary_pass'] for r in status['trials'])
        status['completed_correct_including_recovery'] = sum(r['completion_including_recovery'] for r in status['trials'])
        checkpoint(campaign.snapshot())
    return status


def require_controls():
    data = json.loads((BASE / 'controls/checkpoint.json').read_text())
    if (data['status'] != 'COMPLETE' or len(data['trials']) != 20 or data['primary_correct'] != 20 or
            data['simulator_cleanup']['returncode'] != 0 or data['cleanup_errors'] or
            not all(r['phoenix_audit']['pass'] for r in data['trials'])):
        raise RuntimeError('m4_zero_model_gate_not_passed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('freeze', 'controls', 'live'))
    parser.add_argument('--backend', choices=('ollama', 'siwc'))
    parser.add_argument('--endpoint')
    args = parser.parse_args()
    if args.action == 'freeze': freeze(); return
    os.environ.update(ROS_DOMAIN_ID='217', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',
        LANGCHAIN_TRACING='false', LANGCHAIN_TRACING_V2='false', LANGSMITH_TRACING='false')
    verify()
    auth_status, model, transport = {}, None, None
    with (BASE / 'gazebo.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.action == 'controls':
            run('deterministic', control=True)
            return
        require_controls()
        try:
            if args.backend == 'siwc':
                from rosa_auth.remembered import remembered_session
                from rosa_auth.protected_store import WindowsCredentialStore
                from rosa_auth.oauth import SafeError
                from rosa_backends.chat_siwc import ChatSiwc
                with WindowsCredentialStore('research') as store:
                    if store.load() is None:
                        raise SafeError('manual_sign_in_required_no_automatic_login')
                    with remembered_session(store=store, request_budget=LIMITS['backend_requests'], status=auth_status) as auth:
                        transport = RecoverableSiwc(token_provider=auth.access_token, request_budget=LIMITS['backend_requests'])
                        model = ChatSiwc(model='gpt-6.1-sol', backend=transport)
                        run('siwc', model=model, transport=transport)
            elif args.backend == 'ollama':
                from rosa_backends.chat_ollama import ConfiguredChatOllama
                model = ConfiguredChatOllama(model='qwen3.5:9b', base_url=args.endpoint,
                    num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
                    streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
                run('ollama', model=model, endpoint=args.endpoint)
            else: raise RuntimeError('explicit_backend_required')
        finally:
            if args.backend == 'siwc':
                if model: model.close()
                elif transport: transport.close()
                write(BASE / 'siwc-authorization-status.json', auth_status)
            if args.backend == 'ollama':
                try:
                    request = Request(args.endpoint + '/api/generate', headers={'Content-Type': 'application/json'},
                        data=b'{"model":"qwen3.5:9b","keep_alive":0}')
                    with urlopen(request, timeout=30) as response: write(BASE / 'ollama-unload.json', json.load(response))
                except Exception as error: write(BASE / 'ollama-unload.json', {'error_type': type(error).__name__})


if __name__ == '__main__': main()
