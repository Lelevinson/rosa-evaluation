"""Recover captured adapter responses with exact-body, zero-network replay.

Preserves the original diagnostic assertions and archive. No new model calls.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import zipfile

import httpx
import ollama

BASE = Path('/work/integration-check-20261117')
spec = importlib.util.spec_from_file_location('integration_frozen', BASE / 'source/integration_check.py')
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def differences(a, b, path=''):
    result = []
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                result.append({'path': path + '/' + key, 'expected': a.get(key), 'actual': b.get(key),
                    'missing_from': 'expected' if key not in a else 'actual'})
            else:
                result += differences(a[key], b[key], path + '/' + key)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (left, right) in enumerate(zip(a, b)):
            result += differences(left, right, path + '/' + str(i))
    elif a != b:
        result.append({'path': path, 'expected': a, 'actual': b})
    return result


def main():
    state = json.loads((BASE / 'status.json').read_text())
    assert state['phase'] == 'COMPLETE' and state['reserved_requests'] == 48
    old_archive = BASE / 'LAB_INTEGRATION_DIAGNOSTICS_2026-11-17.zip'
    old_hash = diag.sha(old_archive)
    results = []
    total_mock_requests = 0
    for original in state['results']:
        job = original['job']
        row = {'job': job, 'original_diagnostic_status': original['status'],
            'original_error_type': original.get('error_type'), 'original_error': original.get('error'),
            'live_wall_seconds': original['wall_seconds']}
        if original['status'] == 'ERROR':
            assert original['error_type'] == 'AssertionError'
            assert original['error'] == 'Adapter request differs from zero-network expected body'
            assert len(original['captured_requests']) == len(original['captured_responses']) == 1
            request = original['captured_requests'][0]
            response = original['captured_responses'][0]
            assert response['status'] == 200
            objects = response['objects']
            count = [0]
            def mock(wire):
                count[0] += 1
                assert json.loads(wire.content) == request, 'Offline replay request differs from captured LIVE request'
                if request['stream']:
                    content = ('\n'.join(json.dumps(o) for o in objects) + '\n').encode()
                    return httpx.Response(200, content=content, headers={'Content-Type':'application/x-ndjson'})
                assert len(objects) == 1
                return httpx.Response(200, json=objects[0])
            llm = diag.model_for(job['model'], named=job['named'])
            llm._client = ollama.Client(host=diag.ENDPOINT, transport=httpx.MockTransport(mock))
            start = time.monotonic()
            answer = llm.bind_tools(job['tools']).invoke(diag.prompt(job), stream=job['stream'])
            row['offline_parser_replay_seconds'] = time.monotonic() - start
            row['adapter_answer_replayed'] = answer.model_dump(mode='json')
            row['parsed_calls'] = [{'name': c['name'], 'args': c['args']} for c in answer.tool_calls]
            row['request_body_differences'] = differences(original['sdk_serialized_expected_request'], request)
            row['exact_live_request_replayed'] = True
            row['offline_mock_request_count'] = count[0]
            assert count[0] == 1
            total_mock_requests += count[0]
            llm._client._client.close()
        else:
            assert original['status'] == 'RETURNED'
            request = original['wire_request']
            objects = original['server_objects']
            row['parsed_calls'] = original['parsed_calls']
            row['request_body_differences'] = []
        row['actual_wire_request'] = request
        row['server_objects'] = objects
        row['server_native_calls'] = diag.normalize([c for o in objects for c in o.get('message',{}).get('tool_calls',[])])
        row['parser_preserved_server_calls'] = row['parsed_calls'] == row['server_native_calls']
        row['expected_call_match'] = row['parsed_calls'] == [job['expected']]
        row['server_content'] = ''.join(o.get('message',{}).get('content','') for o in objects)
        row['final_metadata'] = {k:v for k,v in objects[-1].items() if k != 'message'}
        assert row['final_metadata']['eval_count'] <= 512
        results.append(row)
    assert len(results) == 48 and total_mock_requests == 35
    all_preserved = all(r['parser_preserved_server_calls'] for r in results)
    diag.verify_old()
    assert diag.sha(old_archive) == old_hash
    output = {'date':'2026-11-17','actual_live_requests':48,'additional_live_requests':0,
        'offline_mock_replays':total_mock_requests,'original_instrumentation_assertion_failures':35,
        'original_raw_archive_sha256':old_hash,'old_archive_unchanged':True,
        'all_exact_replays_pass':True,'all_server_native_calls_preserved':all_preserved,
        'original_69_source_hashes_unchanged':True,'tool_executions':0,'results':results,
        'usage':{f:sum(r['final_metadata'].get(f,0) for r in results) for f in ['prompt_eval_count','eval_count']}}
    diag.write(BASE / 'RECONCILED_RESULTS.json',output)
    table = [{k:r['job'][k] for k in ['id','model','label','channel','stream']} |
        {k:r[k] for k in ['expected_call_match','parser_preserved_server_calls','parsed_calls']} for r in results]
    diag.write(BASE / 'RECONCILED_TABLE.json',table)
    pairs = []
    for model in [diag.LLAMA,diag.GRANITE]:
        for label in sorted({r['job']['label'] for r in results if r['job']['model']==model and r['job']['kind']=='probe'}):
            selected = [r for r in results if r['job']['model']==model and r['job']['label']==label]
            if len(selected)==2:
                raw=next(r for r in selected if r['job']['channel']=='raw')
                adapted=next(r for r in selected if r['job']['channel']=='adapter')
                pairs.append({'model':model,'label':label,'body_differences':differences(raw['actual_wire_request'],adapted['actual_wire_request']),
                    'raw_expected_match':raw['expected_call_match'],'adapter_expected_match':adapted['expected_call_match']})
    diag.write(BASE / 'RAW_ADAPTER_PAIR_DIFFERENCES.json',pairs)
    files = {str(p.relative_to(BASE)):diag.sha(p) for p in BASE.rglob('*') if p.is_file()
        and p.name not in ['operator.log','INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip','reconciled-archive-verification.json']}
    target = BASE / 'INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip'
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as out:
        for name in files:
            out.write(BASE/name,name)
        out.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':files},indent=2))
    with zipfile.ZipFile(target) as check:
        assert check.testzip() is None
        for name, expected in files.items():
            assert hashlib.sha256(check.read(name)).hexdigest()==expected
    diag.write(BASE/'reconciled-archive-verification.json',{'sha256':diag.sha(target),'bytes':target.stat().st_size,
        'content_files':len(files),'all_hashes_match':True,'original_live_requests':48,'additional_live_requests':0})
    print('OFFLINE_RECONCILIATION_PASS',len(results),'requests;',total_mock_requests,'mock replays; zero extra live calls',flush=True)


if __name__=='__main__':
    main()
