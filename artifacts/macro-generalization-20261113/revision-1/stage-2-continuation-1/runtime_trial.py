"""Authorized Sol dev, public adapters and fresh mock worlds. No task replay."""
from copy import deepcopy
from datetime import datetime,timezone
import json
import signal
import subprocess
import sys
import time
from common import ROOT,REV,REPO,read,write,verify
sys.path.insert(0,str(REV))
from worlds import create_world
from catalogue import registry
from scoring import score,ObserverEvidenceRequired
from tracing import Meter,trace_check,audit
from recovery import Campaign,LoggedGate,RecoverableSiwc
from authorization import restore_only,check_models,MODEL
from rosa_auth.oauth import SafeError
from rosa_backends.chat_siwc import ChatSiwc
from rosa_reliability.macro_agent import MacroROSA,InferenceLimits
from rosa_reliability.bounded_macro import MacroLimits
from rosa_reliability.execution import ControlledStop
from rosa_reliability.prompt_contract import bounded_contract,REQUIRED_TOOLS

PHOENIX='/home/martin/.local/share/rosa-envs/phoenix/bin/python'

def trial(item,model,transport,campaign):
    folder=ROOT/'trials'/item['id'];folder.mkdir(parents=True)
    case=item['case'];started=time.monotonic()
    world,actor,observer=create_world(case['domain'],**case['world_configuration'])
    record_start=len(model.request_records)
    row={'id':item['id'],'mode':item['mode'],'case':case,'backend':'siwc','model':MODEL,
         'expected_scripted_turns':item['expected_turns'],'expected_scripted_native':item['expected_native'],
         'primary_pass':False,'error':None,'decision_actor':'live_model'}
    timeout={'fired':False}
    inv=gate=meter=None
    def expired(signum,frame):
        timeout['fired']=True
        raise TimeoutError('g1_dev_external_task_deadline')
    try:
        with trace_check(folder/'trace.json',{'id':item['id'],'backend':'siwc','decision_actor':'live_model'}) as tracer:
            meter=Meter(observer,tracer);meter.observe('before_agent')
            inv=registry(case['domain']).open({'state':actor,'inspection':actor},mode=item['mode'],
                tracer=tracer,limits=MacroLimits(seconds=360.0))
            agent=MacroROSA(model,inv,backend='siwc',callbacks=[meter])
            gate=LoggedGate(inv,backend='siwc',limits=InferenceLimits(),campaign=campaign,
                release=transport.release_transient_failure,
                journal=lambda value:(folder/'inference-progress.json').write_text(json.dumps(
                    {'inference':value,'snapshot':inv.snapshot()},indent=2)+'\n'))
            agent.inference_budget=agent.completion_gate=gate
            contract=read(REV/'prompt-contract.json')
            assert bounded_contract(REQUIRED_TOOLS)==contract['system']
            query=(contract['rules'].removesuffix('\nUser: ')+f' Execution condition: {item["mode"]}. '+
                contract['condition_sentences'][item['mode']]+contract[case['domain']+'_suffix']+case['request'])
            row['query']=query
            remaining=campaign.remaining_seconds()
            if remaining<=0:raise ControlledStop('g1_dev_backend_deadline')
            signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,min(360,remaining))
            try:answer=agent.invoke(query)
            except Exception as error:
                row['error']={'type':type(error).__name__}
                if isinstance(error,(SafeError,ControlledStop)):
                    row['error']['code']=error.code if isinstance(error,SafeError) else str(error)
                answer='Task interrupted: '+type(error).__name__
            finally:signal.setitimer(signal.ITIMER_REAL,0)
            meter.observe('after_agent');snapshot=inv.snapshot();inference=gate.snapshot()
        task_seconds=time.monotonic()-started
        row.update(answer=answer,snapshot=snapshot,inference=inference,actor_records=deepcopy(actor.records),
                   observer_records=deepcopy(observer.records),task_seconds=task_seconds)
        scored=score(case,snapshot,answer,observer.records)
        refused=False
        try:score(case,snapshot,answer,actor.records)
        except ObserverEvidenceRequired:refused=True
        local=audit(snapshot,folder/'trace.json',meter,inference,actor.records)
        failure=gate.terminal_failure
        if failure and row['error'] is None:row['error']=failure
        codes=meter.execution_errors+([failure.get('code','')] if failure else [])
        scored['budget_exhaustion']=bool(timeout['fired'] or any('budget' in c or 'deadline' in c or
            'threshold_exceeded' in c for c in codes) or
            (inference['decision_calls']>=8 and not any(r.get('accepted') for r in snapshot['reports'])))
        scored['length_stop']=any(e.get('finish_reason')=='length' for e in inference['events'])
        recovered=inference['infrastructure_failures']>0
        row.update(answer=answer,snapshot=snapshot,inference=inference,score=scored,local_audit=local,
            task_seconds=task_seconds,timeout_fired=timeout['fired'],execution_error_codes=codes,
            actual_turns=inference['calls'],actual_decision_turns=inference['decision_calls'],
            turns_match_scripted_expectation=inference['calls']==item['expected_turns'],
            native_match_scripted_expectation=len(actor.records)==item['expected_native'],
            actor_records=deepcopy(actor.records),observer_records=deepcopy(observer.records),
            observer_tags=meter.observer_tags,tool_inputs=meter.tool_inputs,model_inputs=meter.model_inputs,
            model_outputs=meter.model_outputs,model_errors=meter.model_errors,
            sanitized_request_records=model.request_records[record_start:],actor_only_truth_rejected=refused,
            infrastructure_recovered=recovered,
            primary_pass=bool(scored['primary_pass'] and local['pass'] and refused and not recovered and not row['error'] and not timeout['fired']),
            completion_including_recovery=bool(scored['primary_pass'] and local['pass'] and refused and not row['error'] and not timeout['fired']))
        (folder/'result.json').write_text(json.dumps(row,indent=2)+'\n')
        # Persist each result before its server-side trace check; never erase it on failure.
        with (folder/'phoenix-audit.log').open('w') as log:
            result=subprocess.run([PHOENIX,'-B',str(ROOT/'persisted_audit.py'),str(folder)],
                cwd=REPO,stdout=log,stderr=log,timeout=60)
        if (folder/'phoenix-audit.json').exists():row['phoenix_audit']=read(folder/'phoenix-audit.json')
        if result.returncode:raise RuntimeError('persisted_trace_audit_failed')
        if not local['pass'] or not refused:raise RuntimeError('local_trace_or_observer_audit_failed')
        return row
    except BaseException as error:
        row['harness_error_type']=type(error).__name__
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        row.setdefault('actor_records',deepcopy(actor.records))
        row.setdefault('observer_records',deepcopy(observer.records))
        if inv is not None:row.setdefault('snapshot',inv.snapshot())
        if gate is not None:row.setdefault('inference',gate.snapshot())
        row['trial_total_seconds']=time.monotonic()-started
        (folder/'result.json').write_text(json.dumps(row,indent=2)+'\n')
