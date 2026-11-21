"""Own a local Phoenix on 127.0.0.1:6006 for the weekend runs (same settings as G1 stage-4/launch.py).
Usage (WSL): phoenix_service.py start|stop|status --store <dir>. Refuses to touch a Phoenix it does not own."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.request

PHOENIX = '/home/martin/.local/share/rosa-envs/phoenix/bin/python'
REPO = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation')  # tools.phoenix.phoenix_server lives here


def healthy():
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:6006/healthz', timeout=2) as r:
            return r.status == 200
    except OSError:
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('start', 'stop', 'status'))
    p.add_argument('--store', required=True, type=Path)
    a = p.parse_args()
    record = a.store / 'phoenix-service.json'
    if a.action == 'status':
        print(json.dumps({'healthy': healthy(), 'record': json.loads(record.read_text()) if record.exists() else None}))
        return
    if a.action == 'stop':
        r = json.loads(record.read_text())
        os.killpg(r['pid'], signal.SIGTERM)
        r['stopped'] = True
        record.write_text(json.dumps(r, indent=2) + '\n')
        return
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', 6006)) == 0:
            raise SystemExit('port 6006 already in use; not touching an existing service')
    (a.store / 'data').mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ('HOME', 'PATH', 'LANG', 'LC_ALL', 'TMPDIR')}
    env.update(PYTHONPATH=str(REPO), PYTHONDONTWRITEBYTECODE='1', PHOENIX_HOST='127.0.0.1', PHOENIX_PORT='6006',
               PHOENIX_WORKING_DIR=str(a.store / 'data'), PHOENIX_TELEMETRY_ENABLED='false',
               PHOENIX_ALLOW_EXTERNAL_RESOURCES='false', PHOENIX_DISABLE_AGENT_ASSISTANT='true',
               PHOENIX_ENABLE_MCP_SERVER='false', PHOENIX_ALLOWED_SANDBOX_PROVIDERS='')
    log = (a.store / 'server.log').open('a')
    proc = subprocess.Popen([PHOENIX, '-B', '-m', 'tools.phoenix.phoenix_server', 'serve'], cwd=REPO, env=env,
                            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    record.write_text(json.dumps({'pid': proc.pid, 'port': 6006, 'storage': str(a.store / 'data'),
                                  'owned_by': 'weekend runner A', 'stopped': False}, indent=2) + '\n')
    deadline = time.monotonic() + 90
    while not healthy():
        if proc.poll() is not None or time.monotonic() > deadline:
            raise SystemExit('phoenix did not become healthy; see server.log')
        time.sleep(.5)
    print('phoenix healthy pid', proc.pid)


if __name__ == '__main__':
    main()
