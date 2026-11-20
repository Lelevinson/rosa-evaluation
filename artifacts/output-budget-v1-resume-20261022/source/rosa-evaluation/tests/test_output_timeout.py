from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from rosa_reliability import ControlledStop
from rosa_reliability.completion import CompletionAwareROSA,CompletionGate
from rosa_reliability.evidence import EvidenceSession,make_evidence_tools
from experiments.reliability_v2.cases import VALIDATION,MockTransport
from experiments.output_budget_v1_followup.runner import account_usage
from experiments.output_budget_v1.tracing import trace_trial,audit


class Interrupting(BaseChatModel):
    @property
    def _llm_type(self):return 'offline-scripted-wall-interruption'
    def bind_tools(self,tools,**kwargs):return self
    def _generate(self,messages,**kwargs):
        raise ControlledStop('trial_wall_limit_180_seconds')


class Capture(BaseCallbackHandler):
    def __init__(self):
        self.calls=self.output_tokens=self.input_tokens=0
        self.tool_starts,self.tool_ends,self.tool_errors=[],[],[]
    def on_chat_model_start(self,*args,**kwargs):self.calls+=1


class TimeoutTests(unittest.TestCase):
    def test_actual_rosa_interruption_is_closed_and_usage_is_unknown_with_finite_bound(self):
        capture=Capture()
        gate=CompletionGate(per_call=1024)
        spec=VALIDATION[0]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'trace.json'
            with trace_trial({'run_id':'offline-interrupted-generation'},path,phoenix=False) as (tracer,root):
                session=EvidenceSession(MockTransport(spec),spec['targets'],tracer=tracer)
                agent=CompletionAwareROSA(2,Interrupting(callbacks=[capture]),
                    tools=make_evidence_tools(session),load_default_tools=False,
                    streaming=False,completion_gate=gate)
                answer=agent.invoke('Bounded interruption test.')
            self.assertTrue(audit(session.snapshot(),path,capture)['pass'])
            record=account_usage(gate,capture,answer,1024)
            self.assertTrue(record['valid'])
            self.assertFalse(record['complete'])
            self.assertEqual(record['known_output_tokens'],0)
            self.assertEqual(record['output_tokens_upper_bound'],1024)
            self.assertEqual(record['unreturned_generations'],1)
            self.assertEqual(session.write_count,0)

    def test_only_explicit_wall_interruption_gets_partial_usage_classification(self):
        gate=SimpleNamespace(events=[{}],output_tokens=1900)
        meter=SimpleNamespace(calls=2,output_tokens=1900,input_tokens=4000)
        record=account_usage(gate,meter,'An error occurred: trial_wall_limit_180_seconds',1024)
        self.assertEqual(record['output_tokens_upper_bound'],2048)
        self.assertTrue(record['valid'])
        self.assertFalse(account_usage(gate,meter,'An error occurred: network_down',1024)['valid'])


if __name__=='__main__':unittest.main()
