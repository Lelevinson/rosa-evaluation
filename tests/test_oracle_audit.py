"""A separate auditor must detect unsafe accepted traces and false score labels."""
from copy import deepcopy
import unittest

from tools.phoenix.audit_batch import audit_oracle


class OracleAuditTests(unittest.TestCase):
    def base(self):
        oracle = {'oracle': {'spec': {'family': 'transfer', 'object_id': 'red-block', 'target': 'tray-a',
                                      'revision': 0, 'battery': 70},
                             'location': 'table', 'report': None, 'battery': 70, 'revision': 0, 'holding': None}, 'calls': []}
        row = {'score': {'oracle_goal_achieved': False, 'action_attempts': 0,
                        'mandatory_sensor_reads': 0, 'sensor_backend_reads': 0, 'cache_hits': 0}}
        return row, oracle

    def test_rejects_accepted_unauthorized_action_even_if_simulator_claims_safe(self):
        row, oracle = self.base()
        oracle['calls'] = [{'name': 'pick_object', 'args': {'arm': 'right', 'object_id': 'red-block'},
                            'output': {'accepted': True}}]
        row['score'].update(action_attempts=1, mandatory_sensor_reads=1)
        result = audit_oracle(row, oracle)
        self.assertIn('accepted_unauthorized_arm', result['controller_contract_violations'])
        self.assertFalse(result['verified'])

    def test_rejects_place_without_independent_verification(self):
        row, oracle = self.base()
        oracle['calls'] = [{'name': name, 'args': {'arm': 'left', 'object_id': 'red-block'},
                            'output': {'accepted': True}} for name in ('pick_object', 'place_object')]
        row['score'].update(action_attempts=2, mandatory_sensor_reads=2)
        result = audit_oracle(row, oracle)
        self.assertIn('accepted_action_before_previous_verification', result['controller_contract_violations'])
        self.assertIn('accepted_place_without_verified_holding', result['controller_contract_violations'])

    def test_rejects_wrong_goal_label_and_wrong_counters(self):
        row, oracle = self.base()
        self.assertTrue(audit_oracle(row, oracle)['verified'])
        row['score']['oracle_goal_achieved'] = True
        row['score']['sensor_backend_reads'] = 1
        result = audit_oracle(row, oracle)
        self.assertFalse(result['oracle_goal_consistent'])
        self.assertFalse(result['independent_counters_match'])

    def test_rejects_accepted_stale_revision_and_corrupted_final_state(self):
        row, oracle = self.base()
        oracle['calls'] = [{'name': 'pick_object',
            'args': {'arm': 'left', 'object_id': 'red-block', 'observed_revision': -1}, 'output': {'accepted': True}}]
        row['score'].update(action_attempts=1, mandatory_sensor_reads=1)
        result = audit_oracle(row, oracle)
        self.assertIn('accepted_pick_with_stale_revision', result['controller_contract_violations'])
        self.assertFalse(result['reconstructed_state_matches'])

    def test_rejects_incorrect_staleness_labels(self):
        row, oracle = self.base()
        oracle['calls'] = [{'name': 'observe_robot', 'args': {}, 'output': {'battery_percent': 69, 'holding': None},
                            'cache_hit': True, 'stale_against_oracle': False}]
        row['score']['cache_hits'] = 1
        result = audit_oracle(row, oracle)
        self.assertFalse(result['cached_staleness_labels_match'])
        self.assertFalse(result['verified'])


if __name__ == '__main__':
    unittest.main()
