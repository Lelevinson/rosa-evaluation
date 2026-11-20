"""Bounded, simulator-free investigation. Never executes any model tool call."""
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import time
from urllib.request import Request, urlopen
import zipfile

import httpx
import ollama
from ollama._types import ChatRequest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
import langchain_ollama.chat_models as adapter
import importlib.metadata

ROOT = Path('/work')
BASE = ROOT / 'integration-check-20261117'
ENDPOINT = 'http://127.0.0.1:11439'
LLAMA = 'llama3.1:8b-instruct-q4_K_M'
GRANITE = 'granite3.3:8b'
MODELS = ['qwen3.5:9b', LLAMA, GRANITE]
COMMON = 'Use the supplied tool when asked. Do not invent its result.'
NATIVE = {
    LLAMA: 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables.',
    GRANITE: "When a tool is required to answer the user's query, respond only with <|tool_call|> followed by a JSON list of tools used. If a tool does not exist in the provided list of tools, notify the user that you do not have the ability to fulfill the request."
}
PROBE = {'type': 'function', 'function': {'name': 'lab_probe', 'description': 'Harmless synthetic signature. Never executed.',
    'parameters': {'type': 'object', 'properties': {'value': {'type': 'string'}}, 'required': ['value']}}}
OBSERVE = {'type': 'function', 'function': {'name': 'lab_observe', 'description': 'A synthetic fixture observation, not a physical sensor.',
    'parameters': {'type': 'object', 'properties': {}}}}
REPORT = {'type': 'function', 'function': {'name': 'submit_report',
    'description': 'Classify SUCCESS, FAILURE or UNKNOWN and cite the supplied observation_id. Unknown observations never support SUCCESS.',
    'parameters': {'type': 'object', 'properties': {'status': {'type': 'string', 'enum': ['SUCCESS', 'FAILURE', 'UNKNOWN']},
        'observation_id': {'type': 'string'}}, 'required': ['status', 'observation_id']}}}
READ = {'type': 'function', 'function': {'name': 'read_state', 'description': 'Read the synthetic fixture nodes; no device is connected.',
    'parameters': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['nodes']}}}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


spec = importlib.util.spec_from_file_location('frozen_lab', ROOT / 'study/lab_study.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def verify_old():
    original = json.loads((ROOT / 'study/freeze.json').read_text())
    for name, expected in original['files'].items():
        assert sha(ROOT / name) == expected, name
    return original


def normalize(calls):
    return [{'name': c['function']['name'], 'args': c['function'].get('arguments', {})} for c in calls]


class Recorder(httpx.BaseTransport):
    def __init__(self):
        self.inner = httpx.HTTPTransport(retries=0)
        self.requests = []
        self.responses = []

    def handle_request(self, request):
        assert request.url.host == '127.0.0.1' and request.url.port == 11439
        self.requests.append(json.loads(request.content))
        response = self.inner.handle_request(request)
        payload = response.read()
        try:
            rows = [json.loads(payload)]
        except json.JSONDecodeError:
            rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
        self.responses.append({'status': response.status_code, 'objects': rows})
        return response

    def close(self):
        self.inner.close()


def model_for(model, named=False):
    value = lab.configured_model(model, max_output=512)
    if named:
        class NamedToolResult(type(value)):
            def _convert_messages_to_ollama_messages(self, messages):
                converted = super()._convert_messages_to_ollama_messages(messages)
                for message, row in zip(messages, converted):
                    if isinstance(message, ToolMessage):
                        name = message.name or message.additional_kwargs.get('name')
                        if name:
                            row['tool_name'] = name
                return converted
        value = NamedToolResult(**value.model_dump())
    return value


def system_messages(text):
    return [SystemMessage(content=text)] if text else []


def prompt(job):
    tools = job['tools']
    system = job['system']
    if job.get('persistent'):
        system += '\nAvailable function schemas (retain these after tool results):\n' + json.dumps(tools, sort_keys=True)
    messages = system_messages(system)
    kind = job['kind']
    if kind == 'probe':
        messages.append(HumanMessage(content='Call lab_probe once with value exactly ready. Return a native tool call, not a code block or a description.'))
    elif kind == 'read':
        messages.append(HumanMessage(content='Call read_state once with nodes exactly ["/lab_stub"]. This is an interface test; no physical device is connected.'))
    else:
        status = job['expected']['args']['status']
        messages += [HumanMessage(content='Use the synthetic observation result to submit a report. Do not acquire another observation. Use a real tool call, not a prose report.'),
            AIMessage(content='', tool_calls=[{'name': 'lab_observe', 'args': {}, 'id': 'fixture-read'}]),
            ToolMessage(content=json.dumps({'synthetic_fixture': True, 'observation_id': 'obs-lab-1',
                'goal_reached': True if status == 'SUCCESS' else None,
                'observations_available': status == 'SUCCESS'}), tool_call_id='fixture-read',
                additional_kwargs={'name': 'lab_observe'})]
        if kind == 'feedback':
            messages += [AIMessage(content='', tool_calls=[{'name': 'submit_report',
                'args': {'classification': status, 'observation_id': 'obs-lab-1'}, 'id': 'fixture-error'}]),
                ToolMessage(content=json.dumps({'code': 'schema_validation', 'corrections_remaining': 2,
                    'details': [{'field': 'status', 'reason': 'missing'},
                        {'field': 'classification', 'reason': 'extra_forbidden'}], 'rejected': True}),
                    tool_call_id='fixture-error', additional_kwargs={'name': 'submit_report'})]
    return messages


def schedule():
    jobs = []
    def add(model, label, channel, system, kind='probe', stream=False, persistent=False, named=False, status='SUCCESS'):
        tools = [PROBE] if kind == 'probe' else ([READ] if kind == 'read' else [OBSERVE, REPORT])
        expected = {'name': 'lab_probe', 'args': {'value': 'ready'}} if kind == 'probe' else (
            {'name': 'read_state', 'args': {'nodes': ['/lab_stub']}} if kind == 'read' else
            {'name': 'submit_report', 'args': {'status': status, 'observation_id': 'obs-lab-1'}})
        jobs.append({'id': f'{len(jobs)+1:02d}-{label}-{channel}', 'model': model, 'label': label,
            'channel': channel, 'system': system, 'kind': kind, 'stream': stream,
            'persistent': persistent, 'named': named, 'tools': deepcopy(tools), 'expected': expected})
    for channel in ['raw', 'adapter']:
        add(MODELS[0], 'positive-control', channel, COMMON)
    for model in [LLAMA, GRANITE]:
        for system_label, system in [('none', ''), ('generic', COMMON), ('native', COMMON + ' ' + NATIVE[model])]:
            for stream in [False, True]:
                for channel in ['raw', 'adapter']:
                    add(model, f'probe-{system_label}-stream{int(stream)}', channel, system, stream=stream)
        for kind, status in [('report', 'SUCCESS'), ('report', 'UNKNOWN'), ('read', 'SUCCESS')]:
            for persistent in [False, True]:
                add(model, f'{kind}-{status}-schemas{int(persistent)}', 'adapter', COMMON,
                    kind=kind, persistent=persistent, status=status)
        for persistent in [False, True]:
            add(model, f'feedback-schemas{int(persistent)}', 'adapter', COMMON, kind='feedback', persistent=persistent)
        add(model, 'report-SUCCESS-toolname', 'adapter', COMMON, kind='report', named=True)
        for status in ['SUCCESS', 'UNKNOWN']:
            add(model, f'combined-{status}', 'adapter', COMMON + ' ' + NATIVE[model],
                kind='report', persistent=True, status=status)
    assert len(jobs) == 48
    return jobs


def zero_network():
    from rosa_reliability.reference import ReferenceReportArgs
    from rosa_reliability.tools import ReadArgs
    for args in [{'status': 'SUCCESS', 'observation_id': 'obs-lab-1'}, {'status': 'UNKNOWN', 'observation_id': 'obs-lab-1'}]:
        ReferenceReportArgs.model_validate(args)
    ReadArgs.model_validate({'nodes': ['/lab_stub']})
    captured = []
    def mock(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={'model': LLAMA, 'message': {'role': 'assistant', 'content': 'fixture'},
            'done': True, 'done_reason': 'stop', 'prompt_eval_count': 1, 'eval_count': 1})
    m = model_for(LLAMA)
    m._client = ollama.Client(host=ENDPOINT, transport=httpx.MockTransport(mock))
    m.invoke([HumanMessage(content='zero-network fixture')])
    m.invoke([HumanMessage(content='zero-network fixture')], stream=False)
    job = next(j for j in schedule() if j['model'] == LLAMA and j['kind'] == 'report')
    messages = prompt(job)
    baseline = ChatRequest(**m._chat_params(messages, tools=job['tools'], stream=False)).model_dump(exclude_none=True)
    named = model_for(LLAMA, named=True)
    named_wire = ChatRequest(**named._chat_params(messages, tools=job['tools'], stream=False)).model_dump(exclude_none=True)
    versions = {name: importlib.metadata.version(name) for name in ['langchain-ollama', 'langchain-core', 'ollama', 'httpx']}
    source = {name: inspect.getsource(getattr(adapter.ChatOllama, name)) for name in
        ['_chat_params', '_convert_messages_to_ollama_messages', '_create_chat_stream', '_iterate_over_stream']}
    (BASE / 'pinned_adapter_source.json').write_text(json.dumps(source, indent=2))
    llama_template = json.loads((ROOT / 'preparation/model-llama3.1_8b-instruct-q4_K_M.json').read_text())['template']
    granite_template = json.loads((ROOT / 'preparation/model-granite3.3_8b.json').read_text())['template']
    assert 'if and $.Tools $last' in llama_template
    assert 'if eq .Role "user"' in llama_template
    assert '{{- if eq $system "" }}' in granite_template
    assert 'respond only with <|tool_call|>' in granite_template
    for label, value in [('llama-template.txt', llama_template), ('granite-template.txt', granite_template)]:
        (BASE / label).write_text(value)
    output = {'zero_actual_network_requests': True, 'mock_request_count': len(captured), 'versions': versions,
        'constructor_streaming_field_present': 'streaming' in type(m).model_fields,
        'wire_stream_from_constructor_streaming_false': captured[0]['stream'],
        'wire_stream_with_explicit_stream_false': captured[1]['stream'],
        'baseline_tool_result_wire': baseline['messages'][-1],
        'named_tool_result_wire': named_wire['messages'][-1],
        'strict_schema_examples_pass': True,
        'llama_schema_render_branch': 'Function schema block is inside user-role and last-message conditional.',
        'granite_native_guidance_branch': 'Default tool-format instruction is inside empty-custom-system conditional.'}
    assert captured[0]['stream'] is True and captured[1]['stream'] is False
    assert 'tool_name' not in baseline['messages'][-1]
    assert named_wire['messages'][-1]['tool_name'] == 'lab_observe'
    write(BASE / 'zero-network-results.json', output)
    m._client._client.close()
    return output


def run_job(job):
    messages = prompt(job)
    llm = model_for(job['model'], named=job['named'])
    serialized = ChatRequest(**llm._chat_params(messages, tools=job['tools'], stream=job['stream'])).model_dump(exclude_none=True)
    record = {'job': job, 'sdk_serialized_expected_request': serialized, 'started_unix': time.time()}
    started = time.monotonic()
    recorder = None
    try:
        if job['channel'] == 'raw':
            req = Request(ENDPOINT + '/api/chat', data=json.dumps(serialized).encode(), headers={'Content-Type': 'application/json'})
            with urlopen(req, timeout=180) as response:
                payload = response.read()
                try:
                    objects = [json.loads(payload)]
                except json.JSONDecodeError:
                    objects = [json.loads(line) for line in payload.splitlines() if line.strip()]
            record['wire_request'] = serialized
            record['server_objects'] = objects
            parsed = [call for obj in objects for call in adapter._get_tool_calls_from_response(obj)]
            record['parsed_calls'] = [{'name': c['name'], 'args': c['args']} for c in parsed]
        else:
            recorder = Recorder()
            llm._client = ollama.Client(host=ENDPOINT, timeout=180, transport=recorder)
            answer = llm.bind_tools(job['tools']).invoke(messages, stream=job['stream'])
            assert len(recorder.requests) == 1
            record['wire_request'] = recorder.requests[0]
            assert record['wire_request'] == serialized, 'Adapter request differs from zero-network expected body'
            record['server_objects'] = recorder.responses[0]['objects']
            record['parsed_calls'] = [{'name': c['name'], 'args': c['args']} for c in answer.tool_calls]
            record['adapter_answer'] = answer.model_dump(mode='json')
        objects = record['server_objects']
        native = [c for obj in objects for c in obj.get('message', {}).get('tool_calls', [])]
        record['server_native_calls'] = normalize(native)
        record['parser_preserved_server_calls'] = record['parsed_calls'] == record['server_native_calls']
        record['expected_call_match'] = record['parsed_calls'] == [job['expected']]
        record['server_content'] = ''.join(o.get('message', {}).get('content', '') for o in objects)
        record['final_metadata'] = {k:v for k,v in objects[-1].items() if k != 'message'}
        record['status'] = 'RETURNED'
    except Exception as error:
        record.update(status='ERROR', error_type=type(error).__name__, error=str(error)[:200])
        if recorder:
            record['captured_requests'] = recorder.requests
            record['captured_responses'] = recorder.responses
    finally:
        record['wall_seconds'] = time.monotonic() - started
        if recorder:
            recorder.close()
    write(BASE / 'requests' / (job['id'] + '.json'), record)
    return record


def finish(state):
    verify_old()
    freeze = json.loads((BASE / 'freeze.json').read_text())
    for name, expected in freeze['files'].items():
        assert sha(BASE / name) == expected
    rows = state['results']
    summary = {'scheduled': 48, 'reserved_requests': state['reserved_requests'],
        'recorded': len(rows), 'phase': state['phase'], 'native_tool_executions': 0,
        'original_69_source_hashes_unchanged': True,
        'usage': {f: sum(r.get('final_metadata',{}).get(f,0) for r in rows) for f in ['prompt_eval_count','eval_count']},
        'table': [{k:r['job'][k] for k in ['id','model','label','channel','stream']} |
            {k:r.get(k) for k in ['status','expected_call_match','parser_preserved_server_calls','wall_seconds']} for r in rows]}
    write(BASE / 'analysis.json', summary)
    paths = [p for p in BASE.rglob('*') if p.is_file() and p.suffix != '.zip' and p.name != 'operator.log']
    manifest = {str(p.relative_to(BASE)):sha(p) for p in sorted(paths)}
    target = BASE / 'LAB_INTEGRATION_DIAGNOSTICS_2026-11-17.zip'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as out:
        for name in manifest:
            out.write(BASE / name, name)
        out.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':manifest},indent=2))
    with zipfile.ZipFile(target) as check:
        assert check.testzip() is None
        for name, expected in manifest.items():
            assert hashlib.sha256(check.read(name)).hexdigest()==expected
    write(BASE / 'archive-verification.json',{'sha256':sha(target),'bytes':target.stat().st_size,
        'content_files':len(manifest),'all_hashes_pass':True})


def main():
    assert not (BASE / 'freeze.json').exists(), 'Refusing duplicate diagnostics launch'
    original = verify_old()
    state = {'phase':'PREPARING','reserved_requests':0,'max_requests':48,'results':[],'started_unix':time.time()}
    write(BASE / 'status.json',state)
    zero_network()
    jobs = schedule()
    files = {str(p.relative_to(BASE)):sha(p) for p in (BASE / 'source').iterdir() if p.is_file()}
    write(BASE / 'freeze.json', {'date':'2026-11-17','files':files,'schedule':jobs,
        'original_freeze_sha256':sha(ROOT/'study/freeze.json'),
        'model_digests':{m:original['model_metadata'][m]['digest'] for m in MODELS},
        'max_requests':48,'max_output_per_call':512,'robot_executions':0})
    deadline = time.monotonic()+1800
    try:
        for model in MODELS:
            state['model']=model
            state['phase']='RUNNING'
            write(BASE/'status.json',state)
            try:
                for job in [j for j in jobs if j['model']==model]:
                    assert time.monotonic()<deadline, 'Diagnostic window exhausted'
                    assert state['reserved_requests']<48
                    state['reserved_requests']+=1
                    state['current']=job['id']
                    write(BASE/'status.json',state)
                    row=run_job(job)
                    state['results'].append(row)
                    write(BASE/'status.json',state)
                    print(job['id'],model,row['status'],'match',row.get('expected_call_match'),flush=True)
            finally:
                write(BASE/(model.replace(':','_')+'-unload.json'),lab.api('/api/generate',{'model':model,'keep_alive':0},timeout=60))
        state['phase']='COMPLETE'
    except Exception as error:
        state.update(phase='STOPPED',error_type=type(error).__name__,error=str(error)[:200])
    finally:
        state['finished_unix']=time.time()
        write(BASE/'status.json',state)
        finish(state)


if __name__=='__main__':
    main()
