import json
from .runner import DESTINATION, write


def main():
    rows, states = [], []
    for phase in ('mock', 'gazebo'):
        for backend in ('ollama', 'siwc'):
            path = DESTINATION / phase / backend / 'checkpoint.json'
            state = json.loads(path.read_text()) if path.exists() else {'status': 'NOT_RUN', 'trials': []}
            states.append({'phase': phase, 'backend': backend, 'status': state['status'], 'completed': len(state['trials'])})
            for program in (False, True):
                trials = [r for r in state['trials'] if r['program_managed'] == program]
                persisted = [DESTINATION / phase / backend / r['run_id'] / 'phoenix-audit.json' for r in trials]
                rows.append({'phase': phase, 'backend': backend, 'program': program, 'completed': len(trials),
                    'correct': sum(r['score']['pass'] for r in trials),
                    'calls': sum(r['inference']['calls'] for r in trials),
                    'input_tokens': sum(r['inference']['known_input_tokens'] for r in trials),
                    'output_tokens': sum(r['inference']['known_output_tokens'] for r in trials),
                    'native_operations': sum(r['native_operations'] for r in trials),
                    'invalid_attempts': sum(r['score']['invalid_attempts'] for r in trials),
                    'censored_trials': sum(not r['inference']['usage_complete'] for r in trials),
                    'wall_seconds': sum(r['wall_seconds'] for r in trials),
                    'all_traces_match': bool(trials) and all(p.exists() and json.loads(p.read_text())['pass'] for p in persisted)})
    result = {'states': states, 'rows': rows, 'all_planned_collected': all(s['status'] == 'COMPLETE' for s in states)}
    gate_path = DESTINATION / 'mock-gate.json'
    result['mock_gate'] = json.loads(gate_path.read_text()) if gate_path.exists() else None
    write(DESTINATION / 'analysis.json', result)
    lines = ['# Common observation-reference reporting and UR5e transfer', '',
        'Prospective engineering/integration pilot; previous failed Qwen gate is unchanged.', '',
        '| Phase | Backend | Condition | Correct / completed | Calls | Output tokens | Native | Invalid |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in rows:
        lines.append(f'| {r["phase"]} | {r["backend"]} | {"program" if r["program"] else "model"} | '
            f'{r["correct"]}/{r["completed"]} | {r["calls"]} | {r["output_tokens"]} | '
            f'{r["native_operations"]} | {r["invalid_attempts"]} |')
    lines += ['', '```json', json.dumps(states, indent=2), '```', '',
        'Mock gate: ' + str(result['mock_gate']) + '.', '',
        'Correct fault outcomes may be FAILURE or UNKNOWN; they are not successful movements. '
        'The program retrieves report values from a cited existing observation; the model supplies '
        'classification. This is combined-system performance. No old trial was rescored.', '',
        'Native operations, invalid attempts and token costs are reported alongside model calls. '
        'Qwen has a hard requested output budget; Sol has an observed stopping threshold, not '
        'a hard generation cap. Censored usage must not be treated as zero.', '',
        'These fresh cases are development-informed and single-repetition. No statistical, '
        'general reliability or collision-safety claim follows. Before a larger experiment, '
        'include a comparable macro-skill reference and held-out tasks/repetitions.']
    (DESTINATION / 'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
