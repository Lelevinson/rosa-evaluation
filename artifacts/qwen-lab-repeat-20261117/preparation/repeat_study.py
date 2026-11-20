"""Second lab Qwen run. Import frozen execution code without editing it."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/work')
BASE = ROOT / 'qwen-repeat-20261117'
QWEN = 'qwen3.5:9b'
spec = importlib.util.spec_from_file_location('frozen_lab_study', ROOT / 'study/lab_study.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
lab.RESULTS = BASE / 'results'
lab.STUDY = BASE / 'study'
lab.PROJECT = 'rosa-qwen-lab-repeat-20261117'
lab.MODELS = [QWEN]
lab.ORDER = [QWEN]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    record = json.loads((BASE / 'study/freeze.json').read_text())
    for name, expected in record['files'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('Repeat source mismatch: ' + name)
    original = json.loads((ROOT / 'study/freeze.json').read_text())
    if original['schedule'] != record['schedule']:
        raise RuntimeError('Repeat schedule differs from first lab run')
    tags = lab.api('/api/tags')['models']
    current = next(m for m in tags if m['name'] == QWEN)
    if current['digest'] != record['model']['digest']:
        raise RuntimeError('Qwen digest changed')
    return record


lab.verify = verify


def freeze():
    destination = BASE / 'study/freeze.json'
    if destination.exists():
        raise RuntimeError('Refusing to replace repeat freeze')
    original = json.loads((ROOT / 'study/freeze.json').read_text())
    for name, expected in original['files'].items():
        assert digest(ROOT / name) == expected, name
    source_files = dict(original['files'])
    source_files['study/freeze.json'] = digest(ROOT / 'study/freeze.json')
    for path in sorted((BASE / 'study').iterdir()):
        if path.is_file():
            source_files[str(path.relative_to(ROOT))] = digest(path)
    tags = lab.api('/api/tags')['models']
    model = next(m for m in tags if m['name'] == QWEN)
    assert model['digest'] == original['model_metadata'][QWEN]['digest']
    schedule = lab.schedule(QWEN)
    assert schedule == original['schedule']
    hardware = json.loads((BASE / 'hardware.json').read_text())
    source_files[str((BASE / 'hardware.json').relative_to(ROOT))] = digest(BASE / 'hardware.json')
    lab.write(destination, {'study': lab.PROJECT, 'date': '2026-11-17',
        'files': source_files, 'model': model, 'schedule': schedule,
        'planned_trials': 80, 'planned_controls': 20, 'hardware': hardware,
        'requests': {'ordinary': 640, 'narrow_retry_reserve': 3, 'ceiling': 643},
        'limits': {'context': 8192, 'output_per_call': 1024, 'output_per_task': 2048,
            'calls_per_task': 8, 'native_per_task': 10, 'task_seconds': 360,
            'backend_seconds': 28800, 'temperature': 0, 'seed': 42,
            'thinking': False, 'streaming': False, 'response_cache': False},
        'comparison': 'Second same-hardware lab replication; old lab and laptop records retained.',
        'ambiguity_semantics': 'HUMAN_REVIEW_PENDING; 36 known-goal tasks per condition',
        'original_freeze_sha256': digest(ROOT / 'study/freeze.json'),
        'frozen_at_unix': time.time()})
    verify()
    print('FROZEN', len(source_files), 'source/config hashes; 80 scheduled trials', flush=True)


def gpu_gate(model):
    record = json.loads((BASE / 'gpu-preflight.json').read_text())
    assert record['model'] == model and record['pass']
    assert 0 <= time.time() - record['at_unix'] <= 120
    lab.write(BASE / 'results/qwen3.5_9b/gpu-preflight.json', record)


lab.gpu_gate = gpu_gate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'controls', 'run', 'report'])
    action = parser.parse_args().action
    if action == 'freeze':
        freeze()
    elif action == 'controls':
        lab.controls()
    elif action == 'run':
        lab.run(QWEN)
    else:
        verify()
        lab.report()


if __name__ == '__main__':
    main()
