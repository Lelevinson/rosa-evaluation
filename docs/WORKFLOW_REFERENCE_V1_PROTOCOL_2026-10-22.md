# Common observation-reference reporting and small Gazebo transfer

Prospective engineering/integration milestone. Preserve the failed workflow
live v1 Qwen gate and all older results. No rescores or silently replaced trials.
No model training, general planner, memory subsystem, JTVR or physical robot.

## Minimal common change

submit_report takes status and the latest observation_id. Existing session
observations receive task-local IDs; exact node identifiers/values come from
that stored observation. No extra sensor reads or new evidence database.
The existing freshness/classification checks remain authoritative. IDs from
another task, older reads or before any attempted write are rejected. Missing
evidence supports UNKNOWN, never SUCCESS. Software-supplied values are explicitly
credited to ROSA, while the model supplies outcome classification in both arms.
Task-local opaque IDs and timestamps vary across runs and remain in raw evidence.

Model-managed and program-managed conditions receive identical report tools,
catalogue, permissions, primitive capabilities and budgets. Only routine
orchestration differs, as in v1; select_skill macro semantics remain a bundled
system-level intervention. This is not an isolated causal test of reporting
changes versus the earlier differently configured/cased pilot.

## Sequence and frozen gate

1. Focused contract tests: valid truthful reports, stale/foreign/unknown IDs,
   failed-write invalidation, wrong classification and missing observations.
2. Preflight actual ROSA scripted paths and exact persisted Phoenix matching.
3. Four deterministic Gazebo controls with two six-joint poses, suppressed
   command and missing observation. No LLM calls. Repeat those controls after
   each live simulator startup before model-driven trials.
4. Fresh live mock validation: four cases x two arms x two backends = 16 trials.
   Cases: north healthy, south healthy, north no-effect, south no-observation.
   Require ALL 16 independently correct outcomes and complete audits. Otherwise
   terminate both pipelines, revoke OAuth and do NOT proceed to Gazebo. Do not
   redesign around another unrelated Qwen failure during this frozen campaign.
5. Only if the common validation gate passes: four analogous UR5e cases x two
   arms x two backends = 16 Gazebo trials, serialized to avoid simulator resource
   interference. Controllers/domain/partition are isolated, home reset independently
   verified before each trial, then task fault injected. No task command replay.

The new mock node/targets and Gazebo poses differ from previous live trials.
This remains a small development-informed feasibility test with one repetition
per cell, not a held-out benchmark or statistical proof.

## Bounds, authentication and observability

Each trial: 8 model calls, 16 tool attempts including program work, 10 native
operations, 3 invalid corrections, one dispatched write, 180-second external
timeout. Each phase/backend: 64 calls and 2700 active seconds. Both phases per
backend: 128 calls maximum. Gate/serialization waits each bounded at 2700 seconds;
OAuth consent wait 1800 seconds. All waiting is outside scored trial time.

Qwen unchanged serving: pinned Qwen3.5:9b Q4_K_M digest, ctx8192, temperature0,
seed42, thinking off, mmap on, per-call1024 clamped to remaining2048 output.
Sol unchanged official ChatSiwc/account settings, with observed cumulative2048
output threshold before further tool execution; this is NOT a hard generation
cap. Usage on failed hosted generations remains unknown, not fabricated. Compare
conditions within backend; do not claim equal cross-backend token allowances.

No automatic inference retries/truncation continuation. Record every generation,
input/output usage, invalid attempts, reports, program assistance and native
operations. SIGALRM bounds whole trials; native transport calls are independently
bounded. Local timeout triggers model unload before continuing. Auth/quota loss,
trace gaps, accounting errors or accepted unsupported success checkpoint and stop.

Manual new OAuth consent stays required; reuse memory-only authorized renewal
for the same bounded pipeline. No changed scopes, credential persistence or
weaker cleanup. Session revoked after pipeline completion/failure. ROSA/LLM traces
exclude access/refresh tokens and encrypted native reasoning.

Export real spans to the new reference-v1 Phoenix project and match exact IDs
with closed persisted trees. Independent evaluator uses a separate read-only
joint-state subscriber in Gazebo; its observations are never available to the
agent/workflow. Observer/reset/control operations are logged separately from
agent-budget operations; no hidden free verification is credited to the agent.

## Interpretation and next milestone

Primary correct: right selected skill, truthful accepted outcome, normal terminal
return within budgets, independent goal attainment for healthy tasks; correct
FAILURE/UNKNOWN and no unsafe dispatch/replay for injected fault cases. Gazebo
tolerance .025 rad per joint; mock tolerance .01. Verification covers joint-state
outcomes, not collision avoidance, grasping or physical-robot safety.

Report each backend/phase/arm separately: correct outcomes, healthy completion,
invalid/unsupported attempts, feedback corrections, model calls, tokens, native
operations, latency and escalation. Native overhead can increase despite fewer
inferences. Preserve failures as limitations; no automatic new architecture.

Before a larger research experiment, add a strong model-managed macro-skill
reference and held-out tasks/repetitions. That comparison is not required merely
to establish this small Gazebo integration. No large campaign is launched here.
