"""Read-only independent verification of the completed native-schema rerun."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import zipfile

BASE = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parents[3]
PREFIX = 'integration-rerun-20261117-r1/'
MODELS = ['llama3.1:8b-instruct-q4_K_M', 'granite3.3:8b']
OLD = EVAL / 'artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip'
NEW = BASE / 'evidence/NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def checked(z):
    assert z.testzip() is None
    files = json.loads(z.read('ARCHIVE_MANIFEST.json'))['files']
    for name, digest in files.items():
        assert sha(z.read(name)) == digest, name
    return files


spec = importlib.util.spec_from_file_location('repeat_analysis',
    EVAL / 'artifacts/qwen-lab-repeat-20261117/preparation/analyze_repeat.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def pair_summary(rows):
    pairs = {}
    for r in rows:
        if r['case'] != 'ambiguous_goal':
            pairs.setdefault((r['case'], r['repetition']), {})[r['condition']] = r
    assert len(pairs) == 36 and all(len(p) == 2 for p in pairs.values())
    matched = [p for p in pairs.values() if all(r['primary_pass'] for r in p.values())]
    return {'known_goal_pairs': len(pairs), 'both_correct': len(matched),
        'primitive_only_correct': sum(p['primitives']['primary_pass'] and not p['macro']['primary_pass'] for p in pairs.values()),
        'macro_only_correct': sum(p['macro']['primary_pass'] and not p['primitives']['primary_pass'] for p in pairs.values()),
        'both_wrong': sum(not any(r['primary_pass'] for r in p.values()) for p in pairs.values()),
        'matched_success_costs': {c: shared.costs([p[c] for p in matched]) for c in ['primitives', 'macro']}}


def inspect_llm_calls(read, folder, row, wire, cursor, validations=False):
    trace = read(folder + '/trace.json')
    llm = sorted([s for s in trace['spans'] if s.get('attributes', {}).get('openinference.span.kind') == 'LLM'],
                 key=lambda s: s['start_time'])
    assert len(llm) == row['inference']['calls']
    timing = Counter()
    normalizations = []
    invalid_calls = []
    raw_parse_differences = []
    reason = Counter()
    after_tool = 0
    max_prompt = 0
    for span in llm:
        capture = wire[cursor]
        cursor += 1
        assert capture['status'] == 'RETURNED' and capture['http_status'] == 200
        body = capture['request']
        assert body['stream'] is False
        options = body['options']
        assert options['num_ctx'] == 8192 and options['temperature'] == 0 and options['seed'] == 42
        assert 0 < options['num_predict'] <= 1024
        if body.get('tools'):
            assert any('Available function schemas (retain these after tool results):' in m.get('content', '')
                for m in body['messages'] if m['role'] == 'system')
            after_tool += any(m['role'] == 'tool' for m in body['messages'])
        response = capture['response']
        generation = json.loads(span['attributes']['output.value'])['generations'][0]
        if isinstance(generation, list):
            generation = generation[0]
        meta = generation.get('generation_info') or {}
        message = generation['message']['kwargs']
        raw = response['message'].get('tool_calls') or []
        parsed = message.get('tool_calls') or []
        bad = message.get('invalid_tool_calls') or []
        identity = row.get('job', {}).get('id') or row['fixture']['id'] + '-' + row['condition']
        if len(raw) != len(parsed) or [c['function']['name'] for c in raw] != [c['name'] for c in parsed]:
            raw_parse_differences.append({'trial': identity, 'wire_index': cursor, 'raw': raw, 'parsed': parsed, 'invalid': bad})
        for original, adapted in zip(raw, parsed):
            if original['function']['arguments'] != adapted['args']:
                normalizations.append({'trial': identity, 'wire_index': cursor,
                    'raw': original['function'], 'after_adapter': adapted})
        if bad:
            invalid_calls.append({'trial': identity, 'wire_index': cursor, 'invalid': bad})
        for field in ['eval_count', 'eval_duration', 'prompt_eval_count', 'prompt_eval_duration',
                      'load_duration', 'total_duration']:
            assert isinstance(meta.get(field), (float, int)), (identity, field)
            assert meta[field] == response[field], (identity, field)
            timing[field] += meta[field]
        assert row['inference']['usage_complete']
        max_prompt = max(max_prompt, meta['prompt_eval_count'])
        reason[meta.get('done_reason', 'NOT_RECORDED')] += 1
    return cursor, {'timing': dict(timing), 'done_reasons': dict(reason), 'normalizations': normalizations,
        'invalid_tool_calls': invalid_calls, 'raw_parsed_call_differences': raw_parse_differences,
        'schema_requests_after_tool_results': after_tool, 'max_prompt_tokens': max_prompt}


def combine_calls(parts):
    timing = Counter()
    reasons = Counter()
    for p in parts:
        timing.update(p['timing']); reasons.update(p['done_reasons'])
    return {'recorded_ollama_totals': dict(timing), 'done_reasons': dict(reasons),
        'generation_tokens_per_second': timing['eval_count'] / (timing['eval_duration'] / 1e9),
        'max_prompt_tokens': max(p['max_prompt_tokens'] for p in parts),
        'schema_requests_after_tool_results': sum(p['schema_requests_after_tool_results'] for p in parts),
        'argument_normalizations': [v for p in parts for v in p['normalizations']],
        'invalid_tool_calls': [v for p in parts for v in p['invalid_tool_calls']],
        'raw_parsed_call_differences': [v for p in parts for v in p['raw_parsed_call_differences']],
        'prompt_eval_cached_count': 'NOT_RECORDED'}


def main():
    (BASE / 'evidence').mkdir(exist_ok=True)
    assert sha(OLD.read_bytes()) == 'fa5c14cb31ab4079317106af815bf86a810effff595fefa05f2eb6d6d51d9356'
    remote_verification = json.loads((BASE / 'evidence/REMOTE_RAW_VERIFICATION.json').read_text())
    assert sha(NEW.read_bytes()) == remote_verification['sha256']
    assert NEW.stat().st_size == remote_verification['bytes'] and remote_verification['all_hashes_pass']
    with zipfile.ZipFile(OLD) as old, zipfile.ZipFile(NEW) as z:
        old_files, new_files = checked(old), checked(z)
        read = lambda name: json.loads(z.read(PREFIX + name))
        frozen = read('freeze.json')
        stopped_path = BASE / 'evidence/INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip'
        with zipfile.ZipFile(stopped_path) as stopped:
            initial_files = checked(stopped)
            ip = 'integration-rerun-20261117/'
            initial_state = json.loads(stopped.read(ip + 'operator-status.json'))
            initial_validation = json.loads(stopped.read(ip + 'validation/deterministic/checkpoint.json'))
            initial_freeze = json.loads(stopped.read(ip + 'freeze.json'))
            assert initial_state['phase'] == initial_validation['status'] == 'STOPPED'
            assert initial_validation['reserved_requests'] == 0
            assert not any('/wire/' in n or n.endswith('/physical-model-calls.json') for n in initial_files)
            assert initial_freeze['validation_fixtures'] == frozen['validation_fixtures']
            assert initial_freeze['schedule'] == frozen['schedule']
            assert stopped.read(ip + 'source/tool_contract_ollama.py') == z.read(PREFIX + 'source/tool_contract_ollama.py')
        assert (EVAL.parent / 'rosa-research/src/rosa_backends/tool_contract_ollama.py').read_bytes() == z.read(PREFIX + 'source/tool_contract_ollama.py')
        assert len(frozen['files']) == 75
        for name, digest in frozen['files'].items():
            archive = z if name.startswith(PREFIX) else old
            assert sha(archive.read(name)) == digest, name
        original_freeze = json.loads(old.read('study/freeze.json'))
        assert all(frozen['model_digests'][m] == original_freeze['model_metadata'][m]['digest'] for m in MODELS)
        operator = read('operator-status.json')
        assert operator['phase'] == 'EXECUTION_COMPLETE'
        assert all(s['status'] == 'COMPLETE' and s['exit_code'] == 0 for s in operator['steps'])
        control = read('results/deterministic/controls/checkpoint.json')
        assert control['status'] == 'COMPLETE' and control['primary_correct'] == 20 and len(control['trials']) == 20
        assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in control['trials'])
        assert control['simulator_cleanup']['returncode'] == 0 and not control['cleanup_errors']
        validation_control = read('validation/deterministic/checkpoint.json')
        assert validation_control['status'] == 'COMPLETE' and validation_control['correct'] == 12
        assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] and r['safe'] for r in validation_control['trials'])
        output = {'date': '2026-11-17', 'profile': frozen['profile'], 'old_archive_files': len(old_files),
            'model_digests': frozen['model_digests'], 'frozen_baseline_source_commits': original_freeze['source_commits'],
            'initial_stopped_attempt': {'content_files': len(initial_files), 'model_requests': 0,
                'sha256': sha(stopped_path.read_bytes()), 'same_profile_tasks_and_schedule': True},
            'new_archive_files': len(new_files), 'frozen_source_hashes': len(frozen['files']),
            'frozen_source_and_model_digests_pass': True, 'robot_controls': 20,
            'deterministic_validation_controls': 12, 'models': {}, 'validation': {},
            'operator': operator, 'raw_archive_sha256': sha(NEW.read_bytes()),
            'lab_download_hash_matches': True, 'original_lab_archive_unchanged': True, 'all_checks_pass': True}
        for model in MODELS:
            key = model.replace(':', '_')
            vf = 'validation/' + key
            val = read(vf + '/checkpoint.json')
            assert val['status'] == 'COMPLETE' and val['functional_gate'] and len(val['trials']) == 12
            wires = [json.loads(z.read(n)) for n in sorted(new_files) if n.startswith(PREFIX + vf + '/wire/') and n.endswith('.json')]
            cursor = 0; parts = []
            for r in val['trials']:
                folder = vf + '/' + r['fixture']['id'] + '-' + r['condition']
                raw = read(folder + '/result.json')
                assert raw == {k: v for k, v in r.items() if k != 'phoenix_audit'}
                assert r['local_audit']['pass'] and r['phoenix_audit']['pass'] and r['safe']
                assert r['inference']['calls'] <= 8 and r['inference']['known_output_tokens'] <= 2048
                cursor, item = inspect_llm_calls(read, folder, r, wires, cursor, validations=True)
                parts.append(item)
            physical = read(vf + '/physical-model-calls.json')
            assert len(physical) == cursor == len(wires) == val['reserved_requests'] <= 96
            output['validation'][model] = {'correct': val['correct'], 'n': 12, 'functional_gate': True,
                'requests': cursor, 'timing_and_adapter': combine_calls(parts),
                'input_tokens': sum(r['inference']['known_input_tokens'] for r in val['trials']),
                'output_tokens': sum(r['inference']['known_output_tokens'] for r in val['trials']),
                'cases': [{k: r[k] for k in ['fixture', 'condition', 'correct', 'safe', 'world', 'error_type',
                    'expired_fault_exercised', 'answer', 'inference']} for r in val['trials']]}
            ck = read('results/' + key + '/ollama/checkpoint.json')
            assert ck['status'] == 'COMPLETE' and len(ck['trials']) == 80
            assert ck['simulator_cleanup']['returncode'] == 0 and not ck['cleanup_errors']
            assert [r['job'] for r in ck['trials']] == [{k: v for k, v in j.items() if k != 'case'} for j in frozen['schedule']]
            assert [r['case'] for r in ck['trials']] == [j['case']['id'] for j in frozen['schedule']]
            folder = 'results/' + key
            wires = [json.loads(z.read(n)) for n in sorted(new_files) if n.startswith(PREFIX + folder + '/wire/') and n.endswith('.json')]
            cursor = 0; parts = []; failure_details = []; persisted_spans = 0
            for r in ck['trials']:
                trial = folder + '/ollama/' + r['job']['id']
                raw = read(trial + '/result.json')
                for field in ['job', 'case', 'condition', 'inference', 'score', 'primary_pass', 'wall_seconds']:
                    assert r[field] == raw[field]
                assert r['local_audit']['pass'] and r['phoenix_audit']['pass']
                assert r['phoenix_audit'] == read(trial + '/phoenix-audit.json')
                persisted_spans += r['phoenix_audit']['persisted_spans']
                assert r['inference']['calls'] <= 8 and r['inference']['output_upper_bound'] <= 2048
                assert r['wall_seconds'] <= 360 and r['score']['native_operations'] <= 10
                assert r['score']['dispatches'] <= 1 and not r['score']['dispatch_violations']
                cursor, item = inspect_llm_calls(read, trial, r, wires, cursor)
                parts.append(item)
                if not r['primary_pass'] or r['case'] == 'ambiguous_goal':
                    failure_details.append({'case': r['case'], 'condition': r['condition'], 'repetition': r['repetition'],
                        'primary_legacy_pass': r['primary_pass'], 'selected_skill': r['snapshot']['selected_skill'],
                        'score': r['score'], 'answer': r['answer'], 'error_type': r['error_type'],
                        'calls': r['inference']['calls'], 'wall_seconds': r['wall_seconds']})
            physical = read(folder + '/physical-model-calls.json')
            assert len(physical) == cursor == len(wires) == ck['live_model_requests'] <= 643
            assert cursor == ck['campaign']['reserved_requests'] and ck['campaign']['request_cap'] == 643
            assert ck['campaign']['infrastructure_retries'] <= 3 and ck['campaign']['elapsed_seconds'] <= 28800
            old_rows = json.loads(old.read('results/' + key + '/ollama/checkpoint.json'))['trials']
            qwen_rows = json.loads(old.read('results/qwen3.5_9b/ollama/checkpoint.json'))['trials']
            qwen_by_id = {shared.identity(r): r for r in qwen_rows}
            qwen_context = {}
            for c in ['primitives', 'macro']:
                current = [r for r in ck['trials'] if r['condition'] == c and r['case'] != 'ambiguous_goal']
                common = [r for r in current if r['primary_pass'] and qwen_by_id[shared.identity(r)]['primary_pass']]
                qwen_context[c] = {'same_known_goal_cells': len(current), 'both_correct': len(common),
                    'qwen_only_correct': sum(qwen_by_id[shared.identity(r)]['primary_pass'] and not r['primary_pass'] for r in current),
                    'rerun_only_correct': sum(r['primary_pass'] and not qwen_by_id[shared.identity(r)]['primary_pass'] for r in current),
                    'matched_success_costs': {'qwen_original_lab_profile': shared.costs([qwen_by_id[shared.identity(r)] for r in common]),
                        'rerun_native_schema_v1': shared.costs(common)}, 'uniform_profiles': False}
            summary = shared.aggregate(ck['trials'])
            for c in ['primitives', 'macro']:
                chosen = [r for r in ck['trials'] if r['condition'] == c]
                known = [r for r in chosen if r['case'] != 'ambiguous_goal']
                summary[c].update(correct_skill_known_goal=sum(r['score']['goal_correct'] for r in known),
                    validation_codes=dict(Counter(e['code'] for r in chosen for e in r['snapshot']['events'] if e['type'] == 'validation')),
                    returned_error_codes=dict(Counter(str(r['answer']).split('An error occurred:', 1)[1].strip()
                        for r in chosen if str(r['answer']).startswith('An error occurred:'))),
                    native_by_actor={a: sum(r['score'][a + '_native_operations'] for r in chosen) for a in ['model', 'program']},
                    dispatches=sum(r['score']['dispatches'] for r in chosen),
                    known_goal_costs=shared.costs(known),
                    skipped_injected_faults=[r['job']['id'] for r in known if r['score']['injected_fault_exercised'] is False])
            output['models'][model] = {'summary': summary, 'paired': pair_summary(ck['trials']),
                'old_configuration': shared.aggregate(old_rows), 'requests': cursor, 'persisted_spans': persisted_spans,
                'qwen_context_paired': qwen_context,
                'timing_and_adapter': combine_calls(parts), 'failure_and_ambiguous_details': failure_details,
                'trial_ledger': [{'id': r['job']['id'], 'case': r['case'], 'condition': r['condition'],
                    'repetition': r['repetition'], 'correct': r['primary_pass'], 'calls': r['inference']['calls'],
                    'input_tokens': r['inference']['known_input_tokens'], 'output_tokens': r['inference']['known_output_tokens'],
                    'seconds': r['wall_seconds'], 'score': r['score'], 'selected_skill': r['snapshot']['selected_skill']}
                    for r in ck['trials']],
                'campaign_seconds': ck['total_elapsed_seconds'], 'cleanup_pass': True}
            output['models'][model]['campaign_budget'] = ck['campaign']
        output['context_reference_original_lab'] = {
            m: shared.aggregate(json.loads(old.read('results/' + m.replace(':', '_') + '/ollama/checkpoint.json'))['trials'])
            for m in ['qwen3.5:9b', 'ministral-3:8b-instruct-2512-q4_K_M']}
        (BASE / 'evidence/INDEPENDENT_RERUN_ANALYSIS.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'all_checks_pass': True, 'new_archive_files': len(new_files),
            'models': {m: {'requests': v['requests'], 'correct': {c: x['known_goal_correct'] for c, x in v['summary'].items()}}
                for m, v in output['models'].items()}}, indent=2))


if __name__ == '__main__':
    main()
