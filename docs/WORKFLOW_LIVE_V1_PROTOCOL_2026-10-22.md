# Workflow live v1: small feasibility pilot

Prospective development-informed pilot, not a held-out benchmark or significance
test. Historical scores/protocols and the completed workflow development record
remain frozen. No Gazebo or physical robot operations are in this pilot.

## Question and comparison

Does transferring routine skill execution to the current ROSA workflow preserve
verified outcomes and reduce model invocations in these six known task families?
Evaluate Qwen against its reference and Sol against its reference. Neither a
Qwen/Sol capability ranking nor a novel routing algorithm is the primary claim.
The select_skill macro semantics are part of the complete intervention.

Both conditions receive two permitted skills, public numeric targets and the
same user goal. The selected skill must match east/west intent, independently
scored outside the session. The workflow never receives the evaluator's correct
skill label or fault label. Different text exposes the actual execution mode;
other instructions, tools, terminal repair and safeguards are shared.

Six cases: east healthy, west healthy, west accepted-no-effect, east unavailable
observations, west unavailable post-write observations, east controller rejection.
Twelve trials per backend: each case once per condition, counterbalanced nearby
pairs. Twenty-four trials total. No replacement of failed trials or live tuning.
One occurrence per condition cannot support a generalization/statistical claim.

## Controls and resource limits

Per trial: at most 8 model requests, 16 tool attempts including nested workflow
steps, 10 native operations, 3 invalid corrections, one dispatched write, 180s
external SIGALRM. Backend cap: 96 inference requests and 2700s active run time;
consent wait excluded. No automatic inference retry or truncation recovery.
Checkpoint each started trial and save terminal state even after authorization
loss or interruption. Never replay a completed or uncertain command.

Qwen: qwen3.5:9b Q4_K_M, same model digest as the prior campaign, context 8192,
temperature 0, seed 42, thinking disabled, use_mmap true. Per-call output maximum
1024, reduced to the remaining cumulative 2048 output allowance. This is a new
prospective serving choice informed by the completed output-budget study, not
a global edit or a rescore of its 256-token baseline.

Sol: existing ChatSiwc, account-catalog model gpt-6.1-sol, unchanged official OAuth
transport and account sampling defaults. This adapter does NOT expose a hard
per-response generation-token cap. After each returned response, meter all usage;
if cumulative output exceeds 2048, stop before any calls in that response execute.
This is an observed-output stopping threshold, not a hard generated-token bound:
the final hosted response can exceed it. Failed/unreturned hosted generations
have UNKNOWN usage (known lower bound only). The two Sol conditions use identical
rules. Cross-backend token allowances are not claimed equal. Request/time/native
ceilings remain hard client-side dispatch limits.

Require complete nonnegative usage on returned responses; no silent zero defaults.
On local generation timeout reserve the requested allowance as an honest output
upper bound, unload the model before proceeding and preserve finish reason as
unknown. On hosted availability/auth failure save progress and stop; no replay.
Tokens stay in memory, manual new consent, existing granted-scope validation,
renewal and revocation unchanged. Never log tokens, auth headers or native
encrypted reasoning. No credential persistence is enabled.

Both model/tool/native calls use real instrumented ROSA. Export to a new Phoenix
project and match exact span IDs with persisted server spans, with closed trees.
Local callback/native/LLM counters and usage records must agree. Trace/accounting
failure or an accepted unsupported success triggers an engineering stop after
saving the offending trial. Preflight validates scripted failure paths and an
actual Phoenix round-trip before any live generation.

## Independent scoring and attribution

Primary correct outcome requires: correct requested skill, truthful accepted
status/values, normal accepted-report termination within bounds, and physical
mock goal reached for healthy cases. Failure/UNKNOWN cases require their expected
truthful classification and appropriate no-write/no-replay behavior. An accepted
SUCCESS for the wrong selected skill can be locally verified yet fails user-goal
completion; record this separately. Reject unsupported report attempts, retaining
their raw classifications and claim-time truth/evidence in evaluator-only logs.

Report paired within-backend outcomes, healthy completion, correct fault handling,
invalid and unsupported attempts, feedback corrections, program assistance,
model calls, input/output usage (censoring explicit), latency and native/tool
operations. Fewer calls in a failed trial are not successful-task efficiency.
Program evidence and actions are not credited as unassisted model capability.

## Gate for further work

Feasibility validity requires all 24 attempts accounted for, matched persisted
traces and no silent budget/credential failure or unsupported accepted outcome.
For progression of this candidate: each backend's program condition completes
both healthy cases, has no paired outcome loss versus its reference on these
six cases, and introduces no unsafe dispatch/replay. A plausible efficiency
signal requires fewer calls on at least one jointly correct healthy pair without
more native operations. Report each backend separately; no significance claim.

A gate failure is documented, not tuned away by rerunning. Even a passing gate
does not authorize a large benchmark or physical deployment. A subsequent small
UR5e transfer protocol must be specified and bounded separately. Ambiguous goals,
broader tasks, macro-tool references and held-out evaluation remain future work.
