"""Report within-backend paired pilot outcomes, including incomplete attempts."""
import json
from .design import CASES
from .runner import DESTINATION, write


def main():
    backends = []
    for backend in ('ollama', 'siwc'):
        path = DESTINATION / backend / 'checkpoint.json'
        status = json.loads(path.read_text()) if path.exists() else {'status': 'NOT_STARTED', 'trials': []}
        rows = status['trials']
        indexed = {(r['case'], r['program_managed']): r for r in rows}
        conditions = []
        for program in (False, True):
            data = [r for r in rows if r['program_managed'] == program]
            conditions.append({'program_managed': program, 'completed': len(data),
                'correct': sum(r['score']['pass'] for r in data),
                'healthy_correct': sum(r['score']['pass'] for r in data if r['case'] in ('east_healthy', 'west_healthy')),
                'model_calls': sum(r['inference']['calls'] for r in data),
                'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in data),
                'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in data),
                'output_upper_bound': sum(r['inference']['output_upper_bound'] for r in data)
                    if all(r['inference']['output_upper_bound'] is not None for r in data) else None,
                'censored_trials': sum(not r['inference']['usage_complete'] for r in data),
                'native_operations': sum(r['native_operations'] for r in data),
                'wall_seconds_all_attempts': sum(r['wall_seconds'] for r in data),
                'invalid_attempts': sum(r['score']['invalid_attempts'] for r in data),
                'unsupported_attempts': sum(r['score']['unsupported_success_attempts'] for r in data),
                'wrong_skill_trials': sum(not r['score']['correct_skill'] for r in data)})
        pairs, persisted_ok = [], True
        for row in rows:
            folder = DESTINATION / backend / row['run_id']
            persisted = folder / 'phoenix-audit.json'
            persisted_ok = persisted_ok and persisted.exists() and json.loads(persisted.read_text())['pass']
        for spec in CASES:
            reference, program = indexed.get((spec['id'], False)), indexed.get((spec['id'], True))
            if reference and program:
                pairs.append({'case': spec['id'], 'reference_correct': reference['score']['pass'],
                    'program_correct': program['score']['pass'],
                    'paired_loss': reference['score']['pass'] and not program['score']['pass'],
                    'reference_calls': reference['inference']['calls'], 'program_calls': program['inference']['calls'],
                    'program_no_extra_native': program['native_operations'] <= reference['native_operations']})
        complete = status['status'] == 'COMPLETE' and len(rows) == 12
        valid = complete and persisted_ok and all(r['audit']['pass'] for r in rows) and not any(
            r['score']['accepted_unsupported_selected_goal_success'] or r['score']['dispatch_violations'] for r in rows)
        efficiency = [p['case'] for p in pairs if p['case'] in ('east_healthy', 'west_healthy') and
            p['reference_correct'] and p['program_correct'] and p['program_calls'] < p['reference_calls'] and p['program_no_extra_native']]
        healthy = conditions[1]['healthy_correct'] == 2
        gate = valid and healthy and not any(p['paired_loss'] for p in pairs) and bool(efficiency)
        backends.append({'backend': backend, 'status': status['status'], 'valid': valid,
            'candidate_feasibility_gate': gate, 'conditions': conditions, 'pairs': pairs,
            'jointly_correct_healthy_call_savings': efficiency,
            'all_persisted_traces_match': persisted_ok if rows else False})
    complete = all(b['status'] == 'COMPLETE' for b in backends)
    result = {'status': 'COMPLETE' if complete else 'PARTIAL', 'backends': backends,
              'both_backends_feasibility_gate': complete and all(b['candidate_feasibility_gate'] for b in backends),
              'interpretation': 'small development-informed pilot; complete orchestration effect, no significance/generalization claim'}
    write(DESTINATION / 'analysis.json', result)
    lines = ['# Workflow live v1: feasibility report', '', '**Status: ' + result['status'] + '.**', '',
        'This tests the complete orchestration arrangement on six development-informed cases per backend. '
        'It is not a held-out benchmark, a novel routing algorithm claim, or a physical-robot safety evaluation.', '',
        '| Backend | Condition | Correct / completed | Healthy correct / 2 | Calls | Known output tokens | Invalid attempts |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for backend in backends:
        for c in backend['conditions']:
            lines.append(f'| {backend["backend"]} | {"program" if c["program_managed"] else "model"} | '
                f'{c["correct"]}/{c["completed"]} | {c["healthy_correct"]}/2 | {c["model_calls"]} | '
                f'{c["known_output_tokens"]} | {c["invalid_attempts"]} |')
    lines += ['', 'A correct fault trial can truthfully report FAILURE or UNKNOWN; it is not a successful movement.', '',
        'Both-backend progression gate: **' + str(result['both_backends_feasibility_gate']) + '**.',
        'Do not interpret a pending backend as a failed candidate; inspect status and paired records in analysis.json.', '',
        'Sol uses unchanged account defaults with an observed cumulative output stopping threshold, not a hard '
        'generation cap. Qwen uses 1024 maximum per call and a hard cumulative requested allowance of 2048. '
        'Unreturned usage is censored; totals above are known returned usage only. Compare conditions within each backend.', '',
        'All trial results, raw tool/model evidence, local spans and exact persisted Phoenix spans are retained. '
        'Authorization loss and interruptions are checkpointed; no failed trial is silently rerun.', '',
        'Gazebo transfer requires a separately bounded protocol after this gate; no automatic large campaign is launched.']
    (DESTINATION / 'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
