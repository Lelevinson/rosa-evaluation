from copy import deepcopy
import json
import unittest

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import Field
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts, system_prompts
from rosa_reliability.prompt_contract import BoundedPromptROSA, bounded_contract, REQUIRED_TOOLS
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from rosa_reliability.macro import MacroSession
from experiments.workflow_v1.pilot import Scripted, call
from experiments.macro_transfer_v1.inference import InferenceGate, LiveROSA
from experiments.macro_transfer_v1.design import cases, catalogue, PilotTransport


class RepairedROSA(BoundedPromptROSA, LiveROSA):
    pass


class RecordingModel(Scripted):
    seen: list = Field(default_factory=list)

    def _generate(self, messages, **kwargs):
        self.seen.append(deepcopy(messages))
        return super()._generate(messages, **kwargs)


def used(message):
    return message.model_copy(update={'usage_metadata': {
        'input_tokens': 100, 'output_tokens': 10, 'total_tokens': 110}})


class PromptContractTests(unittest.TestCase):
    def setup_agent(self, condition='model', prompts=None, responses=None, repaired=True, fault_index=0):
        spec = cases()[fault_index]
        session = (MacroSession if condition == 'macro' else ReferenceWorkflowSession)(
            PilotTransport(spec), catalogue('mock'), program_managed=condition != 'model', tolerance=.025)
        model = RecordingModel(responses=responses or [used(AIMessage(content='scripted inspection'))])
        gate = InferenceGate('siwc', lambda: None)
        agent = (RepairedROSA if repaired else LiveROSA)(2, model, completion_gate=gate,
            terminal_session=session, tools=make_reference_tools(session),
            load_default_tools=False, prompts=prompts)
        return agent, model, session

    def test_actual_model_input_has_only_registered_tools_and_consistent_order(self):
        agent, model, _ = self.setup_agent()
        agent.invoke('Observe the requested bounded goal: GOAL_SENTINEL.')
        messages = model.seen[0]
        system = '\n'.join(m.content for m in messages if isinstance(m, SystemMessage))
        self.assertEqual(set(agent.tool_names), REQUIRED_TOOLS)
        for absent in ('rosnode_list', 'rostopic_list', 'rosparams', 'math tools'):
            self.assertNotIn(absent, system)
        self.assertIn('before any other tool', system)
        self.assertIn('At most one dispatched write', system)
        self.assertIn('Missing observations cannot authorize movement', system)
        self.assertTrue(any(isinstance(m, HumanMessage) and 'GOAL_SENTINEL' in m.content for m in messages))

    def test_robot_specific_safety_constraints_are_preserved(self):
        prompts = RobotSystemPrompts(constraints_and_guardrails='SAFETY_SENTINEL: use only the bounded near-home envelope.',
            critical_instructions='AUTH_SENTINEL: never expand the authorized skill catalog.')
        agent, model, _ = self.setup_agent(prompts=prompts)
        agent.invoke('Task.')
        system = '\n'.join(m.content for m in model.seen[0] if isinstance(m, SystemMessage))
        self.assertIn('SAFETY_SENTINEL', system)
        self.assertIn('AUTH_SENTINEL', system)

    def test_history_user_and_tool_scratchpad_survive_template_replacement(self):
        agent, _, _ = self.setup_agent()
        messages = agent._get_prompts().format_messages(input='USER_SENTINEL',
            chat_history=[HumanMessage(content='HISTORY_SENTINEL')],
            agent_scratchpad=[ToolMessage(content='TOOL_SENTINEL', tool_call_id='test')])
        self.assertEqual([m.content for m in messages[-3:]],
                         ['HISTORY_SENTINEL', 'USER_SENTINEL', 'TOOL_SENTINEL'])

    def test_all_conditions_receive_identical_common_system_contract(self):
        systems = []
        for condition in ('model', 'macro', 'workflow'):
            agent, model, _ = self.setup_agent(condition)
            agent.invoke('Task.')
            systems.append([m.content for m in model.seen[0] if isinstance(m, SystemMessage)])
        self.assertEqual(systems[0], systems[1])
        self.assertEqual(systems[1], systems[2])

    def test_missing_or_extra_tools_fail_before_inference(self):
        for names in (REQUIRED_TOOLS - {'select_skill'}, REQUIRED_TOOLS | {'unreviewed_tool'}):
            with self.assertRaises(ValueError):
                bounded_contract(names)

    def test_default_rosa_prompts_and_legacy_agent_are_unchanged(self):
        before = deepcopy(system_prompts)
        _, repaired, _ = self.setup_agent()
        legacy, model, _ = self.setup_agent(repaired=False)
        legacy.invoke('Task.')
        self.assertIn('rosnode_list', '\n'.join(m.content for m in model.seen[0] if isinstance(m, SystemMessage)))
        self.assertEqual(before, system_prompts)

    def test_repair_adds_no_inference_or_native_assistance(self):
        agent, model, session = self.setup_agent()
        agent.invoke('Task.')
        self.assertEqual(model.index, 1)
        self.assertEqual(session.tool_calls, 0)
        self.assertFalse(session.budget.events)

    def test_selection_guard_remains_active_after_repair(self):
        agent, model, session = self.setup_agent(responses=[used(call('read_state', {'nodes': ['/ur5e']})),
            used(AIMessage(content='stop'))])
        agent.invoke('Task.')
        self.assertEqual(session.validation_errors, 1)
        self.assertFalse(session.budget.events)


if __name__ == '__main__':
    unittest.main()
