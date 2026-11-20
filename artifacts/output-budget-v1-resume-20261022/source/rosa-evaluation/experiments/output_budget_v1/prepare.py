from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
from .design import jobs
from .runner import ROOT,DESTINATION,REQUEST_CAP,write


def main():
    if (DESTINATION/'freeze.json').exists():
        raise RuntimeError('freeze_exists_do_not_overwrite')
    controls=json.loads((DESTINATION/'deterministic-arm/result.json').read_text())
    if controls['status']!='COMPLETE' or len(controls['rows'])!=4 or not all(r['pass'] for r in controls['rows']):
        raise RuntimeError('deterministic_controls_not_passed')
    tests=json.loads((DESTINATION/'operator/offline-tests.json').read_text())
    if tests['pass'] is not True:
        raise RuntimeError('offline_tests_not_passed')
    from importlib.metadata import version
    write(DESTINATION/'operator/package-versions.json',{name:version(name) for name in (
        'langchain','langchain-core','langchain-ollama','ollama','pydantic',
        'openinference-instrumentation-langchain','opentelemetry-sdk')})
    write(DESTINATION/'schedule.json',jobs())
    research=ROOT.parent/'rosa-research'
    paths=sorted(set(list((research/'src').rglob('*.py'))+
        list((ROOT/'experiments/output_budget_v1').glob('*.py'))+
        [ROOT/'experiments/reliability_v2/cases.py',ROOT/'experiments/reliability_v1/tracing.py',
         ROOT/'experiments/ur5e_transfer_v1/arm.py',ROOT/'experiments/ur5e_transfer_v1/runner.py',
         ROOT/'experiments/ur5e_transfer_v1/tracing.py',ROOT/'tests/test_output_completion.py',
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
        'files':files,'previous_archives':previous,'planned_trials':40,'request_cap':REQUEST_CAP,
        'output_token_cap_per_trial':2048,'offline_tests':tests,
        'no_live_model_requests_before_freeze':True})
    print('FROZEN',len(files),'FILES;40TRIALS;320REQUEST_CAP',flush=True)


if __name__=='__main__':main()
