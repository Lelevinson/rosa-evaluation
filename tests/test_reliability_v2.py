import tempfile
from pathlib import Path
import unittest
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from rosa_backends import create_mock_agent
from rosa_reliability.evidence import EvidenceSession, make_evidence_tools
from experiments.reliability_v2.cases import VALIDATION, MockTransport
from experiments.reliability_v2.prepare import controls
from experiments.reliability_v2.runner import independent_score
from experiments.reliability_v2.tracing import trace_trial, audit


class Scripted(BaseChatModel):
    messages:list
    index:int=0
    @property
    def _llm_type(self):
        return 'scripted-control-not-live-inference'
    def bind_tools(self,tools,**kwargs):
        return self
    def _generate(self,messages,**kwargs):
        result=self.messages[self.index]
        self.index+=1
        return ChatResult(generations=[ChatGeneration(message=result)])


class Capture(BaseCallbackHandler):
    def __init__(self):
        self.tool_starts,self.tool_ends,self.tool_errors=[],[],[]
    def on_tool_start(self,serialized,input_str,**kw):
        self.tool_starts.append(str(kw['run_id']))
    def on_tool_end(self,output,**kw):
        self.tool_ends.append(str(kw['run_id']))
    def on_tool_error(self,error,**kw):
        self.tool_errors.append(str(kw['run_id']))


def call(name,args,index):
    return AIMessage(content='',tool_calls=[{'name':name,'args':args,'id':str(index),'type':'tool_call'}])


class StudyTests(unittest.TestCase):
    def test_all_40_fixed_case_arm_controls_and_equal_schemas(self):
        rows=controls()
        self.assertEqual(len(rows),40)
        self.assertTrue(all(r['pass'] for r in rows))
        self.assertTrue(all(len(r['snapshot']['operations'])<=10 for r in rows))

    def test_actual_rosa_recovery_reuses_read_and_closes_error_spans(self):
        spec=VALIDATION[0]
        for auto in (False,True):
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'trace.json'
                capture=Capture()
                with trace_trial({'run_id':'offline-recovery'},path,phoenix=False) as (tracer,span):
                    session=EvidenceSession(MockTransport(spec),spec['targets'],automatic_verification=auto,tracer=tracer)
                    tools=make_evidence_tools(session)
                    for tool in tools:
                        tool.callbacks=[capture]
                    model=Scripted(messages=[
                        call('read_state',{'nodes':['fixture_violet']},1),
                        call('read_state',{'nodes':['/fixture_violet']},2),
                        call('write_state',{'node_name':'/fixture_violet','values':spec['targets']['/fixture_violet']},3),
                        call('read_state',{'nodes':['/fixture_violet']},4),
                        call('submit_report',{'status':'SUCCESS','observed_values':spec['targets']},5),
                        AIMessage(content='Verified and reported.')])
                    result=create_mock_agent(model,tools,max_iterations=8).invoke('Run the scripted control.')
                    self.assertEqual(result,'Verified and reported.')
                self.assertTrue(audit(session.snapshot(),path,capture)['pass'])
                self.assertEqual(session.validation_errors,1)
                self.assertTrue(session.reports[-1]['accepted'])

    def test_operation_limit_has_terminal_real_error_span(self):
        spec=VALIDATION[1]
        capture=Capture()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'trace.json'
            with trace_trial({'run_id':'offline-budget-stop'},path,phoenix=False) as (tracer,span):
                session=EvidenceSession(MockTransport(spec),spec['targets'],operation_limit=1,tracer=tracer)
                tools=make_evidence_tools(session)
                for tool in tools:
                    tool.callbacks=[capture]
                model=Scripted(messages=[call('read_state',{'nodes':list(spec['targets'])},1)])
                result=create_mock_agent(model,tools,max_iterations=2).invoke('Run the budget control.')
                self.assertIn('native_operation_budget_exhausted',result)
            self.assertTrue(audit(session.snapshot(),path,capture)['pass'])
            self.assertEqual(len(session.budget.events),1)
            self.assertEqual(len(capture.tool_errors),1)

    def test_false_earlier_claim_remains_false_after_final_goal_attainment(self):
        spec=VALIDATION[0]
        transport=MockTransport(spec)
        session=EvidenceSession(transport,spec['targets'])
        session.read(list(spec['targets']))
        session.write('/fixture_violet',spec['targets']['/fixture_violet'])
        actual=session.read(list(spec['targets']))
        session.report('SUCCESS',actual['observed_values'])
        claims=[{'status':'SUCCESS','goal_attained_at_call':False,'fresh_known_evidence':False}]
        result=independent_score(session,spec,transport.values,claims,False,.015)
        self.assertTrue(result['pass'])
        self.assertEqual(result['raw_false_success_claims'],1)
        self.assertEqual(result['raw_unsupported_success_claims'],1)


if __name__=='__main__':
    unittest.main()
