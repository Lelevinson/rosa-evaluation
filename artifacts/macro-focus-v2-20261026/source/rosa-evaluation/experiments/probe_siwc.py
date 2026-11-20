"""Interactive, memory-only OAuth + three-request hosted model smoke test."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

from .config import checkout, phoenix_project, run_dir
from .tracing import trace_operation, trace_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=1455)
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--model', help='Choose an exact account model slug; default: first displayed catalog entry.')
    parser.add_argument('--new-account', action='store_true', help='Create a separate registration without changing saved account identity.')
    args = parser.parse_args()
    sys.path.insert(0, str(checkout('research') / 'src'))
    from rosa_auth.oauth import (Attempt, ISSUER, LoginServer, MemorySession, SafeError,
                                 load_registration, request_json, save_registration)
    from rosa_auth.responses import MOCK_TOOLS, SiwcBackend, output_text, sanitized_response, validated_mock_call

    # Do not inherit external tracing settings during authentication or inference.
    for name in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[name] = 'false'
    run_id = str(uuid4())
    output = run_dir(run_id)
    output.mkdir(parents=True)
    report = {'run_id': run_id, 'mode': 'siwc-memory-only-readiness-smoke',
              'status': 'RUNNING', 'gates': {}, 'requests': [], 'credentials_persisted': False,
              'model_selection': 'explicit' if args.model else 'first_visible_catalog_entry',
              'request_budget': 3}
    metadata = {'run_id': run_id, 'mode': report['mode']}
    session = None
    backend = None

    def save():
        (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')

    def record_response(stage, response, elapsed):
        report['requests'].append(sanitized_response(response, stage, elapsed))
        save()

    save()
    print(f'Report: {output / "result.json"}', flush=True)
    try:
        discovery = request_json(ISSUER + '/.well-known/openid-configuration')
        session = MemorySession(discovery)
        registration_path = Path.home() / '.local/share/rosa-siwc/registration.json'
        registration = load_registration(registration_path)
        active = registration if not args.new_account else {'host_id': registration['host_id']}
        attempt = Attempt(active['host_id'], active.get('client_id'))
        try:
            server = LoginServer(attempt, discovery['authorization_endpoint'], args.port)
        except OSError:
            if args.port == 0:
                raise
            server = LoginServer(attempt, discovery['authorization_endpoint'], 0)
        report['status'] = 'WAITING_FOR_BROWSER_CONSENT'
        report['login_url'] = server.base_url + '/'
        save()
        print(f'Continue with ChatGPT: {server.base_url}/', flush=True)
        print('Complete browser consent. No tokens are printed or saved. At most three AI requests follow.', flush=True)
        deadline = time.monotonic() + args.timeout
        with server:
            while attempt.callback is None and time.monotonic() < deadline:
                server.handle_request()
        if attempt.callback is None:
            raise SafeError('browser_consent_timeout')
        report['status'] = 'VALIDATING_SIGN_IN'
        save()
        subject_hash = session.exchange(attempt, active.get('subject_hash'))
        report['gates']['validated_identity'] = 'PASS'
        new_record = {'host_id': active['host_id'], 'client_id': session.client_id, 'subject_hash': subject_hash}
        record_path = registration_path if not args.new_account else registration_path.with_name('registration-' + uuid4().hex[:12] + '.json')
        save_registration(record_path, new_record)
        if not session.has_plan_scope():
            raise SafeError('plan_usage_scope_not_granted')
        report['gates']['plan_usage_scope'] = 'PASS'
        report['status'] = 'TESTING_MODEL_ACCESS'
        save()
        print('PASS validated sign-in and ChatGPT plan-usage scope', flush=True)
        backend = SiwcBackend(session.tokens['access_token'])
        models = backend.models()
        report['models'] = models
        if not models:
            raise SafeError('no_visible_account_models')
        model = args.model or models[0]['slug']
        if model not in {entry['slug'] for entry in models}:
            raise SafeError('requested_model_not_in_account_catalog')
        report['selected_model'] = model
        metadata['model'] = model
        report['gates']['model_discovery'] = 'PASS'
        print(f'Testing account model: {model}', flush=True)
        save()

        # Authentication and token exchange occur outside this tracing context.
        # This transport uses urllib, so LangChain instrumentation never sees headers.
        with trace_run(True, project=phoenix_project(), metadata=metadata) as span:
            def infer(stage, history, tools=None):
                with trace_operation('siwc.' + stage, kind='LLM', model=model) as request_span:
                    response, elapsed = backend.respond(model, history, tools)
                    request_span.set_attribute('input.value', stage)
                    request_span.set_attribute('output.value', output_text(response))
                    for key, attribute in (('input_tokens', 'llm.token_count.prompt'),
                                           ('output_tokens', 'llm.token_count.completion'),
                                           ('total_tokens', 'llm.token_count.total')):
                        value = (response.get('usage') or {}).get(key)
                        if isinstance(value, int):
                            request_span.set_attribute(attribute, value)
                    record_response(stage, response, elapsed)
                    return response

            response = infer('text_completion', [{'role': 'user', 'content': 'Reply with exactly READY.'}])
            if output_text(response).strip() != 'READY':
                raise SafeError('text_smoke_wrong_answer')
            report['gates']['completed_text_inference'] = 'PASS'
            print('PASS streamed text inference through response.completed', flush=True)
            history = [{'role': 'user', 'content': 'Use mock_robot.get_robot_health for mock-robot. '
                        'After receiving the tool result, report the measured battery percentage. Do not invent readings.'}]
            response = infer('structured_tool_call', history, MOCK_TOOLS)
            with trace_operation('mock_robot.get_robot_health', kind='TOOL') as tool_span:
                call, value = validated_mock_call(response)
                tool_span.set_attribute('input.value', call['arguments'])
                tool_span.set_attribute('output.value', json.dumps(value))
            report['gates']['structured_tool_call'] = 'PASS'
            history.extend(response['output'])
            history.append({'type': 'function_call_output', 'call_id': call['call_id'], 'output': json.dumps(value)})
            response = infer('tool_result_continuation', history, MOCK_TOOLS)
            if any(item.get('type') == 'function_call' for item in response['output']) or '73' not in output_text(response):
                raise SafeError('tool_roundtrip_wrong_answer')
            report['gates']['tool_result_roundtrip'] = 'PASS'
            report['trace_id'] = format(span.get_span_context().trace_id, '032x')
            span.set_attribute('output.value', 'PASS: streamed text and structured mock-tool round trip')
            print('PASS structured mock tool call and grounded continuation', flush=True)
        report['status'] = 'PASS'
    except SafeError as error:
        report['status'] = 'FAIL'
        report['error'] = {'code': error.code, 'http_status': error.status}
        print(f'FAIL: {error}', flush=True)
    except Exception as error:
        # Do not expose arbitrary library exception strings, reprs, or HTTP bodies.
        report['status'] = 'FAIL'
        report['error'] = {'code': 'unexpected_local_error', 'type': type(error).__name__}
        print(f'FAIL local exception type: {type(error).__name__}', flush=True)
    finally:
        if backend is not None:
            backend.close()
        report['session_cleanup'] = session.revoke() if session is not None else 'NO_TOKEN_SESSION'
        save()
        print(f'Session cleanup: {report["session_cleanup"]}', flush=True)
        print(f'Report: {output / "result.json"}', flush=True)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
