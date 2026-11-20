# Fresh macro-skill comparison candidate — not frozen, no live requests

Prerequisite: the separate prompt-contract live validation must satisfy its
frozen engineering AND progression gates. This document does not bypass them.
Keep the engineering/live validation reports separate from this proposed pilot;
combine the reports for discussion after the applicable work finishes.

## Narrow question

With the common prompt repair, does a straightforward bundled ROSA skill retain
verified reliability while reducing inference calls relative to the controlled
primitive reference? Does the existing workflow add a useful advantage over the
macro? These compare complete orchestration arrangements, not a novel selection
algorithm or a claim to have improved the model itself.

Only one underlying capability is implemented: bounded six-joint UR5e pose
execution with read-only observation and validated reporting. Four permitted
pose choices are not four distinct robot capabilities. An observation-only
inspection task needs a different success/permission contract; it is deferred
instead of being disguised as another pose or added through a general planner.

## Fresh cases and pairing

The proposed design module defines a NEW four-pose near-home catalog and six
cases: return home from a nonhome starting pose; maintain an already-achieved
nonhome goal; select a pose satisfying three simultaneous user constraints;
recover a transient prerequisite-read failure before motion; exercise actual
partial actuation and report FAILURE without replay; and handle persistent
post-motion observation loss with UNKNOWN despite command acceptance.

These are prospective new cases within a deliberately small domain, not a
claim of broad unseen-task generalization. Policy code stays unchanged and
receives no private fault, expected-status or correct-skill labels. Case/scorer
development uses only deterministic fixtures. The model still chooses the skill,
responds to escalations and classifies its final evidence. The program never
uses the independent observer to repair a model decision.

Six cases x2 repetitions x3 conditions x2 backends =72 live trials. Each backend
has twelve paired case/repetition groups. Conditions: model-managed primitives,
straight-line guarded macro, existing program-managed workflow. Each condition
occupies each ordinal position four times/backend. Repetition2 changes case and
condition order. No adaptive ordering, optional stopping for favorable scores,
prompt edits, failed-trial replacement, or model replacement during the pilot.

## Shared contract and budgets

Same five tools, common repaired system prefix, catalog, permissions, controller,
report-reference checks, accepted-report termination, truncation handling and
independent scorer in all conditions. Macro/workflow task prompts and schemas
are identical. Bundle-native steps and errors count against the same ceilings.
No JTVR, caching, memory, general planner, retries added by the framework or
command replay. Program actions are credited to the combined system.

Serving profiles remain those of the frozen live validation: Qwen3.5:9b Q4_K_M,
Ollama0.40.6, context8192, per-call output<=1024, temp0/seed42, no reasoning,
streaming or cache; hosted gpt-6.1-sol through the current OAuth adapter.
Per trial:8 calls,180 seconds,16 tool attempts,10 native operations,3 invalid
corrections,1 dispatched write,2048 generated-output observed threshold.
The hosted threshold can overshoot on the final returned generation; account
for the actual usage before withholding tools. No finite cost is invented for
unreturned hosted inference. Each backend:288 requests,4500 active seconds.
If time expires, retain all outcomes and classify the remaining cells unstarted.
No extra retries or continuation after truncation. All extra work is metered.

All conditions use the separately validated simulator-home setup: a generated
copy of the installed top-level Xacro adds only the documented HOME positions
to the existing initial_positions macro parameter. No geometry, controller or
tolerance edits. Three independent cold starts and18 deterministic controls
passed before use; source proof is retained. Earlier live validation's R1 setup
abort and R2 setup amendment remain visible in the evidence lineage. Physics
mesh-collision warnings are a limitation; this study verifies joint outcomes
and does not validate collision avoidance.

Gazebo access is serialized; startup/readiness, independent resets and six
resolved-goal deterministic controls/backend are outside trial costs and
recorded separately. Initial-pose setup is verified by a separate read-only
observer. The actor sees only its own task observation stream. This is simulation
in the existing near-home envelope, with no collision/path-safety or physical
robot claim. Cold local model loading may affect the first trial's latency;
report it and include a prespecified latency sensitivity excluding the first
case/repetition group, alongside the complete primary totals.

## Prospective scoring and measurements

Primary correct outcome requires: correct user-constrained skill; accepted
evidence-backed report with expected status; independent physical agreement for
known values; required correct command attempted exactly as specified; injected
fault actually exercised; normal terminal handling; no unauthorized/replayed
command; and task retry-policy compliance. For an unavailable observation,
one further acquisition is allowed in that unavailability episode, including
bundled acquisitions. More than one extra acquisition fails the new policy
contract but is separately distinguished from an unsafe dispatch. Existing old
scores did not enforce this soft guidance; they remain unchanged.

UNKNOWN may be a correct report even when the private observer knows the goal
was reached. The fresh scorer explicitly distinguishes unavailable actor
evidence from private physical truth. SUCCESS cannot be supported by unknown,
stale, cross-session or pre-write evidence. For partial motion, merely declaring
failure without attempting the correct command fails coverage. For persistent
post-motion loss, attempting the correct movement and exercising the observation
failure are both required. No outcome is inferred for unstarted cells.

Report per backend/condition: correct outcomes; individual failure modes;
selection/report correctness; fault and dispatch coverage; model calls; known
input/output tokens and censored costs; total trial latency; native and bundled
operations; invalid attempts; feedback corrections; unsupported success attempts
and accepted claims; read-only recovery attempts; and all audit/limit results.
Save actual model inputs, tool transcripts, inference metadata, actor ownership,
independent goal/claim-time oracles, exact local/Phoenix spans and atomic progress.

## Prespecified retention screen

This is a small feasibility/retention screen, not a powered confirmatory study.
For a packaged condition versus primitives, require no pair on either backend
where the packaged condition fails and the primitive condition passes, and
at least20% fewer calls per backend on pairs where both
conditions are correct. Report all-attempt costs too; early failures are not
efficiency gains. Require no additional unsupported accepted success or unsafe
dispatch; native operations must not increase by more than20% on matched-correct
pairs. If matched-correct pairs are fewer than6/backend, label the screen
inconclusive. Show paired counts and uncertainty; do not infer backend-wide or
task-wide generalization from twelve groups.

To retain workflow over the simple macro, require no reliability loss on either
backend, at least10% fewer calls on matched-correct pairs for at least one backend,
no call increase on the other, no native-operation increase and no more than10%
trial-latency increase on matched-correct pairs. Require at least6 matched-correct
pairs/backend. Repetitions share six case templates; report per-case repetition
ranges and discordant pairs without treating them as a random sample from all
robotics tasks or claiming statistical significance. Otherwise prefer macro if its primitive-reference screen passes;
if neither passes, preserve the simpler reference and document the limitation.
Do not relax thresholds after seeing results. Latency/token/native totals remain
visible even if the call screen passes; passing is not a claim of universal
overall efficiency.

## Stops, evidence and authorization

Before any inference: freeze protocol, exact schedule, code/source copies,
dependency locks, model profiles, prior validation evidence digests and control
expectations. Then run fresh deterministic controls. Every completed attempt
needs exact Phoenix server-side span matching, actual-input conformance and
limits/usage accounting. Any audit failure, unsupported accepted SELECTED-goal success,
unauthorized/replayed command, changed frozen source or controller failure stops
the batch; normal task failures continue unchanged. An authorized but wrongly
selected user goal is a task/selection failure, recorded separately from an
unsupported selected-goal claim or unauthorized dispatch. Authorization/service/quota
loss saves current evidence, records uncertainty and stops without automatic
replay. Resumption requires a separately reviewed continuation plan that retains
all completed successes and failures.

Manual initial OAuth consent, validated scopes, memory-only renewable tokens and
normal revocation remain mandatory. No migration to the parked team package and
no credential persistence. The live validation's72-request authorization does
not authorize this pilot's separate288-request hosted batch.
