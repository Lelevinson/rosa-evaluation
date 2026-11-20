"""Own an isolated local Phoenix service; no OAuth, Ollama or hosted requests."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
PHOENIX='/home/martin/.local/share/rosa-envs/phoenix/bin/python'
RESEARCH='/home/martin/.local/share/rosa-envs/research/bin/python'

def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    assert not (ROOT/'RUN_ONCE').exists(),'Do not relaunch a frozen attempt.'
    from runner import verify
    verify()
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1',6006))==0:raise RuntimeError('Phoenix_port_already_owned_do_not_touch_existing_service')
    store=ROOT/'phoenix';store.mkdir()
    env={k:v for k,v in os.environ.items() if k in ('HOME','PATH','LANG','LC_ALL','TMPDIR')}
    env.update(PYTHONPATH=str(REPO),PYTHONDONTWRITEBYTECODE='1',PHOENIX_HOST='127.0.0.1',PHOENIX_PORT='6006',
        PHOENIX_WORKING_DIR=str(store/'data'),PHOENIX_TELEMETRY_ENABLED='false',
        PHOENIX_ALLOW_EXTERNAL_RESOURCES='false',PHOENIX_DISABLE_AGENT_ASSISTANT='true',
        PHOENIX_ENABLE_MCP_SERVER='false',PHOENIX_ALLOWED_SANDBOX_PROVIDERS='')
    process=None
    try:
        with (store/'server.log').open('w') as log:
            process=subprocess.Popen([PHOENIX,'-B','-m','tools.phoenix.phoenix_server','serve'],
                cwd=REPO,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
            write('phoenix-service.json',{'pid':process.pid,'owned_by':'G1 Stage3 zero-model control rerun','port':6006,
                'storage':str(store/'data'),'stopped':False})
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            deadline=time.monotonic()+60
            while True:
                if process.poll() is not None:raise RuntimeError('owned_Phoenix_startup_failed')
                try:
                    with opener.open('http://127.0.0.1:6006/healthz',timeout=2) as response:
                        if response.status==200:break
                except OSError:pass
                if time.monotonic()>deadline:raise TimeoutError('Phoenix_readiness_60s')
                time.sleep(.5)
            print('Owned local Phoenix ready; starting scripted controls.',flush=True)
            clean={k:v for k,v in os.environ.items() if k in ('HOME','PATH','LANG','LC_ALL','TMPDIR')}
            clean.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(REPO),OTEL_SDK_DISABLED='false')
            subprocess.run([RESEARCH,'-B',str(ROOT/'runner.py')],cwd=REPO,env=clean,check=True,timeout=1800)
            subprocess.run([PHOENIX,'-B',str(ROOT/'persisted_audit.py')],cwd=REPO,env=clean,check=True,timeout=600)
            subprocess.run([RESEARCH,'-B',str(ROOT/'finish.py')],cwd=REPO,env=clean,check=True,timeout=120)
    except BaseException as error:
        write('launch-error.json',{'error_type':type(error).__name__,'error':str(error),'live_model_requests':0})
        raise
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=20)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
            write('phoenix-service.json',{'pid':process.pid,'owned_by':'G1 Stage3 zero-model control rerun','port':6006,
                'storage':str(store/'data'),'stopped':True,'exit_code':process.returncode})

if __name__=='__main__':main()
