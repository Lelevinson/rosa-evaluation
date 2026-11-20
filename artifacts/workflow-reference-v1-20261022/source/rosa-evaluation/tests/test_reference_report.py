"""Minimal common contract: trusted recorded values, model classification."""
import unittest
from langchain_core.tools import ToolException
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from experiments.workflow_v1.pilot import FixtureTransport, SKILLS, TARGETS


class ReferenceReportTests(unittest.TestCase):
    def setup_session(self, fault='move', program=False):
        session = ReferenceWorkflowSession(FixtureTransport(fault), SKILLS, program_managed=program)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        return session, tools

    def test_both_conditions_report_same_trusted_values_without_copying(self):
        for program in (False, True):
            session, tools = self.setup_session(program=program)
            if not program:
                tools['read_state'].invoke({'nodes': ['/pilot_arm']})
                tools['write_state'].invoke({'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']})
            observed = tools['verify_outcome'].invoke({})
            before = len(session.budget.events)
            result = tools['submit_report'].invoke({'status': 'SUCCESS', 'observation_id': observed['observation_id']})
            self.assertTrue(result['report_accepted'])
            self.assertEqual(result['observed_values'], TARGETS)
            self.assertEqual(len(session.budget.events), before)
            self.assertEqual(session.reports[-1]['values_supplied_by'], 'program_from_existing_observation')

    def test_unknown_is_preserved_and_cannot_be_promoted_to_success(self):
        session, tools = self.setup_session('missing_before', program=True)
        identifier = session.observations[-1]['observation_id']
        self.assertIn('unsupported_success', tools['submit_report'].invoke({'status': 'SUCCESS', 'observation_id': identifier}))
        accepted = tools['submit_report'].invoke({'status': 'UNKNOWN', 'observation_id': identifier})
        self.assertEqual(accepted['observed_values']['/pilot_arm'], {'yaw': None, 'pitch': None})
        self.assertTrue(accepted['report_accepted'])
        self.assertEqual(session.transport.writes, 0)

    def test_prewrite_reference_is_rejected_after_write(self):
        session, tools = self.setup_session()
        old = tools['read_state'].invoke({'nodes': ['/pilot_arm']})
        tools['write_state'].invoke({'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']})
        self.assertIn('stale_observation_reference', tools['submit_report'].invoke(
            {'status': 'FAILURE', 'observation_id': old['observation_id']}))
        self.assertFalse(session.reports)

    def test_reference_invalidated_even_when_write_raises_after_partial_effect(self):
        session, tools = self.setup_session('write_raises')
        old = tools['read_state'].invoke({'nodes': ['/pilot_arm']})
        with self.assertRaises(TimeoutError):
            tools['write_state'].invoke({'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']})
        self.assertIn('stale_observation_reference', tools['submit_report'].invoke(
            {'status': 'FAILURE', 'observation_id': old['observation_id']}))

    def test_new_read_invalidates_older_reference_without_a_write(self):
        session, tools = self.setup_session()
        first = tools['read_state'].invoke({'nodes': ['/pilot_arm']})
        tools['read_state'].invoke({'nodes': ['/pilot_arm']})
        self.assertIn('stale_observation_reference', tools['submit_report'].invoke(
            {'status': 'FAILURE', 'observation_id': first['observation_id']}))

    def test_cross_task_and_unknown_ids_are_rejected(self):
        left, p = self.setup_session('already', program=True)
        right, q = self.setup_session('already', program=True)
        for identifier in (left.observations[-1]['observation_id'], 'made-up'):
            self.assertIn('unknown_observation_reference', q['submit_report'].invoke(
                {'status': 'SUCCESS', 'observation_id': identifier}))
        self.assertFalse(right.reports)

    def test_incorrect_classification_is_recoverable_with_same_reference(self):
        session, tools = self.setup_session('drop', program=True)
        identifier = session.observations[-1]['observation_id']
        self.assertIn('outcome_classification_mismatch', tools['submit_report'].invoke(
            {'status': 'UNKNOWN', 'observation_id': identifier}))
        self.assertTrue(tools['submit_report'].invoke({'status': 'FAILURE', 'observation_id': identifier})['report_accepted'])

    def test_schema_refuses_manual_values_and_reference_failures_consume_no_native_work(self):
        session, tools = self.setup_session('already', program=True)
        before = len(session.budget.events)
        self.assertIn('schema_validation', tools['submit_report'].invoke(
            {'status': 'SUCCESS', 'observation_id': session.observations[-1]['observation_id'], 'observed_values': TARGETS}))
        self.assertEqual(len(session.budget.events), before)


if __name__ == '__main__': unittest.main()
