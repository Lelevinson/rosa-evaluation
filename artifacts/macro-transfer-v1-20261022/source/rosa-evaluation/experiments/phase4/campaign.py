"""Sequential durable phases; live execution survives closure of the chat relay."""
import argparse
from datetime import datetime, timezone
import json
import shutil
import subprocess
import sys
from urllib.request import ProxyHandler, Request, build_opener
from ..config import ROOT
from .runner import CAMPAIGN

POWERSHELL = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
SERVICES = 'C:/Proj/robotics/introtorobotics/rosa-evaluation/scripts/phase4-services.ps1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'live', 'launch'])
    args = parser.parse_args()
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    if args.mode == 'launch':
        with (CAMPAIGN / 'supervisor.log').open('a') as log:
            process = subprocess.Popen([sys.executable, '-B', '-m', __package__ + '.campaign', 'live'],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        (CAMPAIGN / 'supervisor.pid').write_text(str(process.pid) + '\n')
        print(f'Detached Phase 4 supervisor PID {process.pid}', flush=True)
        return
    path = CAMPAIGN / 'campaign.json'
    state = json.loads(path.read_text()) if path.exists() else {'started_utc': datetime.now(timezone.utc).isoformat(), 'steps': {}}

    def save():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, indent=2) + '\n')
        temporary.replace(path)
        (CAMPAIGN / 'supervisor-status.json').write_text(json.dumps({'status': state.get('status'), 'phase': state.get('phase'),
            'updated_utc': datetime.now(timezone.utc).isoformat()}, indent=2) + '\n')

    def step(name, module, *parameters):
        if name in state['steps']:
            if state['steps'][name]['status'] == 'PASSED':
                return
            raise RuntimeError(f'Preserved incomplete/failed step requires explicit review: {name}')
        state.update(status='RUNNING', phase=name)
        command = [sys.executable, '-B', '-m', module, *parameters]
        record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'command': command, 'status': 'RUNNING'}
        state['steps'][name] = record
        save()
        with (CAMPAIGN / f'{name}.log').open('w') as log:
            process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            record['pid'] = process.pid
            save()
            record['returncode'] = process.wait()
        record.update(status='PASSED' if record['returncode'] == 0 else 'FAILED', ended_utc=datetime.now(timezone.utc).isoformat())
        save()
        if record['returncode']:
            raise RuntimeError(f'Phase failed: {name}; inspect {name}.log')

    def batch_id(backend):
        return json.loads((CAMPAIGN / f'{backend}-batch.json').read_text())['batch_id']

    def unload():
        from dotenv import dotenv_values
        endpoint = dotenv_values(ROOT / '.env')['OLLAMA_BASE_URL']
        req = Request(endpoint + '/api/generate', data=b'{"model":"qwen3.5:9b","keep_alive":0}', headers={'Content-Type': 'application/json'})
        with build_opener(ProxyHandler({})).open(req, timeout=30) as response:
            value = json.load(response)
        (CAMPAIGN / 'model-cleanup.json').write_text(json.dumps({'done': value.get('done'), 'reason': value.get('done_reason')}, indent=2) + '\n')

    try:
        if args.mode == 'prepare':
            step('unit-validation', 'unittest', 'discover', '-s', 'tests', '-v')
            step('retrospective', __package__ + '.retrospective')
            step('freeze', __package__ + '.freeze')
            step('scripted', __package__ + '.runner', '--backend', 'scripted')
            step('audit-scripted', __package__ + '.audit', '--batch-id', batch_id('scripted'))
            step('diagnostics', __package__ + '.diagnostics')
            state.update(status='READY_FOR_LIVE', phase='awaiting_hosted_consent')
            save()
        else:
            for name in ('unit-validation', 'retrospective', 'freeze', 'scripted', 'audit-scripted', 'diagnostics'):
                if state['steps'].get(name, {}).get('status') != 'PASSED':
                    raise RuntimeError(f'Preflight not passed: {name}')
            subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', SERVICES, '-Action', 'start'], check=True)
            step('hosted', __package__ + '.runner', '--backend', 'siwc')
            step('audit-hosted', __package__ + '.audit', '--batch-id', batch_id('siwc'))
            step('local', __package__ + '.runner', '--backend', 'ollama')
            unload()
            step('audit-local', __package__ + '.audit', '--batch-id', batch_id('ollama'))
            subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', SERVICES, '-Action', 'stop'], check=True)
            shutil.copy2(ROOT / '.local/ollama/stderr.log', CAMPAIGN / 'ollama-stderr.log')
            (CAMPAIGN / 'execution-checkpoint.json').write_text(json.dumps(state, indent=2) + '\n')
            step('report', __package__ + '.report')
            state.update(status='COMPLETE', phase='complete', ended_utc=datetime.now(timezone.utc).isoformat())
            save()
    except BaseException as error:
        state.update(status='FAILED', error_type=type(error).__name__)
        save()
        if args.mode == 'live':
            try:
                unload()
                subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', SERVICES, '-Action', 'stop'], check=False)
            except Exception:
                pass
        raise


if __name__ == '__main__':
    main()
