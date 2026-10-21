"""Public tasks are fixed before live models; hidden evaluator values stay separate."""
from copy import deepcopy
from ..jtvr_policy.fixtures import suite


def tasks():
    result = []
    for spec in suite():
        if spec['condition'] != 'nominal' or spec['seed'] != 0:
            continue
        value = deepcopy(spec)
        groups = {}
        extras = []
        for req in spec['requirements']:
            if req['field'].startswith('param:'):
                node = req['entity']
                group = groups.setdefault(node, {'names': [], 'report_names': [], 'expected_values': {}})
                name = req['field'][6:]
                group['names'].append(name)
                if 'task' in req['roles']:
                    group['report_names'].append(name)
                if 'equals' in req:
                    group['expected_values'][name] = req['equals']
            else:
                extras.append(req['entity'] + ':' + req['field'])
        parts = []
        for node, group in groups.items():
            if group['expected_values']:
                parts.append(f"On {node}, set parameters {group['expected_values']}, then verify every requested value by post-write observation.")
            else:
                parts.append(f"Read current parameters {group['names']} on {node}.")
            parts.append(f"Report the observed values for {group['report_names']} on {node}.")
        for extra in extras:
            parts.append('Also acquire and acknowledge ' + extra + '.')
        parts.append('Submit exactly one final report. Acknowledgment of a write is not verification. Do not call tools after reporting.')
        value.update(groups=groups, extras=extras, query=' '.join(parts))
        result.append(value)
    return result


def reliability_jobs():
    from ..stateful.scenarios import suite as legacy_suite
    fixtures = [s for s in legacy_suite() if s['family'] in
                ('transfer', 'accepted_failure', 'missing_sensor') and s['variant'] in (0, 1)]
    result = []
    for repetition in (0, 1):
        for index, spec in enumerate(fixtures):
            arms = ['original', 'clarified', 'bounded_recovery', 'enforce_verification']
            shift = (index + repetition) % 4
            arms = arms[shift:] + arms[:shift]
            for arm in arms:
                result.append({'stage': 'reliability', 'spec': spec, 'intervention': arm,
                               'policy': 'none', 'repetition': repetition})
    return result


def batching_jobs():
    result = []
    for repetition in (0, 1):
        for index, spec in enumerate(tasks()):
            arms = ['model_selected', 'amortized_batching']
            if (index + repetition) % 2:
                arms.reverse()
            for arm in arms:
                result.append({'stage': 'batching', 'spec': spec, 'intervention': 'none',
                               'policy': arm, 'repetition': repetition})
    return result


INSTRUCTIONS = (
    'Use only registered tools on the two isolated test nodes. No shell or robot motion. '
    'Read-only tasks must not perform writes. Write only the exact user-authorized parameter targets. '
    'A write acknowledgment never verifies a final value; read back after ALL requested writes on that node. '
    'Use read_parameter_evidence to communicate the node, full names needed for reporting OR verification, '
    'report_names, expected_values (empty for read-only tasks), and preferred strategy. '
    'These arguments are your requirement manifest; derive them from the user request, never invent fields. '
    'For mixed roles include verification-only fields in names even when not in report_names. '
    'Both configurations expose the same helper and primitive ROSA capabilities; the execution policy may '
    'honor your strategy or optimize it. The helper can execute the same direct or discovery-plus-bulk '
    'plan in either configuration. It never writes or silently fills missing requirements. '
    'Strong planning guidance: one direct get costs about 1.13, type discovery 0.41, bulk GetParameters '
    '1.25, node info 0.43, topic info 0.42 cost units. Prefer direct for one field, and bulk for three '
    'fields when discovery plus bulk is cheaper; reuse already observed matching type. Use node_bulk '
    'when a node summary is also required, so that node_info supplies the type at the same time. '
    'You may instead use the primitive tools, including standard bulk service calls, with the same '
    'scope checks. Only registered GetParameters services may be called. '
    'For node_summary use ros2_node_info or node_bulk; for topic_details use ros2_topic_info. '
    'After acquiring evidence, call submit_parameter_report once with outcome success, failure or unknown, '
    'observed_values grouped by node (report only the requested reporting fields), and acknowledged_details '
    'as entity:node_summary or entity:topic_details identifiers. Do not fabricate numeric values. '
    'Use success only when all requested observations and verification predicates are supported. '
    'If evidence cannot be acquired, report unknown; a known wrong target is failure. '
    'Stop tool use after the report and answer briefly. No memory across tasks.'
)
