"""Lab-only preparation. No benchmark launch; empty-prompt lifecycle checks are charged."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess,urllib.request,time,re,math,zipfile
ROOT=Path(__file__).resolve().parents[1]
REV=ROOT.parent
WS=REV.parents[3]
QWEN=REV/'stage-4-qwen-lab-20261119'
LAB=Path('/media/naeem/d1/marvel proj')
CONTAINER='marvel-rosa-lab-20261117'
URL='http://127.0.0.1:11439'
MODELS=[('ministral','ministral-3:8b-instruct-2512-q4_K_M'),('granite','granite3.3:8b'),('llama','llama3.1:8b-instruct-q4_K_M')]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def api(path,data=None,timeout=10):
 req=urllib.request.Request(URL+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def command(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=30)
 return {'command':args,'rc':p.returncode,'stdout':p.stdout[:10000],'stderr':p.stderr[:1000]}
def run_container(script,log,*args):
 import shlex
 internal=Path('/work')/script.relative_to(LAB)
 shell='source /opt/ros/jazzy/setup.bash && '+shlex.join(['/work/runtime/envs/research/bin/python','-B',str(internal),*args])
 with log.open('x') as f:
  p=subprocess.run(['docker','exec','--user','1000:1000',CONTAINER,'bash','-lc',shell],stdout=f,stderr=f,timeout=600)
 if p.returncode:raise RuntimeError('zero_model_check_failed:'+str(log))
def verify_original():
 frozen=read(REV/'stage-4/freeze.json')['files_sha256']
 assert all(sha(WS/n)==v for n,v in frozen.items()),'original_frozen_mismatch'
 old=read(QWEN/'freeze.json')['files_sha256']
 assert all(sha(QWEN/n)==v for n,v in old.items()),'qwen_seal_mismatch'
 if (ROOT/'PROTECTED_BEFORE.json').exists():
  assert all(sha(WS/n)==v for n,v in read(ROOT/'PROTECTED_BEFORE.json')['files_sha256'].items()),'prior_evidence_mismatch'
 return {'original_inputs':len(frozen),'qwen_assembly':len(old),'pass':True}
def body_sources(folder,tag,slug):
 copied=['trial.py','local_model.py','runtime_support.py','recovery.py','tracing.py','persisted_audit.py','launch.py','validate_port.py']
 provenance=[]
 for name in copied:
  source=QWEN/name;s=source.read_text()
  s=s.replace('qwen3.5:9b',tag).replace('rosa-g1-qwen-heldout-lab-20261119','rosa-g1-'+slug+'-exploratory-lab-20261119').replace('g1.qwen.heldout','g1.'+slug+'.exploratory')
  if name=='launch.py':
   s=s.replace("'auxiliary_load_requests'","'auxiliary_requests'").replace("'MODEL_LOAD_PREFLIGHT.json'","'AUXILIARY_REQUESTS.json'").replace("'physical_load_requests'","'charged_requests'")
  (folder/name).write_text(s)
  provenance.append({'file':name,'source_sha256':sha(source),'output_sha256':sha(folder/name)})
 common='''"""Exploratory backend paths; original evidence and new seal are immutable."""
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXTENSION=ROOT.parents[1]
REV=ROOT.parents[2]
REPO=REV.parents[2]
WORKSPACE=REPO.parent
ADJUDICATION=REV/'stage-3/clarification-scoring-v2-20261119'
sys.path[:0]=[str(WORKSPACE/'rosa-research/src'),str(REPO),str(REV),str(ROOT),str(REV/'stage-2'),str(ADJUDICATION)]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,value):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(value,indent=2)+'\\n');os.replace(t,p)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(require_seal=False):
 old=read(REV/'stage-4/freeze.json')['files_sha256']
 bad=[n for n,d in old.items() if digest(WORKSPACE/n)!=d]
 bad += [n for n,d in read(EXTENSION/'PROTECTED_BEFORE.json')['files_sha256'].items() if digest(WORKSPACE/n)!=d]
 if (ROOT/'freeze.json').exists():bad += [n for n,d in read(ROOT/'freeze.json')['files_sha256'].items() if digest(ROOT/n)!=d]
 elif require_seal:raise RuntimeError('backend_not_sealed')
 if bad:raise RuntimeError('Frozen_input_mismatch:'+repr(bad))
 return {'pass':True,'original_frozen_files':len(old),'mismatches':bad}
'''
 (folder/'common.py').write_text(common)
 shutil.copyfile(QWEN/'plan.json',folder/'plan.json')
 op=folder/'operator';op.mkdir()
 s=(QWEN/'operator/final_checks.py').read_text().replace('qwen3.5:9b',tag)
 (op/'final_checks.py').write_text(s)
 shutil.copyfile(QWEN/'operator/observe_runtime.py',op/'observe_runtime.py')
 write(folder/'PORT_PROVENANCE.json',{'source_qwen_seal_sha256':sha(QWEN/'freeze.json'),'source_files':provenance,
  'changes':['model tag','artifact/path roots','Phoenix project/root identity','auxiliary setup accounting field names'],
  'unchanged':['prompts','schemas','permissions','scorer','cases','pair order','native execution','generation parameters','retry eligibility','completion and truncation behavior'],
  'benchmark_requests':0,'label':'exploratory backend, added after Sol and Qwen results'})
def summarize_qwen():
 data=read(QWEN/'operator/completed-report/results.json')
 effective={o['trial_id']:o for o in data['summary']['outcomes']}
 rows=[read(p) for p in (QWEN/'trials').glob('*/result.json')]
 groups={}
 for name,kinds in [('write_bearing',{'write','write_fault'}),('other_known_goal',{'ladder','missing_prerequisite','unavailable_source'})]:
  group=[r for r in rows if r['case']['kind'] in kinds]
  groups[name]={m:{'pass':sum(effective[r['id']]['primary_status']=='PASS' for r in group if r['mode']==m),'attempts':sum(r['mode']==m for r in group)} for m in ['primitives','macro']}
 assert groups['write_bearing']=={'primitives':{'pass':2,'attempts':8},'macro':{'pass':6,'attempts':8}}
 assert groups['other_known_goal']=={'primitives':{'pass':24,'attempts':28},'macro':{'pass':24,'attempts':28}}
 return {'label':'POST_HOC_QWEN_SPLIT_NOT_PREREGISTERED','groups':groups,
  'prediction_id_evidence':{'source':'stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md','sha256':sha(REV/'stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md'),
  'P3':'DROPPED horizon reliability','P4':'catalogue size; NOT RUN'},
  'no_original_edits':True,'model_requests':0}
def idle():
 samples=[]
 for i in range(3):
  x=command(['nvidia-smi','--query-gpu=name,memory.free,utilization.gpu','--format=csv,noheader'])
  assert x['rc']==0
  percent=int(x['stdout'].split(',')[-1].strip().split()[0])
  samples.append({'utc':datetime.now(timezone.utc).isoformat(),'output':x['stdout'],'percent':percent})
  if i<2:time.sleep(2)
 assert all(s['percent']<=5 for s in samples),'GPU_CONTENTION'
 return samples
def lifecycle(folder,tag,kind):
 path=folder/'AUXILIARY_REQUESTS.json'
 ledger=read(path) if path.exists() else {'charged_requests':0,'events':[]}
 assert ledger['charged_requests']<611
 event={'ordinal':ledger['charged_requests']+1,'kind':kind,'status':'RESERVED_BEFORE_DISPATCH','utc':datetime.now(timezone.utc).isoformat(),'task_prompt':False}
 ledger['events'].append(event);ledger['charged_requests']+=1;write(path,ledger)
 payload={'model':tag,'prompt':'','stream':False,'think':False,'keep_alive':'5m' if kind=='LOAD' else 0,
   'options':{'num_ctx':8192,'num_predict':1024,'temperature':0,'seed':42,'use_mmap':True}}
 try:
  result=api('/api/generate',payload,timeout=180)
  assert not result.get('response','') and not result.get('thinking',''),'unexpected_model_text'
  event.update(status='RETURNED_EMPTY',done_reason=result.get('done_reason','NOT_RECORDED'),
    usage_fields={k:result.get(k,'NOT_RECORDED') for k in ['total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration']})
  write(path,ledger)
  return result
 except Exception as error:
  event.update(status='ERROR',error_type=type(error).__name__,http_status=getattr(error,'code',None));write(path,ledger);raise
def main():
 assert ROOT.resolve().is_relative_to(LAB.resolve())
 assert not (ROOT/'PREPARATION_RUN_ONCE').exists()
 (ROOT/'PREPARATION_RUN_ONCE').write_text('No repeated lifecycle requests without preserving prior attempts.\n')
 write(ROOT/'INITIAL_HASH_CHECK.json',verify_original())
 protected={}
 for prior in [REV/'stage-4',QWEN]:
  for p in prior.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.tmp']:protected[p.relative_to(WS).as_posix()]=sha(p)
 for p in [WS/'rosa-evaluation/G1_QWEN_LAB_REPORT_2026-11-19.md',WS/'rosa-evaluation/G1_SOL_ADJUDICATED_REPORT_2026-11-19.md']:
  protected[p.relative_to(WS).as_posix()]=sha(p)
 write(ROOT/'PROTECTED_BEFORE.json',{'files_sha256':protected,'master_readme_excluded_for_dated_updates':True})
 write(ROOT/'QWEN_POSTHOC_SPLIT.json',summarize_qwen())
 assert sha(REV/'stage-2/scoring.py')=='90b0edd6d898ac749d121de29197a669593e022160503414413e0126766e8e4d'
 assert api('/api/ps')['models']==[],'resident_model_before_preparation'
 tags=api('/api/tags')['models'];write(ROOT/'SERVER_TAGS_BEFORE.json',tags)
 env={'driver':command(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.free','--format=csv,noheader']),
  'cuda_compatibility_header':command(['nvidia-smi'])['stdout'][:500],
  'container':command(['docker','inspect','--format','{{json .Image}} {{json .HostConfig.RestartPolicy}}',CONTAINER]),
  'processes':command(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader']),
  'zero_inference_phoenix_health':urllib.request.urlopen('http://127.0.0.1:6006/healthz',timeout=5).status}
 write(ROOT/'ENVIRONMENT.json',env)
 results=[]
 try:
  for slug,tag in MODELS:
   folder=ROOT/'backends'/slug;folder.mkdir(parents=True,exist_ok=False)
   model=next(m for m in tags if m['name']==tag)
   show=api('/api/show',{'model':tag});write(folder/'SERVER_SHOW.json',show)
   config={'slug':slug,'tag':tag,'digest':model['digest'],'size_bytes':model['size'],'details':show.get('details'),
    'capabilities':show.get('capabilities',[]),'advertised_context':{k:v for k,v in show.get('model_info',{}).items() if k.endswith('.context_length')},
    'requested_context':8192,'thinking':'OFF' if 'thinking' in show.get('capabilities',[]) else 'NOT_APPLICABLE_NO_THINKING_CAPABILITY; common think=false retained',
    'template_sha256':hashlib.sha256(show.get('template','').encode()).hexdigest(),'label':'exploratory backend, added after Sol and Qwen results'}
   write(folder/'MODEL_CONFIG.json',config)
   if 'tools' not in show.get('capabilities',[]):
    result={'slug':slug,'tag':tag,'eligibility':'NOT_RUN_INELIGIBLE','reason':'tools capability absent','charged_requests':0}
    write(folder/'ELIGIBILITY.json',result);results.append(result);continue
   assert api('/api/ps')['models']==[]
   write(folder/'GPU_IDLE_BEFORE_LOAD.json',idle())
   server=LAB/'preparation/ollama-server.log';offset=server.stat().st_size
   lifecycle(folder,tag,'LOAD')
   ps=api('/api/ps');write(folder/'LOADED_MODEL.json',ps)
   loaded=next(m for m in ps['models'] if m['name']==tag);assert loaded['digest']==config['digest']
   with server.open() as f:f.seek(offset);fresh=f.read()
   lines=[line for line in fresh.splitlines() if any(s in line.lower() for s in ['offload','flash_attn','flash attention','kv cache','kv_cache','type_k','type_v'])]
   (folder/'FRESH_LOAD_LOG_FILTERED.txt').write_text('\n'.join(lines)+'\n')
   matches=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers',fresh,re.I)
   assert matches,'layer_offload_not_recorded'
   gpu_layers,total_layers=map(int,matches[-1])
   eligible=gpu_layers==total_layers and loaded.get('context_length')==8192
   result={'slug':slug,'tag':tag,'eligibility':'ELIGIBLE' if eligible else 'NOT_RUN_INELIGIBLE',
     'gpu_layers':gpu_layers,'total_layers':total_layers,'loaded_context':loaded.get('context_length'),
     'size_vram':loaded.get('size_vram'),'loaded_size':loaded.get('size'),'reason':None if eligible else 'not fully GPU at required context'}
   lifecycle(folder,tag,'UNLOAD')
   assert api('/api/ps')['models']==[]
   write(folder/'GPU_IDLE_AFTER_UNLOAD.json',idle())
   write(folder/'ELIGIBILITY.json',result)
   if eligible:
    body_sources(folder,tag,slug)
    run_container(folder/'validate_port.py',folder/'ZERO_CONTROLS.log','zero-model-validation-attempt02')
    candidate_files={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.tmp'] and p.name!='freeze.json'}
    write(folder/'freeze.json',{'phase':'PREPARATION_CANDIDATE_BEFORE_FINAL_CHECKS','files_sha256':candidate_files})
    shutil.copyfile(folder/'freeze.json',folder/'operator/PRE_CHECK_CANDIDATE_SEAL.json')
    run_container(folder/'operator/final_checks.py',folder/'SERIALIZATION_CHECKS.log')
    assert read(folder/'zero-model-validation-attempt02/VALIDATION.json')['control_count']==8
    result.update(controls=8,local_audits=8,persisted_audits=8,serialized_bodies=read(folder/'operator/FINAL_ZERO_INFERENCE_CHECKS.json')['comparison_count'])
    files={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.tmp'] and p.name!='freeze.json'}
    write(folder/'freeze.json',{'label':config['label'],'model':tag,'digest':config['digest'],'parent_qwen_seal_sha256':sha(QWEN/'freeze.json'),'pre_run_note_sha256':sha(ROOT/'PRE_RUN_NOTE.md'),'files_sha256':files})
    result['seal_sha256']=sha(folder/'freeze.json')
   result['charged_requests']=read(folder/'AUXILIARY_REQUESTS.json')['charged_requests'];results.append(result)
   write(ROOT/'MODEL_PREPARATION_PROGRESS.json',results)
   print(json.dumps(result),flush=True)
  write(ROOT/'FINAL_HASH_CHECK.json',verify_original())
  write(ROOT/'PREPARATION_RESULT.json',{'status':'READY_FOR_COMBINED_PREFLIGHT_REVIEW','models':results,'benchmark_trials_started':0,'benchmark_requests':0,
   'charged_auxiliary_requests':sum(r['charged_requests'] for r in results),'reviewer':'Levinson','review_not_obtained':True,'new_models_are_exploratory':True})
 except BaseException as error:
  write(ROOT/'PREPARATION_STOP.json',{'status':'STOPPED','error_type':type(error).__name__,'completed_models':results,'benchmark_trials_started':0})
  raise
if __name__=='__main__':main()

