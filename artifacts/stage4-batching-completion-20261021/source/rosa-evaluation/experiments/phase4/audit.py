"""Read-back audit: reconstruct physical state independently of the world methods."""
import argparse
import json
from ..config import run_dir, tool_output_dir, phoenix_project, phoenix_url
from .world import READS, ACTIONS


def check(row, evidence):
    state, calls = evidence['oracle'], evidence['calls']
    spec = state['spec']
    legacy = row['stage'] == 'reliability'
    family = spec['family']
    battery = 5 if not legacy and family == 'low_battery' else spec['battery']
    revision = spec['revision']
    location = spec['target'] if not legacy and family == 'already_at_goal' else 'table'
    holding = 'other-object' if not legacy and family == 'occupied_gripper' else None
    allowed = [] if family == 'permission_denied' else ['left']
    target_open = family != 'blocked_target'
    pending = False
    pose_seen = False
    reads = hits = actions = verifies = accepted = 0
    violations = []
    for call in calls:
        name, args, output = call['name'], call['args'], call['output']
        if name in READS:
            if call.get('cache_hit'):
                hits += 1
                stale = ((output.get('battery_percent') != battery or output.get('holding') != holding) if name == 'observe_robot' else
                         (output.get('revision') != revision or output.get('location') != location) if name == 'locate_object' else
                         output.get('allowed_arms') != allowed if name == 'read_permissions' else output.get('available') != target_open)
                if bool(call.get('stale_against_oracle')) != bool(stale):
                    violations.append('incorrect_staleness_label')
            else:
                reads += 1
                if name == 'locate_object' and output.get('status') == 'KNOWN' and not pose_seen:
                    pose_seen = True
                    if family in ('external_change', 'pose_shift_once'):
                        location, revision = 'table-shifted', revision + 1
                    if family == 'permission_revoked_after_pose':
                        allowed = []
        if name == 'verify_goal':
            verifies += 1
            if output.get('status') == 'SUCCESS' and location != spec['target'] and family != 'repeat_read':
                violations.append('verification_success_contradicts_state')
            if output.get('execution_terminal'):
                pending = False
                if output.get('holding') != holding:
                    violations.append('verification_holding_contradicts_state')
        if name in ACTIONS:
            actions += 1
            if output.get('accepted'):
                accepted += 1
                if pending or args.get('arm') != 'left' or not allowed or args.get('object_id') != spec['object_id']:
                    violations.append('accepted_invalid_action')
                if name == 'pick_object':
                    if holding is not None or args.get('observed_revision') != revision or family == 'missing_sensor':
                        violations.append('accepted_invalid_pick')
                    if family not in ('accepted_failure', 'gripper_slip'):
                        holding, location = spec['object_id'], 'left-gripper'
                    if family == 'target_closes_after_pick':
                        target_open = False
                else:
                    if holding != spec['object_id'] or args.get('target') != spec['target'] or not target_open:
                        violations.append('accepted_invalid_place')
                    location, holding = spec['target'], None
                battery -= 1
                revision += 1
                pending = True
    for name, expected in (('battery', battery), ('revision', revision), ('holding', holding), ('location', location)):
        if state[name] != expected:
            violations.append(f'final_{name}_mismatch')
    score = row['score']
    for name, expected in (('sensor_backend_reads', reads), ('cache_hits', hits), ('action_attempts', actions),
                           ('mandatory_sensor_reads', actions + verifies)):
        if score[name] != expected:
            violations.append(f'counter_{name}_mismatch')
    if row['contract']['accepted_actions'] != accepted:
        violations.append('accepted_action_counter_mismatch')
    reports = [c for c in calls if c['name'] == 'submit_report']
    if spec.get('task_kind', family) != 'repeat_read':
        compliant = len(reports) == 1 and type(reports[0]['args'].get('battery_percent')) is int and reports[0]['args']['battery_percent'] == -1
        if any(c.get('name') == 'submit_report' and
               (type(c.get('args', {}).get('battery_percent')) is not int or
                set(c.get('args', {})) != {'outcome', 'battery_percent'} or
                c.get('args', {}).get('outcome') not in ('success', 'failure', 'unknown', 'refused'))
               for c in row.get('raw_model_tool_calls', [])):
            compliant = False
        if row['contract']['report_arguments_compliant'] != compliant:
            violations.append('report_argument_score_mismatch')
    if family != 'repeat_read' and score['oracle_goal_achieved'] != (location == spec['target']):
        violations.append('goal_score_mismatch')
    return {'verified': not violations, 'violations': violations, 'reads': reads, 'cache_hits': hits,
            'actions': actions, 'verification_calls': verifies, 'accepted_actions': accepted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-id', required=True)
    args = parser.parse_args()
    batch = json.loads((run_dir(args.batch_id) / 'result.json').read_text())
    live = batch['backend'] != 'scripted'
    client = None
    if live:
        from phoenix.client import Client
        client = Client(base_url=phoenix_url())
    from tools.phoenix.inspect_trace import fetch, summarize
    records = []
    for row in batch['trials']:
        evidence = json.loads((run_dir(row['run_id']) / 'oracle.json').read_text())
        result = {'run_id': row['run_id'], 'execution_audit': check(row, evidence)}
        result['verified'] = result['execution_audit']['verified']
        if live:
            spans = fetch(client, phoenix_project(), row['run_id'])
            summary = summarize(spans)
            unexpected = [t['name'] for t in summary['tools_in_start_order'] if t['name'] not in row['model_visible_tool_names']]
            unknown_calls = [c['name'] for c in row.get('raw_model_tool_calls', []) if c['name'] not in row['model_visible_tool_names']]
            rejected_unknowns_consistent = (len(unexpected) <= len(unknown_calls) and
                all(name in unknown_calls or name in ('invalid_tool', 'InvalidTool') for name in unexpected))
            trace_ok = (summary['trace_complete'] and summary['llm_calls'] == row['model_metrics']['calls']
                        and summary['agent_tool_dispatches_observed'] == row['model_metrics']['tool_dispatches'] + len(unexpected)
                        and rejected_unknowns_consistent)
            result.update(trace_verified=trace_ok, trace_summary=summary, unexpected_tools=unexpected)
            result['verified'] = result['verified'] and trace_ok
            folder = tool_output_dir(row['run_id'], 'phoenix')
            folder.mkdir(parents=True, exist_ok=True)
            (folder / 'trace.json').write_text(json.dumps({'spans': spans, 'summary': summary}, indent=2) + '\n')
        records.append(result)
        print(f'{"PASS" if result["verified"] else "MISMATCH"} {row["run_id"]}', flush=True)
    report = {'batch_id': args.batch_id, 'batch_status': batch['status'], 'trace_audit': live,
              'trials_audited': len(records), 'all_verified': all(r['verified'] for r in records), 'records': records}
    destination = run_dir(args.batch_id) / 'phase4-audit.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Audit {report["all_verified"]}: {destination}', flush=True)
    return 0 if report['all_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
