"""Injected integration checks: real HTTP helper/parser/adapter/gate, fake wire.

The canary occurs only in fake inputs and in-memory return paths. Never retain
raw payloads, request headers or exception text in test records.
"""
from copy import deepcopy
import contextlib
import hashlib
from io import BytesIO, StringIO
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REV = STAGE.parent
REPO = STAGE.parents[3]
WORKSPACE = REPO.parent
sys.path[:0] = [str(WORKSPACE/'rosa-research/src'), str(REPO), str(STAGE)]
from rosa_auth import oauth, responses
from rosa_backends.chat_siwc import ChatSiwc
from experiments.macro_m4.recovery import RecoverableSiwc, transient
from observed_transport import ObservedRecoverableSiwc, Observation, FIELDS, NOT_RECORDED

spec = importlib.util.spec_from_file_location('unchanged_g1_dev_recovery_for_metadata_tests', REV/'stage-2/recovery.py')
g1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g1)

CANARY = 'CANARY_METADATA_SECRET_MUST_NOT_BE_RECORDED_8d2a9f'
FIXTURES = ('HTTP_503', 'HTTP_429', 'failed_event_with_code', 'error_without_code', 'midstream_truncation', 'timeout')
EVIDENCE = {'direct_transport': [], 'real_gate': []}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def error_signature(error):
    return dict(class_name=type(error).__name__, code=getattr(error, 'code', None),
                status=getattr(error, 'status', None), message_sha256=sha(str(error).encode()),
                retry_eligible=transient(error))


def events_for(kind):
    if kind == 'error_without_code':
        yield {'type': 'error', 'error': {'type': CANARY, 'message': CANARY, 'token': CANARY}}
        return
    yield {'type': 'response.created', 'response': {'id': 'resp_fixture123', 'private': CANARY}}
    if kind == 'timeout':
        raise TimeoutError('fixture_timeout')
    if kind in ('failed_event_with_code', 'midstream_truncation'):
        yield {'type': 'response.output_text.delta', 'delta': CANARY, 'secret': CANARY}
        if kind == 'failed_event_with_code':
            yield {'type': 'response.failed', 'response': {'id': 'resp_fixture123', 'error': {
                'code': 'rate_limit_exceeded', 'type': 'server_error', 'message': CANARY},
                'encrypted_reasoning': CANARY}}
        return
    if kind == 'malformed':
        yield ['non_object_event', CANARY]
        return
    if kind == 'unknown_provider_code':
        yield {'type': 'response.failed', 'response': {'id': CANARY,
            'error': {'code': CANARY, 'type': CANARY, 'message': CANARY}}}
        return
    yield {'type': 'response.completed', 'response': {'status': 'completed', 'id': 'resp_fixture123',
        'model': 'fixture-model', 'usage': {'input_tokens': 11, 'output_tokens': 7, 'total_tokens': 18},
        'output': [{'type': 'message', 'id': 'msg_fixture', 'content': [
            {'type': 'output_text', 'text': 'Fixture completed.'}]},
            {'type': 'reasoning', 'id': 'reason_fixture', 'encrypted_content': CANARY}]}}


class FakeStream:
    def __init__(self, kind):
        self.kind = kind
        self.closed = False
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.closed = True
    def __iter__(self):
        for event in events_for(self.kind):
            yield ('data: '+json.dumps(event)+'\n').encode()
            yield b'\n'


class FakeOpener:
    def __init__(self, kinds):
        self.kinds = list(kinds)
        self.wire_signatures = []
        self.streams = []
    def open(self, request, timeout):
        # Hash for equivalence only. Never save raw headers or body.
        wire = dict(url=request.full_url, method=request.get_method(),
            data_sha256=sha(request.data or b''),
            headers_sha256=sha(json.dumps(sorted(request.header_items())).encode()), timeout=timeout)
        self.wire_signatures.append(wire)
        kind = self.kinds.pop(0)
        if kind.startswith('HTTP_'):
            body = json.dumps({'error': {'code': CANARY, 'type': 'server_error',
                'message': CANARY, 'token': CANARY}, 'payload': CANARY}).encode()
            raise HTTPError('https://invalid.test', int(kind.split('_')[1]), 'fixture',
                            {'Private': CANARY}, BytesIO(body))
        if kind == 'connect_timeout':
            raise TimeoutError('fixture_connect_timeout')
        stream = FakeStream(kind)
        self.streams.append(stream)
        return stream


def run_direct(backend_class, kind, *, budget=3):
    transport = backend_class(CANARY, request_budget=budget)
    opener = FakeOpener([kind])
    with patch.object(oauth, 'build_opener', return_value=opener):
        try:
            result, elapsed = transport.respond('fixture-model', [{'role': 'user', 'content': CANARY}])
            outcome = dict(returned_sha256=sha(json.dumps(result, sort_keys=True).encode()), elapsed_nonnegative=elapsed >= 0)
        except BaseException as error:
            outcome = dict(error=error_signature(error))
    return dict(outcome=outcome, requests=transport.requests, availability=transport.availability_error,
                wire=opener.wire_signatures, streams_closed=all(s.closed for s in opener.streams)), transport


def run_gate(backend_class, kind, *, retries=0, request_budget=20):
    transport = backend_class(CANARY, request_budget=request_budget)
    opener = FakeOpener([kind, 'success'])
    checkpoints = []
    campaign = g1.Campaign(lambda value: checkpoints.append(value))
    campaign.retries = retries
    invocation = SimpleNamespace(session=SimpleNamespace(budget=SimpleNamespace(started=time.monotonic(), seconds=360)))
    gate = g1.LoggedGate(invocation, backend='siwc', campaign=campaign,
                        release=transport.release_transient_failure, sleeper=lambda _: None)
    model = ChatSiwc(model='fixture-model', backend=transport)
    with patch.object(oauth, 'build_opener', return_value=opener):
        try:
            message = gate.invoke(model, 'Synthetic fixture prompt.')
            outcome = {'content': message.content, 'usage': message.usage_metadata}
        except BaseException as error:
            outcome = {'error': error_signature(error)}
    campaign_view = campaign.snapshot()
    campaign_view.pop('elapsed_seconds')
    return dict(outcome=outcome, gate=gate.snapshot(), terminal_failure=gate.terminal_failure,
                campaign=campaign_view, transport_requests=transport.requests,
                availability=transport.availability_error, wire=opener.wire_signatures,
                streams_closed=all(s.closed for s in opener.streams)), transport


class ObservedTransportTests(unittest.TestCase):
    def assert_safe(self, records):
        self.assertNotIn(CANARY, json.dumps(records))
        for record in records:
            self.assertEqual(set(record), FIELDS)
            self.assertIs(type(record['elapsed_ms']), int)
            self.assertGreaterEqual(record['elapsed_ms'], 0)
            self.assertTrue(all(len(v) <= 64 for v in record.values() if isinstance(v, str)))

    def test_six_integrated_transport_goldens(self):
        expected_code = {'HTTP_503': 'http_error', 'HTTP_429': 'http_error',
            'failed_event_with_code': 'rate_limit_exceeded', 'error_without_code': 'error',
            'midstream_truncation': 'stream_ended_without_completed', 'timeout': None}
        for kind in FIXTURES:
            with self.subTest(kind=kind):
                golden, _ = run_direct(RecoverableSiwc, kind)
                actual, transport = run_direct(ObservedRecoverableSiwc, kind)
                self.assertEqual(actual, golden)
                self.assertEqual(actual['outcome']['error']['code'], expected_code[kind])
                self.assertEqual(actual['outcome']['error']['retry_eligible'], kind == 'HTTP_503')
                self.assertEqual(actual['requests'], 1)
                records = transport.error_metadata_records
                self.assertEqual(len(records), 1)
                self.assert_safe(records)
                r = records[0]
                if kind.startswith('HTTP_'):
                    self.assertEqual(r['failure_surface'], 'HTTP')
                    self.assertEqual(r['http_status'], int(kind.split('_')[1]))
                    self.assertEqual(r['provider_code'], NOT_RECORDED)
                    self.assertEqual(r['provider_type'], NOT_RECORDED)
                    self.assertEqual(r['stream_events_received'], NOT_RECORDED)
                    self.assertEqual(r['output_events_arrived'], NOT_RECORDED)
                elif kind == 'failed_event_with_code':
                    self.assertEqual(r['stream_event_type'], 'response.failed')
                    self.assertEqual(r['provider_code'], 'rate_limit_exceeded')
                    self.assertEqual(r['provider_type'], 'server_error')
                    self.assertEqual(r['stream_events_received'], 3)
                    self.assertIs(r['output_events_arrived'], True)
                    self.assertEqual(r['response_id'], 'resp_fixture123')
                elif kind == 'error_without_code':
                    self.assertEqual(r['stream_event_type'], 'error')
                    self.assertEqual(r['provider_code'], NOT_RECORDED)
                    self.assertEqual(r['provider_type'], NOT_RECORDED)
                    self.assertEqual(r['stream_events_received'], 1)
                    self.assertIs(r['output_events_arrived'], False)
                elif kind == 'midstream_truncation':
                    self.assertEqual(r['failure_surface'], 'STREAM_ENDED')
                    self.assertEqual(r['stream_events_received'], 2)
                    self.assertIs(r['output_events_arrived'], True)
                else:
                    self.assertEqual(r['failure_surface'], 'TIMEOUT')
                    self.assertEqual(r['stream_events_received'], 1)
                    self.assertIs(r['output_events_arrived'], False)
                EVIDENCE['direct_transport'].append(dict(fixture=kind, golden=golden, metadata=records,
                                                         golden_match=True, canary_absent=True))

    def test_real_chat_adapter_and_g1_gate_six_goldens(self):
        for kind in FIXTURES:
            with self.subTest(kind=kind):
                golden, _ = run_gate(RecoverableSiwc, kind)
                actual, transport = run_gate(ObservedRecoverableSiwc, kind)
                self.assertEqual(actual, golden)
                self.assert_safe(transport.error_metadata_records)
                self.assertEqual(actual['campaign']['reserved_requests'], 2 if kind == 'HTTP_503' else 1)
                self.assertEqual(actual['campaign']['infrastructure_retries'], 1 if kind == 'HTTP_503' else 0)
                self.assertEqual(actual['gate']['calls'], 2 if kind == 'HTTP_503' else 1)
                self.assertEqual(actual['gate']['decision_calls'], 1)
                EVIDENCE['real_gate'].append(dict(fixture=kind, golden=golden, golden_match=True,
                    metadata=transport.error_metadata_records, canary_absent=True))

    def test_success_return_and_reasoning_are_unchanged_and_not_recorded(self):
        golden, _ = run_direct(RecoverableSiwc, 'success')
        actual, transport = run_direct(ObservedRecoverableSiwc, 'success')
        self.assertEqual(actual, golden)
        self.assertEqual(transport.error_metadata_records, [])

    def test_unknown_code_and_id_are_not_copied(self):
        golden, _ = run_direct(RecoverableSiwc, 'unknown_provider_code')
        actual, transport = run_direct(ObservedRecoverableSiwc, 'unknown_provider_code')
        self.assertEqual(actual, golden)
        self.assert_safe(transport.error_metadata_records)
        r = transport.error_metadata_records[0]
        self.assertEqual([r[k] for k in ('provider_code', 'provider_type')], [NOT_RECORDED]*2)

    def test_connection_timeout_is_not_invented_from_sanitized_error(self):
        golden, _ = run_direct(RecoverableSiwc, 'connect_timeout')
        actual, transport = run_direct(ObservedRecoverableSiwc, 'connect_timeout')
        self.assertEqual(actual, golden)
        r = transport.error_metadata_records[0]
        self.assertEqual(r['failure_surface'], 'TRANSPORT')
        self.assertEqual(r['stream_events_received'], NOT_RECORDED)
        self.assertEqual(r['output_events_arrived'], NOT_RECORDED)

    def test_malformed_event_preserves_parser_exception(self):
        golden, _ = run_direct(RecoverableSiwc, 'malformed')
        actual, transport = run_direct(ObservedRecoverableSiwc, 'malformed')
        self.assertEqual(actual, golden)
        self.assertEqual(actual['outcome']['error']['class_name'], 'AttributeError')
        self.assert_safe(transport.error_metadata_records)

    def test_observer_preserves_event_object_identity_and_consumption(self):
        events = [{'type': 'response.created'}, {'type': 'response.output_text.delta', 'delta': CANARY}]
        observation = Observation()
        iterator = observation.events(iter(events))
        self.assertIs(next(iterator), events[0])
        self.assertIs(next(iterator), events[1])
        self.assertEqual(observation.record['stream_events_received'], 2)

    def test_elapsed_is_injected_measured_time(self):
        values = iter([10.0, 10.125])
        observation = Observation(clock=lambda: next(values))
        self.assertEqual(observation.finish(oauth.SafeError('http_error', 503))['elapsed_ms'], 125)

    def test_retry_reserve_and_request_ceiling_are_unchanged(self):
        for kwargs in ({'retries': 3}, {'request_budget': 1}):
            golden, _ = run_gate(RecoverableSiwc, 'HTTP_503', **kwargs)
            actual, transport = run_gate(ObservedRecoverableSiwc, 'HTTP_503', **kwargs)
            self.assertEqual(actual, golden)
            self.assert_safe(transport.error_metadata_records)
            self.assertIn('error', actual['outcome'])

    def test_second_failure_is_not_retried_again(self):
        # Exercise the original RecoveryGate's retried flag with two 503s.
        for cls in (RecoverableSiwc, ObservedRecoverableSiwc):
            transport = cls(CANARY, request_budget=20)
            opener = FakeOpener(['HTTP_503', 'HTTP_503', 'success'])
            campaign = g1.Campaign(lambda _: None)
            inv = SimpleNamespace(session=SimpleNamespace(budget=SimpleNamespace(started=time.monotonic(), seconds=360)))
            gate = g1.LoggedGate(inv, backend='siwc', campaign=campaign,
                release=transport.release_transient_failure, sleeper=lambda _: None)
            model = ChatSiwc(model='fixture-model', backend=transport)
            with patch.object(oauth, 'build_opener', return_value=opener), self.assertRaises(oauth.SafeError):
                gate.invoke(model, 'Synthetic fixture prompt.')
            self.assertEqual(transport.requests, 2)
            self.assertEqual(campaign.retries, 1)

    def test_unavailable_latch_and_close_do_not_spend_additional_requests(self):
        for cls in (RecoverableSiwc, ObservedRecoverableSiwc):
            _, transport = run_direct(cls, 'HTTP_429')
            with self.assertRaises(oauth.SafeError):
                transport.respond('fixture-model', [])
            self.assertEqual(transport.requests, 1)
            transport.close()
            self.assertIsNone(transport._access_token)
            self.assertIsNone(transport._token_provider)
            self.assertEqual(transport.availability_error['code'], 'oauth_session_closed')

    def test_metadata_property_does_not_expose_mutable_internal_records(self):
        _, transport = run_direct(ObservedRecoverableSiwc, 'HTTP_429')
        returned = transport.error_metadata_records
        returned[0]['provider_code'] = CANARY
        self.assert_safe(transport.error_metadata_records)


def main():
    output = HERE/'validation-attempt-01'
    output.mkdir(exist_ok=False)
    sources = [WORKSPACE/'rosa-research/src/rosa_auth/oauth.py',
        WORKSPACE/'rosa-research/src/rosa_auth/responses.py',
        WORKSPACE/'rosa-research/src/rosa_backends/chat_siwc.py',
        WORKSPACE/'rosa-research/src/rosa_reliability/macro_agent.py',
        REPO/'experiments/macro_m4/recovery.py', REV/'stage-2/recovery.py',
        HERE/'observed_transport.py']
    before = {str(p.relative_to(WORKSPACE)): sha(p.read_bytes()) for p in sources}
    log = StringIO()
    stdout = StringIO()
    def deny_network(*args, **kwargs):
        raise AssertionError('unexpected_real_network_attempt')
    with patch('socket.socket.connect', side_effect=deny_network), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(log):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ObservedTransportTests)
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    # Fail closed without writing any raw failure traceback if a secret escaped.
    retained_log = stdout.getvalue()+log.getvalue()
    report = dict(tests_run=result.testsRun, passed=result.wasSuccessful(), failures=len(result.failures),
        errors=len(result.errors), golden_cases=EVIDENCE, model_requests=0, network_requests=0,
        source_hashes_before=before,
        source_hashes_after={str(p.relative_to(WORKSPACE)): sha(p.read_bytes()) for p in sources})
    if CANARY in retained_log or CANARY in json.dumps(report):
        (output/'SECRET_EXCLUSION_FAILURE.txt').write_text('Canary exclusion failed. No unsafe output retained.\n')
        raise SystemExit(2)
    (output/'test.log').write_text(retained_log, encoding='utf-8')
    (output/'RESULTS.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('tests_run', 'passed', 'failures', 'errors', 'model_requests', 'network_requests')}))
    if not result.wasSuccessful() or report['source_hashes_before'] != report['source_hashes_after']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
