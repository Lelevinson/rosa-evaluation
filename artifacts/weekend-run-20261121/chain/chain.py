"""Weekend overnight chain (session A). Deterministic: every gate is checked by code against the frozen
criteria; PASS continues, any failure or stop condition halts that track with a STATUS.md entry, and tracks
that do not depend on it continue. Claude only monitors and reports.

Run detached in WSL tmux (research env):  chain.py run      |  chain.py status
Resume after an interruption: launch the same command; completed stages (gates/<stage>.json with
"done": true) are skipped, runners resume only unstarted trials, and a live chain refuses a second copy.

Tracks and order (one GPU, one local model at a time):
  F1   : F1-H  Qwen held-out (GPU) with the Sol held-out arms in parallel (no GPU); then F1 analysis
  PAR  : PB-<model> acceptance (Granite, Llama: native-schema-v1; Qwen, Ministral: plain) -> admission
         PC-<model> Phase C G1 held-out rerun for admitted Granite/Llama -> frozen G1 summary
  GZ   : D1-controls -> D1-freeze-dev -> D1-dev (+ D1 gate) -> D2-freeze -> D2-heldout (+ frozen analysis)
Not in the chain (judgment, done by Claude before launch): F1 dev revision decision + wording freeze
(F1_STAGE1B_FREEZE.json), any Phase B adapter iteration. A model failing acceptance is simply not admitted.
"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.request

WS = Path('/mnt/c/Proj/robotics/introtorobotics')
WR = WS / 'weekend-run-20261121'
GATES, LOGS = WR / 'gates', WR / 'logs'
STATUS_MD = WR / 'STATUS.md'
LOCK = WR / 'chain' / 'chain.lock'
PY = '/home/martin/.local/share/rosa-envs/research/bin/python'
F1_WT = WS / 'wt-a-f1'
PAR_WT = WS / 'wt-a-parity'
GZ_WT = WS / 'wt-a-gazebo'
F1_STUDY = F1_WT / 'artifacts/f1-catalogue-wording-20261121'
PAR_STUDY = PAR_WT / 'artifacts/parity-integration-20261121'
GZ_STUDY = GZ_WT / 'artifacts/gazebo-d-20261121'
OLLAMA = 'http://172.31.0.1:11440'
PHOENIX = 'http://127.0.0.1:6006/healthz'
TAIPEI = timezone(timedelta(hours=8))
DEADLINE = datetime(2026, 11, 23, 6, 0, tzinfo=TAIPEI)
DISK_FLOOR_GB = 3.0
MODELS = {  # tag, G1 digest, Phase B adapter
    'granite': ('granite3.3:8b', 'fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7', 'native-schema-v1'),
    'llama': ('llama3.1:8b-instruct-q4_K_M', '46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e', 'native-schema-v1'),
    'qwen': ('qwen3.5:9b', '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90', 'plain'),
    'ministral': ('ministral-3:8b-instruct-2512-q4_K_M', '1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71', 'plain'),
}
ADAPTER_REL = 'tools/parity/adapters/native_schema_v1.py'
WIN = {F1_WT: r'C:\Proj\robotics\introtorobotics\wt-a-f1', PAR_WT: r'C:\Proj\robotics\introtorobotics\wt-a-parity',
       GZ_WT: r'C:\Proj\robotics\introtorobotics\wt-a-gazebo'}


# ------------------------------------------------------------------ small helpers

def now():
    return datetime.now(timezone.utc)


def stamp():
    t = now()
    return f"{t:%Y-%m-%dT%H:%MZ} ({t.astimezone(TAIPEI):%a %H:%M} TPE)"


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p, v):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + '.tmp')
    t.write_text(json.dumps(v, indent=2) + '\n', encoding='utf-8')
    os.replace(t, p)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def disk_free_gb():
    st = os.statvfs(str(WR))
    return round(st.f_bavail * st.f_frsize / 1e9, 2)


def status(line):
    with STATUS_MD.open('a', encoding='utf-8') as f:
        f.write(f"- {stamp()} [A-chain] {line} Disk free C: {disk_free_gb()} GB.\n")
    print(stamp(), line, flush=True)


def http_json(url, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def before_deadline(margin_minutes=0):
    return now().astimezone(TAIPEI) + timedelta(minutes=margin_minutes) < DEADLINE


def gate_done(name):
    p = GATES / f'{name}.json'
    return p.exists() and read(p).get('done') is True


def gate(name, passed, details, track_stop=False):
    """One summary file per gate. done=True means: never redo this stage on resume."""
    record = {'gate': name, 'pass': passed, 'done': True, 'utc': now().isoformat(), 'disk_free_gb': disk_free_gb(),
              'track_stopped': track_stop, **details}
    write(GATES / f'{name}.json', record)
    status(f"GATE {name}: {'PASS' if passed else 'FAIL/STOP'}; " + json.dumps(details, default=str)[:400])
    return passed


def run(cmd, log, cwd=None, timeout=None, env=None):
    LOGS.mkdir(parents=True, exist_ok=True)
    with open(LOGS / log, 'a') as f:
        f.write(f"\n=== {now().isoformat()} {' '.join(map(str, cmd))}\n")
        f.flush()
        return subprocess.run([str(c) for c in cmd], cwd=cwd, stdout=f, stderr=subprocess.STDOUT, timeout=timeout,
                              env=env).returncode


def services_ok():
    """Ollama 0.40.6 on :11440 and Phoenix on :6006. Restart Ollama once via its own start script if down."""
    try:
        ok = http_json(OLLAMA + '/api/version')['version'] == '0.40.6'
    except Exception:
        ok = False
    if not ok:
        run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
             r'C:\Proj\robotics\introtorobotics\.local\start-parity-ollama.ps1'], 'services.log', timeout=120)
        try:
            ok = http_json(OLLAMA + '/api/version')['version'] == '0.40.6'
        except Exception:
            ok = False
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(PHOENIX, timeout=5) as r:
            ph = r.status == 200
    except Exception:
        ph = False
    if not ph:
        run(['bash', str(WR / 'start_phoenix_tmux.sh')], 'services.log', timeout=200)
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(PHOENIX, timeout=5) as r:
                ph = r.status == 200
        except Exception:
            ph = False
    return ok and ph


def model_present(name):
    tag, digest, _ = MODELS[name]
    try:
        tags = {m['name']: m['digest'] for m in http_json(OLLAMA + '/api/tags')['models']}
    except Exception:
        return False
    return tags.get(tag) == digest


def unload_all():
    try:
        for m in http_json(OLLAMA + '/api/ps')['models']:
            http_json(OLLAMA + '/api/generate', {'model': m['name'], 'keep_alive': 0}, timeout=60)
    except Exception:
        pass


def publish(worktree, paths, message):
    """Commit the given paths on the worktree's own branch and push, via Windows git (credential manager),
    fully non-interactive. Failure is logged and left for Claude; it never blocks the chain."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never', WSLENV='GIT_TERMINAL_PROMPT:GCM_INTERACTIVE')
    w = WIN[worktree]
    rels = [str(Path(p).relative_to(worktree)).replace('/', '\\') for p in paths if Path(p).exists()]
    if not rels:
        return 'nothing to commit'
    codes = [run(['git.exe', '-C', w, 'add', '--', *rels], 'git.log', timeout=300, env=env)]
    codes.append(run(['git.exe', '-C', w, 'commit', '-q', '-m',
                      message + '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>', '--', *rels],
                     'git.log', timeout=300, env=env))
    vf = run(['cmd.exe', '/c', f'cd /d {w} && python -I tools\\freeze\\verify_freeze.py'], 'git.log', timeout=600, env=env)
    branch = subprocess.run(['git.exe', '-C', w, 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True,
                            env=env, timeout=60).stdout.strip()
    try:
        push = run(['git.exe', '-C', w, '-c', 'credential.interactive=never', 'push', '-q', 'origin', branch],
                   'git.log', timeout=180, env=env)
    except subprocess.TimeoutExpired:
        push = 'timeout'
    result = f'commit={codes} verify_freeze={"PASS" if vf == 0 else "FAIL"} push={"ok" if push == 0 else "DEFERRED(" + str(push) + ")"} branch={branch}'
    status(f'publish {worktree.name}: {result}')
    return result


# ------------------------------------------------------------------ watchdog (disk floor, deadline)

ACTIVE_RUNS = []  # run directories that honour STOP_REQUESTED


def watchdog(stop_event):
    while not stop_event.wait(60):
        reason = None
        if disk_free_gb() < DISK_FLOOR_GB:
            reason = f'disk free {disk_free_gb()} GB < {DISK_FLOOR_GB} GB'
        if reason:
            for d in list(ACTIVE_RUNS):
                (Path(d) / 'STOP_REQUESTED').write_text(reason + '\n')
            status('WATCHDOG: ' + reason + '; STOP_REQUESTED written (runners stop between trials).')


# ------------------------------------------------------------------ F1 track

def f1_plan(run_name, stage, backend):
    run_dir = F1_STUDY / 'runs' / run_name
    if not run_dir.exists():
        rc = run(['bash', str(WR / 'f1run.sh'), 'plan', '--run', run_name, '--stage', stage, '--backend', backend], 'f1-chain.log')
        if rc:
            raise RuntimeError(f'f1 plan failed: {run_name}')
    return run_dir, read(run_dir / 'RUN_META.json')['authorization_token']


def f1_execute_popen(run_name, token, log):
    run_dir = F1_STUDY / 'runs' / run_name
    args = ['bash', str(WR / 'f1run.sh'), 'execute', '--run', run_name, '--i-am-authorized', token]
    st = run_dir / 'status.json'
    if st.exists():
        s = read(st)
        if s['status'] == 'COMPLETE':
            return None
        if s['status'] == 'STOPPED':
            args.append('--resume-unstarted')
    ACTIVE_RUNS.append(run_dir)
    return subprocess.Popen(args, stdout=open(LOGS / log, 'a'), stderr=subprocess.STDOUT)


def f1_freeze_ok():
    """Claude writes F1_STAGE1B_FREEZE.json at the wording freeze (PROTOCOL §9). Verify every hash."""
    p = F1_STUDY / 'F1_STAGE1B_FREEZE.json'
    if not p.exists():
        return False, 'F1_STAGE1B_FREEZE.json missing (wording not frozen)'
    bad = [n for n, d in read(p)['files_sha256'].items() if sha(F1_WT / n) != d]
    return (not bad), ('mismatch: ' + repr(bad) if bad else 'all frozen hashes match')


def track_f1(sol_proc_holder):
    if gate_done('F1-H'):
        return
    ok, why = f1_freeze_ok()
    if not ok:
        return gate('F1-H', False, {'reason': why}, track_stop=True)
    if not before_deadline(60):
        return gate('F1-H', False, {'reason': 'deadline: too late to start'}, track_stop=True)
    qdir, qtok = f1_plan('stage1b-heldout-qwen', 'heldout', 'qwen')
    sdir, stok = f1_plan('stage1b-heldout-sol', 'heldout', 'sol')
    sol = f1_execute_popen('stage1b-heldout-sol', stok, 'f1-stage1b-sol.log')
    sol_proc_holder.append(sol)
    status('F1-H started: Qwen held-out (GPU) and Sol held-out (parallel, no GPU).')
    q = f1_execute_popen('stage1b-heldout-qwen', qtok, 'f1-stage1b-qwen.log')
    qrc = q.wait() if q else 0
    status(f'F1 Qwen held-out runner exited {qrc}.')
    unload_all()
    return qrc


def f1_finish(sol_proc_holder, qrc):
    if gate_done('F1-H'):
        return
    srt = None
    if sol_proc_holder and sol_proc_holder[0] is not None:
        srt = sol_proc_holder[0].wait()
    qdir, sdir = F1_STUDY / 'runs/stage1b-heldout-qwen', F1_STUDY / 'runs/stage1b-heldout-sol'
    sol_rows = list((sdir / 'trials').glob('*/result.json')) if sdir.exists() else []
    args = ['bash', '-c', f'cd {F1_WT} && PYTHONDONTWRITEBYTECODE=1 {PY} -I -B tools/f1_wording/analysis.py '
            f'--qwen-run stage1b-heldout-qwen ' + ('--sol-run stage1b-heldout-sol ' if sol_rows else '') +
            f'--out {F1_STUDY}/runs/STAGE1B_ANALYSIS']
    arc = run(args, 'f1-analysis.log', timeout=1800)
    details = {'qwen_runner_exit': qrc, 'sol_runner_exit': srt, 'sol_trials_retained': len(sol_rows), 'analysis_exit': arc}
    passed = arc == 0
    if arc == 0:
        res = read(F1_STUDY / 'runs/STAGE1B_ANALYSIS.json')
        over = res['censoring_stop_rule']['arms_over']
        details.update(decision=res['predictions']['decision'], censoring_arms_over_20pct=over,
                       qwen_status=read(qdir / 'status.json')['status'],
                       sol_status=read(sdir / 'status.json')['status'] if (sdir / 'status.json').exists() else 'NOT_STARTED')
        passed = not over and details['qwen_status'] == 'COMPLETE'
        if over:
            details['stop_condition'] = 'censoring rate above 20% in ' + ', '.join(over)
    gate('F1-H', passed, details, track_stop=not passed)
    publish(F1_WT, [F1_STUDY / 'runs', WR / 'gates'], 'f1: Stage 1b held-out (chain gate F1-H)')


# ------------------------------------------------------------------ parity track

def par_runner(*args, log):
    return run(['bash', '-c', f'cd {PAR_WT} && PYTHONDONTWRITEBYTECODE=1 {PY} -I -B tools/parity/acceptance_run.py ' +
                ' '.join(args)], log)


def par_run(run_name, task_set, name):
    tag, _, adapter = MODELS[name]
    run_dir = PAR_STUDY / 'phase-b-runs' / run_name
    if not run_dir.exists():
        if par_runner('plan', '--run', run_name, '--set', task_set, '--model', tag, '--adapter', adapter, log='parity-chain.log'):
            raise RuntimeError('parity plan failed ' + run_name)
    token = read(run_dir / 'RUN_META.json')['authorization_token']
    extra = []
    if (run_dir / 'status.json').exists():
        s = read(run_dir / 'status.json')['status']
        if s == 'COMPLETE':
            return 0, run_dir
        extra = ['--resume-unstarted']
    ACTIVE_RUNS.append(run_dir)
    rc = par_runner('execute', '--run', run_name, '--i-am-authorized', token, *extra, log=f'parity-{run_name}.log')
    unload_all()
    return rc, run_dir


def track_phase_b():
    admitted = {}
    for name in ('granite', 'llama', 'qwen', 'ministral'):
        g = f'PB-{name}'
        if gate_done(g):
            admitted[name] = read(GATES / f'{g}.json').get('admitted', False)
            continue
        if not model_present(name):
            gate(g, False, {'result': 'NOT RUN (model not in store with the G1 digest)', 'admitted': False})
            admitted[name] = False
            continue
        if not before_deadline(90):
            gate(g, False, {'result': 'NOT RUN (deadline)', 'admitted': False})
            admitted[name] = False
            continue
        rc, run_dir = par_run(f'acceptance-{name}', 'acceptance', name)
        out = run_dir / 'ACCEPTANCE_RESULT.json'
        src = run(['bash', '-c', f'cd {PAR_WT} && {PY} -I -B tools/parity/acceptance_score.py {run_dir}/trials {out} '
                   f'--cases {PAR_STUDY}/tasks/acceptance.json'], 'parity-score.log', timeout=600)
        res = read(out) if out.exists() else {}
        verdict = res.get('model_pass') if src == 0 else None
        # ACCEPTANCE_CRITERIA §4: incomplete = any arm with < 8 of its 9 tool tasks evaluable (G1 V1 censoring)
        run(['bash', '-c', f'cd {PAR_WT} && {PY} -I -B tools/parity/phase_c_summary.py evaluable {run_dir}'],
            'parity-score.log', timeout=600)
        ev = read(run_dir / 'EVALUABLE.json') if (run_dir / 'EVALUABLE.json').exists() else {'incomplete': True}
        run(['bash', '-c', f'cd {PAR_WT} && {PY} -I -B tools/parity/sdk_normalization.py {run_dir}'], 'parity-score.log', timeout=600)
        sdk = read(run_dir / 'SDK_NORMALIZATION.json') if (run_dir / 'SDK_NORMALIZATION.json').exists() else {}
        incomplete = ev['incomplete'] or rc != 0
        if name in ('granite', 'llama'):
            result = ('acceptance incomplete (infrastructure)' if incomplete and verdict is not True else
                      'PASS: admitted (adapted, native-schema-v1)' if verdict is True else
                      'FAIL: not adaptable under parity rules')
            adm = verdict is True
        else:
            result = 'reference point: ' + ('PASS' if verdict is True else 'FAIL (reported, not fixed)')
            adm = True  # Qwen and Ministral are baseline models in D; acceptance is a reference only
        admitted[name] = adm
        gate(g, verdict is True, {'runner_exit': rc, 'scorer_exit': src, 'result': result, 'admitted': adm,
                                   'incomplete': incomplete,
                                   'sdk_normalization_assistance': {k: sdk.get(k) for k in ('raw_tool_calls', 'calls_with_string_encoded_list_or_object')},
                                   'arms': {k: {x: v.get(x) for x in ('recognized_turn_rate', 'schema_valid_rate', 'parse_crashes', 'pass')}
                                            for k, v in (res.get('arms') or {}).items()}})
        publish(PAR_WT, [run_dir, WR / 'gates'], f'parity: Phase B acceptance {name} (chain gate {g})')
    return admitted


def track_phase_c(admitted):
    for name in ('granite', 'llama'):
        g = f'PC-{name}'
        if gate_done(g) or not admitted.get(name):
            continue
        if not before_deadline(240):
            gate(g, False, {'result': 'designed, not run (deadline)'})
            continue
        rc, run_dir = par_run(f'phase-c-{name}', 'g1-heldout', name)
        arc = run(['bash', '-c', f'cd {PAR_WT} && {PY} -I -B tools/parity/phase_c_summary.py summary {run_dir}'],
                  'parity-phase-c-summary.log', timeout=1800)
        run(['bash', '-c', f'cd {PAR_WT} && {PY} -I -B tools/parity/sdk_normalization.py {run_dir}'], 'parity-score.log', timeout=600)
        summary = read(run_dir / 'PHASE_C_SUMMARY.json') if (run_dir / 'PHASE_C_SUMMARY.json').exists() else {}
        gate(g, rc == 0 and arc == 0, {'label': 'adapted-integration rerun (laptop)', 'runner_exit': rc,
                                        'summary_exit': arc, 'counts': summary.get('counts')})
        publish(PAR_WT, [run_dir, WR / 'gates'], f'parity: Phase C rerun {name} (chain gate {g})')


# ------------------------------------------------------------------ Gazebo track (B's frozen runner)

def models_json(admitted):
    rows = [{'name': 'sol', 'backend': 'siwc', 'model': 'gpt-6.1-sol'}]
    for name in ('qwen', 'ministral', 'granite', 'llama'):
        if not admitted.get(name) or not model_present(name):
            continue
        tag, digest, adapter = MODELS[name]
        row = {'name': name, 'backend': 'ollama', 'tag': tag, 'digest': digest, 'endpoint': OLLAMA, 'adapter': None}
        if adapter != 'plain':
            row['adapter'] = {'path': ADAPTER_REL, 'sha256': sha(GZ_WT / ADAPTER_REL),
                              'label': 'adapted (native-schema-v1: transport, 3 flagged non-vendor details)'}
        rows.append(row)
    path = GZ_STUDY / 'models.json'
    if path.exists():
        if read(path) != rows:
            raise RuntimeError('models.json already exists with a different model set; not overwriting')
    else:
        write(path, rows)
    return path


def gz_job(stage, models=None):
    args = ['bash', str(GZ_WT / 'experiments/gazebo_d/job.sh'), str(GZ_WT), stage] + ([models] if models else [])
    return run(args, f'gazebo-{stage}.log', timeout=None)


def gz_runner(*args):
    return run(['bash', '-c', f'cd {GZ_WT} && source /opt/ros/jazzy/setup.bash >/dev/null 2>&1; {PY} -B -m '
                f'experiments.gazebo_d.runner ' + ' '.join(args)], 'gazebo-freeze.log', timeout=600)


def track_gazebo(admitted):
    rel_models = 'artifacts/gazebo-d-20261121/models.json'
    if not gate_done('D1-controls'):
        rc = gz_job('controls')
        st = GZ_STUDY / 'runs/controls/status.json'
        s = read(st) if st.exists() else {}
        trials = s.get('trials', [])
        passed = rc == 0 and s.get('status') == 'COMPLETE' and len(trials) == 52 and all(t.get('primary_pass') is True for t in trials)
        gate('D1-controls', passed, {'job_exit': rc, 'status': s.get('status'), 'trials': len(trials),
                                     'passed_trials': sum(t.get('primary_pass') is True for t in trials)}, track_stop=not passed)
        publish(GZ_WT, [GZ_STUDY / 'runs/controls', GZ_STUDY / 'jobs', WR / 'gates'], 'gazebo-d: D1 controls (chain gate)')
        if not passed:
            return
    elif not read(GATES / 'D1-controls.json')['pass']:
        return
    models_json(admitted)
    if not gate_done('D1-dev'):
        if not (GZ_STUDY / 'runs/dev/freeze.json').exists() and gz_runner('freeze', '--stage', 'dev', '--models', rel_models):
            return gate('D1-dev', False, {'reason': 'dev freeze failed'}, track_stop=True)
        rc = gz_job('dev', rel_models)
        unload_all()
        g = GZ_STUDY / 'runs/dev/D1_GATE.json'
        d1 = read(g) if g.exists() else {}
        gate('D1-dev', d1.get('pass') is True, {'job_exit': rc, 'd1_gate': d1}, track_stop=d1.get('pass') is not True)
        publish(GZ_WT, [GZ_STUDY / 'runs/dev', GZ_STUDY / 'models.json', GZ_STUDY / 'jobs', WR / 'gates'],
                'gazebo-d: D1 dev and gate (chain)')
        if d1.get('pass') is not True:
            return
    elif not read(GATES / 'D1-dev.json')['pass']:
        return
    if not gate_done('D2-heldout'):
        if not before_deadline(30):
            return gate('D2-heldout', False, {'result': 'designed, not run (deadline)'}, track_stop=True)
        if not (GZ_STUDY / 'runs/heldout/freeze.json').exists() and gz_runner('freeze', '--stage', 'heldout', '--models', rel_models):
            return gate('D2-heldout', False, {'reason': 'held-out freeze failed'}, track_stop=True)
        rc = gz_job('heldout', rel_models)
        unload_all()
        st = GZ_STUDY / 'runs/heldout/status.json'
        s = read(st) if st.exists() else {}
        ana = (GZ_STUDY / 'runs/heldout/analysis/ANALYSIS.md').exists()
        gate('D2-heldout', rc == 0 and ana, {'job_exit': rc, 'status': s.get('status'), 'trials': len(s.get('trials', [])),
                                              'stopped_models': s.get('stopped_models'), 'analysis_written': ana,
                                              'note': 'ambiguous outcomes PRELIMINARY until human rating'})
        publish(GZ_WT, [GZ_STUDY / 'runs/heldout', GZ_STUDY / 'jobs', WR / 'gates'], 'gazebo-d: D2 held-out (chain)')


# ------------------------------------------------------------------ main

def cmd_run():
    if LOCK.exists():
        pid = int(LOCK.read_text().split()[0])
        if Path(f'/proc/{pid}').exists():
            sys.exit(f'REFUSED: chain already running (pid {pid})')
    LOCK.write_text(f'{os.getpid()} {now().isoformat()}\n')
    stop = threading.Event()
    threading.Thread(target=watchdog, args=(stop,), daemon=True).start()
    status(f'CHAIN START pid {os.getpid()} (resume-safe; completed gates are skipped).')
    try:
        if not services_ok():
            status('CHAIN STOP: Ollama or Phoenix not available after one restart attempt.')
            return 2
        sol_holder = []
        qrc = track_f1(sol_holder)
        admitted = track_phase_b()          # Sol F1 arms may still be running (no GPU)
        f1_finish(sol_holder, qrc)
        track_phase_c(admitted)
        track_gazebo(admitted)
        status('CHAIN END. See weekend-run-20261121/gates/*.json.')
        return 0
    except Exception as error:
        status(f'CHAIN STOP on error {type(error).__name__}: {str(error)[:300]}')
        raise
    finally:
        stop.set()
        LOCK.unlink(missing_ok=True)


def cmd_status():
    for p in sorted(GATES.glob('*.json')):
        g = read(p)
        print(p.stem, 'PASS' if g['pass'] else 'FAIL/STOP', g['utc'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('run', 'status'))
    sys.exit({'run': cmd_run, 'status': cmd_status}[ap.parse_args().cmd]() or 0)
