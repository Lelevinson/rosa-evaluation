"""Durable sequential live supervisor; preserves every failed/interrupted step."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import ProxyHandler, Request, build_opener

from ..config import ROOT
from .runner import CAMPAIGN
from .protocol import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('launch', 'live'))
    args = parser.parse_args()
    verify()
    if args.action == 'launch':
        target = CAMPAIGN / 'supervisor.pid'
        if target.exists():
            raise RuntimeError('supervisor_already_launched')
        with (CAMPAIGN / 'supervisor.log').open('a') as output:
            process = subprocess.Popen([sys.executable, '-B', '-m', __package__ + '.campaign', 'live'],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        target.write_text(str(process.pid))
        print(f'Detached Stage 4 supervisor PID {process.pid}')
        return
    state = {'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat(), 'steps': {}}
    def save():
        temporary = CAMPAIGN / 'supervisor.tmp'
        temporary.write_text(json.dumps(state, indent=2))
        temporary.replace(CAMPAIGN / 'supervisor-status.json')
    def step(name, module, *parameters, executable=None):
        state['phase'] = name
        record = {'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat()}
        state['steps'][name] = record
        with (CAMPAIGN / (name + '.log')).open('w') as output:
            process = subprocess.Popen([executable or sys.executable, '-B', '-m', module, *parameters],
                cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            record['pid'] = process.pid
            save()
            record['returncode'] = process.wait()
        record.update(status='PASSED' if record['returncode'] == 0 else 'FAILED',
                      finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        if record['returncode']:
            raise RuntimeError('live_step_failed:' + name)
    try:
        phoenix_python = str(Path.home() / '.local/share/rosa-envs/phoenix/bin/python')
        step('hosted', __package__ + '.runner', '--backend', 'siwc')
        step('audit-hosted', __package__ + '.audit', '--backend', 'siwc', executable=phoenix_python)
        step('local', __package__ + '.runner', '--backend', 'ollama')
        step('audit-local', __package__ + '.audit', '--backend', 'ollama', executable=phoenix_python)
        state.update(status='COMPLETE', phase='ready_for_report_and_commit')
    except BaseException as error:
        state.update(status='FAILED', error_type=type(error).__name__)
        raise
    finally:
        from dotenv import dotenv_values
        endpoint = dotenv_values(ROOT / '.env').get('OLLAMA_BASE_URL')
        if endpoint:
            try:
                request = Request(endpoint + '/api/generate', data=b'{"model":"qwen3.5:9b","keep_alive":0}', headers={'Content-Type': 'application/json'})
                with build_opener(ProxyHandler({})).open(request, timeout=30) as response:
                    cleanup = json.load(response)
                (CAMPAIGN / 'model-cleanup.json').write_text(json.dumps({'done': cleanup.get('done'), 'reason': cleanup.get('done_reason')}))
            except Exception as error:
                state['cleanup_error'] = type(error).__name__
        (CAMPAIGN / 'monitor.stop').write_text('Live execution finished or stopped.')
        state['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    main()
