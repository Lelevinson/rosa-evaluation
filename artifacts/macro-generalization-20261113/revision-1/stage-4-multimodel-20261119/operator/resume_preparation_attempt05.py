"""Continue preflight after metadata/service failures. Reuse the recorded load; no trial replay."""
from pathlib import Path
import json,hashlib,re,shutil,time
import prepare_extension as p
ROOT=p.ROOT
def files(folder):
 return {x.relative_to(folder).as_posix():p.sha(x) for x in folder.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix not in ['.pyc','.tmp'] and x.name!='freeze.json'}
def main():
 assert not (ROOT/'PREPARATION_ATTEMPT05_RUN_ONCE').exists()
 (ROOT/'PREPARATION_ATTEMPT05_RUN_ONCE').write_text('Resume existing auxiliary counters; no benchmark launch.\n')
 p.verify_original()
 tags=p.read(ROOT/'SERVER_TAGS_BEFORE.json')
 current=p.api('/api/tags')['models']
 assert all(next(m for m in current if m['name']==tag)['digest']==next(m for m in tags if m['name']==tag)['digest'] for slug,tag in p.MODELS)
 results=[]
 for slug,tag in p.MODELS:
  folder=ROOT/'backends'/slug
  if (folder/'freeze.json').exists():raise RuntimeError('Unexpected prior seal: inspect rather than rerun controls')
  if not folder.exists():
   folder.mkdir(parents=True)
   model=next(m for m in tags if m['name']==tag)
   show=p.api('/api/show',{'model':tag});p.write(folder/'SERVER_SHOW.json',show)
   config={'slug':slug,'tag':tag,'digest':model['digest'],'size_bytes':model['size'],'details':show.get('details'),
    'capabilities':show.get('capabilities',[]),'advertised_context':{k:v for k,v in show.get('model_info',{}).items() if k.endswith('.context_length')},
    'requested_context':8192,'thinking':'OFF' if 'thinking' in show.get('capabilities',[]) else 'NOT_APPLICABLE_NO_THINKING_CAPABILITY; common think=false retained',
    'template_sha256':hashlib.sha256(show.get('template','').encode()).hexdigest(),'label':'exploratory backend, added after Sol and Qwen results'}
   p.write(folder/'MODEL_CONFIG.json',config)
  config=p.read(folder/'MODEL_CONFIG.json')
  if 'tools' not in config['capabilities']:
   result={'slug':slug,'tag':tag,'eligibility':'NOT_RUN_INELIGIBLE','reason':'no tools capability','charged_requests':0};p.write(folder/'ELIGIBILITY.json',result);results.append(result);continue
  server=p.LAB/'preparation/ollama-server.log'
  if (folder/'LOADED_MODEL.json').exists():
   ledger=p.read(folder/'AUXILIARY_REQUESTS.json')
   assert slug=='ministral' and ledger['charged_requests']==2 and ledger['events'][-1]['kind']=='UNLOAD' and ledger['events'][0]['status']=='RETURNED_EMPTY'
   loaded=p.read(folder/'LOADED_MODEL.json')
   start=max(0,server.stat().st_size-200000)
   note='Recovered bounded post-failure tail: original pre-load byte offset was not recorded; load receipt and loaded API snapshot retained. No repeat load.'
  else:
   assert p.api('/api/ps')['models']==[]
   p.write(folder/'GPU_IDLE_BEFORE_LOAD.json',p.idle())
   start=server.stat().st_size;p.write(folder/'LOAD_LOG_OFFSET.json',{'byte_offset':start})
   p.lifecycle(folder,tag,'LOAD')
   loaded=p.api('/api/ps');p.write(folder/'LOADED_MODEL.json',loaded)
   note='Fresh byte range from recorded pre-load offset.'
  match=next(m for m in loaded['models'] if m['name']==tag);assert match['digest']==config['digest']
  with server.open('rb') as f:f.seek(start);data=f.read()
  text=data.decode('utf-8',errors='replace')
  selected=[line for line in text.splitlines() if any(t in line.lower() for t in ['offload','flash_attn','flash attention','kv cache','kv_cache','type_k','type_v'])]
  (folder/'FRESH_LOAD_LOG_FILTERED.txt').write_text('\n'.join(selected)+'\n')
  p.write(folder/'LOG_DECODING_RECEIPT.json',{'byte_offset':start,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'replacement_characters':text.count(chr(65533)),'note':note,'raw_payloads_not_copied':True})
  matches=re.findall(r'offloaded\s+(\d+)/(\d+)\s+layers',text,re.I);assert matches,'layer_offload_not_recorded'
  gpu,total=map(int,matches[-1])
  eligible=gpu==total and match.get('context_length')==8192 and match.get('size_vram')==match.get('size')
  result={'slug':slug,'tag':tag,'eligibility':'ELIGIBLE' if eligible else 'NOT_RUN_INELIGIBLE','gpu_layers':gpu,'total_layers':total,'loaded_context':match.get('context_length'),'size_vram':match.get('size_vram'),'loaded_size':match.get('size'),'reason':None if eligible else 'full GPU/context proof failed'}
  resident=p.api('/api/ps')['models']
  if resident:
   assert len(resident)==1 and resident[0]['name']==tag
   p.lifecycle(folder,tag,'UNLOAD')
  else:p.write(folder/'NO_UNLOAD_REQUEST_NEEDED.json',{'reason':'No resident model; prior LOAD and UNLOAD retained in immutable preflight receipts','charged_additional_requests':0})
  assert p.api('/api/ps')['models']==[]
  p.write(folder/'GPU_IDLE_AFTER_UNLOAD.json',p.idle())
  p.write(folder/'ELIGIBILITY.json',result)
  if eligible:
   p.body_sources(folder,tag,slug)
   p.run_container(folder/'validate_port.py',folder/'ZERO_CONTROLS.log','zero-model-validation-attempt02')
   p.write(folder/'freeze.json',{'phase':'PREPARATION_CANDIDATE_BEFORE_FINAL_CHECKS','files_sha256':files(folder)})
   shutil.copyfile(folder/'freeze.json',folder/'operator/PRE_CHECK_CANDIDATE_SEAL.json')
   p.run_container(folder/'operator/final_checks.py',folder/'SERIALIZATION_CHECKS.log')
   validation=p.read(folder/'zero-model-validation-attempt02/VALIDATION.json');assert validation['control_count']==8
   result.update(controls=8,local_audits=8,persisted_audits=8,serialized_bodies=p.read(folder/'operator/FINAL_ZERO_INFERENCE_CHECKS.json')['comparison_count'])
   p.write(folder/'freeze.json',{'label':config['label'],'model':tag,'digest':config['digest'],'parent_qwen_seal_sha256':p.sha(p.QWEN/'freeze.json'),'pre_run_note_sha256':p.sha(ROOT/'PRE_RUN_NOTE.md'),'files_sha256':files(folder)})
   result['seal_sha256']=p.sha(folder/'freeze.json')
  result['charged_requests']=p.read(folder/'AUXILIARY_REQUESTS.json')['charged_requests']
  results.append(result);p.write(ROOT/'MODEL_PREPARATION_PROGRESS.json',results);print(json.dumps(result),flush=True)
 p.write(ROOT/'FINAL_HASH_CHECK.json',p.verify_original())
 p.write(ROOT/'PREPARATION_RESULT.json',{'status':'READY_FOR_COMBINED_PREFLIGHT_REVIEW','models':results,'benchmark_trials_started':0,'benchmark_requests':0,'charged_auxiliary_requests':sum(x['charged_requests'] for x in results),'reviewer':'Levinson','review_not_obtained':True,'new_models_are_exploratory':True})
if __name__=='__main__':
 try:main()
 except BaseException as e:
  p.write(ROOT/'PREPARATION_ATTEMPT05_STOP.json',{'error_type':type(e).__name__,'benchmark_requests':0,'retain_all_auxiliary_ledgers':True})
  raise

