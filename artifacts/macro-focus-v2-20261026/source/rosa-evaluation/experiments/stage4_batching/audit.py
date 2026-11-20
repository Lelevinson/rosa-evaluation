"""Audit final live records against separate state/ROS evidence and Phoenix."""
import argparse
import json
from pathlib import Path

from ..config import phoenix_project, phoenix_url
from ..phase4.audit import check as reliability_check
from .runner import CAMPAIGN, PROJECT
from .trace_accounting import counts


def batching_check(row, evidence):
    errors = []
    events, commands = evidence['native_events'], row['native_commands']
    if len(events) != len(commands):
        errors.append('native_event_command_count_mismatch')
    seen_writes = set()
    latest = {}
    for event, command in zip(events, commands):
        args, tool = event['args'], event['tool']
        if tool == 'ros2_param_set':
            seen_writes.add((args['node_name'], args['param_name']))
            latest.pop((args['node_name'], args['param_name']), None)
            continue
        node = args.get('node_name') or args.get('service_name', '').removesuffix('/get_parameters')
        for field, value in event.get('parsed', {}).items():
            if not field.startswith('param:'):
                continue
            name = field[6:]
            rpcs = [rpc for rpc in command['server_rpcs'] if rpc['kind'] == 'get_parameters'
                    and rpc['node'] == node and name in rpc['oracle_values']]
            if not rpcs or any(rpc['oracle_values'][name] != value for rpc in rpcs):
                errors.append('parsed_value_disagrees_with_server')
            latest[(node, name)] = value
    if row['cli_commands'] != len(commands):
        errors.append('cli_count_mismatch')
    if row['server_rpcs'] != sum(len(c['server_rpcs']) for c in commands):
        errors.append('rpc_count_mismatch')
    if row['manifest_requests'] != len(evidence['manifests']):
        errors.append('manifest_count_mismatch')
    # Score validation: a claimed passing task must have a report supported by
    # independently read final values, not merely a helper success return.
    if evidence['strict_contract_pass']:
        if len(evidence['reports']) != 1:
            errors.append('passing_task_has_wrong_report_count')
        else:
            report = evidence['reports'][0]['args']
            for node, fields in report['observed_values'].items():
                for name, value in fields.items():
                    if evidence['oracle_values'].get(node, {}).get(name) != value or latest.get((node, name)) != value:
                        errors.append('passing_report_disagrees_with_evidence')
        if evidence['errors']:
            errors.append('passing_task_has_contract_errors')
    if row['strict_contract_pass'] != evidence['strict_contract_pass']:
        errors.append('row_score_mismatch')
    return {'verified': not errors, 'violations': errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('siwc', 'ollama'), required=True)
    args = parser.parse_args()
    destination = CAMPAIGN / args.backend
    batch = json.loads((destination / 'result.json').read_text())
    from phoenix.client import Client
    import httpx
    from tools.phoenix.inspect_trace import fetch, summarize
    client = Client(http_client=httpx.Client(base_url=phoenix_url(), timeout=60, trust_env=False))
    records = []
    for row in batch['trials']:
        folder = destination / 'trials' / row['run_id']
        evidence = json.loads((folder / 'evidence.json').read_text())
        state_check = reliability_check(row, evidence) if row['stage'] == 'reliability' else batching_check(row, evidence)
        spans = fetch(client, PROJECT, row['run_id'])
        summary = summarize(spans)
        accounting = counts(spans)
        unknown = [t for t in summary['tools_in_start_order'] if t['scope'] == 'agent'
                   and t['name'] not in row['model_visible_tool_names']]
        warmups = sum(e.get('actor') == 'charged_warmup' for e in evidence.get('native_events', []))
        unknown_native = [t for t in unknown if t['name'] not in ('ros2_service_info',) or not warmups]
        requested_unknown = [c['name'] for c in row['raw_model_tool_calls'] if c['name'] not in row['model_visible_tool_names']]
        allowed_unknown = all(t['name'] in requested_unknown or t['name'] in ('invalid_tool', 'InvalidTool') for t in unknown_native)
        trace_ok = (summary['trace_complete'] and summary['llm_calls'] == row['model_metrics']['calls']
            and accounting['model_tool_spans'] == row['model_metrics']['tool_dispatches'] + len(unknown_native)
            and allowed_unknown)
        if row['stage'] == 'batching':
            trace_ok = trace_ok and accounting['native_tool_spans'] == len(row['native_commands'])
        record = {'run_id': row['run_id'], 'stage': row['stage'], 'state_audit': state_check,
                  'trace_audit': trace_ok, 'verified': state_check['verified'] and trace_ok,
                  'trace_summary': summary, 'actor_accounting': accounting}
        records.append(record)
        (folder / 'trace.json').write_text(json.dumps({'spans': spans, 'summary': summary}, indent=2) + '\n')
        print(('PASS' if record['verified'] else 'MISMATCH') + ' ' + row['run_id'], flush=True)
    report = {'backend': args.backend, 'batch_status': batch['status'], 'trials': len(records),
              'all_verified': len(records) == 80 and all(r['verified'] for r in records), 'records': records}
    (destination / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['all_verified']:
        raise RuntimeError('live_readback_audit_incomplete_or_failed')


if __name__ == '__main__':
    main()
