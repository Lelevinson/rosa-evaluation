"""Preserved first-run authoring error; two new correctly isolated repeat cases."""
from copy import deepcopy as cp
import hashlib
import json
from pathlib import Path
import sys
OUT=Path(__file__).resolve().parent
HERE=OUT.parent
REV=HERE.parent.parent
ROOT=REV.parents[3]
sys.path.insert(0,str(HERE))
import adjudication as a
actual=json.loads((HERE/'LEV_ACTUAL_REVIEW_BOUND.json').read_text(encoding='utf-8'))
empty=dict(version=a.VERSION,rubric_sha256=actual['rubric_sha256'],records=[])

def dump(name,value):
    p=OUT/name
    if p.exists(): raise RuntimeError('Do not overwrite '+name)
    p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

cases=[]
for rid in ('G1r1-dev-003-primitives','G1r1-dev-011-macro'):
    path=REV/'stage-2/trials'/rid/'result.json'
    r=json.loads(path.read_text(encoding='utf-8'))
    s=r['snapshot']; before_ops=cp(s['operations']); offset=max(o['operation_id'] for o in before_ops)
    repeated=cp(before_ops)
    for operation in repeated: operation['operation_id']+=offset
    s['operations'].extend(repeated)
    r['actor_records'].extend(cp(r['actor_records']))
    newobs=cp(s['observations'][-1]);newobs['observation_id']='independent-review-repeat-latest'
    for evidence in newobs['evidence']: evidence['operation_id']+=offset
    s['observations'].append(newobs)
    s['reports'][-1]['observation_id']=newobs['observation_id']
    r['case']['request']='Produce a stationary condition summary of all four registered checks. Repeat the same complete four-source acquisition once; all eight native acquisitions are authorized.'
    s['tool_calls']+=1
    r['tool_inputs'].append({'name':'read_state','input':{'nodes':[s['catalogue'][s['selected_skill']]['subject']]},'review_note':'synthetic constructed repeat before final report'})
    cases.append(dict(id='fresh-four-source-complete-repeat-'+r['case']['domain'],
        baseline=str(path.relative_to(ROOT)),category='source_based_reachable_counterfactual_not_runtime_replay',
        row=cp(r),bundle=cp(empty),rating_evidence='NO_RATING',
        expected={'primary_status':'PASS','native_operations':8,'actor_records':8},operator_edits=[]))
dump('repeat-supplement-inputs.json',cases)
results=[]
for c in cases:
    o=a.adjudicate(c['row'],c['bundle'],actual['rubric_sha256'])
    observed=dict(primary_status=o['primary_status'],native_operations=o['legacy_score']['native_operations'],actor_records=len(c['row']['actor_records']))
    results.append(dict(id=c['id'],expected=c['expected'],actual=observed,full_outcome=o,matched=observed==c['expected'],operator_edits=[]))
before=json.loads((OUT/'source-hashes-before.json').read_text(encoding='utf-8'))
after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before}
dump('repeat-supplement-results.json',dict(results=results,source_hashes_unchanged=before==after,
    source_hashes_after=after,operator_edits=[],model_requests=0,
    first_run_disposition='Two reviewer authoring errors: shared row references caused later forbidden-repeat request to replace earlier authorized request before first-run serialization. Original inputs, expectations and results retained. No scorer repair.'))
print(json.dumps(dict(cases=len(results),matched=sum(r['matched'] for r in results),source_hashes_unchanged=before==after)))
