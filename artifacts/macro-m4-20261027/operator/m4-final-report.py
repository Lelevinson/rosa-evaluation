"""Postprocess the frozen, completed M4 campaign; no inference or runtime changes."""
import hashlib
import json
from pathlib import Path
from statistics import median

workspace = Path(__file__).resolve().parents[1]
root = workspace / 'rosa-evaluation'
base = root / 'artifacts/macro-m4-20261027'
analysis = json.loads((base / 'analysis.json').read_text())
assert analysis['complete'] and not analysis['clarification_review_pending']
assert not analysis['observed_dispatch_violations']
checkpoints = {b: json.loads((base / b / 'checkpoint.json').read_text()) for b in ('siwc', 'ollama')}
freeze = json.loads((base / 'freeze.json').read_text())
for name, digest in freeze['files'].items():
    assert hashlib.sha256((workspace / name).read_bytes()).hexdigest() == digest
    assert hashlib.sha256((base / 'source' / name).read_bytes()).hexdigest() == digest
for b, checkpoint in checkpoints.items():
    assert checkpoint['status'] == 'COMPLETE' and len(checkpoint['trials']) == 40
    assert checkpoint['simulator_cleanup']['returncode'] == 0 and not checkpoint['cleanup_errors']
    assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in checkpoint['trials'])
    assert sum(r['inference']['calls'] for r in checkpoint['trials']) == checkpoint['campaign']['reserved_requests']
    assert all(r['inference']['usage_complete'] for r in checkpoint['trials'])

def percent(p, m):
    return 100 * (1 - m / p) if p else 0

def rows(b, c):
    return [r for r in checkpoints[b]['trials'] if r['condition'] == c]

def metric(b, c):
    return analysis['backends'][b]['conditions'][c]

labels = {'siwc': 'Sol', 'ollama': 'Qwen'}
lines = ['# M4 final results and research handoff', '', 'Date: **2026-10-27**. Branch: `member/martin`.', '',
    '## Verdict and project decision', '',
    '**M4 execution and review are complete, with mixed findings.** All 80 scheduled live trials have '
    'saved results and passing local/exact persisted-Phoenix trace audits. All eight required clarification '
    'reviews are recorded. No trials were replaced, extended or imputed. Completion of the campaign '
    'does not mean all tasks passed.', '',
    '**Sol passed the prospective macro engineering screen; Qwen did not.** Sol achieved20/20 '
    'in both conditions with44.1% fewer model requests. Qwen achieved15/20 with primitives and14/20 '
    'with the macro: the candidate has one additional observed primary failure and therefore fails '
    'the no-greater-failure screen despite lower cost. The complete two-backend evaluation does '
    'not support an unqualified reliability-preserving macro recommendation.', '',
    'Retain the small module as a documented engineering capability and the positive Sol result as '
    'bounded evidence. Do not make macro mode an unconditional cross-model default or claim that '
    'Qwen reliability improved. Proceed toward M5 consolidation/reporting with this limitation visible; '
    'no new experiment, prompt tuning, planner, JTVR, memory or physical robot deployment is launched '
    'by this report. The current benefit is ordinary orchestration/skill packaging, not a demonstrated '
    'novel tool-selection algorithm.', '',
    '## What was compared', '',
    'Ten prospective task families x two repetitions x two conditions x two backends =80 trials. '
    'Conditions are model-managed primitives and the simple bounded macro, within each backend. '
    'The same repaired ROSA prompt/interface, five public tools, catalogue, application permissions, '
    'report-by-observation contract, safeguards and independent outcome checks apply. The reference '
    'is not untouched upstream ROSA. Only routine execution ownership changes.', '',
    'The model selects a skill and classifies its outcome; Python handles the macro\'s bounded '
    'read/conditional-write/fresh-verification sequence. Movement goals are home, stage_left and '
    'park_right, all one six-joint capability. The distinct second capability is read-only readiness '
    'inspection. These are separate skill invocations, not a general multi-skill planner. Movement '
    'tasks allow both capability types; inspection/ambiguity tasks permit only inspection. Therefore '
    'the model still has meaningful selection/clarification decisions.', '',
    'Case/condition order is paired and counterbalanced; Sol runs first, Qwen second with serialized '
    'Gazebo access. Cases and scoring were authored by this project and frozen before inference, '
    'not independently designed by an external evaluator. Two repetitions of ten families are a '
    'small clustered sample, not80 independent tasks.', '',
    '## Full schedule: correctness and all-attempt resource use', '',
    '| Backend / condition | Primary pass /20 | Requests | Known input tokens | Known output tokens | Native ops | Invalid attempts | Wrong-goal accepted SUCCESS |',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
for b in labels:
    for c in ('primitives', 'macro'):
        m = metric(b, c)
        lines.append(f"| {labels[b]} / {c} | {m['primary_passes']}/20 | {m['model_requests']} | "
            f"{m['known_input_tokens']:,} | {m['known_output_tokens']:,} | {m['native_operations']} | "
            f"{m['invalid_attempts']} | {m['wrong_goal_accepted_successes']} |")
lines += ['', 'All250 model requests are accounted for:106 Sol and144 Qwen, below323/backend '
    'and646 combined. There were no infrastructure retries/recovered trials, no incomplete-usage '
    'trial records, no censored/unstarted cells, no task/backend deadline stops and no OAuth renewal '
    'or quota interruption. Primary and completion-including-recovery counts are identical.', '',
    'Unsupported selected-evidence SUCCESS attempts and actual dispatch violations were zero. '
    '**This does not mean all success claims answered the user:** Qwen accepted two wrong-goal '
    'successes in primitives and three in macro mode. Four were ambiguous requests answered with '
    'readiness; the fifth was a requested partial-movement case answered with readiness. The '
    'report validator grounds the selected skill, not unrestricted natural-language intent.', '',
    '## How quick were the models?', '',
    '| Backend / condition | Total task seconds | Mean seconds/task | Median seconds/task |',
    '|---|---:|---:|---:|']
for b in labels:
    for c in ('primitives', 'macro'):
        times = [r['wall_seconds'] for r in rows(b, c)]
        lines.append(f'| {labels[b]} / {c} | {sum(times):,.2f} | {sum(times)/len(times):.2f} | {median(times):.2f} |')
lines += ['', 'Task wall time covers the model/tool loop, including waits, corrections and bounded '
    'recovery. It excludes simulator initialization/reset, outside-task independent scoring '
    'observations and persisted trace auditing. It is not pure model-generation time.', '',
    '| Backend | Both conditions: task minutes | Closed backend minutes | Non-task overhead minutes |',
    '|---|---:|---:|---:|']
for b in labels:
    task = sum(r['wall_seconds'] for r in checkpoints[b]['trials'])
    total = checkpoints[b]['total_elapsed_seconds']
    lines.append(f'| {labels[b]} | {task/60:.2f} | {total/60:.2f} | {(total-task)/60:.2f} |')
lines += ['', 'Backend elapsed time includes setup/reset/independent checks/audit and cleanup, '
    'but not waiting for the other backend to finish. The two backends used different compute, '
    'tokenization and sampling controls. These observed times describe this laptop/service setup; '
    'they do not establish an intrinsic hardware-independent speed ranking. Cold/warm model state '
    'and host activity were not randomized across backend order. No dollar/energy cost or pure '
    'generation tokens/second was measured.', '',
    '## Efficiency reductions: all attempts and matched successful pairs', '',
    'Positive reduction means the macro used less; a negative native reduction means more native work.', '',
    '| Backend | All-attempt request reduction | Known input reduction | Known output reduction | Task-time reduction | Native reduction |',
    '|---|---:|---:|---:|---:|---:|']
for b in labels:
    p, m = metric(b, 'primitives'), metric(b, 'macro')
    values = [percent(p[k], m[k]) for k in ('model_requests', 'known_input_tokens', 'known_output_tokens', 'task_wall_seconds', 'native_operations')]
    lines.append('| ' + labels[b] + ' | ' + ' | '.join(f'{v:+.1f}%' for v in values) + ' |')
lines += ['', 'All-attempt costs include failed tasks. Qwen\'s savings accompany lower primary '
    'correctness; a missed movement can avoid work and appear efficient. Accordingly, paired '
    'successful-task accounting is also shown; neither view replaces the other.', '',
    '| Backend | Both-pass pairs /20 | Requests primitives → macro | Call reduction | Native primitives → macro | Native reduction | Task seconds primitives → macro | Time reduction |',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
for b in labels:
    record = analysis['backends'][b]
    paired = {}
    for r in checkpoints[b]['trials']:
        paired.setdefault((r['case'], r['repetition']), {})[r['condition']] = r
    both = [pair for pair in paired.values() if all(r['primary_pass'] for r in pair.values())]
    times = {c: sum(p[c]['wall_seconds'] for p in both) for c in ('primitives', 'macro')}
    calls, native = record['matched_calls'], record['matched_native_operations']
    lines.append(f"| {labels[b]} | {record['matched_primary_success_pairs']}/20 | "
        f"{calls['primitives']} → {calls['macro']} | {100*record['matched_call_reduction']:.1f}% | "
        f"{native['primitives']} → {native['macro']} | {percent(native['primitives'],native['macro']):+.1f}% | "
        f"{times['primitives']:,.2f} → {times['macro']:,.2f} | {percent(times['primitives'],times['macro']):.1f}% |")
lines += ['', 'Sol has20 jointly successful pairs. Qwen has13: one macro-only success '
    '(constrained selection r2), two primitive-only successes (partial execution r1/r2), '
    'four pairs where both fail, and13 where both pass. These results are descriptive; '
    'no statistical noninferiority, equivalence or broad generalization claim is made.', '',
    '## Per-family completion and fault exercise', '',
    '| Family | Sol primitives /2 | Sol macro /2 | Qwen primitives /2 | Qwen macro /2 |',
    '|---|---:|---:|---:|---:|']
for case in dict.fromkeys(r['case'] for r in checkpoints['siwc']['trials']):
    scores = [sum(r['primary_pass'] for r in rows(b,c) if r['case']==case) for b in labels for c in ('primitives','macro')]
    lines.append('| ' + case + ' | ' + ' | '.join(f'{v}/2' for v in scores) + ' |')
lines += ['', 'Sol exercised every required injected fault. Qwen\'s primitive partial-command '
    'cases both executed the injected partial wrist motion and correctly reported failure. Its '
    'macro partial-command cases both selected inspection instead: zero movement was dispatched '
    'and the partial-execution fault was not exercised. All four Qwen missing-movement-prerequisite '
    'cases also selected inspection; they did not exercise the intended motion observation timeout '
    'or complete the requested UNKNOWN outcome. These are goal-selection/fault-coverage failures, '
    'not evidence that the candidate handled the injected motion faults.', '',
    'Dispatch accounting: Sol had six movement dispatch attempts per condition (four published, '
    'two deliberately suppressed ineffective commands; two of the publications were injected '
    'partial commands). Qwen primitives had five (three published including two partial; two '
    'suppressed), macro four (two published, no partial; two suppressed). Already-satisfied cases '
    'correctly avoided commands. Inspection tasks never published trajectories.', '',
    '## Qwen failure analysis: all11 failed tasks retained', '',
    '| Trial | Calls | Seconds | Saved termination/outcome |', '|---|---:|---:|---|']
for r in checkpoints['ollama']['trials']:
    if r['primary_pass']: continue
    answer = r['answer']
    outcome = ('Accepted truthful readiness SUCCESS for wrong/ambiguous user goal' if r['score']['accepted_success_wrong_user_goal']
               else answer.replace('An error occurred: ', ''))
    lines.append(f"| {r['job']['id']} | {r['inference']['calls']} | {r['wall_seconds']:.2f} | {outcome} |")
lines += ['', 'Every failed Qwen task selected `ur5e.inspect_readiness`. For the seven failed '
    'non-ambiguous movement cases this was the wrong capability; the other four required '
    'clarification rather than any selection. Five failures later ended with a length-truncated '
    'response; one ended with validation-retry exhaustion. Truncation is a recorded terminal '
    'condition, not proof that raising output allowance would fix the earlier selection mistake.', '',
    'A task-level `error_type=null` is not proof of no failure: ROSA can return a safe error string '
    'that independent scoring still marks failed. Rejected writes against inspection were blocked '
    'before dispatch; attempted reselection was rejected because the one-skill invocation was '
    'already committed. That prevents silent policy changes/replay but can lock in a bad initial '
    'selection. This is a documented architectural trade-off, not a defect to retune mid-study.', '',
    '## Required clarification review', '',
    'All four Sol transcripts passed the frozen rubric. All four Qwen transcripts failed: '
    'Qwen selected readiness, acquired two sources and submitted accepted SUCCESS instead of '
    'asking for clarification before any selection/acquisition/report. Zero movement did not '
    'satisfy the rubric. The readings were factually grounded; the intended task was unresolved.', '',
    'Reviews are Codex operator adjudication, **not independent human adjudication**. Each record '
    'has a reason and SHA256 of the saved answer, validated by the unchanged frozen analyzer. '
    'Automated primary scores did not change after the review. The original four-review '
    'execution checkpoint and its ZIP remain preserved separately.', '',
    '## Engineering screen, bounds and observability', '',
    'The prospective screen required all20 pairs, all quality audits, no dispatch violations, '
    'no greater number of primary failed tasks, at least25% fewer calls on both-pass pairs, '
    'and at most25% extra native operations on those pairs. Sol passes all conditions. Qwen '
    'passes the audit/bounds/cost components but fails the correctness condition (six macro '
    'failures versus five primitive failures). The screen is a development criterion, not '
    'a statistical reliability guarantee.', '',
    'All80 live local audits and exact persisted-Phoenix audits pass:1,434 Sol spans and1,856 '
    'Qwen spans,3,290 total. The20 deterministic controls add202 spans;100 audited tasks '
    'and3,492 spans including controls. No missing/reconciled-away spans, unsafe dispatches '
    'or robot-command replay were observed. Separate independent observers share simulator '
    'interfaces; independence refers to evaluator state/transport, not a different physical sensor.', '',
    'Maximum charged calls/task: Sol5, Qwen8; maximum known generated tokens/task:188 and2,048; '
    'maximum native operations/task:3 and6; maximum task time32.03 and286.84 seconds. Limits '
    'remained8 charged calls,2,048 observed output,10 native/16 tool attempts/3 permitted corrections, '
    '360 seconds and at most one movement dispatch. The rejection that exhausts a correction '
    'allowance is still recorded; validation-rejection count is not an extra permitted retry.', '',
    'Both simulators closed with returncode0 and no cleanup errors; local model unload succeeded '
    'as recorded. The supervisor\'s nullable child exit_code fields were not treated as evidence '
    'of zero exits. Backend checkpoints/audits/cleanup are the outcome evidence.', '',
    '## Reproducibility, authorization and provenance', '',
    'Frozen runtime: research `c0c61a0`, evaluation `4412f05`;62 source/config files. Freeze '
    'SHA256: `2da35ca96e0315e0b0dff95de2958e33880b1c7c4812af06b76e75b6a51e2400`. '
    'All working and archived frozen inputs still match. Documentation/closeout utilities added '
    'after freezing are postprocessing, not experimental inputs. Earlier M2/M3 evidence382-entry '
    'verification and old campaign archives remain unchanged.', '',
    'Qwen: `qwen3.5:9b` Q4_K_M, digest '
    '`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`, '
    'Ollama0.40.6, num_ctx8192, up to1024 generated tokens/call within the remaining allowance, '
    'temperature0/seed42/mmap true, no reasoning/stream/cache. Sol: `gpt-6.1-sol` through existing '
    'ChatSiwc with provider defaults and observed-output gate, not an identical provider generation '
    'cap. ROS2 Jazzy/Gazebo Harmonic/UR5e controllers remain unchanged; applicable research and '
    'Phoenix uv locks are archived, with no evaluation-root Python project.', '',
    'The opted-in remembered grant renewed once for the hosted batch, remained encrypted, and '
    'cleared in-memory credentials on exit. No new consent was bypassed. No credentials are '
    'included in the package. This successful batch is not an overnight endurance guarantee.', '',
    'The initial Windows supervisor left `EXECUTION_FINISHED_REVIEW_REQUIRED` as a historical '
    'saved phase. Final closure is recorded in `closeout.json`; it does not rewrite that original '
    'operator record. The pre-review analysis/report/review/manifest are retained under '
    '`review-history/execution-checkpoint/` and in the original execution ZIP. The final package '
    'has a separate name and manifest; it does not replace the execution archive.', '',
    '## Recommended next work: M5 consolidation', '',
    '1. Consolidate the reusable component, runnable demonstration, limitations and reproducibility '
    'instructions using this completed positive/negative evidence. No new candidate architecture is needed.',
    '2. Present the Sol efficiency result and Qwen failed retention screen side by side. Keep '
    'macro mode optional and task/permission bounded; do not promise reliability across local models.',
    '3. Ask teammates/reviewers to examine intent selection, truthful wrong-goal reports and '
    'the one-skill commitment trade-off before proposing any separate future repair or experiment.',
    '4. Resolve prior-art/novelty and practical portability claims in the final write-up. A useful '
    'engineering module can be a valid undergraduate deliverable without a new algorithm.',
    '5. Keep teammate-backend migration, episodic memory, full JTVR and hardware deferred. '
    'No physical-robot safety, collision-free planning, gripper/perception or general autonomy claim follows.', '',
    '## Evidence to share with another chatbot', '',
    'Start with this report, `analysis.json`, `clarification-review.json`, the efficiency/timing '
    'report and the living project README. Inspect failed trials and per-task raw inference/trace '
    'records when challenging conclusions. Use `final-archive-manifest.json` for the final ZIP; '
    'historical manifests belong to their separately labeled checkpoint generations.', '',
    'The final evidence ZIP/sidecar verification will be recorded alongside the archive. Hash '
    'integrity establishes byte identity, not scientific validity. Commits are local unless '
    'a separate push is actually performed; no remote publication is claimed.']
text = '\n'.join(lines) + '\n'
# Improve prose spacing without altering code literals, exact paths or identifiers.
import re
text = re.sub(r'\b(all|and|with|than|at least|at most|Sol|Qwen|of|for|versus|allowance|task|tokens|trials|cases|requests|spans|total|audits|native|seconds|Ollama|num_ctx|temperature|seed)(?=\d)', r'\1 ', text)
text = text.replace('Qwen 3.5', 'Qwen3.5')
(base / 'FINAL_REPORT_FOR_CHATGPT.md').write_text(text, encoding='utf-8')
closeout = {
    'date': '2026-10-27', 'status': 'CLOSED_MIXED_FINDINGS', 'study_complete': True,
    'scheduled_trials': 80, 'recorded_trials': 80, 'audited_trials': 80,
    'clarification_reviews': 8, 'sol_reviews_passed': 4, 'qwen_reviews_failed': 4,
    'sol_engineering_screen_pass': analysis['backends']['siwc']['engineering_screen_pass'],
    'qwen_engineering_screen_pass': analysis['backends']['ollama']['engineering_screen_pass'],
    'overall_two_backend_retention': False,
    'decision': 'Retain bounded module as optional engineering capability; Sol positive, Qwen failed '
                'reliability-preserving retention. No unqualified cross-model recommendation.',
    'next_action': 'M5 consolidation/write-up using the mixed findings; no new experiment or architecture launched.',
    'final_report': 'artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md',
    'inference_requests': 250, 'live_spans': 3290, 'control_spans': 202,
    'frozen_source_files_verified': 62,
}
(base / 'closeout.json').write_text(json.dumps(closeout, indent=2) + '\n')
print(json.dumps(closeout, indent=2))
