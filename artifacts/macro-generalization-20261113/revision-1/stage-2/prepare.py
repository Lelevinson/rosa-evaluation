"""Freeze reviewed Stage 2 inputs and sources before live generation."""
from datetime import datetime,timezone
from importlib.metadata import version
import sys
from common import ROOT,REV,WORKSPACE,STAGE1,read,write,digest

def main():
    assert not (ROOT/'freeze.json').exists(),'Preserve the first freeze.'
    assert read(ROOT/'authorization-review.json')['launch_allowed']
    assert read(ROOT/'scorer-validation.json')['pass']
    assert read(STAGE1/'analysis.json')['pass']
    protected=read(STAGE1/'protected-before.json')
    for path in REV.rglob('*'):
        if path.is_file() and ROOT not in path.parents:
            name=path.relative_to(WORKSPACE).as_posix()
            if name in protected:assert digest(path)==protected[name],name
            protected[name]=digest(path)
    assert all(digest(WORKSPACE/name)==value for name,value in protected.items())
    manifest=read(STAGE1/'stage1-manifest.json')['files']
    assert all(digest(STAGE1/name)==value for name,value in manifest.items())
    write('protected-before.json',protected)
    plan=[r for r in read(STAGE1/'control-plan.json') if r['block']=='cases' and r['case']['split']=='dev']
    assert len(plan)==36 and len({r['case']['case_id'] for r in plan})==18
    write('plan.json',plan)
    write('settings.json',{'study':'AI-authored exploratory G1; Sol dev only','model':'gpt-6.1-sol',
        'trials':36,'cases':18,'physical_request_cap':291,'reserve_cap':3,'backend_seconds':28800,
        'logical_calls_per_task':8,'observed_output_gate':2048,'native_limit':10,'tool_limit':16,
        'correction_limit':3,'task_seconds':360,'max_dispatches':1,'native_ratio_band':[.75,1.25],
        'unchanged_prompt_contract_sha256':digest(REV/'prompt-contract.json'),
        'scorer_amendment_cycles_used':1,'P1_P4_adjudication':False,'Qwen_started':False,
        'independent_teammate_authorship':False,'quota':'UNKNOWN'})
    write('environment.json',{'python':sys.version,'environment':'Existing pinned WSL research environment',
        'packages':{name:version(name) for name in ('langchain','langchain-core',
            'openinference-instrumentation-langchain','opentelemetry-sdk','pydantic','PyJWT')},
        'phoenix':'20.23.0, enforced by unchanged HTTP-only server shim','packages_installed_or_updated':False})
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*')) if p.is_file()}
    write('freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'parent_stage1_manifest_sha256':digest(STAGE1/'stage1-manifest.json'),
        'confirmation_sha256':digest(ROOT/'CONFIRMATION_2026-11-14.md')})
    write('status.json',{'status':'PREPARED','completed':0,'planned':36,'live_model_requests':0,'later_stages_started':False})
    print({'frozen_files':len(files),'protected_files':len(protected),'trials':36,'live_model_requests':0})

if __name__=='__main__':main()
