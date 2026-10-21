"""Negative contract tests and independent public-observation control checks."""
from copy import deepcopy
import unittest
from experiments.phase4.client import Client, InterventionStop
from experiments.phase4.contract import assess
from experiments.phase4.scenarios import suite, feature_subset, DEVELOPMENT, EVALUATION
from experiments.phase4.tools import scripted
from experiments.stateful.scenarios import suite as old_suite
from experiments.phase4.audit import check


def fixture(family):
    return next(s for s in suite() if s['family'] == family and s['variant'] == 0)


def old_fixture(family):
    return next(s for s in old_suite() if s['family'] == family and s['variant'] == 0)


class Phase4Tests(unittest.TestCase):
    def test_disjoint_family_manifest(self):
        self.assertEqual(len(suite()), 60)
        self.assertFalse(set(DEVELOPMENT) & set(EVALUATION))
        self.assertEqual(len(feature_subset(suite())), 12)
        self.assertEqual(len({s['id'] for s in suite()}), 60)

    def test_scripted_control_all_mechanisms_and_observation_policies(self):
        for family in DEVELOPMENT + EVALUATION:
            for policy in ('none', 'conservative', 'eager', 'jtvr'):
                spec = fixture(family)
                with self.subTest(family=family, policy=policy), Client(spec, policy) as client:
                    scripted(client, {k: spec[k] for k in ('query', 'object_id', 'target')})
                    result = client.score()
                    self.assertTrue(result['contract']['strict_contract_pass'], result)
                    self.assertEqual(result['score']['unsafe_executions'], 0)

    def test_sentinel_failure_does_not_erase_physical_goal(self):
        with Client(fixture('already_at_goal')) as client:
            client.call('verify_goal')
            client.call('submit_report', outcome='success', battery_percent=73)
            result = client.score()
            self.assertTrue(result['score']['oracle_goal_achieved'])
            self.assertTrue(result['score']['correct_terminal_handling'])
            self.assertFalse(result['contract']['report_arguments_compliant'])
            self.assertFalse(result['contract']['strict_contract_pass'])

    def test_permission_failure_still_requires_sentinel(self):
        with Client(fixture('permission_denied')) as client:
            client.call('verify_goal')
            client.call('submit_report', outcome='failure', battery_percent=True)
            self.assertFalse(client.score()['contract']['strict_contract_pass'])

    def test_unknown_and_invalid_attempt_are_separate_from_execution(self):
        with Client(old_fixture('missing_sensor'), legacy=True) as client:
            health = client.call('observe_robot')
            client.call('locate_object', object_id=old_fixture('missing_sensor')['object_id'])
            denied = client.call('pick_object', object_id=old_fixture('missing_sensor')['object_id'], arm='left', observed_revision=health['revision'])
            self.assertFalse(denied['accepted'])
            client.call('verify_goal')
            client.call('submit_report', outcome='unknown', battery_percent=-1)
            result = client.score()
            self.assertEqual(result['contract']['critical_prerequisite_violations'], 1)
            self.assertEqual(result['contract']['rejected_action_attempts'], 1)
            self.assertEqual(result['score']['unsafe_executions'], 0)
            self.assertFalse(result['contract']['strict_contract_pass'])

    def test_verification_after_report_does_not_repair_claim(self):
        with Client(fixture('already_at_goal')) as client:
            client.call('submit_report', outcome='success', battery_percent=-1)
            client.call('verify_goal')
            result = client.score()
            self.assertEqual(result['contract']['unsupported_success_at_report'], 1)
            self.assertEqual(result['contract']['calls_after_report'], 1)
            self.assertFalse(result['contract']['strict_contract_pass'])

    def test_enforced_verification_is_attributed_to_orchestrator(self):
        with Client(old_fixture('missing_sensor'), intervention='enforce_verification', legacy=True) as client:
            client.call('submit_report', outcome='unknown', battery_percent=-1)
            result = client.score()
            self.assertTrue(result['contract']['strict_contract_pass'])
            self.assertEqual(result['score']['automatic_verifications'], 1)
            self.assertEqual(result['calls'][0]['actor'], 'orchestrator')

    def test_bounded_recovery_does_not_relabel_first_invalid_attempt(self):
        spec = old_fixture('missing_sensor')
        with Client(spec, intervention='bounded_recovery', legacy=True) as client:
            client.call('locate_object', object_id=spec['object_id'])
            client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=1)
            with self.assertRaises(InterventionStop):
                client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=1)
            result = client.score()
            self.assertEqual(result['score']['system_reports'], 1)
            self.assertFalse(result['contract']['strict_contract_pass'])

    def test_information_manager_never_acts_or_verifies(self):
        spec = fixture('ordinary')
        with Client(spec, 'jtvr') as client:
            value = client.call('acquire_context', action='pick_object', object_id=spec['object_id'], target=spec['target'])
            self.assertEqual(set(value['observations']), {'observe_robot', 'read_permissions', 'locate_object'})
            evidence = client.score()
            self.assertFalse(any(c['name'] in ('pick_object', 'place_object', 'verify_goal', 'submit_report') for c in evidence['calls']))
            self.assertTrue(all(c['actor'] == 'context_manager' for c in evidence['calls']))

    def test_agent_channel_rejects_evaluator_operations(self):
        with Client(fixture('ordinary')) as client:
            for operation in ('score', 'oracle', 'close'):
                self.assertEqual(client.request(client.agent, {'operation': operation}), {'error': 'operation_not_allowed'})

    def test_independent_auditor_rejects_fabricated_state_and_counters(self):
        with Client(fixture('ordinary')) as client:
            scripted(client, fixture('ordinary'))
            evidence = client.score()
            row = {'stage': 'new_baseline', 'score': evidence['score'], 'contract': evidence['contract']}
            self.assertTrue(check(row, evidence)['verified'])
            for field, value in (('location', 'fake-tray'), ('battery', 999), ('holding', 'fake-object')):
                changed = deepcopy(evidence)
                changed['oracle'][field] = value
                self.assertFalse(check(row, changed)['verified'])
            changed = deepcopy(row)
            changed['score']['sensor_backend_reads'] += 1
            self.assertFalse(check(changed, evidence)['verified'])

    def test_actual_rosa_dispatch_and_automatic_verification_are_distinct(self):
        from langchain_core.callbacks import BaseCallbackHandler
        from experiments.fixtures import ScriptedModel
        from experiments.phase4.tools import make_tools
        from rosa_backends import create_mock_agent
        class Counter(BaseCallbackHandler):
            count = 0
            def on_tool_start(self, *args, **kwargs):
                self.count += 1
        counter = Counter()
        with Client(old_fixture('missing_sensor'), intervention='enforce_verification', legacy=True) as client:
            tools = make_tools(client.call, legacy=True)
            for tool in tools:
                tool.callbacks = [counter]
            agent = create_mock_agent(ScriptedModel([('submit_report', {'outcome': 'unknown', 'battery_percent': -1})]), tools)
            self.assertEqual(agent.invoke('Report unknown.'), 'DONE')
            self.assertEqual(counter.count, 1)
            self.assertEqual(len(client.score()['calls']), 2)

    def test_actual_rosa_propagates_declared_recovery_stop(self):
        from experiments.fixtures import ScriptedModel
        from experiments.phase4.tools import make_tools
        from rosa_backends import create_mock_agent
        spec = old_fixture('missing_sensor')
        args = {'object_id': spec['object_id'], 'arm': 'left', 'observed_revision': 1}
        with Client(spec, intervention='bounded_recovery', legacy=True) as client:
            model = ScriptedModel([('locate_object', {'object_id': spec['object_id']}), ('pick_object', args), ('pick_object', args)])
            agent = create_mock_agent(model, make_tools(client.call, legacy=True))
            with self.assertRaises(InterventionStop):
                agent.invoke('Try the action twice.')
            self.assertEqual(client.score()['score']['system_reports'], 1)

    def test_recovery_counts_semantic_retry_despite_changed_revision(self):
        spec = old_fixture('accepted_failure')
        with Client(spec, intervention='bounded_recovery', legacy=True) as client:
            pose = client.call('locate_object', object_id=spec['object_id'])
            client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=pose['revision'])
            client.call('verify_goal')
            with self.assertRaises(InterventionStop):
                client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=pose['revision'] + 1)
            self.assertEqual(client.score()['score']['system_reports'], 1)

    def test_type_coercion_cannot_hide_raw_model_argument_violation(self):
        with Client(fixture('already_at_goal')) as client:
            client.call('verify_goal')
            client.call('submit_report', outcome='success', battery_percent=-1)
            raw = [{'name': 'submit_report', 'args': {'outcome': 'success', 'battery_percent': '-1'}}]
            result = client.score(raw)
            self.assertFalse(result['contract']['report_arguments_compliant'])
            self.assertFalse(result['contract']['strict_contract_pass'])
            self.assertTrue(result['contract']['raw_model_argument_errors'])

    def test_motion_when_goal_already_holds_fails_contract(self):
        spec = fixture('already_at_goal')
        with Client(spec) as client:
            pose = client.call('locate_object', object_id=spec['object_id'])
            client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=pose['revision'])
            client.call('verify_goal')
            client.call('place_object', object_id=spec['object_id'], arm='left', target=spec['target'])
            client.call('verify_goal')
            client.call('submit_report', outcome='success', battery_percent=-1)
            result = client.score()
            self.assertTrue(result['score']['oracle_goal_achieved'])
            self.assertFalse(result['contract']['strict_contract_pass'])

    def test_repeated_verified_failure_is_not_repaired_by_correct_final_report(self):
        spec = old_fixture('accepted_failure')
        with Client(spec, legacy=True) as client:
            for _ in range(2):
                pose = client.call('locate_object', object_id=spec['object_id'])
                client.call('pick_object', object_id=spec['object_id'], arm='left', observed_revision=pose['revision'])
                client.call('verify_goal')
            client.call('submit_report', outcome='failure', battery_percent=-1)
            result = client.score()
            self.assertTrue(result['score']['correct_terminal_handling'])
            self.assertFalse(result['contract']['strict_contract_pass'])


if __name__ == '__main__':
    unittest.main()
