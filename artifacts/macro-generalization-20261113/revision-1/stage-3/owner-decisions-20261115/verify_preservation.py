"""Verify owner decisions preserve source and all prior checkpoints."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STAGE3=ROOT.parent
WORKSPACE=STAGE3.parents[4]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    sources=read(STAGE3/'instrumentation/observability-boundary-tests.json')['source_hashes_before']
    source_checks={name:dict(expected=value,actual=digest(WORKSPACE/name)) for name,value in sources.items()}
    assert all(row['expected']==row['actual'] for row in source_checks.values())
    counts={}
    for base,manifest,receipt in [
        (STAGE3,'PREPARATION_MANIFEST.json','PREPARATION_VERIFICATION.json'),
        (STAGE3/'predictions-amendment-20261114','AMENDMENT_MANIFEST.json','AMENDMENT_VERIFICATION.json'),
        (STAGE3/'controls-rerun-20261114','CONTROL_EVIDENCE_MANIFEST.json','CONTROL_VERIFICATION.json')]:
        original=read(base/manifest)
        assert digest(base/manifest)==read(base/receipt)['manifest_sha256']
        assert all(digest(base/name)==value for name,value in original['files'].items())
        counts[base.name]=len(original['files'])
    result=dict(date='2026-11-15',passed=True,protected_source_checks=source_checks,
        prior_checkpoint_files_verified=counts,hook_applied=False,
        experimental_backend_requests=0,
        review_model_usage='Separate GPT-6 Astra review is authorized; its reasoning usage is not an experiment backend request.')
    (ROOT/'preservation-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(dict(passed=True,source_files_verified=len(source_checks),prior_checkpoints=counts,experimental_backend_requests=0))

if __name__=='__main__':main()
