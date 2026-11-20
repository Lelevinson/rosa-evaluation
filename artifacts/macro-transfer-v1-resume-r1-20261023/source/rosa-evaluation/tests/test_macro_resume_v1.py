import unittest
from copy import deepcopy
from experiments.macro_resume_v1.runner import remaining_jobs, execution_scope, CombinedCounter, original
from rosa_reliability import ControlledStop


class ContinuationTests(unittest.TestCase):
    def state(self):
        return {'status': 'STOPPED', 'current_trial': None, 'simulator_cleanup': {'returncode': 0},
            'trials': [dict(case='done', condition='model', run_id='old-failure',
                inference={'usage_complete': True}, score={'pass': False}),
                dict(case='quota', condition='workflow', run_id='old-quota',
                inference={'usage_complete': False}, answer='subscription_sharing_usage_limit_exceeded',
                native_operations=0, tool_attempts=0)]}

    def schedule(self):
        return [dict(case={'id': name}, condition=condition) for name, condition in
                [('done', 'model'), ('quota', 'workflow'), ('new', 'macro')]]

    def test_keeps_completed_failures_and_selects_only_safe_remaining_cells(self):
        selected = remaining_jobs(self.state(), self.schedule())
        self.assertEqual([j['original_schedule_index'] for j in selected], [1, 2])
        self.assertEqual(selected[0]['prior_run_id'], 'old-quota')

    def test_refuses_prior_tool_activity_even_with_quota_error(self):
        for field in ('native_operations', 'tool_attempts'):
            state = self.state()
            state['trials'][-1][field] = 1
            with self.assertRaisesRegex(RuntimeError, 'uncertain_prior_attempt'):
                remaining_jobs(state, self.schedule())

    def test_refuses_active_or_unclean_original_batch(self):
        for change in ({'status': 'RUNNING'}, {'current_trial': {'id': 'uncertain'}},
                       {'simulator_cleanup': {'returncode': None}}):
            state = self.state()
            state.update(change)
            with self.assertRaises(RuntimeError):
                remaining_jobs(state, self.schedule())

    def test_execution_scope_restores_frozen_runner_after_exception(self):
        before = original.DESTINATION, original.jobs, original.verify_freeze
        with self.assertRaises(ValueError):
            with execution_scope([{'condition': 'macro'}]):
                self.assertEqual(original.jobs('gazebo'), [{'condition': 'macro'}])
                raise ValueError('scripted failure')
        self.assertEqual(before, (original.DESTINATION, original.jobs, original.verify_freeze))

    def test_combined_counter_stops_before_33rd_additional_request(self):
        counter = CombinedCounter(43, 500)
        for value in range(44, 76):
            counter['calls'] = value
        self.assertEqual(counter['calls'], 75)
        with self.assertRaises(ControlledStop):
            counter['calls'] = 76
        self.assertEqual(counter['calls'], 75)

    def test_original_combined_time_limit_still_applies(self):
        counter = CombinedCounter(43, 4501)
        with self.assertRaises(ControlledStop):
            counter['calls'] = 44


if __name__ == '__main__':
    unittest.main()
