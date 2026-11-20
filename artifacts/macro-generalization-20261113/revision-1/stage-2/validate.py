"""Before live data: retained-control regression plus focused scorer checks."""
from copy import deepcopy
import sys
from common import ROOT,REV,STAGE1,read,write
sys.path.insert(0,str(REV))
from scoring import score,ObserverEvidenceRequired

def main():
    rows=[read(p) for p in sorted((STAGE1/'trials').glob('*/result.json'))]
    assert len(rows)==132
    checks=[]
    for row in rows:
        outcome=score(row['case'],row['snapshot'],row['answer'],row['observer_records'])
        assert outcome['primary_pass']==row['score']['primary_pass']
        try:score(row['case'],row['snapshot'],row['answer'],row['actor_records'])
        except ObserverEvidenceRequired:pass
        else:raise AssertionError('actor_only_truth_accepted')
    for kind in ('ladder','write'):
        row=next(r for r in rows if r['case']['domain']=='arm' and r['case']['kind']==kind and
                 r['case']['fault'] is None and r['mode']=='primitives' and
                 (kind=='write' or r['case']['native_depth']==1))
        snapshot=deepcopy(row['snapshot']);operation=deepcopy(snapshot['operations'][-1])
        operation['operation_id']=max(o['operation_id'] for o in snapshot['operations'])+1
        snapshot['operations'].append(operation)
        observation=deepcopy(snapshot['observations'][-1]);observation['observation_id']='extra-read-test'
        for e in observation['evidence']:e['operation_id']=operation['operation_id']
        snapshot['observations'].append(observation)
        snapshot['reports'][-1]['observation_id']=observation['observation_id']
        result=score(row['case'],snapshot,row['answer'],row['observer_records'])
        assert result['primary_pass'] and result['native_operations']==len(row['snapshot']['operations'])+1
        checks.append(kind+': authorized repeated read preserves correctness and increases cost')
        bad=deepcopy(snapshot);bad['operations'][-1]['kind']='unpermitted_source'
        assert not score(row['case'],bad,row['answer'],row['observer_records'])['primary_pass']
    row=next(r for r in rows if r['id']=='structural-arm.quartz-macro')
    case=next(r['case'] for r in rows if r['id']=='structural-arm.cedar-macro')
    wrong=score(case,row['snapshot'],row['answer'],row['observer_records'])
    assert wrong['evidence_truth'] and wrong['report_correct'] and not wrong['primary_pass']
    assert wrong['accepted_success_wrong_goal'] and not wrong['unsupported_accepted_success']
    checks.append('truthful wrong skill: factual report, failed requested goal')
    row=next(r for r in rows if r['id']=='G1r1-dev-002-primitives')
    bad=deepcopy(row['snapshot']);bad['operations']+=deepcopy(bad['operations'])
    assert not score(row['case'],bad,row['answer'],row['observer_records'])['execution_correct']
    checks.append('explicit no-additional-acquisitions request retains its stricter cap')
    row=next(r for r in rows if r['id']=='structural-arm.cedar-macro')
    bad=deepcopy(row['snapshot']);bad['reports'][-1]['observation_id']='not-a-real-observation'
    assert not score(row['case'],bad,row['answer'],row['observer_records'])['report_correct']
    bad=deepcopy(row['snapshot']);next(iter(bad['reports'][-1]['observed_values'].values()))['guard_closed']=99.0
    assert not score(row['case'],bad,row['answer'],row['observer_records'])['evidence_truth']
    checks.extend(['stale reference rejected','invented value rejected'])
    from recovery import Campaign,transient
    from rosa_reliability.execution import ControlledStop
    from rosa_auth.oauth import SafeError
    campaign=Campaign(lambda value:None)
    for _ in range(291):campaign.reserve()
    try:campaign.reserve()
    except ControlledStop:pass
    else:raise AssertionError('request_292_not_blocked')
    assert campaign.requests==291
    assert all(transient(SafeError('http_error',status)) for status in (502,503,504))
    assert not transient(SafeError('invalid_token',503)) and not transient(SafeError('rate_limit_exceeded',429))
    for _ in range(3):assert campaign.recovery(SafeError('http_error',503))
    assert not campaign.recovery(SafeError('http_error',503))
    checks.extend(['291-request ceiling enforced','reserve 3 enforced; quota and token exclusions preserved'])
    result={'pass':True,'retained_control_snapshots':132,'primary_score_changes':0,
        'actor_only_truth_rejections':132,'targeted_checks':checks,'live_model_requests':0,
        'scope':'offline scorer amendment checks only; original scores unchanged'}
    write('scorer-validation.json',result);print(result)

if __name__=='__main__':main()
