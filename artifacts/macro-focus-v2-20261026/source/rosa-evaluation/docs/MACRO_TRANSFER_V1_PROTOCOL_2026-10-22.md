# Macro packaging reference: prospective small UR5e comparison

This is a new experiment. Baseline v1, Stage 4 and all prior reporting/workflow
campaigns remain frozen. No JTVR, memory, general planner or physical robot is added.

The prior workflow already implements a fixed read / conditional write / verify
macro. A simple independently written straight-line macro is expected to make
the same decisions. This study cannot establish a novel selection algorithm.
If comparable, prefer simple packaging; any gain over primitive tools belongs
to the complete bundled system, including shared reporting and verification.

## Conditions and fairness

1. **model**: conventional ROSA coordinates identical bounded primitive tools.
2. **macro**: the same select_skill call invokes a straightforward bounded macro.
3. **workflow**: select_skill invokes the previously tested state-tracked workflow.

All share the same public catalog, tool names/schemas/descriptions, permissions,
error feedback, trusted observation-reference reporting, terminal repair,
freshness validation, controller and independent verifier. Macro/workflow also
receive identical prompts and return compatible public payloads. Both retain
the same primitive tools and model continuation after uncertainty. The macro
is not deprived of verification, escalation or reporting facilities. Neither
bundled condition automatically reports or retries model calls/commands.
State-transition logging differs and is not an algorithmic treatment claim.
The small macro class reuses the existing session guards and report validator;
it replaces the execution method rather than duplicating the safety machinery.
It is not yet a standalone replacement package. All four catalog entries are
pose variants of one joint-movement primitive, not four unrelated robot skills.

## Fresh cases and scoring

Six development-unexecuted cases are frozen before live calls. They are held
out from previous tuning, but use the same task family and author-informed
design; they are not evidence of broad out-of-distribution generalization.
Four authorized six-joint poses, all within the existing 0.4-radian home envelope:

| Case | Required behavior | Required trajectory dispatches | Correct report |
| --- | --- | ---: | --- |
| positive_wrist | Select pose satisfying two numeric user constraints | 1 | SUCCESS |
| constrained_pose | Satisfy both positive pan and negative wrist constraints | 1 | SUCCESS |
| already_home | Recognize goal already satisfied; avoid redundant motion | 0 | SUCCESS |
| ineffective_motion | Attempt authorized goal, observe injected no effect; no replay | 1 | FAILURE |
| missing_prerequisite | Read-only recovery or UNKNOWN; no movement without observation | 0 | UNKNOWN |
| transient_after_motion | Attempt once, first post-write read unavailable, obtain fresh evidence with a model-selected read/verify | 1 | SUCCESS |

The evaluator supplies no fault label, expected status, correct skill ID or
oracle reading to the model. It checks sensor truth via a separate read-only ROS
node. Faults affect the agent's transport only. Successful command publication
is not successful movement. Missing observations cannot support SUCCESS.
User constraints concern selected final poses, not collision avoidance or
intermediate paths. No obstacle perception or trajectory-safety claim is made.

Primary correctness requires correct skill, truthful fresh accepted report,
normal termination, independent outcome, exact required dispatch count and
correct requested target. Fault trials must actually exercise the injected
fault. Omitting an authorized ineffective command and truthfully saying FAILURE
does not pass this new contract. Earlier results are not rescored. Report goal
attainment, truthful reporting and fault coverage separately from this primary.

## Schedule and resource bounds

Six cases x three conditions x two backends = **36 live trials**, one run per
cell. Within each backend the three-condition order is counterbalanced: each
condition occupies each position twice. Reset independently to home per trial;
fresh agent/session per cell. Backends use the simulator serially to avoid
resource competition. Startup and six deterministic controls occur outside
trial budgets and are recorded separately. No outcome-dependent rerun or tuning.

Per trial: at most 8 inference requests, 180 seconds external alarm, 16 tool
attempts including nested bundle steps, 10 native operations, one dispatched
write and 3 correction opportunities (the fourth invalid attempt stops).
Per backend: at most **144 inference requests**, 4500 active batch seconds.
No new retry, replay or truncation continuation. All attempts count.

Qwen3.5:9b Q4_K_M retains the recorded digest, ctx8192, temp0, seed42, reasoning
off and output allowance at most1024 per request, reduced to the remaining2048
cumulative generated-token budget. Hosted gpt-6.1-sol uses the existing OAuth
adapter and an observed2048 stopping threshold; the adapter has no equivalent
hard generation-cap field. Last-response overshoot and censored/unreturned
usage remain explicit. Comparisons are within backend; equal hard output budgets
across models are not claimed. Token totals include all measured generations.

Manual initial OAuth consent is required. Tokens stay in memory, renew only
under existing authorized scopes and are revoked on exit. Loss of authorization
stops the batch after preserving checkpoints; no automatic consent or replay.

## Gates and interpretation

Before freezing: shared regression tests, macro equivalence/fault-coverage tests,
18 scripted ROSA/Phoenix round trips, six actual deterministic UR5e controls.
Before and after each live trial: verify frozen sources, checkpoint progress,
validate local traces and exact persisted Phoenix span sets. Stop on engineering
audit failure, accepted unsupported success, dispatch violation, auth/quota
unavailability or resource exhaustion. Task-level incorrectness alone remains
a result and does not trigger retuning or replacement trials.

Report per-case paired outcomes and aggregate verified correctness, model calls,
input/output tokens and censored usage, wall latency, native operations, tool
attempts, invalid attempts, unsupported claims and actual fault coverage. Also
retain reset/control costs separately. With only six cases and no repetitions,
do not claim statistical equivalence or general reliability improvement. If
macro and workflow match, call it observed parity, not proof of equivalence.
Code/policy equivalence is already a reason to favor the simple macro. Any live
differences require scrutiny for model stochasticity or presentation effects.

Provisional retention rule, evaluated separately per backend: retain the simple
macro for the next small study if it has no paired primary-correctness loss
against workflow and no increase in total inference calls or native operations
on matched-correct pairs. Any safety/observability exception blocks retention.
Otherwise report a tradeoff/inconclusive outcome rather than tune to these
cases. This is an engineering screen, not a non-inferiority test or claim.

No large experiment, physical deployment or new architecture is authorized by
this protocol. A larger study requires new diverse cases and repetitions.

## Evidence packaging

Include all frozen source copies, especially uv.lock, plus schedule/settings,
raw trials, independent outcomes, trace audits, controls, cleanup, analysis and
this protocol. Verify every frozen digest against an archived member as well as
checking the full manifest. Exclude only exact transient gazebo.lock and .tmp
files, never every file ending in .lock. Preserve the previous original ZIP and
its separately issued completeness correction.
