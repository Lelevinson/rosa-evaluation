# ROSA research: six-stage roadmap and evidence map

Updated: 2026-10-21 after the three-policy experiment. This is a complete roadmap document, not a claim that all six
stages are complete. Original JTVR design and current code were compared in
[JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md](JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md).

The subsequent [policy comparison report](../artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md)
records 1,152 audited policy episodes and 15 audited real ROS smoke episodes.
JTVR tied amortized batching on all 96 primary fixtures and missed the predefined
10% benefit criterion. Full custom Runnable/model integration is paused for this
catalogue. This does not complete the separate live reliability follow-up.

## Project goal and numbering

Evaluate Qwen3.5 9B and the hosted OAuth comparator through the same ROSA interface,
then determine whether bounded joint task/verification evidence acquisition and
verified episodic memory add measurable value over strong simpler alternatives.
Eventually validate compatible high-level skills on a specified simulated robot
and, separately, an approved physical platform.

These six stages are project work packages. They do not renumber old master-plan
gates retrospectively. The completed historical Stage/Gate 1–4 report ended at
simple caching; it did not test the original JTVR selector. The broader Stage 4
below includes original-JTVR research and is currently incomplete.

| Stage | Work package | Current status | Evidence / remaining requirement |
| --- | --- | --- | --- |
| 1 | Interchangeable Qwen and hosted ROSA backends | Demonstrated in mock tools | Native calls and actual modified ROSA integration work; not yet a robot skill interface. |
| 2 | Stateful world, contract and independent scoring | Working foundation; corrections tested | v1 scorer and trace audits exist; v2 has 41 passing tests. New ROS evidence contracts/parsers remain. |
| 3 | Baselines and controlled reliability experiments | v1 pilot completed; follow-up pending | 120 v1 live trials across 12 scenarios plus 540 scripted controls. Prospective v2 model trials: zero. |
| 4 | Caching and original JTVR evidence acquisition | Policy comparison and real ROS smoke completed; reliability follow-up pending | Original selection core tested separately from fixed bundles. No benefit over strong batching; full integration paused. |
| 5 | Verified episodic memory | Not started | Needs history-dependent tasks and controls for extra examples, retrieval and token budget. |
| 6 | ROS/Gazebo arm and eventual hardware integration | Base simulator installed; arm integration not started | Gazebo 8.15.0 responds; robot models/controllers/skills are not configured. Hardware is unspecified. |

## Stage 1 — shared backend interface

Deliverable: one ROSA tool interface with selectable local Qwen or hosted account
model, native tool arguments/results, session isolation, and bounded requests.

Already demonstrated:

- Qwen3.5 9B native single/dependent tool round trips and actual custom-only ROSA.
- Hosted model through the same modified ROSA executor, with memory-only OAuth
  credentials and session revocation after completed batches.
- Explicit allowlisted tools; copied per-agent prompts; no accumulated trial chat.
- Local uv environments, Phoenix and project-owned Ollama services.

Keep backend settings and resource limits in each run. This establishes interface
compatibility, not capability equivalence or reliable physical motion. Original
JTVR needs additional cross-backend policy-observation history tests; existing
native-call tests do not establish deterministic continuation support.

## Stage 2 — task contract, world and evaluator

Deliverable: explicit success/failure/UNKNOWN/refusal rules and an evaluator that
checks state/evidence independently of the model's claim.

The foundation uses a separate world process, agent/evaluator IPC channels,
ordered calls and Phoenix read-back. World and scorer share a trusted simulation
implementation; this is not independent physical sensing or an adversarial OS sandbox.

The corrected movement contract separates:

1. Physical goal state.
2. Accurate structured outcome classification.
3. Tool/report argument compliance, including raw model types before coercion.
4. Rejected invalid attempts versus accepted actions and unsafe executions.
5. Required verification at claim time, one report, and no subsequent tools.
6. Repeated verified failures and unnecessary movement when a goal already holds.

The old battery sentinel is retained for controlled comparison. Redesigning that
API is a separate intervention. The original-JTVR parameter contract will be
separately versioned: valid post-write reads may jointly support task reporting
and equality verification. It must not inherit the movement-specific requirement
to invoke a tool named `verify_goal`.

Exit criteria: negative tests reject false claims, missing/late evidence, invalid
arguments, stale/scope-mismatched facts and corrupted records. An accurate value
can resolve an observation obligation while showing the goal is false. No
hypothetical lookahead value may enter the actual evidence ledger.

## Stage 3 — baselines and reliability attribution

Baseline v1 is preserved. Original baseline handling was local 24/36 (66.7%) and
hosted 30/36 (83.3%); both verified all 18 achievable baseline goals. Retrospective
additional strict checks give local 12/36 and hosted 30/36. These percentages
measure different contracts and must remain separately labeled.

The v2 scripted preflight completed 264 final trials and independent audits. Its
60 fixtures vary twelve failure mechanisms but remain simple transfer tasks.
They do not reproduce the original ROS information-acquisition problem.

Proposed reliability follow-up: six existing development fixtures, four independent
configurations, two repetitions = 48 trials per backend:

- Original instructions.
- Clarified instructions only.
- Bounded recovery only.
- Report-time verification enforcement only.

This is a small intervention screen, not a general capability ranking or safety
proof. Count system-generated verification/reports separately from model behavior;
a guard repair is a combined-system improvement. Use one inference configuration
within the comparison; keep performance tuning under separate identifiers.

Nine local native diagnostic requests completed. The original 8192-context
auto-offload profile generated approximately 9–11 tokens/s on the short request;
forced 24-layer offload approximately 14–15. This does not establish sustained
task speed or remove memory constraints. No behavioral baseline silently adopted
the faster profile.

Exit criteria: complete planned attempts, preserve failures, export traces/audits,
and report each intervention separately. Do not manufacture a required score by
changing evaluation rules after seeing failures.

## Stage 4 — reliability, original-JTVR selection and ROS validation

### 4A. Consolidate reliability evidence

Finish the Stage 3 follow-up under a fresh, accurately named protocol. Preserve
the interrupted v2 candidate and frozen artifacts. Its `jtvr` policy label means
fixed dependency bundling, not a successful or failed original implementation.

On receipt of the original design, the pending hosted batch was closed before
consent with zero model requests/trials. Cleanup reported NO_TOKEN_SESSION. Its
automatic local successor did not run. No prior experiment was erased.

### 4B. Test the original contribution

The policy-only tier below has now run under the separate
[frozen protocol](STAGE4_POLICY_PROTOCOL_2026-10-21.md): 288 primary, 576 sensitivity,
96 depth and 192 role-ablation episodes, all audited. Primary J/B costs tied
96/96; prior-type sensitivity had two J losses. Joint scheduling helped both B
and J, and depth two did not improve over depth one. These results do not justify
the full Runnable/model tier in the currently registered catalogue. The remaining
text preserves the wider conditional plan, not authorization to bypass that stop.

Use original ROSA information-tool contracts: parameter get/set, service/node
information and supported GetParameters calls. Do not introduce a custom aggregate
tool available only to JTVR.

Minimum components to review before implementation:

- Canonical joint obligations and a provenance-bearing evidence ledger.
- Dispatch-time field epochs, phase barriers and conservative parsers.
- Common exact-instance enforcement and read-only continuation runner.
- Greedy acquisition, amortized batching and depth-two prefix/residual selection.
- Configurable ROSA agent factory and cross-backend continuation formatter.
- Native operation, model-call, token, policy/binding and total-cost measurements.

Compare strong prompted ROSA with conservative reuse, greedy coverage/cost,
amortized batching plus reuse, and original JTVR. The latter three share the same
requirements, costs, capabilities, validity and continuation facility. A generic
deterministic task planner is an auxiliary control, not a replacement for batching.

Begin with the review's policy-only study: 96 fixed fixtures per policy, up to
384 episodes including a weak cache mechanism control. Freeze calibration and
evaluation separately. If JTVR and strong batching tie throughout the scope,
document that boundary before building more.

If justified, the model screen is eight preselected fixtures x four arms x two
backends x two repetitions = 128 episodes. Continuation on/off on four preselected
cases for batching/JTVR adds 16 episodes. A role-separated rollout ablation keeps
shared reuse enabled to isolate joint obligations.

For planning: 48 reliability + 64 core selection + 8 continuation-ablation episodes
per backend = 120 episodes/backend. At respective 14/12/12 request caps, that is at
most 1,536 model requests/backend, excluding separately declared calibration. These
are proposed budgets, not completed or automatically approved experiments. Settle
the revised protocol before launching this schedule.

Fix success criteria prospectively. Preserve observed verification correctness,
then measure improvement against amortized batching including overhead. A small
screen can justify further evaluation, not a general reliability/novelty claim.

### 4C. Validate ROS interfaces

Completed a 15-episode nominal smoke check: five templates under each of G/B/J,
using real ROSA wrappers, isolated Jazzy nodes and separately recorded server
values. All passed. B and J used the same native work; one-repeat wall times are
not a comparative latency result. Real injected-fault campaigns remain unrun.

Use isolated test parameter nodes with real Jazzy CLI/service interfaces. Confirm
raw parsing, batching, write/readback phases and native request counts. Turtlesim
is optional; no robot arm or Gazebo is required. Scope access to test nodes.
Do not assume atomic snapshots or detection of arbitrary external writers. State
writer/freshness assumptions and report stress-test failures.

### Completion and decision

Stage 4 completes when the agreed experiment reaches its predefined stop point,
with all planned or explicitly stopped work accounted for and audited. A tied,
negative or inconclusive outcome is valid. It does not justify relabeling a fixed
bundle as original JTVR or omitting unfavorable cases.

Deliverables: versioned protocol/source identity, complete ledger, raw/normalized
evidence, cost logs, audits, limitations and a keep/simplify/stop decision. Explain
which later experiments an early stop left unrun. Until then Stage 4 is incomplete.

## Stage 5 — verified episodic memory

Start when the task distribution gives prior verified experience a useful role.
Current observations remain authoritative for mutable robot state.

Compare no memory, fixed-example prompts with matched examples/token budget,
unverified memory and outcome-verified memory. Store provenance, task scope,
execution conditions, freshness limits and SUCCESS/FAILURE/UNKNOWN separately.
Test incorrect/outdated episodes, changed conditions and overgeneralization.

Measure retrieval overhead, total tokens/time and task outcomes. Memory must not
authorize motion or replace required observations. A database implementation alone
does not complete the research question; a measured negative decision is valid.

## Stage 6 — simulated arm, then separately approved hardware

ROS 2 Jazzy and Gazebo integration are installed; Gazebo 8.15.0 responds after
sourcing ROS. The inspected robotics workspace is empty. No arm model/launch
configuration was found in the two repositories. The usual ros2_control/Gazebo
controller packages and MoveIt were absent. Earlier GUI checks reported software
rendering; current GUI usability is unverified.

First make one supported example arm move through ordinary ROS control. Expose
a few validated ROSA skills and give both models identical pose tasks from the
same reset states. Independently check fresh joint measurements. Then attempt
physics-based grasp/place; coordinated dual-arm behavior follows the simpler path.

Robot models, controllers, planning and gripper/perception assumptions are separate
integration tasks. Prefer the eventual hardware model when its drivers/constraints
are known. Physical testing also requires the specified lab platform, interlocks
and authorization.

This stage can begin before Stage 5 if robot relevance is the priority. JTVR and
memory are not prerequisites for Gazebo. Mock percentages do not transfer
numerically to a physics simulator or hardware.

## Conditional commit requested by the user

Verified destination: `https://github.com/Lelevinson/rosa-evaluation.git`, local
branch `member/martin`. The user requested committing results/files after the
newly tested Stage 4 finishes. That condition has not been met; no final Stage 4
commit or push was performed in this review.

At completion:

1. Confirm the branch; inspect all existing dirty/staged work.
2. Preserve Baseline v1 and identify retrospective calculations.
3. Place curated reports, CSV/JSON summaries, protocol/manifest hashes and exact
   reproduction commands inside the evaluation repository. Workspace `reports/`
   is outside this repository; generated `results/` is ignored. They are not
   automatically included in a commit.
4. Preserve reviewed raw evidence as an artifact with checksum and clear location.
   Do not blanket-force-add local results, databases or configuration.
5. Reference the research revision or an exact reviewed patch for required ROSA
   changes; an evaluation commit does not capture sibling repository edits.
6. Complete relevant tests, audits, credential checks and diff review. Stage an
   explicit authorized file list and commit the actual result, including a
   negative/inconclusive conclusion, on `member/martin`.

## Immediate next decision

Review and settle the original-spec minimal experiment before JTVR code changes.
Keep focused reliability work in a separate configuration. The earlier sign-in
prompt is retired; a subsequent batch needs a fresh prompt with revised scope.
