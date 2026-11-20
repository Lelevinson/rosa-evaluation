"""Host-side detached launcher; fresh GPU and immutable-source checks precede exec."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LAB = Path('/media/naeem/d1/marvel proj')
WORKSPACE = ROOT.parents[4]


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--resume-unstarted', action='store_true')
    args = parser.parse_args()
    assert ROOT.resolve().is_relative_to(LAB.resolve())
    freeze = read(ROOT / 'freeze.json')
    assert all(digest(ROOT / n) == d for n, d in freeze['files_sha256'].items())
    parent = read(ROOT.parent / 'stage-4/freeze.json')
    assert all(digest(WORKSPACE / n) == d for n, d in parent['files_sha256'].items())
    if not args.preflight_only:
        ack = read(ROOT / 'owner-launch-acknowledgment.json')
        assert ack['launch_allowed'] and ack['freeze_sha256'] == digest(ROOT / 'freeze.json')
        if args.resume_unstarted:
            assert read(ROOT / 'status.json')['status'] == 'STOPPED'
        else:
            assert not (ROOT / 'RUN_ONCE').exists()
    with urllib.request.urlopen('http://127.0.0.1:11439/api/tags', timeout=5) as response:
        models = json.load(response)['models']
    model = next(m for m in models if m['name'] == 'qwen3.5:9b')
    assert model['digest'] == '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'
    with urllib.request.urlopen('http://127.0.0.1:6006/healthz', timeout=5) as response:
        assert response.status == 200
    samples = []
    for index in range(3):
        raw = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,utilization.gpu',
            '--format=csv,noheader'], text=True).strip()
        percent = int(raw.split(',')[-1].strip().split()[0])
        samples.append({'at_unix': time.time(), 'gpu': raw, 'percent': percent})
        if index < 2:
            time.sleep(2)
    assert all(s['percent'] <= 5 for s in samples), 'GPU_busy_no_workloads_terminated'
    assert shutil.disk_usage(ROOT).free > 2 ** 30
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    record = {'checked_utc': stamp, 'pass': True, 'gpu_samples': samples,
        'frozen_inputs_verified': len(parent['files_sha256']), 'sealed_port_files_verified': len(freeze['files_sha256']),
        'freeze_sha256': digest(ROOT / 'freeze.json'), 'operator_sha256': digest(__file__),
        'model_digest': model['digest'], 'existing_phoenix_healthy': True,
        'preflight_only': args.preflight_only, 'no_new_inference_requests': True}
    (HERE / ('launch-preflight-' + stamp + '.json')).write_text(json.dumps(record, indent=2) + '\n')
    if args.preflight_only:
        print(json.dumps(record))
        return
    path = Path('/work') / ROOT.relative_to(LAB) / 'launch.py'
    command = 'source /opt/ros/jazzy/setup.bash && ' + shlex.join([
        '/work/runtime/envs/research/bin/python', '-B', str(path), '--execute'
    ] + (['--resume-unstarted'] if args.resume_unstarted else []))
    with (HERE / ('launcher-' + stamp + '.log')).open('x') as log:
        child = subprocess.Popen(['docker', 'exec', '--user', '1000:1000', 'marvel-rosa-lab-20261117',
            'bash', '-lc', command], stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    (HERE / ('worker-' + stamp + '.json')).write_text(json.dumps({
        'pid': child.pid, 'started_utc': stamp, 'detached': True, 'source_freeze_sha256': record['freeze_sha256'],
        'operator_sha256': record['operator_sha256'], 'resume_unstarted_only': args.resume_unstarted,
        'log': 'launcher-' + stamp + '.log'}, indent=2) + '\n')
    print(json.dumps({'pid': child.pid, 'status': 'DETACHED_START_REQUESTED', 'stamp': stamp}))


if __name__ == '__main__':
    main()
