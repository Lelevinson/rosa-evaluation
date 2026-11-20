from datetime import datetime, timezone
import shutil
import subprocess
import sys
from .runner import ROOT, BASE, DESTINATION, read, sha, original, verify_original, remaining_jobs, jobs


def main():
    verify_original()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    plan = remaining_jobs(state, jobs('gazebo'))
    if len(plan) != 5 or state['total_model_calls'] != 13:
        raise RuntimeError('unexpected_original_attempts_or_resources')
    if read(BASE / 'session-siwc.json')['auth']['session_cleanup'] != 'REVOKED':
        raise RuntimeError('original_session_not_revoked')
    DESTINATION.mkdir(parents=True, exist_ok=False)
    run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_prompt_live_resume_v1.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (DESTINATION / 'preflight.log').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('continuation_preflight_failed')
    original.write(DESTINATION / 'schedule.json', {'jobs': plan})
    paths = [*PathGlob(ROOT / 'experiments/prompt_live_resume_v1'),
        ROOT / 'tests/test_prompt_live_resume_v1.py',
        ROOT / 'docs/PROMPT_CONTRACT_V1_CONTINUATION_R1_2026-10-26.md',
        ROOT.parent / 'reports/prompt-live-resume-v1-run.ps1', DESTINATION / 'schedule.json']
    files = {}
    for path in sorted(paths):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = sha(path)
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    evidence = {p.relative_to(BASE).as_posix(): sha(p) for p in BASE.rglob('*')
        if p.is_file() and 'source' not in p.relative_to(BASE).parts and p.suffix in ('.json', '.md', '.log')}
    original.write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': files, 'original_evidence': evidence, 'live_requests_before_freeze': 0,
        'planned_trials': 5, 'additional_request_cap': 40, 'original_request_cap': 72,
        'prior_reserved_calls': 13, 'maximum_combined_calls': 53})
    print('FROZEN:single continuation,5 cells,max40 additional requests; initial evidence retained.')


def PathGlob(path):
    return list(path.glob('*.py'))


if __name__ == '__main__':
    main()
