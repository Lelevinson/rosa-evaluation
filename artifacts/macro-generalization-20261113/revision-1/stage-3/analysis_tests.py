"""Analysis-tool tests only; these are not independent scorer-review cases."""
from copy import deepcopy
import gzip
import json
import unittest
from common import ROOT, dev_rows, read, write
from censoring import annotate, censor_class, pair_gap

class AnalysisTests(unittest.TestCase):
    def test_original_false_flags_unchanged(self):
        row = next(r for r in dev_rows() if r['id'] == 'G1r1-dev-012-primitives')
        original = deepcopy(row)
        result = annotate(row)
        self.assertEqual(result['censor_class'], 'INFRA_CENSORED_PRE_OUTPUT')
        self.assertTrue(all(v == 'NOT_EVALUABLE' for v in result['component_columns'].values()))
        self.assertEqual(row, original)
        self.assertIs(row['score']['selection_correct'], False)
    def test_post_action_and_world_record_retained(self):
        row = deepcopy(dev_rows()[0])
        row['analysis_failure_observation'] = dict(surface='IN_STREAM', completed_response_in_failed_call=False,
            tool_executions_before_failure=1, native_operations_before_failure=1, dispatches_before_failure=0)
        observer = deepcopy(row['observer_records'])
        self.assertEqual(annotate(row)['censor_class'], 'INFRA_CENSORED_POST_ACTION')
        self.assertEqual(row['observer_records'], observer)
    def test_explicit_pre_output(self):
        row = deepcopy(dev_rows()[0])
        row['analysis_failure_observation'] = dict(surface='HTTP', completed_response_in_failed_call=False)
        self.assertEqual(censor_class(row), 'INFRA_CENSORED_PRE_OUTPUT')
    def test_completed_response_not_censored_by_flag(self):
        row = deepcopy(dev_rows()[0])
        row['analysis_failure_observation'] = dict(surface='IN_STREAM', completed_response_in_failed_call=True)
        self.assertIsNone(censor_class(row))
    def test_unclassified_recovery_fails_closed(self):
        row = deepcopy(dev_rows()[0])
        row.update(error=None, infrastructure_recovered=True)
        row['inference']['events'] = [dict(status='EXTERNAL_FAILURE')]
        with self.assertRaises(ValueError):
            censor_class(row)
    def test_pair_gap_threshold(self):
        first = [dict(start_time='2026-11-14T00:00:00Z')]
        self.assertFalse(pair_gap(first, [dict(start_time='2026-11-14T00:30:00Z')])['flagged'])
        self.assertTrue(pair_gap(first, [dict(start_time='2026-11-14T00:30:01Z')])['flagged'])
    def test_all_bootstrap_draws_retained(self):
        analysis = read(ROOT/'analysis/dev-analysis.json')
        with gzip.open(ROOT/'analysis/dev-bootstrap-draws.jsonl.gz', 'rt') as stream:
            draws = [json.loads(line) for line in stream]
        self.assertEqual(len(draws), 10000)
        self.assertEqual([d['draw'] for d in draws], list(range(10000)))
        self.assertTrue(all(len(d['group_indices']) == analysis['bootstrap']['template_groups'] for d in draws))
        for key, value in analysis['bootstrap']['intervals'].items():
            self.assertEqual(sum(d['metrics'][key] is None for d in draws), value['empty_draws'])
    def test_reproduced_views(self):
        result = read(ROOT/'analysis/dev-analysis.json')
        self.assertEqual(result['operational_views']['primitives']['V2_denominator'], 17)
        self.assertEqual(result['operational_views']['primitives']['V3_denominator'], 18)
        self.assertEqual(result['operational_views']['macro']['V2_denominator'], 18)
        self.assertEqual(len(result['excluded_pairs']), 1)

if __name__ == '__main__':
    import io
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AnalysisTests))
    (ROOT/'analysis/unit-tests.log').write_text(stream.getvalue(), encoding='utf-8')
    write('analysis/unit-tests.json', dict(passed=result.wasSuccessful(), methods=result.testsRun,
        errors=len(result.errors), failures=len(result.failures), model_requests=0,
        independent_scorer_review=False))
    print({'pass': result.wasSuccessful(), 'methods': result.testsRun})
    raise SystemExit(0 if result.wasSuccessful() else 1)
