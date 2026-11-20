"""Prepare an isolated repeat of the unchanged 132 zero-model controls."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STAGE3=ROOT.parent
REV=ROOT.parents[1]
REPO=ROOT.parents[4]
WORKSPACE=ROOT.parents[5]

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (ROOT/'control-input-freeze.json').exists()
    for base,manifest_name,receipt_name,key in (
        (STAGE3,'PREPARATION_MANIFEST.json','PREPARATION_VERIFICATION.json','manifest_sha256'),
        (STAGE3/'predictions-amendment-20261114','AMENDMENT_MANIFEST.json','AMENDMENT_VERIFICATION.json','manifest_sha256')):
        manifest=read(base/manifest_name)
        assert digest(base/manifest_name)==read(base/receipt_name)[key]
        assert all(digest(base/name)==value for name,value in manifest['files'].items())
    protected=read(STAGE3/'protected-before.json')
    assert all(digest(WORKSPACE/name)==value for name,value in protected.items())
    for path in REV.rglob('*'):
        if path.is_file() and ROOT not in path.parents:
            protected[path.relative_to(WORKSPACE).as_posix()]=digest(path)
    write('protected-before.json',protected)
    source=REV/'stage-1'
    transformations={
        'runner.py': [('REV=ROOT.parent','REV=ROOT.parents[1]'),
                      ('REPO=ROOT.parents[3]','REPO=ROOT.parents[4]'),
                      ("ROOT/'freeze.json'","ROOT/'control-input-freeze.json'")],
        'launch.py': [('REPO=ROOT.parents[3]','REPO=ROOT.parents[4]'),
                      ('G1 Stage1 launch','G1 Stage3 zero-model control rerun')],
        'tracing.py': [('rosa-g1-ai-authored-controls-20261113','rosa-g1-stage3-controls-20261114')],
        'persisted_audit.py': [('rosa-g1-ai-authored-controls-20261113','rosa-g1-stage3-controls-20261114')],
    }
    provenance={}
    for name,changes in transformations.items():
        text=(source/name).read_text(encoding='utf-8')
        for old,new in changes:
            assert old in text,(name,old)
            text=text.replace(old,new)
        ast.parse(text)
        (ROOT/name).write_text(text,encoding='utf-8')
        provenance[name]=dict(source=str((source/name).relative_to(WORKSPACE)),source_sha256=digest(source/name),
                              destination_sha256=digest(ROOT/name),changes=changes)
    (ROOT/'control-plan.json').write_bytes((source/'control-plan.json').read_bytes())
    (ROOT/'scoring.py').write_bytes((REV/'stage-2/scoring.py').read_bytes())
    (ROOT/'prepare.py').write_text('''from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[5]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\\n',encoding='utf-8')
''',encoding='utf-8')
    write('provenance.json',dict(copied_runtime_sources=provenance,
        control_plan_sha256=digest(ROOT/'control-plan.json'), unchanged_plan_source_sha256=digest(source/'control-plan.json'),
        scorer_sha256=digest(ROOT/'scoring.py'), original_stage2_scorer_sha256=digest(REV/'stage-2/scoring.py'),
        expected_trials=132, expected_heldout_fixture_trials=76, expected_structural_trials=20,
        expected_dev_fixture_trials=36, live_model_requests=0,
        warning='Synthetic decisions and token metadata; not independent scorer review or live model outcomes.'))
    plan=read(ROOT/'control-plan.json')
    assert len(plan)==132 and sum(r['case'].get('split')=='heldout' for r in plan)==76
    assert (ROOT/'finish.py').exists()
    files={p.name:digest(p) for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.py','.json','.md')}
    write('control-input-freeze.json',dict(kind='Zero-model control input inventory, NOT G-g study freeze',files=files,
        case_edits=0, model_requests=0))
    write('status.json',dict(status='PREPARED',planned=132,completed=0,live_model_requests=0,Stage4_started=False))
    print(dict(prepared_controls=132,heldout_fixture_trials=76,protected_files=len(protected),model_requests=0))

if __name__=='__main__':main()
