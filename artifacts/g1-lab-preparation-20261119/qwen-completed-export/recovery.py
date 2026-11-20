"""Parameterize the existing M4 recovery gate with the confirmed G1 dev cap."""
from copy import deepcopy
import sys
import time
from common import REPO
sys.path.insert(0,str(REPO))
from experiments.macro_m4.recovery import RecoveryGate,RecoverableSiwc,transient
from rosa_reliability.execution import ControlledStop


class Campaign:
    def __init__(self,checkpoint):
        self.started=time.monotonic();self.requests=self.retries=0
        self.events=[];self.checkpoint=checkpoint
    def reserve(self):
        if self.requests>=611 or time.monotonic()-self.started>=28800:
            raise ControlledStop('g1_dev_campaign_request_or_time_budget_exhausted')
        self.requests+=1;self.checkpoint(self.snapshot())
    def recovery(self,error):
        if not transient(error) or self.retries>=3:return False
        self.retries+=1
        self.events.append({'after_request':self.requests,'http_status':getattr(error,'status',None),
            'usage':'UNKNOWN_CENSORED','retry_number':self.retries})
        self.checkpoint(self.snapshot());return True
    def snapshot(self):
        return {'reserved_requests':self.requests,'request_cap':611,'infrastructure_retries':self.retries,
                'reserve_cap':3,'elapsed_seconds':time.monotonic()-self.started,'events':deepcopy(self.events)}

class LoggedGate(RecoveryGate):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.terminal_failure=None
    def invoke(self,*args,**kwargs):
        try:return super().invoke(*args,**kwargs)
        except Exception as error:
            self.terminal_failure={'type':type(error).__name__}
            if isinstance(error,ControlledStop):self.terminal_failure['code']=str(error)
            elif hasattr(error,'code'):self.terminal_failure['code']=error.code
            raise
