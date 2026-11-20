"""Sequential lab execution only after one explicit combined owner acknowledgment."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,shlex,time,urllib.request
ROOT=Path(__file__).resolve().parents[1]
LAB=Path('/media/naeem/d1/marvel proj')
WS=ROOT.parent.parents[3]
CONTAINER='marvel-g1-extension-20261119'
ORDER=['ministral','granite','llama']
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
def api(path,data=None):
 q=urllib.request.Request('http://127.0.0.1:11439'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(q,timeout=30) as r:return json.load(r)
def verify():
 assert subprocess.check_output(['docker','inspect','--format','{{.Image}}',CONTAINER],text=True).strip()=='sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2'
 assert api('/api/version')['version']=='0.40.6'
 f=read(ROOT/'EXTENSION_INPUT_FREEZE.json')
 assert all(sha(ROOT/n)==h for n,h in f['root_files_sha256'].items())
 assert all(sha(WS/n)==h for n,h in read(ROOT/'PROTECTED_BEFORE.json')['files_sha256'].items())
 parent=read(ROOT.parent/'stage-4/freeze.json')
 assert all(sha(WS/n)==h for n,h in parent['files_sha256'].items())
 for slug in ORDER:
  b=ROOT/'backends'/slug
  if read(b/'ELIGIBILITY.json')['eligibility']!='ELIGIBLE':continue
  assert sha(b/'freeze.json')==f['backend_seals_sha256'][slug]
  assert all(sha(b/n)==h for n,h in read(b/'freeze.json')['files_sha256'].items())
 return True
def idle(slug):
 assert api('/api/ps')['models']==[]
 samples=[]
 for i in range(3):
  text=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader'],text=True).strip()
  samples.append({'utc':datetime.now(timezone.utc).isoformat(),'gpu':text,'percent':int(text.split(',')[-1].strip().split()[0])})
  if i<2:time.sleep(2)
 write(ROOT/'operator/live'/slug/'fresh-idle.json',{'samples':samples})
 assert all(x['percent']<=5 for x in samples),'GPU_contention'
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args();assert args.execute
 ack=read(ROOT/'owner-launch-acknowledgment.json')
 assert ack['launch_allowed'] and ack['model_order']==ORDER and ack['maximum_attempts']==228 and ack['physical_request_cap_per_model']==611
 assert ack['extension_input_freeze_sha256']==sha(ROOT/'EXTENSION_INPUT_FREEZE.json')
 verify();assert not (ROOT/'BENCHMARK_RUN_ONCE').exists()
 (ROOT/'BENCHMARK_RUN_ONCE').write_text('No failed/completed cell replay; independent cumulative backend budgets.\n')
 live=ROOT/'operator/live';live.mkdir(exist_ok=False)
 state={'status':'RUNNING','model_order':ORDER,'current_model':None,'completed_models':[],'benchmark_launch_authorization_sha256':sha(ROOT/'owner-launch-acknowledgment.json'),'charged_preflight_requests':6,'cleanup_requests':{}}
 try:
  for slug in ORDER:
   b=ROOT/'backends'/slug;config=read(b/'MODEL_CONFIG.json')
   if read(b/'ELIGIBILITY.json')['eligibility']!='ELIGIBLE':
    state['completed_models'].append({'model':slug,'status':'NOT_RUN_INELIGIBLE'});continue
   verify();idle(slug)
   tag=next(m for m in api('/api/tags')['models'] if m['name']==config['tag']);assert tag['digest']==config['digest']
   state['current_model']=slug;write(ROOT/'SEQUENCE_STATUS.json',state)
   assert not (b/'owner-launch-acknowledgment.json').exists()
   write(b/'owner-launch-acknowledgment.json',{'launch_allowed':True,'trials':76,'physical_request_cap':611,'freeze_sha256':sha(b/'freeze.json'),'authority':'single explicit combined owner acknowledgment','combined_ack_sha256':sha(ROOT/'owner-launch-acknowledgment.json')})
   internal=Path('/work')/(b/'launch.py').relative_to(LAB)
   command='source /opt/ros/jazzy/setup.bash && '+shlex.join(['/work/runtime/envs/research/bin/python','-B',str(internal),'--execute'])
   with (live/slug/'worker.log').open('x') as log:
    child=subprocess.Popen(['docker','exec',CONTAINER,'bash','-lc',command],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
   with (live/slug/'telemetry.log').open('x') as log:
    observer=subprocess.Popen(['python3','-B',str(ROOT/'operator/observe_live.py'),str(b)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
   write(live/slug/'worker.json',{'pid':child.pid,'observer_pid':observer.pid,'detached':True,'container':CONTAINER})
   rc=child.wait();status=read(b/'status.json')
   assert rc==0 and status['status']=='COMPLETE' and status['completed']==76,'backend_stopped_preserve_before_resume'
   rows=[read(p) for p in (b/'trials').glob('*/result.json')]
   assert len(rows)==76 and all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
   assert status['charged_total_requests']<=611
   cleanup=0;resident=api('/api/ps')['models']
   if resident:
    assert len(resident)==1 and resident[0]['name']==config['tag']
    assert status['charged_total_requests']<611,'no_remaining_cleanup_request'
    elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(status['started_utc'])).total_seconds();assert elapsed<28800,'live_window_expired_no_extra_request'
    receipt={'kind':'UNLOAD_AFTER_BATCH','charged_request':True,'reserved_before_dispatch':True,'before_total':status['charged_total_requests']}
    write(live/slug/'cleanup.json',receipt)
    result=api('/api/generate',{'model':config['tag'],'prompt':'','stream':False,'think':False,'keep_alive':0})
    assert not result.get('response','') and not result.get('thinking','')
    cleanup=1;receipt.update(status='RETURNED_EMPTY',after_total=status['charged_total_requests']+1);write(live/slug/'cleanup.json',receipt)
   state['cleanup_requests'][slug]=cleanup
   state['completed_models'].append({'model':slug,'status':'EXECUTION_COMPLETE_REVIEW_PENDING','inference_requests':status['live_model_requests'],'charged_including_setup_cleanup':status['charged_total_requests']+cleanup})
   state['current_model']=None;write(ROOT/'SEQUENCE_STATUS.json',state)
   reporter=Path('/work')/(ROOT/'operator/report_backend.py').relative_to(LAB)
   report_command='source /opt/ros/jazzy/setup.bash && '+shlex.join(['/work/runtime/envs/research/bin/python','-B',str(reporter),slug])
   subprocess.run(['docker','exec',CONTAINER,'bash','-lc',report_command],check=True)
   verify();time.sleep(5)
  state['status']='EXECUTION_COMPLETE_HUMAN_REVIEW_PENDING';write(ROOT/'SEQUENCE_STATUS.json',state)
  subprocess.run(['python3','-B',str(ROOT/'operator/make_pooled_packet.py')],check=True)
 except BaseException as e:
  state.update(status='STOPPED',error_type=type(e).__name__);write(ROOT/'SEQUENCE_STATUS.json',state);raise
if __name__=='__main__':main()

