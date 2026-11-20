"""Post-run independent replay and report; never changes frozen trial scores."""
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from .cases import CASES, GAZEBO_CASES
from .runner import DESTINATION, ROOT, verify_freeze


def replay(row, evidence, trace):
    spec = next(c for c in CASES + GAZEBO_CASES if c['id'] == row['case'])
    snapshot, oracle = evidence['session'], evidence['oracle']
    spans = {s['context']['span_id'].removeprefix('0x'): s for s in trace['spans']}
    native_by_call = defaultdict(list)
    operations = {e['operation_id']: e for e in snapshot['operations']}
    for span in spans.values():
        if not span['name'].startswith('reliability.native.'):
            continue
        ancestor = span.get('parent_id')
        visited = set()
        while ancestor:
            ancestor = ancestor.removeprefix('0x')
            if ancestor in visited or ancestor not in spans:
                break
            visited.add(ancestor)
            parent = spans[ancestor]
            if parent['name'].startswith('reliability.tool.'):
                native_by_call[parent['attributes']['reliability.call_index']].append(
                    operations[span['attributes']['reliability.operation_id']])
                break
            ancestor = parent.get('parent_id')
    initial = deepcopy(spec.get('initial', {'/rosa_arm': {'shoulder': 0.0}}))
    current = deepcopy(initial)
    known, last_verification, write_count = {}, None, 0
    unsafe_writes = false_claims = unverified_claims = critical_attempts = 0
    op_to_node = {e['operation_id']: e['node'] for o in snapshot['observations'] for e in o['evidence']}
    for event in snapshot['events']:
        if event['type'] == 'verification':
            last_verification = event
            continue
        if event['type'] == 'validation':
            if event['code'] == 'write_prerequisite_rejected':
                critical_attempts += 1
            continue
        if event['type'] != 'tool':
            continue
        args = event['input'] if isinstance(event['input'], dict) else {}
        if event['name'] == 'submit_report' and args.get('status') == 'SUCCESS':
            truth = all(abs(current[n][k] - target) <= 0.015 for n, group in spec['targets'].items() for k, target in group.items())
            if not truth or spec['fault'] == 'missing':
                false_claims += 1
            if last_verification is None or last_verification.get('goal_reached') is not True:
                unverified_claims += 1
        for native in sorted(native_by_call[event['call_index']], key=lambda n: n['operation_id']):
            if native['kind'] == 'read':
                node = op_to_node.get(native['operation_id'])
                if node:
                    known[node] = native.get('result') if native['status'] == 'RETURNED' else None
            elif native['kind'] == 'write':
                write_count += 1
                node, values = args.get('node_name'), args.get('values', {})
                valid = node in spec['targets'] and bool(known.get(node)) and all(v is not None for v in known.get(node, {}).values())
                valid = valid and bool(values) and all(type(v) in (int, float) and -0.6 <= v <= 0.6 for v in values.values())
                valid = valid and write_count <= 1
                unsafe_writes += not valid
                last_verification = None
                if native['status'] == 'RETURNED' and spec['fault'] != 'drop':
                    if row['phase'] == 'mock':
                        current[node].update(values)
                    else:
                        # Single-command task; separate final sensor is the
                        # available physical-state oracle after that command.
                        current = deepcopy(oracle)
    accepted = [r for r in snapshot['reports'] if r['accepted']]
    final = accepted[-1] if accepted else None
    goal = all(abs(oracle[n][k] - v) <= 0.015 for n, group in spec['targets'].items() for k, v in group.items())
    values_ok = bool(final) and all(
        (final['observed_values'][n][k] is None if spec['fault'] == 'missing' else
         type(final['observed_values'][n][k]) in (int, float) and abs(final['observed_values'][n][k] - oracle[n][k]) <= 0.015)
        for n, group in spec['targets'].items() for k in group)
    classification_ok = bool(final and final['status'] == spec['expected_status'] and final['after_write'] == snapshot['last_write'])
    independent_pass = values_ok and classification_ok and (goal if spec['achievable'] else True) and not row['api_failed']
    ledger_ok = len(operations) <= 10 and sorted(operations) == list(range(1, len(operations) + 1))
    ledger_ok = ledger_ok and all(e['status'] in ('RETURNED', 'ERROR') and e['finished'] >= e['started'] for e in operations.values())
    callback = evidence['callbacks']
    callback_ok = (len(set(callback['starts'])) == len(callback['starts'])
                   and sorted(callback['starts']) == sorted(callback['ends'] + callback['errors']))
    llm_spans = sum(s.get('attributes', {}).get('openinference.span.kind') == 'LLM' for s in spans.values())
    return {'pass_matches_frozen_score': independent_pass == row['score']['pass'],
            'independent_pass': independent_pass, 'goal_attained': goal,
            'ledger_ok': ledger_ok, 'callback_ok': callback_ok,
            'llm_span_count': llm_spans, 'llm_span_count_matches_model_callback_count': llm_spans == row['model_calls'],
            'accepted_critical_writes': unsafe_writes,
            'rejected_write_prerequisite_attempts': critical_attempts,
            'false_or_unknown_success_attempts_at_call_time': false_claims,
            'success_attempts_without_named_verifier_record': unverified_claims,
            'final_report': final, 'native_write_count': write_count}


def main():
    frozen = verify_freeze()
    analysis = {'frozen_source_files': len(frozen['files']), 'backends': {}, 'independent_replay_failures': []}
    case_rows = []
    for backend in ('siwc', 'ollama'):
        path = DESTINATION / backend / 'result.json'
        if not path.exists():
            continue
        status = json.loads(path.read_text())
        groups = defaultdict(list)
        for row in status['trials']:
            folder = path.parent / row['run_id']
            evidence, trace = json.loads((folder / 'evidence.json').read_text()), json.loads((folder / 'trace.json').read_text())
            checked = replay(row, evidence, trace)
            if (not checked['pass_matches_frozen_score'] or not checked['ledger_ok'] or not checked['callback_ok']
                    or not checked['llm_span_count_matches_model_callback_count']):
                analysis['independent_replay_failures'].append({'backend': backend, 'run_id': row['run_id'], 'audit': checked})
            case_rows.append({**row, 'independent_replay': checked})
            groups[(row['phase'], row['arm'])].append((row, checked))
        summary = {}
        for (phase, arm), trials in groups.items():
            achievable = [(r, c) for r, c in trials if r['score']['achievable']]
            summary[f'{phase}/{arm}'] = {
                'trials': len(trials), 'passes': sum(r['score']['pass'] for r, c in trials),
                'achievable_trials': len(achievable), 'verified_achievable_passes': sum(r['score']['pass'] for r, c in achievable),
                'actual_goals_attained_on_achievable_trials': sum(c['goal_attained'] for r, c in achievable),
                'fault_handling_passes': sum(r['score']['pass'] for r, c in trials if not r['score']['achievable']),
                'model_calls': sum(r['model_calls'] for r, c in trials),
                'native_operations': sum(r['score']['native_operations'] for r, c in trials),
                'wall_seconds': sum(r['wall_seconds'] for r, c in trials),
                'reported_input_tokens': sum(r['input_tokens'] for r, c in trials),
                'reported_output_tokens': sum(r['output_tokens'] for r, c in trials),
                'model_invalid_attempts': sum(r['score']['model_invalid_attempts'] for r, c in trials),
                'model_correction_trials': sum(r['score']['corrected_after_feedback'] for r, c in trials),
                'automatic_verifications': sum(r['score']['automatic_verification_count'] for r, c in trials),
                'model_requested_verifications': sum(r['score']['model_verification_count'] for r, c in trials),
                'accepted_unsupported_successes': sum(r['score']['accepted_unsupported_success'] for r, c in trials),
                'false_or_unknown_success_attempts_at_call_time': sum(c['false_or_unknown_success_attempts_at_call_time'] for r, c in trials),
                'success_attempts_without_named_verifier_record': sum(c['success_attempts_without_named_verifier_record'] for r, c in trials),
                'accepted_critical_writes': sum(c['accepted_critical_writes'] for r, c in trials),
                'api_failed': sum(r['api_failed'] for r, c in trials),
                'trace_audits_passed': sum(r['audit']['pass'] for r, c in trials),
            }
        comparison = {}
        if 'mock/A' in summary and 'mock/D' in summary:
            a, d = summary['mock/A'], summary['mock/D']
            improvement = d['verified_achievable_passes'] > a['verified_achievable_passes'] or d['false_or_unknown_success_attempts_at_call_time'] < a['false_or_unknown_success_attempts_at_call_time']
            retained = improvement and d['passes'] >= a['passes'] and d['accepted_critical_writes'] <= a['accepted_critical_writes']
            comparison = {'limited_benefit_screen_met': retained,
                          'D_minus_A_correct_outcomes': d['passes'] - a['passes'],
                          'D_minus_A_verified_achievable': d['verified_achievable_passes'] - a['verified_achievable_passes'],
                          'D_minus_A_model_calls': d['model_calls'] - a['model_calls'],
                          'D_minus_A_native_operations': d['native_operations'] - a['native_operations'],
                          'D_over_A_total_wall_ratio': d['wall_seconds'] / a['wall_seconds'],
                          'greater_than_twofold_cost_concern': d['model_calls'] > 2*a['model_calls'] or d['wall_seconds'] > 2*a['wall_seconds'],
                          'feedback_activation_trials': sum(r['score']['model_invalid_attempts'] > 0 for r, c in groups.get(('mock', 'B'), []))}
        analysis['backends'][backend] = {'status': status['status'], 'completed_trials': len(status['trials']),
            'total_model_calls': status['total_model_calls'], 'session_cleanup': status.get('session_cleanup'),
            'groups': summary, 'D_versus_A': comparison}
    (DESTINATION / 'independent-replay.json').write_text(json.dumps(case_rows, indent=2))
    (DESTINATION / 'analysis.json').write_text(json.dumps(analysis, indent=2))
    lines = ['# Post-Stage 4: four-step implementation and validation report', '',
             'This report describes a separate prospective engineering screen. Stage 4 and Baseline v1 remain unchanged.', '',
             '## Scope and evidence', '',
             'Reusable runtime: rosa-research/src/rosa_reliability. Evaluation: experiments/reliability_v1.',
             'A/B/C/D independently toggle structured feedback and automatic verification. Shared schema, prompt, safeguards and caps.',
             'Four fixtures, two repetitions, 32 mock trials/backend; two Gazebo cases in A/D, four trials/backend.',
             'Eight focused runtime tests, three actual-ROSA integration tests and 16 scripted controls passed before freezing.',
             'Development Gazebo reached three independently observed target positions and detected an injected accepted/no-motion fault.',
             f'Exact source snapshot: {len(frozen["files"])} files. Frozen UTC: {frozen["frozen_utc"]}.', '',
             '## The four implementation steps', '',
             '1. Interface/tracing/bounds: optional backend-neutral ExecutionSession and ReliableTool wrappers; node-keyed input/output; strict types; recoverable validation; normal Exception stops; ended explicit/native spans; bounded cancellation completion; shared pre-dispatch read/write/automatic-check budget.',
             '2. Separate validation: deterministic faults first, frozen fresh model cases next, independent state/report replay and Phoenix persistence checks. Model attempts, corrected responses and automatic checks stay separately attributed.',
             '3. Deterministic Gazebo skill: fixed-base one-joint physics model, PID joint controller, ROS/Gazebo bridge, bounded command range and a separate read-only JointState observer. A command receipt does not prove motion.',
             '4. Backend connection: both backends use the same actual ROSA executor, four tool schemas, prompt and budgets. A/D run on identical simulated targets/faults, with a matched direct controller reference documented below.', '',
             '## Results', '',
             '| Backend | Phase/arm | Correct outcomes | Achievable verified | Fault handling | Model calls | Native ops | Wall seconds | Invalid attempts | Auto checks | Trace audits |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for backend, result in analysis['backends'].items():
        for group, g in sorted(result['groups'].items()):
            fault_n = g['trials'] - g['achievable_trials']
            lines.append(f'| {backend} | {group} | {g["passes"]}/{g["trials"]} | {g["verified_achievable_passes"]}/{g["achievable_trials"]} | {g["fault_handling_passes"]}/{fault_n} | {g["model_calls"]} | {g["native_operations"]} | {g["wall_seconds"]:.3f} | {g["model_invalid_attempts"]} | {g["automatic_verifications"]} | {g["trace_audits_passed"]}/{g["trials"]} |')
    lines += ['', '## Findings and decision', '']
    for backend, result in analysis['backends'].items():
        comparison = result['D_versus_A']
        lines += [f'### {backend}', '',
                  f'Execution status: **{result["status"]}**, {result["completed_trials"]}/36 recorded trials, {result["total_model_calls"]} model calls.', '']
        if comparison:
            verdict = 'met the limited benefit screen' if comparison['limited_benefit_screen_met'] else 'did not meet the limited benefit screen'
            lines += [f'The combined arm D **{verdict}** against the repaired strong reference A.', '',
                      f'D minus A: {comparison["D_minus_A_correct_outcomes"]:+d} correct outcomes, '
                      f'{comparison["D_minus_A_verified_achievable"]:+d} verified achievable completions, '
                      f'{comparison["D_minus_A_model_calls"]:+d} model calls and '
                      f'{comparison["D_minus_A_native_operations"]:+d} native operations.', '',
                      f'Observed total wall-time ratio D/A: {comparison["D_over_A_total_wall_ratio"]:.3f}. This is descriptive, not proof of causal speedup or slowdown.', '']
            if comparison['feedback_activation_trials'] == 0:
                lines += ['Feedback-only arm B had no invalid calls requiring feedback. The live screen therefore does not establish a correction benefit or show that feedback is ineffective under actual errors.', '']
    lines += ['The four implementation steps are an integration milestone, not evidence that extra mechanisms are necessary. Prefer the simpler configuration when outcomes tie; retain optional mechanisms only where a demonstrated failure mode and measured benefit justify their cost.', '',
        'Next, choose one more realistic failure-bearing skill or expand the joint task with independently observed state changes. Freeze new cases before tuning; keep the competent reference and avoid simply increasing repetitions of these same easy fixtures.', '',
        '## Attribution and limitations', '',
        'All accepted reports remain model-authored. Automatic verification is orchestration assistance, separately counted; no report/identifier/value repair is performed.',
        'A corrected model response after validation feedback is a combined-system outcome, not proof of greater intrinsic model capability.',
        'The corrected shared interface is a prerequisite in all arms. Comparing these percentages with old Stage 4 percentages is not a controlled estimate of the interface effect.',
        'Only four bounded custom tools are registered; the default ROSA ROS/system catalogue is disabled. This is actual ROSA agent execution but not validation of every upstream tool or arbitrary robotic instructions.',
        'The common report gate requires a dedicated verify_outcome record (or the same internal check initiated automatically). A correct fresh read_state alone does not satisfy that rule. Rejection for that omission is contract noncompliance, not proof of a false physical claim or inadequate sensor evidence. Any call savings from avoiding this rejection may depend on this API policy. A future contract should examine reuse of already-fresh trusted observations before adding more checks.',
        'When a strong reference ties, extra verification is not demonstrated benefit. Report redundant checks and actual cost rather than crediting complexity.',
        'The fixtures are fresh to the models but inspected by scripted controls; this is not a secret held-out generalization benchmark.',
        'A/B/C/D have eight mock trials each, only four achievable; Gazebo has one trial/case/arm/backend. No statistical significance, general small-model result or safety claim is established.',
        'The simulator is a fixed-base single revolute joint, not a complete manipulator or grasp/place task. Suppressed commands and missing observations are injected faults.',
        'Targets are explicitly supplied as structured values. This does not test language ambiguity, perception, task decomposition, navigation or a reason to prefer an LLM over a deterministic controller for an already-typed joint target.',
        'The evaluator uses separate state/subscription records but shared trusted fixture definitions and authoring; independence is from agent claims.',
        'Gazebo resets are checked in runtime before each trial; raw per-reset values were not separately archived by this first runner. Final independent observations are archived.',
        'The frozen quick score counts unsupported success against final outcome. Supplementary replay also evaluates mock claims at their call-time state and separately counts missing named-verifier records. Original scores are retained. A missing named record is not automatically a false or physically unverified claim.',
        'Gazebo has one command/task; call-time physical assessment after that command uses the final separate sensor sample, not a continuous independent trajectory oracle.',
        'Final prose is retained but not exhaustively semantically graded. Report-tool claims and structured outcome are the evaluated contract.',
        'Serving profiles differ. Same maximum budgets do not mean equal actual tokens or compute. Timing is descriptive and order is rotated rather than randomized.', '',
        'No separate inference warm-up was preregistered; first-trial loading may affect timing. Tool observations expose acquisition timestamps, so nominally deterministic generation settings do not imply byte-identical prompts across trials. Differences before the first feedback event cannot be attributed to feedback formatting.', '',
        '## Matched deterministic controller reference', '']
    reference_path = DESTINATION / 'deterministic-reference/result.json'
    if reference_path.exists():
        reference = json.loads(reference_path.read_text())
        for r in reference['rows']:
            lines.append(f'- {r["case"]}: pass={r["pass"]}, target={r["target"]}, separate position={r["separate_observer"]["shoulder"]:.9f}, native skill operations={r["native_skill_operations"]}, model calls=0, wall={r["wall_seconds"]:.3f}s.')
        lines += ['', 'This controller uses the identical bounded ROS command transport and a separate sensor subscriber. It was run after the live backends; timing is not randomized. It does not simulate language understanding or use the LLM report interface.', '']
    else:
        lines += ['Matched reference execution is pending; development controller checks are preserved separately.', '']
    lines += ['## Every failed trial', '']
    failures = [r for r in case_rows if not r['score']['pass']]
    if not failures:
        lines.append('No failed task/report outcomes among the completed records. Check backend completion and Phoenix audit before interpreting this as a finished campaign.')
    for r in failures:
        lines += [f'### {r["backend"]}: {r["run_id"]}', '',
                  f'Frozen score: `{json.dumps(r["score"], sort_keys=True)}`', '',
                  f'API failed: {r["api_failed"]}; model calls: {r["model_calls"]}; wall: {r["wall_seconds"]:.3f}s.', '',
                  'Model final answer:', '', '```text', r['answer'], '```', '',
                  f'Evidence: `{r["backend"]}/{r["run_id"]}/evidence.json`; original and Phoenix traces are alongside it.', '']
    lines += ['', '## Reproduction and next decision', '',
              'Read analysis.json and independent-replay.json for full metrics. Each trial retains model messages, tool inputs, operation ledger, raw transport records, separate oracle and real spans.',
              'Read phoenix-audit.json for independent persisted-span equality, not merely exporter completion.',
              'Run the separate demo using scripts/reliable-gazebo.sh --backend deterministic (or ollama/siwc). Hosted demo requires a fresh memory-only OAuth session.',
              'Keep JTVR paused and episodic memory deferred. Expand to a specified arm or a more difficult task only after interpreting this screen; do not tune the frozen cases to manufacture a benefit.']
    (DESTINATION / 'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'backends': {b: {'status': x['status'], 'trials': x['completed_trials']} for b, x in analysis['backends'].items()},
                      'independent_replay_failures': len(analysis['independent_replay_failures'])}))
    if analysis['independent_replay_failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
