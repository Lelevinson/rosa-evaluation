from copy import deepcopy
import unittest
from unittest.mock import patch
from experiments.prompt_live_resume_v2 import runner
from experiments.ur5e_transfer_v1 import arm


class SetupAmendmentTests(unittest.TestCase):
    def test_validated_three_cold_starts_are_required(self):
        self.assertTrue(runner.verify_setup()['pass'])
        with patch.object(runner, 'read', return_value={'pass': False}):
            with self.assertRaisesRegex(RuntimeError, 'cold_start_gate_failed'):
                runner.verify_setup()

    def test_R2_rejects_R1_if_it_used_even_one_model_request(self):
        real_read = runner.read
        state = deepcopy(real_read(runner.FIRST / 'gazebo/siwc/checkpoint.json'))
        state['total_model_calls'] = 1
        def mocked(path):
            return state if path == runner.FIRST / 'gazebo/siwc/checkpoint.json' else real_read(path)
        with patch.object(runner.r1, 'verify_freeze', return_value=None), patch.object(runner, 'read', side_effect=mocked):
            with self.assertRaisesRegex(RuntimeError, 'zero_inference_setup_abort'):
                runner.verify_original()

    def test_setup_scope_restores_every_setting_even_after_exception(self):
        previous = (runner.original.DESTINATION, runner.original.jobs, runner.original.verify_freeze, arm.ArmSimulator)
        with self.assertRaisesRegex(RuntimeError, 'sentinel'):
            with runner.execution_scope([]):
                self.assertIs(arm.ArmSimulator, runner.HomeSpawnSimulator)
                self.assertEqual(runner.original.jobs('gazebo'), [])
                raise RuntimeError('sentinel')
        self.assertEqual(previous, (runner.original.DESTINATION, runner.original.jobs,
                                   runner.original.verify_freeze, arm.ArmSimulator))
