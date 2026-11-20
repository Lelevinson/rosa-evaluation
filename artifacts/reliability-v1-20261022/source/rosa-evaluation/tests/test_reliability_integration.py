import tempfile
from pathlib import Path
import unittest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from rosa_backends import create_mock_agent
from rosa_reliability import ExecutionSession
from rosa_reliability.tools import make_tools
from experiments.reliability_v1.cases import CASES, MemoryTransport
from experiments.reliability_v1.runner import run_scripted
from experiments.reliability_v1.tracing import trace_trial, audit
from langchain_core.callbacks import BaseCallbackHandler


class ScriptedModel(BaseChatModel):
    messages: list
    index: int = 0
    @property
    def _llm_type(self):
        return 'scripted-engineering-control-not-inference'
    def bind_tools(self, tools, **kwargs):
        return self
    def _generate(self, messages, **kwargs):
        result = self.messages[self.index]
        self.index += 1
        return ChatResult(generations=[ChatGeneration(message=result)])


class Capture(BaseCallbackHandler):
    def __init__(self):
        self.tool_starts, self.tool_ends, self.tool_errors = [], [], []
    def on_tool_start(self, serialized, input_str, **kw):
        self.tool_starts.append(str(kw['run_id']))
    def on_tool_end(self, output, **kw):
        self.tool_ends.append(str(kw['run_id']))
    def on_tool_error(self, error, **kw):
        self.tool_errors.append(str(kw['run_id']))


def call(name, args, index):
    return AIMessage(content='', tool_calls=[{'name': name, 'args': args, 'id': str(index), 'type': 'tool_call'}])


class ReliabilityIntegrationTests(unittest.TestCase):
    def test_scripted_contract_controls_all_four_arms_and_cases(self):
        rows = run_scripted()
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r['pass'] for r in rows))

    def test_actual_rosa_validation_feedback_and_phoenix_span_export(self):
        spec = CASES[1]
        for automatic in (False, True):
            with self.subTest(automatic=automatic), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'trace.json'
                capture = Capture()
                with trace_trial({'run_id': 'scripted-control-' + str(automatic)}, path) as (tracer, span):
                    session = ExecutionSession(MemoryTransport(spec), spec['targets'], tracer=tracer,
                                               automatic_verification=automatic, structured_feedback=True)
                    tools = make_tools(session)
                    for tool in tools:
                        tool.callbacks = [capture]
                    model = ScriptedModel(messages=[
                        call('read_state', {'nodes': ['bench_east']}, 1),
                        call('read_state', {'nodes': ['/bench_east', '/bench_west']}, 2),
                        call('write_state', {'node_name': '/bench_east', 'values': {'position': 0.31}}, 3),
                        call('verify_outcome', {}, 4),
                        call('submit_report', {'status': 'SUCCESS', 'observed_values': {'position': 0.31}}, 5),
                        call('submit_report', {'status': 'SUCCESS', 'observed_values': spec['targets']}, 6),
                        AIMessage(content='Verified and reported.'),
                    ])
                    answer = create_mock_agent(model, tools, max_iterations=8).invoke('Execute the scripted engineering control.')
                    self.assertEqual(answer, 'Verified and reported.')
                result = audit(session.snapshot(), path, capture)
                self.assertTrue(result['pass'], result)
                self.assertEqual(session.validation_errors, 2)
                self.assertTrue(session.reports[-1]['accepted'])

    def test_actual_rosa_controlled_budget_stop_has_terminal_phoenix_tool_span(self):
        spec = CASES[0]
        capture = Capture()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.json'
            with trace_trial({'run_id': 'scripted-controlled-stop'}, path) as (tracer, span):
                session = ExecutionSession(MemoryTransport(spec), spec['targets'], operation_limit=1, tracer=tracer)
                tools = make_tools(session)
                for tool in tools:
                    tool.callbacks = [capture]
                model = ScriptedModel(messages=[call('read_state', {'nodes': ['/bench_east', '/bench_west']}, 1)])
                result = create_mock_agent(model, tools, max_iterations=2).invoke('Read both nodes.')
                self.assertIn('native_operation_budget_exhausted', result)
            checked = audit(session.snapshot(), path, capture)
            self.assertTrue(checked['pass'], checked)
            self.assertEqual(len(capture.tool_errors), 1)
            self.assertEqual(len(session.budget.events), 1)


if __name__ == '__main__':
    unittest.main()
