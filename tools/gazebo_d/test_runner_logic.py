"""Offline tests of experiments/gazebo_d/runner.py pure logic. No Gazebo, no ROS node, no model.

Run from the repo root (budget-cap test needs rosa_reliability, i.e. the D12 WSL research env):
  python -B tools/gazebo_d/test_runner_logic.py
"""
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from experiments.gazebo_d import runner as R  # noqa: E402

THREE = ['sol', 'qwen', 'ministral']


class RunnerLogic(unittest.TestCase):
    def test_admitted_rows_keep_order_and_drop_models(self):
        full = R.admitted_rows('heldout', R.json.loads((R.SCHEDULE / 'heldout.json').read_text())['models_full_set'])
        three = R.admitted_rows('heldout', THREE)
        self.assertEqual(len(full), 200)
        self.assertEqual(len(three), 120)
        self.assertEqual([r['seq'] for r in three], sorted(r['seq'] for r in three))
        self.assertEqual({r['model'] for r in three}, set(THREE))
        # every case has both arms for every admitted model
        for case in {r['case'] for r in three}:
            self.assertEqual(sum(r['case'] == case for r in three), 6)
        with self.assertRaises(ValueError):
            R.admitted_rows('heldout', ['gpt'])

    def test_whole_case_blocks(self):
        rows = R.admitted_rows('heldout', THREE)
        positions = [r['case_position'] for r in rows]
        self.assertEqual(positions, sorted(positions))   # a case finishes for all models before the next starts

    def test_ceilings(self):
        c = R.ceilings(R.admitted_rows('heldout', THREE))
        self.assertEqual(c['qwen'], {'trials': 40, 'request_cap': 323, 'reserve_cap': 3, 'seconds_cap': 28800})
        self.assertEqual(R.ceilings(R.admitted_rows('dev', THREE))['sol']['request_cap'], 99)

    def test_classify_resume(self):
        rows = R.admitted_rows('dev', THREE)[:3]
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / R.trial_name(rows[0])).mkdir()
            (Path(t) / R.trial_name(rows[0]) / 'result.json').write_text('{}')
            (Path(t) / R.trial_name(rows[1])).mkdir()
            s = R.classify(t, rows)
        self.assertEqual([s[r['seq']] for r in rows], ['DONE', 'INTERRUPTED', 'UNSTARTED'])

    def test_deadline(self):
        self.assertTrue(R.may_start(datetime(2026, 11, 23, 5, 59, tzinfo=R.TAIPEI)))
        self.assertFalse(R.may_start(datetime(2026, 11, 23, 6, 0, tzinfo=R.TAIPEI)))

    def test_reset_check(self):
        target = {'a': 0.0, 'b': .2}
        ok = {'trajectory_controller_active': True, 'joint_state_broadcaster_active': True, 'joint_sample_fresh': True}
        self.assertEqual(R.reset_check({'fault': None}, target, {'a': .01, 'b': .19}, ok), [])
        self.assertEqual(R.reset_check({'fault': None}, target, {'a': .05, 'b': .2}, ok), ['start_pose_not_confirmed'])
        inactive = dict(ok, trajectory_controller_active=False)
        self.assertEqual(R.reset_check({'fault': 'inactive'}, target, target, inactive), [])
        self.assertEqual(len(R.reset_check({'fault': 'inactive'}, target, target, ok)), 1)
        self.assertEqual(len(R.reset_check({'fault': None}, target, target, inactive)), 1)

    def test_budget_cap(self):
        try:
            from rosa_reliability.execution import ControlledStop
        except ImportError:
            self.skipTest('rosa_reliability not importable (run in the D12 WSL env)')
        b = R.DCampaignBudget(lambda s: None, request_cap=2, seconds_cap=100)
        b.reserve(); b.reserve()
        with self.assertRaises(ControlledStop):
            b.reserve()
        b2 = R.DCampaignBudget(lambda s: None, request_cap=9, seconds_cap=10)
        b2.active_seconds = 10
        with self.assertRaises(ControlledStop):
            b2.reserve()

    def test_m4_modules_import(self):
        try:
            import experiments.macro_m4.design as design  # noqa: F401
            from experiments.macro_m4.scoring import score  # noqa: F401
        except ImportError as e:
            self.skipTest(f'M4 modules need the WSL env: {e}')
        self.assertEqual(design.LIMITS['calls_per_task'], 8)
        cat = design.registry().catalogue()
        for c in R.load_cases().values():
            if c['skill']:
                self.assertIn(c['skill'], cat)
            self.assertIn(c['initial'], cat)


if __name__ == '__main__':
    unittest.main(verbosity=1)
