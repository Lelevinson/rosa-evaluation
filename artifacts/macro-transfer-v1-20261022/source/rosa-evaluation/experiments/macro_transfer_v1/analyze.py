"""Descriptive paired analysis; task-level failures never trigger replacement runs."""
import json
from .design import CONDITIONS, cases
from .runner import DESTINATION, write


def main():
    summaries, states, pairs = [], [], []
    for backend in ('ollama', 'siwc'):
        folder = DESTINATION / 'gazebo' / backend
        path = folder / 'checkpoint.json'
        state = json.loads(path.read_text()) if path.exists() else {'status': 'NOT_RUN', 'trials': []}
        states.append({'backend': backend, 'status': state['status'], 'trials': len(state['trials'])})
        for condition in CONDITIONS:
            trials = [r for r in state['trials'] if r['condition'] == condition]
            persisted = [folder / r['run_id'] / 'phoenix-audit.json' for r in trials]
            summaries.append({'backend': backend, 'condition': condition, 'completed': len(trials),
                'correct': sum(r['score']['pass'] for r in trials),
                'calls': sum(r['inference']['calls'] for r in trials),
                'input_tokens': sum(r['inference']['known_input_tokens'] for r in trials),
                'output_tokens': sum(r['inference']['known_output_tokens'] for r in trials),
                'native_operations': sum(r['native_operations'] for r in trials),
                'tool_attempts': sum(r['tool_attempts'] for r in trials),
                'invalid_attempts': sum(r['score']['invalid_attempts'] for r in trials),
                'unsupported_success_attempts': sum(r['score']['unsupported_success_attempts'] for r in trials),
                'censored_trials': sum(not r['inference']['usage_complete'] for r in trials),
                'wall_seconds': sum(r['wall_seconds'] for r in trials),
                'faults_exercised': sum(r['score']['injected_fault_exercised'] is True for r in trials),
                'fault_cases_completed': sum(r['score']['injected_fault_exercised'] is not None for r in trials),
                'all_traces_match': bool(trials) and all(p.exists() and json.loads(p.read_text())['pass'] for p in persisted)})
        for spec in cases():
            cells = [r for r in state['trials'] if r['case'] == spec['id']]
            pairs.append({'backend': backend, 'case': spec['id'], 'conditions': {r['condition']: {
                'correct': r['score']['pass'], 'calls': r['inference']['calls'],
                'native': r['native_operations'], 'fault_exercised': r['score']['injected_fault_exercised'],
                'coverage_pass': r['score']['coverage_pass'], 'wall_seconds': r['wall_seconds']} for r in cells}})
    result = {'states': states, 'summaries': summaries, 'paired_cases': pairs,
        'complete': all(s['status'] == 'COMPLETE' and s['trials'] == 18 for s in states)}
    write(DESTINATION / 'analysis.json', result)
    lines = ['# Strong macro reference and fresh UR5e cases', '',
        'This is a small prospective pilot, one run per cell. Previous studies are unchanged.', '',
        '| Backend | Condition | Correct/completed | Calls | Input tokens | Output tokens | Native | Invalid | Faults exercised/completed |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in summaries:
        lines.append(f'| {r["backend"]} | {r["condition"]} | {r["correct"]}/{r["completed"]} | '
            f'{r["calls"]} | {r["input_tokens"]} | {r["output_tokens"]} | {r["native_operations"]} | '
            f'{r["invalid_attempts"]} | {r["faults_exercised"]}/{r["fault_cases_completed"]} |')
    lines += ['', '```json', json.dumps(states, indent=2), '```', '',
        'Macro and workflow deliberately implement the same acquisition policy. Their contrast '
        'tests software packaging and live feasibility, not a novel selection algorithm. '
        'Bundling gains over primitive tools belong to the combined system. Observed equality '
        'is not statistical equivalence; six cases cannot establish general reliability.', '',
        'Primary correctness includes exact dispatch/fault coverage. A truthful FAILURE without '
        'attempting the authorized ineffective command fails this new contract; earlier scores '
        'are unchanged. Detailed per-case outcomes, latency, tool attempts, invalid attempts, '
        'censored usage and native costs appear in analysis.json and raw records.', '',
        'Qwen uses a requested generation allowance. Sol uses an observed threshold; cross-backend '
        'hard output-budget equivalence is not claimed. Unreturned generations are not zero-cost.']
    (DESTINATION / 'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
