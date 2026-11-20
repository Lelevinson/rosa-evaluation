from datetime import datetime, timezone
import shutil
import subprocess
import sys
from .runner import (ROOT, BASE, FIRST, PREFLIGHT, DESTINATION, original, read, sha,
                     verify_original, remaining_jobs, jobs)


def main():
    verify_original()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    plan = remaining_jobs(state, jobs('gazebo'))
    if len(plan) != 5 or state['total_model_calls'] != 13:
        raise RuntimeError('unexpected_continuation_resources')
    DESTINATION.mkdir(parents=True, exist_ok=False)
    check = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_prompt_live_resume_v2.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (DESTINATION / 'preflight.log').write_text(check.stdout + check.stderr)
    if check.returncode:
        raise RuntimeError('R2_setup_scope_preflight_failed')
    original.write(DESTINATION / 'schedule.json', {'jobs': plan})
    paths = [*PathGlob(ROOT / 'experiments/prompt_live_resume_v2'),
        ROOT / 'experiments/simulator_home_v1.py', ROOT / 'tests/test_simulator_home_v1.py',
        ROOT / 'tests/test_prompt_live_resume_v2.py',
        ROOT / 'docs/PROMPT_CONTRACT_V1_CONTINUATION_R2_2026-10-26.md',
        ROOT.parent / 'reports/prompt-live-resume-v2-run.ps1', DESTINATION / 'schedule.json']
    files = {}
    for path in sorted(paths):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = sha(path)
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    digest_evidence = lambda root: {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*')
        if p.is_file() and 'source' not in p.relative_to(root).parts and p.suffix in ('.json', '.md', '.log', '.xacro')}
    original.write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': files, 'R1_evidence': digest_evidence(FIRST), 'setup_evidence': digest_evidence(PREFLIGHT),
        'live_requests_before_freeze': 0, 'planned_trials': 5, 'additional_request_cap': 40,
        'original_request_cap': 72, 'prior_reserved_calls': 13, 'R1_reserved_calls': 0,
        'maximum_combined_calls': 53, 'setup_amendment': 'explicit_HOME_spawn_only'})
    print('FROZEN:R2 setup amendment;5 hosted cells,max40 new requests;3 cold-start controls passed.')


def PathGlob(path):
    return list(path.glob('*.py'))


if __name__ == '__main__':
    main()
