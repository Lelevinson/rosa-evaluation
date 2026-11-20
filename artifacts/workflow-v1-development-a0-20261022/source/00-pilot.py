"""Real ROSA + scripted providers: execution feasibility, not model performance.

Run as a module from rosa-evaluation. Creates a new evidence directory and never
overwrites prior results. No model service, OAuth or simulator is contacted.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import time

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from rosa_reliability.terminal import AcceptedReportROSA
from rosa_reliability.workflow import WorkflowSession, make_workflow_tools
from experiments.reliability_v1.tracing import audit, trace_trial


TARGETS = {'/pilot_arm': {'yaw': .24, 'pitch': -.19}}
INITIAL = {'/pilot_arm': {'yaw': -.17, 'pitch': .28}}
SKILLS = {'inspect_station': TARGETS}
CASES = ('move', 'already', 'drop', 'missing_before', 'missing_after', 'reject', 'write_raises')


class FixtureTransport:
    requires_observation = True

    def __init__(self, fault='move'):
        self.fault = fault
        self.values = deepcopy(TARGETS if fault == 'already' else INITIAL)
        self.records = []
        self.writes = 0

    def read(self, node, names):
        self.records.append({'kind': 'read', 'node': node})
        if self.fault == 'missing_before' or (self.fault == 'missing_after' and self.writes):
            raise TimeoutError('injected_observation_unavailable')
        return {name: self.values[node][name] for name in names}

    def validate_write(self, node, values):
        if set(values) != set(TARGETS[node]) or any(abs(v) > .5 for v in values.values()):
            return 'complete bounded coordinate set required'
        if self.fault == 'reject':
            return 'injected_controller_unavailable'

    def write(self, node, values):
        self.writes += 1
        self.records.append({'kind': 'write', 'node': node})
        if self.fault == 'write_raises':
            self.values[node]['yaw'] = values['yaw']  # uncertain partial side effect
            raise TimeoutError('injected_uncertain_write')
        if self.fault != 'drop':
            self.values[node].update(values)
        return {'accepted': True, 'meaning': 'request acceptance only'}


def call(name, args):
    return AIMessage(content='', tool_calls=[{'name': name, 'args': args,
        'id': 'scripted-' + name, 'type': 'tool_call'}])


def responses(fault, program):
    planned = [call('select_skill', {'skill_id': 'inspect_station'})]
    if not program:
        planned.append(call('read_state', {'nodes': ['/pilot_arm']}))
        if fault not in ('already', 'missing_before'):
            planned.append(call('write_state', {'node_name': '/pilot_arm', 'values': TARGETS['/pilot_arm']}))
        if fault == 'write_raises':
            return planned
        planned.append(call('verify_outcome', {}))
    if fault == 'write_raises':
        return planned
    if program and fault in ('missing_before', 'reject'):
        planned.append(call('verify_outcome', {}))
    unknown = fault in ('missing_before', 'missing_after')
    values = {n: {k: None for k in group} for n, group in TARGETS.items()} if unknown else (
        INITIAL if fault in ('drop', 'reject') else TARGETS)
    status = 'UNKNOWN' if unknown else 'FAILURE' if fault in ('drop', 'reject') else 'SUCCESS'
    return [*planned, call('submit_report', {'status': status, 'observed_values': values})]


class Scripted(BaseChatModel):
    responses: list
    index: int = 0

    @property
    def _llm_type(self):
        return 'workflow-development-scripted-not-a-live-model'

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, **kwargs):
        if self.index >= len(self.responses):
            raise AssertionError('unexpected_extra_model_call_after_planned_terminal')
        response = self.responses[self.index]
        self.index += 1
        return ChatResult(generations=[ChatGeneration(message=response)])


class Meter(BaseCallbackHandler):
    def __init__(self):
        self.tool_starts, self.tool_ends, self.tool_errors = [], [], []

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_starts.append(str(kwargs['run_id']))

    def on_tool_end(self, output, **kwargs):
        self.tool_ends.append(str(kwargs['run_id']))

    def on_tool_error(self, error, **kwargs):
        self.tool_errors.append(str(kwargs['run_id']))


def run_case(fault, program, folder):
    transport, meter = FixtureTransport(fault), Meter()
    model = Scripted(responses=responses(fault, program))
    started = time.monotonic()
    metadata = {'run_id': folder.name, 'provider': 'scripted', 'program_managed': program,
                'case': fault, 'purpose': 'development_not_model_performance'}
    with trace_trial(metadata, folder / 'trace.json', phoenix=False) as (tracer, root):
        session = WorkflowSession(transport, SKILLS, program_managed=program, tracer=tracer)
        tools = make_workflow_tools(session)
        for tool in tools:
            tool.callbacks = [meter]
        agent = AcceptedReportROSA(2, model, terminal_session=session, tools=tools,
            load_default_tools=False, accumulate_chat_history=False)
        answer = agent.invoke('Execute the authorized inspection skill and report the observed outcome.')
    snap = session.snapshot()
    expected_status = ('UNKNOWN' if fault in ('missing_before', 'missing_after') else
                       'FAILURE' if fault in ('drop', 'reject') else 'SUCCESS')
    accepted = [r for r in snap['reports'] if r.get('accepted')]
    actual_goal = all(abs(transport.values[n][k] - v) <= .01 for n, group in TARGETS.items() for k, v in group.items())
    # Independent truth is available only here, outside the workflow/session.
    correct_report = bool(accepted and accepted[-1]['status'] == expected_status
        and all(accepted[-1]['observed_values'][n][k] is None if fault in ('missing_before', 'missing_after')
                else abs(accepted[-1]['observed_values'][n][k] - transport.values[n][k]) <= .01
                for n, group in TARGETS.items() for k in group))
    uncertain_stop = (fault == 'write_raises' and not accepted and transport.writes == 1
        and 'injected_uncertain_write' in answer)
    checks = {'expected_result': uncertain_stop if fault == 'write_raises' else correct_report,
              'at_most_one_write': transport.writes <= 1,
              'no_motion_without_observation': fault != 'missing_before' or transport.writes == 0,
              'native_cap': len(snap['operations']) <= 10, 'tool_cap': snap['tool_calls'] <= 16,
              'model_cap': model.index <= 8,
              'normal_terminal': uncertain_stop or bool(accepted and json.loads(answer)['report_accepted']),
              'trace_audit': audit(snap, folder / 'trace.json', meter)['pass']}
    result = {**metadata, 'pass': all(checks.values()), 'checks': checks, 'model_calls': model.index,
              'native_operations': len(snap['operations']), 'tool_attempts': snap['tool_calls'],
              'invalid_attempts': snap['validation_errors'], 'actual_goal_reached': actual_goal,
              'accepted_report_status': accepted[-1]['status'] if accepted else None,
              'program_native_operations': sum(e['actor'] == 'program' for e in snap['operations']),
              'wall_seconds_scripted_only': time.monotonic() - started,
              'answer': answer, 'snapshot': snap, 'transport_records': transport.records,
              'audit': audit(snap, folder / 'trace.json', meter)}
    (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *Path(__file__).resolve().parents[3].joinpath(
        'rosa-research/src/rosa_reliability').glob('*.py')]
    sources.append(Path(__file__).resolve().parents[2] / 'docs/WORKFLOW_V1_DEVELOPMENT_2026-10-22.md')
    manifest = {}
    for index, source in enumerate(sources):
        data = source.read_bytes()
        manifest[str(source)] = hashlib.sha256(data).hexdigest()
        destination = args.output / 'source' / f'{index:02d}-{source.name}'
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(data)
    (args.output / 'source-hashes.json').write_text(json.dumps(manifest, indent=2) + '\n')
    results = []
    for fault in CASES:
        for program in (False, True):
            folder = args.output / f'{fault}-{"program" if program else "model"}'
            folder.mkdir()
            results.append(run_case(fault, program, folder))
            (args.output / 'checkpoint.json').write_text(json.dumps({
                'status': 'RUNNING', 'completed': len(results), 'all_pass': all(r['pass'] for r in results)}, indent=2))
    summary = {'status': 'COMPLETE', 'purpose': 'scripted_execution_feasibility_not_live_model_evaluation',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'trials': len(results),
        'all_pass': all(r['pass'] for r in results),
        'results': [{k: r[k] for k in ('run_id', 'case', 'program_managed', 'pass', 'model_calls',
            'native_operations', 'tool_attempts', 'invalid_attempts', 'accepted_report_status', 'checks')} for r in results]}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.output / 'checkpoint.json').write_text(json.dumps({'status': 'COMPLETE', 'all_pass': summary['all_pass']}, indent=2))
    print(json.dumps(summary, indent=2))
    if not summary['all_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
