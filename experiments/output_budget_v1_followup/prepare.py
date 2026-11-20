from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
from experiments.output_budget_v1.design import jobs
from .runner import ROOT,DESTINATION,REQUEST_CAP,write


def main():
    if (DESTINATION/'freeze.json').exists():
        raise RuntimeError('freeze_exists_do_not_overwrite')
    original=ROOT/'artifacts/output-budget-v1-20261022'
    controls=json.loads((original/'deterministic-arm/result.json').read_text())
    if controls['status']!='COMPLETE' or len(controls['rows'])!=4 or not all(r['pass'] for r in controls['rows']):
        raise RuntimeError('deterministic_controls_not_passed')
    tests=json.loads((DESTINATION/'operator/offline-tests.json').read_text())
    if tests['pass'] is not True:
        raise RuntimeError('offline_tests_not_passed')
    from importlib.metadata import version
    write(DESTINATION/'operator/package-versions.json',{name:version(name) for name in (
        'langchain','langchain-core','langchain-ollama','ollama','pydantic',
        'openinference-instrumentation-langchain','opentelemetry-sdk')})
    first=json.loads((original/'gazebo/ollama/result.json').read_text())
    if first['status']!='FAILED' or len(first['trials'])!=1 or first['trials'][0]['run_id']!='000-r0-ur5e_coordinated_move-R256':
        raise RuntimeError('unexpected_original_attempt_do_not_rerun')
    original_schedule=json.loads((original/'schedule.json').read_text())
    if original_schedule!=jobs():
        raise RuntimeError('original_schedule_changed')
    write(DESTINATION/'schedule.json',original_schedule[1:])
    research=ROOT.parent/'rosa-research'
    paths=sorted(set(list((research/'src').rglob('*.py'))+
        list((ROOT/'experiments/output_budget_v1_followup').glob('*.py'))+
        list((ROOT/'experiments/output_budget_v1').glob('*.py'))+
        [ROOT/'experiments/reliability_v2/cases.py',ROOT/'experiments/reliability_v1/tracing.py',
         ROOT/'experiments/ur5e_transfer_v1/arm.py',ROOT/'experiments/ur5e_transfer_v1/runner.py',
         ROOT/'experiments/ur5e_transfer_v1/tracing.py',ROOT/'tests/test_output_completion.py',
         ROOT/'tests/test_output_timeout.py',ROOT/'docs/OUTPUT_BUDGET_V1_FOLLOWUP_2026-10-22.md',
         ROOT/'docs/OUTPUT_BUDGET_V1_PROTOCOL_2026-10-22.md',DESTINATION/'schedule.json',
         research/'pyproject.toml',research/'uv.lock']+
        list((ROOT.parent/'reports').glob('output-budget-v1*.ps1'))+
        list((ROOT.parent/'reports').glob('output-budget-v1*.sh'))))
    files={}
    for path in paths:
        name=path.relative_to(ROOT.parent).as_posix()
        files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        target=DESTINATION/'source'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    previous={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
        (ROOT/'artifacts').glob('*.zip') if p.name.startswith(('ROSA_','reliability-v1-'))}
    write(DESTINATION/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),
        'files':files,'previous_archives':previous,'planned_trials':39,'request_cap':REQUEST_CAP,
        'original_first_trial_kept':first['trials'][0]['run_id'],
        'original_source_freeze_sha256':hashlib.sha256((original/'freeze.json').read_bytes()).hexdigest(),
        'original_trial_result_sha256':hashlib.sha256((original/'gazebo/ollama'/first['trials'][0]['run_id']/'result.json').read_bytes()).hexdigest(),
        'no_original_trial_rerun':True,
        'output_token_cap_per_trial':2048,'offline_tests':tests,
        'no_live_model_requests_before_freeze':True})
    print('FROZEN',len(files),'FILES;39REMAINING_TRIALS;312REQUEST_CAP',flush=True)


if __name__=='__main__':main()

