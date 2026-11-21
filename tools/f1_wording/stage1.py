"""F1 Stage 1 runner (G3). Study-local wrapper around the frozen G1 held-out trial procedure.

The trial body is the frozen G1 one (revision-1/stage-4/runner.py:trial and
stage-4-qwen-lab-20261119/trial.py:trial), with exactly these differences:
  * the agent is wording.make_agent(arm, ...): 'base' = frozen MacroROSA, 'new' = F1MacroROSA;
  * trial folders live under the F1 study (runs/<run>/trials/<id>);
  * the Phoenix project / root span are F1-specific (tools/f1_wording/persisted_audit.py);
  * the campaign request cap is 8 x planned trials + 3 reserve (PROTOCOL §10), not G1's 611;
  * backend 'scripted' replaces the model with the zero-request ScriptedCaller (dry run, D14).
Bounds, scorer, censoring, retry rights and the prompt construction are imported, never copied.

Subcommands (run inside the D12 WSL research env):
  plan    --run <name> --stage dev|heldout --backend qwen|sol|scripted [--arms base,new]
  execute --run <name> [--resume-unstarted] --i-am-authorized <token from the run's AUTHORIZATION.json>
A run directory is created once by 'plan' and never reused for a different plan.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import threading
import time
import urllib.request

HERE = Path(__file__).resolve().parent
REPO_F1 = HERE.parents[1]
STUDY = REPO_F1 / 'artifacts/f1-catalogue-wording-20261121'
WORKSPACE = Path(os.environ.get('F1_WORKSPACE', '/mnt/c/Proj/robotics/introtorobotics'))
G1 = WORKSPACE / 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1'
PHOENIX_PY = '/home/martin/.local/share/rosa-envs/phoenix/bin/python'
PHOENIX_URL = 'http://127.0.0.1:6006'
OLLAMA_ENDPOINT = os.environ.get('F1_OLLAMA_ENDPOINT', 'http://172.31.0.1:11440')
QWEN = 'qwen3.5:9b'
QWEN_DIGEST = '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'
HELDOUT_SEED = 20261121
LOCAL_OPTIONS = {'num_ctx': 8192, 'temperature': 0, 'seed': 42, 'use_mmap': True}
PROJECT = 'rosa-f1-stage1-20261121'
ROOT_SPAN = 'f1.stage1.trial'


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def sha_lf(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


# ---------------------------------------------------------------- plan

def load_cases(stage):
    if stage == 'heldout':
        return read(STUDY / 'cases/heldout.json')
    g1_cases = {c['case_id']: c for c in read(G1 / 'stage-1/cases.json')}
    dev = []
    for entry in read(STUDY / 'cases/dev.json')['cases']:
        c = deepcopy(g1_cases[entry['case_id']])
        c['f1_type'] = {'ladder': 'inspection_control', 'write': 'direct_movement',
                        'missing_prerequisite': 'movement_prerequisite'}.get(c['kind'], c['kind'])
        dev.append(c)
    return dev


def build_plan(stage, backend, arms):
    """Seeded case order (heldout: shuffle seed 20261121; dev: file order). Within a case the base/new
    order alternates by template group (sorted group index even -> base first), PROTOCOL §5.4 / D7."""
    cases = load_cases(stage)
    if stage == 'heldout':
        random.Random(HELDOUT_SEED).shuffle(cases)
    controls = {r['case_id']: r for r in read(STUDY / 'controls/CONTROL_ROWS.json')}
    groups = sorted({c['template_group'] for c in cases})
    plan = []
    for case in cases:
        order = ['base', 'new'] if groups.index(case['template_group']) % 2 == 0 else ['new', 'base']
        for arm in [a for a in order if a in arms]:
            ctrl = controls[case['case_id']][arm]
            plan.append({'id': f"{case['case_id']}-{arm}-{backend}", 'case_id': case['case_id'], 'arm': arm,
                         'backend': backend, 'mode': 'macro', 'stage': stage,
                         'template_group': case['template_group'], 'f1_type': case['f1_type'],
                         'expected_turns': ctrl['calls'], 'expected_native': ctrl['native_operations'],
                         'case': case})
    return plan


def cmd_plan(args):
    run = STUDY / 'runs' / args.run
    if run.exists():
        raise SystemExit(f'run directory exists; never reuse it: {run}')
    arms = args.arms.split(',')
    plan = build_plan(args.stage, args.backend, arms)
    run.mkdir(parents=True)
    write(run / 'plan.json', plan)
    import wording
    meta = {'run': args.run, 'stage': args.stage, 'backend': args.backend, 'arms': arms, 'trials': len(plan),
            'request_cap': 8 * len(plan) + 3, 'created_utc': now(), 'wording_revision': wording.WORDING_REVISION,
            'plan_sha256': hashlib.sha256((run / 'plan.json').read_bytes()).hexdigest(),
            'heldout_seed': HELDOUT_SEED if args.stage == 'heldout' else None,
            'execution_host': 'laptop (lab unavailable, D16): Windows 11 + WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB',
            'authorization_token': hashlib.sha256(f'{args.run}:{time.time()}'.encode()).hexdigest()[:16]}
    write(run / 'RUN_META.json', meta)
    print(json.dumps({k: v for k, v in meta.items() if k != 'authorization_token'}, indent=1))
    print('authorization token (pass to execute):', meta['authorization_token'])


# ---------------------------------------------------------------- backend wiring

def import_backend(backend):
    """Put the frozen G1 support modules for this backend on sys.path (they share module names, so one
    backend per process). 'scripted' uses the Qwen-lab support with the scripted gate backend."""
    source = G1 / ('stage-4' if backend == 'sol' else 'stage-4-qwen-lab-20261119')
    sys.path.insert(0, str(source))
    import common  # noqa: F401  (inserts the frozen G1 paths, exactly as G1 did)
    sys.path.insert(0, str(HERE))
    import tracing
    tracing.PROJECT, tracing.ROOT_SPAN = PROJECT, ROOT_SPAN
    return source, common


class F1Campaign:
    """G1 recovery.Campaign semantics with the F1 physical cap (8 x trials + 3) and 8 h wall budget."""

    def __init__(self, checkpoint, cap):
        from recovery import Campaign
        self.inner = Campaign(checkpoint)
        self.cap = cap

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def reserve(self):
        from rosa_reliability.execution import ControlledStop
        if self.inner.requests >= self.cap or time.monotonic() - self.inner.started >= 28800:
            raise ControlledStop('f1_campaign_request_or_time_budget_exhausted')
        self.inner.requests += 1
        self.inner.checkpoint(self.snapshot())

    def recovery(self, error):
        return self.inner.recovery(error)

    def snapshot(self):
        value = self.inner.snapshot()
        value['request_cap'] = self.cap
        return value


def scripted_model_class():
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, ChatResult

    class ScriptedCaller(BaseChatModel):
        """Same oracle as controls.py; zero live requests. Used only for the D14 dry run."""
        invocation: object = None
        case: dict = {}
        index: int = 0

        @property
        def _llm_type(self):
            return 'f1-scripted-no-live-model'

        @property
        def request_records(self):
            return []

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, **kwargs):
            index, self.index = self.index, self.index + 1
            usage = {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
            if self.case['kind'] == 'ambiguous':
                message = AIMessage(content='Should I inspect readiness or move to a registered target?',
                                    usage_metadata=usage, response_metadata={'finish_reason': 'stop'})
                return ChatResult(generations=[ChatGeneration(message=message)])
            definition = self.invocation.catalogue[self.case['skill_id']]
            inspection = definition['kind'] == 'read_only_inspection'
            if index == 0:
                name, call = 'select_skill', {'skill_id': self.case['skill_id']}
            else:
                observation = self.invocation.snapshot()['observations'][-1]
                flat = [v for fields in observation['observed_values'].values() for v in fields.values()]
                reached = (all(v == 1.0 for v in flat) if inspection else all(
                    observation['observed_values'][n][k] is not None and
                    abs(observation['observed_values'][n][k] - v) <= .025
                    for n, fields in definition['targets'].items() for k, v in fields.items()))
                status = 'UNKNOWN' if any(v is None for v in flat) else 'SUCCESS' if reached else 'FAILURE'
                name, call = 'submit_report', {'status': status, 'observation_id': observation['observation_id']}
            message = AIMessage(content='', tool_calls=[{'name': name, 'args': call, 'id': f'scripted-{index}',
                                'type': 'tool_call'}], usage_metadata=usage, response_metadata={'finish_reason': 'stop'})
            return ChatResult(generations=[ChatGeneration(message=message)])

    class NullTransport:
        error_metadata_records = []

        def release_transient_failure(self, error):
            raise RuntimeError('scripted_backend_has_no_transport')

    return ScriptedCaller, NullTransport


# ---------------------------------------------------------------- trial (frozen G1 body; see module doc)

def trial(run, item, model, transport, campaign):
    from worlds import create_world
    from catalogue import registry
    from scoring import score, ObserverEvidenceRequired
    from tracing import Meter, trace_check, audit
    from recovery import LoggedGate
    from runtime_support import journal_progress, freeze_raw_result
    from rosa_auth.oauth import SafeError
    from rosa_reliability.macro_agent import InferenceLimits
    from rosa_reliability.bounded_macro import MacroLimits
    from rosa_reliability.execution import ControlledStop
    from rosa_reliability.prompt_contract import bounded_contract, REQUIRED_TOOLS
    import wording

    trials = run / 'trials'
    folder = trials / item['id']
    folder.mkdir(parents=True)  # fails if the trial was ever started: no replacement
    case = item['case']
    started = time.monotonic()
    world, actor, observer = create_world(case['domain'], **case['world_configuration'])
    gate_backend = {'qwen': 'ollama', 'sol': 'siwc', 'scripted': 'scripted'}[item['backend']]
    if item['backend'] == 'scripted':
        model.case, model.index = case, 0
    record_start = len(model.request_records)
    metadata_start = len(transport.error_metadata_records)
    row = {'id': item['id'], 'mode': 'macro', 'case': case, 'backend': gate_backend,
           'model': {'qwen': QWEN, 'sol': 'gpt-6.1-sol', 'scripted': 'scripted-oracle'}[item['backend']],
           'f1_arm': item['arm'], 'f1_stage': item['stage'], 'f1_type': item['f1_type'],
           'wording_revision': wording.WORDING_REVISION if item['arm'] == 'new' else 'g1-frozen',
           'execution_host': 'laptop (lab unavailable, D16)',
           'expected_scripted_turns': item['expected_turns'], 'expected_scripted_native': item['expected_native'],
           'primary_pass': False, 'error': None,
           'decision_actor': 'scripted_fixture_oracle' if item['backend'] == 'scripted' else 'live_model'}
    timeout = {'fired': False}
    inv = gate = meter = None

    def expired(signum, frame):
        timeout['fired'] = True
        raise TimeoutError('f1_external_task_deadline')

    # G1 trial.py relative-write helpers resolve against their own ROOT; point them at this run.
    import common
    common.ROOT = run
    import runtime_support
    runtime_support.ROOT = run
    try:
        with trace_check(folder / 'trace.json', {'id': item['id'], 'backend': gate_backend,
                                                  'decision_actor': row['decision_actor']}) as tracer:
            meter = Meter(observer, tracer)
            meter.observe('before_agent')
            inv = registry(case['domain']).open({'state': actor, 'inspection': actor}, mode='macro',
                                                tracer=tracer, limits=MacroLimits(seconds=360.0))
            if item['backend'] == 'scripted':
                model.invocation = inv
            agent = wording.make_agent(item['arm'], model, inv, backend=gate_backend, callbacks=[meter])
            gate = LoggedGate(inv, backend=gate_backend, limits=InferenceLimits(), campaign=campaign,
                              local_options=LOCAL_OPTIONS if gate_backend == 'ollama' else None,
                              release=transport.release_transient_failure,
                              journal=lambda value: journal_progress(folder, value, inv, meter, actor, transport,
                                                                     metadata_start, timeout))
            agent.inference_budget = agent.completion_gate = gate
            contract = read(G1 / 'prompt-contract.json')
            assert bounded_contract(REQUIRED_TOOLS) == contract['system']
            query = (contract['rules'].removesuffix('\nUser: ') + ' Execution condition: macro. ' +
                     contract['condition_sentences']['macro'] + contract[case['domain'] + '_suffix'] + case['request'])
            row['query'] = query
            remaining = 28800 - (time.monotonic() - campaign.started)
            if remaining <= 0:
                raise ControlledStop('f1_backend_deadline')
            signal.signal(signal.SIGALRM, expired)
            signal.setitimer(signal.ITIMER_REAL, min(360, remaining))
            try:
                answer = agent.invoke(query)
            except Exception as error:
                row['error'] = {'type': type(error).__name__}
                if isinstance(error, (SafeError, ControlledStop)):
                    row['error']['code'] = error.code if isinstance(error, SafeError) else str(error)
                answer = 'Task interrupted: ' + type(error).__name__
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            meter.observe('after_agent')
            snapshot = inv.snapshot()
            inference = gate.snapshot()
        task_seconds = time.monotonic() - started
        scored = score(case, snapshot, answer, observer.records)
        refused = False
        try:
            score(case, snapshot, answer, actor.records)
        except ObserverEvidenceRequired:
            refused = True
        local = audit(snapshot, folder / 'trace.json', meter, inference, actor.records)
        failure = gate.terminal_failure
        if failure and row['error'] is None:
            row['error'] = failure
        codes = meter.execution_errors + ([failure.get('code', '')] if failure else [])
        scored['budget_exhaustion'] = bool(timeout['fired'] or any(
            'budget' in c or 'deadline' in c or 'threshold_exceeded' in c for c in codes) or
            (inference['decision_calls'] >= 8 and not any(r.get('accepted') for r in snapshot['reports'])))
        scored['length_stop'] = any(e.get('finish_reason') == 'length' for e in inference['events'])
        recovered = inference['infrastructure_failures'] > 0
        row.update(answer=answer, snapshot=snapshot, inference=inference, score=scored, local_audit=local,
                   task_seconds=task_seconds, timeout_fired=timeout['fired'], execution_error_codes=codes,
                   actual_turns=inference['calls'], actual_decision_turns=inference['decision_calls'],
                   turns_match_scripted_expectation=inference['calls'] == item['expected_turns'],
                   native_match_scripted_expectation=len(actor.records) == item['expected_native'],
                   actor_records=deepcopy(actor.records), observer_records=deepcopy(observer.records),
                   observer_tags=meter.observer_tags, tool_inputs=meter.tool_inputs, model_inputs=meter.model_inputs,
                   model_outputs=meter.model_outputs, model_errors=meter.model_errors,
                   sanitized_request_records=model.request_records[record_start:], actor_only_truth_rejected=refused,
                   infrastructure_recovered=recovered,
                   primary_pass=bool(scored['primary_pass'] and local['pass'] and refused and not recovered
                                     and not row['error'] and not timeout['fired']),
                   completion_including_recovery=bool(scored['primary_pass'] and local['pass'] and refused
                                                      and not row['error'] and not timeout['fired']))
        (folder / 'result.json').write_text(json.dumps(row, indent=2) + '\n')
        with (folder / 'phoenix-audit.log').open('w') as log:
            result = subprocess.run([PHOENIX_PY, '-B', str(HERE / 'persisted_audit.py'), str(folder),
                                     PROJECT, ROOT_SPAN], cwd=str(HERE), stdout=log, stderr=log, timeout=60)
        if (folder / 'phoenix-audit.json').exists():
            row['phoenix_audit'] = read(folder / 'phoenix-audit.json')
        if result.returncode:
            raise RuntimeError('persisted_trace_audit_failed')
        if not local['pass'] or not refused:
            raise RuntimeError('local_trace_or_observer_audit_failed')
        return row
    except BaseException as error:
        row['harness_error_type'] = type(error).__name__
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        row.setdefault('actor_records', deepcopy(actor.records))
        row.setdefault('observer_records', deepcopy(observer.records))
        if inv is not None:
            row.setdefault('snapshot', inv.snapshot())
        if gate is not None:
            row.setdefault('inference', gate.snapshot())
        row['trial_total_seconds'] = time.monotonic() - started
        freeze_raw_result(row, folder, transport, metadata_start)
        (folder / 'result.json').write_text(json.dumps(row, indent=2) + '\n')


# ---------------------------------------------------------------- telemetry and readiness

def http_json(url, timeout=5):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=timeout) as response:
        return json.loads(response.read().decode())


def gpu_sample():
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
                              '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10).stdout
        used, total, util = [x.strip() for x in out.strip().split(',')]
        return {'vram_used_mib': int(used), 'vram_total_mib': int(total), 'gpu_util_pct': int(util)}
    except Exception as error:
        return {'error': type(error).__name__}


class Telemetry(threading.Thread):
    def __init__(self, path, with_ollama):
        super().__init__(daemon=True)
        self.path, self.with_ollama, self.stop_event = path, with_ollama, threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            sample = {'utc': now(), **gpu_sample()}
            if self.with_ollama:
                try:
                    sample['ollama_ps'] = [{k: m.get(k) for k in ('name', 'digest', 'size', 'size_vram', 'context_length')}
                                           for m in http_json(OLLAMA_ENDPOINT + '/api/ps')['models']]
                except Exception as error:
                    sample['ollama_ps_error'] = type(error).__name__
            with self.path.open('a') as f:
                f.write(json.dumps(sample) + '\n')
            self.stop_event.wait(10)


def readiness(backend):
    """Read-only checks before a live block (LAB_PLAN §3, laptop form)."""
    record = {'utc': now(), 'backend': backend, 'gpu': gpu_sample()}
    if backend == 'qwen':
        record['ollama_version'] = http_json(OLLAMA_ENDPOINT + '/api/version')['version']
        tags = {m['name']: m['digest'] for m in http_json(OLLAMA_ENDPOINT + '/api/tags')['models']}
        record['qwen_digest'] = tags.get(QWEN)
        record['serving'] = dict(LOCAL_OPTIONS, think=False, num_predict_per_call_max=1024, endpoint=OLLAMA_ENDPOINT)
        if record['ollama_version'] != '0.40.6' or record['qwen_digest'] != QWEN_DIGEST:
            raise SystemExit('readiness_failed: ' + json.dumps(record))
    try:
        http_json(PHOENIX_URL + '/healthz')
        record['phoenix'] = 'healthy'
    except Exception:
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(PHOENIX_URL + '/healthz', timeout=5) as r:
                record['phoenix'] = 'healthy' if r.status == 200 else f'status {r.status}'
        except Exception as error:
            raise SystemExit('readiness_failed: phoenix not reachable: ' + type(error).__name__)
    return record


KNOWN_DOC_DRIFT = {
    # Edited by commit 37a7e19 (2026-11-20, "M4/M5 corrections"), before tag freeze-2026-11-21; an M5 status
    # note, not code and not a G1 input. Recorded in STATUS.md and the F1 run report.
    'rosa-evaluation/artifacts/macro-m5-20261027/status.json',
}


def g1_freeze_check(source):
    """Hash every file in the G1 stage-4 freeze (+ the backend seal). Stop on any mismatch in code or in
    the G1 study tree; record (never hide) the known pre-freeze documentation edit."""
    names = dict(read(G1 / 'stage-4/freeze.json')['files_sha256'])
    seal = source / 'freeze.json'
    if seal.exists() and source.name != 'stage-4':
        base = source.relative_to(WORKSPACE)
        names.update({f'{base.as_posix()}/{n}': d for n, d in read(seal)['files_sha256'].items()})
    bad = [n for n, d in names.items() if hashlib.sha256((WORKSPACE / n).read_bytes()).hexdigest() != d]
    fatal = [n for n in bad if n not in KNOWN_DOC_DRIFT]
    if fatal:
        raise SystemExit('g1 frozen input mismatch: ' + repr(fatal))
    return {'files': len(names), 'mismatches': bad, 'known_doc_drift_recorded': sorted(set(bad) & KNOWN_DOC_DRIFT)}


# ---------------------------------------------------------------- execute

def cmd_execute(args):
    run = STUDY / 'runs' / args.run
    meta = read(run / 'RUN_META.json')
    if args.i_am_authorized != meta['authorization_token']:
        raise SystemExit('authorization token does not match RUN_META.json')
    assert hashlib.sha256((run / 'plan.json').read_bytes()).hexdigest() == meta['plan_sha256'], 'plan changed'
    backend = meta['backend']
    source, common = import_backend(backend)
    sys.path.insert(0, str(HERE))
    from controls import check_frozen_inputs
    frozen = check_frozen_inputs(WORKSPACE)
    g1_check = g1_freeze_check(source)
    import wording
    if meta['wording_revision'] != wording.WORDING_REVISION:
        raise SystemExit('wording revision changed since plan; plan a new run')
    status_path = run / 'status.json'
    if args.resume_unstarted:
        status = read(status_path)
        assert status['status'] == 'STOPPED', 'resume only a STOPPED run'
    else:
        assert not (run / 'RUN_ONCE').exists(), 'run already started; use --resume-unstarted'
        (run / 'RUN_ONCE').write_text('No replacement of completed or censored trials.\n')
        status = {'status': 'STARTING', 'planned': meta['trials'], 'completed': 0, 'started_utc': now(),
                  'current_trial': None, 'phases': []}
    ready = readiness(backend)
    phase = {'started_utc': now(), 'readiness': ready, 'frozen_inputs_verified': frozen, 'g1_freeze_check': g1_check}
    status['phases'].append(phase)

    def checkpoint(budget):
        status['campaign'] = budget
        status['live_model_requests'] = budget['reserved_requests'] if backend != 'scripted' else 0
        write(status_path, status)

    campaign = F1Campaign(checkpoint, meta['request_cap'])
    if args.resume_unstarted:
        campaign.inner.requests = status['campaign']['reserved_requests']
        campaign.inner.retries = status['campaign']['infrastructure_retries']
        campaign.inner.events = status['campaign']['events']
        origin = datetime.fromisoformat(status['started_utc'])
        campaign.inner.started = time.monotonic() - (datetime.now(timezone.utc) - origin).total_seconds()
    retained = {p.parent.name for p in (run / 'trials').glob('*/result.json')}
    started_dirs = {p.name for p in (run / 'trials').glob('*') if p.is_dir()}
    if started_dirs - retained:
        raise SystemExit('a started trial has no result; inspect before resuming: ' + repr(sorted(started_dirs - retained)))
    telemetry = Telemetry(run / 'telemetry.jsonl', with_ollama=backend == 'qwen')
    telemetry.start()
    model = transport = None
    auth_status = {}
    stack = None
    try:
        if backend == 'qwen':
            from local_model import MeasuredOllama, LocalObservation
            transport = LocalObservation()
            model = MeasuredOllama(model=QWEN, base_url=OLLAMA_ENDPOINT, num_ctx=8192, num_predict=1024,
                                   temperature=0, seed=42, use_mmap=True, streaming=False, reasoning=False,
                                   cache=False, client_kwargs={'timeout': 180}).observe_with(transport)
        elif backend == 'scripted':
            ScriptedCaller, NullTransport = scripted_model_class()
            model, transport = ScriptedCaller(cache=False), NullTransport()
        else:
            from contextlib import ExitStack
            from authorization import restore_only, check_models, MODEL
            from recovery import RecoverableSiwc
            from rosa_backends.chat_siwc import ChatSiwc
            stack = ExitStack()
            active = stack.enter_context(restore_only(auth_status))
            check_models(active, auth_status)
            write(run / f"authorization-status-phase{len(status['phases'])}.json", auth_status)
            transport = RecoverableSiwc(token_provider=active.access_token, request_budget=meta['request_cap'])
            model = ChatSiwc(model=MODEL, backend=transport)
        status['status'] = 'RUNNING'
        stop_file = run / 'STOP_REQUESTED'
        for item in read(run / 'plan.json'):
            if item['id'] in retained:
                continue
            if stop_file.exists():
                raise KeyboardInterrupt('stop requested between trials')
            if backend == 'sol':
                transport.raise_if_unavailable()
            status['current_trial'] = item['id']
            checkpoint(campaign.snapshot())
            before = len(transport.error_metadata_records)
            row = trial(run, item, model, transport, campaign)
            retained.add(item['id'])
            status['completed'] = len(retained)
            status['current_trial'] = None
            checkpoint(campaign.snapshot())
            print(json.dumps({'utc': now(), 'completed': len(retained), 'planned': meta['trials'], 'id': item['id'],
                              'primary_pass_raw': row['primary_pass'], 'calls': row['inference']['calls'],
                              'length_stop': row['score'].get('length_stop'), 'task_s': round(row['task_seconds'], 1),
                              'charged_total': campaign.requests}), flush=True)
            if hasattr(model, 'request_records'):
                write(run / f"physical-call-journal-phase{len(status['phases'])}.json", model.request_records)
            if len(transport.error_metadata_records) > before:
                raise RuntimeError('transport_failure_preserved_inspect_before_unstarted_resume')
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__, error=str(error)[:300])
        raise
    finally:
        telemetry.stop_event.set()
        phase['ended_utc'] = now()
        phase['gpu_after'] = gpu_sample()
        status['completed_utc'] = now()
        checkpoint(campaign.snapshot())
        if hasattr(model, 'request_records') and model is not None:
            write(run / f"physical-call-journal-phase{len(status['phases'])}.json", model.request_records)
        if backend == 'sol':
            try:
                if model is not None:
                    model.close()
                elif transport is not None:
                    transport.close()
            finally:
                if stack is not None:
                    stack.close()
                write(run / f"authorization-status-phase{len(status['phases'])}.json", auth_status)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--run', required=True)
    p.add_argument('--stage', choices=('dev', 'heldout'), required=True)
    p.add_argument('--backend', choices=('qwen', 'sol', 'scripted'), required=True)
    p.add_argument('--arms', default='base,new')
    e = sub.add_parser('execute')
    e.add_argument('--run', required=True)
    e.add_argument('--resume-unstarted', action='store_true')
    e.add_argument('--i-am-authorized', required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(HERE))
    {'plan': cmd_plan, 'execute': cmd_execute}[args.cmd](args)


if __name__ == '__main__':
    main()
