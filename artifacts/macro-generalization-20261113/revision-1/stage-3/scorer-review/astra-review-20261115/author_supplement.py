"""Add a new permitted-repeat case; preserve original expectations and outcomes."""
import hashlib
import json
from pathlib import Path
from copy import deepcopy

here=Path(__file__).resolve().parent
original=json.loads((here/'submission.json').read_text(encoding='utf-8'))
source=next(c for c in original['cases'] if c['case_id']=='repeated-two-source-inspection')
new=deepcopy(source)
new.update(case_id='repeated-arm-two-source-explicit-permission',
    description='Repeat the same two arm sources under an expressly permitted second acquisition.',
    expectation_rationale='The original baseline banned extra acquisitions. This NEW case changes the request to authorize a second read; the original expectation error is retained.')
new['changes'].append({'op':'replace','path':'/case/request','value':
    'Inspect guard_closed and joint_sample_fresh. A second read-only acquisition of both sources is authorized within the native-operation budget.'})
submission={k:deepcopy(v) for k,v in original.items() if k!='cases'}
submission['cases']=[new]
submission['supplements_original_sha256']=hashlib.sha256((here/'submission.json').read_bytes()).hexdigest()
target=here/'supplement-submission.json'
assert not target.exists()
target.write_text(json.dumps(submission,indent=2)+'\n',encoding='utf-8')
print({'new_cases':1,'original_expectations_unchanged':True})
