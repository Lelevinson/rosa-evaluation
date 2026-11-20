import json
import unittest
from langchain_core.messages import AIMessage
from rosa_reliability import ControlledStop
from rosa_reliability.workflow import WorkflowSession, make_workflow_tools
from experiments.workflow_v1.pilot import Scripted, call
from experiments.workflow_live_v1.design import CASES, SKILLS, LIMITS, PilotTransport, jobs
from experiments.workflow_live_v1.inference import InferenceGate, LiveROSA
from experiments.workflow_live_v1.runner import score


def used(message, output=10):
    return message.model_copy(update={'usage_metadata': {'input_tokens': 100,
        'output_tokens': output, 'total_tokens': 100 + output}})


class InferenceTests(unittest.TestCase):
    def test_local_remaining_allowance_is_enforced(self):
        class Model:
            def __init__(self): self.allowances = []
            def invoke(self, prompt, **kwargs):
                allowance = kwargs['options']['num_predict']
                self.allowances.append(allowance)
                return used(AIMessage(content='text'), allowance)
        model = Model()
        gate = InferenceGate('ollama', lambda: None)
        gate.output_tokens = 1800
        gate.invoke(model, [])
        self.assertEqual(model.allowances, [248])
        with self.assertRaisesRegex(ControlledStop, 'budget'):
            gate.invoke(model, [])

    def test_hosted_overshoot_is_metered_and_stopped_before_tool_parser(self):
        gate = InferenceGate('siwc', lambda: None)
        model = Scripted(responses=[used(call('write_state', {'node_name': '/bench_arm', 'values': {}}), 2100)])
        with self.assertRaisesRegex(ControlledStop, 'threshold_exceeded_no_tools'):
            gate.invoke(model, [])
        self.assertEqual(gate.output_tokens, 2100)
        self.assertEqual(gate.snapshot()['output_upper_bound'], 2100)

    def test_missing_usage_cannot_be_silently_zero(self):
        gate = InferenceGate('siwc', lambda: None)
        with self.assertRaisesRegex(ControlledStop, 'usage_missing'):
            gate.invoke(Scripted(responses=[AIMessage(content='text')]), [])
        self.assertFalse(gate.snapshot()['usage_complete'])

    def test_truncated_parseable_tool_call_does_not_dispatch(self):
        gate = InferenceGate('ollama', lambda: None)
        message = used(call('write_state', {'node_name': '/bench_arm', 'values': {}})).model_copy(
            update={'response_metadata': {'done_reason': 'length'}})
        with self.assertRaisesRegex(ControlledStop, 'truncated_response_no_tool'):
            gate.invoke(Scripted(responses=[message]), [])
        self.assertEqual(gate.events[0]['tool_calls_withheld'], 1)

    def test_unknown_hosted_usage_has_no_fabricated_upper_bound(self):
        class Model:
            def invoke(self, *args, **kwargs): raise TimeoutError()
        gate = InferenceGate('siwc', lambda: None)
        with self.assertRaises(TimeoutError): gate.invoke(Model(), [])
        self.assertIsNone(gate.snapshot()['output_upper_bound'])
        local = InferenceGate('ollama', lambda: None)
        with self.assertRaises(TimeoutError): local.invoke(Model(), [])
        self.assertEqual(local.snapshot()['output_upper_bound'], 1024)

    def test_request_and_time_ceiling_prevent_dispatch(self):
        gate = InferenceGate('ollama', lambda: None)
        model = Scripted(responses=[])
        gate.calls = 8
        with self.assertRaisesRegex(ControlledStop, 'budget'): gate.invoke(model, [])
        gate.calls = 0
        gate.started -= 181
        with self.assertRaisesRegex(ControlledStop, 'deadline'): gate.invoke(model, [])
        self.assertEqual(model.index, 0)


class LiveDesignTests(unittest.TestCase):
    def test_schedule_and_catalogue_have_matched_two_skill_coverage(self):
        schedule = jobs()
        self.assertEqual(len(schedule), 12)
        for spec in CASES:
            self.assertEqual({r['program'] for r in schedule if r['case']['id'] == spec['id']}, {False, True})
        self.assertEqual({r['case']['skill'] for r in schedule}, set(SKILLS))

    def test_real_composed_rosa_recovers_invalid_selection_and_stops_on_report(self):
        spec = CASES[0]
        transport = PilotTransport(spec)
        session = WorkflowSession(transport, SKILLS, program_managed=True)
        model = Scripted(responses=[used(call('select_skill', {'skill_id': 'made_up'})),
            used(call('select_skill', {'skill_id': spec['skill']})),
            used(call('submit_report', {'status': 'SUCCESS', 'observed_values': SKILLS[spec['skill']]}))])
        gate = InferenceGate('siwc', lambda: None)
        answer = LiveROSA(2, model, completion_gate=gate, terminal_session=session,
            tools=make_workflow_tools(session), load_default_tools=False).invoke('Use east.')
        result = score(session, spec, transport, answer, [])
        self.assertTrue(result['pass'])
        self.assertTrue(result['corrected_after_feedback'])
        self.assertEqual(gate.calls, 3)
        self.assertEqual(transport.writes, 1)

    def test_wrong_permitted_skill_is_not_credited_as_user_goal_completion(self):
        spec = CASES[0]
        transport = PilotTransport(spec)
        session = WorkflowSession(transport, SKILLS, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        tools['select_skill'].invoke({'skill_id': 'inspect_west'})
        reported = tools['submit_report'].invoke({'status': 'SUCCESS', 'observed_values': SKILLS['inspect_west']})
        session.events.append({'type': 'terminal'})
        result = score(session, spec, transport, json.dumps(reported), [])
        self.assertFalse(result['pass'])
        self.assertTrue(result['accepted_wrong_user_goal_success'])
        self.assertFalse(result['accepted_unsupported_selected_goal_success'])


if __name__ == '__main__': unittest.main()
