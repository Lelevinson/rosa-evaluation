"""Read-only analysis of the frozen live validation; never changes scores."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from experiments.prompt_live_v1.runner import DESTINATION, verify_freeze, write


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def summarize():
    manifest = verify_freeze()
    summary = {'protocol': manifest['protocol'], 'backends': {},
        'engineering_gate': False, 'progression_gate': False,
        'historical_results_unchanged': True}
    lines = ['# Live prompt-contract validation', '',
        'Known development cases, one run per case/condition; not a causal efficacy study.', '']
    for backend in ('ollama', 'siwc'):
        folder = DESTINATION / 'gazebo' / backend
        state_path = folder / 'checkpoint.json'
        if not state_path.exists():
            summary['backends'][backend] = {'status': 'NOT_STARTED'}
            continue
        state = read(state_path)
        rows = state['trials']
        censored = [r for r in rows if not r['inference']['usage_complete']]
        controls_path = folder / 'fresh-controls/result.json'
        controls = read(controls_path) if controls_path.exists() else {}
        control_pass = bool(controls.get('pass') and len(controls.get('rows', [])) == 6)
        audits = []
        for row in rows:
            trial = folder / row['run_id']
            audit_paths = [trial / 'phoenix-audit.json', trial / 'model-input-contract.json']
            audits.append(row['audit']['pass'] and all(p.exists() and read(p)['pass'] for p in audit_paths))
        safe = all(not r['score']['dispatch_violations'] and
            not r['score']['accepted_unsupported_selected_goal_success'] and
            r['inference']['calls'] <= 8 and r['native_operations'] <= 10 for r in rows)
        cleanup = state.get('simulator_cleanup', {}).get('returncode') == 0
        auth_cleanup = None
        if backend == 'siwc':
            auth_path = DESTINATION / 'session-siwc.json'
            auth_cleanup = auth_path.exists() and read(auth_path)['auth'].get('session_cleanup') == 'REVOKED'
            cleanup = cleanup and auth_cleanup
        else:
            cleanup = cleanup and (DESTINATION / 'local-model-unload.json').exists()
        engineering = (state['status'] == 'COMPLETE' and len(rows) == 9 and control_pass and
            all(audits) and safe and state['total_model_calls'] <= 72 and cleanup)
        groups = defaultdict(list)
        for row in rows:
            groups[row['condition']].append(row)
        out = {'status': state['status'], 'trials': len(rows), 'correct': sum(r['score']['pass'] for r in rows),
            'completed_scoreable_trials': len(rows) - len(censored), 'service_censored_attempts': len(censored),
            'unstarted_cells': 9 - len(rows),
            'reserved_calls': state['total_model_calls'], 'audited_trials': sum(audits),
            'deterministic_controls_pass': control_pass, 'cleanup_verified': cleanup,
            'engineering_gate': engineering,
            'progression_gate': engineering and all(r['score']['pass'] for r in rows), 'conditions': {}}
        lines += [f'## {backend}', '', f"Status: {state['status']}; {out['correct']}/{len(rows)} correct; "
                  f"{state['total_model_calls']} reserved inference requests.", '',
                  f"Scoreable completed trials: {out['completed_scoreable_trials']}; censored attempts: {len(censored)}; "
                  f"unstarted cells: {out['unstarted_cells']}. A service-censored raw score is not an established model failure.", '']
        lines += ['| Condition | Correct | Calls | Input tokens | Output tokens | Native operations | Invalid attempts | Corrected trials | Trial seconds |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for condition, group in groups.items():
            item = {'trials': len(group), 'correct': sum(r['score']['pass'] for r in group),
                'calls': sum(r['inference']['calls'] for r in group),
                'input_tokens': sum(r['inference']['known_input_tokens'] for r in group),
                'output_tokens': sum(r['inference']['known_output_tokens'] for r in group),
                'native_operations': sum(r['native_operations'] for r in group),
                'invalid_attempts': sum(r['score']['invalid_attempts'] for r in group),
                'corrected_trials': sum(r['score']['corrected_after_feedback'] for r in group),
                'program_native_operations': sum(r['score']['program_native_operations'] for r in group),
                'usage_complete': all(r['inference']['usage_complete'] for r in group),
                'wall_seconds': sum(r['wall_seconds'] for r in group)}
            out['conditions'][condition] = item
            lines.append(f"| {condition} | {item['correct']}/{item['trials']} | {item['calls']} | "
                f"{item['input_tokens']} | {item['output_tokens']} | {item['native_operations']} | "
                f"{item['invalid_attempts']} | {item['corrected_trials']} | {item['wall_seconds']:.2f} |")
        for row in rows:
            if not row['score']['pass']:
                lines += ['', f"Failed frozen contract: {row['run_id']}. Score: `{json.dumps(row['score'], sort_keys=True)}`"]
        lines += ['', f"Engineering gate: {engineering}. Progression gate: {out['progression_gate']}.", '']
        summary['backends'][backend] = out
    summary['engineering_gate'] = all(summary['backends'][b].get('engineering_gate', False) for b in ('ollama', 'siwc'))
    summary['progression_gate'] = all(summary['backends'][b].get('progression_gate', False) for b in ('ollama', 'siwc'))
    lines += ['## Interpretation', '',
        'The opt-in repair changes the common system-prefix instructions only. Historical results remain intact. '
        'Known cases and tiny sample size prohibit a general reliability or causal prompt-effect claim. '
        'Task outcomes, engineering conformance and readiness to progress are reported separately. '
        'A correct outcome after rejected attempts is a combined-system result; it does not erase '
        'the model error. Program-managed native operations are explicitly attributed to ROSA. '
        'This validation retains the preceding scorer: one-additional-read wording is guidance '
        'and is not independently enforced as a hard retry ceiling. Exceedances must be disclosed '
        'as behavior, not silently rescored. The fresh pilot proposes explicit prospective retry-policy scoring.', '',
        f"Overall engineering gate: {summary['engineering_gate']}. Overall progression gate: {summary['progression_gate']}.", '',
        'No fresh held-out pilot may start automatically while its readiness gate is false. '
        'Do not repair/tune prompts on these outcomes and relabel a repeat as this frozen validation.']
    write(DESTINATION / 'analysis.json', summary)
    (DESTINATION / 'VALIDATION_REPORT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    summarize()
