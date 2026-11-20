"""Client-side limits and honest usage accounting, before the tool parser."""
from copy import deepcopy
import time

from rosa_reliability import ControlledStop
from rosa_reliability.completion import CompletionAwareROSA
from rosa_reliability.terminal import AcceptedReportROSA
from .design import LIMITS


class LiveROSA(AcceptedReportROSA, CompletionAwareROSA):
    """Compose existing opt-in terminal and pre-parser seams; change neither."""


class InferenceGate:
    def __init__(self, backend, batch_reserve):
        self.backend, self.batch_reserve = backend, batch_reserve
        self.started = time.monotonic()
        self.calls = self.input_tokens = self.output_tokens = 0
        self.events = []

    def invoke(self, model, prompt, config=None):
        remaining = LIMITS['output_threshold'] - self.output_tokens
        if self.calls >= LIMITS['model_calls'] or remaining <= 0:
            raise ControlledStop('inference_budget_exhausted_before_dispatch')
        if time.monotonic() - self.started >= LIMITS['seconds']:
            raise ControlledStop('inference_deadline_exhausted_before_dispatch')
        self.batch_reserve()
        allowance = min(LIMITS['local_per_call'], remaining) if self.backend == 'ollama' else None
        self.calls += 1
        event = {'call': self.calls, 'status': 'UNRETURNED', 'requested_output_allowance': allowance,
                 'usage': None, 'finish_reason': None}
        self.events.append(event)
        options = {'options': {'num_predict': allowance, 'num_ctx': 8192, 'temperature': 0,
                              'seed': 42, 'use_mmap': True}} if allowance is not None else {}
        message = model.invoke(prompt, config=config, **options)
        usage = message.usage_metadata or {}
        if any(type(usage.get(k)) is not int or usage[k] < 0
               for k in ('input_tokens', 'output_tokens', 'total_tokens')):
            event['status'] = 'RETURNED_USAGE_INVALID'
            raise ControlledStop('returned_usage_missing_or_invalid')
        self.input_tokens += usage['input_tokens']
        self.output_tokens += usage['output_tokens']
        reason = (message.response_metadata or {}).get('done_reason',
                  (message.response_metadata or {}).get('finish_reason'))
        event.update(status='RETURNED', usage=dict(usage), finish_reason=reason)
        if allowance is not None and usage['output_tokens'] > allowance:
            raise ControlledStop('provider_exceeded_requested_output_allowance')
        if self.output_tokens > LIMITS['output_threshold']:
            raise ControlledStop('observed_output_threshold_exceeded_no_tools_dispatched')
        if reason == 'length':
            event['tool_calls_withheld'] = len(message.tool_calls)
            raise ControlledStop('truncated_response_no_tool_dispatch_no_automatic_retry')
        return message

    def snapshot(self):
        unreturned = [e for e in self.events if e['status'] == 'UNRETURNED']
        upper = (self.output_tokens + sum(e['requested_output_allowance'] for e in unreturned)
                 if self.backend == 'ollama' else self.output_tokens if not unreturned else None)
        return {'calls': self.calls, 'known_input_tokens': self.input_tokens,
                'known_output_tokens': self.output_tokens, 'output_upper_bound': upper,
                'usage_complete': all(e['status'] == 'RETURNED' for e in self.events),
                'events': deepcopy(self.events)}
