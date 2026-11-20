"""Combine scoreable cells, retain every original attempt and censored cost."""
from collections import defaultdict
import json
from .runner import BASE, DESTINATION, read, verify_freeze, jobs, original


def audited(folder, row):
    trial = folder / row['run_id']
    paths = [trial / 'phoenix-audit.json', trial / 'model-input-contract.json']
    return row['audit']['pass'] and all(p.exists() and read(p)['pass'] for p in paths)


def costs(rows):
    return {'attempt_rows': len(rows), 'calls': sum(r['inference']['calls'] for r in rows),
        'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in rows),
        'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in rows),
        'unreturned_requests': sum(sum(e['status'] == 'UNRETURNED' for e in r['inference']['events']) for r in rows),
        'native_operations': sum(r['native_operations'] for r in rows),
        'program_native_operations': sum(r['score']['program_native_operations'] for r in rows),
        'invalid_attempts': sum(r['score']['invalid_attempts'] for r in rows),
        'corrected_trials': sum(r['score']['corrected_after_feedback'] for r in rows),
        'wall_seconds': sum(r['wall_seconds'] for r in rows)}


def main():
    verify_freeze()
    initial = read(BASE / 'analysis.json')
    result = {'protocol': 'prompt-contract-v1-live+continuation-r1', 'backends': {},
        'engineering_gate': False, 'progression_gate': False, 'historical_results_unchanged': True}
    result['backends']['ollama'] = initial['backends']['ollama']
    state_path = DESTINATION / 'gazebo/siwc/checkpoint.json'
    old_state = read(BASE / 'gazebo/siwc/checkpoint.json')
    state = read(state_path) if state_path.exists() else {'status': 'NOT_STARTED', 'trials': []}
    plan = read(DESTINATION / 'schedule.json')['jobs']
    old_rows, rows = old_state['trials'], state['trials']
    completed = {index: row for index, row in enumerate(old_rows) if row['inference']['usage_complete']}
    for spec, row in zip(plan, rows):
        index = spec['original_schedule_index']
        expected = jobs('gazebo')[index]
        if (row['case'], row['condition']) != (expected['case']['id'], expected['condition']):
            raise RuntimeError('continuation_result_schedule_mismatch')
        if index in completed:
            raise RuntimeError('completed_outcome_replaced')
        if row['inference']['usage_complete']:
            completed[index] = row
    all_rows = old_rows + rows
    all_audits = [audited(BASE / 'gazebo/siwc', r) for r in old_rows] + [
        audited(DESTINATION / 'gazebo/siwc', r) for r in rows]
    controls_path = DESTINATION / 'gazebo/siwc/fresh-controls/result.json'
    controls = read(controls_path) if controls_path.exists() else {}
    cleanup_path = DESTINATION / 'session-siwc.json'
    cleanup = (state.get('simulator_cleanup', {}).get('returncode') == 0 and
        cleanup_path.exists() and read(cleanup_path)['auth'].get('session_cleanup') == 'REVOKED')
    ledger_path = DESTINATION / 'resource-ledger.json'
    ledger = read(ledger_path) if ledger_path.exists() else {}
    resource_ok = (ledger.get('combined_reserved_calls', 999) <= 72 and
        ledger.get('additional_reserved_calls', 999) <= 40 and
        ledger.get('combined_reserved_calls') == sum(r['inference']['calls'] for r in all_rows))
    safe = not any(r['score']['dispatch_violations'] or r['score']['accepted_unsupported_selected_goal_success']
                   for r in all_rows)
    engineering = (state['status'] == 'COMPLETE' and len(rows) == 5 and len(completed) == 9 and
        all(all_audits) and controls.get('pass') and len(controls.get('rows', [])) == 6 and
        initial['backends']['siwc']['deterministic_controls_pass'] and
        initial['backends']['siwc']['cleanup_verified'] and cleanup and resource_ok and safe)
    correct = sum(r['score']['pass'] for r in completed.values())
    conditions = {condition: costs([r for r in all_rows if r['condition'] == condition])
                  for condition in ('model', 'macro', 'workflow')}
    completed_conditions = {condition: {'trials': sum(r['condition'] == condition for r in completed.values()),
        'correct': sum(r['condition'] == condition and r['score']['pass'] for r in completed.values())}
        for condition in ('model', 'macro', 'workflow')}
    hosted = {'status': state['status'], 'trials': len(completed), 'correct': correct,
        'audited_trials': sum(all_audits), 'attempt_rows': len(all_rows),
        'service_censored_attempts': sum(not r['inference']['usage_complete'] for r in all_rows),
        'cleanup_verified': bool(cleanup), 'engineering_gate': bool(engineering),
        'progression_gate': bool(engineering and correct == 9),
        'conditions': conditions, 'completed_conditions': completed_conditions, 'resource_ledger': ledger,
        'all_attempt_costs': costs(all_rows),
        'scoreable_cells': [{'original_schedule_index': i, 'case': r['case'], 'condition': r['condition'],
                            'correct': r['score']['pass']} for i, r in sorted(completed.items())]}
    result['backends']['siwc'] = hosted
    result['engineering_gate'] = all(b['engineering_gate'] for b in result['backends'].values())
    result['progression_gate'] = all(b['progression_gate'] for b in result['backends'].values())
    original.write(DESTINATION / 'COMBINED_ANALYSIS.json', result)
    lines = ['# Prompt-contract live validation with bounded continuation', '',
        f"Qwen: {result['backends']['ollama']['correct']}/9 correct completed outcomes,34 model requests.",
        f"Sol: {correct}/{len(completed)} correct completed scoreable outcomes; {len(all_rows)} total attempt rows; "
        f"{hosted['service_censored_attempts']} censored attempt(s).", '',
        f"Hosted resource ledger: `{json.dumps(ledger, sort_keys=True)}`.",
        'All-attempt costs include the original interrupted attempt. Its unreturned generation has unknown cost, '
        'not zero. Its raw failed terminal score is unchanged. Four originally completed outcomes were preserved; '
        'only the read-only interrupted cell and unstarted cells were eligible for the continuation.', '',
        '| Hosted condition | Completed correct | Calls, all attempts | Known input tokens | Known output tokens | Native ops | Invalid attempts |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for condition, c in conditions.items():
        done = completed_conditions[condition]
        lines.append(f"| {condition} | {done['correct']}/{done['trials']} | {c['calls']} | "
            f"{c['known_input_tokens']} | {c['known_output_tokens']} | {c['native_operations']} | {c['invalid_attempts']} |")
    lines += ['', f"All hosted attempt audits: {sum(all_audits)}/{len(all_audits)}. Cleanup verified: {cleanup}.", '',
        f"Overall engineering gate: {result['engineering_gate']}. Overall progression gate: {result['progression_gate']}.", '',
        'This is known-case validation with one run per completed cell. It does not establish a causal prompt '
        'effect, broad reliability advantage or an improvement to model weights. Qwen attempted a write without '
        'available prerequisite data; ROSA blocked it before dispatch and Qwen corrected its final report. '
        'Such outcomes credit the guarded combined system. Additional observation attempts beyond soft retry '
        'guidance remain disclosed behavior; original frozen scores are not retrospectively changed.', '',
        'Keep the initial engineering report, initial live attempt report and this continuation report separate '
        'until the user requests the combined discussion package. The held-out pilot remains gated on the '
        'completed validation and its own prospective freeze and manual hosted consent.']
    (DESTINATION / 'COMBINED_VALIDATION_REPORT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'engineering_gate': result['engineering_gate'], 'progression_gate': result['progression_gate'],
        'hosted_completed': len(completed), 'hosted_correct': correct, 'hosted_attempts': len(all_rows)}, indent=2))


if __name__ == '__main__':
    main()
