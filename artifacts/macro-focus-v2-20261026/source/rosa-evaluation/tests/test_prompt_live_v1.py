import json
from pathlib import Path
import tempfile
import unittest
from rosa_reliability.prompt_contract import bounded_contract, REQUIRED_TOOLS
from experiments.prompt_live_v1.design import jobs, LIMITS
from experiments.prompt_live_v1.runner import validate_actual_inputs


class LiveRepairCoordinatorTests(unittest.TestCase):
    def test_known_schedule_is_nine_unique_cells_not_held_out(self):
        plan = jobs('gazebo')
        self.assertEqual(len(plan), 9)
        self.assertEqual(len({(j['case']['id'], j['condition']) for j in plan}), 9)
        self.assertEqual({j['condition'] for j in plan}, {'model', 'macro', 'workflow'})
        self.assertEqual({j['case']['id'] for j in plan},
            {'already_home', 'missing_prerequisite', 'transient_after_motion'})
        self.assertEqual(LIMITS['backend_request_cap'], LIMITS['model_calls'] * len(plan))
        with self.assertRaises(ValueError):
            jobs('mock')

    def test_actual_input_guard_rejects_missing_goal_or_wrong_system(self):
        valid = [[{'role': 'system', 'content': bounded_contract(REQUIRED_TOOLS)},
                  {'role': 'human', 'content': 'user goal'}]]
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            validate_actual_inputs(valid, 'user goal', 1, folder)
            self.assertTrue(json.loads((folder / 'model-input-contract.json').read_text())['pass'])
            for prompt, goal, calls in ((valid, 'different goal', 1),
                    ([[{'role': 'system', 'content': 'old default'}]], 'user goal', 1),
                    (valid, 'user goal', 2)):
                with self.assertRaisesRegex(RuntimeError, 'actual_model_input_contract_mismatch'):
                    validate_actual_inputs(prompt, goal, calls, folder)
