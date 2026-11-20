"""Scripted fixtures exercise real public adapters; no model server is called."""
from copy import deepcopy
import io
import json
from pathlib import Path
import signal
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parent
REV=ROOT.parents[1]
REPO=ROOT.parents[4]
sys.path[:0]=[str(REV),str(REPO)]
from prepare import read,write,digest,WORKSPACE
from worlds import create_world
from catalogue import registry
from scoring import score,ObserverEvidenceRequired
from tracing import Meter,trace_check,audit
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration,ChatResult
from rosa_reliability.macro_agent import MacroROSA
from rosa_reliability.bounded_macro import MacroLimits
from rosa_reliability.prompt_contract import bounded_contract,REQUIRED_TOOLS


class ScriptedCaller(BaseChatModel):
    invocation:object
    case:dict
    index:int=0
    @property
    def _llm_type(self):return 'g1-scripted-no-live-model'
    def bind_tools(self,tools,**kwargs):return self
    def _generate(self,messages,**kwargs):
        index,self.index=self.index,self.index+1
        if self.case['kind']=='ambiguous':
            assert index==0
            message=AIMessage(content='Should I inspect readiness or move to a registered target?',
                usage_metadata={'input_tokens':10,'output_tokens':5,'total_tokens':15},
                response_metadata={'finish_reason':'stop'})
            return ChatResult(generations=[ChatGeneration(message=message)])
        definition=self.invocation.catalogue[self.case['skill_id']]
        inspection=definition['kind']=='read_only_inspection'
        steps=[('select_skill',{'skill_id':self.case['skill_id']})]
        if self.invocation.mode=='primitives':
            nodes=[definition['subject']] if inspection else list(definition['targets'])
            steps.append(('read_state',{'nodes':nodes}))
            if not inspection and self.case['fault']!='missing_pose':
                node=nodes[0]
                steps.extend([('write_state',{'node_name':node,'values':definition['targets'][node]}),
                              ('verify_outcome',{})])
        if index<len(steps):name,args=steps[index]
        else:
            assert index==len(steps),'unexpected_extra_scripted_turn'
            observation=self.invocation.snapshot()['observations'][-1]
            values=observation['observed_values']
            flat=[v for fields in values.values() for v in fields.values()]
            reached=(all(v==1.0 for v in flat) if inspection else all(
                values[n][k] is not None and abs(values[n][k]-v)<=.025
                for n,fields in definition['targets'].items() for k,v in fields.items()))
            status='UNKNOWN' if any(v is None for v in flat) else 'SUCCESS' if reached else 'FAILURE'
            name,args='submit_report',{'status':status,'observation_id':observation['observation_id']}
        message=AIMessage(content='',tool_calls=[{'name':name,'args':args,'id':f'scripted-{index}','type':'tool_call'}],
            usage_metadata={'input_tokens':10,'output_tokens':5,'total_tokens':15},
            response_metadata={'finish_reason':'stop'})
        return ChatResult(generations=[ChatGeneration(message=message)])


def verify():
    freeze=read(ROOT/'control-input-freeze.json')
    changed=[name for name,value in freeze['files'].items() if digest(ROOT/name)!=value]
    protected=read(ROOT/'protected-before.json')
    changed.extend(name for name,value in protected.items() if digest(WORKSPACE/name)!=value)
    if changed:raise RuntimeError('protected_or_frozen_file_mismatch:'+repr(changed))
    return {'pass':True,'frozen_files':len(freeze['files']),'protected_files':len(protected),'mismatches':[]}


def unit_checks():
    import observer_separation_test,world_semantics_test
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module)
                             for module in (observer_separation_test,world_semantics_test))
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (ROOT/'unit-tests.log').write_text(stream.getvalue())
    write('unit-tests.json',{'pass':result.wasSuccessful(),'tests':result.testsRun,
        'errors':len(result.errors),'failures':len(result.failures),'live_model_requests':0})
    if not result.wasSuccessful():raise RuntimeError('observer_or_world_unit_failure')


def trial(item):
    folder=ROOT/'trials'/item['id'];folder.mkdir(parents=True)
    case=item['case'];start=time.monotonic()
    world,actor,observer=create_world(case['domain'],**case['world_configuration'])
    output={'id':item['id'],'block':item['block'],'mode':item['mode'],'case':case,
            'decision_actor':'scripted_fixture_oracle','token_usage_kind':'synthetic_fixture_metadata',
            'live_model_requests':0,'pass':False}
    try:
        with trace_check(folder/'trace.json',{'id':item['id'],'decision_actor':'scripted_fixture_oracle'}) as tracer:
            meter=Meter(observer,tracer);meter.observe('before_agent')
            invocation=registry(case['domain']).open({'state':actor,'inspection':actor},
                mode=item['mode'],tracer=tracer,limits=MacroLimits(seconds=360.0))
            model=ScriptedCaller(invocation=invocation,case=case,cache=False)
            agent=MacroROSA(model,invocation,backend='scripted',callbacks=[meter])
            contract=read(REV/'prompt-contract.json')
            assert bounded_contract(REQUIRED_TOOLS)==contract['system']
            query=(contract['rules'].removesuffix('\nUser: ')+f' Execution condition: {item["mode"]}. '+
                contract['condition_sentences'][item['mode']]+contract[case['domain']+'_suffix']+case['request'])
            output['query']=query
            answer=agent.invoke(query)
            meter.observe('after_agent')
            snapshot=invocation.snapshot();accounting=agent.inference_budget.snapshot()
        scored=score(case,snapshot,answer,observer.records)
        refused=False
        try:score(case,snapshot,answer,actor.records)
        except ObserverEvidenceRequired:refused=True
        local=audit(snapshot,folder/'trace.json',meter,accounting,actor.records)
        counterfactuals={}
        if case['kind']!='ambiguous':
            stale=deepcopy(snapshot)
            stale['reports'][-1]['observation_id']='nonexistent-observation'
            counterfactuals['stale_reference_rejected']=not score(case,stale,answer,observer.records)['primary_pass']
            wrong=deepcopy(snapshot)
            fields=next(iter(wrong['reports'][-1]['observed_values'].values()))
            field=next(iter(fields));fields[field]=99.0
            counterfactuals['invented_value_rejected']=not score(case,wrong,answer,observer.records)['primary_pass']
            if case['expected_status']=='UNKNOWN':
                unsupported=deepcopy(snapshot);unsupported['reports'][-1]['status']='SUCCESS'
                counterfactuals['unknown_not_success']=not score(case,unsupported,answer,observer.records)['primary_pass']
        count_ok=accounting['calls']==item['expected_turns'] and len(snapshot['operations'])==item['expected_native']
        output.update(answer=answer,snapshot=snapshot,accounting=accounting,score=scored,local_audit=local,
            actor_only_ground_truth_rejected=refused,expected_counts_match=count_ok,scorer_negative_controls=counterfactuals,
            actor_records=deepcopy(actor.records),observer_records=deepcopy(observer.records),
            observer_tags=meter.observer_tags,model_outputs=meter.model_outputs,tool_inputs=meter.tool_inputs,
            pass_=scored['primary_pass'] and local['pass'] and refused and count_ok and all(counterfactuals.values()))
        output['pass']=output.pop('pass_')
    except BaseException as error:
        output.update(error_type=type(error).__name__,error=str(error),
                      actor_records=deepcopy(actor.records),observer_records=deepcopy(observer.records))
        raise
    finally:
        output['elapsed_seconds']=time.monotonic()-start
        (folder/'result.json').write_text(json.dumps(output,indent=2)+'\n')
    return output


def main():
    assert not (ROOT/'RUN_ONCE').exists(),'Frozen attempt already started; do not replace it.'
    verify();(ROOT/'RUN_ONCE').write_text('No automatic replacement or command replay.\n')
    rows=[];state={'status':'RUNNING','completed':0,'planned':132,'live_model_requests':0,'Stage2_started':False}
    def timeout(signum,frame):raise TimeoutError('stage1_external_deadline')
    signal.signal(signal.SIGALRM,timeout)
    try:
        unit_checks()
        for item in read(ROOT/'control-plan.json'):
            signal.setitimer(signal.ITIMER_REAL,360)
            row=trial(item);rows.append(row)
            signal.setitimer(signal.ITIMER_REAL,0)
            state.update(completed=len(rows),last_trial=item['id']);write('status.json',state)
            print(f'{len(rows)}/132 {item["id"]} pass={row["pass"]}',flush=True)
            if not row['pass']:raise RuntimeError('mandatory_control_failed:'+item['id'])
            if len(rows)==20:
                write('structural-gate.json',{'pass':True,'trials':20,'actual_counts_match':True})
        state.update(status='LOCAL_CONTROLS_COMPLETE_PERSISTED_AUDIT_PENDING',protected_check=verify())
    except BaseException as error:
        state.update(status='STOPPED',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        write('status.json',state)
        write('local-summary.json',{'pass':len(rows)==132 and all(r['pass'] for r in rows),
            'completed':len(rows),'live_model_requests':0,'rows':[{'id':r['id'],'pass':r['pass']} for r in rows]})


if __name__=='__main__':main()
