"""Seal exact held-out inputs plus protected source; no live inference."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
STAGE3=HERE.parent
REV=STAGE3.parent
STAGE4=REV/'stage-4'
REPO=STAGE4.parents[3]
WORKSPACE=REPO.parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (STAGE4/'freeze.json').exists()
    assert read(HERE/'wiring-validation.json')['pass']
    assert read(STAGE3/'error-metadata-v2-20261119/validation-attempt-01/RESULTS.json')['passed']
    assert read(STAGE3/'clarification-scoring-v2-20261119/independent-review/CLEARANCE.json')['clearance']=='PASS'
    assert read(STAGE3/'human-review-20261119/INTAKE_RECEIPT.json')['case_count']==4
    controls=STAGE3/'controls-rerun-20261114'
    assert read(controls/'analysis.json')['passed']
    manifest=read(controls/'CONTROL_EVIDENCE_MANIFEST.json')['files']
    assert all(sha(controls/n)==v for n,v in manifest.items())
    protected=read(STAGE3/'protected-before.json')
    old_mismatches=[n for n,v in protected.items() if sha(WORKSPACE/n)!=v]
    assert old_mismatches==['rosa-evaluation/PROJECT_MASTER_README.md'],old_mismatches
    context=HERE/'MASTER_CONTEXT_AT_FREEZE.md'
    context.write_bytes((REPO/'PROJECT_MASTER_README.md').read_bytes())
    files={n:v for n,v in protected.items() if n!='rosa-evaluation/PROJECT_MASTER_README.md'}
    for root in (STAGE3,STAGE4):
        for p in root.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.name!='freeze.json':
                files[p.relative_to(WORKSPACE).as_posix()]=sha(p)
    for name in ('worlds.py','catalogue.py','catalogues.json','prompt-contract.json','template-groups.json',
                 'paired-order-proposal.json','resources.json','PREDICTIONS_AND_THRESHOLDS.md'):
        files[(REV/name).relative_to(WORKSPACE).as_posix()]=sha(REV/name)
    for name in ('cases.json','control-plan.json','stage1-manifest.json'):
        p=REV/'stage-1'/name;files[p.relative_to(WORKSPACE).as_posix()]=sha(p)
    assert all(sha(WORKSPACE/n)==d for n,d in files.items())
    freeze={'frozen_utc':datetime.now(timezone.utc).isoformat(),'date':'2026-11-19',
        'files_sha256':files,'original_guard_mismatches_preserved':old_mismatches,
        'mutable_context_exception':'Living PROJECT_MASTER_README.md only, authorized progress updates; dated exact context copy sealed',
        'trial_cases':38,'trials':76,'ordinary_cap':608,'reserve':3,'total_physical_cap':611,
        'metadata_contract':'Approved reduced coverage','scorer_contract':'Approved human clarification v2',
        'authorship':'AI-authored cases','stage4_launch_authorized':False,
        'environment':{'python':sys.version,'packages':{n:version(n) for n in ('langchain','langchain-core','pydantic','PyJWT')}}}
    (STAGE4/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frozen_files':len(files),'trials':76,'requests':0,'launch_authorized':False}))

if __name__=='__main__':main()
