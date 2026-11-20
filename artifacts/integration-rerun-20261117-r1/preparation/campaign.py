"""New opt-in profile campaign; imports old frozen runner without editing it."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
import httpx
import ollama

from tool_contract_ollama import ToolContractProfile, PROFILE_VERSION

ROOT=Path('/work')
BASE=Path(__file__).resolve().parents[1]
PROJECT='rosa-native-schema-rerun-20261117'
MODELS=['llama3.1:8b-instruct-q4_K_M','granite3.3:8b']
spec=importlib.util.spec_from_file_location('original_lab',ROOT/'study/lab_study.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
original_factory=lab.configured_model
lab.RESULTS=BASE/'results';lab.STUDY=BASE/'source';lab.PROJECT=PROJECT
lab.MODELS=MODELS;lab.ORDER=MODELS


def verify():
    record=json.loads((BASE/'freeze.json').read_text())
    for name,expected in record['files'].items():
        assert lab.sha(ROOT/name)==expected, 'Frozen source mismatch: '+name
    tags={m['name']:m['digest'] for m in lab.api('/api/tags')['models']}
    assert all(tags[m]==digest for m,digest in record['model_digests'].items())
    return record


lab.verify=verify


def fixtures():
    return [
        {'id':'inspect_ready','skill':'fixture.inspect','status':'SUCCESS','fault':'none','ready':1.0,
         'request':'Check fixture readiness and report the result. Do not move the fixture.'},
        {'id':'inspect_unready','skill':'fixture.inspect','status':'FAILURE','fault':'none','ready':0.0,
         'request':'Inspect fixture readiness. Report whether it is ready; do not change its position.'},
        {'id':'set_level','skill':'fixture.adjust','status':'SUCCESS','fault':'none','ready':1.0,
         'request':'Set the fixture level to the registered target 0.35, verify it, and report the outcome.'},
        {'id':'write_no_effect','skill':'fixture.adjust','status':'FAILURE','fault':'ineffective','ready':1.0,
         'request':'Set fixture level to 0.35 and verify the result. If the command has no effect, report FAILURE; do not repeat the command.'},
        {'id':'source_unavailable','skill':'fixture.adjust','status':'UNKNOWN','fault':'missing','ready':1.0,
         'request':'Set fixture level to 0.35 only if its current level can be observed. If observations are unavailable, report UNKNOWN without writing.'},
        {'id':'expired_observation','skill':'fixture.inspect','status':'SUCCESS','fault':'expire','ready':1.0,
         'request':'Inspect fixture readiness and report it. If your report is rejected because evidence is stale, acquire fresh evidence and report again. Do not move.'},
    ]


def freeze():
    assert not (BASE/'freeze.json').exists()
    old=json.loads((ROOT/'study/freeze.json').read_text())
    files=dict(old['files'])
    for name,digest in files.items():assert lab.sha(ROOT/name)==digest
    files['study/freeze.json']=lab.sha(ROOT/'study/freeze.json')
    files.update({str(p.relative_to(ROOT)):lab.sha(p) for p in (BASE/'source').iterdir() if p.is_file()})
    for model in MODELS:
        metadata=json.loads((ROOT/'preparation'/('model-'+lab.key(model)+'.json')).read_text())
        assert 'tools' in metadata['capabilities']
    lab.write(BASE/'freeze.json',{'date':'2026-11-17','files':files,'model_digests':{
        m:old['model_metadata'][m]['digest'] for m in MODELS},'profile':PROFILE_VERSION,
        'schedule':lab.schedule(MODELS[0]),'validation_fixtures':fixtures(),
        'validation_requests_per_model':96,'robot_requests_per_model':643,
        'robot_trials_per_model':80,'robot_controls':20,'http_stream':False,
        'context':8192,'output_per_call':1024,'output_per_task':2048,'temperature':0,'seed':42,
        'validation_gate':'All audits/bounds pass; each model completes >=1 healthy SUCCESS loop per execution mode.',
        'frozen_unix':time.time()})
    verify(); print('FROZEN',len(files),'hashes',flush=True)


class WireCapture(httpx.BaseTransport):
    def __init__(self,folder):
        self.folder=folder;self.folder.mkdir(parents=True,exist_ok=True)
        assert not list(folder.glob('*.json'))
        self.count=0;self.inner=httpx.HTTPTransport(retries=0)

    def handle_request(self,request):
        assert request.url.host=='127.0.0.1' and request.url.port==11439
        body=json.loads(request.content)
        assert body['stream'] is False
        opts=body['options']
        assert opts['num_ctx']==8192 and opts['temperature']==0 and opts['seed']==42
        assert 0<opts['num_predict']<=1024
        if body.get('tools'):
            assert any('Available function schemas (retain these after tool results):' in m.get('content','')
                for m in body['messages'] if m['role']=='system')
        self.count+=1;path=self.folder/f'{self.count:04d}.json'
        row={'request':body,'status':'STARTED','started_unix':time.time()}
        lab.write(path,row)
        try:
            response=self.inner.handle_request(request);payload=response.read()
            row.update(status='RETURNED',http_status=response.status_code,response=json.loads(payload))
            return response
        except BaseException as error:
            row.update(status='ERROR',error_type=type(error).__name__)
            raise
        finally:lab.write(path,row)

    def close(self):self.inner.close()


def configured_model(model,max_output=1024,journal=None,wire_folder=None):
    base=original_factory(model,max_output=max_output,journal=journal)
    class ProfiledMeasuredChat(ToolContractProfile,type(base)):
        pass
    value=ProfiledMeasuredChat(**base.model_dump())
    capture=WireCapture(wire_folder or BASE/'results'/lab.key(model)/'wire')
    value._client=ollama.Client(host=lab.ENDPOINT,timeout=180,transport=capture)
    return value


lab.configured_model=configured_model


def gpu_gate(model):
    record=json.loads((BASE/('gpu-'+lab.key(model)+'.json')).read_text())
    assert record['model']==model and record['pass'] and 0<=time.time()-record['at_unix']<=120
    lab.write(BASE/'results'/lab.key(model)/'gpu-preflight.json',record)


lab.gpu_gate=gpu_gate


def persisted(folder,project):
    command='import experiments.macro_capabilities_v2.persisted as p; p.PROJECT='+repr(project)+'; p.main()'
    run=subprocess.run([str(ROOT/'runtime/envs/phoenix/bin/python'),'-B','-c',command,'--folder',str(folder)],
        cwd=ROOT/'baseline/rosa-evaluation',capture_output=True,text=True,timeout=60)
    (folder/'phoenix-audit.log').write_text(run.stdout+run.stderr)
    assert run.returncode==0,'Persisted Phoenix audit failed'
    return json.loads((folder/'phoenix-audit.json').read_text())


class FixtureState:
    def __init__(self,fault):self.value=0.0;self.fault=fault;self.writes=0;self.records=[]
    def read(self,node,fields):
        if self.fault=='missing':raise TimeoutError('fixture_observation_unavailable')
        return {name:self.value for name in fields}
    def write(self,node,values):
        self.writes+=1;self.records.append({'node':node,'values':deepcopy(values)})
        if self.fault!='ineffective':self.value=values['level']
        return {'accepted_locally':True}


class FixtureInspection:
    def __init__(self,ready):self.ready=ready
    def read_group(self,source,names):return {name:bool(self.ready) for name in names}


def registry():
    from rosa_reliability.capabilities import CapabilityRegistry,InspectionSkill
    from rosa_reliability.bounded_macro import StateSkill
    return CapabilityRegistry().register(StateSkill(skill_id='fixture.adjust',targets={'/fixture':{'level':0.35}})).register(
        InspectionSkill(skill_id='fixture.inspect',subject='/fixture_status',checks={'health':['ready']}))


def reference_report(inv,config):
    evidence=inv.session.observations[-1]
    values=evidence['observed_values'];targets=inv.session.targets
    status='UNKNOWN' if any(v is None for group in values.values() for v in group.values()) else (
        'SUCCESS' if all(abs(values[n][k]-v)<=inv.limits.tolerance for n,g in targets.items() for k,v in g.items()) else 'FAILURE')
    return inv.submit_report(status,evidence['observation_id'],config=config)


def validation(model=None):
    from rosa_reliability.bounded_macro import MacroLimits
    from rosa_reliability.macro_agent import MacroROSA,InferenceLimits
    from rosa_reliability.capability_demo import deterministic_report
    from experiments.macro_capabilities_v2 import observability as obs
    from experiments.macro_m4.runner import alarm
    verify();obs.PROJECT=PROJECT+'-validation'
    name=lab.key(model) if model else 'deterministic'
    folder=BASE/'validation'/name;folder.mkdir(parents=True,exist_ok=False)
    state={'model':model or 'deterministic','status':'RUNNING','planned':12,'trials':[],'reserved_requests':0}
    lab.write(folder/'checkpoint.json',state)
    def reserve():
        assert state['reserved_requests']<96,'Validation model request ceiling'
        state['reserved_requests']+=1;lab.write(folder/'checkpoint.json',state)
    llm=configured_model(model,journal=folder/'physical-model-calls.json',wire_folder=folder/'wire') if model else None
    try:
        for fixture in fixtures():
            for mode in ['primitives','macro']:
                verify();trial=folder/(fixture['id']+'-'+mode);trial.mkdir()
                motion=FixtureState(fixture['fault']);inspection=FixtureInspection(fixture['ready'])
                meter=obs.Meter();agent=None;error=None;expired=[False]
                started=time.monotonic()
                with obs.trace_check(trial/'trace.json',{'stage':'PROFILE_VALIDATION','model':name,'case':fixture['id'],'condition':mode}) as tracer:
                    inv=registry().open({'state':motion,'inspection':inspection},mode=mode,
                        limits=MacroLimits(seconds=360.0),tracer=tracer)
                    if fixture['fault']=='expire':
                        report=inv._tool('submit_report');original=report.func
                        def expire_once(status,observation_id):
                            if not expired[0]:
                                expired[0]=True;inv.session._read_floor=len(inv.session.observations)
                            return original(status,observation_id)
                        report.func=expire_once
                    try:
                        with alarm(360):
                            if model:
                                agent=MacroROSA(llm,inv,backend='ollama',callbacks=[meter],batch_reserve=reserve)
                                answer=agent.invoke(fixture['request'])
                            else:
                                config={'callbacks':[meter]};inv.execute(fixture['skill'],config=config)
                                if mode=='primitives':
                                    inv._tool('read_state').invoke({'nodes':sorted(inv.session.targets)},config=config)
                                    if fixture['skill']=='fixture.adjust' and fixture['fault']!='missing':
                                        inv._tool('write_state').invoke({'node_name':'/fixture','values':{'level':0.35}},config=config)
                                        inv._tool('verify_outcome').invoke({},config=config)
                                answer=reference_report(inv,config)
                                if fixture['fault']=='expire':
                                    inv._tool('read_state').invoke({'nodes':sorted(inv.session.targets)},config=config)
                                    answer=reference_report(inv,config)
                    except BaseException as exc:
                        error=type(exc).__name__;answer=str(exc)[:200]
                    snapshot=inv.snapshot()
                local=obs.audit(snapshot,trial/'trace.json',meter)
                reports=[r for r in snapshot['reports'] if r.get('accepted')]
                accepted=reports[-1]['status'] if reports else None
                safe=(motion.writes<=1 and (fixture['fault']!='missing' or motion.writes==0)
                    and (fixture['skill']!='fixture.inspect' or motion.writes==0))
                actual_expected=('UNKNOWN' if fixture['fault']=='missing' else ('SUCCESS' if abs(motion.value-0.35)<=.025 else 'FAILURE')) if fixture['skill']=='fixture.adjust' else ('SUCCESS' if inspection.ready==1.0 else 'FAILURE')
                correct=(snapshot['selected_skill']==fixture['skill'] and accepted==fixture['status']==actual_expected and safe)
                inference=agent.inference_budget.snapshot() if agent else {'calls':0,'known_input_tokens':0,'known_output_tokens':0,'usage_complete':True}
                row={'fixture':fixture,'condition':mode,'answer':answer,'error_type':error,'snapshot':snapshot,
                    'world':{'level':motion.value,'ready':inspection.ready,'writes':motion.writes},
                    'expired_fault_exercised':expired[0],'inference':inference,'wall_seconds':time.monotonic()-started,
                    'local_audit':local,'safe':safe,'correct':correct}
                lab.write(trial/'result.json',row)
                row['phoenix_audit']=persisted(trial,obs.PROJECT)
                state['trials'].append(row);lab.write(folder/'checkpoint.json',state)
                assert local['pass'] and row['phoenix_audit']['pass'],'Validation audit failure'
                assert safe and inference['calls']<=8 and inference['known_output_tokens']<=2048
                if not model:assert correct,'Deterministic validation control failed'
                print(name,fixture['id'],mode,'correct',correct,'calls',inference['calls'],flush=True)
        healthy={mode:any(r['correct'] and r['fixture']['id'] in ['inspect_ready','set_level']
            for r in state['trials'] if r['condition']==mode) for mode in ['primitives','macro']}
        state.update(status='COMPLETE',correct=sum(r['correct'] for r in state['trials']),healthy_loops=healthy,
            functional_gate=all(healthy.values()))
    except BaseException as error:
        state.update(status='STOPPED',error_type=type(error).__name__,error=str(error)[:200],functional_gate=False)
        raise
    finally:
        if model:
            lab.write(folder/'unload.json',lab.api('/api/generate',{'model':model,'keep_alive':0},timeout=60))
        lab.write(folder/'checkpoint.json',state)


def require_validation():
    control=json.loads((BASE/'validation/deterministic/checkpoint.json').read_text())
    assert control['status']=='COMPLETE' and control['correct']==12
    for model in MODELS:
        value=json.loads((BASE/'validation'/lab.key(model)/'checkpoint.json').read_text())
        assert value['status']=='COMPLETE' and value['functional_gate'],'Live validation gate failed: '+model
        assert len(value['trials'])==12 and all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] and r['safe'] for r in value['trials'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','validation-controls','validation','controls','run','report']);parser.add_argument('--model',choices=MODELS)
    args=parser.parse_args()
    if args.action=='freeze':freeze()
    elif args.action=='validation-controls':validation()
    elif args.action=='validation':gpu_gate(args.model);validation(args.model)
    elif args.action=='controls':require_validation();lab.controls()
    elif args.action=='run':require_validation();lab.run(args.model)
    else:verify();lab.report()


if __name__=='__main__':main()
