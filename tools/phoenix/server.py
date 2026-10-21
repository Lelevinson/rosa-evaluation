"""Start/stop the project-owned persistent loopback Phoenix process."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
from urllib.request import urlopen
from urllib.parse import urlparse
from experiments.config import ROOT, phoenix_url, tool_state_dir

TOOL = Path(__file__).resolve().parent
STATE = tool_state_dir('phoenix')
PID = STATE / 'process.json'
URL = phoenix_url()
HOST = urlparse(URL).hostname
PORT = urlparse(URL).port or 80


def owned_process():
    if not PID.exists():
        return None
    record = json.loads(PID.read_text())
    proc = Path('/proc') / str(record['pid'])
    try:
        return record['pid'] if (proc.joinpath('stat').read_text().split()[21] == record['started']
            and b'tools.phoenix.phoenix_server' in proc.joinpath('cmdline').read_bytes()
            and proc.joinpath('cwd').resolve() == ROOT) else None
    except FileNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    args = parser.parse_args()
    pid = owned_process()
    if args.action == 'stop':
        if pid:
            os.kill(pid, signal.SIGTERM)
            for _ in range(150):
                if not owned_process():
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError('Server did not stop; inspect log before intervening.')
        PID.unlink(missing_ok=True)
        print('Phoenix stopped. Trace storage retained.')
    elif args.action == 'status':
        if not pid:
            raise SystemExit('Phoenix is not running under this controller.')
        with urlopen(URL, timeout=3) as response:
            print(f'Phoenix PID {pid}, HTTP {response.status}, {URL}, data={STATE / "data"}')
    else:
        if pid:
            print(f'Phoenix already running: PID {pid}, {URL}')
            return
        with socket.socket() as check:
            check.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            check.bind((HOST, PORT))
        STATE.mkdir(parents=True, exist_ok=True)
        # Whitelist environment; no inherited cloud tokens, database URL or exporters.
        env = {key: os.environ[key] for key in ('HOME', 'PATH', 'LANG', 'LC_ALL', 'TMPDIR') if key in os.environ}
        env.update(PHOENIX_HOST=HOST, PHOENIX_PORT=str(PORT),
                   PHOENIX_WORKING_DIR=str(STATE / 'data'),
                   PHOENIX_TELEMETRY_ENABLED='false', PHOENIX_ALLOW_EXTERNAL_RESOURCES='false',
                   PHOENIX_DISABLE_AGENT_ASSISTANT='true', PHOENIX_ENABLE_MCP_SERVER='false',
                   PHOENIX_ALLOWED_SANDBOX_PROVIDERS='')
        with (STATE / 'server.log').open('ab') as log:
            process = subprocess.Popen([str((TOOL / '.venv').resolve() / 'bin/python'), '-m',
                'tools.phoenix.phoenix_server', 'serve'], cwd=ROOT, env=env,
                stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        PID.write_text(json.dumps({'pid': process.pid,
            'started': Path(f'/proc/{process.pid}/stat').read_text().split()[21]}))
        for _ in range(240):
            if process.poll() is not None:
                raise RuntimeError(f'Phoenix exited; inspect {STATE / "server.log"}')
            try:
                with urlopen(URL, timeout=1) as response:
                    if response.status == 200:
                        print(f'Phoenix ready: {URL}, PID {process.pid}, data={STATE / "data"}')
                        return
            except OSError:
                pass
            time.sleep(0.2)
        raise RuntimeError(f'Phoenix readiness timed out; inspect {STATE / "server.log"}')


if __name__ == '__main__':
    main()
