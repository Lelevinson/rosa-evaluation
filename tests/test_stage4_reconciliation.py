"""Saved recovery evidence must not excuse unrelated or larger trace gaps."""
from copy import deepcopy
import json
import unittest

from experiments.stage4_batching.reconcile_audit import guard_gap_checks
from experiments.stage4_batching.runner import CAMPAIGN
from experiments.stage4_batching.trace_accounting import counts
from tools.phoenix.inspect_trace import summarize


class GuardTraceGapTests(unittest.TestCase):
    def setUp(self):
        folder = CAMPAIGN / 'ollama/trials/40f610ee-29c2-4bbb-8a03-e53262118338'
        self.row = json.loads((folder / 'result.json').read_text())
        self.evidence = json.loads((folder / 'evidence.json').read_text())
        self.trace = json.loads((folder / 'trace.json').read_text())
        self.summary = summarize(self.trace['spans'])
        self.actors = counts(self.trace['spans'])

    def accounted(self):
        return guard_gap_checks(self.row, self.evidence, self.trace, self.summary, self.actors)['accounted']

    def test_saved_guard_gap_has_cross_record_support(self):
        self.assertTrue(self.accounted())

    def test_two_missing_spans_are_not_accepted(self):
        self.actors['model_tool_spans'] -= 1
        self.assertFalse(self.accounted())

    def test_raw_argument_tampering_is_not_accepted(self):
        self.row['raw_model_tool_calls'][-1]['args']['arm'] = 'right'
        self.assertFalse(self.accounted())

    def test_missing_attributed_report_is_not_accepted(self):
        self.evidence['calls'] = [c for c in self.evidence['calls'] if c['actor'] != 'orchestrator']
        self.assertFalse(self.accounted())

    def test_nonintervention_trial_is_not_accepted(self):
        self.row['intervention'] = 'original'
        self.assertFalse(self.accounted())


if __name__ == '__main__':
    unittest.main()
