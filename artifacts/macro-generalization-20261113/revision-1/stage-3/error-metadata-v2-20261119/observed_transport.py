"""Opt-in G1-only metadata observation; protected transport/parser stay unchanged.

The short respond port preserves the pinned SiwcBackend path, adding only parsed
event observation and sanitized failure records. Recovery is inherited unchanged.
This module never logs requests, raw errors, output text or credentials.
"""
from copy import deepcopy
import json
import re
import time
from urllib.request import Request

from rosa_auth import responses
from rosa_auth.oauth import SafeError
from experiments.macro_m4.recovery import RecoverableSiwc

NOT_RECORDED = 'NOT_RECORDED'
FIELDS = frozenset({'failure_surface', 'http_status', 'sanitized_transport_code',
                    'stream_event_type', 'provider_code', 'provider_type',
                    'output_events_arrived', 'stream_events_received', 'response_id', 'elapsed_ms'})
FAILURE_EVENTS = frozenset({'error', 'response.failed', 'response.incomplete'})
OUTPUT_EVENTS = frozenset({'response.output_item.added', 'response.output_item.done',
    'response.output_text.delta', 'response.output_text.done', 'response.content_part.added',
    'response.content_part.done', 'response.function_call_arguments.delta',
    'response.function_call_arguments.done', 'response.reasoning_summary_text.delta',
    'response.reasoning_summary_text.done', 'response.reasoning_summary_part.added',
    'response.reasoning_summary_part.done'})
PROVIDER_CODES = frozenset({'access_denied', 'invalid_grant', 'invalid_scope', 'invalid_client',
    'unauthorized_client', 'unsupported_grant_type', 'invalid_request', 'insufficient_scope',
    'invalid_token', 'rate_limit_exceeded', 'insufficient_quota', 'server_error',
    'chatpass_v2_scope_not_authorized', 'chatpass_v2_invalid_authorization_context',
    'invalid_refresh_token', 'token_expired', 'refresh_token_expired',
    'refresh_token_invalidated', 'refresh_token_reused'})
PROVIDER_TYPES = frozenset({'server_error', 'rate_limit_error', 'invalid_request_error',
                            'insufficient_quota', 'authentication_error', 'permission_error'})
TRANSPORT_CODES = PROVIDER_CODES | frozenset({'http_error', 'transport_error',
    'stream_event_too_large', 'invalid_stream_json', 'stream_budget_exceeded',
    'error', 'response_failed', 'response_incomplete', 'malformed_completed_response',
    'stream_ended_without_completed', 'oauth_session_closed', 'refresh_token_unavailable',
    'invalid_refresh_response', 'oauth_scope_changed', 'invalid_granted_scopes',
    'unexpected_granted_scopes', 'plan_usage_scope_not_granted', 'invalid_access_token_response',
    'invalid_token_lifetime', 'invalid_json_response', 'invalid_json_object_response'})


def allowed(value, choices):
    return value if isinstance(value, str) and len(value) <= 64 and value in choices else NOT_RECORDED


class Observation:
    def __init__(self, *, clock=time.perf_counter):
        self._clock = clock
        self._started = clock()
        self.record = dict(failure_surface=NOT_RECORDED, http_status=NOT_RECORDED,
            sanitized_transport_code=NOT_RECORDED, stream_event_type=NOT_RECORDED,
            provider_code=NOT_RECORDED, provider_type=NOT_RECORDED,
            output_events_arrived=NOT_RECORDED, stream_events_received=NOT_RECORDED,
            response_id=NOT_RECORDED, elapsed_ms=0)

    def events(self, source):
        # These describe parsed events only, never the provider's unseen wire.
        self.record['stream_events_received'] = 0
        self.record['output_events_arrived'] = False
        for event in source:
            self.record['stream_events_received'] += 1
            if isinstance(event, dict):
                kind = event.get('type')
                response = event.get('response')
                response = response if isinstance(response, dict) else {}
                identifier = response.get('id')
                if isinstance(identifier, str) and re.fullmatch(r'resp_[A-Za-z0-9]{1,59}', identifier):
                    self.record['response_id'] = identifier
                if isinstance(kind, str) and kind in OUTPUT_EVENTS:
                    self.record['output_events_arrived'] = True
                if isinstance(kind, str) and kind in FAILURE_EVENTS:
                    self.record['failure_surface'] = 'IN_STREAM'
                    self.record['stream_event_type'] = kind
                    detail = response.get('error') or event.get('error') or event
                    if isinstance(detail, dict):
                        self.record['provider_code'] = allowed(detail.get('code'), PROVIDER_CODES)
                        self.record['provider_type'] = allowed(detail.get('type'), PROVIDER_TYPES)
            yield event  # Preserve identity, order, parser consumption and payload.

    def finish(self, error):
        if isinstance(error, SafeError):
            self.record['sanitized_transport_code'] = allowed(error.code, TRANSPORT_CODES)
            if type(error.status) is int and 100 <= error.status <= 599:
                self.record['http_status'] = error.status
        if self.record['failure_surface'] == NOT_RECORDED:
            if self.record['http_status'] != NOT_RECORDED:
                self.record['failure_surface'] = 'HTTP'
            elif isinstance(error, TimeoutError):
                self.record['failure_surface'] = 'TIMEOUT'
            elif isinstance(error, SafeError) and error.code == 'stream_ended_without_completed':
                self.record['failure_surface'] = 'STREAM_ENDED'
            elif isinstance(error, SafeError) and error.code == 'transport_error':
                self.record['failure_surface'] = 'TRANSPORT'
            else:
                self.record['failure_surface'] = 'LOCAL_OR_UNKNOWN'
        self.record['elapsed_ms'] = max(0, int((self._clock() - self._started) * 1000))
        return deepcopy(self.record)


class ObservedRecoverableSiwc(RecoverableSiwc):
    """Same transport/recovery contract, opt-in sanitized metadata for checkpoints."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._error_metadata_records = []

    @property
    def error_metadata_records(self):
        return deepcopy(self._error_metadata_records)

    def respond(self, model, history, tools=None):
        self.raise_if_unavailable()
        if self.requests >= self.request_budget:
            raise SafeError('smoke_request_budget_exceeded')
        self.requests += 1
        payload = responses.build_request(model, history, tools)
        observation = Observation()
        try:
            request = Request(responses.RESOURCE + '/responses', data=json.dumps(payload).encode(), headers={
                'Authorization': 'Bearer ' + self._token(),
                'Content-Type': 'application/json', 'Accept': 'text/event-stream'})
            started = time.perf_counter()
            with responses.open_request(request) as stream:
                response = responses.completed_response(observation.events(responses.parse_events(stream)))
        except SafeError as error:
            self._unavailable = (error.code, error.status)
            self._error_metadata_records.append(observation.finish(error))
            raise
        except BaseException as error:
            # Preserve even timeout/interrupt exception semantics and availability.
            self._error_metadata_records.append(observation.finish(error))
            raise
        return response, time.perf_counter() - started
