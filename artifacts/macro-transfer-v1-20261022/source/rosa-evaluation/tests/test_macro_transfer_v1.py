import unittest
from copy import deepcopy
from rosa_reliability.macro import MacroSession
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from experiments.macro_transfer_v1.design import cases, catalogue, PilotTransport, query, jobs
from experiments.macro_transfer_v1.scoring import score


def execute(spec, cls, program=True):
    transport = PilotTransport(spec)
    session = cls(transport, catalogue('mock'), program_managed=program, tolerance=.025)
    tools = {t.name: t for t in make_reference_tools(session)}
    response = tools['select_skill'].invoke({'skill_id': spec['skill']})
    if spec['fault'] == 'transient_after':
        response = tools['verify_outcome'].invoke({})
    observation = session.observations[-1]
    report = tools['submit_report'].invoke({'status': spec['expected'],
        'observation_id': observation['observation_id']})
    return session, transport, tools, report


class MacroTransferTests(unittest.TestCase):
    def test_macro_and_workflow_same_native_policy_for_all_cases(self):
        for spec in cases():
            with self.subTest(case=spec['id']):
                left = execute(spec, MacroSession)
                right = execute(spec, ReferenceWorkflowSession)
                self.assertEqual(left[1].records, right[1].records)
                self.assertEqual(left[3]['observed_values'], right[3]['observed_values'])
                self.assertEqual(left[3]['status'], right[3]['status'])
                self.assertTrue(left[3]['report_accepted'] and right[3]['report_accepted'])
                self.assertEqual(left[0].write_count, right[0].write_count)
                self.assertEqual(left[0].write_count, spec['required_dispatches'])
                self.assertEqual(left[0].tool_calls, right[0].tool_calls)

    def test_macro_and_workflow_identical_public_contract(self):
        for spec in cases():
            self.assertEqual(query(spec, 'macro', 'gazebo'), query(spec, 'workflow', 'gazebo'))
        sessions = [cls(PilotTransport(cases()[0]), catalogue('mock'), program_managed=True)
                    for cls in (MacroSession, ReferenceWorkflowSession)]
        schemas = [[(t.name, t.description, t.args_schema.model_json_schema())
                    for t in make_reference_tools(s)] for s in sessions]
        self.assertEqual(*schemas)

    def test_no_effect_without_attempt_fails_new_coverage_score(self):
        spec = cases()[3]
        transport = PilotTransport(spec)
        session = ReferenceWorkflowSession(transport, catalogue('mock'), program_managed=False)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        observed = tools['read_state'].invoke({'nodes': ['/ur5e']})
        tools['submit_report'].invoke({'status': 'FAILURE', 'observation_id': observed['observation_id']})
        session.events.append({'type': 'terminal'})
        result = score(session, spec, transport, '{}', [], catalogue('mock'), .025)
        self.assertTrue(result['legacy_outcome_contract_pass'])
        self.assertFalse(result['pass'])
        self.assertFalse(result['injected_fault_exercised'])

    def test_fault_is_exercised_only_with_correct_target_command(self):
        spec = cases()[3]
        session, transport, _, _ = execute(spec, MacroSession)
        session.events.append({'type': 'terminal'})
        result = score(session, spec, transport, '{}', [], catalogue('mock'), .025)
        self.assertTrue(result['pass'])
        transport.records[-2]['requested']['wrist_3_joint'] = 0.
        self.assertFalse(score(session, spec, transport, '{}', [], catalogue('mock'), .025)['pass'])

    def test_unknown_cannot_be_turned_into_success(self):
        spec = cases()[4]
        session = MacroSession(PilotTransport(spec), catalogue('mock'), program_managed=True)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        self.assertIn('unsupported_success', tools['submit_report'].invoke({
            'status': 'SUCCESS', 'observation_id': session.observations[-1]['observation_id']}))
        self.assertEqual(session.write_count, 0)

    def test_reselection_never_replays_and_old_evidence_stays_invalid(self):
        for cls in (MacroSession, ReferenceWorkflowSession):
            spec = cases()[5]
            session = cls(PilotTransport(spec), catalogue('mock'), program_managed=True)
            tools = {t.name: t for t in make_reference_tools(session)}
            tools['select_skill'].invoke({'skill_id': spec['skill']})
            old = session.observations[-1]['observation_id']
            self.assertIn('skill_already_selected', tools['select_skill'].invoke({'skill_id': spec['skill']}))
            fresh = tools['verify_outcome'].invoke({})
            self.assertIn('stale_observation_reference', tools['submit_report'].invoke({
                'status': 'SUCCESS', 'observation_id': old}))
            self.assertTrue(tools['submit_report'].invoke({'status': 'SUCCESS',
                'observation_id': fresh['observation_id']})['report_accepted'])
            self.assertEqual(session.write_count, 1)

    def test_new_schedule_balances_condition_position(self):
        schedule = jobs('gazebo')
        self.assertEqual(len(schedule), 18)
        for condition in ('model', 'macro', 'workflow'):
            self.assertEqual([sum(job['condition'] == condition for job in schedule[p::3])
                              for p in range(3)], [2, 2, 2])


if __name__ == '__main__':
    unittest.main()
