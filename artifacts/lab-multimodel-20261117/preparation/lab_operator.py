"""Host-only bounded operator. Avoids shadowing Python's stdlib operator module."""
import hashlib
import json
from pathlib import Path
import random
import subprocess
import time
import traceback
from urllib.request import urlopen

ROOT = Path('/media/naeem/d1/marvel proj')
CONTAINER = 'marvel-rosa-lab-20261117'
MODELS = ['qwen3.5:9b', 'llama3.1:8b-instruct-q4_K_M', 'granite3.3:8b',
          'ministral-3:8b-instruct-2512-q4_K_M']
ORDER = list(MODELS)
random.Random(20261117).shuffle(ORDER)
PREFIX = ('source /opt/ros/jazzy/setup.bash; '
          'export PYTHONPATH=/work/baseline/rosa-research/src:/work/baseline/rosa-evaluation:/work/study:${PYTHONPATH:-}; '
          'exec /work/runtime/envs/research/bin/python -B /work/study/lab_study.py ')
state = {'phase': 'PREPARING', 'planned_trials': 320, 'model_order': ORDER,
         'models': [], 'started_unix': time.time()}


def save():
    p = ROOT / 'results/operator-status.json'
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n')
    tmp.replace(p)


def command(args, logfile, timeout):
    with (ROOT / 'preparation' / logfile).open('x') as log:
        result = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-lc', PREFIX + args],
            stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    return result.returncode


def gpu_check(model):
    samples = []
    for _ in range(3):
        raw = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,memory.free',
            '--format=csv,noheader,nounits'], text=True).strip()
        utilization, free = map(int, raw.split(','))
        samples.append({'utilization_percent': utilization, 'free_MiB': free})
        time.sleep(1)
    processes = subprocess.check_output(['nvidia-smi', '--query-compute-apps=process_name',
        '--format=csv,noheader'], text=True).splitlines()
    competing = [p for p in processes if p and 'gnome-remote-desktop' not in p]
    record = {'at_unix': time.time(), 'model': model, 'samples': samples,
        'compute_processes': processes, 'competing_compute': competing,
        'pass': not competing and all(x['utilization_percent'] <= 15 and x['free_MiB'] >= 9000 for x in samples)}
    (ROOT / 'preparation' / ('gpu-' + model.replace(':', '_') + '.json')).write_text(json.dumps(record, indent=2))
    if not record['pass']:
        raise RuntimeError('GPU gate failed; other users/processes will not be stopped')


def main():
    if (ROOT / 'results/operator-status.json').exists():
        raise RuntimeError('An operator record already exists; no blind restart')
    save()
    try:
        for _ in range(60):
            try:
                with urlopen('http://127.0.0.1:6006', timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError('Phoenix not ready')
        state['phase'] = 'FREEZE'
        save()
        if command('freeze', 'freeze.log', 120):
            raise RuntimeError('Freeze failed')
        state['phase'] = 'DETERMINISTIC_CONTROLS'
        save()
        if command('controls', 'controls.log', 1800):
            raise RuntimeError('Deterministic controls failed; zero scored model calls launched')
        state['phase'] = 'MODELS'
        save()
        for model in ORDER:
            gpu_check(model)
            item = {'model': model, 'started_unix': time.time(), 'status': 'RUNNING'}
            state['models'].append(item)
            state['current_model'] = model
            save()
            code = command('run --model ' + model, model.replace(':', '_') + '-run.log', 29100)
            item.update(exit_code=code, finished_unix=time.time(), status='COMPLETE' if code == 0 else 'STOPPED')
            save()
            command('report', model.replace(':', '_') + '-interim-report.log', 120)
            if code:
                raise RuntimeError('Model run stopped; retained for diagnosis: ' + model)
            time.sleep(5)
        state['phase'] = 'EXECUTION_COMPLETE'
    except Exception as error:
        state.update(phase='STOPPED', error_type=type(error).__name__, error=str(error),
            diagnostic_traceback=traceback.format_exc())
        raise
    finally:
        state['updated_unix'] = time.time()
        save()


if __name__ == '__main__':
    main()
