"""Deterministic prerequisites and exact-byte prospective source freeze."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from .cases import ARMS, MockTransport, jobs
from .runner import ROOT, DESTINATION, write


def controls():
    from rosa_reliability.evidence import EvidenceSession, make_evidence_tools
    rows=[]
    schemas=[]
    for job in jobs('validation')+jobs('mock'):
        spec,arm=job['spec'],job['arm']
        transport=MockTransport(spec)
        session=EvidenceSession(transport,spec['targets'],structured_feedback=ARMS[arm][0],
            automatic_verification=ARMS[arm][1],tolerance=.015,write_limit=1)
        tools=make_evidence_tools(session)
        schemas.append([t.args_schema.model_json_schema() for t in tools])
        tool={t.name:t for t in tools}
        observed=tool['read_state'].invoke({'nodes':sorted(spec['targets'])})
        if any(v is None for g in observed['observed_values'].values() for v in g.values()):
            observed=tool['read_state'].invoke({'nodes':sorted(spec['targets'])})
        unknown=any(v is None for g in observed['observed_values'].values() for v in g.values())
        if not unknown:
            pending=[n for n,g in spec['targets'].items() if any(abs(observed['observed_values'][n][k]-v)>.015 for k,v in g.items())]
            if pending:
                result=tool['write_state'].invoke({'node_name':pending[0],'values':spec['targets'][pending[0]]})
                if isinstance(result,str) and 'temporary controller busy' in result:
                    tool['write_state'].invoke({'node_name':pending[0],'values':spec['targets'][pending[0]]})
        verified=tool['verify_outcome'].invoke({})
        if spec['fault']=='postwrite_read' and verified['goal_reached'] is None:
            verified=tool['verify_outcome'].invoke({})
        outcome='UNKNOWN' if verified['goal_reached'] is None else 'SUCCESS' if verified['goal_reached'] else 'FAILURE'
        result=tool['submit_report'].invoke({'status':outcome,'observed_values':verified['observed_values']})
        passed=isinstance(result,dict) and result['report_accepted'] and outcome==spec['expected_status']
        rows.append({'phase':job['phase'],'case':spec['id'],'arm':arm,'pass':passed,'snapshot':session.snapshot()})
    if any(s!=schemas[0] for s in schemas):
        raise RuntimeError('tool_schema_differs_by_arm')
    return rows


def main():
    DESTINATION.mkdir(parents=True,exist_ok=True)
    if (DESTINATION/'freeze.json').exists():
        raise RuntimeError('freeze_exists_do_not_overwrite')
    rows=controls()
    if len(rows)!=40 or not all(r['pass'] for r in rows):
        write(DESTINATION/'failed-development-controls.json',rows)
        raise RuntimeError('scripted_case_controls_failed')
    write(DESTINATION/'scripted-controls.json',rows)
    research=ROOT.parent/'rosa-research'
    paths=sorted(list((research/'src').rglob('*.py'))+
        list((ROOT/'experiments/reliability_v2').glob('*.py'))+
        [ROOT/'experiments/reliability_v1/tracing.py', research/'tests/test_evidence.py',
         research/'tests/test_reliability.py', research/'tests/test_siwc.py', research/'tests/test_siwc_overnight.py',
         research/'tests/test_shared_backends.py', ROOT/'tests/test_reliability_v2.py',
         research/'pyproject.toml',research/'uv.lock', ROOT/'docs/RELIABILITY_V2_PROTOCOL_2026-10-22.md'])
    manifest={}
    for path in paths:
        name=path.relative_to(ROOT.parent).as_posix()
        manifest[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        target=DESTINATION/'source'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    write(DESTINATION/'schedule.json',{'validation':jobs('validation'),'mock':jobs('mock')})
    write(DESTINATION/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),
        'files':manifest,'no_live_inference_before_freeze':True,'scripted_controls':40,
        'trials_per_backend':{'validation':8,'mock':32,'gazebo':8},'hosted_total_cap':384})
    print('SOURCE_FROZEN',len(manifest),'FILES;40CONTROLS_PASS',flush=True)


if __name__=='__main__':
    main()
