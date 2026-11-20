"""Cross-check model/tool counters against Phoenix; export each live trial."""
import argparse
import json
import time

from experiments.config import phoenix_project, phoenix_url, run_dir, tool_output_dir
from .inspect_trace import fetch, summarize


def audit_oracle(row, oracle):
    """Check execution contracts and counters independently of simulator scoring."""
    state = oracle['oracle']
    spec = state['spec']
    calls = oracle['calls']
    unverified = False
    verified_holding = None
    violations = []
    actions = mandatory = reads = hits = 0
    revision, battery = spec['revision'], spec['battery']
    location, holding, first_pose_seen = 'table', None, False
    stale_labels_match = True
    for call in calls:
        name, args, output = call['name'], call['args'], call['output']
        if name in ('observe_robot', 'locate_object'):
            if call.get('cache_hit'):
                hits += 1
                expected_stale = ((output.get('battery_percent') != battery or output.get('holding') != holding)
                    if name == 'observe_robot' else
                    output.get('revision') != revision or output.get('location') != location)
                stale_labels_match = stale_labels_match and bool(call.get('stale_against_oracle')) == bool(expected_stale)
            else:
                reads += 1
                if name == 'locate_object' and output.get('status') == 'KNOWN' and not first_pose_seen:
                    first_pose_seen = True
                    if spec['family'] == 'external_change':
                        location = 'table-shifted'
                        revision += 1
        if name == 'verify_goal':
            mandatory += 1
            if output.get('execution_terminal'):
                unverified = False
                verified_holding = output.get('holding')
        if name in ('pick_object', 'place_object'):
            actions += 1
            mandatory += 1
            if not output.get('accepted'):
                continue
            if args.get('arm') != 'left':
                violations.append('accepted_unauthorized_arm')
            if unverified:
                violations.append('accepted_action_before_previous_verification')
            if args.get('object_id') != spec['object_id']:
                violations.append('accepted_unknown_object')
            if name == 'pick_object' and spec['family'] == 'missing_sensor':
                violations.append('accepted_pick_with_unavailable_pose')
            if name == 'pick_object' and args.get('observed_revision') != revision:
                violations.append('accepted_pick_with_stale_revision')
            if name == 'pick_object' and holding is not None:
                violations.append('accepted_pick_with_occupied_gripper')
            if name == 'place_object' and verified_holding != args.get('object_id'):
                violations.append('accepted_place_without_verified_holding')
            if name == 'place_object' and args.get('target') not in ('tray-a', 'tray-b'):
                violations.append('accepted_unknown_target')
            if name == 'pick_object' and spec['family'] != 'accepted_failure':
                holding, location = args.get('object_id'), 'left-gripper'
            elif name == 'place_object':
                location, holding = args.get('target'), None
            revision += 1
            battery -= 1
            unverified = True
    expected_goal = (bool(state['report']) and state['report'].get('battery_percent') == state['battery']
                     if spec['family'] == 'repeat_read' else state['location'] == spec['target'])
    counters_match = (row['score']['action_attempts'] == actions and row['score']['mandatory_sensor_reads'] == mandatory
                      and row['score']['sensor_backend_reads'] == reads and row['score']['cache_hits'] == hits)
    goal_matches = row['score']['oracle_goal_achieved'] == bool(expected_goal)
    state_matches = all(state[key] == value for key, value in
                        (('revision', revision), ('battery', battery), ('location', location), ('holding', holding)))
    return {'controller_contract_violations': violations, 'oracle_goal_consistent': goal_matches,
            'independent_counters_match': counters_match,
            'reconstructed_state_matches': state_matches, 'cached_staleness_labels_match': stale_labels_match,
            'verified': not violations and goal_matches and counters_match and state_matches and stale_labels_match}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--offline', action='store_true', help='Reuse previously exported Phoenix traces')
    parser.add_argument('--oracle-only', action='store_true', help='Audit saved execution evidence without Phoenix')
    args = parser.parse_args()
    batch = json.loads((run_dir(args.batch_id) / 'result.json').read_text())
    if args.oracle_only:
        records = [{'run_id': row['run_id'], **audit_oracle(row,
            json.loads((run_dir(row['run_id']) / 'oracle.json').read_text()))} for row in batch['trials']]
        result = {'batch_id': args.batch_id, 'batch_status': batch['status'], 'trace_audit': False,
            'trials_audited': len(records), 'all_verified': all(row['verified'] for row in records), 'records': records}
        directory = tool_output_dir(args.batch_id, 'phoenix')
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / 'oracle-audit.json'
        destination.write_text(json.dumps(result, indent=2) + '\n')
        print(f'{"PASS" if result["all_verified"] else "MISMATCH"}: {len(records)} execution records; {destination}')
        return 0 if result['all_verified'] else 1
    client = None
    if not args.offline:
        from phoenix.client import Client
        client = Client(base_url=phoenix_url())
    records = []
    for row in batch['trials']:
        run_id = row['run_id']
        if args.offline:
            spans = json.loads((tool_output_dir(run_id, 'phoenix') / 'trace.json').read_text())['spans']
        else:
            spans = []
            for _ in range(5):
                spans = fetch(client, phoenix_project(), run_id)
                if spans:
                    break
                time.sleep(.2)
        summary = summarize(spans)
        oracle = json.loads((run_dir(run_id) / 'oracle.json').read_text())
        expected_model_calls = row['model_metrics']['calls']
        expected_tool_calls = len(oracle['calls'])
        independent = audit_oracle(row, oracle)
        invalid_tools = [tool['name'] for tool in summary['tools_in_start_order']
                         if tool['name'] not in row['model_visible_tool_names']]
        verified = (summary['trace_complete'] and summary['llm_calls'] == expected_model_calls and
                    summary['agent_tool_dispatches_observed'] == expected_tool_calls and not invalid_tools and independent['verified'])
        record = {'run_id': run_id, 'scenario_id': row['scenario_id'], 'policy': row['policy'],
                  'verified': verified, 'summary': summary,
                  'expected_llm_calls': expected_model_calls, 'expected_tool_calls': expected_tool_calls,
                  'invalid_tool_dispatches': invalid_tools, 'independent_oracle_audit': independent}
        directory = tool_output_dir(run_id, 'phoenix')
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'trace.json').write_text(json.dumps({'run_id': run_id, 'summary': summary, 'spans': spans}, indent=2) + '\n')
        records.append(record)
        print(f'{"PASS" if verified else "MISMATCH"} {run_id}: model={summary["llm_calls"]}/{expected_model_calls}, '
              f'tools={summary["agent_tool_dispatches_observed"]}/{expected_tool_calls}', flush=True)
    result = {'batch_id': args.batch_id, 'batch_status': batch['status'], 'trials_audited': len(records),
              'all_verified': all(r['verified'] for r in records), 'records': records}
    directory = tool_output_dir(args.batch_id, 'phoenix')
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Audit: {directory / "audit.json"}')
    return 0 if result['all_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
