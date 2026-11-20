"""Post-hoc tool-binding diagnostic, not a repair or a scored robotics trial.

The protocol allows at most one 64-token probe/model. It runs only AFTER every
main trial finishes. No returned tool/code is ever executed, and no retry occurs.
"""
from pathlib import Path
import json
import subprocess
import time

from lab_study import MODELS, ROOT, api, configured_model, key, verify, write
from experiments.macro_capabilities_v2 import observability


def main():
    verify()
    operator = json.loads((ROOT / 'results/operator-status.json').read_text())
    if operator['phase'] != 'EXECUTION_COMPLETE':
        raise RuntimeError('Main campaign must finish first; no concurrent probe')
    for model in MODELS:
        checkpoint = json.loads((ROOT / 'results' / key(model) / 'ollama/checkpoint.json').read_text())
        if checkpoint['status'] != 'COMPLETE' or len(checkpoint['trials']) != 80:
            raise RuntimeError('Main schedule incomplete')
    destination = ROOT / 'post-run-tool-probe'
    destination.mkdir(exist_ok=False)
    observability.PROJECT = 'rosa-lab-postrun-tool-probe-20261117'
    schema = {'type': 'function', 'function': {'name': 'lab_probe',
        'description': 'A harmless function signature for a tool-binding check. It will not be executed.',
        'parameters': {'type': 'object', 'properties': {'value': {'type': 'string'}},
            'required': ['value']}}}
    messages = [{'role': 'system', 'content': 'Use the supplied tool when asked. Do not invent its result.'},
        {'role': 'user', 'content': 'Call lab_probe once with value exactly ready. Return a native tool call, not a code block or a description.'}]
    status = {'label': 'POST_HOC_DIAGNOSTIC', 'planned': 4, 'physical_slots_reserved': 0,
        'output_cap_per_call': 64, 'native_tool_executions': 0, 'results': [],
        'reason': 'Check simple tool-binding behavior after observing different main-task behavior; do not tune or replace main trials.'}
    write(destination / 'status.json', status)
    deadline = time.monotonic() + 900
    for model in MODELS:
        if time.monotonic() >= deadline:
            break
        folder = destination / key(model)
        folder.mkdir()
        status['physical_slots_reserved'] += 1
        write(destination / 'status.json', status)
        record = {'model': model, 'request': messages, 'tool_schema': schema,
            'output_cap': 64, 'executed_tools': 0}
        started = time.monotonic()
        try:
            with observability.trace_check(folder / 'trace.json',
                    {'stage': 'POST_HOC_TOOL_BINDING_PROBE', 'model': model}):
                llm = configured_model(model, max_output=64)
                message = llm.bind_tools([schema]).invoke(messages)
                record['response'] = message.model_dump(mode='json')
                record['valid_native_probe_call'] = (len(message.tool_calls) == 1 and
                    message.tool_calls[0]['name'] == 'lab_probe' and
                    message.tool_calls[0]['args'] == {'value': 'ready'})
            command = ("import experiments.macro_capabilities_v2.persisted as p; "
                "p.PROJECT='rosa-lab-postrun-tool-probe-20261117'; p.main()")
            check = subprocess.run([str(ROOT / 'runtime/envs/phoenix/bin/python'), '-B',
                '-c', command, '--folder', str(folder)], capture_output=True, text=True, timeout=60)
            (folder / 'audit.log').write_text(check.stdout + check.stderr)
            record['persisted_audit_pass'] = check.returncode == 0
            if check.returncode:
                raise RuntimeError('Diagnostic trace audit failed')
        except Exception as error:
            record['error_type'] = type(error).__name__
            record['http_status'] = getattr(error, 'status_code', None)
        finally:
            record['wall_seconds'] = time.monotonic() - started
            try:
                record['unload'] = api('/api/generate', {'model': model, 'keep_alive': 0}, timeout=60)
            except Exception as error:
                record['unload_error_type'] = type(error).__name__
        write(folder / 'result.json', record)
        status['results'].append(record)
        write(destination / 'status.json', status)
        time.sleep(3)
    status['complete'] = len(status['results']) == 4
    write(destination / 'status.json', status)
    print(json.dumps({'results': [{k: r.get(k) for k in
        ('model','valid_native_probe_call','error_type','persisted_audit_pass')} for r in status['results']],
        'native_tool_executions': 0}), flush=True)


if __name__ == '__main__':
    main()
