import unittest
from experiments.macro_capabilities_v2.m3 import TASKS, trial_allowance


class M2M3BoundsTests(unittest.TestCase):
    def test_external_trial_alarm_cannot_outlive_backend_allowance(self):
        self.assertEqual(trial_allowance(0, now=0), 180)
        self.assertEqual(trial_allowance(0, now=710), 10)
        for now in (720, 721):
            with self.assertRaises(RuntimeError): trial_allowance(0, now=now)

    def test_read_only_and_ambiguous_tasks_cannot_authorize_motion(self):
        for task in TASKS:
            if task['id'] in ('inspect', 'clarify'):
                self.assertEqual(task['allowed'], ['ur5e.inspect_readiness'])
                self.assertEqual(task['writes'], 0)
        movement = next(t for t in TASKS if t['id'] == 'move')
        self.assertIsNone(movement['allowed'])
        self.assertEqual(movement['writes'], 1)


if __name__ == '__main__': unittest.main()
