"""Read-only host telemetry; no inference, credentials, payloads, or application changes."""
from pathlib import Path
import subprocess,json,time,urllib.request
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
log=ROOT/'operator/gpu-runtime-telemetry.jsonl'
server=Path('/media/naeem/d1/marvel proj/preparation/ollama-server.log')
offset=server.stat().st_size
start=time.monotonic()
while time.monotonic()-start < 8*3600+120:
    record={'utc':datetime.now(timezone.utc).isoformat()}
    commands={
      'gpu':['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.free,clocks.current.sm,clocks.current.memory,temperature.gpu,power.draw,pstate','--format=csv,noheader'],
      'compute_processes':['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],
      'container':['docker','inspect','--format','{{json .State}}','marvel-rosa-lab-20261117']}
    for k,cmd in commands.items():
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=4)
            record[k]={'rc':p.returncode,'stdout':p.stdout[:2000]}
        except Exception as e:record[k]={'error_type':type(e).__name__}
    try:
        with urllib.request.urlopen('http://127.0.0.1:11439/api/ps',timeout=3) as response:
            record['loaded_models']=json.load(response)
    except Exception as e:record['model_inventory_error_type']=type(e).__name__
    try:
        with server.open('rb') as f:
            f.seek(offset);chunk=f.read(1024*1024);offset=f.tell()
        lower=chunk.lower()
        record['server_error_signatures']={name:lower.count(pattern) for name,pattern in
            [('CUDA_OUT_OF_MEMORY',b'cuda out of memory'),('OUT_OF_MEMORY',b'out of memory'),
             ('CONNECTION_RESET',b'connection reset'),('RUNNER_TERMINATED',b'runner process has terminated')]}
    except Exception as e:record['server_signature_error_type']=type(e).__name__
    try:
        state=json.loads((ROOT/'status.json').read_text())
        record['campaign']={k:state.get(k) for k in ['status','completed','current_trial','charged_total_requests']}
    except FileNotFoundError:state={}
    with log.open('a') as f:f.write(json.dumps(record)+'\n')
    if state.get('status') in ['COMPLETE','STOPPED']:break
    time.sleep(10)
