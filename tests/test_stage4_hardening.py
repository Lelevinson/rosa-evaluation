"""Budget hardening is tested separately; it does not rewrite study execution."""
import unittest

from tests.test_stage4_batching import fixture, FakeEnvironment, COSTS
from experiments.stage4_batching.bounded_gateway import BoundedGateway


class NativeBudgetTests(unittest.TestCase):
    def test_25th_write_is_blocked_before_native_execution(self):
        spec = fixture('write_report_verify')
        environment = FakeEnvironment(spec)
        gateway = BoundedGateway(spec, 'model_selected', environment.invoke, COSTS)
        for _ in range(24):
            gateway.call('ros2_param_set', node_name='/jtvr_alpha', param_name='alpha', param_value='20')
        self.assertEqual(len(environment.calls), 24)
        rejected = gateway.call('ros2_param_set', node_name='/jtvr_alpha', param_name='alpha', param_value='20')
        self.assertIn('error', rejected)
        self.assertEqual(len(environment.calls), 24)
        self.assertEqual(len(gateway.events), 24)

    def test_report_remains_available_when_execution_budget_is_exhausted(self):
        spec = fixture('one_parameter')
        environment = FakeEnvironment(spec)
        gateway = BoundedGateway(spec, 'model_selected', environment.invoke, COSTS)
        gateway.max_native_reads = 0
        rejected = gateway.call('ros2_param_get', node_name='/jtvr_alpha', param_name='alpha')
        self.assertIn('error', rejected)
        accepted = gateway.call('submit_parameter_report', outcome='unknown', observed_values={}, acknowledged_details=[])
        self.assertTrue(accepted['report_recorded'])
        self.assertEqual(environment.calls, [])


if __name__ == '__main__':
    unittest.main()
