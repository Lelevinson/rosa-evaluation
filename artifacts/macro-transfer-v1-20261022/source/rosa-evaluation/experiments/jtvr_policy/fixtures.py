"""Fixed grounded catalogue/task fixtures. No policy sees hidden values/faults."""
from copy import deepcopy

NODES = ('/jtvr_alpha', '/jtvr_beta')
PARAMS = ('alpha', 'beta', 'gamma')
TEMPLATES = ('one_parameter', 'three_cold', 'three_warm', 'write_report_verify',
             'mixed_roles', 'node_summary_and_parameters', 'two_node_scope',
             'parameters_and_topic_qos')
CONDITIONS = ('nominal', 'cached_discovery', 'high_setup_cost', 'wrong_bulk_type',
              'partial_bulk', 'ambiguous_write_ack')
OPPORTUNITY = frozenset(('three_cold', 'write_report_verify', 'mixed_roles',
                          'node_summary_and_parameters', 'two_node_scope'))


def requirement(node, field, roles=('task',), target=None, phase='final'):
    result = {'entity': node, 'field': field, 'phase': phase, 'roles': list(roles)}
    if target is not None:
        result['equals'] = target
    return result


def suite():
    result = []
    for template in TEMPLATES:
        for condition in CONDITIONS:
            for seed in (0, 1):
                nodes = NODES if template == 'two_node_scope' else NODES[:1]
                names = PARAMS[:1] if template == 'one_parameter' else PARAMS
                writes, requirements = [], []
                is_write = template in ('write_report_verify', 'mixed_roles')
                for node in nodes:
                    for index, name in enumerate(names):
                        target = (index + 1) * 20 + seed if is_write else None
                        roles = ('task', 'verification') if is_write else ('task',)
                        if template == 'mixed_roles' and name != 'alpha':
                            roles = ('verification',)
                        requirements.append(requirement(node, 'param:' + name, roles, target))
                        if is_write:
                            writes.append({'entity': node, 'field': 'param:' + name, 'value': target})
                if template == 'node_summary_and_parameters':
                    requirements.append(requirement(nodes[0], 'node_summary', phase='graph'))
                if template == 'parameters_and_topic_qos':
                    requirements.append(requirement(nodes[0] + '/status', 'topic_details', phase='graph'))
                result.append({'id': f'{template}__{condition}__{seed}', 'template': template,
                    'condition': condition, 'seed': seed, 'requirements': requirements,
                    'writes': writes, 'warm_type': template == 'three_warm' or condition == 'cached_discovery',
                    'opportunity': template in OPPORTUNITY and condition in
                        ('nominal', 'cached_discovery', 'high_setup_cost'),
                    'write_fault_inert': not is_write and condition == 'ambiguous_write_ack'})
    return deepcopy(result)
