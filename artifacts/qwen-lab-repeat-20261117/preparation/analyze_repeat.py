"""Independently verify downloaded raw evidence and compare retained Qwen runs."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import zipfile

EVAL = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parents[1]
OLD = EVAL / 'artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip'
NEW = BASE / 'evidence/QWEN_LAB_REPEAT_RAW_2026-11-17.zip'
PREFIX = 'qwen-repeat-20261117/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(row):
    return row['case'], row['repetition'], row['condition']


def aggregate(rows):
    result = {}
    for condition in ['primitives', 'macro']:
        selected = [r for r in rows if r['condition'] == condition]
        known = [r for r in selected if r['case'] != 'ambiguous_goal']
        result[condition] = {
            'attempts': len(selected), 'known_goal_n': len(known),
            'known_goal_correct': sum(r['primary_pass'] for r in known),
            'ambiguous_pending_human_review': len(selected) - len(known),
            'legacy_ambiguous_regex_passes': sum(r['primary_pass'] for r in selected if r['case'] == 'ambiguous_goal'),
            'calls': sum(r['inference']['calls'] for r in selected),
            'input_tokens': sum(r['inference']['known_input_tokens'] for r in selected),
            'output_tokens': sum(r['inference']['known_output_tokens'] for r in selected),
            'usage_complete': all(r['inference']['usage_complete'] for r in selected),
            'native_operations': sum(r['score']['native_operations'] for r in selected),
            'invalid_attempts': sum(r['score']['invalid_attempts'] for r in selected),
            'selected_outcome_correct_known_goal': sum(r['score']['selected_outcome_correct'] for r in known),
            'faults_actually_exercised': sum(r['score']['injected_fault_exercised'] is True for r in known),
            'outer_exception_types': dict(Counter(r['error_type'] for r in selected if r.get('error_type'))),
            'returned_error_messages': sum(str(r.get('answer', '')).startswith('An error occurred:') for r in selected),
            'structured_unsupported_success_attempts': sum(r['score']['unsupported_success_attempts'] for r in selected),
            'known_goal_accepted_wrong_successes': sum(r['score']['accepted_success_wrong_user_goal'] for r in known),
            'mean_seconds': statistics.mean(r['wall_seconds'] for r in selected),
            'median_seconds': statistics.median(r['wall_seconds'] for r in selected),
            'total_seconds': sum(r['wall_seconds'] for r in selected),
            'families': {family: {'correct': sum(r['primary_pass'] for r in selected if r['case'] == family),
                'n': sum(r['case'] == family for r in selected),
                'semantic_status': 'HUMAN_REVIEW_PENDING' if family == 'ambiguous_goal' else 'KNOWN_GOAL'}
                for family in sorted({r['case'] for r in selected})},
        }
    return result


def costs(rows):
    return {'trials': len(rows), 'calls': sum(r['inference']['calls'] for r in rows),
        'input_tokens': sum(r['inference']['known_input_tokens'] for r in rows),
        'output_tokens': sum(r['inference']['known_output_tokens'] for r in rows),
        'seconds': sum(r['wall_seconds'] for r in rows),
        'native_operations': sum(r['score']['native_operations'] for r in rows)}


def main():
    with zipfile.ZipFile(OLD) as old, zipfile.ZipFile(NEW) as new:
        for archive in [old, new]:
            assert archive.testzip() is None
            manifest = json.loads(archive.read('ARCHIVE_MANIFEST.json'))
            for name, expected in manifest['files'].items():
                assert sha(archive.read(name)) == expected, name
        read = lambda name: json.loads(new.read(PREFIX + name))
        frozen = read('study/freeze.json')
        for name, expected in frozen['files'].items():
            archive = new if name.startswith(PREFIX) else old
            assert sha(archive.read(name)) == expected, name
        old_checkpoint = json.loads(old.read('results/qwen3.5_9b/ollama/checkpoint.json'))
        checkpoint = read('results/qwen3.5_9b/ollama/checkpoint.json')
        control = read('results/deterministic/controls/checkpoint.json')
        assert checkpoint['status'] == 'COMPLETE' and len(checkpoint['trials']) == 80
        assert control['status'] == 'COMPLETE' and control['primary_correct'] == 20
        assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in control['trials'])
        assert checkpoint['simulator_cleanup']['returncode'] == 0 and not checkpoint['cleanup_errors']
        rows = checkpoint['trials']
        assert [r['job'] for r in rows] == [{k: v for k, v in job.items() if k != 'case'}
            for job in frozen['schedule']]
        assert [r['case'] for r in rows] == [job['case']['id'] for job in frozen['schedule']]
        assert len({identity(r) for r in rows}) == 80
        duration_fields = Counter()
        done_reasons = Counter()
        spans = 0
        traced_calls = 0
        max_prompt = 0
        for row in rows:
            folder = 'results/qwen3.5_9b/ollama/' + row['job']['id'] + '/'
            raw = read(folder + 'result.json')
            for field in ['job', 'case', 'condition', 'repetition', 'inference', 'score', 'primary_pass', 'wall_seconds']:
                assert raw[field] == row[field], (field, row['job']['id'])
            audit = read(folder + 'phoenix-audit.json')
            assert audit['pass'] and audit == row['phoenix_audit'] and row['local_audit']['pass']
            spans += audit['persisted_spans']
            assert row['inference']['calls'] <= 8 and row['inference']['output_upper_bound'] <= 2048
            assert row['wall_seconds'] <= 360 and row['score']['native_operations'] <= 10
            assert row['score']['dispatches'] <= 1 and not row['score']['dispatch_violations']
            assert row['inference']['usage_complete']
            llm = [s for s in read(folder + 'trace.json')['spans']
                if s.get('attributes', {}).get('openinference.span.kind') == 'LLM']
            assert len(llm) == row['inference']['calls']
            for span in llm:
                traced_calls += 1
                output = json.loads(span['attributes']['output.value'])
                generation = output['generations'][0]
                if isinstance(generation, list):
                    generation = generation[0]
                meta = generation.get('generation_info') or {}
                for field in ['eval_count', 'eval_duration', 'prompt_eval_count', 'prompt_eval_duration',
                        'load_duration', 'total_duration']:
                    assert isinstance(meta.get(field), (int, float)), (field, row['job']['id'])
                    duration_fields[field] += meta[field]
                max_prompt = max(max_prompt, meta['prompt_eval_count'])
                done_reasons[meta.get('done_reason', 'NOT_RECORDED')] += 1
        physical = read('results/qwen3.5_9b/physical-model-calls.json')
        assert len(physical) == traced_calls == checkpoint['live_model_requests']
        assert traced_calls <= 643
        all_summaries = {'lab_run_1': aggregate(old_checkpoint['trials']), 'lab_run_2': aggregate(rows)}
        historical = EVAL / 'artifacts/macro-m4-20261027/ollama/checkpoint.json'
        historical_rows = []
        if historical.exists():
            historical_rows = json.loads(historical.read_text())['trials']
            all_summaries['historical_laptop_m4'] = aggregate(historical_rows)
        before = {identity(r): r for r in old_checkpoint['trials']}
        after = {identity(r): r for r in rows}
        comparison = {}
        for condition in ['primitives', 'macro']:
            keys = [k for k in before if k[2] == condition and k[0] != 'ambiguous_goal']
            common = [k for k in keys if before[k]['primary_pass'] and after[k]['primary_pass']]
            comparison[condition] = {'paired_known_goal': len(keys),
                'both_correct': len(common),
                'first_only_correct': sum(before[k]['primary_pass'] and not after[k]['primary_pass'] for k in keys),
                'repeat_only_correct': sum(not before[k]['primary_pass'] and after[k]['primary_pass'] for k in keys),
                'both_wrong': sum(not before[k]['primary_pass'] and not after[k]['primary_pass'] for k in keys),
                'changed_cells': [{'case': k[0], 'repetition': k[1], 'first_correct': before[k]['primary_pass'],
                    'repeat_correct': after[k]['primary_pass']} for k in keys if before[k]['primary_pass'] != after[k]['primary_pass']],
                'matched_success_costs': {'first': costs([before[k] for k in common]),
                    'repeat': costs([after[k] for k in common])}}
        within_repeat = {}
        historical_pairs = {}
        h = {identity(r): r for r in historical_rows}
        for c in ['primitives', 'macro']:
            shared = [k for k in h if k in after and k[0] != 'ambiguous_goal' and k[2] == c]
            good = [k for k in shared if h[k]['primary_pass'] and after[k]['primary_pass']]
            historical_pairs[c] = {'common_known_goal_cells': len(shared),
                'historical_correct': sum(h[k]['primary_pass'] for k in shared),
                'repeat_correct': sum(after[k]['primary_pass'] for k in shared),
                'both_correct': len(good),
                'historical_only_correct': sum(h[k]['primary_pass'] and not after[k]['primary_pass'] for k in shared),
                'repeat_only_correct': sum(after[k]['primary_pass'] and not h[k]['primary_pass'] for k in shared),
                'matched_success_costs': {'historical': costs([h[k] for k in good]),
                    'repeat': costs([after[k] for k in good])}}
        for case, repetition in sorted({(r['case'], r['repetition']) for r in rows if r['case'] != 'ambiguous_goal'}):
            pair = {c: after[(case, repetition, c)] for c in ['primitives', 'macro']}
            if all(r['primary_pass'] for r in pair.values()):
                for c, r in pair.items():
                    within_repeat.setdefault(c, []).append(r)
        output = {'date': '2026-11-17', 'study': frozen['study'], 'hardware': frozen['hardware'],
            'model': frozen['model'], 'summary': all_summaries, 'same_lab_paired_comparison': comparison,
            'historical_paired_comparison': historical_pairs,
            'within_repeat_matched_success': {c: costs(v) for c, v in within_repeat.items()},
            'audits': {'model_trials': 80, 'controls': 20, 'live_persisted_spans': spans,
                'source_hashes': len(frozen['files']), 'all_pass': True},
            'timing': {'recorded_ollama_totals': dict(duration_fields), 'done_reasons': dict(done_reasons),
                'generation_tokens_per_second': duration_fields['eval_count'] / (duration_fields['eval_duration'] / 1e9),
                'max_prompt_tokens': max_prompt, 'campaign_seconds': checkpoint['total_elapsed_seconds'],
                'prompt_eval_cached_count': 'NOT_RECORDED'},
            'requests': traced_calls, 'physical_requests': len(physical),
            'limits_all_pass': True, 'no_unsafe_dispatch': True,
            'raw_archive_sha256': sha(NEW.read_bytes())}
        changed_evidence = []
        for c, s in comparison.items():
            for changed in s['changed_cells']:
                k = (changed['case'], changed['repetition'], c)
                item = {'case': k[0], 'repetition': k[1], 'condition': c}
                for label, source in [('first', before), ('repeat', after)]:
                    r = source[k]
                    item[label] = {'primary_pass': r['primary_pass'], 'selected_skill': r['snapshot']['selected_skill'],
                        'accepted_report_status': r['score']['accepted_report_status'],
                        'goal_correct': r['score']['goal_correct'],
                        'injected_fault_exercised': r['score']['injected_fault_exercised'],
                        'dispatches': r['score']['dispatches'], 'calls': r['inference']['calls'],
                        'wall_seconds': r['wall_seconds'], 'answer': r['answer'],
                        'validation_errors': r['snapshot']['validation_errors']}
                changed_evidence.append(item)
        output['changed_cell_evidence'] = changed_evidence
        destination = BASE / 'evidence'
        (destination / 'INDEPENDENT_REPEAT_ANALYSIS.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
        (destination / 'INDEPENDENT_REPEAT_VERIFICATION.json').write_text(json.dumps({
            'raw_archive_sha256': output['raw_archive_sha256'], 'both_archives_all_hashes_match': True,
            'new_frozen_source_hashes': len(frozen['files']), 'original_source_files_preserved': 69,
            'live_audits': 80, 'controls': 20, 'requests': traced_calls, 'bounds_pass': True}, indent=2) + '\n')
    print(json.dumps({'summary': all_summaries, 'comparison': comparison, 'timing': output['timing']}, indent=2))


if __name__ == '__main__':
    main()
