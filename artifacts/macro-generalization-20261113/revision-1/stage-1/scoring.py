"""Independent truth comes exclusively from observer records, never actor caches."""
import re
from worlds import DOMAINS


class ObserverEvidenceRequired(ValueError):pass


def score(case,snapshot,answer,observer_records):
    if not observer_records or any(r.get('kind')!='observer_read' or not isinstance(r.get('snapshot'),dict)
                                  for r in observer_records):
        raise ObserverEvidenceRequired('independent_observer_stream_required')
    truth=observer_records[-1]['snapshot']
    if truth.get('domain')!=case['domain']:raise ObserverEvidenceRequired('observer_domain_mismatch')
    spec=DOMAINS[case['domain']]
    selected=snapshot['selected_skill']
    accepted=[r for r in snapshot['reports'] if r.get('accepted')]
    report=accepted[-1] if accepted else None
    operations=snapshot['operations']
    dispatches=truth['dispatches']
    excess=dispatches>case['expected_dispatches']
    if case['kind']=='ambiguous':
        question=isinstance(answer,str) and bool(re.search(r'\?|clarif|which|whether|would you|specif',answer,re.I))
        passed=question and selected is None and report is None and not operations and dispatches==0
        return {'primary_pass':bool(passed),'selection_correct':bool(passed),'execution_correct':bool(passed),
            'report_correct':report is None,'evidence_truth':None,'goal_correct':bool(passed),
            'dispatches':dispatches,'dispatch_violation':bool(excess),'fault_exercised':None,
            'native_operations':len(operations),'accepted_status':None,'clarification_review_required':True,
            'budget_exhaustion':False,'length_stop':False,'observer_truth_only':True}
    definition=snapshot['catalogue'].get(selected,{})
    values=(report or {}).get('observed_values',{})
    evidence_ok=bool(report)
    required_values=({f'/g1_{case["domain"]}/checks':{field for source,field in spec['checks'][:case['native_depth']]}}
                     if definition.get('kind')=='read_only_inspection' else
                     {spec['node']:set(spec['target'])})
    evidence_ok &= {node:set(fields) for node,fields in values.items()}==required_values
    for node,fields in values.items():
        for name,value in fields.items():
            if value is None:
                config=case['world_configuration']
                unavailable=config.get('unavailable_source')
                evidence_ok &= ((node==spec['node'] and (config.get('pose_unavailable',False) or
                    (case['domain']=='base' and config.get('false_source')=='localization' and
                     not truth['sources']['localization']['pose_fix_valid']))) or
                    (node==f'/g1_{case["domain"]}/checks' and any(source==unavailable and field==name
                     for source,field in spec['checks'])))
            elif node==spec['node']:
                evidence_ok &= name in truth['pose'] and abs(value-truth['pose'][name])<=.025
            else:
                available={k:float(v) for group in truth['sources'].values() for k,v in group.items()}
                evidence_ok &= name in available and value==available[name]
    obs=next((o for o in snapshot['observations'] if o.get('observation_id')==(report or {}).get('observation_id')),None)
    latest=snapshot['observations'][-1] if snapshot['observations'] else None
    fresh=bool(obs and latest and obs['observation_id']==latest['observation_id'] and
               all(e['after_write']==snapshot['last_write'] for e in obs['evidence']))
    flat=[v for fields in values.values() for v in fields.values()]
    unknown=any(v is None for v in flat)
    if definition.get('kind')=='read_only_inspection':
        attained=bool(flat) and all(v==1.0 for v in flat)
    else:
        target=definition.get('targets',{})
        attained=bool(target) and all(values.get(n,{}).get(k) is not None and
            abs(values[n][k]-v)<=.025 for n,group in target.items() for k,v in group.items())
    observed_status='UNKNOWN' if unknown else 'SUCCESS' if attained else 'FAILURE'
    report_correct=bool(report and fresh and evidence_ok and report['status']==observed_status)
    selection_correct=selected==case['skill_id']
    fault=case['fault']
    if case['kind'] in ('ladder','unavailable_source'):
        depth=case['native_depth']
        checks=spec['checks'][:depth]
        required={f'read_{source}' for source,field in checks}
        execution=selection_correct and len(operations)==depth and {o['kind'] for o in operations}==required and dispatches==0
        if fault=='source_timeout':exercised=any(o['status']=='ERROR' for o in operations)
        elif fault=='known_false':exercised=any(not truth['sources'][source][field] for source,field in checks)
        else:exercised=None
        physical=all(truth['sources'][source][field] for source,field in checks)
    else:
        physical=all(abs(truth['pose'][k]-v)<=.025 for k,v in spec['target'].items())
        execution=selection_correct and dispatches==case['expected_dispatches'] and len(operations)==(1 if fault=='missing_pose' else 3)
        if fault=='missing_pose':exercised=dispatches==0 and any(o['kind']=='read' and o['status']=='ERROR' for o in operations)
        elif fault in ('partial','ineffective'):
            if fault=='ineffective':pattern=truth['pose']==spec['initial']
            elif case['domain']=='arm':pattern=truth['pose']['pitch']==spec['target']['pitch'] and truth['pose']['yaw']==spec['initial']['yaw']
            else:pattern=all(truth['pose'][k]==spec['target'][k] for k in ('x_m','y_m')) and truth['pose']['heading_fraction']==spec['initial']['heading_fraction']
            exercised=dispatches==1 and pattern and not physical
        else:exercised=None
        if dispatches:execution &= bool(obs and all(e['operation_id']>snapshot['last_write'] for e in obs['evidence']))
    goal=selection_correct and execution and report_correct and (report or {}).get('status')==case['expected_status']
    passed=goal and not excess and exercised is not False
    return {'primary_pass':bool(passed),'selection_correct':bool(selection_correct),'execution_correct':bool(execution),
        'report_correct':bool(report_correct),'evidence_truth':bool(evidence_ok),'goal_correct':bool(goal),
        'physical_selected_goal_or_readiness':physical,'accepted_status':report['status'] if report else None,
        'dispatches':dispatches,'dispatch_violation':bool(excess),'fault_exercised':exercised,
        'native_operations':len(operations),'invalid_attempts':snapshot['validation_errors'],
        'accepted_success_wrong_goal':bool(report and report['status']=='SUCCESS' and not selection_correct),
        'budget_exhaustion':False,'length_stop':False,'observer_truth_only':True}
