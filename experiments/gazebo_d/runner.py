"""Gazebo D runner: study-local wrapper around the frozen M4 harness (D0_PROTOCOL §3).

Reuses UNCHANGED: experiments/macro_m4/{design,scoring,recovery,runner}.py (registry, query(), LIMITS, score(),
RecoveryGate, RecoverableSiwc, alarm(), reference(), verify()), experiments/macro_capabilities_v2 (Meter, audit,
trace_check, persisted, switch_trajectory, MissingSource, write) and rosa-research c0c61a0 (MacroROSA,
GazeboDemo, ArmTransport, ArmReadinessTransport). The per-trial body below is M4 run()'s body, copied
(M4 runner.py sha256 f5727b1e…; see freeze), because M4 run() takes one backend and starts its own simulator.

Differences, all outside the model's view: D cases + fixed schedule; one Gazebo per stage; per-row model
factory; per-model request/time ledger (DCampaignBudget = M4 CampaignBudget logic with an explicit cap);
ROS_DOMAIN_ID=231; scripted reset check; /api/ps offload record; local-model unload on model switch;
no row starts after the deadline; resume runs only unstarted rows.

Actions (run in the D12 WSL research env, from the rosa-evaluation root):
  python -B -m experiments.gazebo_d.runner plan     --stage heldout --models models.json
  python -B -m experiments.gazebo_d.runner freeze   --stage dev     --models models.json
  python -B -m experiments.gazebo_d.runner controls                  # 52 zero-model controls
  python -B -m experiments.gazebo_d.runner live     --stage dev     --models models.json
models.json (written by session A at launch from Phase B outcomes), list of admitted models:
  [{"name": "qwen", "backend": "ollama", "tag": "qwen3.5:9b", "digest": "56671c2a…", "endpoint": "http://…:11440",
    "adapter": null | {"path": "tools/parity/adapters/granite.py", "sha256": "…", "label": "…"}},
   {"name": "sol", "backend": "siwc", "model": "gpt-6.1-sol"}, …]
Adapter interface: the module defines make_model(kwargs: dict) -> chat model, where kwargs are exactly the
ConfiguredChatOllama keyword arguments below. It may only make allowed transport changes (Phase B).
"""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'artifacts/gazebo-d-20261121'
CASES = D / 'cases'
SCHEDULE = D / 'schedule'
RUNS = D / 'runs'
TAIPEI = timezone(timedelta(hours=8))
DEADLINE = datetime(2026, 11, 23, 6, 0, tzinfo=TAIPEI)          # no row STARTS at or after this
DOMAIN_ID = '231'
TOLERANCE = .025
OLLAMA_KWARGS = dict(num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
                     streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
FROZEN_INPUTS = ['experiments/gazebo_d/runner.py', 'experiments/gazebo_d/__init__.py',
                 'experiments/gazebo_d/job.sh', 'experiments/gazebo_d/start_detached.ps1',
                 'artifacts/gazebo-d-20261121/cases/dev.json', 'artifacts/gazebo-d-20261121/cases/heldout.json',
                 'artifacts/gazebo-d-20261121/cases/template-groups.json',
                 'artifacts/gazebo-d-20261121/schedule/dev.json', 'artifacts/gazebo-d-20261121/schedule/heldout.json',
                 'tools/gazebo_d/analysis.py', 'artifacts/gazebo-d-20261121/D0_PROTOCOL.md']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


# ---------------------------------------------------------------- pure planning logic (tested offline)

def load_cases():
    return {c['id']: c for split in ('dev', 'heldout')
            for c in json.loads((CASES / f'{split}.json').read_text(encoding='utf-8'))}


def admitted_rows(stage, admitted_names):
    """Schedule rows for admitted models only, original order and seq kept."""
    rows = json.loads((SCHEDULE / f'{stage}.json').read_text(encoding='utf-8'))['rows']
    unknown = set(admitted_names) - {r['model'] for r in rows}
    if unknown:
        raise ValueError('unknown_model:' + ','.join(sorted(unknown)))
    return [r for r in rows if r['model'] in admitted_names]


def ceilings(rows):
    """Per-model request ceiling = 8 x trials + 3 reserve (M4 rule); 8 h per model per stage."""
    per = {}
    for r in rows:
        per[r['model']] = per.get(r['model'], 0) + 1
    return {m: {'trials': n, 'request_cap': 8 * n + 3, 'reserve_cap': 3, 'seconds_cap': 8 * 3600} for m, n in per.items()}


def trial_name(row):
    return f"{row['seq']:03d}-{row['case']}-{row['model']}-{row['arm']}"


def classify(stage_dir, rows):
    """DONE (result.json), INTERRUPTED (folder without result: never rerun), UNSTARTED."""
    state = {}
    for r in rows:
        folder = Path(stage_dir) / trial_name(r)
        state[r['seq']] = ('DONE' if (folder / 'result.json').exists() else
                           'INTERRUPTED' if folder.exists() else 'UNSTARTED')
    return state


def may_start(now=None):
    now = now or datetime.now(TAIPEI)
    return now < DEADLINE


class DCampaignBudget:
    """M4 CampaignBudget logic (reserve / transient recovery / snapshot) with an explicit per-model cap."""
    def __init__(self, checkpoint, *, request_cap, seconds_cap, reserve_cap=3, clock=time.monotonic):
        self.clock, self.started, self.checkpoint = clock, clock(), checkpoint
        self.request_cap, self.seconds_cap, self.reserve_cap = request_cap, seconds_cap, reserve_cap
        self.requests = self.retries = 0
        self.events = []
        self.active_seconds = 0.0          # only time spent inside this model's trials counts

    def reserve(self):
        from rosa_reliability.execution import ControlledStop
        if self.requests >= self.request_cap or self.active_seconds >= self.seconds_cap:
            raise ControlledStop('d_model_request_or_time_budget_exhausted')
        self.requests += 1
        self.checkpoint(self.snapshot())

    def recovery(self, error):
        from experiments.macro_m4.recovery import transient
        if not transient(error) or self.retries >= self.reserve_cap:
            return False
        self.retries += 1
        self.events.append({'after_request': self.requests, 'error_type': type(error).__name__,
                            'http_status': getattr(error, 'status', getattr(error, 'status_code', None)),
                            'usage': 'UNKNOWN_CENSORED', 'retry_number': self.retries})
        self.checkpoint(self.snapshot())
        return True

    def snapshot(self):
        return {'reserved_requests': self.requests, 'request_cap': self.request_cap,
                'infrastructure_retries': self.retries, 'reserve_cap': self.reserve_cap,
                'active_seconds': self.active_seconds, 'seconds_cap': self.seconds_cap,
                'events': deepcopy(self.events)}


def reset_check(spec, initial_target, initial_observation, before_readiness):
    """Scripted reset check (D0 §6 a,b). Returns a list of failures (empty = pass)."""
    failures = []
    if any(abs(initial_observation[k] - v) > TOLERANCE for k, v in initial_target.items()):
        failures.append('start_pose_not_confirmed')
    expected = {k: True for k in before_readiness}
    if spec['fault'] == 'inactive':
        expected['trajectory_controller_active'] = False
    if before_readiness != expected:
        failures.append('readiness_before_task_unexpected:' + json.dumps(before_readiness, sort_keys=True))
    return failures


# ---------------------------------------------------------------- freeze

def freeze_inputs(models):
    files = {p: sha(ROOT / p) for p in FROZEN_INPUTS}
    for m in models:
        if m.get('adapter'):
            if sha(ROOT / m['adapter']['path']) != m['adapter']['sha256']:
                raise RuntimeError('d_adapter_hash_mismatch:' + m['name'])
            files[m['adapter']['path']] = m['adapter']['sha256']
    return files


def write_freeze(stage, models_path):
    models = json.loads(Path(models_path).read_text())
    folder = RUNS / stage
    if (folder / 'freeze.json').exists():
        raise RuntimeError('d_stage_already_frozen')
    m4 = json.loads((ROOT / 'artifacts/macro-m4-20261027/freeze.json').read_text())
    dump(folder / 'freeze.json', {'stage': stage, 'frozen_at': datetime.now(TAIPEI).isoformat(),
        'files': freeze_inputs(models), 'models': models, 'models_json_sha256': sha(models_path),
        'm4_freeze_sha256': sha(ROOT / 'artifacts/macro-m4-20261027/freeze.json'),
        'm4_files': len(m4['files']), 'ollama_kwargs': OLLAMA_KWARGS, 'domain_id': DOMAIN_ID,
        'deadline': DEADLINE.isoformat(), 'ceilings': ceilings(admitted_rows(stage, [m['name'] for m in models]))})
    print('FROZEN', stage, len(models), 'models')


def verify_stage(stage):
    record = json.loads((RUNS / stage / 'freeze.json').read_text())
    for name, expected in record['files'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('d_frozen_input_changed:' + name)
    return record


# ---------------------------------------------------------------- live model plumbing

def api(endpoint, path, body=None, timeout=30):
    from urllib.request import Request, urlopen
    data = None if body is None else json.dumps(body).encode()
    request = Request(endpoint + path, data=data, headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def ollama_model(spec):
    tags = {m['name']: m['digest'] for m in api(spec['endpoint'], '/api/tags')['models']}
    if tags.get(spec['tag']) != spec['digest']:
        raise RuntimeError('d_model_digest_mismatch:' + spec['name'])
    kwargs = dict(OLLAMA_KWARGS, model=spec['tag'], base_url=spec['endpoint'])
    if spec.get('adapter'):
        path = ROOT / spec['adapter']['path']
        if sha(path) != spec['adapter']['sha256']:
            raise RuntimeError('d_adapter_hash_mismatch:' + spec['name'])
        module_spec = importlib.util.spec_from_file_location('d_adapter_' + spec['name'], path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module.make_model(kwargs)
    from rosa_backends.chat_ollama import ConfiguredChatOllama
    return ConfiguredChatOllama(**kwargs)


def unload(spec):
    try:
        return api(spec['endpoint'], '/api/generate', {'model': spec['tag'], 'keep_alive': 0})
    except Exception as error:
        return {'error_type': type(error).__name__}


def offload_record(spec):
    try:
        loaded = api(spec['endpoint'], '/api/ps', timeout=5).get('models', [])
        rows = [m for m in loaded if m.get('name') == spec['tag'] or m.get('model') == spec['tag']]
        return {'models': rows, 'vram_fraction': [round(m['size_vram'] / m['size'], 4) for m in rows if m.get('size')]}
    except Exception as error:
        return {'error_type': type(error).__name__}


# ---------------------------------------------------------------- stage execution

def run_stage(stage, *, control=False, models=None):
    from experiments.macro_m4 import runner as m4
    from experiments.macro_m4.design import LIMITS, registry, query
    from experiments.macro_m4.recovery import RecoveryGate, RecoverableSiwc
    from experiments.macro_m4.scoring import score
    from experiments.macro_capabilities_v2.observability import Meter, audit, trace_check
    from experiments.macro_capabilities_v2.runner import MissingSource, persisted, switch_trajectory
    from rosa_reliability.gazebo_demo import GazeboDemo
    from rosa_reliability.macro_agent import MacroROSA, InferenceLimits
    from rosa_reliability.bounded_macro import MacroLimits
    from rosa_reliability.ros_arm import ArmTransport, JOINTS
    from rosa_reliability.ros_readiness import ArmReadinessTransport

    m4.verify()                                         # all 62 frozen M4 files unchanged
    cases = load_cases()
    if control:
        folder = RUNS / 'controls'
        rows = [{'seq': i + 1, 'case': cid, 'model': 'deterministic', 'arm': arm}
                for i, (cid, arm) in enumerate((c, a) for c in sorted(cases) for a in ('primitives', 'macro'))]
        specs = {}
    else:
        verify_stage(stage)
        folder = RUNS / stage
        specs = {m['name']: m for m in models}
        rows = admitted_rows(stage, list(specs))
    folder.mkdir(parents=True, exist_ok=True)
    state = classify(folder, rows)
    status = {'stage': 'controls' if control else stage, 'status': 'STARTING', 'planned': len(rows),
              'previously_done': sum(v == 'DONE' for v in state.values()),
              'interrupted_not_rerun': [s for s, v in state.items() if v == 'INTERRUPTED'],
              'trials': [], 'reset_checks': [], 'model_switches': [], 'stopped_models': {}}
    caps = {} if control else ceilings(rows)
    budgets = {}

    def checkpoint(_=None):
        status['ledgers'] = {m: b.snapshot() for m, b in budgets.items()}
        dump(folder / 'status.json', status)

    for name in caps:
        budgets[name] = DCampaignBudget(checkpoint, request_cap=caps[name]['request_cap'],
                                        seconds_cap=caps[name]['seconds_cap'])
    simulator = GazeboDemo(folder / 'simulator')
    movement = inspection = observer = readiness_observer = None
    inactive, loaded, sol = False, None, None
    sol_context = None
    started = time.monotonic()
    try:
        simulator.start()
        movement, inspection = ArmTransport(), ArmReadinessTransport()
        observer, readiness_observer = ArmTransport(read_only=True), ArmReadinessTransport()
        status['status'] = 'RUNNING'
        for row in rows:
            if state[row['seq']] != 'UNSTARTED':
                continue
            if not may_start():
                status['deadline_reached'] = datetime.now(TAIPEI).isoformat()
                break
            name = row['model']
            if name in status['stopped_models']:
                continue
            if not control:
                verify_stage(stage)
            m4.verify()
            spec_model = specs.get(name)
            backend = 'scripted' if control else spec_model['backend']
            # ---- model plumbing (outside task)
            model, transport = None, None
            if backend == 'ollama':
                if loaded and loaded['name'] != name:
                    status['model_switches'].append({'before_seq': row['seq'], 'unloaded': loaded['name'],
                                                     'response': unload(loaded)})
                loaded = spec_model
                model = ollama_model(spec_model)
            elif backend == 'siwc':
                if sol is None:
                    from rosa_auth.remembered import remembered_session
                    from rosa_auth.protected_store import WindowsCredentialStore
                    from rosa_auth.oauth import SafeError
                    from rosa_backends.chat_siwc import ChatSiwc
                    store = WindowsCredentialStore('research').__enter__()
                    if store.load() is None:
                        raise SafeError('manual_sign_in_required_no_automatic_login')
                    sol_context = remembered_session(store=store, request_budget=caps[name]['request_cap'],
                                                     status=status.setdefault('sol_authorization', {}))
                    auth = sol_context.__enter__()
                    transport = RecoverableSiwc(token_provider=auth.access_token,
                                                request_budget=caps[name]['request_cap'])
                    sol = (ChatSiwc(model=spec_model.get('model', 'gpt-6.1-sol'), backend=transport), transport, store)
                model, transport = sol[0], sol[1]
                transport.raise_if_unavailable()
            case = cases[row['case']]
            spec, condition = case, row['arm']
            trial = folder / trial_name(row)
            trial.mkdir()
            status['current_trial'] = trial.name
            checkpoint()
            # ---- M4 outside-task setup (copied) + D reset check
            setup_started = time.monotonic()
            with m4.alarm(120):
                movement.suppress_commands = movement.partial_commands = movement.missing_observations = False
                movement.read('/ur5e', list(JOINTS))
                initial = registry().catalogue()[spec['initial']]['targets']['/ur5e']
                receipt = movement.write('/ur5e', initial)
                initial_observation = observer.read('/ur5e', list(JOINTS))
                if any(abs(initial_observation[k] - v) > TOLERANCE for k, v in initial.items()):
                    raise RuntimeError('m4_reset_not_independently_confirmed')
                management = None
                if spec['fault'] == 'inactive':
                    management = switch_trajectory(inspection, False)
                    inactive = True
                before_readiness = {**readiness_observer.read_group('controllers',
                    ['trajectory_controller_active', 'joint_state_broadcaster_active']),
                    **readiness_observer.read_group('joint_state', ['joint_sample_fresh'])}
            reset_failures = reset_check(spec, initial, initial_observation, before_readiness)
            status['reset_checks'].append({'seq': row['seq'], 'pass': not reset_failures, 'failures': reset_failures})
            dump(trial / 'outside-task-setup.json', {'trajectory_dispatches': 1, 'receipt': receipt,
                'independent_joints': initial_observation, 'independent_readiness': before_readiness,
                'controller_management': management, 'reset_check': reset_failures,
                'seconds': time.monotonic() - setup_started})
            if reset_failures:
                raise RuntimeError('d_reset_check_failed:' + ';'.join(reset_failures))
            # ---- M4 trial body (copied)
            movement.suppress_commands = spec['fault'] == 'ineffective'
            movement.partial_commands = spec['fault'] == 'partial'
            movement.missing_observations = spec['fault'] == 'missing_motion'
            reader = MissingSource(inspection, spec['fault']) if spec['fault'] in ('controllers', 'joint_state') else inspection
            offset = len(movement.records)
            meter, gate = Meter(), None
            task_started = time.monotonic()
            error = None
            with trace_check(trial / 'trace.json', {'stage': 'D-' + status['stage'], 'backend': name,
                    'condition': condition, 'case': spec['id'], 'repetition': 0, 'control': control}) as tracer:
                inv = registry().open({'state': movement, 'inspection': reader}, mode=condition,
                    allowed_skills=spec['allowed'], tracer=tracer, limits=MacroLimits(seconds=LIMITS['trial_seconds']))
                try:
                    with m4.alarm(LIMITS['trial_seconds']):
                        if control:
                            answer = m4.reference(inv, spec, condition, {'callbacks': [meter]})
                        else:
                            budget = budgets[name]
                            agent = MacroROSA(model, inv, backend=backend, callbacks=[meter])
                            gate = RecoveryGate(inv, backend=backend, limits=InferenceLimits(),
                                local_options=agent.inference_budget.local_options, campaign=budget,
                                release=transport.release_transient_failure if transport else None,
                                journal=lambda inference: dump(trial / 'inference-progress.json',
                                    {'inference': inference, 'snapshot': inv.snapshot()}))
                            agent.inference_budget = agent.completion_gate = gate
                            answer = agent.invoke(query(spec, condition))
                except Exception as exc:
                    error = type(exc).__name__
                    answer = 'Task interrupted: ' + error
                snapshot = inv.snapshot()
            wall = time.monotonic() - task_started
            if not control:
                budgets[name].active_seconds += wall
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
            out = {'row': row, 'case': spec['id'], 'family': spec['family'], 'd_type': spec['d_type'],
                'template_group': spec['template_group'], 'model': name, 'condition': condition,
                'model_label': ((spec_model or {}).get('adapter') or {}).get('label'),
                'request': spec['request'], 'answer': answer, 'snapshot': snapshot, 'inference': inference,
                'score': result, 'wall_seconds': wall, 'independent_joints': observed,
                'independent_readiness': readiness, 'movement_records': records, 'error_type': error,
                'local_audit': local, 'infrastructure_recovered': recovered,
                'primary_pass': result['pass'] and local['pass'] and not recovered,
                'completion_including_recovery': result['pass'] and local['pass']}
            dump(trial / 'audit.json', local)
            out['phoenix_audit'] = persisted(trial)
            if backend == 'ollama':
                out['offload'] = offload_record(spec_model)
            dump(trial / 'result.json', out)
            status['trials'].append({'seq': row['seq'], 'model': name, 'case': spec['id'], 'arm': condition,
                                     'primary_pass': out['primary_pass'], 'calls': inference['calls'], 'error': error})
            status['current_trial'] = None
            # ---- after-task restore + reset check (c), (d)
            if inactive:
                restore = switch_trajectory(inspection, True)
                dump(trial / 'outside-task-controller-restore.json', restore)
                inactive = False
            outside = [r for r in movement.records[offset + len(records):] if r['kind'] == 'trajectory_request']
            if outside:
                raise RuntimeError('d_reset_check_failed:dispatch_outside_task_window')
            checkpoint()
            print(json.dumps({'stage': status['stage'], 'seq': row['seq'], 'model': name, 'case': spec['id'],
                              'arm': condition, 'primary_pass': out['primary_pass'], 'calls': inference['calls']}),
                  flush=True)
            if not local['pass'] or not out['phoenix_audit'].get('pass'):
                raise RuntimeError('d_trace_audit_failed:' + trial.name)
            if control and not out['primary_pass']:
                raise RuntimeError('d_control_failed:' + trial.name)
            if not control and budgets[name].requests >= budgets[name].request_cap:
                status['stopped_models'][name] = 'request_ceiling_reached'
        if not control:
            verify_stage(stage)
        status['status'] = 'COMPLETE' if all(classify(folder, rows)[r['seq']] == 'DONE' for r in rows) else 'PARTIAL'
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__, error=str(error)[:500])
        raise
    finally:
        errors = []
        if inactive and inspection:
            try:
                switch_trajectory(inspection, True)
            except Exception as error:
                errors.append('controller_restore_' + type(error).__name__)
        for item in (movement, inspection, observer, readiness_observer):
            if item:
                try:
                    item.close()
                except Exception as error:
                    errors.append(type(error).__name__)
        if loaded:
            status['final_unload'] = unload(loaded)
        if sol:
            try:
                sol[0].close()
            except Exception as error:
                errors.append('sol_close_' + type(error).__name__)
            try:
                sol_context.__exit__(None, None, None)
                sol[2].__exit__(None, None, None)
            except Exception as error:
                errors.append('sol_session_' + type(error).__name__)
        status['cleanup_errors'] = errors
        status['simulator_cleanup'] = simulator.close()
        status['total_elapsed_seconds'] = time.monotonic() - started
        checkpoint()
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('plan', 'freeze', 'controls', 'live'))
    parser.add_argument('--stage', choices=('dev', 'heldout'))
    parser.add_argument('--models')
    args = parser.parse_args()
    models = json.loads(Path(args.models).read_text()) if args.models else None
    if args.action == 'plan':
        rows = admitted_rows(args.stage, [m['name'] for m in models])
        print(json.dumps({'stage': args.stage, 'rows': len(rows), 'ceilings': ceilings(rows)}, indent=1))
        return
    if args.action == 'freeze':
        write_freeze(args.stage, args.models)
        return
    os.environ.update(ROS_DOMAIN_ID=DOMAIN_ID, ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',
                      LANGCHAIN_TRACING='false', LANGCHAIN_TRACING_V2='false', LANGSMITH_TRACING='false')
    import fcntl
    with (D / 'gazebo.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.action == 'controls':
            run_stage(None, control=True)
        else:
            if args.stage == 'heldout':
                gate = json.loads((RUNS / 'dev' / 'D1_GATE.json').read_text())
                if not gate.get('pass'):
                    raise RuntimeError('d1_gate_not_passed_no_heldout')
            run_stage(args.stage, models=models)


if __name__ == '__main__':
    main()
