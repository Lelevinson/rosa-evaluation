"""Ten new trials only; the interrupted original trial is never retried."""
from datetime import datetime,timezone
import time
from common import ROOT,ORIGINAL,read,write,verify,require_approval
from runtime_trial import trial,RecoverableSiwc,ChatSiwc,restore_only,check_models,MODEL,SafeError,ControlledStop
from recovery import transient

class CumulativeCampaign:
    def __init__(self,checkpoint,clock=time.monotonic):
        old=read(ORIGINAL/'status.json')['campaign']
        self.prior_requests=old['reserved_requests'];self.prior_seconds=old['elapsed_seconds']
        self.requests=self.prior_requests;self.retries=old['infrastructure_retries']
        self.clock=clock;self.started=clock();self.checkpoint=checkpoint;self.events=[]
    def remaining_seconds(self):
        elapsed=self.clock()-self.started
        return min(1800-elapsed,28800-self.prior_seconds-elapsed)
    def reserve(self):
        if self.remaining_seconds()<=0 or self.requests>=291 or self.requests-self.prior_requests>=83:
            raise ControlledStop('continuation_request_or_time_budget_exhausted')
        self.requests+=1;self.checkpoint(self.snapshot())
    def recovery(self,error):
        if not transient(error) or self.retries>=3:return False
        self.retries+=1
        self.events.append({'after_request':self.requests,'http_status':getattr(error,'status',None),
            'usage':'UNKNOWN_CENSORED','retry_number':self.retries})
        self.checkpoint(self.snapshot());return True
    def snapshot(self):
        elapsed=self.clock()-self.started
        return {'reserved_requests':self.requests,'request_cap':291,'segment_requests':self.requests-self.prior_requests,
            'segment_cap':83,'infrastructure_retries':self.retries,'reserve_cap':3,
            'elapsed_seconds':self.prior_seconds+elapsed,'segment_elapsed_seconds':elapsed,
            'new_window_seconds':1800,'remaining_seconds':max(0,self.remaining_seconds()),'events':self.events.copy()}

def main():
    require_approval();verify()
    assert not (ROOT/'RUN_ONCE').exists(),'Do not replay this continuation.'
    (ROOT/'RUN_ONCE').write_text('Only originally unstarted trials. No automatic replacement.\n')
    state={'status':'STARTING','planned':10,'completed':0,'original_finalized':26,
        'cumulative_finalized':26,'live_model_requests':66,'new_model_requests':0,'current_trial':None,
        'started_utc':datetime.now(timezone.utc).isoformat(),'later_stages_started':False}
    def checkpoint(value):
        state.update(campaign=value,live_model_requests=value['reserved_requests'],new_model_requests=value['segment_requests'])
        write('status.json',state)
    campaign=CumulativeCampaign(checkpoint);checkpoint(campaign.snapshot())
    auth={};model=transport=None
    try:
        with restore_only(auth) as active:
            check_models(active,auth);write('launch-authorization-status.json',auth)
            transport=RecoverableSiwc(token_provider=active.access_token,request_budget=83)
            model=ChatSiwc(model=MODEL,backend=transport);state['status']='RUNNING'
            for item in read(ROOT/'plan.json'):
                transport.raise_if_unavailable()
                assert not (ORIGINAL/'trials'/item['id']).exists(),'Original attempt must never be replaced.'
                state['current_trial']=item['id'];checkpoint(campaign.snapshot())
                row=trial(item,model,transport,campaign)
                state['completed']+=1;state['cumulative_finalized']=26+state['completed'];state['current_trial']=None
                checkpoint(campaign.snapshot())
                print({'new_done':state['completed'],'new_planned':10,'total_finalized':state['cumulative_finalized'],
                    'total_planned':36,'id':item['id'],'primary_pass':row['primary_pass'],
                    'calls':row['actual_turns'],'cumulative_requests':campaign.requests},flush=True)
                transport.raise_if_unavailable()
            assert transport.requests==campaign.requests-66
            state.update(status='COMPLETE',protected_check=verify())
    except BaseException as error:
        state.update(status='STOPPED',error_type=type(error).__name__)
        state['error_code']=(error.code if isinstance(error,SafeError) else str(error)
            if isinstance(error,ControlledStop) else 'inspect_retained_trial_and_audit')
        raise
    finally:
        if model:model.close()
        elif transport:transport.close()
        write('launch-authorization-status.json',auth)
        state['completed_utc']=datetime.now(timezone.utc).isoformat();checkpoint(campaign.snapshot())

if __name__=='__main__':main()
