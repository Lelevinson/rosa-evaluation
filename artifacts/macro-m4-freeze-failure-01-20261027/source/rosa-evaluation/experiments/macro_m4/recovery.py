"""Prospective infrastructure reserve, independent of robot execution policy."""
from copy import deepcopy
import time

from rosa_auth.oauth import SafeError
from rosa_auth.responses import SiwcBackend
from rosa_reliability.execution import ControlledStop
from rosa_reliability.macro_agent import InferenceBudget

from .design import LIMITS


def transient(error):
    # Only explicit HTTP responses qualify. No guessing that a timeout, truncated
    # generation, bad tool call, quota error or revoked grant is infrastructure.
    status = error.status if isinstance(error, SafeError) else getattr(error, 'status_code', None)
    if status not in (502, 503, 504): return False
    code = getattr(error, 'code', '')
    return not any(word in code for word in ('scope', 'quota', 'subscription', 'token', 'grant', 'client', 'auth'))


class RecoverableSiwc(SiwcBackend):
    def release_transient_failure(self, error):
        if not transient(error) or self._unavailable != (error.code, error.status):
            raise ControlledStop('ineligible_transport_recovery')
        self._unavailable = None


class CampaignBudget:
    def __init__(self, checkpoint, *, clock=time.monotonic):
        self.clock, self.started, self.checkpoint = clock, clock(), checkpoint
        self.requests = self.retries = 0
        self.events = []

    def reserve(self):
        if self.requests >= LIMITS['backend_requests'] or self.clock() - self.started >= LIMITS['backend_seconds']:
            raise ControlledStop('m4_campaign_request_or_time_budget_exhausted')
        self.requests += 1
        self.checkpoint(self.snapshot())

    def recovery(self, error):
        if not transient(error) or self.retries >= LIMITS['infrastructure_reserve']:
            return False
        self.retries += 1
        self.events.append({'after_request': self.requests, 'error_type': type(error).__name__,
            'http_status': getattr(error, 'status', getattr(error, 'status_code', None)),
            'usage': 'UNKNOWN_CENSORED', 'retry_number': self.retries})
        self.checkpoint(self.snapshot())
        return True

    def snapshot(self):
        return {'reserved_requests': self.requests, 'request_cap': LIMITS['backend_requests'],
            'infrastructure_retries': self.retries, 'reserve_cap': LIMITS['infrastructure_reserve'],
            'elapsed_seconds': self.clock() - self.started, 'events': deepcopy(self.events)}


class RecoveryGate(InferenceBudget):
    """Same validated generation gate; preserve every failed request in evidence.

    Refunding one normal slot is allowed only with a charged infrastructure
    reserve. Successful retry completions still consume a normal decision slot.
    No previous robot action or complete agent invocation is replayed here.
    """
    def __init__(self, *args, campaign, release=None, journal=None, sleeper=time.sleep, **kwargs):
        self.campaign, self.release, self.sleeper, self.journal = campaign, release, sleeper, journal
        super().__init__(*args, batch_reserve=campaign.reserve, **kwargs)

    def invoke(self, model, prompt, config=None):
        retried = False
        while True:
            before = len(self.events)
            try:
                return super().invoke(model, prompt, config)
            except Exception as error:
                if (retried or len(self.events) == before or not transient(error) or
                        not self.campaign.recovery(error)):
                    raise
                event = self.events[-1]
                event.update(status='EXTERNAL_FAILURE', error_type=type(error).__name__,
                    http_status=getattr(error, 'status', getattr(error, 'status_code', None)),
                    credited_infrastructure_reserve=True)
                self.calls -= 1
                if self.release: self.release(error)
                self.sleeper(LIMITS['backoff_seconds'])
                retried = True
            finally:
                if self.journal: self.journal(self.snapshot())

    def snapshot(self):
        result = super().snapshot()
        result.update(calls=len(self.events), decision_calls=self.calls,
            infrastructure_failures=sum(e['status'] == 'EXTERNAL_FAILURE' for e in self.events),
            returned_usage_valid=all(e['status'] in ('RETURNED', 'EXTERNAL_FAILURE') for e in self.events),
            usage_complete=all(e['status'] == 'RETURNED' for e in self.events))
        # Failed HTTP responses may still have consumed provider compute. Do not
        # pretend an unknown cost is zero or claim a complete output upper bound.
        if result['infrastructure_failures']: result['output_upper_bound'] = None
        for index, event in enumerate(result['events'], 1): event['physical_request_index'] = index
        return result
