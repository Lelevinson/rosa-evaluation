from copy import deepcopy
import unittest
from unittest.mock import patch
from experiments.prompt_live_resume_v1.runner import (BASE, read, remaining_jobs, jobs, CombinedCounter)
from rosa_reliability import ControlledStop


class RepairContinuationTests(unittest.TestCase):
    def setUp(self):
        self.state = read(BASE / 'gazebo/siwc/checkpoint.json')
        self.schedule = jobs('gazebo')

    def test_select_only_censored_read_only_and_unstarted_cells(self):
        plan = remaining_jobs(self.state, self.schedule)
        self.assertEqual([j['original_schedule_index'] for j in plan], [4, 5, 6, 7, 8])
        self.assertEqual(plan[0]['reason'], 'censored_service_interruption_read_only')

    def test_genuine_completed_failures_are_never_replaced(self):
        self.state['trials'][0]['score']['pass'] = False
        self.assertNotIn(0, [j['original_schedule_index'] for j in remaining_jobs(self.state, self.schedule)])

    def test_any_prior_command_or_report_blocks_replay(self):
        for key, value in (('dispatch_count', 1), ('accepted_report_status', 'UNKNOWN')):
            altered = deepcopy(self.state)
            altered['trials'][-1]['score'][key] = value
            with self.assertRaises(RuntimeError):
                remaining_jobs(altered, self.schedule)
        with patch('experiments.prompt_live_resume_v1.runner.read',
                   return_value={'transport_records': [{'kind': 'trajectory_request'}]}):
            with self.assertRaisesRegex(RuntimeError, 'prior_command_dispatch'):
                remaining_jobs(self.state, self.schedule)

    def test_uncertain_teardown_and_bad_order_rejected(self):
        altered = deepcopy(self.state)
        altered['simulator_cleanup']['returncode'] = -9
        with self.assertRaises(RuntimeError):
            remaining_jobs(altered, self.schedule)
        altered = deepcopy(self.state)
        altered['trials'][0]['case'] = 'unexpected'
        with self.assertRaises(RuntimeError):
            remaining_jobs(altered, self.schedule)

    def test_additional_combined_and_time_bounds_before_dispatch(self):
        counter = CombinedCounter(13, 0)
        counter['calls'] = 53
        with self.assertRaises(ControlledStop):
            counter['calls'] = 54
        self.assertEqual(counter['calls'], 53)
        overall = CombinedCounter(70, 0)
        overall['calls'] = 72
        with self.assertRaises(ControlledStop):
            overall['calls'] = 73
        expired = CombinedCounter(13, 4500)
        with self.assertRaises(ControlledStop):
            expired['calls'] = 14
