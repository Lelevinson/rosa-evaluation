"""Detached host operator for one separately preserved lab Qwen repeat."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import traceback
import zipfile
from urllib.request import urlopen

ROOT = Path('/media/naeem/d1/marvel proj')
BASE = ROOT / 'qwen-repeat-20261117'
PREFIX = ('source /opt/ros/jazzy/setup.bash; '
    'export PYTHONPATH=/work/baseline/rosa-research/src:/work/baseline/rosa-evaluation:/work/study:${PYTHONPATH:-}; '
    'exec /work/runtime/envs/research/bin/python -B /work/qwen-repeat-20261117/study/repeat_study.py ')
state = {'phase': 'PREPARING', 'planned_trials': 80, 'started_unix': time.time()}


def save():
    path = BASE / 'operator-status.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(path)


def command(action, timeout):
    with (BASE / (action + '.log')).open('x') as log:
        completed = subprocess.run(['docker', 'exec', '--user', '1000:1000',
            '-e', 'HOME=/work/runtime/home', 'marvel-rosa-lab-20261117',
            'bash', '-lc', PREFIX + action], stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    if completed.returncode:
        raise RuntimeError(action + '_failed; retained logs and results')


def gpu_check():
    samples = []
    for _ in range(3):
        raw = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
            '--format=csv,noheader,nounits'], text=True).strip()
        use, free = map(int, raw.split(','))
        samples.append({'utilization_percent': use, 'free_MiB': free})
        time.sleep(1)
    processes = subprocess.check_output(['nvidia-smi', '--query-compute-apps=process_name',
        '--format=csv,noheader'], text=True).splitlines()
    competitors = [p for p in processes if p and 'gnome-remote-desktop' not in p]
    record = {'model': 'qwen3.5:9b', 'at_unix': time.time(), 'samples': samples,
        'compute_processes': processes, 'competing_compute': competitors,
        'pass': not competitors and all(r['utilization_percent'] <= 15 and r['free_MiB'] >= 9000 for r in samples)}
    (BASE / 'gpu-preflight.json').write_text(json.dumps(record, indent=2))
    if not record['pass']:
        raise RuntimeError('GPU preflight failed; no competing processes stopped')


def archive():
    paths = [p for p in BASE.rglob('*') if p.is_file() and p.suffix != '.zip'
        and p.name not in ('operator.log', 'evidence-verification.json')
        and '__pycache__' not in p.parts]
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    original = json.loads((ROOT / 'study/freeze.json').read_text())
    for name, expected in original['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    frozen = json.loads((BASE / 'study/freeze.json').read_text())
    for name, expected in frozen['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    target = BASE / 'QWEN_LAB_REPEAT_RAW_2026-11-17.zip'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as out:
        for name in manifest:
            out.write(ROOT / name, name)
        out.writestr('ARCHIVE_MANIFEST.json', json.dumps({'files': manifest, 'phase': state['phase']}, indent=2))
    with zipfile.ZipFile(target) as check:
        assert check.testzip() is None
        for name, expected in manifest.items():
            assert hashlib.sha256(check.read(name)).hexdigest() == expected
    (BASE / 'evidence-verification.json').write_text(json.dumps({'files': len(manifest),
        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size,
        'all_hashes_pass': True, 'old_69_source_hashes_pass': True}, indent=2))


def main():
    if (BASE / 'operator-status.json').exists():
        raise RuntimeError('Existing operator status; no blind restart')
    save()
    try:
        hardware = {'gpu': subprocess.check_output(['nvidia-smi',
            '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'], text=True).strip(),
            'kernel': subprocess.check_output(['uname', '-sr'], text=True).strip(),
            'captured_unix': time.time()}
        (BASE / 'hardware.json').write_text(json.dumps(hardware, indent=2))
        with urlopen('http://127.0.0.1:6006', timeout=5) as response:
            assert response.status == 200
        for action, timeout in [('freeze', 120), ('controls', 1800), ('run', 29100), ('report', 120)]:
            state['phase'] = action.upper()
            save()
            if action == 'run':
                gpu_check()
            command(action, timeout)
        state['phase'] = 'EXECUTION_COMPLETE'
    except Exception as error:
        state.update(phase='STOPPED', error_type=type(error).__name__, error=str(error),
            diagnostic_traceback=traceback.format_exc())
    finally:
        state['finished_unix'] = time.time()
        save()
        if (BASE / 'study/freeze.json').exists():
            archive()


if __name__ == '__main__':
    main()
