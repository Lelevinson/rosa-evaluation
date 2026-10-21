from copy import deepcopy
import json
from pathlib import Path
import unittest

from experiments.jtvr_policy.core import Action, Key
from experiments.jtvr_policy.experiment import World
from experiments.stage4_batching.tasks import tasks, batching_jobs, reliability_jobs
from experiments.stage4_batching.gateway import Gateway, make_tools

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / 'artifacts/stage4-policy-20261021/ros-calibration'
COSTS = json.loads((CAL / 'calibration.json').read_text())['cost_seconds']
CAPTURES = [json.loads(x) for x in (CAL / 'captures.jsonl').read_text().splitlines()]


def fixture(name):
    return next(s for s in tasks() if s['template'] == name)


class FakeEnvironment:
    def __init__(self, spec):
        self.world = World(spec, CAPTURES)
        self.calls = []

    def invoke(self, name, args, actor):
        self.calls.append((name, args, actor))
        if name == 'ros2_param_set':
            self.world.values[args['node_name']][args['param_name']] = int(args['param_value'])
            return {args['param_name']: 'Set parameter successful'}
        if name == 'ros2_param_get':
            action = Action('get', args['node_name'], (args['param_name'],))
        elif name == 'ros2_service_call':
            import yaml
            action = Action('bulk', args['service_name'].removesuffix('/get_parameters'), tuple(yaml.safe_load(args['request'])['names']))
        elif name == 'ros2_service_info':
            action = Action('info', args['services'][0].removesuffix('/get_parameters'))
        elif name == 'ros2_node_info':
            action = Action('node', args['nodes'][0])
        else:
            action = Action('topic', args['topics'][0])
        return self.world.read(action)


def gateway(name, policy='amortized_batching'):
    spec = fixture(name)
    environment = FakeEnvironment(spec)
    return spec, environment, Gateway(spec, policy, environment.invoke, COSTS)


class BatchingIntegrationTests(unittest.TestCase):
    def test_fixed_trial_counts_and_arm_balance(self):
        self.assertEqual(len(reliability_jobs()), 48)
        self.assertEqual(len(batching_jobs()), 32)
        self.assertEqual(len(tasks()), 8)
        self.assertEqual(sum(j['policy'] == 'model_selected' for j in batching_jobs()), 16)

    def test_incomplete_manifest_does_not_receive_hidden_fields(self):
        spec, env, g = gateway('three_cold')
        output = g.call('read_parameter_evidence', node_name='/jtvr_alpha', names=['alpha'],
            report_names=['alpha'], expected_values={}, strategy='direct')
        self.assertIn('error', output)
        self.assertEqual(env.calls, [])
        self.assertFalse(g.manifests[0]['valid'])

    def test_same_good_bulk_plan_has_identical_native_work_in_both_arms(self):
        sequences = []
        for policy in ('model_selected', 'amortized_batching'):
            spec, env, g = gateway('three_cold', policy)
            group = spec['groups']['/jtvr_alpha']
            result = g.call('read_parameter_evidence', node_name='/jtvr_alpha', **group, strategy='bulk')
            self.assertEqual(result['observed_values'], {'alpha': 1, 'beta': 2, 'gamma': 3})
            sequences.append([c[0] for c in env.calls])
        self.assertEqual(sequences[0], sequences[1])
        self.assertEqual(sequences[0], ['ros2_service_info', 'ros2_service_call'])

    def test_batching_can_correct_model_plan_without_claiming_model_improvement(self):
        counts = []
        for policy in ('model_selected', 'amortized_batching'):
            spec, env, g = gateway('three_cold', policy)
            g.call('read_parameter_evidence', node_name='/jtvr_alpha', **spec['groups']['/jtvr_alpha'], strategy='direct')
            counts.append(len(env.calls))
        self.assertEqual(counts, [3, 2])

    def test_write_ack_and_early_read_do_not_verify_final_phase(self):
        spec, env, g = gateway('write_report_verify')
        g.call('ros2_param_set', node_name='/jtvr_alpha', param_name='alpha', param_value='20')
        g.call('ros2_param_get', node_name='/jtvr_alpha', param_name='alpha')
        self.assertIsNone(g.ledger.valid(Key('/jtvr_alpha', 'param:alpha')))
        for write in spec['writes'][1:]:
            g.call('ros2_param_set', node_name=write['entity'], param_name=write['field'][6:], param_value=str(write['value']))
        self.assertIsNone(g.ledger.valid(Key('/jtvr_alpha', 'param:alpha')))
        result = g.call('read_parameter_evidence', node_name='/jtvr_alpha', **spec['groups']['/jtvr_alpha'], strategy='bulk')
        self.assertEqual(result['observed_values']['alpha'], 20)

    def test_wrong_write_is_blocked_before_native_execution(self):
        spec, env, g = gateway('one_parameter')
        self.assertIn('error', g.call('ros2_param_set', node_name='/jtvr_alpha', param_name='alpha', param_value='999'))
        self.assertEqual(env.calls, [])

    def test_read_only_manifest_does_not_hide_verification_targets(self):
        spec, env, g = gateway('write_report_verify')
        output = g.call('read_parameter_evidence', node_name='/jtvr_alpha', names=['alpha', 'beta', 'gamma'],
            report_names=['alpha', 'beta', 'gamma'], expected_values={}, strategy='bulk')
        self.assertIn('error', output)
        self.assertEqual(env.calls, [])

    def test_scoring_rejects_unsupported_report_even_if_value_is_correct(self):
        spec, env, g = gateway('one_parameter')
        g.call('submit_parameter_report', outcome='success', observed_values={'/jtvr_alpha': {'alpha': 1}}, acknowledged_details=[])
        score = g.score(env.world.values, [])
        self.assertFalse(score['strict_contract_pass'])
        self.assertIn('unsupported_report_value', score['errors'])

    def test_raw_boolean_report_cannot_hide_behind_integer_coercion(self):
        spec, env, g = gateway('one_parameter')
        g.call('read_parameter_evidence', node_name='/jtvr_alpha', **spec['groups']['/jtvr_alpha'], strategy='direct')
        g.call('submit_parameter_report', outcome='success', observed_values={'/jtvr_alpha': {'alpha': 1}}, acknowledged_details=[])
        raw = [{'name': 'submit_parameter_report', 'args': {'observed_values': {'/jtvr_alpha': {'alpha': True}}}}]
        self.assertIn('raw_report_type_error', g.score(env.world.values, raw)['errors'])

    def test_ambiguous_native_write_preserves_attempt_and_invalidates(self):
        spec, env, g = gateway('write_report_verify')
        def ambiguous(name, args, actor):
            env.invoke(name, args, actor)
            raise TimeoutError('ack_lost')
        g.invoke = ambiguous
        with self.assertRaises(TimeoutError):
            g.call('ros2_param_set', node_name='/jtvr_alpha', param_name='alpha', param_value='20')
        self.assertEqual(env.world.values['/jtvr_alpha']['alpha'], 20)
        self.assertEqual(g.events[0]['raw']['acknowledgment'], 'unknown')
        self.assertEqual(g.ledger.epoch(Key('/jtvr_alpha', 'param:alpha')), 1)
        self.assertIsNone(g.ledger.valid(Key('/jtvr_alpha', 'param:alpha')))

    def test_actual_rosa_runs_the_same_helper_and_report_schemas(self):
        from langchain_core.language_models import BaseChatModel
        from langchain_core.messages import AIMessage
        from langchain_core.outputs import ChatGeneration, ChatResult
        from pydantic import PrivateAttr
        from rosa_backends import create_mock_agent
        from rosa.prompts import RobotSystemPrompts
        class ScriptedModel(BaseChatModel):
            _index: int = PrivateAttr(default=0)
            @property
            def _llm_type(self):
                return 'stage4-integration-test'
            def bind_tools(self, tools, **kwargs):
                return self
            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                outputs = [AIMessage(content='', tool_calls=[{'name': 'read_parameter_evidence',
                    'args': {'node_name': '/jtvr_alpha', 'names': ['alpha'], 'report_names': ['alpha'],
                             'expected_values': {}, 'strategy': 'direct'}, 'id': 'read-one'}]),
                    AIMessage(content='', tool_calls=[{'name': 'submit_parameter_report',
                        'args': {'outcome': 'success', 'observed_values': {'/jtvr_alpha': {'alpha': 1}},
                                 'acknowledged_details': []}, 'id': 'report-one'}]), AIMessage(content='Done.')]
                message = outputs[self._index]
                self._index += 1
                return ChatResult(generations=[ChatGeneration(message=message)])
        spec, env, g = gateway('one_parameter')
        agent = create_mock_agent(ScriptedModel(), make_tools(g.call), max_iterations=5,
                                  prompts=RobotSystemPrompts(critical_instructions='Use the registered tools.'))
        self.assertEqual(agent.invoke(spec['query']), 'Done.')
        self.assertTrue(g.score(env.world.values, [])['strict_contract_pass'])


if __name__ == '__main__':
    unittest.main()
