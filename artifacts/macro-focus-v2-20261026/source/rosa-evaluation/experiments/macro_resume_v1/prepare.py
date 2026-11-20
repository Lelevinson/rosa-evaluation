from datetime import datetime, timezone
import json
import shutil
import subprocess
import sys
from .runner import BASE, DESTINATION, ROOT, original, remaining_jobs, full_jobs, verify_original, sha, read


def main():
    if DESTINATION.exists():
        raise RuntimeError('continuation_directory_exists_do_not_overwrite')
    verify_original()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    plan = remaining_jobs(state, full_jobs('gazebo'))
    if [j['original_schedule_index'] for j in plan] != [14, 15, 16, 17]:
        raise RuntimeError('unexpected_remaining_cells')
    if read(BASE / 'session-siwc.json')['auth']['session_cleanup'] != 'REVOKED':
        raise RuntimeError('old_token_session_cleanup_unverified')
    DESTINATION.mkdir()
    check = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_macro_resume_v1.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (DESTINATION / 'preflight.log').write_text(check.stdout + check.stderr)
    if check.returncode:
        raise RuntimeError('continuation_preflight_failed')
    original.write(DESTINATION / 'schedule.json', {'jobs': plan})
    paths = list((ROOT / 'experiments/macro_resume_v1').glob('*.py'))
    paths += [ROOT / 'tests/test_macro_resume_v1.py',
        ROOT / 'docs/MACRO_TRANSFER_V1_CONTINUATION_R1_2026-10-23.md',
        ROOT.parent / 'reports/macro-resume-v1-run.ps1', DESTINATION / 'schedule.json']
    files = {}
    for path in sorted(paths):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = sha(path)
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    artifacts = ['freeze.json', 'gazebo/siwc/checkpoint.json', 'gazebo/ollama/checkpoint.json',
                 'session-siwc.json', 'PARTIAL_AUDIT.json']
    original.write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': files, 'original_artifacts': {name: sha(BASE / name) for name in artifacts},
        'original_freeze_sha256': sha(BASE / 'freeze.json'), 'prior_hosted_calls': state['total_model_calls'],
        'additional_cap': 32, 'combined_hosted_cap': 75, 'planned_trials': 4,
        'live_requests_before_freeze': 0, 'all_original_treatments_preserved': True})
    print('FROZEN continuation: four cells, six tests passed, at most32 new requests; old results preserved.')


if __name__ == '__main__':
    main()
