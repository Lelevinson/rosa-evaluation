"""Synthetic-row tests for tools/gazebo_d/analysis.py. Zero model calls, no ROS, no Gazebo.

Run: python -I -B tools/gazebo_d/test_analysis.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis as A  # noqa: E402

CASES = A.load_cases()
HELD = [c for c in CASES.values() if c['split'] == 'heldout']


def row(model, case, arm, *, passed=True, calls=None, native=2, selected=None, error=None, last='RETURNED',
        operations=True):
    c = CASES[case]
    calls = calls if calls is not None else (2 if arm == 'macro' else 3)
    sel = selected if selected is not None else c['skill']
    return {'model': model, 'case': case, 'condition': arm, 'primary_pass': passed, 'phoenix_audit': {'pass': True},
            'error_type': error, 'wall_seconds': 10.0 * calls,
            'inference': {'calls': calls, 'decision_calls': calls, 'known_input_tokens': 100 * calls,
                          'known_output_tokens': 10 * calls, 'usage_complete': last == 'RETURNED',
                          'events': [{'status': 'RETURNED'}] * (calls - 1) + [{'status': last}]},
            'snapshot': {'selected_skill': sel, 'operations': [{'kind': 'x'}] if operations else []},
            'score': {'goal_correct': sel == c['skill'], 'selected_outcome_correct': passed, 'dispatch_violations': [],
                      'dispatches': c['writes'], 'injected_fault_exercised': None, 'native_operations': native},
            'offload': {'vram_fraction': [0.55]}}


def write_runs(root, rows):
    for i, r in enumerate(rows, 1):
        d = Path(root) / 'heldout' / f"{i:03d}-{r['case']}-{r['model']}-{r['condition']}"
        d.mkdir(parents=True)
        (d / 'result.json').write_text(json.dumps(r))


class Analysis(unittest.TestCase):
    def base(self):
        rows = []
        for c in HELD:
            for arm in ('primitives', 'macro'):
                rows.append(row('sol', c['id'], arm))
        return rows

    def run_rows(self, rows, reviews=None):
        with tempfile.TemporaryDirectory() as t:
            write_runs(t, rows)
            rp = None
            if reviews is not None:
                rp = Path(t) / 'reviews.json'
                rp.write_text(json.dumps(reviews))
            return A.analyze('heldout', t, rp)

    def test_all_pass(self):
        a = self.run_rows(self.base())['models']['sol']
        v = a['views_known_goal']
        self.assertEqual(v['primitives']['V2'], {'passes': 18, 'evaluable': 18})
        self.assertEqual(v['macro']['scheduled'], 18)
        p = a['predictions']
        self.assertEqual(p['D-P1']['matched_pairs'], 18)
        self.assertAlmostEqual(p['D-P1']['R'], 1 - 36 / 54, places=4)
        self.assertEqual(p['D-P1']['status'], 'Support')
        self.assertEqual(p['D-P2']['status'], 'Support')
        self.assertEqual(p['D-P3']['status'], 'Support')
        self.assertEqual(a['discordant_V2'], {'primitives_only': 0, 'macro_only': 0, 'exact_binomial_p_two_sided': None})
        self.assertEqual(len(a['ambiguous']), 4)
        self.assertTrue(all(x['status'] == 'PENDING' for x in a['ambiguous']))
        self.assertEqual(a['bootstrap']['groups'], 9)
        self.assertEqual(a['bootstrap']['pass_difference_macro_minus_primitives_95'], [0, 0])
        self.assertNotIn('D-P4', p)

    def test_macro_worse_by_three_is_against_and_binomial(self):
        rows = self.base()
        known = [c['id'] for c in HELD if c['kind'] != 'clarification'][:3]
        for r in rows:
            if r['case'] in known and r['condition'] == 'macro':
                r['primary_pass'] = False
                r['score']['selected_outcome_correct'] = False
        a = self.run_rows(rows)['models']['sol']
        self.assertEqual(a['predictions']['D-P3']['status'], 'Against')
        d = a['discordant_V2']
        self.assertEqual((d['primitives_only'], d['macro_only']), (3, 0))
        self.assertAlmostEqual(d['exact_binomial_p_two_sided'], 0.25)
        self.assertEqual(a['costs_matched_success']['pairs'], 15)

    def test_macro_worse_by_two_is_support(self):
        rows = self.base()
        known = [c['id'] for c in HELD if c['kind'] != 'clarification'][:2]
        for r in rows:
            if r['case'] in known and r['condition'] == 'macro':
                r['primary_pass'] = False
        self.assertEqual(self.run_rows(rows)['models']['sol']['predictions']['D-P3']['status'], 'Support')

    def test_weak_reduction_and_native_lower(self):
        rows = self.base()
        for r in rows:
            if r['condition'] == 'macro':
                r['inference']['calls'] = 3
                r['score']['native_operations'] = 1
        p = self.run_rows(rows)['models']['sol']['predictions']
        self.assertEqual(p['D-P1']['status'], 'Against')
        self.assertEqual(p['D-P2']['status'], 'Against')

    def test_censoring_rules_and_v3_flip(self):
        rows = self.base()
        known = [c['id'] for c in HELD if c['kind'] != 'clarification']
        # 3 macro failures (V2 passes_M=15 vs 18 -> Against); then censor 2 primitives so V2 P=16 -> Support,
        # V3 P=16 too; censor instead 2 primitives and check classes
        for r in rows:
            if r['case'] in known[:2] and r['condition'] == 'macro':
                r['primary_pass'] = False
            if r['case'] in known[2:3] and r['condition'] == 'macro':
                r.update(primary_pass=False, error_type='ConnectionError')
                r['inference']['events'][-1] = {'status': 'UNRETURNED'}
        a = self.run_rows(rows)['models']['sol']
        v = a['views_known_goal']['macro']
        self.assertEqual(v['V1']['censored'], 1)
        self.assertEqual(v['V2'], {'passes': 15, 'evaluable': 17})
        self.assertEqual(v['V3'], {'passes': 15, 'denominator': 18})
        self.assertEqual(a['predictions']['D-P3']['status'], 'Against')   # 15 < 18 - 2 in V2 and V3
        self.assertEqual(a['costs_matched_success']['pairs'], 15)

    def test_budget_end_is_not_censoring(self):
        r = row('sol', HELD[0]['id'], 'macro', passed=False, error='ControlledStop', last='UNRETURNED')
        self.assertIsNone(A.censoring(r))
        r = row('sol', HELD[0]['id'], 'macro', passed=False, error='ConnectionError', last='UNRETURNED', operations=False)
        self.assertEqual(A.censoring(r), 'PRE_OUTPUT')

    def test_compromised(self):
        rows = self.base()
        for r in rows[:10]:
            if CASES[r['case']]['kind'] != 'clarification':
                r.update(primary_pass=False, error_type='ConnectionError')
                r['inference']['events'][-1] = {'status': 'UNRETURNED'}
        p = self.run_rows(rows)['models']['sol']['predictions']
        self.assertTrue(all(x['status'] == 'Uninformative' for x in p.values()))

    def test_qwen_inspection_first_and_reviews(self):
        rows = []
        failing = {}
        movement = [c['id'] for c in HELD if c['kind'] == 'movement'][:4]
        for c in HELD:
            for arm in ('primitives', 'macro'):
                fail = c['id'] in movement and arm == 'primitives'
                rows.append(row('qwen', c['id'], arm, passed=not fail,
                                selected='ur5e.inspect_readiness' if fail else None))
        amb = [c['id'] for c in HELD if c['kind'] == 'clarification']
        reviews = {}
        with tempfile.TemporaryDirectory() as t:
            write_runs(t, rows)
            for d in (Path(t) / 'heldout').iterdir():
                if any(a in d.name for a in amb):
                    reviews[d.name] = {'pass': True, 'reason': 'asks which task', 'rater': 'test'}
            rp = Path(t) / 'reviews.json'
            rp.write_text(json.dumps(reviews))
            a = A.analyze('heldout', t, rp)['models']['qwen']
        p4 = a['predictions']['D-P4']
        self.assertEqual((p4['failed'], p4['inspection_first'], p4['status'], p4['preliminary']), (4, 4, 'Support', False))
        self.assertTrue(all(x['status'] is True for x in a['ambiguous']))
        self.assertEqual(a['selection_execution']['primitives']['selection_correct'], 14)

    def test_few_pairs_uninformative(self):
        rows = [r for r in self.base() if r['case'] in [c['id'] for c in HELD][:4]]   # 4 known-goal pairs < 5
        p = self.run_rows(rows)['models']['sol']['predictions']
        self.assertEqual(p['D-P1']['status'], 'Uninformative')
        self.assertEqual(self.run_rows(rows)['models']['sol']['views_known_goal']['macro']['unstarted'], 14)

    def test_binomial(self):
        self.assertAlmostEqual(A.binom_two_sided(5, 0), 0.0625)
        self.assertAlmostEqual(A.binom_two_sided(2, 2), 1.0)
        self.assertIsNone(A.binom_two_sided(0, 0))

    def test_deterministic_bootstrap(self):
        rows = self.base()
        rows[1]['primary_pass'] = False
        a = self.run_rows(rows)['models']['sol']['bootstrap']
        b = self.run_rows(rows)['models']['sol']['bootstrap']
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main(verbosity=1)
