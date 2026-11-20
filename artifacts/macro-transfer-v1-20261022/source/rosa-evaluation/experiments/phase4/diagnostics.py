"""Small fixed native requests; performance profiles never change behavior settings."""
from datetime import datetime, timezone
import json
import os
import platform
import sys
from importlib.metadata import distributions
import subprocess
import time
from urllib.request import ProxyHandler, Request, build_opener
from dotenv import load_dotenv
from ..config import ROOT
from .runner import CAMPAIGN


def main():
    load_dotenv(ROOT / '.env')
    endpoint = os.environ['OLLAMA_BASE_URL']
    model = os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
    opener = build_opener(ProxyHandler({}))

    def request(path, data=None):
        encoded = None if data is None else json.dumps(data).encode()
        with opener.open(Request(endpoint + path, data=encoded, headers={'Content-Type': 'application/json'}), timeout=240) as response:
            return json.load(response)

    from langchain_core.utils.function_calling import convert_to_openai_tool
    from .tools import NEW_CONTRACT, make_tools
    schemas = [convert_to_openai_tool(t) for t in make_tools(lambda *args, **kwargs: {})]
    prompt = {'model': model, 'stream': False, 'think': False, 'keep_alive': '10m',
              'messages': [{'role': 'system', 'content': NEW_CONTRACT},
                           {'role': 'user', 'content': 'Call observe_robot exactly once to inspect the robot. Do not call any other tool yet.'}],
              'tools': schemas}
    profiles = [('primary_8192_auto', {'num_ctx': 8192}),
                ('context_4096_auto', {'num_ctx': 4096}),
                ('offload_8192_24layers', {'num_ctx': 8192, 'num_gpu': 24})]
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'model': model,
              'behavioral_primary_unchanged': True, 'primary_profile': 'primary_8192_auto',
              'prompt': prompt, 'model_catalog': request('/api/tags'),
              'environment': {'linux_memory': subprocess.check_output(['free', '-m'], text=True),
                              'kernel': subprocess.check_output(['uname', '-a'], text=True),
                              'python': sys.version, 'platform': platform.platform(),
                              'packages': sorted([{'name': d.metadata.get('Name'), 'version': d.version} for d in distributions()], key=lambda d: str(d['name']))},
              'profiles': []}
    destination = CAMPAIGN / 'local-diagnostics.json'
    for name, options in profiles:
        request('/api/generate', {'model': model, 'keep_alive': 0})
        row = {'profile': name, 'options': {**options, 'temperature': 0, 'seed': 42, 'num_predict': 128, 'use_mmap': True},
               'started_utc': datetime.now(timezone.utc).isoformat(), 'turns': []}
        for repeat in range(3):
            started = time.perf_counter()
            try:
                value = request('/api/chat', {**prompt, 'options': row['options']})
                duration = value.get('eval_duration', 0)
                turns = {'repeat': repeat, 'wall_seconds': time.perf_counter() - started,
                         **{k: value.get(k) for k in ('total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'done_reason')},
                         'generation_tokens_per_second': value.get('eval_count', 0) * 1e9 / duration if duration else None,
                         'tool_names': [c.get('function', {}).get('name') for c in value.get('message', {}).get('tool_calls', [])]}
                turns['expected_tool_call'] = turns['tool_names'] == ['observe_robot']
                row['turns'].append(turns)
                row['loaded_model'] = request('/api/ps')
            except Exception as error:
                row['turns'].append({'repeat': repeat, 'error_type': type(error).__name__, 'wall_seconds': time.perf_counter() - started})
                break
        report['profiles'].append(row)
        destination.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'profile': name, 'turns': row['turns']}, indent=2), flush=True)
    request('/api/generate', {'model': model, 'keep_alive': 0})
    report['ended_utc'] = datetime.now(timezone.utc).isoformat()
    report['final_loaded_models'] = request('/api/ps')
    destination.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
