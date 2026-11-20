# Reliability v1: prospective engineering validation and Gazebo transfer screen

Registered before live inference on 2026-10-22. This is separate from the closed
Stage 4 campaign. No historical score or source snapshot is replaced.

## Question and hypotheses

Under fixed execution limits, do structured validation feedback and automatic
fresh verification improve ROSA task/report reliability beyond a consistent
interface, clear instructions and ordinary bounded retries?

H1: structured feedback increases compliant correction and final correct
outcomes relative to ordinary errors carrying the same facts. H2: automatic
verification reduces missing verification or unsupported success claims, with
any gain reported alongside its operation/time cost. The combined arm may help,
tie or hurt; no synergy or broad small-model claim is presumed.

This small screen is an engineering validation, not a powered confirmatory
study. Two repetitions on four new fixtures do not establish generalization.

## Shared platform and interventions

All arms use the actual modified ROSA AgentExecutor, custom-only tools, the same
clear prompt, canonical node IDs, strict numeric types, node-keyed state/report
structure, safety constraints and explicit verification tool. No runtime schema
or identifier/value repair occurs. Missing observations are null with explicit
timeout provenance. Observed outcomes are SUCCESS, FAILURE or UNKNOWN.

| Arm | Error representation | Automatic verification after a write |
| --- | --- | --- |
| A | Plain text containing the same facts | No |
| B | Structured JSON | No |
| C | Plain text containing the same facts | Yes |
| D | Structured JSON | Yes |

The reference can correct errors and request verification itself. All arms must
verify freshly before an accepted final report. Automatic checks use the same
transport, consume the shared native budget and are attributed to the
orchestrator. No automatic report construction or extra recovery policy is
introduced. Report numbers and goal attainment have a declared absolute
tolerance of 0.015 (state units; radians in the joint fixture).

Plain and JSON errors contain code, details, rejected status and remaining
corrections. This tests the representations of those facts, not generic errors
versus privileged advice. Pre-dispatch prerequisite checks remain enabled in
every arm. Model attempts and accepted dispatches are reported separately.

## Cases, order and sample size

`experiments/reliability_v1/cases.py` fixes four new development-independent live
fixtures: two-node state discrimination, post-write freshness, an accepted but
ineffective command, and unavailable observations. Each backend runs four arms
and two repetitions: 32 mock trials. Order rotates by fixture and repetition;
it is fixed rather than statistically randomized. No case is tuned after live
results. Deterministic scripted controls inspect these fixtures before freezing;
they are fresh to the models, not a secret held-out benchmark.

After those trials, each backend runs A and D on the same Gazebo bounded move
and accepted-but-unexecuted fault, one repetition each: four simulator trials.
This is a limited transfer check, not an additional complete factorial study.
The supported fixture is a custom single revolute-joint arm with a fixed base,
not a full manipulator, grasping environment, MoveIt stack or hardware robot.

The Gazebo joint position controller receives ROS Float64 commands through
ros_gz_bridge. A separate read-only ROS node evaluates actual JointState output;
it does not trust command receipts, target values or the agent's cached readings.
Outside-trial reset to zero must be independently observed within 0.015 radians.
Command suppression is an injected transport fault, not evidence of a naturally
occurring simulator failure. It tests whether acceptance is confused with motion.

## Limits and serving profiles

Per backend: 36 trials, maximum 288 model requests, three hours after sign-in.
Per trial: eight model calls/iterations, 16 tool attempts, 10 native dispatch
reservations, 180 seconds, at most one native write request. Up to three invalid
calls may receive corrective feedback; the fourth terminates. Rejecting an
invalid call does not consume native dispatch budget. Every actual transport
read/write reservation, including an errored read or automatic check, does.

Local: qwen3.5:9b, temperature 0, seed 42, context 8192, output 256, reasoning
disabled, mmap enabled; no serving optimization during behavioral testing.
Hosted: existing OAuth adapter, account-catalog gpt-6.1-sol and account-default
sampling. These are not matched model/token/compute profiles. Auth tokens stay
in memory and are revoked on scope exit. No new API key is required.

Inference runs sequentially within a backend. No automatic retry/rerun of a
failed trial or campaign is allowed. Unexpected tracing/operational failures
stop the batch and remain recorded; any revision needs a separate version.

## Evaluation and decision rules

Primary achievable-task endpoint: verified goal attainment with an accurate,
accepted model report and normal operational completion. Report physical/mock
goal state, report compliance and API/limit exits separately.

For fault cases report correct FAILURE/UNKNOWN handling separately, not as
achieved movement goals. Record initial schema compliance, all invalid attempts,
model corrections after feedback, raw unsupported SUCCESS report attempts,
accepted unsupported reports, automatic versus model-requested verification,
native work, model calls, reported tokens and wall time. Preserve final prose,
but do not claim exhaustive semantic grading of arbitrary extra prose.

All agent tool starts require terminal LangChain callbacks and real exported
tool spans. All reserved native operations require ended explicit spans and
terminal ledger records. Phoenix persistence is checked separately from local
export completion. A missing span is an acceptance failure, not repaired by
inventing a callback. Deterministic cancellation tests require bounded in-flight
dispatch completion and callback closure before cancellation propagates.

Engineering acceptance: deterministic schema/freshness/budget/stop/cancellation
tests pass, all live trace audits pass, operation caps hold, no accepted
out-of-bound or unknown-state writes, and no accepted unsupported success.
Model failures are measured results, not permission to retune until they pass.

For the limited benefit screen, D versus A must improve achievable completion or
reduce false model success attempts by at least one trial within a backend,
without lower correct outcome handling or more accepted critical violations.
Flag greater-than-twofold model-call or wall-time totals as a cost concern.
Report denominators and per-case paired outcomes; these coarse pilot criteria
do not establish statistical significance or a publishable research contribution.
If ties, failure or ceiling effects prevent an improvement claim, state that.

## Reproducibility and boundaries

Freeze the runtime source, tools, tests, case schedule and this protocol before
live inference, with exact-byte snapshots and SHA-256. Existing Stage 4 artifacts
remain unchanged. New reusable implementation belongs in rosa-research; this
protocol, scorer, raw records and reports belong in rosa-evaluation.

Official integration references:

- [Gazebo JointPositionController](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointPositionController.html)
- [Gazebo JointStatePublisher](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointStatePublisher.html)
- [ROS/Gazebo bridge message mappings](https://index.ros.org/p/ros_gz_bridge/)
