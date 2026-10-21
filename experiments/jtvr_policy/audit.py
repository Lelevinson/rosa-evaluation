"""Read-back audit from persisted traces, without calling the policy parser."""
from collections import Counter
import json
import re


def check(row, spec):
    errors = []
    trace = row['trace']
    requirements = {(r['entity'], r['field'], r.get('phase', 'final')): r
                    for r in spec['requirements']}
    epochs, barriers, actual, known_types = {}, {}, {}, {}
    parsed_sources = {}
    fragment_counts = Counter()
    for index, event in enumerate(trace):
        args, tool = event['arguments'], event['tool']
        if tool == 'ros2_param_set':
            pair = args['node_name'], 'param:' + args['param_name']
            epochs[pair] = epochs.get(pair, 0) + 1
            barriers[pair] = event['write_completed_tick']
            if event['epoch'] != epochs[pair]:
                errors.append('write_epoch_mismatch')
            continue
        if tool in ('ros2_service_info', 'ros2_node_info'):
            if tool == 'ros2_service_info':
                for endpoint, raw in event['raw'].items():
                    if isinstance(raw, str):
                        known_types[endpoint.removesuffix('/get_parameters')] = raw.strip()
            else:
                for node, raw in event['raw'].items():
                    if isinstance(raw, str):
                        match = re.search(re.escape(node + '/get_parameters') + r': ([^\s]+)', raw)
                        if match:
                            known_types[node] = match[1]
        if event['actor'] not in ('policy_root', 'read_continuation'):
            continue
        fragment_counts[event['fragment_id']] += 1
        if fragment_counts[event['fragment_id']] > 2:
            errors.append('too_many_fragment_executions')
        if event['actor'] == 'read_continuation' and fragment_counts[event['fragment_id']] != 2:
            errors.append('continuation_without_root')
        if tool == 'ros2_service_call':
            node = args['service_name'].removesuffix('/get_parameters')
            if args['srv_type'] != 'rcl_interfaces/srv/GetParameters':
                errors.append('unsafe_service_type')
            if row['profile'] != 'prior_type_allowed' and known_types.get(node) != args['srv_type']:
                errors.append('bulk_without_actual_matching_type')
            match = re.fullmatch(r'\{names: \[([a-z, ]+)\]\}', args['request'])
            names = match[1].split(', ') if match else []
            if not names or any((node, 'param:' + name, 'final') not in requirements for name in names):
                errors.append('out_of_scope_bulk_request')
        for field, value in event['parsed'].items():
            entity = (args.get('node_name') or args.get('service_name', '').removesuffix('/get_parameters')
                      or (args.get('nodes') or args.get('topics') or [''])[0])
            if tool == 'ros2_service_info':
                entity = args['services'][0].removesuffix('/get_parameters')
            phase = 'graph' if field in ('node_summary', 'service_type', 'topic_details') else 'final'
            pair = entity, field
            if event['epochs_at_start'][field] != epochs.get(pair, 0):
                errors.append('stale_epoch_ingested')
            if event['read_started_tick'] < barriers.get(pair, 0):
                errors.append('read_before_write_barrier')
            if field.startswith('param:'):
                if type(value) is not int or event['oracle_at_read'].get(field[6:]) != value:
                    errors.append('value_disagrees_with_world_at_read')
                if tool not in ('ros2_param_get', 'ros2_service_call'):
                    errors.append('fabricated_parameter_coverage')
            elif field == 'topic_details' and tool != 'ros2_topic_info':
                errors.append('fabricated_qos_coverage')
            elif field == 'node_summary' and tool != 'ros2_node_info':
                errors.append('fabricated_node_summary_coverage')
            actual[(entity, field, phase)] = value
            parsed_sources[(index, entity, field)] = value
    for record in row['evidence']:
        if record['status'] != 'VALID' or record['tool'] == 'ros2_service_info' and record['raw_ref'] not in range(len(trace)):
            continue
        key = record['key']
        source = record['raw_ref'], key['entity'], key['field']
        # Warm-cache facts also have real raw-result references, not policy reads.
        if trace[record['raw_ref']]['actor'] == 'cache_warmup':
            if record['value'] != known_types.get(key['entity']):
                errors.append('invalid_warm_fact')
        elif source not in parsed_sources or parsed_sources[source] != record['value']:
            errors.append('evidence_without_raw_provenance')
    all_observed = all(key in actual for key in requirements)
    if row['all_observations_resolved'] != all_observed:
        errors.append('resolution_score_disagrees')
    success = all_observed and all(r.get('equals') is None or actual.get(key) == r['equals']
                                   for key, r in requirements.items())
    if row['verified_contract_pass'] != success:
        errors.append('goal_score_disagrees')
    if row['cli_commands'] != sum(x['cli_commands'] for x in trace):
        errors.append('cli_count_disagrees')
    if abs(row['modeled_cost'] - sum(x['cost'] for x in trace)) > 1e-8:
        errors.append('cost_count_disagrees')
    if row['model_requests'] != 0:
        errors.append('unexpected_model_request')
    return {'fixture_id': row['fixture_id'], 'policy': row['policy'], 'profile': row['profile'],
            'depth': row['depth'], 'role_separated': row['role_separated'],
            'passed': not errors, 'errors': errors}


def check_real(episodes, captures, native):
    """Compare persisted parsed values with separately recorded server callbacks."""
    outcomes = []
    for episode in episodes:
        errors = []
        start, end = episode['native_range']
        commands = native[start:end]
        for dispatch in episode['dispatches']:
            capture = captures[dispatch['raw_ref']]
            # Every wrapper here is one CLI; capture order maps to native order.
            command = native[dispatch['raw_ref']]
            for field, value in dispatch['parsed'].items():
                if field.startswith('param:'):
                    wanted = field[6:]
                    matches = [rpc for rpc in command['server_rpcs']
                        if rpc['kind'] == 'get_parameters' and wanted in rpc['oracle_values']]
                    if not matches or any(rpc['oracle_values'][wanted] != value for rpc in matches):
                        errors.append('parsed_value_disagrees_with_separate_server_record')
            if capture['tool'] != {'get': 'ros2_param_get', 'bulk': 'ros2_service_call',
                'info': 'ros2_service_info', 'node': 'ros2_node_info', 'topic': 'ros2_topic_info'}[dispatch['action']['op']]:
                errors.append('raw_reference_tool_mismatch')
        if episode['cli_commands'] != len(commands):
            errors.append('native_count_mismatch')
        if episode['server_rpcs'] != sum(len(c['server_rpcs']) for c in commands):
            errors.append('rpc_count_mismatch')
        outcomes.append({'fixture_id': episode['fixture_id'], 'policy': episode['policy'],
                         'passed': not errors, 'errors': errors})
    return outcomes
