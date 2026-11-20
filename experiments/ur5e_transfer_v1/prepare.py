from datetime import datetime,timezone
import hashlib
from pathlib import Path
import shutil
from .runner import ROOT,DESTINATION,write
from .arm import arm_cases


def main():
    if (DESTINATION/'freeze.json').exists():
        raise RuntimeError('freeze_exists_do_not_overwrite')
    import json
    controls=json.loads((DESTINATION/'deterministic-arm/result.json').read_text())
    if controls['status']!='COMPLETE' or len(controls['rows'])!=4 or not all(r['pass'] for r in controls['rows']):
        raise RuntimeError('deterministic_controls_not_passed')
    for row,spec in zip(controls['rows'],arm_cases()):
        attained=all(abs(row['independent_observation'][k]-v)<=.025 for k,v in spec['targets']['/ur5e'].items())
        if spec['expected_status']!='UNKNOWN' and attained!=spec['achievable']:
            raise RuntimeError('independent_controller_outcome_mismatch')
    research=ROOT.parent/'rosa-research'
    paths=sorted(list((research/'src').rglob('*.py'))+
        list((ROOT/'experiments/ur5e_transfer_v1').glob('*.py'))+
        [ROOT/'experiments/reliability_v2/cases.py',ROOT/'experiments/reliability_v1/tracing.py',
         ROOT/'tests/test_ur5e_readiness.py',ROOT/'docs/UR5E_TRANSFER_V1_PROTOCOL_2026-10-22.md',
         research/'pyproject.toml',research/'uv.lock'])
    files={}
    for path in paths:
        name=path.relative_to(ROOT.parent).as_posix()
        files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        destination=DESTINATION/'source'/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,destination)
    write(DESTINATION/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'deterministic_controls':4,'readiness_unit_tests':2,'planned_trials_per_backend':8,
        'request_cap_per_backend':64,'no_live_model_requests_before_freeze':True})
    write(DESTINATION/'arm-gate.json',{'pass':True,'deterministic_controls':4,'separate_followup':True})
    print('FROZEN',len(files),'FILES;4DETERMINISTIC_CONTROLS_PASS',flush=True)


if __name__=='__main__':
    main()
