"""Same custom-only ROSA, prompts and mock tools for Ollama or SIWC.

This is a bounded integration test, not an independently scored task benchmark.
"""
import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Literal
from uuid import uuid4
from urllib.request import ProxyHandler, Request, build_opener

from .config import ROOT, checkout, phoenix_project, run_dir
from .tracing import trace_run


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['ollama', 'siwc'], required=True)
    parser.add_argument('--model')
    parser.add_argument('--base-url')
    parser.add_argument('--use-mmap', action=argparse.BooleanOptionalAction,
                        default={'true': True, 'false': False}.get(os.getenv('OLLAMA_USE_MMAP', '').lower()))
    parser.add_argument('--case', choices=['single', 'dependent', 'both'], default='both')
    parser.add_argument('--timeout', type=int, default=900, help='Browser sign-in timeout')
    parser.add_argument('--port', type=int, default=1455)
    parser.add_argument('--tracing', choices=['on', 'off'], default='on')
    args = parser.parse_args()
    if args.backend == 'siwc' and args.base_url:
        parser.error('The OAuth endpoint cannot be overridden')
    source = checkout('research')
    sys.path.insert(0, str(source / 'src'))
    from langchain_core.tools import tool
    from langchain_core.utils.function_calling import convert_to_openai_tool
    from rosa_backends import create_model, create_mock_agent
    from rosa_auth.oauth import SafeError
    from rosa_auth.responses import SiwcBackend
    from rosa_auth.session import interactive_session

    for name in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[name] = 'false'
    run_id = str(uuid4())
    output = run_dir(run_id)
    output.mkdir(parents=True)
    metadata = {'run_id': run_id, 'mode': 'shared-rosa-backend-readiness',
                'backend': args.backend, 'fixture': 'fixed-in-memory-no-actuation',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'agent': 'modified ROSA, custom-only tools', 'max_iterations': 4,
                'accumulate_chat_history': False, 'cache': False, 'episodic_memory': False}
    report = {'metadata': metadata, 'status': 'RUNNING', 'cases': [], 'credentials_persisted': False}
    for label, path in (('research', source), ('evaluation', ROOT)):
        metadata[label + '_commit'] = subprocess.check_output(
            ['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    metadata['source_sha256'] = {str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for package in ('rosa', 'rosa_auth', 'rosa_backends')
        for path in sorted((source / 'src' / package).rglob('*.py'))}
    metadata['probe_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    def save():
        (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')

    entries = []

    @tool
    def get_robot_health(robot_id: Literal['mock-robot']) -> dict:
        """Read health and active arm of the named mock robot."""
        entries.append({'name': 'get_robot_health', 'args': {'robot_id': robot_id}})
        return {'robot_id': robot_id, 'battery_percent': 73, 'active_arm': 'left', 'source': 'mock'}

    @tool
    def get_gripper_state(arm: Literal['left', 'right']) -> dict:
        """Read the specified mock arm's gripper state."""
        entries.append({'name': 'get_gripper_state', 'args': {'arm': arm}})
        return {'arm': arm, 'state': 'open', 'source': 'mock'}

    cases = [
        ('single', [get_robot_health],
         'Use get_robot_health for mock-robot and report its measured battery percentage.',
         [{'name': 'get_robot_health', 'args': {'robot_id': 'mock-robot'}}]),
        ('dependent', [get_robot_health, get_gripper_state],
         'First read health for mock-robot. Its result tells you the active arm. '
         'Only after that result, read that arm gripper state. Report the battery percentage and gripper state.',
         [{'name': 'get_robot_health', 'args': {'robot_id': 'mock-robot'}},
          {'name': 'get_gripper_state', 'args': {'arm': 'left'}}]),
    ]
    llm = None
    transport = None
    context = (interactive_session(request_budget=8, timeout=args.timeout, port=args.port, status=report)
               if args.backend == 'siwc' else nullcontext(None))
    save()
    print(f'Run: {run_id}\nReport: {output / "result.json"}', flush=True)
    try:
        with context as session:
            if session is not None:
                transport = SiwcBackend(session.tokens['access_token'], request_budget=8)
                catalog = transport.models()
                report['models'] = catalog
                model = args.model or (catalog[0]['slug'] if catalog else None)
                if not model or model not in {item['slug'] for item in catalog}:
                    raise SafeError('requested_model_not_in_account_catalog')
                llm = create_model('siwc', model=model, siwc_transport=transport)
                metadata['wire_settings'] = {'store': False, 'stream': True, 'system_role': 'developer',
                                             'tool_namespace': 'rosa_tools', 'request_budget': 8,
                                             'sampling': 'account model defaults; overrides unsupported'}
            else:
                model = args.model or os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
                base_url = args.base_url or os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
                local_http = build_opener(ProxyHandler({}))
                def local_json(path):
                    with local_http.open(Request(base_url.rstrip('/') + path), timeout=10) as response:
                        return json.load(response)
                catalog = local_json('/api/tags')['models']
                installed = next((item for item in catalog if item['name'] == model), None)
                if installed is None:
                    raise SafeError('requested_local_model_not_installed')
                metadata['ollama_version'] = local_json('/api/version')['version']
                metadata['model_digest'] = installed['digest']
                metadata['model_details'] = installed.get('details', {})
                llm = create_model('ollama', model=model, base_url=base_url, use_mmap=args.use_mmap)
                metadata['wire_settings'] = {'base_url': base_url, 'temperature': 0, 'seed': 42,
                                             'reasoning': False, 'num_ctx': 4096, 'num_predict': 256,
                                             'use_mmap': args.use_mmap}
            metadata['model'] = model
            save()
            with trace_run(args.tracing == 'on', project=phoenix_project(), metadata=metadata) as span:
                if span is not None:
                    report['trace_id'] = format(span.get_span_context().trace_id, '032x')
                for name, tools, query, expected in cases:
                    if args.case not in (name, 'both'):
                        continue
                    entries.clear()
                    agent = create_mock_agent(llm, tools, max_iterations=4)
                    started = time.perf_counter()
                    answer = agent.invoke(query)
                    passed = (entries == expected and '73' in answer and
                              (name != 'dependent' or 'open' in answer.lower()) and
                              not answer.startswith('An error occurred:'))
                    report['cases'].append({'name': name, 'query': query, 'tool_names': list(agent.tool_names),
                        'tool_schemas': [convert_to_openai_tool(t) for t in tools],
                        'observed_calls': list(entries), 'expected_calls': expected,
                        'answer': answer, 'wall_seconds': time.perf_counter() - started,
                        'status': 'PASS' if passed else 'FAIL'})
                    save()
                    print(f'{"PASS" if passed else "FAIL"} {args.backend} ROSA {name}', flush=True)
                    if not passed:
                        raise SafeError('shared_rosa_smoke_failed')
                if span is not None:
                    span.set_attribute('output.value', 'PASS: shared ROSA mock-tool integration')
            report['status'] = 'PASS'
    except KeyboardInterrupt:
        report['status'] = 'INTERRUPTED'
        report['error'] = {'code': 'local_interruption'}
        print('Interrupted; closing the test session.', flush=True)
    except SafeError as error:
        report['status'] = 'FAIL'
        report['error'] = {'code': error.code, 'http_status': error.status}
        print(f'FAIL: {error}', flush=True)
    except Exception as error:
        report['status'] = 'FAIL'
        report['error'] = {'code': 'unexpected_local_error', 'type': type(error).__name__}
        print(f'FAIL local exception type: {type(error).__name__}', flush=True)
    finally:
        if args.backend == 'siwc' and llm is not None:
            report['requests'] = llm.request_records
            llm.close()
        elif transport is not None:
            transport.close()
        save()
        print(f'Report: {output / "result.json"}', flush=True)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
