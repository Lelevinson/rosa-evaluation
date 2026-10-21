"""Live readiness smoke: native Ollama tools, then custom-only ROSA with Phoenix.

All exposed tools read fixed in-memory fixtures. This is not a task benchmark.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import time
from typing import Literal
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4

from .config import ROOT, checkout, phoenix_project, run_dir
from .tracing import trace_run


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default=os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434'))
    parser.add_argument('--model', default=os.getenv('OLLAMA_MODEL', 'qwen3.5:9b'))
    parser.add_argument('--num-ctx', type=int, default=4096)
    parser.add_argument('--use-mmap', action=argparse.BooleanOptionalAction,
                        default={'true': True, 'false': False}.get(os.getenv('OLLAMA_USE_MMAP', '').lower()))
    args = parser.parse_args()
    source = checkout('research')
    sys.path.insert(0, str(source / 'src'))
    from langchain_core.tools import tool
    from langchain_core.utils.function_calling import convert_to_openai_tool
    from rosa_backends import create_model
    from rosa import ROSA

    opener = build_opener(ProxyHandler({}))

    def api(path, payload=None):
        request = Request(args.base_url.rstrip('/') + path,
                          data=None if payload is None else json.dumps(payload).encode(),
                          headers={'Content-Type': 'application/json'})
        with opener.open(request, timeout=300) as response:
            return json.load(response)

    metadata = {'run_id': str(uuid4()), 'mode': 'qwen-readiness-smoke',
                'model': args.model, 'base_url': args.base_url,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'num_ctx': args.num_ctx, 'num_predict': 256, 'temperature': 0,
                'seed': 42, 'reasoning': False, 'use_mmap': args.use_mmap,
                'fixture': 'fixed-in-memory-no-actuation'}
    output = run_dir(metadata['run_id'])
    output.mkdir(parents=True)
    for label, path in (('research', source), ('evaluation', ROOT)):
        metadata[f'{label}_commit'] = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        diff = subprocess.check_output(['git', '-C', str(path), 'diff', '--no-ext-diff'], text=True)
        (output / f'{label}.patch').write_text(diff)
    metadata['source_sha256'] = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((source / 'src/rosa').rglob('*.py'))
    }
    metadata['probe_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    evidence = {'metadata': metadata, 'status': 'RUNNING', 'native': [], 'rosa': None}

    def save():
        (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')

    save()
    invocations = []

    @tool
    def get_robot_health(robot_id: Literal['mock-robot']) -> dict:
        """Read health and active arm of the named mock robot."""
        invocations.append({'tool': 'get_robot_health', 'args': {'robot_id': robot_id}})
        return {'robot_id': robot_id, 'battery_percent': 73, 'active_arm': 'left', 'faulted': False, 'source': 'mock'}

    @tool
    def get_gripper_state(arm: Literal['left', 'right']) -> dict:
        """Read the specified mock arm's gripper state."""
        invocations.append({'tool': 'get_gripper_state', 'args': {'arm': arm}})
        return {'arm': arm, 'state': 'open', 'source': 'mock'}

    try:
        metadata['ollama_version'] = api('/api/version')['version']
        model = next(item for item in api('/api/tags')['models'] if item['name'] == args.model)
        metadata['model_digest'] = model['digest']
        metadata['model_size_bytes'] = model['size']
        metadata['model_details'] = model.get('details', {})

        def native_case(name, prompt, tools, expected):
            invocations.clear()
            messages = [{'role': 'user', 'content': prompt}]
            record = {'case': name, 'initial_messages': list(messages), 'turns': [], 'status': 'RUNNING'}
            evidence['native'].append(record)
            for turn in range(len(expected) + 1):
                started = time.perf_counter()
                result = api('/api/chat', {'model': args.model, 'stream': False, 'think': False,
                    'messages': messages, 'tools': [convert_to_openai_tool(t) for t in tools],
                    'options': {'temperature': 0, 'num_ctx': args.num_ctx, 'num_predict': 256, 'seed': 42,
                                **({} if args.use_mmap is None else {'use_mmap': args.use_mmap})},
                    'keep_alive': '5m'})
                message = result['message']
                # Keep model text and native calls; omit any backend reasoning payload.
                message = {key: message[key] for key in ('role', 'content', 'tool_calls') if key in message}
                record['turns'].append({'message': message, 'wall_seconds': time.perf_counter() - started,
                    'prompt_eval_count': result.get('prompt_eval_count'), 'eval_count': result.get('eval_count'),
                    'done': result.get('done'), 'done_reason': result.get('done_reason'),
                    'load_duration_ns': result.get('load_duration'), 'eval_duration_ns': result.get('eval_duration')})
                save()
                if not result.get('done') or result.get('done_reason') == 'length':
                    raise AssertionError(f'{name}: generation did not finish within its output budget')
                calls = message.get('tool_calls', [])
                if turn == len(expected):
                    if calls or '73' not in message.get('content', ''):
                        raise AssertionError(f'{name}: expected a grounded final battery answer')
                    if name == 'dependent-two-tool' and 'open' not in message['content'].lower():
                        raise AssertionError('Missing grounded gripper state')
                    record['status'] = 'PASS'
                    break
                if len(calls) != 1:
                    raise AssertionError(f'{name}: expected one native tool call, received {len(calls)}')
                function = calls[0]['function']
                wanted_name, wanted_args = expected[turn]
                if function['name'] != wanted_name or function['arguments'] != wanted_args:
                    raise AssertionError(f'{name}: wrong tool, order, or arguments: {function}')
                selected = next(t for t in tools if t.name == wanted_name)
                value = selected.invoke(function['arguments'])
                record['turns'][-1]['tool_result'] = value
                messages.extend([message, {'role': 'tool', 'tool_name': wanted_name, 'content': json.dumps(value)}])
            record['invocations'] = list(invocations)
            print(f'PASS native {name}', flush=True)
            save()

        native_case('single-tool',
            'Use get_robot_health to read mock-robot battery. Then report the measured battery percentage.',
            [get_robot_health], [('get_robot_health', {'robot_id': 'mock-robot'})])
        native_case('dependent-two-tool',
            'First read health for mock-robot. Its result tells you the active arm. '
            'Only after that result, read that arm gripper state. Report the battery percentage and gripper state.',
            [get_robot_health, get_gripper_state],
            [('get_robot_health', {'robot_id': 'mock-robot'}), ('get_gripper_state', {'arm': 'left'})])

        invocations.clear()
        llm = create_model('ollama', model=args.model, base_url=args.base_url,
                           num_ctx=args.num_ctx, use_mmap=args.use_mmap)
        agent = ROSA(2, llm, tools=[get_robot_health], load_default_tools=False,
                     streaming=False, accumulate_chat_history=False, max_iterations=3)
        if agent.tool_names != ('get_robot_health',):
            raise AssertionError(f'Unexpected ROSA tool registry: {agent.tool_names}')
        started = time.perf_counter()
        with trace_run(True, project=phoenix_project(), metadata=metadata) as span:
            answer = agent.invoke('Use get_robot_health for mock-robot and report its measured battery percentage.')
            span.set_attribute('output.value', answer)
            evidence['rosa'] = {'answer': answer, 'tool_names': agent.tool_names,
                                'invocations': list(invocations), 'wall_seconds': time.perf_counter() - started,
                                'trace_id': format(span.get_span_context().trace_id, '032x')}
            if '73' not in answer or invocations != [{'tool': 'get_robot_health', 'args': {'robot_id': 'mock-robot'}}]:
                raise AssertionError('ROSA did not complete exactly the required mock call and grounded answer')
        evidence['runtime_models'] = api('/api/ps')
        evidence['status'] = 'PASS'
        print('PASS custom-only ROSA tool round trip with Phoenix tracing', flush=True)
    except Exception as error:
        evidence['status'] = 'FAIL'
        evidence['error'] = {'type': type(error).__name__, 'message': str(error)}
        for record in evidence['native']:
            if record['status'] == 'RUNNING':
                record['status'] = 'FAIL'
        raise
    finally:
        save()
        print(f'Report: {output / "result.json"}', flush=True)


if __name__ == '__main__':
    main()
