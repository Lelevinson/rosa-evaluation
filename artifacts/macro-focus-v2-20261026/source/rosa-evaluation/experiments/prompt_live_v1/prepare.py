from datetime import datetime, timezone
import hashlib
import shutil
import subprocess
import sys
from .runner import ROOT, DESTINATION, write
from .design import jobs, LIMITS
from experiments.macro_resume_v1.runner import verify_freeze as verify_history


def main():
    verify_history()
    DESTINATION.mkdir(parents=True, exist_ok=False)
    check = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_prompt_live_v1.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (DESTINATION / 'preflight.log').write_text(check.stdout + check.stderr)
    if check.returncode:
        raise RuntimeError('new_live_coordinator_preflight_failed')
    write(DESTINATION / 'schedule.json', {'jobs': jobs('gazebo'), 'limits': LIMITS})
    paths = [*PathGlob(ROOT / 'experiments/prompt_live_v1'),
        *PathGlob(ROOT / 'experiments/prompt_contract_v1'),
        ROOT / 'tests/test_prompt_live_v1.py', ROOT / 'tests/test_prompt_contract_v1.py',
        ROOT / 'docs/PROMPT_CONTRACT_V1_LIVE_PROTOCOL_2026-10-26.md',
        ROOT.parent / 'reports/prompt-live-v1-run.ps1',
        ROOT.parent / 'rosa-research/src/rosa_reliability/prompt_contract.py',
        DESTINATION / 'schedule.json']
    files = {}
    for path in sorted(paths):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'protocol': 'prompt-contract-v1-live', 'files': files, 'planned_trials_per_backend': 9,
        'request_cap_per_backend': 72, 'live_requests_before_freeze': 0,
        'historical_sources_checked': True,
        'historical_continuation_freeze_sha256': hashlib.sha256(
            (ROOT / 'artifacts/macro-transfer-v1-resume-r1-20261023/freeze.json').read_bytes()).hexdigest()})
    print('FROZEN: 9 known-case Gazebo trials/backend, 72 requests/backend. No live calls yet.')


def PathGlob(path):
    return list(path.glob('*.py'))


if __name__ == '__main__':
    main()
