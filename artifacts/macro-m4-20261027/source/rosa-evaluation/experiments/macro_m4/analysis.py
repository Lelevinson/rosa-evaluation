"""Aggregate saved attempts. No trial reruns, omitted failures or imputed passes."""
import hashlib
import json
from pathlib import Path

from .runner import BASE, write


def answer_digest(answer): return hashlib.sha256(json.dumps(answer, sort_keys=True).encode()).hexdigest()


def analyze():
    reviews_path = BASE / 'clarification-review.json'
    reviews = json.loads(reviews_path.read_text()) if reviews_path.exists() else {}
    result = {'backends': {}, 'clarification_review_pending': [], 'observed_dispatch_violations': []}
    for backend in ('siwc', 'ollama'):
        path = BASE / backend / 'checkpoint.json'
        if not path.exists():
            result['backends'][backend] = {'status': 'UNSTARTED', 'scheduled': 40}
            continue
        checkpoint = json.loads(path.read_text())
        rows = checkpoint['trials']
        for row in rows:
            key = backend + '/' + row['job']['id']
            row['analysis_primary_pass'] = bool(row['primary_pass'] and row.get('phoenix_audit', {}).get('pass'))
            row['analysis_completion_including_recovery'] = bool(row['completion_including_recovery'] and
                row.get('phoenix_audit', {}).get('pass'))
            if row['case'] == 'ambiguous_goal':
                review = reviews.get(key)
                if review is None:
                    result['clarification_review_pending'].append({'key': key, 'answer': row['answer'],
                        'automated_pass': row['score']['pass'], 'answer_sha256': answer_digest(row['answer'])})
                else:
                    if review['answer_sha256'] != answer_digest(row['answer']): raise RuntimeError('review_answer_changed')
                    if type(review['pass']) is not bool or not review.get('reason'): raise RuntimeError('invalid_review')
                    row['analysis_primary_pass'] &= review['pass']
                    row['analysis_completion_including_recovery'] &= review['pass']
            if row['score']['dispatch_violations']:
                result['observed_dispatch_violations'].append({'key': key, 'violations': row['score']['dispatch_violations']})
        conditions = {}
        for condition in ('primitives', 'macro'):
            subset = [r for r in rows if r['condition'] == condition]
            conditions[condition] = {'attempts_with_results': len(subset),
                'primary_passes': sum(r['analysis_primary_pass'] for r in subset),
                'completion_including_recovery': sum(r['analysis_completion_including_recovery'] for r in subset),
                'model_requests': sum(r['inference']['calls'] for r in subset),
                'charged_decision_calls': sum(r['inference']['decision_calls'] for r in subset),
                'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in subset),
                'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in subset),
                'usage_incomplete_trials': sum(not r['inference']['usage_complete'] for r in subset),
                'infrastructure_recovered_trials': sum(r['infrastructure_recovered'] for r in subset),
                'native_operations': sum(r['score']['native_operations'] for r in subset),
                'invalid_attempts': sum(r['score']['invalid_attempts'] for r in subset),
                'wrong_goal_accepted_successes': sum(r['score']['accepted_success_wrong_user_goal'] for r in subset),
                'unsupported_success_attempts': sum(r['score']['unsupported_success_attempts'] for r in subset),
                'task_wall_seconds': sum(r['wall_seconds'] for r in subset),
                'persisted_trace_passes': sum(r.get('phoenix_audit', {}).get('pass', False) for r in subset)}
        by_pair = {}
        for row in rows: by_pair.setdefault((row['case'], row['repetition']), {})[row['condition']] = row
        paired = [pair for pair in by_pair.values() if set(pair) == {'macro', 'primitives'}]
        both = [pair for pair in paired if all(r['analysis_primary_pass'] for r in pair.values())]
        calls = {c: sum(p[c]['inference']['calls'] for p in both) for c in conditions}
        native = {c: sum(p[c]['score']['native_operations'] for p in both) for c in conditions}
        reduction = 1 - calls['macro'] / calls['primitives'] if calls['primitives'] else None
        ratio = native['macro'] / native['primitives'] if native['primitives'] else None
        wins = [p['macro']['case'] + '/r' + str(p['macro']['repetition']) for p in paired
            if p['macro']['analysis_primary_pass'] and not p['primitives']['analysis_primary_pass']]
        losses = [p['macro']['case'] + '/r' + str(p['macro']['repetition']) for p in paired
            if p['primitives']['analysis_primary_pass'] and not p['macro']['analysis_primary_pass']]
        audited = all(r['local_audit']['pass'] and r.get('phoenix_audit', {}).get('pass') for r in rows)
        complete = checkpoint['status'] == 'COMPLETE' and len(rows) == 40 and len(paired) == 20
        pending = any(r['key'].startswith(backend + '/') for r in result['clarification_review_pending'])
        screen = bool(complete and audited and not pending and not any(r['score']['dispatch_violations'] for r in rows) and
            conditions['macro']['primary_passes'] >= conditions['primitives']['primary_passes'] and
            reduction is not None and reduction >= .25 and ratio is not None and ratio <= 1.25)
        result['backends'][backend] = {'status': checkpoint['status'], 'scheduled': 40,
            'attempts_with_results': len(rows), 'interrupted_current_trial': checkpoint['current_trial'],
            'unstarted_or_no_result_cells': 40 - len(rows), 'conditions': conditions,
            'paired_cells': len(paired), 'matched_primary_success_pairs': len(both),
            'matched_calls': calls, 'matched_native_operations': native,
            'matched_call_reduction': reduction, 'matched_native_ratio': ratio,
            'macro_paired_wins': wins, 'macro_paired_losses': losses, 'engineering_screen_pass': screen,
            'campaign': checkpoint['campaign'], 'simulator_cleanup': checkpoint['simulator_cleanup'],
            'total_elapsed_seconds': checkpoint['total_elapsed_seconds']}
    result['complete'] = (not result['clarification_review_pending'] and
        all(b.get('status') == 'COMPLETE' and b.get('attempts_with_results') == 40 for b in result['backends'].values()))
    write(BASE / 'analysis.json', result)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__': analyze()
