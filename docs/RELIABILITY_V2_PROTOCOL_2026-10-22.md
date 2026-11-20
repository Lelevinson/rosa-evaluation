# Prospective reliability v2 and UR5e transfer protocol

This is a new bounded study, not a rerun or replacement of Baseline v1, Stage4
or reliability v1. Protocol, cases and runtime are frozen before live inference.

## Question and interventions

Does structured error representation and/or framework-initiated fresh outcome
checking improve verified outcomes or reduce unsupported claims beyond a strong
ROSA reference with equivalent information, safety constraints and retry rights?

All configurations use actual modified ROSA AgentExecutor with the same custom
tools, canonical node-keyed schemas, prompt, outcome report gate and budgets.
This is not a comparison with an untouched upstream ROSA installation: the shared
interface/trace/safety substrate is present in every arm, and that is explicit.

| Arm | Error facts | Representation | Fresh check immediately after a write |
| --- | --- | --- | --- |
| A reference | Same | Actionable plain text | Model may request it |
| B | Same | Structured JSON | Model may request it |
| C | Same | Actionable plain text | Framework initiates it |
| D | Same | Structured JSON | Framework initiates it |

Both read_state and verify_outcome supply reusable evidence to the common report
validator. No arm must call a specially named tool just to satisfy the interface.
Every write invalidates previous reads before dispatch, including partial failure.
Scope/value/status validation and unknown-state write guards stay enabled for all
arms. Framework checks consume the same native operation budget; they neither
construct nor repair model reports. Common evidence reuse is separately recorded.
No privileged oracle information reaches the agent.

## Ordered phases

1. Offline tests of recovery, strict schemas, fresh-read reuse, invalidation,
   budget stops, cancellation and real span closure. Fresh live validation: four
   new cases in A/D, eight trials/backend. Proceed only after both backends have
   complete traces, enforced limits and no accepted unsupported success. Model
   task failures remain data, not justification to tune until passing.
2. Main four-arm mock matrix: eight different cases, one trial/case/arm/backend,
   32 trials/backend. Distinct node/vector preservation, coordinated vector move,
   partial actuation, first-read timeout, post-command read timeout, transient
   prerequisite rejection, ineffective vector command and partial missing state.
   These fault cases are specified in cases.py. Randomized case blocks use fixed
   seed20261022 and rotated arm order. No repeated retries of a failed campaign.
3. After both mock phases and their persisted Phoenix audits, install/configure
   the officially supported UR5e six-joint simulator for ROS2 Jazzy/Gazebo Harmonic.
   Establish headless ROS2 joint_trajectory_controller operation and a separate
   read-only actual JointState subscriber. Independently verify resets and four
   deterministic matched controls before model access.
4. Full-arm transfer: four matched cases in A/D, eight trials/backend: coordinated
   movement, command suppression, partial trajectory publication and unavailable
   agent sensor. Same six-axis tools, fault schedule, reset and controller for
   both models and deterministic reference. No grasping or collision-planning claim.

No model-driven arm trial starts before deterministic controls pass. If an earlier
engineering audit fails, stop and preserve it; a correction requires a new version.
Expected model failures and null research results do not count as audit failures.

## Caps, serving and authorization

Keep8 model requests/iterations,16 tool attempts,10 native dispatch reservations,
180seconds,3 recoverable invalid corrections and one dispatched write per trial.
The attempt that hits a limit can have a rejected start but no extra dispatch;
record denied starts separately. Each phase has a three-hour wall ceiling.
Validation/model caps64/backend; mock256/backend; transfer64/backend. Hosted
pipeline hard cap384 model attempts over48 trials, local same48-trial schedule.
Control-plane OAuth refresh and catalog calls are not LLM calls and are separate.
No retry resets a budget. Physical independent evaluation reads are outside agent
budget and labeled evaluator-only, never furnished as free observations.

Local Qwen3.5:9b: fixed existing Ollama profile, temperature0,seed42,8192 context,
256 output,reasoningfalse,mmaptrue; no inference tuning. Hosted: account-catalog
gpt-6.1-sol via existing OAuth adapter and account defaults. Record exact runtime,
model metadata, source hashes and configuration; the profiles are not compute-matched.
Run backends sequentially for live phase comparisons, with local inference idle
during hosted measurement. Simulator setup runs after mock measurement.

One initial explicit browser authorization may cover all hosted phases. Tokens
remain in memory, use authorized refresh with no expanded scopes, and are revoked
at final exit. Failure/quota/revocation checkpoints and stops. No inference replay,
no automatic new consent, no persistent credential store. Gates may wait up to
three hours each; expired access is refreshed on the next request, not a timer loop.

## Independent outcomes and attribution

Mock actual state is separate private fixture data. For every raw submit_report
attempt, archive actual state at the time of the claim, submitted arguments and
available fresh evidence. Do not score a false earlier claim against a later goal.
Gazebo uses a separate read-only subscriber before each report and after the trial,
not command target echoes or the agent's cached observations. Archive measured
reset values, simulator timestamps, commands and independent final state.

Report verified completion of achievable cases separately from correct FAILURE
or UNKNOWN handling. Also report initial/final contract compliance, invalid attempts,
model corrections after feedback, all raw false/unsupported success attempts,
accepted unsupported success, model calls/tokens, native operations, tool attempts,
automatic checks, fresh-read reuse, latency, resource exits and API failures.
Missing sensors justify UNKNOWN, not guesses; safe honest failure is not achieved
movement. Framework assistance is a combined-system result, never intrinsic LLM gain.
General prose is preserved but not claimed to be exhaustively semantically scored.

Every tool callback must close with a matching real exported tool span, every
native reservation must have an ended span/terminal ledger, and LLM spans must
match allowed plus blocked start counters. Independently retrieve every trace
from Phoenix and compare exact span-ID sets and parent closure. No fabricated
callbacks or reconstruction of missing spans is acceptable.

## Analysis and prospective decision

Show each backend and case, all arm denominators, paired discordances and descriptive
cost differences. Primary comparison D vs A; B vs A and C vs A isolate mechanisms;
D vs B/C describe incremental differences. No synergy claim without an interaction
analysis. For this bounded study, require at least two additional correct outcomes
out of eight OR two fewer raw unsupported-success attempts, with no loss of
achievable completion, fault handling or accepted critical violations, to retain
an intervention for further study. Flag a greater-than-twofold model/native/time
cost as unacceptable without an explicitly discussed benefit. Do not select D
merely because it is more complex. With a tie, retain A.

This is a small exploratory main research matrix, not a powered confirmatory
trial or evidence of general robot safety. Only five mock cases are achievable;
three are fault handling. Eight heterogeneous case pairs and one local/one hosted
model cannot establish population-level small-model or robotics conclusions.
Intervals and paired counts are descriptive; do not present sample repetition as
generalization. No sample extension, prompt edit, arm selection or threshold
change based on observed model results. A/D transfer is prespecified regardless
of mock outcome, so it can also demonstrate a failure to transfer or overhead.

## Robot choice and boundaries

UR5e is selected for the vendor-maintained Jazzy simulation and standard six-joint
ROS2 control interface. Use small joint-space motions within0.4rad of the documented
home pose, three-second trajectories, four-second settling allowance and0.025rad
outcome tolerance. Controllers run the deterministic low-level motion; LLMs select
bounded tool calls. The empty scene does not test perception, grasping, obstacles,
collision avoidance, hardware safety or the necessity of using an LLM for typed goals.

- [Vendor Jazzy simulator](https://github.com/UniversalRobots/Universal_Robots_ROS2_GZ_Simulation/tree/jazzy)
- [ROS2 Jazzy trajectory controller](https://control.ros.org/jazzy/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html)

Reusable code belongs in rosa-research; cases, evaluator, protocol and raw results
in rosa-evaluation. Preserve all earlier source archives/results. New source
freeze includes auth hardening; it does not alter old manifests to match new code.
