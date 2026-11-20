from datetime import datetime,timezone
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import shutil
from .runner import ROOT,DESTINATION,write


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (DESTINATION/'freeze.json').exists():raise RuntimeError('freeze_exists')
    original=ROOT/'artifacts/output-budget-v1-20261022'
    previous=ROOT/'artifacts/output-budget-v1-followup-20261022'
    for campaign in (original,previous):
        frozen=json.loads((campaign/'freeze.json').read_text())
        for name,digest in frozen['files'].items():
            if sha(ROOT.parent/name)!=digest:raise RuntimeError('prior_frozen_source_changed:'+name)
    saved=json.loads((previous/'gazebo/ollama/result.json').read_text())
    first=json.loads((original/'gazebo/ollama/result.json').read_text())
    if len(saved['trials'])!=34 or saved['current_trial']['run_id']!='035-r1-ur5e_coordinated_move-L512':
        raise RuntimeError('unexpected_interruption_checkpoint')
    if (previous/'gazebo/ollama'/saved['current_trial']['run_id']/'result.json').exists():
        raise RuntimeError('interrupted_attempt_has_result_do_not_replace')
    for prerequisite in ('operator/offline-tests.json','pre-resume-phoenix-audit.json'):
        if json.loads((DESTINATION/prerequisite).read_text())['pass'] is not True:
            raise RuntimeError('pre_resume_check_failed:'+prerequisite)
    controls=json.loads((DESTINATION/'deterministic-arm/result.json').read_text())
    if controls['status']!='COMPLETE' or len(controls['rows'])!=4 or not all(r['pass'] for r in controls['rows']):
        raise RuntimeError('post_restart_controls_failed')
    versions=json.loads((previous/'operator/package-versions.json').read_text())
    actual={name:version(name) for name in versions}
    if actual!=versions:raise RuntimeError('package_versions_changed_after_restart')
    write(DESTINATION/'operator/package-versions.json',actual)
    schedule=json.loads((original/'schedule.json').read_text())
    write(DESTINATION/'schedule.json',schedule[35:])
    rows=first['trials']+saved['trials']
    known_calls=sum(r['model_calls'] for r in rows)
    upper_output=sum(r['output_tokens']+(
        min(r['per_call'],2048-r['output_tokens']) if r['model_calls']>len(r['completion']['events']) else 0)
        for r in rows)
    budget={'completed_calls':known_calls,'completed_output_upper_bound':upper_output,
        'interrupted_attempt_reserved_calls':8,'interrupted_attempt_reserved_output':2048,
        'resume_request_cap':40,'resume_output_cap':10240,
        'total_calls_upper_bound':known_calls+8+40,
        'total_output_upper_bound':upper_output+2048+10240,
        'original_call_cap':320,'original_output_cap':81920,'resume_active_seconds_cap':1800}
    prior_active=(datetime.fromisoformat(saved['updated_utc'])-datetime.fromisoformat(saved['started_utc'])).total_seconds()
    prior_active+=(datetime.fromisoformat(first['updated_utc'])-datetime.fromisoformat(first['started_utc'])).total_seconds()+180
    budget['prior_active_seconds_conservative']=prior_active
    budget['combined_active_seconds_upper_bound']=prior_active+1800
    if budget['combined_active_seconds_upper_bound']>10800:
        raise RuntimeError('original_active_time_budget_would_be_exceeded')
    if budget['total_calls_upper_bound']>320 or budget['total_output_upper_bound']>81920:
        raise RuntimeError('original_resource_caps_would_be_exceeded')
    write(DESTINATION/'budget-reservation.json',budget)
    write(DESTINATION/'INTERRUPTION.json',{'observed_utc':datetime.now(timezone.utc).isoformat(),
        'interrupted_run_id':saved['current_trial']['run_id'],'outcome':'UNKNOWN_UNSCORABLE',
        'reason':'supervisor_absent_and_wsl_found_stopped','shutdown_cause_unknown':True,
        'original_checkpoint_sha256':sha(previous/'gazebo/ollama/result.json'),
        'saved_trials_preserved':35,'replacement_is_separate_attempt':True,
        'total_attempts_after_completion':41,'scored_trials_after_completion':40})
    research=ROOT.parent/'rosa-research'
    paths=list((research/'src').rglob('*.py'))
    for package in ('output_budget_v1','output_budget_v1_followup','output_budget_v1_resume'):
        paths+=list((ROOT/'experiments'/package).glob('*.py'))
    paths += [ROOT/'experiments/reliability_v2/cases.py',ROOT/'experiments/reliability_v1/tracing.py',
        ROOT/'experiments/ur5e_transfer_v1/arm.py',ROOT/'experiments/ur5e_transfer_v1/runner.py',
        ROOT/'experiments/ur5e_transfer_v1/tracing.py',ROOT/'tests/test_output_completion.py',
        ROOT/'tests/test_output_timeout.py',research/'pyproject.toml',research/'uv.lock',DESTINATION/'schedule.json']
    paths+=list((ROOT/'docs').glob('OUTPUT_BUDGET_V1*.md'))
    paths+=list((ROOT.parent/'reports').glob('output-budget-v1*.ps1'))
    paths+=list((ROOT.parent/'reports').glob('output-budget-v1*.sh'))
    files={}
    for path in sorted(set(paths)):
        name=path.relative_to(ROOT.parent).as_posix()
        files[name]=sha(path)
        target=DESTINATION/'source'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    write(DESTINATION/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'previous_archives':json.loads((previous/'freeze.json').read_text())['previous_archives'],
        'prior_source_freezes':{p.name:sha(p/'freeze.json') for p in (original,previous)},
        'prior_completed_data':{p.relative_to(ROOT.parent).as_posix():sha(p)
            for campaign in (original,previous) for p in (campaign/'gazebo/ollama').glob('*/result.json')},
        'original_interrupted_checkpoint_sha256':sha(previous/'gazebo/ollama/result.json'),
        'resource_reservation':budget,'planned_scored_trials':5,'replacement_attempts':1,
        'total_complete_case_trials':40,'total_attempts':41,'no_live_resume_requests_before_freeze':True})
    print('FROZEN',len(files),'FILES;5UNFINISHED_ENTRIES;RESERVATIONS',json.dumps(budget),flush=True)


if __name__=='__main__':main()
