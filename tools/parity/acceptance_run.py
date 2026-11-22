"""Parity Phase B runner (session A). Frozen G1 multi-model trial procedure on the laptop (D16 / PX-1).

The trial body is the frozen G1 one (revision-1/stage-4-multimodel-20261119/backends/<m>/trial.py), with
exactly these differences:
  * the model tag is a parameter (one model per run), and the trial folder is phase-b-runs/<run>/trials/<id>;
  * adapter 'native-schema-v1' (Llama, Granite) = rosa-research 8713f9b ToolContractProfile mixed into the frozen
    G1 MeasuredOllama, exactly as integration-rerun-20261117-r1/preparation/campaign.py did; adapter 'plain'
    (Qwen, Ministral) = the frozen G1 MeasuredOllama unchanged;
  * the Phoenix project / root span are parity-specific; the campaign cap is 8 x trials + 3 reserve;
  * the order is the frozen ACCEPTANCE_CRITERIA.md §3 list (or the scratch file order for scratch runs).
Agent, prompts, catalogue, tools, bounds, scorer, censoring and retry rights are imported, never copied.

  plan    --run <name> --set acceptance|scratch --model <tag> --adapter plain|native-schema-v1 [--cases ids]
  execute --run <name> --i-am-authorized <token> [--resume-unstarted]
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import urllib.request

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STUDY = REPO / 'artifacts/parity-integration-20261121'
RUNS = STUDY / 'phase-b-runs'
WORKSPACE = Path(os.environ.get('PARITY_WORKSPACE', '/mnt/c/Proj/robotics/introtorobotics'))
G1 = WORKSPACE / 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1'
SUPPORT = G1 / 'stage-4-qwen-lab-20261119'
RESEARCH = WORKSPACE / 'rosa-research'
PHOENIX_PY = '/home/martin/.local/share/rosa-envs/phoenix/bin/python'
OLLAMA_ENDPOINT = os.environ.get('PARITY_OLLAMA_ENDPOINT', 'http://172.31.0.1:11440')
LOCAL_OPTIONS = {'num_ctx': 8192, 'temperature': 0, 'seed': 42, 'use_mmap': True}
PROJECT = 'rosa-parity-phase-b-20261121'
ROOT_SPAN = 'parity.phase_b.trial'
DIGESTS = {'qwen3.5:9b': '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90',
           'ministral-3:8b-instruct-2512-q4_K_M': '1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71',
           'granite3.3:8b': 'fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7',
           'llama3.1:8b-instruct-q4_K_M': '46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e'}
ADAPTER_FILE = RESEARCH / 'src/rosa_backends/tool_contract_ollama.py'
ADAPTER_SHA256 = None  # filled at freeze time by the plan command and checked at execute
# ACCEPTANCE_CRITERIA.md §3 (authoritative list; P = primitives, M = macro)
ACCEPTANCE_ORDER = ('acc-007 P, acc-009 M, acc-004 P, acc-002 M, acc-004 M, acc-003 P, acc-007 M, acc-006 P, '
                    'acc-005 M, acc-008 P, acc-010 M, acc-008 M, acc-001 P, acc-001 M, acc-010 P, acc-002 P, '
                    'acc-006 M, acc-005 P, acc-003 M, acc-009 P')
LOW_DISK_GB = 3.0
DEADLINE_UTC = datetime(2026, 11, 22, 22, 0, tzinfo=timezone.utc)  # = Mon 2026-11-23 06:00 Taipei
G1_PLANS = G1 / 'stage-4-multimodel-20261119/backends'


def now():
    return datetime.now(timezone.utc).isoformat()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + '.tmp')
    t.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    os.replace(t, p)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def research_commit():
    return {'commit': git('rev-parse', 'HEAD', cwd=RESEARCH), 'branch': git('rev-parse', '--abbrev-ref', 'HEAD', cwd=RESEARCH),
            'dirty_src': bool(git('status', '--porcelain', '--', 'src', cwd=RESEARCH)),
            'tool_contract_ollama_sha256': sha(ADAPTER_FILE)}


def check_task_hashes():
    sums = {}
    for line in (STUDY / 'tasks/SHA256SUMS.txt').read_text().splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            sums[name.lstrip('*').strip()] = digest
    bad = [n for n, d in sums.items() if sha(STUDY / 'tasks' / Path(n).name) != d]
    if bad:
        raise SystemExit('task hash mismatch: ' + repr(bad))
    return sums


def disk_free_gb(path):
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize / 1e9


def build_plan(task_set, model, adapter, only):
    if task_set == 'g1-heldout':
        # Phase C: the frozen G1 multi-model held-out plan for this model, same items and order as G1.
        slug = {'granite3.3': 'granite', 'llama3.1': 'llama', 'ministral-3': 'ministral'}[model.split(':')[0]]
        g1 = read(G1_PLANS / slug / 'plan.json')
        key = model.split(':')[0].replace('.', '')
        return [dict(item, id=f"{item['id']}-{key}-adapted", g1_id=item['id'], model=model, adapter=adapter,
                     task_set=task_set, case_id=item['case']['case_id']) for item in g1]
    tasks = {t['case_id']: t for t in read(STUDY / f'tasks/{task_set}.json')}
    if task_set == 'acceptance':
        order = [(f"PAR-{x.split()[0]}", {'P': 'primitives', 'M': 'macro'}[x.split()[1]])
                 for x in ACCEPTANCE_ORDER.split(', ')]
    else:
        ids = [i for i in tasks if not only or i in only]
        order = [(i, m) for i in ids for m in ('primitives', 'macro')]
    key = model.split(':')[0].replace('.', '')
    return [{'id': f'{cid}-{mode}-{key}', 'case_id': cid, 'mode': mode, 'model': model, 'adapter': adapter,
             'task_set': task_set, 'expected_turns': None, 'expected_native': None, 'case': tasks[cid]}
            for cid, mode in order]


def cmd_plan(a):
    run = RUNS / a.run
    if run.exists():
        raise SystemExit('run directory exists; never reused')
    if a.task_set == 'acceptance' and a.cases:
        raise SystemExit('the acceptance test always runs all 20 trials')
    if a.adapter == 'native-schema-v1' and a.model.split(':')[0] not in ('llama3.1', 'granite3.3'):
        raise SystemExit('native-schema-v1 supports llama3.1 and granite3.3 only')
    hashes = check_task_hashes()
    if a.task_set == 'g1-heldout' and a.cases:
        raise SystemExit('Phase C always runs the whole frozen G1 plan')
    plan = build_plan(a.task_set, a.model, a.adapter, set(a.cases.split(',')) if a.cases else None)
    run.mkdir(parents=True)
    write(run / 'plan.json', plan)
    meta = {'run': a.run, 'task_set': a.task_set, 'model': a.model, 'model_digest_expected': DIGESTS[a.model],
            'adapter': a.adapter, 'adapter_sha256': sha(ADAPTER_FILE) if a.adapter != 'plain' else None,
            'rosa_research': research_commit(), 'trials': len(plan), 'request_cap': 611 if a.task_set == 'g1-heldout' else 8 * len(plan) + 3,
            'task_hashes': hashes, 'created_utc': now(),
            'plan_sha256': sha(run / 'plan.json'), 'runner_sha256': sha(Path(__file__)),
            'execution_host': 'laptop (lab unavailable, D16): Windows 11 + WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB',
            'authorization_token': hashlib.sha256(f'{a.run}:{time.time()}'.encode()).hexdigest()[:16]}
    write(run / 'RUN_META.json', meta)
    print(json.dumps({k: v for k, v in meta.items() if k not in ('authorization_token', 'task_hashes')}, indent=1))
    print('authorization token:', meta['authorization_token'])


def import_support():
    sys.path.insert(0, str(SUPPORT))
    import common  # noqa: F401  (frozen G1 path setup)
    import tracing
    tracing.PROJECT, tracing.ROOT_SPAN = PROJECT, ROOT_SPAN
    return common


class Campaign:
    def __init__(self, checkpoint, cap):
        from recovery import Campaign as G1Campaign
        self.inner, self.cap = G1Campaign(checkpoint), cap

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def reserve(self):
        from rosa_reliability.execution import ControlledStop
        if self.inner.requests >= self.cap or time.monotonic() - self.inner.started >= 28800:
            raise ControlledStop('parity_campaign_request_or_time_budget_exhausted')
        self.inner.requests += 1
        self.inner.checkpoint(self.snapshot())

    def recovery(self, error):
        return self.inner.recovery(error)

    def snapshot(self):
        v = self.inner.snapshot()
        v['request_cap'] = self.cap
        return v


class WireCapture:
    """httpx transport that records every Ollama request/response body (as integration-rerun-20261117-r1
    campaign.py WireCapture). Observation only: the bytes returned to the client are unchanged. Needed to
    report the SDK's argument normalization (ChatOllama _parse_arguments_from_tool_call) separately."""

    def __init__(self, folder):
        import httpx
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.count = len(list(self.folder.glob('*.json')))
        self.inner = httpx.HTTPTransport(retries=0)

    def handle_request(self, request):
        self.count += 1
        path = self.folder / f'{self.count:05d}.json'
        row = {'request': json.loads(request.content or b'{}'), 'status': 'STARTED', 'utc': now()}
        write(path, row)
        try:
            response = self.inner.handle_request(request)
            payload = response.read()
            text = payload.decode('utf-8', errors='replace')
            row.update(status='RETURNED', http_status=response.status_code,
                       response=[json.loads(l) for l in text.splitlines() if l.strip()])
            import httpx
            return httpx.Response(response.status_code, headers=response.headers, content=payload,
                                  request=request, extensions=response.extensions)
        except BaseException as error:
            row.update(status='ERROR', error_type=type(error).__name__)
            raise
        finally:
            write(path, row)

    def close(self):
        self.inner.close()


def attach_wire(model, folder):
    import httpx
    import ollama
    model._client = ollama.Client(host=OLLAMA_ENDPOINT, timeout=180, transport=WireCapture(folder))
    return model


def make_model(model, adapter):
    from local_model import MeasuredOllama, LocalObservation
    transport = LocalObservation()
    kwargs = dict(model=model, base_url=OLLAMA_ENDPOINT, num_ctx=8192, num_predict=1024, temperature=0, seed=42,
                  use_mmap=True, streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
    if adapter == 'plain':
        return MeasuredOllama(**kwargs).observe_with(transport), transport
    sys.path.insert(0, str(RESEARCH / 'src'))
    from rosa_backends.tool_contract_ollama import ToolContractProfile, PROFILE_VERSION
    assert PROFILE_VERSION == 'native-schema-v1'

    class ProfiledMeasuredOllama(ToolContractProfile, MeasuredOllama):
        pass
    return ProfiledMeasuredOllama(**kwargs).observe_with(transport), transport


def trial(run, item, model, transport, campaign):
    from worlds import create_world
    from catalogue import registry
    from scoring import score, ObserverEvidenceRequired
    from tracing import Meter, trace_check, audit
    from recovery import LoggedGate
    from runtime_support import journal_progress, freeze_raw_result
    from rosa_auth.oauth import SafeError
    from rosa_reliability.macro_agent import MacroROSA, InferenceLimits
    from rosa_reliability.bounded_macro import MacroLimits
    from rosa_reliability.execution import ControlledStop
    from rosa_reliability.prompt_contract import bounded_contract, REQUIRED_TOOLS
    import common
    import runtime_support
    common.ROOT = runtime_support.ROOT = run

    folder = run / 'trials' / item['id']
    folder.mkdir(parents=True)
    case = item['case']
    started = time.monotonic()
    world, actor, observer = create_world(case['domain'], **case['world_configuration'])
    record_start = len(model.request_records)
    metadata_start = len(transport.error_metadata_records)
    row = {'id': item['id'], 'mode': item['mode'], 'case': case, 'backend': 'ollama', 'model': item['model'],
           'adapter': item['adapter'], 'task_set': item['task_set'], 'execution_host': 'laptop (lab unavailable, D16)',
           'expected_scripted_turns': item.get('expected_turns'), 'expected_scripted_native': item.get('expected_native'),
           'g1_id': item.get('g1_id'), 'label': 'adapted-integration rerun (laptop)' if item['task_set'] == 'g1-heldout' else None,
           'primary_pass': False, 'error': None, 'decision_actor': 'live_model'}
    timeout = {'fired': False}
    inv = gate = meter = None

    def expired(signum, frame):
        timeout['fired'] = True
        raise TimeoutError('parity_external_task_deadline')

    try:
        with trace_check(folder / 'trace.json', {'id': item['id'], 'backend': 'ollama', 'decision_actor': 'live_model'}) as tracer:
            meter = Meter(observer, tracer)
            meter.observe('before_agent')
            inv = registry(case['domain']).open({'state': actor, 'inspection': actor}, mode=item['mode'],
                                                tracer=tracer, limits=MacroLimits(seconds=360.0))
            agent = MacroROSA(model, inv, backend='ollama', callbacks=[meter])
            gate = LoggedGate(inv, backend='ollama', limits=InferenceLimits(), campaign=campaign, local_options=LOCAL_OPTIONS,
                              release=transport.release_transient_failure,
                              journal=lambda value: journal_progress(folder, value, inv, meter, actor, transport,
                                                                     metadata_start, timeout))
            agent.inference_budget = agent.completion_gate = gate
            contract = read(G1 / 'prompt-contract.json')
            assert bounded_contract(REQUIRED_TOOLS) == contract['system']
            query = (contract['rules'].removesuffix('\nUser: ') + f' Execution condition: {item["mode"]}. ' +
                     contract['condition_sentences'][item['mode']] + contract[case['domain'] + '_suffix'] + case['request'])
            row['query'] = query
            remaining = 28800 - (time.monotonic() - campaign.started)
            if remaining <= 0:
                raise ControlledStop('parity_backend_deadline')
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
            result = subprocess.run([PHOENIX_PY, '-B', str(HERE / 'persisted_audit.py'), str(folder), PROJECT, ROOT_SPAN],
                                    cwd=str(HERE), stdout=log, stderr=log, timeout=60)
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


def http_json(url, timeout=5):
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=timeout) as r:
        return json.loads(r.read().decode())


def gpu_sample():
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
                              '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10).stdout
        used, total, util = [x.strip() for x in out.strip().split(',')]
        return {'vram_used_mib': int(used), 'vram_total_mib': int(total), 'gpu_util_pct': int(util)}
    except Exception as error:
        return {'error': type(error).__name__}


class Telemetry(threading.Thread):
    def __init__(self, path):
        super().__init__(daemon=True)
        self.path, self.stop_event = path, threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            s = {'utc': now(), **gpu_sample()}
            try:
                s['ollama_ps'] = [{k: m.get(k) for k in ('name', 'digest', 'size', 'size_vram', 'context_length')}
                                  for m in http_json(OLLAMA_ENDPOINT + '/api/ps')['models']]
            except Exception as error:
                s['ollama_ps_error'] = type(error).__name__
            with self.path.open('a') as f:
                f.write(json.dumps(s) + '\n')
            self.stop_event.wait(10)


def cmd_execute(a):
    run = RUNS / a.run
    meta = read(run / 'RUN_META.json')
    if a.i_am_authorized != meta['authorization_token']:
        raise SystemExit('authorization token mismatch')
    assert sha(run / 'plan.json') == meta['plan_sha256'], 'plan changed'
    check_task_hashes()
    rr = research_commit()
    if meta['adapter'] != 'plain' and rr['tool_contract_ollama_sha256'] != meta['adapter_sha256']:
        raise SystemExit('adapter changed since plan (frozen SHA-256 mismatch)')
    if rr['dirty_src']:
        raise SystemExit('rosa-research src has uncommitted changes; runs must cite an exact commit')
    common = import_support()
    version = http_json(OLLAMA_ENDPOINT + '/api/version')['version']
    tags = {m['name']: m['digest'] for m in http_json(OLLAMA_ENDPOINT + '/api/tags')['models']}
    if version != '0.40.6' or tags.get(meta['model']) != DIGESTS[meta['model']]:
        raise SystemExit(f'readiness failed: version {version}, digest {tags.get(meta["model"])}')
    status_path = run / 'status.json'
    if a.resume_unstarted:
        status = read(status_path)
        assert status['status'] == 'STOPPED'
    else:
        assert not (run / 'RUN_ONCE').exists()
        (run / 'RUN_ONCE').write_text('No replacement of completed or censored trials.\n')
        status = {'status': 'STARTING', 'planned': meta['trials'], 'completed': 0, 'started_utc': now(), 'phases': []}
    phase = {'started_utc': now(), 'ollama_version': version, 'model_digest': tags[meta['model']],
             'rosa_research': rr, 'gpu': gpu_sample(), 'disk_free_gb': round(disk_free_gb(str(run)), 1)}
    status['phases'].append(phase)

    def checkpoint(budget):
        status['campaign'] = budget
        status['live_model_requests'] = budget['reserved_requests']
        write(status_path, status)

    campaign = Campaign(checkpoint, meta['request_cap'])
    if a.resume_unstarted:
        c = status['campaign']
        campaign.inner.requests, campaign.inner.retries, campaign.inner.events = c['reserved_requests'], c['infrastructure_retries'], c['events']
        origin = datetime.fromisoformat(status['started_utc'])
        campaign.inner.started = time.monotonic() - (datetime.now(timezone.utc) - origin).total_seconds()
    retained = {p.parent.name for p in (run / 'trials').glob('*/result.json')}
    started_dirs = {p.name for p in (run / 'trials').glob('*') if p.is_dir()}
    if started_dirs - retained:
        raise SystemExit('started trial without result: ' + repr(sorted(started_dirs - retained)))
    telemetry = Telemetry(run / 'telemetry.jsonl')
    telemetry.start()
    model, transport = make_model(meta['model'], meta['adapter'])
    attach_wire(model, run / 'wire')
    journal = run / f"physical-call-journal-phase{len(status['phases'])}.json"
    try:
        status['status'] = 'RUNNING'
        for item in read(run / 'plan.json'):
            if item['id'] in retained:
                continue
            if (run / 'STOP_REQUESTED').exists():
                raise KeyboardInterrupt('stop requested between trials')
            if datetime.now(timezone.utc) >= DEADLINE_UTC:
                raise KeyboardInterrupt('deadline Mon 2026-11-23 06:00 Taipei reached; no new trial starts')
            free = disk_free_gb(str(run))
            if free < LOW_DISK_GB:
                raise KeyboardInterrupt(f'disk free {free:.1f} GB < {LOW_DISK_GB} GB; stopped between trials')
            status['current_trial'] = item['id']
            checkpoint(campaign.snapshot())
            before = len(transport.error_metadata_records)
            row = trial(run, item, model, transport, campaign)
            retained.add(item['id'])
            status['completed'], status['current_trial'] = len(retained), None
            checkpoint(campaign.snapshot())
            print(json.dumps({'utc': now(), 'done': len(retained), 'planned': meta['trials'], 'id': item['id'],
                              'pass_raw': row['primary_pass'], 'calls': row['inference']['calls'],
                              'tool_calls': sum(len(o.get('tool_calls') or []) for o in row['model_outputs']),
                              'task_s': round(row['task_seconds'], 1)}), flush=True)
            write(journal, model.request_records)
            if len(transport.error_metadata_records) > before:
                raise RuntimeError('transport_failure_preserved_inspect_before_unstarted_resume')
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__, error=str(error)[:300])
        raise
    finally:
        telemetry.stop_event.set()
        phase.update(ended_utc=now(), gpu_after=gpu_sample(), disk_free_gb_after=round(disk_free_gb(str(run)), 1))
        checkpoint(campaign.snapshot())
        write(journal, model.request_records)


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest='cmd', required=True)
    a = s.add_parser('plan')
    a.add_argument('--run', required=True)
    a.add_argument('--set', dest='task_set', choices=('acceptance', 'scratch', 'g1-heldout'), required=True)
    a.add_argument('--model', choices=tuple(DIGESTS), required=True)
    a.add_argument('--adapter', choices=('plain', 'native-schema-v1'), required=True)
    a.add_argument('--cases')
    e = s.add_parser('execute')
    e.add_argument('--run', required=True)
    e.add_argument('--i-am-authorized', required=True)
    e.add_argument('--resume-unstarted', action='store_true')
    args = p.parse_args()
    {'plan': cmd_plan, 'execute': cmd_execute}[args.cmd](args)


if __name__ == '__main__':
    main()
