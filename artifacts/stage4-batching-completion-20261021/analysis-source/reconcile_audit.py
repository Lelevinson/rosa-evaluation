"""Post-run reconciliation of a specific recovery-stop tracing gap.

Preserves the failed frozen auditor and supervisor outputs. This never invents
a missing span or converts task failures to passes. No live services are used.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .audit import batching_check
from .protocol import verify
from .runner import CAMPAIGN
from .trace_accounting import counts
from ..phase4.audit import check as reliability_check
from tools.phoenix.inspect_trace import summarize


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard_gap_checks(row, evidence, trace, summary, actors):
    """Require independent agreement on the suppressed final dispatch and stop."""
    raw = row['raw_model_tool_calls']
    world_model = [c for c in evidence['calls'] if c['actor'] == 'model']
    orchestrator = [c for c in evidence['calls'] if c['actor'] == 'orchestrator']
    latest_pose = verification = last_accepted = None
    for call in world_model:
        if call['name'] == 'locate_object':
            latest_pose = call['output']
        elif call['name'] == 'verify_goal':
            verification = call['output']
        elif call['name'] in ('pick_object', 'place_object'):
            verification = None
            if call['output'].get('accepted'):
                last_accepted = call['name']
    unknown = bool(latest_pose and latest_pose.get('status') == 'UNKNOWN')
    failed_pick = bool(last_accepted == 'pick_object' and verification
        and verification.get('execution_terminal') and not verification.get('holding'))
    last = raw[-1] if raw else {'name': None, 'args': {}}
    repeat = any(c['name'] == last['name'] and all(c['args'].get(key) == last['args'].get(key)
        for key in ('object_id', 'arm')) for c in raw[:-1])
    requested_names = summary['llm_requested_tools']
    spans = sorted((s for s in trace['spans'] if s['span_kind'] == 'LLM'), key=lambda s: s['start_time'])
    attrs = spans[-1]['attributes'] if spans else {}
    prefix = 'llm.output_messages.0.message.tool_calls.0.tool_call.'
    try:
        last_trace_args = json.loads(attrs.get(prefix + 'function.arguments', 'null'))
    except (TypeError, ValueError):
        last_trace_args = None
    expected_orchestrator_names = ([] if verification else ['verify_goal']) + ['submit_report']
    checks = {
        'bounded_recovery_flag': row['stage'] == 'reliability'
            and row['intervention'] == 'bounded_recovery' and row['orchestrator_recovery'],
        'one_guard_and_system_report': evidence['score']['guard_stops'] == 1
            and evidence['score']['system_reports'] == 1,
        'guard_predicate_reconstructed': repeat and (unknown or failed_pick)
            and last['name'] in ('pick_object', 'place_object'),
        'model_world_calls_are_exact_prefix': [(c['name'], c['args']) for c in world_model]
            == [(c['name'], c['args']) for c in raw[:-1]],
        'orchestrator_tail': [c['name'] for c in orchestrator] == expected_orchestrator_names
            and evidence['calls'][-len(orchestrator):] == orchestrator if orchestrator else False,
        'attributed_report_arguments': bool(orchestrator) and orchestrator[-1]['args'] == {
            'outcome': 'unknown' if unknown else 'failure', 'battery_percent': -1},
        'raw_and_trace_requests_agree': requested_names == [c['name'] for c in raw]
            and attrs.get(prefix + 'function.name') == last['name']
            and attrs.get(prefix + 'id') == last.get('id') and last_trace_args == last['args'],
        'callback_dispatch_count': row['model_metrics']['tool_dispatches'] == len(raw),
        'exactly_one_final_tool_span_missing': actors['native_tool_spans'] == 0
            and actors['model_tool_spans'] == len(raw) - 1
            and [c['name'] for c in summary['tools_in_start_order']] == requested_names[:-1],
        'all_recorded_spans_closed_and_model_count_matches': summary['trace_complete']
            and summary['llm_calls'] == row['model_metrics']['calls'],
    }
    return {'accounted': all(checks.values()), 'checks': checks,
        'missing_tool_spans': 1, 'missing_dispatch': last,
        'full_tool_span_coverage': False}


def review_campaign():
    frozen = verify()
    supervisor = read(CAMPAIGN / 'supervisor-status.json')
    if any(supervisor['steps'][step]['status'] != 'PASSED' for step in ('hosted', 'audit-hosted', 'local')):
        raise RuntimeError('live_data_or_hosted_audit_incomplete')
    records = []
    for backend in ('siwc', 'ollama'):
        batch = read(CAMPAIGN / backend / 'result.json')
        audit = read(CAMPAIGN / backend / 'audit.json')
        if batch['status'] != 'COMPLETE' or len(batch['trials']) != 80 or len(audit['records']) != 80:
            raise RuntimeError('incomplete_backend:' + backend)
        saved = {r['run_id']: r for r in audit['records']}
        if set(saved) != {r['run_id'] for r in batch['trials']} or len(saved) != 80:
            raise RuntimeError('trial_identity_mismatch')
        for row in batch['trials']:
            folder = CAMPAIGN / backend / 'trials' / row['run_id']
            if read(folder / 'result.json') != row:
                raise RuntimeError('trial_result_changed')
            evidence, trace = read(folder / 'evidence.json'), read(folder / 'trace.json')
            original = saved[row['run_id']]
            state = reliability_check(row, evidence) if row['stage'] == 'reliability' else batching_check(row, evidence)
            summary, actors = summarize(trace['spans']), counts(trace['spans'])
            consistent = (state['verified'] and state == original['state_audit']
                and summary == trace['summary'] == original['trace_summary']
                and actors == original['actor_accounting'])
            gap = None
            accounted = consistent and original['verified'] and original['trace_audit']
            if consistent and not original['verified'] and original['state_audit']['verified']:
                if row['stage'] == 'reliability' and row['orchestrator_recovery']:
                    gap = guard_gap_checks(row, evidence, trace, summary, actors)
                    accounted = gap['accounted']
            records.append({'backend': backend, 'run_id': row['run_id'],
                'frozen_audit_verified': original['verified'], 'state_and_saved_trace_consistent': consistent,
                'accounted': bool(accounted), 'known_trace_gap': gap})
    return {'status': 'RECONCILED_WITH_DOCUMENTED_TRACE_GAPS',
        'all_records_accounted': len(records) == 160 and all(r['accounted'] for r in records),
        'live_trials': len(records), 'frozen_audit_passes': sum(r['frozen_audit_verified'] for r in records),
        'known_gap_trials': sum(r['known_trace_gap'] is not None for r in records),
        'missing_tool_spans': sum(r['known_trace_gap']['missing_tool_spans'] for r in records if r['known_trace_gap']),
        'full_tool_span_coverage': not any(r['known_trace_gap'] for r in records),
        'new_model_requests': 0, 'task_scores_changed': False,
        'frozen_source_files_verified': len(frozen['source_sha256']),
        'original_supervisor_status': supervisor['status'],
        'original_file_sha256': {str(p.relative_to(CAMPAIGN)): sha(p) for p in (
            CAMPAIGN / 'supervisor-status.json', CAMPAIGN / 'siwc/audit.json', CAMPAIGN / 'ollama/audit.json',
            CAMPAIGN / 'siwc/result.json', CAMPAIGN / 'ollama/result.json')}, 'records': records}


def main():
    output = CAMPAIGN / 'audit-reconciliation.json'
    if output.exists():
        raise RuntimeError('reconciliation_exists_no_overwrite')
    report = review_campaign()
    report['reviewed_utc'] = datetime.now(timezone.utc).isoformat()
    report['analysis_source_sha256'] = sha(Path(__file__))
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'records'}, indent=2))
    if not report['all_records_accounted']:
        raise RuntimeError('unexplained_audit_mismatch_remains')


if __name__ == '__main__':
    main()
