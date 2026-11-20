"""Read-only ten-second telemetry, bound to the actual extension container."""
import sys,json,time,subprocess,urllib.request
from pathlib import Path
from datetime import datetime,timezone
b=Path(sys.argv[1]).resolve()
assert b.parent.name=='backends'
out=b.parent.parent/'operator/live'/b.name/'telemetry.jsonl'
for _ in range(2900):
 row={'utc':datetime.now(timezone.utc).isoformat()}
 for key,cmd in {'gpu':['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.free,clocks.current.sm,clocks.current.memory,temperature.gpu,power.draw','--format=csv,noheader'],
 'processes':['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],
 'container':['docker','inspect','--format','{{json .State}}','marvel-g1-extension-20261119']}.items():
  try:
   p=subprocess.run(cmd,capture_output=True,text=True,timeout=5);row[key]={'rc':p.returncode,'stdout':p.stdout[:2200]}
  except Exception as e:row[key]={'error_type':type(e).__name__}
 try:
  with urllib.request.urlopen('http://127.0.0.1:11439/api/ps',timeout=3) as response:row['models']=json.load(response)
 except Exception as e:row['models_error']=type(e).__name__
 try:state=json.loads((b/'status.json').read_text());row['campaign']={k:state.get(k) for k in ['status','completed','live_model_requests','charged_total_requests']}
 except FileNotFoundError:state={}
 with out.open('a') as f:f.write(json.dumps(row)+'\n')
 if state.get('status') in ['COMPLETE','STOPPED']:break
 time.sleep(10)

