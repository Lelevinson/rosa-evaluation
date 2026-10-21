"""Analysis checks: failures cannot earn speed credit or pass an empty screen."""
import unittest

from experiments.stage4_batching.final_report import batching_comparison


def row(policy, repetition, *, success=True, strict=True, seconds=10, cli=4):
    return {'scenario_id': 'fixture', 'repetition': repetition, 'policy': policy,
            'combined_pass': success, 'strict_contract_pass': strict,
            'wall_seconds': seconds, 'cli_commands': cli, 'server_rpcs': cli}


class FinalAnalysisTests(unittest.TestCase):
    def test_no_pairs_cannot_satisfy_retention(self):
        self.assertFalse(batching_comparison([])['screening_retention_criterion_met'])

    def test_early_failed_exit_is_not_a_speedup(self):
        rows = [row('model_selected', 0), row('amortized_batching', 0, success=False, strict=False, seconds=.1, cli=0)]
        result = batching_comparison(rows)
        self.assertFalse(result['screening_retention_criterion_met'])
        self.assertEqual(result['both_successful_pairs'], 0)
        self.assertIsNone(result['successful_pair_relative_reduction']['wall_seconds'])

    def test_a_benefit_requires_consistent_repeat_direction(self):
        rows = [row('model_selected', i) for i in (0, 1)]
        rows += [row('amortized_batching', 0, seconds=1, cli=1), row('amortized_batching', 1, seconds=11, cli=5)]
        self.assertFalse(batching_comparison(rows)['screening_retention_criterion_met'])

    def test_positive_matched_work_benefit_is_distinct_from_time(self):
        rows = [row('model_selected', i) for i in (0, 1)]
        rows += [row('amortized_batching', i, cli=3) for i in (0, 1)]
        result = batching_comparison(rows)
        self.assertTrue(result['screening_retention_criterion_met'])
        self.assertEqual(result['successful_pair_relative_reduction']['wall_seconds'], 0)
        self.assertEqual(result['successful_pair_relative_reduction']['cli_commands'], .25)


if __name__ == '__main__':
    unittest.main()
