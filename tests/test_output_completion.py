"""Real ROSA execution tests with scripted providers; no live model tuning."""
from pathlib import Path
import tempfile
import unittest

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from rosa_reliability import ControlledStop
from rosa_reliability.completion import CompletionAwareROSA, CompletionGate
from rosa_reliability.evidence import EvidenceSession, make_evidence_tools
from experiments.reliability_v2.cases import VALIDATION, MockTransport
from experiments.output_budget_v1.design import CONDITIONS, jobs
from experiments.output_budget_v1.tracing import trace_trial, audit


def message(content='',tool=None,args=None,reason='stop',output=20):
    return AIMessage(content=content,
        tool_calls=[{'name':tool,'args':args,'id':'scripted','type':'tool_call'}] if tool else [],
        response_metadata={'done_reason':reason},
        usage_metadata={'input_tokens':100,'output_tokens':output,'total_tokens':100+output})


class Scripted(BaseChatModel):
    responses:list
    seen:list=[]
    index:int=0
    @property
    def _llm_type(self): return 'scripted-no-live-inference'
    def bind_tools(self,tools,**kwargs): return self
    def _generate(self,messages,**kwargs):
        self.seen.append({'messages':messages,'options':kwargs.get('options')})
        response=self.responses[self.index]
        self.index+=1
        return ChatResult(generations=[ChatGeneration(message=response)])


class Capture(BaseCallbackHandler):
    def __init__(self):
        self.tool_starts,self.tool_ends,self.tool_errors=[],[],[]
        self.model_calls=0
    def on_chat_model_start(self,serialized,messages,**kw): self.model_calls+=1
    def on_tool_start(self,serialized,input_str,**kw): self.tool_starts.append(str(kw['run_id']))
    def on_tool_end(self,output,**kw): self.tool_ends.append(str(kw['run_id']))
    def on_tool_error(self,error,**kw): self.tool_errors.append(str(kw['run_id']))


class CompletionTests(unittest.TestCase):
    def test_truncated_tool_calls_are_withheld_and_never_stitched(self):
        model=Scripted(responses=[message('incomplete',tool='write_state',args={'node_name':'/x','values':{'p':1}},reason='length',output=256),message('finished')])
        gate=CompletionGate(recover=True)
        returned=gate.invoke(model,[])
        self.assertEqual(returned.content,'finished')
        self.assertEqual(gate.recoveries,1)
        self.assertEqual(model.seen[1]['messages'][-2].tool_calls,[])
        self.assertEqual(model.seen[1]['messages'][-2].additional_kwargs,{})
        self.assertIn('No tool calls',model.seen[1]['messages'][-1].content)
        self.assertEqual(gate.output_tokens,276)

    def test_per_request_cap_is_reduced_to_remaining_shared_allowance(self):
        model=Scripted(responses=[message(reason='length',output=512),message(output=88)])
        gate=CompletionGate(per_call=512,total_tokens=600,recover=True)
        gate.invoke(model,[])
        self.assertEqual([r['options']['num_predict'] for r in model.seen],[512,88])
        with self.assertRaisesRegex(ControlledStop,'shared_inference_budget'):
            gate.invoke(model,[])
        self.assertEqual(model.index,2)

    def test_recovery_is_bounded_and_disabled_reference_is_unchanged(self):
        model=Scripted(responses=[message(reason='length',output=256)]*3)
        gate=CompletionGate(recover=True,recovery_limit=2)
        with self.assertRaisesRegex(ControlledStop,'recovery_limit'):
            gate.invoke(model,[])
        self.assertEqual(model.index,3)
        self.assertEqual(gate.recoveries,2)
        baseline=CompletionGate(recover=False)
        response=baseline.invoke(Scripted(responses=[message(reason='length',output=256)]),[])
        self.assertEqual(response.response_metadata['done_reason'],'length')

    def test_inference_call_and_time_limits_prevent_dispatch(self):
        model=Scripted(responses=[message()]*2)
        gate=CompletionGate(calls=1)
        gate.invoke(model,[])
        with self.assertRaisesRegex(ControlledStop,'shared_inference_budget'):
            gate.invoke(model,[])
        expired=CompletionGate()
        expired.started-=181
        with self.assertRaisesRegex(ControlledStop,'deadline'):
            expired.invoke(model,[])
        self.assertEqual(model.index,1)

    def test_real_rosa_post_write_truncation_does_not_replay_command_and_closes_spans(self):
        spec=VALIDATION[0]
        node=next(iter(spec['targets']))
        capture=Capture()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'trace.json'
            with trace_trial({'run_id':'offline-completion-recovery'},path,phoenix=False) as (tracer,root):
                session=EvidenceSession(MockTransport(spec),spec['targets'],write_limit=1,tracer=tracer)
                tools=make_evidence_tools(session)
                for tool in tools: tool.callbacks=[capture]
                model=Scripted(callbacks=[capture],responses=[
                    message(tool='read_state',args={'nodes':[node]}),
                    message(tool='write_state',args={'node_name':node,'values':spec['targets'][node]}),
                    message('partial',tool='write_state',args={'node_name':node,'values':spec['targets'][node]},reason='length',output=256),
                    message(tool='read_state',args={'nodes':[node]}),
                    message(tool='submit_report',args={'status':'SUCCESS','observed_values':spec['targets']}),
                    message('Done.')])
                gate=CompletionGate(recover=True,tracer=tracer)
                answer=CompletionAwareROSA(2,model,tools=tools,load_default_tools=False,
                    streaming=False,accumulate_chat_history=False,max_iterations=8,
                    completion_gate=gate).invoke('Run bounded scripted test.')
                self.assertEqual(answer,'Done.')
                self.assertEqual(session.write_count,1)
                self.assertTrue(session.reports[-1]['accepted'])
                self.assertEqual(gate.calls,6)
                self.assertEqual(capture.model_calls,6)
            self.assertTrue(audit(session.snapshot(),path,capture)['pass'])
            self.assertEqual(len([e for e in session.events if e['type']=='tool' and e['name']=='write_state']),1)

    def test_frozen_design_has_equal_case_repetition_coverage(self):
        schedule=jobs()
        self.assertEqual(len(schedule),40)
        self.assertEqual(set(CONDITIONS),{'L256','L512','L1024','C256','R256'})
        for label in CONDITIONS:
            selected=[row for row in schedule if row['condition']==label]
            self.assertEqual(len(selected),8)
            self.assertEqual(len({(row['repeat'],row['spec']['id']) for row in selected}),8)


if __name__=='__main__': unittest.main()
