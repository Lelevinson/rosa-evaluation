"""Read-only M4 extraction; write only alongside this script. No network/model calls."""
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import csv
import hashlib
import json
import statistics

import numpy as np

OUT = Path(__file__).resolve().parent
EVAL = OUT.parents[1]
M4 = EVAL / 'artifacts/macro-m4-20261027'
HIST_LOG = EVAL / '.local/ollama/m4-stderr.log'
FIELDS = ('total_duration', 'load_duration', 'prompt_eval_count',
          'prompt_eval_duration', 'eval_count', 'eval_duration', 'prompt_eval_cached_count')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def csv_out(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def epoch(t):
    return datetime.fromisoformat(t.replace('Z', '+00:00')).timestamp()


def interval_union(intervals):
    end = None
    total = 0.0
    for a, b in sorted(intervals):
        assert b >= a
        total += max(0, b - max(a, end if end is not None else a))
        end = max(b, end if end is not None else b)
    return total


def regression(rows, y):
    x = np.array([[r['output_tokens'], r['input_tokens']] for r in rows], dtype=float)
    target = np.array([r[y] for r in rows], dtype=float)
    design = np.column_stack([np.ones(len(rows)), x])
    b, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    resid = target - design @ b
    corr = float(np.corrcoef(x.T)[0, 1])
    return {'n': len(rows), 'outcome': y, 'intercept_seconds': float(b[0]),
            'output_token_coefficient_seconds': float(b[1]),
            'input_token_coefficient_seconds': float(b[2]),
            'r_squared': float(1 - resid @ resid / ((target-target.mean()) @ (target-target.mean()))),
            'input_output_predictor_correlation': corr, 'design_rank': int(rank),
            'collinearity_caution': abs(corr) >= .7,
            'interpretation': 'Descriptive association; repeated families/turns are dependent. No causal coefficients or independent-sample inference.'}


def first_calls(generation):
    return [{'name': c['name'], 'args': c['args']}
            for c in generation['message']['kwargs'].get('tool_calls', [])]


def main():
    checkpoint = M4 / 'ollama/checkpoint.json'
    data = json.loads(checkpoint.read_text(encoding='utf-8'))
    protected = {p.relative_to(M4).as_posix(): sha(p) for p in M4.rglob('*') if p.is_file()}
    save('protected-m4-before.json', protected)
    freeze = json.loads((M4 / 'freeze.json').read_text(encoding='utf-8'))
    frozen_checks = []
    for name, expected in freeze['files'].items():
        live, archived = EVAL.parent / name, M4 / 'source' / name
        frozen_checks.append({'file': name, 'expected_sha256': expected,
                              'live_matches': sha(live) == expected,
                              'archived_matches': sha(archived) == expected})
    assert all(x['live_matches'] and x['archived_matches'] for x in frozen_checks)
    calls, trials, fixtures = [], [], []
    field_counts = Counter()
    historical_statuses = []
    source_hashes = {'ollama/checkpoint.json': sha(checkpoint), 'freeze.json': sha(M4 / 'freeze.json')}
    for trial in data['trials']:
        ident = trial['job']['id']
        folder = M4 / 'ollama' / ident
        path = folder / 'trace.json'
        source_hashes[path.relative_to(M4).as_posix()] = sha(path)
        spans = json.loads(path.read_text(encoding='utf-8'))['spans']
        llms = sorted((s for s in spans if s['name'] == 'ConfiguredChatOllama'
                       and s['attributes'].get('openinference.span.kind') == 'LLM'),
                      key=lambda s: s['start_time'])
        assert len(llms) == trial['inference']['calls']
        ops = trial['snapshot']['operations']
        assert all('started' in o and 'finished' in o for o in ops)
        native = interval_union([(o['started'], o['finished']) for o in ops])
        root = next(s for s in spans if s['name'] == 'rosa.capability.demo')
        root_s = epoch(root['end_time']) - epoch(root['start_time'])
        native_spans = [s for s in spans if s['name'].startswith('reliability.native.')]
        assert len(native_spans) == len(ops)
        native_epoch = interval_union([(epoch(s['start_time']), epoch(s['end_time'])) for s in native_spans])
        group = []
        for i, span in enumerate(llms):
            a = span['attributes']
            g = json.loads(a['output.value'])['generations'][0][0]
            md = g['generation_info']
            usage = g['message']['kwargs']['usage_metadata']
            ledger = trial['inference']['events'][i]
            assert usage == ledger['usage']
            for k in FIELDS:
                if md.get(k) is not None:
                    field_counts[k] += 1
            row = {'trial': ident, 'family': trial['case'], 'condition': trial['condition'],
                   'repetition': trial['repetition'], 'call': i+1,
                   'input_tokens': md['prompt_eval_count'], 'output_tokens': md['eval_count'],
                   'finish_reason': md['done_reason'],
                   'client_span_seconds': epoch(span['end_time']) - epoch(span['start_time'])}
            for k in FIELDS:
                row[k] = md.get(k)
            for field in ('total', 'load', 'prompt_eval', 'eval'):
                row[field + '_seconds'] = md[field + '_duration'] / 1e9
            row['server_other_seconds'] = row['total_seconds'] - sum(row[k + '_seconds'] for k in ('load', 'prompt_eval', 'eval'))
            row['generation_tokens_per_second'] = md['eval_count'] / row['eval_seconds'] if row['eval_seconds'] > 0 else None
            row['output_allowance'] = ledger['requested_output_allowance']
            row['hit_requested_output_cap'] = row['output_tokens'] >= row['output_allowance']
            calls.append(row)
            group.append(row)
            if (trial['repetition'] == 1 and i == 0) or row['input_tokens'] == 4027:
                fixtures.append({'id': ident + '-call-' + str(i+1),
                    'family': trial['case'], 'condition': trial['condition'], 'call': i+1,
                    'recorded_input_tokens': row['input_tokens'], 'source_trace': path.relative_to(M4).as_posix(),
                    'source_trace_sha256': sha(path), 'span_id': span['context']['span_id'],
                    'messages_serialized': json.loads(a['input.value'])['messages'][0],
                    'invocation_parameters': json.loads(a['llm.invocation_parameters']),
                    'historical_tool_calls': first_calls(g),
                    'historical_content': g['message']['kwargs'].get('content', '')})
        assert sum(r['input_tokens'] for r in group) == trial['inference']['known_input_tokens']
        assert sum(r['output_tokens'] for r in group) == trial['inference']['known_output_tokens']
        answer = trial['answer']
        ending = ('correct' if trial['primary_pass'] else 'response_length_stop' if
                  'truncated_response_no_tool_dispatch' in answer else 'validation_retry_exhaustion' if
                  'validation_retry_budget_exhausted' in answer else 'wrong_skill_or_goal')
        row = {'trial': ident, 'family': trial['case'], 'condition': trial['condition'],
               'repetition': trial['repetition'], 'ending_type': ending,
               'primary_pass': trial['primary_pass'], 'selected_skill': trial['snapshot']['selected_skill'],
               'calls': len(group), 'input_tokens': sum(r['input_tokens'] for r in group),
               'output_tokens': sum(r['output_tokens'] for r in group),
               'task_seconds': trial['wall_seconds'], 'native_monotonic_seconds': native,
               'task_minus_native_seconds': trial['wall_seconds'] - native,
               'trace_root_seconds': root_s, 'trace_native_seconds': native_epoch,
               'client_llm_span_seconds': sum(r['client_span_seconds'] for r in group),
               'native_operations': len(ops)}
        for k in ('total', 'load', 'prompt_eval', 'eval', 'server_other'):
            row['server_' + k + '_seconds'] = sum(r[k + '_seconds'] for r in group)
        row['trace_root_minus_client_llm_and_native_seconds'] = root_s - row['client_llm_span_seconds'] - native_epoch
        row['server_minus_task_seconds'] = row['server_total_seconds'] - row['task_seconds']
        trials.append(row)
        status_path = folder / 'outside-task-ollama-status.json'
        if status_path.exists():
            source_hashes[status_path.relative_to(M4).as_posix()] = sha(status_path)
            historical_statuses.append({'trial': ident, **json.loads(status_path.read_text(encoding='utf-8'))})
    assert len(trials) == 40 and len(calls) == 144
    save('field-inventory.json', {'requests': len(calls), 'per_request_recorded': dict(field_counts),
        'not_recorded_per_request': [k for k in FIELDS if not field_counts[k]],
        'source': 'trace.json / ConfiguredChatOllama / attributes.output.value JSON / generations[0][0].generation_info; usage cross-checked against ledger',
        'native_time': 'per-operation snapshot started/finished monotonic intervals, merged union',
        'duplicate_metadata': 'generation_info and message.kwargs.response_metadata are duplicate views, not independent calls'})
    csv_out('per-call.csv', calls)
    csv_out('per-trial.csv', trials)
    save('historical-loaded-status.json', historical_statuses)
    save('replay-inputs.json', fixtures)
    stage1 = [x['id'] for x in fixtures if x['condition'] == 'macro' and x['call'] == 1]
    safety = max(fixtures, key=lambda x: x['recorded_input_tokens'])
    assert len(stage1) == 10 and safety['recorded_input_tokens'] == 4027
    save('proposed-stage1-inputs.json', {'family_input_ids': stage1, 'context_safety_id': safety['id'],
        'repeat_input_ids': [x['id'] for x in fixtures if x['condition'] == 'macro' and x['call'] == 1
                             and x['family'] in ('move_constrained', 'inspect_healthy', 'ambiguous_goal')],
        'status': 'PROPOSED_NOT_RUN', 'selection': 'repetition 1, one macro first turn per family; actual max-input request across both conditions'})
    groups = defaultdict(list)
    for row in trials:
        groups[row['ending_type']].append(row)
    total_task = sum(r['task_seconds'] for r in trials)
    ending_summary = [{'ending_type': k, 'trials': len(v),
                       'mean_task_seconds': statistics.mean(r['task_seconds'] for r in v),
                       'total_task_seconds': sum(r['task_seconds'] for r in v),
                       'share_total_task_percent': 100*sum(r['task_seconds'] for r in v)/total_task}
                      for k, v in groups.items()]
    csv_out('ending-type-summary.csv', ending_summary)
    paired = defaultdict(list)
    for row in trials:
        paired[(row['family'], row['repetition'])].append(row)
    both = [r for pair in paired.values() if len(pair) == 2 and all(r['primary_pass'] for r in pair) for r in pair]
    assert len(both) == 26
    comparison = []
    for name, subset in [('all_attempts', trials), ('both_pass_pairs', both)]:
        for cond in ('primitives', 'macro'):
            sub = [r for r in subset if r['condition'] == cond]
            row = {'subset': name, 'condition': cond, 'trials': len(sub),
                   'correct': sum(r['primary_pass'] for r in sub)}
            for k in ('task_seconds', 'calls', 'input_tokens', 'output_tokens', 'native_operations', 'native_monotonic_seconds'):
                row['total_' + k] = sum(r[k] for r in sub)
                row['mean_' + k] = statistics.mean(r[k] for r in sub)
            comparison.append(row)
    csv_out('matched-comparison.csv', comparison)
    fits = [regression(trials, 'task_seconds'), regression(trials, 'task_minus_native_seconds'),
            regression(calls, 'total_seconds'), regression(calls, 'client_span_seconds'), regression(calls, 'eval_seconds')]
    save('regressions.json', fits)
    sums = {k: sum(r[k] for r in trials) for k in (
        'task_seconds', 'native_monotonic_seconds', 'task_minus_native_seconds', 'trace_root_seconds',
        'trace_native_seconds', 'client_llm_span_seconds', 'server_total_seconds', 'server_load_seconds',
        'server_prompt_eval_seconds', 'server_eval_seconds', 'server_server_other_seconds',
        'trace_root_minus_client_llm_and_native_seconds')}
    save('analysis.json', {'scope': 'Exploratory archived timing analysis; not an M4 rescore or live serving comparison',
        'trials': len(trials), 'calls': len(calls), 'totals': sums, 'ending_types': ending_summary,
        'comparisons': comparison, 'regressions': fits,
        'median_recorded_generation_tokens_per_second': statistics.median(r['generation_tokens_per_second'] for r in calls),
        'clock_warning': 'Task and native durations use WSL monotonic; trace durations use timestamp differences; provider durations use server timings. Boundaries/clocks are uncalibrated. Server time exceeding task time is retained, not assigned negative overhead.',
        'client_vs_server_cache': 'cache=False is LangChain response caching, not proof of disabled Ollama prompt/KV reuse.'})
    patterns = ('offloaded', 'model buffer size', 'KV buffer size', 'K (f16)',
                'RS buffer size', 'Flash Attention enabled', 'flash_attn ',
                'prompt cache is enabled', 'model size:', 'id=0, n_layer=')
    log_lines = HIST_LOG.read_text(encoding='utf-8', errors='replace').splitlines()
    excerpts = [{'line': i+1, 'text': line} for i, line in enumerate(log_lines)
                if any(p in line for p in patterns)]
    save('historical-server-log-excerpts.json', {'source': str(HIST_LOG.relative_to(EVAL)),
        'sha256': sha(HIST_LOG), 'excerpts': excerpts})
    save('source-integrity.json', {'m4_sources': source_hashes, 'frozen_source_checks': frozen_checks,
        'protected_m4_file_count': len(protected),
        'all_m4_files_unchanged_after_analysis': all(p.is_file() and sha(p) == expected
            for rel, expected in protected.items() for p in [M4 / rel]),
        'historical_server_log_sha256': sha(HIST_LOG), 'analyzer_sha256': sha(Path(__file__)),
        'new_inference_requests': 0})
    print(json.dumps({'trials': len(trials), 'calls': len(calls), 'all_fields': dict(field_counts),
                      'totals': sums, 'ending_types': ending_summary, 'regressions': fits}, indent=2))


if __name__ == '__main__':
    main()
