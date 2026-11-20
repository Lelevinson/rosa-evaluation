"""Zero-network boundary probe; do not patch or replace production code."""
from io import BytesIO
import json
import sys
import time
from unittest.mock import patch
from urllib.error import HTTPError
from common import ROOT, REPO, WORKSPACE, write, digest
sys.path.insert(0, str(REPO))
from rosa_auth import oauth, responses
from experiments.macro_m4.recovery import transient

CANARY = 'CANARY_STAGE3_SECRET_DO_NOT_RETAIN_7f93b1'
ALLOWED = {'failure_surface', 'http_status', 'stream_event_type', 'provider_code', 'provider_type',
           'output_events_arrived', 'stream_events_received', 'response_id', 'elapsed_ms'}

def signature(error):
    return {'class': type(error).__name__, 'code': getattr(error, 'code', None),
            'status': getattr(error, 'status', None), 'retry_eligible': transient(error)}

def safe_code(value):
    return oauth.error_code(value, 'UNRECOGNIZED')[:64] if value is not None else 'NOT_RECORDED'

class EventObserver:
    """A possible G1-side wrapper can observe parsed events before parser failure."""
    def __init__(self):
        self.started = time.perf_counter()
        self.record = dict(failure_surface='NOT_RECORDED', http_status=None,
            stream_event_type='NOT_RECORDED', provider_code='NOT_RECORDED', provider_type='NOT_RECORDED',
            output_events_arrived=False, stream_events_received=0, response_id='NOT_RECORDED', elapsed_ms=0)
    def events(self, events):
        for event in events:
            self.record['stream_events_received'] += 1
            kind = event.get('type')
            if isinstance(kind, str) and kind.startswith('response.output'):
                self.record['output_events_arrived'] = True
            response = event.get('response', {})
            identifier = response.get('id') if isinstance(response, dict) else None
            import re
            if isinstance(identifier, str) and re.fullmatch(r'resp_[A-Za-z0-9]{1,59}', identifier):
                self.record['response_id'] = identifier[:64]
            if kind in ('error', 'response.failed', 'response.incomplete'):
                self.record['failure_surface'] = 'IN_STREAM'
                self.record['stream_event_type'] = kind
                detail = response.get('error') or event.get('error') or event
                if isinstance(detail, dict):
                    self.record['provider_code'] = safe_code(detail.get('code'))
                    value = detail.get('type')
                    self.record['provider_type'] = value if value in (
                        'server_error', 'rate_limit_error', 'invalid_request_error', 'insufficient_quota') else 'UNRECOGNIZED'
            yield event  # Same event object, unchanged order and content.

def invoke_stream(kind, observed):
    observer = EventObserver()
    def events():
        if kind == 'timeout':
            raise TimeoutError('fixture_timeout')
        if kind == 'midstream_truncation':
            yield {'type': 'response.output_text.delta', 'delta': CANARY}
            return
        if kind == 'failed_event_with_code':
            yield {'type': 'response.created', 'response': {'id': 'resp_fixture123'}}
            yield {'type': 'response.output_text.delta', 'delta': CANARY}
            yield {'type': 'response.failed', 'response': {'id': 'resp_fixture123', 'error': {
                'code': 'rate_limit_exceeded', 'type': 'server_error', 'message': CANARY}}}
        else:
            yield {'type': 'error', 'error': {'type': CANARY, 'message': CANARY}}
    try:
        responses.completed_response(observer.events(events()) if observed else events())
        raise AssertionError('Fixture must fail')
    except (oauth.SafeError, TimeoutError) as error:
        observer.record['elapsed_ms'] = int(1000*(time.perf_counter()-observer.started))
        if observed and observer.record['failure_surface'] == 'NOT_RECORDED':
            observer.record['failure_surface'] = 'TIMEOUT' if kind == 'timeout' else 'STREAM_ENDED'
        return signature(error), observer.record

def main():
    tracked = [WORKSPACE/'rosa-research/src/rosa_auth/oauth.py',
               WORKSPACE/'rosa-research/src/rosa_auth/responses.py',
               REPO/'experiments/macro_m4/recovery.py']
    before = {str(path.relative_to(WORKSPACE)): digest(path) for path in tracked}
    checks = []
    for status in (503, 429):
        payload = json.dumps({'error': {'code': 'fixture_provider_code', 'type': 'server_error',
                                       'message': CANARY}}).encode()
        class Opener:
            def open(self, request, timeout):
                raise HTTPError('https://invalid.test', status, 'fixture', {}, BytesIO(payload))
        with patch.object(oauth, 'build_opener', return_value=Opener()):
            try:
                oauth.open_request(oauth.Request('https://invalid.test'))
                raise AssertionError('Expected HTTP fixture failure')
            except oauth.SafeError as error:
                observed = signature(error)
                assert observed['status'] == status and observed['retry_eligible'] == (status == 503)
                assert set(vars(error)) == {'code', 'status'}
                checks.append({'fixture': 'HTTP_'+str(status), 'golden': observed,
                    'http_status_captured': True, 'provider_original_code_recoverable': False,
                    'provider_type_recoverable': False, 'boundary_information_lost': True})
    for kind in ('failed_event_with_code', 'error_without_code', 'midstream_truncation', 'timeout'):
        golden, _ = invoke_stream(kind, False)
        actual, record = invoke_stream(kind, True)
        assert actual == golden
        assert set(record) == ALLOWED
        assert all(len(value) <= 64 for value in record.values() if isinstance(value, str))
        assert CANARY not in json.dumps(record)
        if kind == 'failed_event_with_code':
            assert record['provider_code'] == 'rate_limit_exceeded'
            assert record['provider_type'] == 'server_error'
            assert record['stream_events_received'] == 3 and record['output_events_arrived']
        checks.append({'fixture': kind, 'golden_equivalence': True, 'golden': golden,
                       'sanitized_record': record, 'canary_absent': True})
    after = {str(path.relative_to(WORKSPACE)): digest(path) for path in tracked}
    assert before == after
    result = dict(status='BLOCKED_SOURCE_HOOK_APPROVAL_REQUIRED', six_boundary_fixtures_passed=True,
        instrumentation_complete=False, integrated_transport=False,
        evidence='Unchanged open_request consumes HTTP error body and preserves only sanitized code/status. Provider type and original unrecognized code cannot be recovered by an outer wrapper.',
        tests=checks, source_hashes_before=before, source_hashes_after=after,
        canary_present_in_records=False, network_requests=0, model_requests=0,
        retry_logic_changed=False, parser_changed=False, protected_source_changed=False,
        proposed_diff_applied=False)
    assert CANARY not in json.dumps(result)
    write('instrumentation/observability-boundary-tests.json', result)
    print(json.dumps({key: result[key] for key in ('status', 'six_boundary_fixtures_passed',
        'instrumentation_complete', 'network_requests', 'model_requests', 'protected_source_changed')}))

if __name__ == '__main__':
    main()
