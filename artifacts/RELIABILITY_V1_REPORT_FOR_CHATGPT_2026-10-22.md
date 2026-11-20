# Reliability v1: complete review for ChatGPT

This consolidated review adds explicit rejected-call attribution to the sealed primary report. It does not alter the original trials, scores, analysis or evidence ZIP.

## Read this qualification first

**Both backends passed 36/36 final combined-system outcomes, but Qwen did not produce error-free model behavior.**

| Backend | Final combined passes | Trials with no rejected model calls | Rejected model calls | UNKNOWN-state write attempts | Executed UNKNOWN-state writes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hosted | 36/36 | 36/36 | 0 | 0 | 0 |
| Qwen | 36/36 | 27/36 | 9 | 3 | 0 |

The nine Qwen rejections occurred in nine separate trials: three attempted writes despite unavailable state, plus six reports lacking the dedicated verifier record. The shared guard blocked every UNKNOWN-state write before native dispatch. All nine trials subsequently reached the required final report. No schema/type validation error occurred in the live trials.

The six report rejections are contract issues, not six false physical claims. In particular, a correct fresh read alone does not satisfy this implementation's named verify_outcome rule. The three write attempts are a distinct decision defect; successful guard enforcement does not erase them.

The common prerequisite guard exists in every arm, including A. These observations demonstrate that the tested guard rejected these requests, not that D caused better safety than A. Trials with no rejected calls can still include automatic verification; that column is not an intrinsic model-only score.

## Every rejected call

| Backend/trial | Model request | Rejection | Final outcome |
| --- | --- | --- | --- |
| ollama/007-mock-postwrite_freshness-A-r0 | `submit_report {"observed_values": {"/bench_east": {"position": 0.31}, "/bench_west": {"position": -0.24}}, "status": "SUCCESS"}` | fresh_verification_required | SUCCESS; combined pass |
| ollama/012-mock-unavailable_observation-D-r0 | `write_state {"node_name": "/bench_west", "values": {"position": 0.19}}` | write_prerequisite_rejected | UNKNOWN; combined pass |
| ollama/013-mock-unavailable_observation-A-r0 | `submit_report {"observed_values": {"/bench_west": {"position": null}}, "status": "UNKNOWN"}` | fresh_verification_required | UNKNOWN; combined pass |
| ollama/014-mock-unavailable_observation-B-r0 | `submit_report {"observed_values": {"/bench_west": {"position": null}}, "status": "UNKNOWN"}` | fresh_verification_required | UNKNOWN; combined pass |
| ollama/015-mock-unavailable_observation-C-r0 | `submit_report {"observed_values": {"/bench_west": {"position": null}}, "status": "UNKNOWN"}` | fresh_verification_required | UNKNOWN; combined pass |
| ollama/028-mock-unavailable_observation-A-r1 | `write_state {"node_name": "/bench_west", "values": {"position": 0.19}}` | write_prerequisite_rejected | UNKNOWN; combined pass |
| ollama/029-mock-unavailable_observation-B-r1 | `submit_report {"observed_values": {"/bench_west": {"position": null}}, "status": "UNKNOWN"}` | fresh_verification_required | UNKNOWN; combined pass |
| ollama/030-mock-unavailable_observation-C-r1 | `write_state {"node_name": "/bench_west", "values": {"position": 0.19}}` | write_prerequisite_rejected | UNKNOWN; combined pass |
| ollama/031-mock-unavailable_observation-D-r1 | `submit_report {"observed_values": {"/bench_west": {"position": null}}, "status": "UNKNOWN"}` | fresh_verification_required | UNKNOWN; combined pass |

## Performance interpretation

The reference and combined arms tie on completion. Local mock A used 43 model calls and D used 38, with 34 native operations each. Local Gazebo A used 12 model calls and eight native operations; D used nine calls and seven operations. These are small exploratory comparisons, not a demonstrated general speedup. Timing, task order, visible acquisition timestamps, redundant reads and the named-verifier policy limit causal interpretation.

Hosted mock A and D each used 36 model calls, while D used 34 native operations versus A's 28. Hosted Gazebo A and D each used ten model calls, while D used eight native operations versus A's six. Automatic checking therefore added work without completion improvement for that tested backend.

This completes the requested integration milestone for a single-joint fixture. It does not establish full-manipulator readiness, safe unguarded Qwen control, broad generalization or algorithmic novelty.

## Evidence preservation

The sealed base ZIP SHA-256 remains `2bd6963cd27e01df9e86df9a7f9fbd1d84dba03e52c3fb85d42d86ea717e51a5`; all 400 manifest members were independently reverified. The new JSON enumerates every rejection without changing a historical score.

The complete review bundle contains this consolidated report, the addendum JSON, its generation source, a manifest, and the unchanged original evidence ZIP. Unzip the original evidence ZIP to inspect all raw trials and source snapshots.

---

# Original sealed report (unchanged)

# Post-Stage 4: four-step implementation and validation report

This report describes a separate prospective engineering screen. Stage 4 and Baseline v1 remain unchanged.

## Scope and evidence

Reusable runtime: rosa-research/src/rosa_reliability. Evaluation: experiments/reliability_v1.
A/B/C/D independently toggle structured feedback and automatic verification. Shared schema, prompt, safeguards and caps.
Four fixtures, two repetitions, 32 mock trials/backend; two Gazebo cases in A/D, four trials/backend.
Eight focused runtime tests, three actual-ROSA integration tests and 16 scripted controls passed before freezing.
Development Gazebo reached three independently observed target positions and detected an injected accepted/no-motion fault.
Exact source snapshot: 35 files. Frozen UTC: 2026-10-21T19:05:19.549002+00:00.

## The four implementation steps

1. Interface/tracing/bounds: optional backend-neutral ExecutionSession and ReliableTool wrappers; node-keyed input/output; strict types; recoverable validation; normal Exception stops; ended explicit/native spans; bounded cancellation completion; shared pre-dispatch read/write/automatic-check budget.
2. Separate validation: deterministic faults first, frozen fresh model cases next, independent state/report replay and Phoenix persistence checks. Model attempts, corrected responses and automatic checks stay separately attributed.
3. Deterministic Gazebo skill: fixed-base one-joint physics model, PID joint controller, ROS/Gazebo bridge, bounded command range and a separate read-only JointState observer. A command receipt does not prove motion.
4. Backend connection: both backends use the same actual ROSA executor, four tool schemas, prompt and budgets. A/D run on identical simulated targets/faults, with a matched direct controller reference documented below.

## Results

| Backend | Phase/arm | Correct outcomes | Achievable verified | Fault handling | Model calls | Native ops | Wall seconds | Invalid attempts | Auto checks | Trace audits |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| siwc | gazebo/A | 2/2 | 1/1 | 1/1 | 10 | 6 | 38.375 | 0 | 0 | 2/2 |
| siwc | gazebo/D | 2/2 | 1/1 | 1/1 | 10 | 8 | 32.983 | 0 | 2 | 2/2 |
| siwc | mock/A | 8/8 | 4/4 | 4/4 | 36 | 28 | 113.369 | 0 | 0 | 8/8 |
| siwc | mock/B | 8/8 | 4/4 | 4/4 | 36 | 28 | 106.960 | 0 | 0 | 8/8 |
| siwc | mock/C | 8/8 | 4/4 | 4/4 | 36 | 34 | 105.597 | 0 | 4 | 8/8 |
| siwc | mock/D | 8/8 | 4/4 | 4/4 | 36 | 34 | 108.177 | 0 | 4 | 8/8 |
| ollama | gazebo/A | 2/2 | 1/1 | 1/1 | 12 | 8 | 120.625 | 0 | 0 | 2/2 |
| ollama | gazebo/D | 2/2 | 1/1 | 1/1 | 9 | 7 | 114.131 | 0 | 2 | 2/2 |
| ollama | mock/A | 8/8 | 4/4 | 4/4 | 43 | 34 | 528.068 | 3 | 0 | 8/8 |
| ollama | mock/B | 8/8 | 4/4 | 4/4 | 42 | 34 | 477.617 | 2 | 0 | 8/8 |
| ollama | mock/C | 8/8 | 4/4 | 4/4 | 38 | 34 | 449.383 | 2 | 4 | 8/8 |
| ollama | mock/D | 8/8 | 4/4 | 4/4 | 38 | 34 | 447.482 | 2 | 4 | 8/8 |

## Findings and decision

### siwc

Execution status: **COMPLETE**, 36/36 recorded trials, 164 model calls.

The combined arm D **did not meet the limited benefit screen** against the repaired strong reference A.

D minus A: +0 correct outcomes, +0 verified achievable completions, +0 model calls and +6 native operations.

Observed total wall-time ratio D/A: 0.954. This is descriptive, not proof of causal speedup or slowdown.

Feedback-only arm B had no invalid calls requiring feedback. The live screen therefore does not establish a correction benefit or show that feedback is ineffective under actual errors.

### ollama

Execution status: **COMPLETE**, 36/36 recorded trials, 182 model calls.

The combined arm D **did not meet the limited benefit screen** against the repaired strong reference A.

D minus A: +0 correct outcomes, +0 verified achievable completions, -5 model calls and +0 native operations.

Observed total wall-time ratio D/A: 0.847. This is descriptive, not proof of causal speedup or slowdown.

The four implementation steps are an integration milestone, not evidence that extra mechanisms are necessary. Prefer the simpler configuration when outcomes tie; retain optional mechanisms only where a demonstrated failure mode and measured benefit justify their cost.

Next, choose one more realistic failure-bearing skill or expand the joint task with independently observed state changes. Freeze new cases before tuning; keep the competent reference and avoid simply increasing repetitions of these same easy fixtures.

## Attribution and limitations

All accepted reports remain model-authored. Automatic verification is orchestration assistance, separately counted; no report/identifier/value repair is performed.
A corrected model response after validation feedback is a combined-system outcome, not proof of greater intrinsic model capability.
The corrected shared interface is a prerequisite in all arms. Comparing these percentages with old Stage 4 percentages is not a controlled estimate of the interface effect.
Only four bounded custom tools are registered; the default ROSA ROS/system catalogue is disabled. This is actual ROSA agent execution but not validation of every upstream tool or arbitrary robotic instructions.
The common report gate requires a dedicated verify_outcome record (or the same internal check initiated automatically). A correct fresh read_state alone does not satisfy that rule. Rejection for that omission is contract noncompliance, not proof of a false physical claim or inadequate sensor evidence. Any call savings from avoiding this rejection may depend on this API policy. A future contract should examine reuse of already-fresh trusted observations before adding more checks.
When a strong reference ties, extra verification is not demonstrated benefit. Report redundant checks and actual cost rather than crediting complexity.
The fixtures are fresh to the models but inspected by scripted controls; this is not a secret held-out generalization benchmark.
A/B/C/D have eight mock trials each, only four achievable; Gazebo has one trial/case/arm/backend. No statistical significance, general small-model result or safety claim is established.
The simulator is a fixed-base single revolute joint, not a complete manipulator or grasp/place task. Suppressed commands and missing observations are injected faults.
Targets are explicitly supplied as structured values. This does not test language ambiguity, perception, task decomposition, navigation or a reason to prefer an LLM over a deterministic controller for an already-typed joint target.
The evaluator uses separate state/subscription records but shared trusted fixture definitions and authoring; independence is from agent claims.
Gazebo resets are checked in runtime before each trial; raw per-reset values were not separately archived by this first runner. Final independent observations are archived.
The frozen quick score counts unsupported success against final outcome. Supplementary replay also evaluates mock claims at their call-time state and separately counts missing named-verifier records. Original scores are retained. A missing named record is not automatically a false or physically unverified claim.
Gazebo has one command/task; call-time physical assessment after that command uses the final separate sensor sample, not a continuous independent trajectory oracle.
Final prose is retained but not exhaustively semantically graded. Report-tool claims and structured outcome are the evaluated contract.
Serving profiles differ. Same maximum budgets do not mean equal actual tokens or compute. Timing is descriptive and order is rotated rather than randomized.

No separate inference warm-up was preregistered; first-trial loading may affect timing. Tool observations expose acquisition timestamps, so nominally deterministic generation settings do not imply byte-identical prompts across trials. Differences before the first feedback event cannot be attributed to feedback formatting.

## Matched deterministic controller reference

- gazebo_bounded_move: pass=True, target=0.28, separate position=0.279999930, native skill operations=3, model calls=0, wall=1.525s.
- gazebo_accepted_no_motion: pass=True, target=-0.32, separate position=0.000000000, native skill operations=3, model calls=0, wall=1.520s.

This controller uses the identical bounded ROS command transport and a separate sensor subscriber. It was run after the live backends; timing is not randomized. It does not simulate language understanding or use the LLM report interface.

## Every failed trial

No failed task/report outcomes among the completed records. Check backend completion and Phoenix audit before interpreting this as a finished campaign.

## Reproduction and next decision

Read analysis.json and independent-replay.json for full metrics. Each trial retains model messages, tool inputs, operation ledger, raw transport records, separate oracle and real spans.
Read phoenix-audit.json for independent persisted-span equality, not merely exporter completion.
Run the separate demo using scripts/reliable-gazebo.sh --backend deterministic (or ollama/siwc). Hosted demo requires a fresh memory-only OAuth session.
Keep JTVR paused and episodic memory deferred. Expand to a specified arm or a more difficult task only after interpreting this screen; do not tune the frozen cases to manufacture a benefit.
