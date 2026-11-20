"""Prepare a reviewable continuation; never approve the expired time window."""
import ast
import sys
from datetime import datetime,timezone,timedelta
from common import ROOT,ORIGINAL,WORKSPACE,REPO,read,write,digest
sys.path.insert(0,str(REPO))

def main():
    assert not (ROOT/'freeze.json').exists()
    original_manifest=read(ORIGINAL/'stage2-manifest.json')
    assert all(digest(ORIGINAL/n)==v for n,v in original_manifest['files'].items())
    protected=read(ORIGINAL/'protected-before.json')
    for p in ORIGINAL.rglob('*'):
        if p.is_file():protected[p.relative_to(WORKSPACE).as_posix()]=digest(p)
    assert all(digest(WORKSPACE/n)==v for n,v in protected.items())
    write('protected-before.json',protected)
    review=read(ORIGINAL/'interruption-review.json');allowed=[r['id'] for r in review['not_started']]
    plan=[r for r in read(ORIGINAL/'plan.json') if r['id'] in allowed]
    assert [r['id'] for r in plan]==allowed and len(plan)==10 and sum(r['expected_turns'] for r in plan)==28
    assert all(not (ORIGINAL/'trials'/r['id']).exists() for r in plan)
    write('plan.json',plan)
    source=(ORIGINAL/'runner.py').read_text().split('\ndef main():')[0]
    before='remaining=28800-(time.monotonic()-campaign.started)'
    assert source.count(before)==1
    (ROOT/'runtime_trial.py').write_text(source.replace(before,'remaining=campaign.remaining_seconds()'))
    for name in ('authorization.py','tracing.py','scoring.py','recovery.py','persisted_audit.py'):
        assert digest(ROOT/name)==digest(ORIGINAL/name),name
    assert read(ROOT/'authorization-preflight.json')['pass']
    write('authorization-review.json',{'reviewed_date':'2026-11-14','preflight_pass_reviewed':True,
        'provider_renewal_verified':True,'scopes_unchanged':True,'required_model_available':True,
        'quota':'UNKNOWN','inference_requests':0,'launch_allowed':False,
        'remaining_gate':'EXPLICIT_NEW_TIME_WINDOW_APPROVAL','automatic_login':False})
    previous=read(ORIGINAL/'status.json')
    deadline=datetime.fromisoformat(previous['started_utc'])+timedelta(hours=8)
    write('time-gate.json',{'checked_utc':datetime.now(timezone.utc).isoformat(),
        'original_deadline_utc':deadline.isoformat(),'original_window_expired':datetime.now(timezone.utc)>deadline,
        'requested_new_window_seconds':1800,'approved':False,'new_model_requests':0,
        'prior_charged_requests':66,'cumulative_request_cap':291,'segment_cap':83,
        'prior_active_execution_seconds':previous['campaign']['elapsed_seconds']})
    # Offline resource checks and source syntax only; no model instantiation/request.
    for p in ROOT.glob('*.py'):ast.parse(p.read_text())
    from runner import CumulativeCampaign
    from rosa_reliability.execution import ControlledStop
    clock=[0.0];campaign=CumulativeCampaign(lambda value:None,clock=lambda:clock[0])
    for _ in range(83):campaign.reserve()
    try:campaign.reserve()
    except ControlledStop:pass
    else:raise AssertionError('segment_cap_not_enforced')
    assert campaign.requests==149
    campaign=CumulativeCampaign(lambda value:None,clock=lambda:clock[0]);clock[0]=1801
    try:campaign.reserve()
    except ControlledStop:pass
    else:raise AssertionError('new_window_not_enforced')
    write('validation.json',{'pass':True,'exact_unstarted_ids':10,'expected_requests':28,
        'prior_requests_carried':66,'segment_cap_enforced':83,'cumulative_cap':291,
        'proposed_window_enforced':1800,'scorer_changed':False,'new_model_requests':0})
    write('executor-provenance.json',{'source':str(ORIGINAL/'runner.py'),
        'source_sha256':digest(ORIGINAL/'runner.py'),'generated_trial_sha256':digest(ROOT/'runtime_trial.py'),
        'sole_executor_change':before+' -> remaining=campaign.remaining_seconds()',
        'case_scorer_amendment_cycles_used':1,'new_case_scorer_cycles':0})
    files={p.name:digest(p) for p in ROOT.iterdir() if p.is_file()}
    write('freeze.json',{'files':files,'original_manifest_sha256':digest(ORIGINAL/'stage2-manifest.json'),
        'owner_continuation_authorized':True,'new_time_window_approval_required':True})
    write('status.json',{'status':'READY_PENDING_TIME_WINDOW_APPROVAL','planned':10,'completed':0,
        'original_finalized':26,'cumulative_finalized':26,'live_model_requests':66,'new_model_requests':0,
        'later_stages_started':False})
    print({'prepared_trials':10,'frozen_files':len(files),'protected_files':len(protected),
        'preflight':'PASS','original_window_expired':True,'approval_still_required':True,'new_model_requests':0})

if __name__=='__main__':main()
