"""Freeze only after known-case live validation passes; never starts inference."""
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys
from .runner import ROOT, DESTINATION, write
from .gates import require_validation, VALIDATION, CONTINUATION, FIRST_CONTINUATION
from .design import jobs, LIMITS
from experiments.macro_resume_v1.runner import verify_freeze as verify_history


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require_validation()
    history = verify_history()
    DESTINATION.mkdir(parents=True, exist_ok=False)
    check = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_macro_focus_v2.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (DESTINATION / 'preflight.log').write_text(check.stdout + check.stderr)
    if check.returncode:
        raise RuntimeError('fresh_pilot_preflight_failed')
    write(DESTINATION / 'schedule.json', {'jobs': jobs(), 'limits': LIMITS})
    paths = [*PathGlob(ROOT / 'experiments/macro_focus_v2'),
        *PathGlob(ROOT / 'experiments/prompt_contract_v1'),
        ROOT / 'tests/test_macro_focus_v2.py',
        ROOT / 'experiments/simulator_home_v1.py', ROOT / 'tests/test_simulator_home_v1.py',
        ROOT / 'docs/MACRO_FOCUS_V2_PROTOCOL_2026-10-26.md',
        ROOT.parent / 'reports/macro-focus-v2-run.ps1',
        ROOT.parent / 'rosa-research/src/rosa_reliability/prompt_contract.py',
        DESTINATION / 'schedule.json']
    base_history = json.loads((ROOT / 'artifacts/macro-transfer-v1-20261022/freeze.json').read_text())
    paths += [ROOT.parent / name for name in {*base_history['files'], *history['files']}]
    # The prior validation coordinator is reused only for atomic JSON writes;
    # preserve all its already-frozen source digests alongside this new freeze.
    old = json.loads((VALIDATION / 'freeze.json').read_text())
    paths += [ROOT.parent / name for name in old['files']]
    files = {}
    for path in sorted(set(paths)):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = sha(path)
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    evidence = ['analysis.json', 'freeze.json', 'gazebo/ollama/checkpoint.json',
        'gazebo/siwc/checkpoint.json', 'session-siwc.json', 'environment-preflight.json']
    continuation = {p.relative_to(ROOT.parent).as_posix(): sha(p) for p in CONTINUATION.rglob('*')
        if p.is_file() and 'source' not in p.relative_to(CONTINUATION).parts and
        p.suffix in ('.json', '.log', '.md')} if CONTINUATION.exists() else {}
    continuation.update({p.relative_to(ROOT.parent).as_posix(): sha(p) for p in FIRST_CONTINUATION.rglob('*')
        if p.is_file() and 'source' not in p.relative_to(FIRST_CONTINUATION).parts and
        p.suffix in ('.json', '.log', '.md')})
    write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'protocol': 'macro-focus-v2', 'files': files, 'planned_trials_per_backend': 36,
        'request_cap_per_backend': 288, 'live_requests_before_freeze': 0,
        'validation_evidence': {name: sha(VALIDATION / name) for name in evidence},
        'validation_continuation_evidence': continuation,
        'historical_sources_checked': True, 'scope': 'one_bounded_pose_capability'})
    print('FROZEN:36 fresh trials/backend;288 requests/backend. No pilot inference yet.')


def PathGlob(path):
    return list(path.glob('*.py'))


if __name__ == '__main__':
    main()
