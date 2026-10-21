"""Behavioral and adversarial tests for the new isolated policy experiment."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from experiments.jtvr_policy.core import (Action, GET_TYPE, Key, Ledger, Obligation,
    State, coverage, manifest, parse, select, type_key)
from experiments.jtvr_policy.experiment import execute
from experiments.jtvr_policy.fixtures import NODES, suite
from experiments.jtvr_policy.audit import check

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / 'artifacts/stage4-policy-20261021/ros-calibration'


def state_for(count=3, extra=()):
    requirements = [Obligation(Key(NODES[0], 'param:' + name), frozenset(('task',)))
                    for name in ('alpha', 'beta', 'gamma')[:count]] + list(extra)
    return State(requirements, Ledger(), {tool: 1.0 for tool in
        ('ros2_param_get', 'ros2_service_info', 'ros2_service_call', 'ros2_node_info', 'ros2_topic_info')})


class EvidenceTests(unittest.TestCase):
    def test_manifest_deduplication_does_not_double_charge_roles(self):
        task = {'entity': '/n', 'field': 'param:a', 'roles': ['task'], 'equals': 20}
        verify = {**task, 'roles': ['verification']}
        combined = {**task, 'roles': ['task', 'verification']}
        result = manifest([task, verify], [combined])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].roles, frozenset(('task', 'verification')))

    def test_incomplete_wrong_target_or_expanded_manifest_is_rejected(self):
        truth = [{'entity': '/n', 'field': 'param:a', 'roles': ['task', 'verification'], 'equals': 20}]
        variants = [[], [{**truth[0], 'equals': 15}], [{**truth[0], 'roles': ['task']}],
                    truth + [{**truth[0], 'entity': '/other'}], [{**truth[0], 'equals': True}]]
        for rows in variants:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                manifest(rows, truth)

    def test_write_dispatch_invalidates_even_without_acknowledgment(self):
        ledger, key = Ledger(), Key('/n', 'param:a')
        ledger.ingest(key, 20, epoch=0, started=0, raw_ref=0, tool='read')
        ledger.dispatch_write(key)
        self.assertIsNone(ledger.valid(key))
        self.assertEqual(ledger.epoch(key), 1)
        self.assertFalse(ledger.ingest(key, 20, epoch=1, started=1, raw_ref=1, tool='inflight'))
        ledger.complete_write(key)
        self.assertFalse(ledger.ingest(key, 20, epoch=0, started=0, raw_ref=2, tool='delayed'))
        self.assertTrue(ledger.ingest(key, 15, epoch=1, started=ledger.tick, raw_ref=3, tool='fresh'))
        self.assertEqual(ledger.valid(key).value, 15)  # Valid evidence, failed goal.

    def test_read_started_before_write_completion_is_not_post_write_evidence(self):
        ledger, key = Ledger(), Key('/n', 'param:a')
        ledger.dispatch_write(key)
        started = ledger.tick
        ledger.complete_write(key)
        self.assertFalse(ledger.ingest(key, 20, epoch=1, started=started, raw_ref=0, tool='read'))

    def test_scope_phase_and_age_prevent_reuse(self):
        ledger, key = Ledger(), Key('/left', 'param:a')
        ledger.ingest(key, 1, epoch=0, started=0, raw_ref=0, tool='read')
        self.assertIsNone(ledger.valid(Key('/right', 'param:a')))
        self.assertIsNone(ledger.valid(Key('/left', 'param:a', 'before')))
        ledger.tick = 33
        self.assertIsNone(ledger.valid(key))

    def test_external_writer_is_not_detectable_by_local_epochs(self):
        ledger, key = Ledger(), Key('/n', 'param:a')
        ledger.ingest(key, 1, epoch=0, started=0, raw_ref=0, tool='read')
        external_world_value = 2
        self.assertNotEqual(ledger.valid(key).value, external_world_value)
        # Explicit limitation, not a fabricated external-writer guarantee.


class ParserAndPolicyTests(unittest.TestCase):
    def test_actual_captured_shapes_parse(self):
        rows = [json.loads(line) for line in (CALIBRATION / 'captures.jsonl').read_text().splitlines()]
        actions = {'ros2_param_get': Action('get', NODES[0], ('alpha',)),
            'ros2_service_info': Action('info', NODES[0]),
            'ros2_service_call': Action('bulk', NODES[0], ('alpha', 'beta', 'gamma')),
            'ros2_node_info': Action('node', NODES[0]),
            'ros2_topic_info': Action('topic', NODES[0] + '/status')}
        for row in rows:
            if row['purpose'] == 'development_calibration_0':
                with self.subTest(tool=row['tool']):
                    self.assertTrue(parse(actions[row['tool']], row['raw']))

    def test_short_bulk_is_not_zipped_to_names(self):
        action = Action('bulk', '/n', ('a', 'b'))
        raw = {'response': 'response:\nrcl_interfaces.srv.GetParameters_Response(values=['
               'rcl_interfaces.msg.ParameterValue(type=2, integer_value=20)])'}
        self.assertEqual(parse(action, raw), {})

    def test_unset_entry_preserves_only_unambiguous_numeric_values(self):
        action = Action('bulk', '/n', ('a', 'b'))
        raw = {'response': 'response:\nrcl_interfaces.srv.GetParameters_Response(values=['
               'rcl_interfaces.msg.ParameterValue(type=0, integer_value=0),'
               'rcl_interfaces.msg.ParameterValue(type=2, integer_value=20)])'}
        self.assertEqual(parse(action, raw), {'param:b': 20})

    def test_untrusted_repr_is_not_executed_or_accepted(self):
        action = Action('bulk', '/n', ('a',))
        self.assertEqual(parse(action, {'response': "response:\n__import__('os').system('invalid')"}), {})
        self.assertEqual(parse(Action('get', '/n', ('a',)), {'a': 'ERROR: Integer value is: 20'}), {})

    def test_node_info_cannot_supply_parameter_values_or_qos(self):
        due = {Key('/n', 'param:a'), Key('/n', 'node_summary', 'graph'), Key('/n/status', 'topic_details', 'graph')}
        self.assertEqual(coverage(Action('node', '/n'), due), {Key('/n', 'node_summary', 'graph')})

    def test_cold_triplet_exposes_discovery_but_batching_matches_jtvr(self):
        state = state_for()
        g, b, j = [select(state, p) for p in ('greedy', 'batching', 'jtvr')]
        self.assertEqual(g.reference_completion, 3)
        self.assertEqual(b.predicted_completion, 2)
        self.assertEqual(j.predicted_completion, 2)
        self.assertIn(j.fragment[0].op, ('info', 'node'))
        self.assertEqual(state.ledger.records, [])  # No imagined evidence leakage.

    def test_single_field_does_not_pay_discovery(self):
        for policy in ('greedy', 'batching', 'jtvr'):
            self.assertEqual(select(state_for(1), policy).fragment[0].op, 'get')

    def test_warm_bulk_is_callable_even_for_greedy(self):
        state = state_for()
        state.ledger.ingest(type_key(NODES[0]), GET_TYPE, epoch=0, started=0, raw_ref=0, tool='seed')
        for policy in ('greedy', 'batching', 'jtvr'):
            self.assertEqual(select(state, policy).fragment[0].op, 'bulk')

    def test_batching_credits_node_summary_discovery_overlap(self):
        state = state_for(extra=(Obligation(Key(NODES[0], 'node_summary', 'graph'), frozenset(('task',))),))
        batch = select(state, 'batching')
        self.assertEqual(batch.predicted_completion, 2)
        self.assertEqual(batch.fragment[0].op, 'node')
        self.assertEqual(batch.fragment[1].op, 'bulk')

    def test_high_setup_cost_rejects_unprofitable_exploration(self):
        state = state_for()
        state.costs.update(ros2_service_info=4, ros2_node_info=4)
        for policy in ('greedy', 'batching', 'jtvr'):
            self.assertEqual(select(state, policy).fragment[0].op, 'get')

    def test_wrong_actual_type_cancels_bulk_continuation(self):
        state = state_for()
        state.ledger.ingest(type_key(NODES[0]), 'example_interfaces/srv/Trigger',
                            epoch=0, started=0, raw_ref=0, tool='actual')
        for policy in ('greedy', 'batching', 'jtvr'):
            self.assertNotEqual(select(state, policy).fragment[0].op, 'bulk')

    def test_changed_requirements_are_replanned_not_reused_blindly(self):
        state = state_for(1)
        old = select(state, 'jtvr').fragment
        state.obligations += state_for(3).obligations[1:]
        new = select(state, 'jtvr').fragment
        self.assertEqual(old[0].op, 'get')
        self.assertIn(new[0].op, ('info', 'node'))

    def test_expansion_cap_and_greedy_reference_are_retained(self):
        state = state_for()
        decision = select(state, 'jtvr', max_expansions=0)
        self.assertEqual(decision.fragment[0].op, 'get')
        self.assertEqual(decision.predicted_completion, decision.reference_completion)
        self.assertLessEqual(select(state, 'jtvr', max_expansions=3).expansions, 3)

    def test_partial_results_fall_back_under_common_runner(self):
        captures = [json.loads(line) for line in (CALIBRATION / 'captures.jsonl').read_text().splitlines()]
        costs = json.loads((CALIBRATION / 'calibration.json').read_text())['cost_seconds']
        spec = next(s for s in suite() if s['template'] == 'three_cold' and
                    s['condition'] == 'partial_bulk' and s['seed'] == 0)
        for policy in ('batching', 'jtvr'):
            result = execute(spec, policy, costs, captures)
            self.assertTrue(result['verified_contract_pass'])
            self.assertEqual(sum(r.get('op') == 'bulk' for r in result['trace']), 1)
            self.assertTrue(any(r.get('op') == 'get' for r in result['trace']))

    def test_ambiguous_write_requires_observation_not_ack(self):
        captures = [json.loads(line) for line in (CALIBRATION / 'captures.jsonl').read_text().splitlines()]
        costs = json.loads((CALIBRATION / 'calibration.json').read_text())['cost_seconds']
        spec = next(s for s in suite() if s['template'] == 'write_report_verify' and
                    s['condition'] == 'ambiguous_write_ack' and s['seed'] == 0)
        result = execute(spec, 'jtvr', costs, captures)
        self.assertTrue(result['verified_contract_pass'])
        self.assertTrue(all(e['status'] == 'INVALID' for e in result['evidence'] if e['tool'] == 'pre_write_seed'))
        self.assertTrue(all(v == 'TRUE' for v in result['goal_predicates'].values()))

    def test_readback_audit_detects_fabricated_value_and_unproven_type(self):
        captures = [json.loads(line) for line in (CALIBRATION / 'captures.jsonl').read_text().splitlines()]
        costs = json.loads((CALIBRATION / 'calibration.json').read_text())['cost_seconds']
        spec = next(s for s in suite() if s['template'] == 'three_cold' and
                    s['condition'] == 'nominal' and s['seed'] == 0)
        row = execute(spec, 'batching', costs, captures)
        self.assertTrue(check(row, spec)['passed'])
        broken = deepcopy(row)
        bulk = next(r for r in broken['trace'] if r.get('op') == 'bulk')
        bulk['parsed']['param:alpha'] = 999
        self.assertFalse(check(broken, spec)['passed'])
        broken = deepcopy(row)
        discovery = next(r for r in broken['trace'] if r.get('op') == 'info')
        discovery['raw'] = {'/jtvr_alpha/get_parameters': 'example_interfaces/srv/Trigger'}
        self.assertIn('bulk_without_actual_matching_type', check(broken, spec)['errors'])


if __name__ == '__main__':
    unittest.main()
