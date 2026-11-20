from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rosa_reliability.macro import MacroSession
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from rosa_reliability.ros_arm import HOME_POSE
from experiments.macro_focus_v2.design import catalogue, cases, jobs, query, LIMITS, FaultTransport
from experiments.macro_focus_v2.scoring import score
from experiments.macro_focus_v2.gates import require_validation


class FixtureArm:
    requires_observation = True

    def __init__(self, spec):
        self.values = deepcopy(catalogue()[spec['initial_skill']])
        self.records, self.fault = [], spec['fault']

    def validate_write(self, node, values):
        if node != '/ur5e' or set(values) != set(HOME_POSE) or any(
                abs(v - HOME_POSE[k]) > .4 for k, v in values.items()):
            return 'invalid bounded target'

    def read(self, node, names):
        self.records.append({'kind': 'read', 'missing': False})
        return deepcopy(self.values[node])

    def write(self, node, values):
        self.records.append({'kind': 'write', 'requested': deepcopy(values),
            'injected_partial': self.fault == 'partial'})
        self.values[node] = deepcopy(values)
        if self.fault == 'partial':
            self.values[node]['wrist_3_joint'] = HOME_POSE['wrist_3_joint']
        return {'request_accepted_locally': True}


def execute_fixture(spec, condition):
    transport = FaultTransport(FixtureArm(spec), spec)
    session = (MacroSession if condition == 'macro' else ReferenceWorkflowSession)(
        transport, catalogue(), program_managed=condition != 'model', tolerance=.025)
    tools = {t.name: t for t in make_reference_tools(session)}
    tools['select_skill'].invoke({'skill_id': spec['skill']})
    if condition == 'model' or spec['fault'] == 'transient_before':
        tools['read_state'].invoke({'nodes': ['/ur5e']})
        if condition == 'model' and spec['fault'] == 'transient_before':
            tools['read_state'].invoke({'nodes': ['/ur5e']})
        if spec['required_dispatches']:
            tools['write_state'].invoke({'node_name': '/ur5e', 'values': catalogue()[spec['skill']]['/ur5e']})
        tools['verify_outcome'].invoke({})
    if spec['fault'] == 'missing_after':
        tools['verify_outcome'].invoke({})
    observation = session.observations[-1]
    tools['submit_report'].invoke({'status': spec['expected'], 'observation_id': observation['observation_id']})
    session.events.append({'type': 'terminal'})
    return session, transport, tools


class FreshMacroTests(unittest.TestCase):
    def test_external_trial_timer_is_bounded_by_backend_deadline(self):
        from experiments.macro_focus_v2.runner import trial_allowance
        from rosa_reliability import ControlledStop
        self.assertEqual(trial_allowance(0, now=0), 180)
        self.assertEqual(trial_allowance(0, now=4490), 10)
        with self.assertRaises(ControlledStop):
            trial_allowance(0, now=4500)

    @staticmethod
    def paired_rows(correct_candidate=True, pair_count=12):
        rows = []
        for index in range(pair_count):
            for condition, calls in (('model', 6), ('macro', 3)):
                rows.append({'case': 'case-' + str(index // 2), 'repetition': index % 2 + 1,
                    'condition': condition, 'inference': {'calls': calls, 'known_input_tokens': calls * 100,
                    'known_output_tokens': calls * 10, 'usage_complete': True}, 'native_operations': 3,
                    'wall_seconds': calls * 5, 'score': {'pass': condition == 'model' or correct_candidate,
                    'program_native_operations': 0 if condition == 'model' else 3, 'invalid_attempts': 0,
                    'corrected_after_feedback': False, 'unsupported_success_attempts': 0,
                    'accepted_unsupported_selected_goal_success': False, 'dispatch_violations': [],
                    'injected_fault_exercised': None}})
        return rows

    def test_retention_never_rewards_cheap_failed_trials(self):
        from experiments.macro_focus_v2.analysis import comparison
        rows = self.paired_rows(correct_candidate=False)
        result = comparison(rows, 'macro', 'model', .8, 1.2)
        self.assertFalse(result['screen_pass'])
        self.assertEqual(len(result['candidate_losses']), 12)
        self.assertEqual(result['matched_correct_pairs'], 0)
        self.assertIsNone(result['matched_call_reduction_fraction'])

    def test_retention_requires_enough_complete_pairs_and_native_bound(self):
        from experiments.macro_focus_v2.analysis import comparison
        good = self.paired_rows()
        self.assertTrue(comparison(good, 'macro', 'model', .8, 1.2)['screen_pass'])
        self.assertFalse(comparison(self.paired_rows(pair_count=5), 'macro', 'model', .8, 1.2)['screen_pass'])
        for row in good:
            if row['condition'] == 'macro':
                row['native_operations'] = 10
        self.assertFalse(comparison(good, 'macro', 'model', .8, 1.2)['screen_pass'])

    def test_balanced_paired_schedule_and_caps(self):
        plan = jobs()
        self.assertEqual(len(plan), 36)
        self.assertEqual(len({(j['case']['id'], j['condition'], j['repetition']) for j in plan}), 36)
        self.assertEqual(LIMITS['backend_request_cap'], 8 * len(plan))
        for condition in ('model', 'macro', 'workflow'):
            self.assertEqual([sum(plan[i]['condition'] == condition for i in range(position, 36, 3))
                              for position in range(3)], [4, 4, 4])

    def test_targets_within_existing_near_home_permission(self):
        for group in catalogue().values():
            self.assertEqual(set(group['/ur5e']), set(HOME_POSE))
            self.assertTrue(all(abs(v - HOME_POSE[k]) <= .4 for k, v in group['/ur5e'].items()))

    def test_macro_workflow_prompts_identical_private_labels_absent(self):
        for spec in cases():
            text = query(spec, 'macro', 'gazebo')
            self.assertEqual(text, query(spec, 'workflow', 'gazebo'))
            for private in ('expected_status', 'required_dispatches', 'initial_skill', 'injected_partial',
                            'transient_before', 'missing_after'):
                self.assertNotIn(private, text)

    def test_all_eighteen_control_paths_and_fault_coverage(self):
        for spec in cases():
            for condition in ('model', 'macro', 'workflow'):
                with self.subTest(case=spec['id'], condition=condition):
                    session, transport, _ = execute_fixture(spec, condition)
                    result = score(session, spec, transport, '{}', [], catalogue(), .025,
                                   transport.underlying.values)
                    self.assertTrue(result['pass'], result)
                    self.assertLessEqual(len(session.snapshot()['operations']), 10)

    def test_unknown_is_truthful_despite_private_goal_attainment(self):
        spec = next(s for s in cases() if s['fault'] == 'missing_after')
        session, transport, _ = execute_fixture(spec, 'macro')
        result = score(session, spec, transport, '{}', [], catalogue(), .025, transport.underlying.values)
        self.assertTrue(result['pass'])
        self.assertTrue(result['truthful_report'])
        self.assertTrue(result['requested_goal_attained'])
        self.assertEqual(result['accepted_report_status'], 'UNKNOWN')

    def test_postwrite_unknown_cannot_be_promoted_to_success(self):
        spec = next(s for s in cases() if s['fault'] == 'missing_after')
        transport = FaultTransport(FixtureArm(spec), spec)
        session = MacroSession(transport, catalogue(), program_managed=True, tolerance=.025)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        tools['submit_report'].invoke({'status': 'SUCCESS',
            'observation_id': session.observations[-1]['observation_id']})
        self.assertFalse(any(r.get('accepted') for r in session.reports))
        self.assertEqual(session.write_count, 1)

    def test_primary_contract_requires_actual_partial_fault_attempt(self):
        spec = next(s for s in cases() if s['fault'] == 'partial')
        session, transport, _ = execute_fixture(spec, 'macro')
        for record in transport.records:
            record.pop('injected_partial', None)
        result = score(session, spec, transport, '{}', [], catalogue(), .025, transport.underlying.values)
        self.assertFalse(result['pass'])
        self.assertFalse(result['injected_fault_exercised'])

    def test_no_live_pilot_on_missing_or_failed_validation(self):
        import experiments.macro_focus_v2.gates as gate
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(gate, 'VALIDATION', Path(temp)), patch.object(gate, 'CONTINUATION', Path(temp) / 'absent'), patch.object(gate, 'FIRST_CONTINUATION', Path(temp) / 'also_absent'):
                with self.assertRaisesRegex(RuntimeError, 'not_finalized'):
                    require_validation()
                (Path(temp) / 'analysis.json').write_text(json.dumps({'engineering_gate': True, 'progression_gate': False}))
                with self.assertRaisesRegex(RuntimeError, 'gate_failed'):
                    require_validation()
