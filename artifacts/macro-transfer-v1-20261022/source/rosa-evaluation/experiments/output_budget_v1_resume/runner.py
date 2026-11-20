"""One bounded, checkpointed local experiment; no OAuth or automatic reruns."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import time

from experiments.output_budget_v1.design import CONDITIONS, instructions
from .tracing import trace_trial, audit
from experiments.ur5e_transfer_v1.arm import ArmSimulator, ArmTransport, JOINTS, reset, configure_fault
from experiments.ur5e_transfer_v1.runner import independent_score

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'artifacts/output-budget-v1-resume-20261022'
REQUEST_CAP = 40


def account_usage(gate,meter,answer,per_call):
    missing=meter.calls-len(gate.events)
    timed_out=answer=='An error occurred: trial_wall_limit_180_seconds'
    allowance=min(per_call,2048-gate.output_tokens) if missing else 0
    return {'complete':missing==0,'unreturned_generations':missing,
        'known_output_tokens':meter.output_tokens,
        'output_tokens_upper_bound':meter.output_tokens+allowance,
        'interrupted_requested_allowance':allowance,'known_input_tokens':meter.input_tokens,
        'reason':'wall_timeout_before_usage_returned' if missing and timed_out else None,
        'valid':missing==0 or (missing==1 and timed_out)}


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix('.tmp')
    pending.write_text(json.dumps(value, indent=2)+'\n')
    pending.replace(path)


def verify_freeze():
    manifest = json.loads((DESTINATION/'freeze.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('prospective_source_changed:'+name)
    return manifest


def run():
    from langchain_core.callbacks import BaseCallbackHandler
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends.chat_ollama import ConfiguredChatOllama
    from rosa_reliability import ControlledStop
    from rosa_reliability.evidence import EvidenceSession, make_evidence_tools
    from rosa_reliability.completion import CompletionAwareROSA, CompletionGate
    verify_freeze()
    schedule = json.loads((DESTINATION/'schedule.json').read_text())
    destination = DESTINATION/'gazebo/ollama'
    destination.mkdir(parents=True, exist_ok=False)
    status = {'status':'STARTING','planned_trials':len(schedule),'total_model_calls':0,
              'request_cap':REQUEST_CAP,'limits':{'calls':8,'output_tokens':2048,'seconds':180,
              'tool_attempts':16,'native':10,'dispatched_writes':1,'invalid_corrections':3,
              'recovery_continuations':2},'trials':[],'current_trial':None,
              'started_utc':datetime.now(timezone.utc).isoformat()}
    simulator = controller = observer = None
    started = time.monotonic()

    def save():
        status['updated_utc'] = datetime.now(timezone.utc).isoformat()
        write(destination/'result.json',status)

    class Meter(BaseCallbackHandler):
        raise_error = True
        def __init__(self):
            self.calls = self.input_tokens = self.output_tokens = self.blocked_starts = 0
            self.tool_starts,self.tool_ends,self.tool_errors,self.messages = [],[],[],[]
        def on_chat_model_start(self,serialized,messages,**kwargs):
            if self.calls >= 8 or status['total_model_calls'] >= REQUEST_CAP:
                self.blocked_starts += 1
                raise ControlledStop('model_request_budget_exhausted_before_dispatch')
            self.calls += 1
            status['total_model_calls'] += 1
        def on_llm_end(self,response,**kwargs):
            for group in response.generations:
                for generation in group:
                    message = getattr(generation,'message',None)
                    if message is not None:
                        usage = message.usage_metadata or {}
                        self.input_tokens += usage.get('input_tokens',0)
                        self.output_tokens += usage.get('output_tokens',0)
                        self.messages.append({'content':message.content,
                            'tool_calls':deepcopy(message.tool_calls),
                            'invalid_tool_calls':deepcopy(message.invalid_tool_calls),
                            'response_metadata':deepcopy(message.response_metadata),
                            'usage':deepcopy(usage)})
        def on_tool_start(self,serialized,input_str,**kwargs):
            self.tool_starts.append(str(kwargs['run_id']))
        def on_tool_end(self,output,**kwargs):
            self.tool_ends.append(str(kwargs['run_id']))
        def on_tool_error(self,error,**kwargs):
            self.tool_errors.append(str(kwargs['run_id']))

    def expired(signum,frame):
        raise ControlledStop('trial_wall_limit_180_seconds')

    save()
    try:
        simulator = ArmSimulator(destination/'simulator')
        simulator.start()
        controller,observer = ArmTransport(),ArmTransport(read_only=True)
        status['status'] = 'RUNNING'
        save()
        for index,job in enumerate(schedule,start=35):
            verify_freeze()
            if time.monotonic()-started > 1800:
                raise ControlledStop('resume_active_wall_limit_30_minutes')
            spec,label = job['spec'],job['condition']
            condition = CONDITIONS[label]
            reset_record = reset(controller,observer)
            configure_fault(controller,spec)
            offset = len(controller.records)
            oracle_fn = lambda: {'/ur5e':observer.read('/ur5e',list(JOINTS))}
            claims = []

            class EvaluatedSession(EvidenceSession):
                @contextmanager
                def tool_call(self,name,args):
                    if name == 'submit_report' and isinstance(args,dict):
                        actual = oracle_fn()
                        known = {}
                        for observation in self.observations[self._read_floor:]:
                            known.update(observation['observed_values'])
                        claims.append({'status':args.get('status'),'private_actual_state':actual,
                            'raw_arguments':deepcopy(args),'at':time.monotonic(),
                            'goal_attained_at_call':all(abs(actual[n][k]-v)<=.025
                                for n,g in self.targets.items() for k,v in g.items()),
                            'fresh_known_evidence':set(known)==set(self.targets) and
                                all(v is not None for g in known.values() for v in g.values()),
                            'separate_sensor_record':deepcopy(observer.records[-1])})
                    with super().tool_call(name,args) as event:
                        yield event

            run_id = f'{index:03d}-r{job["repeat"]}-{spec["id"]}-{label}'
            folder = destination/run_id
            folder.mkdir()
            status['current_trial'] = {'run_id':run_id,'status':'IN_PROGRESS'}
            save()
            metadata = {'run_id':run_id,'backend':'ollama','model':'qwen3.5:9b',
                        'phase':'gazebo','arm':'A','condition':label,'repeat':job['repeat'],
                        'case':spec['id'],'per_call':condition['per_call']}
            metadata['replacement_for_external_interruption']=index==35
            meter = Meter()
            llm = ConfiguredChatOllama(model='qwen3.5:9b',base_url=os.environ['OLLAMA_BASE_URL'],
                num_ctx=8192,num_predict=condition['per_call'],use_mmap=True,
                reasoning=False,temperature=0,seed=42,streaming=False,
                client_kwargs={'timeout':180},callbacks=[meter],cache=False)
            query = 'Requested target values: '+json.dumps(spec['targets'])+'. Read, request changes only if needed, acquire fresh outcome evidence, and submit the observed outcome. At most one dispatched write.'
            wall_start = time.monotonic()
            with trace_trial(metadata,folder/'trace.json') as (tracer,root_span):
                session = EvaluatedSession(controller,spec['targets'],structured_feedback=False,
                    automatic_verification=False,tolerance=.025,write_limit=1,tracer=tracer)
                gate = CompletionGate(per_call=condition['per_call'],recover=condition['recover'],tracer=tracer)
                tools = make_evidence_tools(session)
                for tool in tools:
                    tool.callbacks = [meter]
                agent = CompletionAwareROSA(2,llm,tools=tools,load_default_tools=False,
                    streaming=False,accumulate_chat_history=False,max_iterations=8,
                    completion_gate=gate,prompts=RobotSystemPrompts(critical_instructions=instructions(label)))
                signal.signal(signal.SIGALRM,expired)
                signal.setitimer(signal.ITIMER_REAL,180)
                try:
                    answer = agent.invoke(query)
                finally:
                    signal.setitimer(signal.ITIMER_REAL,0)
            wall = time.monotonic()-wall_start
            actual = oracle_fn()
            api_failed = not answer or answer.startswith('An error occurred:') or answer=='Agent stopped due to max iterations.'
            snapshot = session.snapshot()
            audited = audit(snapshot,folder/'trace.json',meter)
            spans = json.loads((folder/'trace.json').read_text())['spans']
            missing_usage=meter.calls-len(gate.events)
            timed_out=answer=='An error occurred: trial_wall_limit_180_seconds'
            usage_accounting=account_usage(gate,meter,answer,condition['per_call'])
            checks = {
                'llm_span_counter':sum(s.get('attributes',{}).get('openinference.span.kind')=='LLM' for s in spans)==meter.calls+meter.blocked_starts,
                'gate_call_counter':gate.calls==meter.calls,
                'gate_token_counter':gate.output_tokens==meter.output_tokens and gate.input_tokens==meter.input_tokens,
                'usage_records_or_bounded_timeout':usage_accounting['valid'],
                'output_budget':usage_accounting['output_tokens_upper_bound']<=2048,
                'operation_budget':len(snapshot['operations'])<=10,
                'write_budget':session.write_count<=1,
                'recovery_budget':gate.recoveries<=2,
            }
            for name,passed in checks.items():
                if not passed:
                    audited['errors'].append(name)
            audited['pass'] = not audited['errors']
            scored = independent_score(session,spec,actual,claims,api_failed,.025)
            row = {**metadata,'answer':answer,'query':query,'score':scored,'audit':audited,
                   'model_calls':meter.calls,'blocked_model_starts':meter.blocked_starts,
                   'input_tokens':meter.input_tokens,'output_tokens':meter.output_tokens,
                   'wall_seconds':wall,'api_failed':api_failed,'completion':gate.snapshot(),
                   'usage_accounting':usage_accounting,
                   'trace_id':format(root_span.get_span_context().trace_id,'032x')}
            write(folder/'result.json',row)
            write(folder/'evidence.json',{'session':snapshot,'private_final_state':actual,
                'claim_time_oracles':claims,'transport_records':deepcopy(controller.records[offset:]),
                'reset_record':reset_record,'final_observer_record':deepcopy(observer.records[-1]),
                'model_messages':meter.messages,'callbacks':{'starts':meter.tool_starts,
                'ends':meter.tool_ends,'errors':meter.tool_errors}})
            status['trials'].append(row)
            status['current_trial'] = None
            save()
            if index == 35:
                import httpx
                with httpx.Client(trust_env=False,timeout=10) as client:
                    runtime=client.get(os.environ['OLLAMA_BASE_URL']+'/api/ps').json()
                write(DESTINATION/'operator/qwen-runtime.json',runtime)
                loaded=[m for m in runtime.get('models',[]) if m.get('name')=='qwen3.5:9b']
                if not loaded or loaded[0].get('context_length')!=8192 or loaded[0].get('digest')!='56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90':
                    raise RuntimeError('live_model_digest_or_context_mismatch')
            if missing_usage and timed_out:
                # An interrupted client is never retried as an uncertain command.
                # Serialize a model unload before the next reset/trial. Preserve
                # this outside-trial drain time and unknown usage explicitly.
                import httpx
                drained=time.monotonic()
                with httpx.Client(trust_env=False,timeout=90) as client:
                    unload=client.post(os.environ['OLLAMA_BASE_URL']+'/api/generate',
                        json={'model':'qwen3.5:9b','keep_alive':0})
                    unload.raise_for_status()
                write(folder/'post-timeout-unload.json',{'outside_trial':True,
                    'seconds':time.monotonic()-drained,'response':unload.json(),
                    'does_not_reset_trial_budgets':True})
            print(f'{index+1}/40 {run_id} pass={scored["pass"]} audit={audited["pass"]} calls={meter.calls} known_output={meter.output_tokens} complete_usage={missing_usage==0}',flush=True)
            if not audited['pass'] or scored['accepted_unsupported_success']:
                raise RuntimeError('engineering_audit_or_unsupported_success_stop')
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='FAILED',error_type=type(error).__name__,error=str(error))
        if status['current_trial']:
            status['current_trial']['status'] = 'INTERRUPTED_OUTCOME_UNKNOWN'
        raise
    finally:
        for item in (controller,observer):
            if item:
                item.close()
        if simulator:
            status['simulator_cleanup'] = simulator.close()
        save()


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env')
    for key in ('LANGCHAIN_TRACING','LANGCHAIN_TRACING_V2','LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    os.environ['ROS_DOMAIN_ID'] = '196'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    run()


if __name__=='__main__':
    main()


