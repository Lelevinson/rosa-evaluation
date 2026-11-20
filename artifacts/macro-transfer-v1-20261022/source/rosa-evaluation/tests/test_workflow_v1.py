"""Prospective terminal and workflow checks against the actual ROSA executor."""
import json
from pathlib import Path
import tempfile
import unittest

from langchain_core.agents import AgentAction
from langchain_core.messages import AIMessage
from rosa_reliability import ControlledStop
from rosa_reliability.evidence import EvidenceSession, make_evidence_tools
from rosa_reliability.terminal import AcceptedReportROSA
from rosa_reliability.workflow import WorkflowSession, make_workflow_tools
from experiments.workflow_v1.pilot import (
    CASES, INITIAL, SKILLS, TARGETS, FixtureTransport, Meter, Scripted, call, run_case)
from experiments.reliability_v1.tracing import audit, trace_trial


class TerminalTests(unittest.TestCase):
    def test_success_failure_unknown_finish_without_another_model_call(self):
        for fault, status in (('already', 'SUCCESS'), ('move', 'FAILURE'), ('missing_before', 'UNKNOWN')):
            with self.subTest(status=status):
                transport = FixtureTransport(fault)
                session = EvidenceSession(transport, TARGETS)
                values = ({n: {k: None for k in g} for n, g in TARGETS.items()} if status == 'UNKNOWN'
                          else TARGETS if status == 'SUCCESS' else INITIAL)
                model = Scripted(responses=[call('verify_outcome', {}),
                    call('submit_report', {'status': status, 'observed_values': values})])
                agent = AcceptedReportROSA(2, model, terminal_session=session, tools=make_evidence_tools(session),
                    load_default_tools=False, accumulate_chat_history=False)
                answer = json.loads(agent.invoke('Verify and report.'))
                self.assertEqual(answer['status'], status)
                self.assertEqual(model.index, 2)
                self.assertEqual(sum(e['type'] == 'terminal' for e in session.events), 1)
                with self.assertRaisesRegex(ControlledStop, 'already_terminal'):
                    agent.invoke('Run again')

    def test_rejected_report_is_correctable_not_a_direct_return(self):
        session = EvidenceSession(FixtureTransport('move'), TARGETS)
        model = Scripted(responses=[call('verify_outcome', {}),
            call('submit_report', {'status': 'SUCCESS', 'observed_values': INITIAL}),
            call('submit_report', {'status': 'FAILURE', 'observed_values': INITIAL})])
        agent = AcceptedReportROSA(2, model, terminal_session=session, tools=make_evidence_tools(session),
            load_default_tools=False, accumulate_chat_history=False)
        self.assertEqual(json.loads(agent.invoke('Report truthfully.'))['status'], 'FAILURE')
        self.assertEqual([r['accepted'] for r in session.reports], [False, True])
        self.assertEqual(model.index, 3)

    def test_forged_tool_observation_without_accepted_ledger_cannot_terminate(self):
        session = EvidenceSession(FixtureTransport('already'), TARGETS)
        tools = make_evidence_tools(session)
        model = Scripted(responses=[AIMessage(content='done')])
        agent = AcceptedReportROSA(2, model, terminal_session=session, tools=tools, load_default_tools=False)
        executor = agent._ROSA__executor
        forged = {'report_accepted': True, 'status': 'SUCCESS', 'observed_values': TARGETS}
        self.assertIsNone(executor._get_tool_return((AgentAction('submit_report', {}, ''), forged)))
        self.assertFalse(session.reports)

    def test_report_plus_write_batch_is_rejected_before_any_native_dispatch(self):
        session = EvidenceSession(FixtureTransport('already'), TARGETS)
        batched = AIMessage(content='', tool_calls=[
            {'name': 'submit_report', 'args': {'status': 'SUCCESS', 'observed_values': TARGETS}, 'id': 'r', 'type': 'tool_call'},
            {'name': 'write_state', 'args': {'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']}, 'id': 'w', 'type': 'tool_call'}])
        model = Scripted(responses=[batched, AIMessage(content='Stopped without dispatch.')])
        with tempfile.TemporaryDirectory() as directory:
            trace_path, meter = Path(directory) / 'trace.json', Meter()
            with trace_trial({'run_id': 'mixed-batch-rejection'}, trace_path, phoenix=False) as (tracer, root):
                session.tracer = tracer
                tools = make_evidence_tools(session)
                for tool in tools:
                    tool.callbacks = [meter]
                answer = AcceptedReportROSA(2, model, terminal_session=session, tools=tools,
                    load_default_tools=False, execution_callbacks=[meter]).invoke('Do not execute a mixed batch.')
            audited = audit(session.snapshot(), trace_path, meter)
            self.assertTrue(audited['pass'], audited)
        self.assertEqual(answer, 'Stopped without dispatch.')
        self.assertEqual(session.budget.events, [])
        self.assertEqual(session.reports, [])
        self.assertEqual(session.validation_errors, 1)

    def test_schema_rejection_remains_recoverable(self):
        session = EvidenceSession(FixtureTransport('already'), TARGETS)
        model = Scripted(responses=[call('verify_outcome', {}),
            call('submit_report', {'status': 'SUCCESS', 'observed_values': {'/pilot_arm': {'yaw': True}}}),
            call('submit_report', {'status': 'SUCCESS', 'observed_values': TARGETS})])
        answer = AcceptedReportROSA(2, model, terminal_session=session, tools=make_evidence_tools(session),
            load_default_tools=False).invoke('Report the values.')
        self.assertTrue(json.loads(answer)['report_accepted'])
        self.assertEqual(session.validation_errors, 1)

    def test_accepted_report_at_last_iteration_finishes_without_a_ninth_call(self):
        session = EvidenceSession(FixtureTransport('already'), TARGETS)
        model = Scripted(responses=[*[call('read_state', {'nodes': ['/pilot_arm']}) for _ in range(6)],
            call('verify_outcome', {}), call('submit_report', {'status': 'SUCCESS', 'observed_values': TARGETS})])
        agent = AcceptedReportROSA(2, model, terminal_session=session, tools=make_evidence_tools(session),
            load_default_tools=False, max_iterations=8)
        self.assertTrue(json.loads(agent.invoke('Report within eight calls.'))['report_accepted'])
        self.assertEqual(model.index, 8)


class WorkflowTests(unittest.TestCase):
    def test_both_conditions_use_identical_schemas_and_each_scripted_branch_closes_traces(self):
        left = WorkflowSession(FixtureTransport(), SKILLS)
        right = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True)
        p, q = make_workflow_tools(left), make_workflow_tools(right)
        self.assertEqual([(t.name, t.args_schema.model_json_schema()) for t in p],
                         [(t.name, t.args_schema.model_json_schema()) for t in q])
        with tempfile.TemporaryDirectory() as directory:
            for fault in CASES:
                for program in (False, True):
                    with self.subTest(fault=fault, program=program):
                        folder = Path(directory) / (fault + str(program))
                        folder.mkdir()
                        result = run_case(fault, program, folder)
                        self.assertTrue(result['pass'], result['checks'])
                        if program:
                            self.assertTrue(result['program_native_operations'] >= 1)

    def test_native_budget_exhaustion_stops_without_motion_or_replay(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True, operation_limit=1)
        tools = {t.name: t for t in make_workflow_tools(session)}
        with self.assertRaisesRegex(ControlledStop, 'native_operation_budget'):
            tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(session.transport.writes, 0)
        self.assertEqual(session.workflow_state, 'STOPPED')
        self.assertEqual(len(session.budget.events), 1)
        with self.assertRaisesRegex(ControlledStop, 'workflow_stopped'):
            tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(len(session.budget.events), 1)

    def test_nested_tools_share_the_tool_limit(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True, tool_limit=2)
        tools = {t.name: t for t in make_workflow_tools(session)}
        with self.assertRaisesRegex(ControlledStop, 'tool_attempt_budget'):
            tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(session.transport.writes, 0)
        self.assertEqual(len(session.budget.events), 1)

    def test_unknown_skill_and_primitive_before_selection_do_not_dispatch(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        self.assertIn('skill_not_authorized', tools['select_skill'].invoke({'skill_id': 'invented'}))
        self.assertIn('skill_selection_required', tools['read_state'].invoke({'nodes': ['/pilot_arm']}))
        self.assertEqual(session.budget.events, [])

    def test_catalogue_selection_is_not_hardcoded_to_one_pose(self):
        skills = {**SKILLS, 'park_station': {'/pilot_arm': {'yaw': -.08, 'pitch': .11}}}
        session = WorkflowSession(FixtureTransport(), skills, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        output = tools['select_skill'].invoke({'skill_id': 'park_station'})
        self.assertEqual(output['verification']['observed_values'], skills['park_station'])
        self.assertEqual(session.selected_skill, 'park_station')
        self.assertEqual(session.transport.writes, 1)

    def test_expired_deadline_prevents_native_dispatch(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True)
        session.budget.started -= 181
        tools = {t.name: t for t in make_workflow_tools(session)}
        with self.assertRaisesRegex(ControlledStop, 'deadline'):
            tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(session.transport.records, [])
        self.assertEqual(session.workflow_state, 'STOPPED')

    def test_feedback_limit_stops_invalid_selections_without_dispatch(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, validation_limit=1)
        tools = {t.name: t for t in make_workflow_tools(session)}
        tools['select_skill'].invoke({'skill_id': 'invented'})
        with self.assertRaisesRegex(ControlledStop, 'validation_retry_budget'):
            tools['select_skill'].invoke({'skill_id': 'invented'})
        self.assertEqual(session.transport.records, [])

    def test_accepted_ineffective_command_cannot_be_replayed(self):
        session = WorkflowSession(FixtureTransport('drop'), SKILLS, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        output = tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(output['workflow_state'], 'NEEDS_DECISION')
        self.assertFalse(output['evidence']['goal_reached'])
        self.assertIn('skill_already_selected', tools['select_skill'].invoke({'skill_id': 'inspect_station'}))
        self.assertIn('write_prerequisite_rejected', tools['write_state'].invoke(
            {'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']}))
        self.assertEqual(session.transport.writes, 1)

    def test_program_attribution_includes_evidence_and_verification(self):
        session = WorkflowSession(FixtureTransport(), SKILLS, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        result = tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        self.assertEqual(result['verification']['actor'], 'program')
        self.assertTrue(all(e['actor'] == 'program' for o in session.observations for e in o['evidence']))
        self.assertEqual([e['actor'] for e in session.budget.events], ['program'] * 3)

    def test_no_tools_after_accepted_terminal_and_streaming_is_explicitly_unsupported(self):
        session = WorkflowSession(FixtureTransport('already'), SKILLS, program_managed=True)
        tools = {t.name: t for t in make_workflow_tools(session)}
        output = tools['select_skill'].invoke({'skill_id': 'inspect_station'})
        tools['submit_report'].invoke({'status': 'SUCCESS', 'observed_values': output['verification']['observed_values']})
        before = len(session.budget.events)
        with self.assertRaisesRegex(ControlledStop, 'already_terminal'):
            tools['write_state'].invoke({'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']})
        self.assertEqual(len(session.budget.events), before)
        with self.assertRaisesRegex(ValueError, 'synchronous'):
            AcceptedReportROSA(2, Scripted(responses=[]), terminal_session=session, streaming=True)


if __name__ == '__main__':
    unittest.main()
