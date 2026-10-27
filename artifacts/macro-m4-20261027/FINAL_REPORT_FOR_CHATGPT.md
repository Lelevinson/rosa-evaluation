# M4 final results and research handoff

Date: **2026-10-27**. Branch: `member/martin`.

## Verdict and project decision

**M4 execution and review are complete, with mixed findings.** All 80 scheduled live trials have saved results and passing local/exact persisted-Phoenix trace audits. All eight required clarification reviews are recorded. No trials were replaced, extended or imputed. Completion of the campaign does not mean all tasks passed.

**Sol passed the prospective macro engineering screen; Qwen did not.** Sol achieved20/20 in both conditions with 44.1% fewer model requests. Qwen achieved15/20 with primitives and 14/20 with the macro: the candidate has one additional observed primary failure and therefore fails the no-greater-failure screen despite lower cost. The complete two-backend evaluation does not support an unqualified reliability-preserving macro recommendation.

Retain the small module as a documented engineering capability and the positive Sol result as bounded evidence. Do not make macro mode an unconditional cross-model default or claim that Qwen reliability improved. Proceed toward M5 consolidation/reporting with this limitation visible; no new experiment, prompt tuning, planner, JTVR, memory or physical robot deployment is launched by this report. The current benefit is ordinary orchestration/skill packaging, not a demonstrated novel tool-selection algorithm.

## What was compared

Ten prospective task families x two repetitions x two conditions x two backends =80 trials. Conditions are model-managed primitives and the simple bounded macro, within each backend. The same repaired ROSA prompt/interface, five public tools, catalogue, application permissions, report-by-observation contract, safeguards and independent outcome checks apply. The reference is not untouched upstream ROSA. Only routine execution ownership changes.

The model selects a skill and classifies its outcome; Python handles the macro's bounded read/conditional-write/fresh-verification sequence. Movement goals are home, stage_left and park_right, all one six-joint capability. The distinct second capability is read-only readiness inspection. These are separate skill invocations, not a general multi-skill planner. Movement tasks allow both capability types; inspection/ambiguity tasks permit only inspection. Therefore the model still has meaningful selection/clarification decisions.

Case/condition order is paired and counterbalanced; Sol runs first, Qwen second with serialized Gazebo access. Cases and scoring were authored by this project and frozen before inference, not independently designed by an external evaluator. Two repetitions of ten families are a small clustered sample, not80 independent tasks.

## Full schedule: correctness and all-attempt resource use

| Backend / condition | Primary pass /20 | Requests | Known input tokens | Known output tokens | Native ops | Invalid attempts | Wrong-goal accepted SUCCESS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sol / primitives | 20/20 | 68 | 95,333 | 2,221 | 38 | 0 | 0 |
| Sol / macro | 20/20 | 38 | 48,754 | 1,145 | 40 | 0 | 0 |
| Qwen / primitives | 15/20 | 91 | 207,958 | 19,445 | 50 | 15 | 2 |
| Qwen / macro | 14/20 | 53 | 105,779 | 12,519 | 48 | 12 | 3 |

All250 model requests are accounted for:106 Sol and 144 Qwen, below323/backend and 646 combined. There were no infrastructure retries/recovered trials, no incomplete-usage trial records, no censored/unstarted cells, no task/backend deadline stops and no OAuth renewal or quota interruption. Primary and completion-including-recovery counts are identical.

Unsupported selected-evidence SUCCESS attempts and actual dispatch violations were zero. **This does not mean all success claims answered the user:** Qwen accepted two wrong-goal successes in primitives and three in macro mode. Four were ambiguous requests answered with readiness; the fifth was a requested partial-movement case answered with readiness. The report validator grounds the selected skill, not unrestricted natural-language intent.

## How quick were the models?

| Backend / condition | Total task seconds | Mean seconds/task | Median seconds/task |
|---|---:|---:|---:|
| Sol / primitives | 328.36 | 16.42 | 13.18 |
| Sol / macro | 194.58 | 9.73 | 8.57 |
| Qwen / primitives | 2,669.72 | 133.49 | 117.59 |
| Qwen / macro | 1,703.63 | 85.18 | 46.53 |

Task wall time covers the model/tool loop, including waits, corrections and bounded recovery. It excludes simulator initialization/reset, outside-task independent scoring observations and persisted trace auditing. It is not pure model-generation time.

| Backend | Both conditions: task minutes | Closed backend minutes | Non-task overhead minutes |
|---|---:|---:|---:|
| Sol | 8.72 | 17.68 | 8.96 |
| Qwen | 72.89 | 81.97 | 9.08 |

Backend elapsed time includes setup/reset/independent checks/audit and cleanup, but not waiting for the other backend to finish. The two backends used different compute, tokenization and sampling controls. These observed times describe this laptop/service setup; they do not establish an intrinsic hardware-independent speed ranking. Cold/warm model state and host activity were not randomized across backend order. No dollar/energy cost or pure generation tokens/second was measured.

## Efficiency reductions: all attempts and matched successful pairs

Positive reduction means the macro used less; a negative native reduction means more native work.

| Backend | All-attempt request reduction | Known input reduction | Known output reduction | Task-time reduction | Native reduction |
|---|---:|---:|---:|---:|---:|
| Sol | +44.1% | +48.9% | +48.4% | +40.7% | -5.3% |
| Qwen | +41.8% | +49.1% | +35.6% | +36.2% | +4.0% |

All-attempt costs include failed tasks. Qwen's savings accompany lower primary correctness; a missed movement can avoid work and appear efficient. Accordingly, paired successful-task accounting is also shown; neither view replaces the other.

| Backend | Both-pass pairs /20 | Requests primitives → macro | Call reduction | Native primitives → macro | Native reduction | Task seconds primitives → macro | Time reduction |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sol | 20/20 | 68 → 38 | 44.1% | 38 → 40 | -5.3% | 328.36 → 194.58 | 40.7% |
| Qwen | 13/20 | 53 → 28 | 47.2% | 31 → 29 | +6.5% | 1,417.23 → 696.76 | 50.8% |

Sol has20 jointly successful pairs. Qwen has13: one macro-only success (constrained selection r2), two primitive-only successes (partial execution r1/r2), four pairs where both fail, and 13 where both pass. These results are descriptive; no statistical noninferiority, equivalence or broad generalization claim is made.

## Per-family completion and fault exercise

| Family | Sol primitives /2 | Sol macro /2 | Qwen primitives /2 | Qwen macro /2 |
|---|---:|---:|---:|---:|
| move_constrained | 2/2 | 2/2 | 1/2 | 2/2 |
| already_satisfied | 2/2 | 2/2 | 2/2 | 2/2 |
| ineffective_command | 2/2 | 2/2 | 2/2 | 2/2 |
| partial_command | 2/2 | 2/2 | 2/2 | 0/2 |
| missing_prerequisite | 2/2 | 2/2 | 0/2 | 0/2 |
| inspect_healthy | 2/2 | 2/2 | 2/2 | 2/2 |
| inspect_inactive | 2/2 | 2/2 | 2/2 | 2/2 |
| inspect_missing_controllers | 2/2 | 2/2 | 2/2 | 2/2 |
| inspect_missing_joint | 2/2 | 2/2 | 2/2 | 2/2 |
| ambiguous_goal | 2/2 | 2/2 | 0/2 | 0/2 |

Sol exercised every required injected fault. Qwen's primitive partial-command cases both executed the injected partial wrist motion and correctly reported failure. Its macro partial-command cases both selected inspection instead: zero movement was dispatched and the partial-execution fault was not exercised. All four Qwen missing-movement-prerequisite cases also selected inspection; they did not exercise the intended motion observation timeout or complete the requested UNKNOWN outcome. These are goal-selection/fault-coverage failures, not evidence that the candidate handled the injected motion faults.

Dispatch accounting: Sol had six movement dispatch attempts per condition (four published, two deliberately suppressed ineffective commands; two of the publications were injected partial commands). Qwen primitives had five (three published including two partial; two suppressed), macro four (two published, no partial; two suppressed). Already-satisfied cases correctly avoided commands. Inspection tasks never published trajectories.

## Qwen failure analysis: all 11 failed tasks retained

| Trial | Calls | Seconds | Saved termination/outcome |
|---|---:|---:|---|
| 07-partial_command-r1-macro | 4 | 182.26 | Accepted truthful readiness SUCCESS for wrong/ambiguous user goal |
| 09-missing_prerequisite-r1-primitives | 6 | 286.84 | truncated_response_no_tool_dispatch_no_automatic_retry |
| 10-missing_prerequisite-r1-macro | 5 | 278.21 | truncated_response_no_tool_dispatch_no_automatic_retry |
| 19-ambiguous_goal-r1-macro | 2 | 34.25 | Accepted truthful readiness SUCCESS for wrong/ambiguous user goal |
| 20-ambiguous_goal-r1-primitives | 3 | 52.88 | Accepted truthful readiness SUCCESS for wrong/ambiguous user goal |
| 29-ambiguous_goal-r2-macro | 2 | 34.92 | Accepted truthful readiness SUCCESS for wrong/ambiguous user goal |
| 30-ambiguous_goal-r2-primitives | 3 | 52.46 | Accepted truthful readiness SUCCESS for wrong/ambiguous user goal |
| 31-move_constrained-r2-primitives | 5 | 221.69 | truncated_response_no_tool_dispatch_no_automatic_retry |
| 37-partial_command-r2-macro | 3 | 164.42 | truncated_response_no_tool_dispatch_no_automatic_retry |
| 39-missing_prerequisite-r2-primitives | 6 | 269.36 | truncated_response_no_tool_dispatch_no_automatic_retry |
| 40-missing_prerequisite-r2-macro | 7 | 228.40 | validation_retry_budget_exhausted |

Every failed Qwen task selected `ur5e.inspect_readiness`. For the seven failed non-ambiguous movement cases this was the wrong capability; the other four required clarification rather than any selection. Five failures later ended with a length-truncated response; one ended with validation-retry exhaustion. Truncation is a recorded terminal condition, not proof that raising output allowance would fix the earlier selection mistake.

A task-level `error_type=null` is not proof of no failure: ROSA can return a safe error string that independent scoring still marks failed. Rejected writes against inspection were blocked before dispatch; attempted reselection was rejected because the one-skill invocation was already committed. That prevents silent policy changes/replay but can lock in a bad initial selection. This is a documented architectural trade-off, not a defect to retune mid-study.

## Required clarification review

All four Sol transcripts passed the frozen rubric. All four Qwen transcripts failed: Qwen selected readiness, acquired two sources and submitted accepted SUCCESS instead of asking for clarification before any selection/acquisition/report. Zero movement did not satisfy the rubric. The readings were factually grounded; the intended task was unresolved.

Reviews are Codex operator adjudication, **not independent human adjudication**. Each record has a reason and SHA256 of the saved answer, validated by the unchanged frozen analyzer. Automated primary scores did not change after the review. The original four-review execution checkpoint and its ZIP remain preserved separately.

## Engineering screen, bounds and observability

The prospective screen required all 20 pairs, all quality audits, no dispatch violations, no greater number of primary failed tasks, at least 25% fewer calls on both-pass pairs, and at most 25% extra native operations on those pairs. Sol passes all conditions. Qwen passes the audit/bounds/cost components but fails the correctness condition (six macro failures versus five primitive failures). The screen is a development criterion, not a statistical reliability guarantee.

All80 live local audits and exact persisted-Phoenix audits pass:1,434 Sol spans and 1,856 Qwen spans,3,290 total. The20 deterministic controls add202 spans;100 audited tasks and 3,492 spans including controls. No missing/reconciled-away spans, unsafe dispatches or robot-command replay were observed. Separate independent observers share simulator interfaces; independence refers to evaluator state/transport, not a different physical sensor.

Maximum charged calls/task: Sol 5, Qwen 8; maximum known generated tokens/task:188 and 2,048; maximum native operations/task:3 and 6; maximum task time32.03 and 286.84 seconds. Limits remained8 charged calls,2,048 observed output,10 native/16 tool attempts/3 permitted corrections, 360 seconds and at most one movement dispatch. The rejection that exhausts a correction allowance is still recorded; validation-rejection count is not an extra permitted retry.

Both simulators closed with returncode0 and no cleanup errors; local model unload succeeded as recorded. The supervisor's nullable child exit_code fields were not treated as evidence of zero exits. Backend checkpoints/audits/cleanup are the outcome evidence.

## Reproducibility, authorization and provenance

Frozen runtime: research `c0c61a0`, evaluation `4412f05`;62 source/config files. Freeze SHA256: `2da35ca96e0315e0b0dff95de2958e33880b1c7c4812af06b76e75b6a51e2400`. All working and archived frozen inputs still match. Documentation/closeout utilities added after freezing are postprocessing, not experimental inputs. Earlier M2/M3 evidence382-entry verification and old campaign archives remain unchanged.

Qwen: `qwen3.5:9b` Q4_K_M, digest `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`, Ollama 0.40.6, num_ctx 8192, up to1024 generated tokens/call within the remaining allowance, temperature 0/seed 42/mmap true, no reasoning/stream/cache. Sol: `gpt-6.1-sol` through existing ChatSiwc with provider defaults and observed-output gate, not an identical provider generation cap. ROS2 Jazzy/Gazebo Harmonic/UR5e controllers remain unchanged; applicable research and Phoenix uv locks are archived, with no evaluation-root Python project.

The opted-in remembered grant renewed once for the hosted batch, remained encrypted, and cleared in-memory credentials on exit. No new consent was bypassed. No credentials are included in the package. This successful batch is not an overnight endurance guarantee.

The initial Windows supervisor left `EXECUTION_FINISHED_REVIEW_REQUIRED` as a historical saved phase. Final closure is recorded in `closeout.json`; it does not rewrite that original operator record. The pre-review analysis/report/review/manifest are retained under `review-history/execution-checkpoint/` and in the original execution ZIP. The final package has a separate name and manifest; it does not replace the execution archive.

## Recommended next work: M5 consolidation

1. Consolidate the reusable component, runnable demonstration, limitations and reproducibility instructions using this completed positive/negative evidence. No new candidate architecture is needed.
2. Present the Sol efficiency result and Qwen failed retention screen side by side. Keep macro mode optional and task/permission bounded; do not promise reliability across local models.
3. Ask teammates/reviewers to examine intent selection, truthful wrong-goal reports and the one-skill commitment trade-off before proposing any separate future repair or experiment.
4. Resolve prior-art/novelty and practical portability claims in the final write-up. A useful engineering module can be a valid undergraduate deliverable without a new algorithm.
5. Keep teammate-backend migration, episodic memory, full JTVR and hardware deferred. No physical-robot safety, collision-free planning, gripper/perception or general autonomy claim follows.

## Evidence to share with another chatbot

Start with this report, `analysis.json`, `clarification-review.json`, the efficiency/timing report and the living project README. Inspect failed trials and per-task raw inference/trace records when challenging conclusions. Use `final-archive-manifest.json` for the final ZIP; historical manifests belong to their separately labeled checkpoint generations.

The final evidence ZIP/sidecar verification will be recorded alongside the archive. Hash integrity establishes byte identity, not scientific validity. Commits are local unless a separate push is actually performed; no remote publication is claimed.
