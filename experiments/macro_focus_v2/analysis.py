"""Prospective descriptive retention analysis; never modifies trial scores."""
from collections import defaultdict
import json
from .runner import DESTINATION, verify_freeze, write


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def totals(rows):
    return {'trials': len(rows), 'correct': sum(r['score']['pass'] for r in rows),
        'calls': sum(r['inference']['calls'] for r in rows),
        'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in rows),
        'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in rows),
        'native_operations': sum(r['native_operations'] for r in rows),
        'program_native_operations': sum(r['score']['program_native_operations'] for r in rows),
        'invalid_attempts': sum(r['score']['invalid_attempts'] for r in rows),
        'corrected_trials': sum(r['score']['corrected_after_feedback'] for r in rows),
        'unsupported_success_attempts': sum(r['score']['unsupported_success_attempts'] for r in rows),
        'accepted_unsupported_success': sum(r['score']['accepted_unsupported_selected_goal_success'] for r in rows),
        'accepted_wrong_user_goal_success': sum(r['score'].get('accepted_wrong_user_goal_success', False) for r in rows),
        'retry_policy_violations': sum('observation_retry_guidance_exceeded' in r['score'].get('policy_violations', []) for r in rows),
        'unsafe_dispatches': sum(bool(r['score']['dispatch_violations']) for r in rows),
        'fault_exercised_trials': sum(r['score']['injected_fault_exercised'] is True for r in rows),
        'usage_complete': all(r['inference']['usage_complete'] for r in rows),
        'wall_seconds': sum(r['wall_seconds'] for r in rows)}


def comparison(rows, candidate, reference, call_ratio, native_ratio):
    groups = defaultdict(dict)
    for row in rows:
        groups[(row['case'], row['repetition'])][row['condition']] = row
    pairs = [(key, group[candidate], group[reference]) for key, group in groups.items()
             if candidate in group and reference in group]
    matched = [(key, a, b) for key, a, b in pairs if a['score']['pass'] and b['score']['pass']]
    losses = [key for key, a, b in pairs if not a['score']['pass'] and b['score']['pass']]
    wins = [key for key, a, b in pairs if a['score']['pass'] and not b['score']['pass']]
    a, b = totals([x[1] for x in matched]), totals([x[2] for x in matched])
    sufficient = len(pairs) == 12 and len(matched) >= 6
    pass_screen = sufficient and not losses and a['calls'] <= call_ratio * b['calls'] and (
        a['native_operations'] <= native_ratio * b['native_operations'])
    return {'paired_cells': len(pairs), 'matched_correct_pairs': len(matched),
        'candidate_losses': losses, 'candidate_wins': wins,
        'matched_candidate': a, 'matched_reference': b, 'sufficient': sufficient,
        'screen_pass': pass_screen,
        'matched_call_reduction_fraction': 1 - a['calls'] / b['calls'] if b['calls'] else None,
        'paired_details': [{'case': key[0], 'repetition': key[1],
            'candidate_correct': x['score']['pass'], 'reference_correct': y['score']['pass'],
            'candidate_calls': x['inference']['calls'], 'reference_calls': y['inference']['calls'],
            'candidate_native': x['native_operations'], 'reference_native': y['native_operations']}
            for key, x, y in pairs]}


def main():
    verify_freeze()
    report = {'protocol': 'macro-focus-v2', 'backends': {}, 'study_complete_and_audited': False}
    lines = ['# Fresh bounded macro-skill pilot', '',
        'Prospective six-case, two-repetition comparison. One bounded UR5e pose capability. '
        'These are descriptive feasibility results, not evidence of a novel selection algorithm.', '']
    for backend in ('ollama', 'siwc'):
        folder = DESTINATION / 'gazebo' / backend
        if not (folder / 'checkpoint.json').exists():
            report['backends'][backend] = {'status': 'NOT_STARTED', 'complete_and_audited': False}
            continue
        state = read(folder / 'checkpoint.json')
        rows = state['trials']
        controls_path = folder / 'fresh-controls/result.json'
        controls = read(controls_path) if controls_path.exists() else {}
        audits = []
        for row in rows:
            trial = folder / row['run_id']
            paths = [trial / 'phoenix-audit.json', trial / 'model-input-contract.json']
            audits.append(row['audit']['pass'] and all(p.exists() and read(p)['pass'] for p in paths))
        cleanup = state.get('simulator_cleanup', {}).get('returncode') == 0
        cleanup_path = DESTINATION / ('session-siwc.json' if backend == 'siwc' else 'local-model-unload.json')
        if backend == 'siwc':
            cleanup = cleanup and cleanup_path.exists() and read(cleanup_path)['auth'].get('session_cleanup') == 'REVOKED'
        else:
            cleanup = cleanup and cleanup_path.exists()
        complete = (state['status'] == 'COMPLETE' and len(rows) == 36 and all(audits) and
            controls.get('pass') and len(controls.get('rows', [])) == 6 and cleanup and
            not any(r['score']['accepted_unsupported_selected_goal_success'] or
                    r['score']['dispatch_violations'] for r in rows))
        groups = {condition: [r for r in rows if r['condition'] == condition]
                  for condition in ('model', 'macro', 'workflow')}
        out = {'status': state['status'], 'complete_and_audited': bool(complete),
            'reserved_calls': state['total_model_calls'], 'accounted_trial_calls': sum(r['inference']['calls'] for r in rows),
            'current_trial': state.get('current_trial'), 'audited_trials': sum(audits),
            'cleanup_verified': cleanup, 'conditions': {c: totals(g) for c, g in groups.items()},
            'macro_vs_primitives': comparison(rows, 'macro', 'model', .8, 1.2),
            'workflow_vs_primitives': comparison(rows, 'workflow', 'model', .8, 1.2),
            'workflow_vs_macro': comparison(rows, 'workflow', 'macro', .9, 1.)}
        # Prespecified sensitivity excludes the entire first case/repetition
        # group (all conditions), not whichever individual trial is slowest.
        first = (rows[0]['case'], rows[0]['repetition']) if rows else None
        out['latency_sensitivity_excluding_first_group'] = {c: sum(r['wall_seconds'] for r in g
            if (r['case'], r['repetition']) != first) for c, g in groups.items()}
        out['per_case_repetitions'] = {case: {c: [
            {'repetition': r['repetition'], 'correct': r['score']['pass'],
             'calls': r['inference']['calls'], 'wall_seconds': r['wall_seconds']}
            for r in g if r['case'] == case] for c, g in groups.items()}
            for case in sorted({r['case'] for r in rows})}
        report['backends'][backend] = out
        lines += [f'## {backend}', '', f"Status: {state['status']}. Reserved requests: {state['total_model_calls']}. "
                  f"Completed/audited trial rows: {sum(audits)}/{len(rows)}.", '',
            '| Condition | Correct | Calls | Input tokens | Output tokens | Native | Invalid attempts | Trial seconds |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
        for c, item in out['conditions'].items():
            lines.append(f"| {c} | {item['correct']}/{item['trials']} | {item['calls']} | "
                f"{item['known_input_tokens']} | {item['known_output_tokens']} | {item['native_operations']} | "
                f"{item['invalid_attempts']} | {item['wall_seconds']:.2f} |")
        lines.append('')
        for row in rows:
            if not row['score']['pass']:
                lines += [f"- Failed contract: {row['run_id']}: `{json.dumps(row['score'], sort_keys=True)}`"]
        lines.append('')
    report['study_complete_and_audited'] = all(report['backends'][b].get('complete_and_audited', False)
        for b in ('ollama', 'siwc'))
    report['retention_decision'] = 'INCOMPLETE_OR_AUDIT_FAILURE_NO_RETENTION_CLAIM'
    if report['study_complete_and_audited']:
        both = [report['backends'][b] for b in ('ollama', 'siwc')]
        macro = all(b['macro_vs_primitives']['screen_pass'] for b in both)
        wf_primitive = all(b['workflow_vs_primitives']['screen_pass'] for b in both)
        wf_macro = [b['workflow_vs_macro'] for b in both]
        dominates_macro = (all(c['sufficient'] and not c['candidate_losses'] and
            c['matched_candidate']['calls'] <= c['matched_reference']['calls'] and
            c['matched_candidate']['native_operations'] <= c['matched_reference']['native_operations'] and
            c['matched_candidate']['wall_seconds'] <= 1.1 * c['matched_reference']['wall_seconds'] for c in wf_macro)
            and any(c['screen_pass'] for c in wf_macro))
        report['retention_decision'] = ('RETAIN_WORKFLOW_CANDIDATE' if wf_primitive and dominates_macro else
            'PREFER_SIMPLE_MACRO' if macro else 'KEEP_PRIMITIVE_REFERENCE_NO_PACKAGING_RETENTION')
    lines += ['## Decision', '', report['retention_decision'], '',
        'See analysis.json for paired correctness/cost screens, all-attempt totals, fault coverage, '
        'actor attribution, feedback corrections, per-case repetitions and the prespecified latency '
        'sensitivity. Unstarted or censored cells are never assumed successful. Correct guarded '
        'outcomes do not erase invalid model attempts. UNKNOWN can be correct despite private goal '
        'attainment when the actor lacks outcome evidence. Native operations include bundled work.', '',
        'The two repetitions share six case templates. No statistical significance, general robot-task '
        'advantage or improvement to model weights is claimed. A retained candidate only passed this '
        'small, deliberately limited descriptive screen. Keep the original campaign and separate '
        'prompt-validation findings intact; combine discussion reports later.']
    write(DESTINATION / 'analysis.json', report)
    (DESTINATION / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'study_complete_and_audited': report['study_complete_and_audited'],
                      'retention_decision': report['retention_decision']}))


if __name__ == '__main__':
    main()
