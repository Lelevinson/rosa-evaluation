"""Windows coordinator: serialized owned servers and durably bounded requests."""
from pathlib import Path
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import URLError
import hashlib
import json
import os
import queue
import re
import socket
import subprocess
import threading
import time

from report import comparison, render, results

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
OPENER=build_opener(ProxyHandler({}))
STARTED=time.monotonic()
CONFIG=json.loads((ROOT/'protocol.json').read_text())
STATE={'status':'PREPARING','profile':None,'ordinal':None,'charged_requests':0,
       'known_input_tokens':0,'known_output_tokens':0,'unreturned_output_upper_bound':0,
       'max_requests':45,'tool_dispatches':0}


def save(path, obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')


def checkpoint():
    charged=list((ROOT/'reservations').glob('*.json'))
    rows=[r for p in ('A','B','C') for r in results(p)]
    good=[r for r in rows if r['status']=='RETURNED']
    STATE.update(charged_requests=len(charged),known_input_tokens=sum(r['usage']['input_tokens'] for r in good),
        known_output_tokens=sum(r['usage']['output_tokens'] for r in good),
        unreturned_output_upper_bound=1024*(len(charged)-len(good)),elapsed_seconds=time.monotonic()-STARTED)
    save(ROOT/'status.json',STATE)
    render()


def verify():
    frozen=json.loads((ROOT/'freeze.json').read_text())
    for name,digest in frozen['probe_files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'frozen_source_changed:'+name
    assert time.monotonic()-STARTED<9000,'campaign_external_deadline'


def get(endpoint,path,body=None):
    req=Request(endpoint+path,data=json.dumps(body).encode() if body is not None else None,
                headers={'Content-Type':'application/json'})
    with OPENER.open(req,timeout=10) as response:return json.load(response)


def gpu_gate(path,owned=0,during=False):
    args=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'gpu_gate.ps1'),
          '-OutputFile',str(path),'-OwnedServerId',str(owned)]
    if during:args+=['-DuringRequest']
    result=subprocess.run(args,capture_output=True,text=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    if not path.exists():
        save(path,{'pass':False,'gate_process_exit':result.returncode,'stderr':result.stderr})
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    if result.returncode or not data.get('pass'):raise RuntimeError('gpu_gate_failed:'+path.relative_to(ROOT).as_posix())


def wait_event(events,deadline,server,folder):
    last_probe=time.monotonic()
    probe=0
    while time.monotonic()<deadline:
        verify()
        if server is not None and server.poll() is not None:raise RuntimeError('owned_server_exited')
        try:return events.get(timeout=1)
        except queue.Empty:pass
        if server is not None and time.monotonic()-last_probe>15:
            probe+=1;gpu_gate(folder/f'during-{probe:02d}.json',server.pid,True);checkpoint();last_probe=time.monotonic()
    raise TimeoutError('external_request_or_worker_deadline')


def validate_runtime(folder,profile,endpoint):
    log=(folder/'server-stderr.log').read_text(encoding='utf-8',errors='replace')
    precision=CONFIG['profiles'][profile]['kv_type']
    assert 'Flash Attention enabled' in log,'effective_FA_not_enabled'
    assert f'K ({precision})' in log and f'V ({precision})' in log,'effective_KV_type_mismatch'
    loaded=get(endpoint,'/api/ps')
    model=next(m for m in loaded['models'] if m['name']=='qwen3.5:9b')
    assert model['digest']==CONFIG['digest'] and model['context_length']==CONFIG['profiles'][profile]['num_ctx']
    save(folder/'loaded-model.json',loaded)
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,clocks.current.sm,power.draw',
        '--format=csv'],capture_output=True,text=True,timeout=10)
    save(folder/'gpu-loaded.json',{'stdout':gpu.stdout,'stderr':gpu.stderr})
    env=os.environ.copy();env['OLLAMA_HOST']=endpoint
    ps=subprocess.run([str(WORKSPACE/'.local/ollama-0.40.6/ollama.exe'),'ps'],capture_output=True,text=True,timeout=10,env=env)
    (folder/'ollama-ps.txt').write_text(ps.stdout,encoding='utf-8')
    offload=re.findall(r'offloaded (\d+)/(\d+) layers to GPU',log)
    kv=re.findall(r'CUDA0 KV buffer size\s*=\s*([\d.]+) MiB',log)
    first=json.loads((folder/'00/result.json').read_text())
    save(folder/'hardware.json',{'offload_layers':list(map(int,offload[-1])) if offload else None,
        'gpu_KV_mib':float(kv[-1]) if kv else None,'loaded_model':model,
        'physical_gpu_reading':gpu.stdout,'ollama_ps':ps.stdout,'effective_FA':True,
        'effective_KV':precision,'warmup_load_seconds':first['metadata']['load_duration']/1e9})
    save(folder/'runtime-check.json',{'pass':True,'effective_FA_enabled':True,'effective_KV':precision,
        'context':model['context_length'],'model_digest':model['digest']})


def profile_run(profile,gateway):
    folder=ROOT/profile;folder.mkdir(exist_ok=False)
    STATE.update(profile=profile,ordinal=None,status='PROFILE_PREFLIGHT');checkpoint()
    gpu_gate(folder/'pre-server-gpu.json')
    endpoint=f'http://{gateway}:11437'
    with socket.socket() as port:
        if port.connect_ex((gateway,11437))==0:raise RuntimeError('unowned_service_on_probe_port')
    env=os.environ.copy()
    for k in ('OLLAMA_FLASH_ATTENTION','OLLAMA_KV_CACHE_TYPE','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY'):
        env.pop(k,None)
    env.update(OLLAMA_HOST=f'{gateway}:11437',OLLAMA_MODELS=str(Path.home()/'.ollama/models'),
        OLLAMA_NO_CLOUD='1',OLLAMA_NOPRUNE='1',OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',
        OLLAMA_CONTEXT_LENGTH='4096',OLLAMA_KEEP_ALIVE='2m',OLLAMA_DEBUG_LOG_REQUESTS='false')
    if profile!='A':env.update(OLLAMA_FLASH_ATTENTION='true',OLLAMA_KV_CACHE_TYPE='q8_0')
    server=worker=None
    stdout=(folder/'server-stdout.log').open('w',encoding='utf-8')
    stderr=(folder/'server-stderr.log').open('w',encoding='utf-8')
    worker_stderr=(folder/'worker-stderr.log').open('w',encoding='utf-8')
    try:
        server=subprocess.Popen([str(WORKSPACE/'.local/ollama-0.40.6/ollama.exe'),'serve'],env=env,
            stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        save(folder/'owned-server.json',{'pid':server.pid,'endpoint':endpoint,'profile':profile})
        until=time.monotonic()+60
        version=None
        while time.monotonic()<until:
            if server.poll() is not None:raise RuntimeError('server_failed_startup')
            try:version=get(endpoint,'/api/version');break
            except (URLError,TimeoutError):time.sleep(.5)
        assert version and version['version']=='0.40.6','pinned_version_unavailable'
        tags=get(endpoint,'/api/tags')
        model=next(m for m in tags['models'] if m['name']=='qwen3.5:9b')
        assert model['digest']==CONFIG['digest'],'pinned_digest_mismatch'
        save(folder/'verified-version-model.json',{'version':version,'model':model})
        linux='/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/qwen-serving-phase1-20261112/worker.py'
        worker_env=os.environ.copy()
        for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY'):worker_env.pop(k,None)
        worker=subprocess.Popen(['wsl.exe','--distribution','Ubuntu-24.04','--user','martin','--exec',
            '/home/martin/.local/share/rosa-envs/research/bin/python','-B',linux,profile,endpoint],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=worker_stderr,text=True,bufsize=1,
            env=worker_env,creationflags=subprocess.CREATE_NO_WINDOW)
        events=queue.Queue()
        def reader():
            for line in worker.stdout:
                try:events.put(json.loads(line))
                except ValueError:events.put({'event':'unexpected_stdout'})
            events.put({'event':'worker_eof'})
        threading.Thread(target=reader,daemon=True).start()
        assert wait_event(events,time.monotonic()+60,server,folder)['event']=='ready','worker_not_ready'
        for ordinal,job in enumerate(CONFIG['schedule']):
            verify()
            gpu_gate(folder/f'before-{ordinal:02d}.json',server.pid)
            STATE.update(status='RUNNING',ordinal=ordinal,fixture=job['fixture']);checkpoint()
            worker.stdin.write(json.dumps({'profile':profile,'ordinal':ordinal})+'\n');worker.stdin.flush()
            event=wait_event(events,time.monotonic()+210,server,folder)
            checkpoint()
            if event.get('event')!='returned':raise RuntimeError('request_not_returned:'+str(event))
            assert event['ordinal']==ordinal and event['profile']==profile
            assert event['prompt_count_matches'],'prompt_count_equivalence_failed'
            if ordinal==0:validate_runtime(folder,profile,endpoint)
            print(json.dumps({'profile':profile,'completed_requests':ordinal+1,'profile_cap':15,
                'charged_requests':STATE['charged_requests'],'output_tokens':STATE['known_output_tokens']}),flush=True)
        STATE['status']='PROFILE_COMPLETE';checkpoint()
    finally:
        if server is not None and server.poll() is None:
            try:get(endpoint,'/api/chat',{'model':'qwen3.5:9b','messages':[],'keep_alive':0,'stream':False})
            except Exception:pass
            killed=subprocess.run(['taskkill.exe','/PID',str(server.pid),'/T','/F'],capture_output=True,text=True,timeout=15)
            save(folder/'cleanup.json',{'exit_code':killed.returncode,'stdout':killed.stdout,'stderr':killed.stderr})
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait(timeout=5)
        if worker is not None:
            try:worker.stdin.close()
            except Exception:pass
            try:worker.wait(timeout=10)
            except subprocess.TimeoutExpired:worker.kill();worker.wait(timeout=5)
        stdout.close();stderr.close();worker_stderr.close()
        checkpoint()


def main():
    with (ROOT/'RUN_ONCE').open('x') as f:f.write('No automatic resume or replay.\n')
    verify();checkpoint()
    try:
        ps=subprocess.run(['wsl.exe','--distribution','Ubuntu-24.04','--user','martin','--exec','/usr/bin/ps','-eo','pid,comm'],capture_output=True,text=True,timeout=30)
        save(ROOT/'wsl-process-preflight.json',{'exit_code':ps.returncode,'stdout':ps.stdout,'stderr':ps.stderr})
        assert ps.returncode==0,'WSL_process_preflight_failed'
        assert not any(line.split()[-1] in ('gz','gzserver','gzclient','ollama','llama-server') for line in ps.stdout.splitlines() if line.split()),'WSL_competing_worker'
        route=subprocess.run(['wsl.exe','--distribution','Ubuntu-24.04','--user','martin','--exec','/usr/sbin/ip','-4','route','show','default'],capture_output=True,text=True,timeout=30)
        assert route.returncode==0 and 'via ' in route.stdout,'WSL_gateway_unavailable'
        gateway=route.stdout.split('via ',1)[1].split()[0]
        for profile in ('A','B'):
            if profile=='B':
                STATE['status']='UNLOADED_COOLDOWN';checkpoint();time.sleep(30)
            profile_run(profile,gateway)
        screen=comparison('B')
        save(ROOT/'stage1-decision.json',screen)
        if screen['candidate']:
            STATE['status']='CONDITIONAL_C_COOLDOWN';checkpoint();time.sleep(30)
            profile_run('C',gateway)
        else:save(ROOT/'stage2-decision.json',{'C_run':False,'reason':'B did not pass all predefined candidate gates; no Phase 0 context bottleneck established.'})
        STATE.update(status='COMPLETE',profile=None,ordinal=None)
    except BaseException as exc:
        STATE.update(status='STOPPED_NO_AUTOMATIC_RETRY',stop_reason=str(exc),stop_type=type(exc).__name__)
    finally:
        frozen=json.loads((ROOT/'freeze.json').read_text())
        m4=WORKSPACE/'rosa-evaluation/artifacts/macro-m4-20261027'
        old=WORKSPACE/'rosa-evaluation/artifacts/qwen-timing-probe-20261112'
        protected=json.loads((old/'protected-m4-before.json').read_text())
        mismatches=[name for name,digest in protected.items() if hashlib.sha256((m4/name).read_bytes()).hexdigest()!=digest]
        freeze=json.loads((m4/'freeze.json').read_text())
        changed=[name for name,digest in freeze['files'].items() if hashlib.sha256((WORKSPACE/name).read_bytes()).hexdigest()!=digest]
        save(ROOT/'closeout-integrity.json',{'M4_files_verified':len(protected),'M4_mismatches':mismatches,
            'frozen_sources_verified':len(freeze['files']),'frozen_source_mismatches':changed,
            'phase0_manifest_unchanged':hashlib.sha256((old/'manifest.json').read_bytes()).hexdigest()==frozen['phase0_manifest_sha256']})
        if mismatches or changed:STATE.update(status='STOPPED_INTEGRITY_EXCEPTION',stop_reason='Protected M4/source hash changed')
        checkpoint()
        print(json.dumps({'status':STATE['status'],'charged_requests':STATE['charged_requests'],
            'stop_reason':STATE.get('stop_reason')}),flush=True)


if __name__=='__main__':main()
