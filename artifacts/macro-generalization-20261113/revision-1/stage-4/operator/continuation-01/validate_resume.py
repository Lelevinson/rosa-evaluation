"""Zero-model checks for continuation counters, scope and original time window."""
from copy import deepcopy
import json
from pathlib import Path
import resume

prior=resume.read(resume.ROOT/'status.json')
assert prior['status']=='STOPPED' and prior['completed']==3 and prior['campaign']['reserved_requests']==8
plan=resume.read(resume.ROOT/'plan.json')
done={p.parent.name for p in (resume.ROOT/'trials').glob('*/result.json')}
remaining=[p for p in plan if p['id'] not in done]
assert len(done)==3 and len(remaining)==73 and remaining[0]['id']=='G1r1-heldout-018-macro'
assert not set(p['id'] for p in remaining)&done
campaign=resume.campaign_from_prior(lambda _:None,prior)
assert campaign.requests==8 and campaign.retries==0
assert campaign.snapshot()['elapsed_seconds']>=prior['campaign']['elapsed_seconds']
campaign.reserve();assert campaign.requests==9
for _ in range(602):campaign.reserve()
try:campaign.reserve()
except resume.runtime.ControlledStop:pass
else:raise AssertionError('cumulative_ceiling_not_enforced')
assert campaign.requests==611
assert resume.runtime.trial.__code__.co_filename.endswith('/stage-4/runner.py')
assert resume.runtime.RecoverableSiwc.__module__=='observed_transport'
assert not resume.runtime.Campaign(lambda _:None).recovery(resume.runtime.SafeError('error'))
receipt={'pass':True,'remaining_cells':73,'prior_requests':8,'remaining_physical_allowance':603,
    'cumulative_ceiling_enforced':611,'time_window_reset':False,'failed_trial_retried':False,
    'uses_same_frozen_trial':True,'stream_error_retry_eligible':False,'model_requests':0,'network_requests':0}
out=resume.HERE/'VALIDATION.json';assert not out.exists()
out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
