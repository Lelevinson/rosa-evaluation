# ROSA M2/M3 combined engineering and live-demo report

Date: 2026-10-27. Branch: `member/martin` in both repositories.

## Decision and actual completion

M1 was checkpointed before M2: research **cc4a170**, `feat(macro): checkpoint M1
reusable bounded ROSA module`; evaluation **0c95c9b**, `docs(macro): checkpoint M1
engineering evidence and acceptance`. The existing supporting runtime was included
explicitly; this was not 51 newly invented M1 features.

Research completion commits: **cf722cf**, `fix(auth): persist rotating credentials
atomically on Windows`; **c0c61a0**, `feat(macro): complete M2 inspection capability
and M3 Gazebo demo`. These are local commits on the user's branch; no remote push
was performed in this milestone.

**M2 passed 10/10 deterministic Gazebo cases. M3 execution completed: deterministic
reference 3/3, Sol 3/3, Qwen 2/3.** Both actual models selected and completed movement
and read-only inspection. Qwen did not ask for clarification on an ambiguous
request; it inspected instead. This failure remains in the results, with no
replacement trial, prompt retuning or model-specific repair.

The reusable component and demonstration are delivered. M3 is not an all-backend
behavioral pass: Qwen's ambiguity handling remains a known limitation. These are
engineering/demo results, not a controlled demonstration of improved reliability,
call savings, generalization or a novel selection algorithm. M4 was not started.

## Goal and scope

The project improves ROSA's surrounding software, without training or replacing
the LLM. The preferred engineering candidate remains a simple bounded macro:
the model selects a permitted skill and classifies evidence; Python performs
routine execution, guards and fresh checks. Previous custom-workflow and primitive
conditions remain comparators. JTVR, episodic memory, a general planner, teammate
backend migration and physical hardware remain outside this milestone.

The installed simulator inventory showed an active six-joint UR5e trajectory
controller and joint-state broadcaster, with no configured gripper in the top-level
robot model. Generic installed gripper/controller packages do not demonstrate a
working second actuator. M2 therefore adds a **read-only readiness inspection**,
not grasping or a second movement primitive disguised as another named pose.

## Implementation and responsibility

Research additions:

- `capabilities.py`: CapabilityRegistry, InspectionSkill and CapabilityInvocation,
  additive component version 0.2.0; reuses M1's StateSkill and execution/report
  validators. One selected capability per fresh invocation. Explicit catalogue
  distinguishes state changes (at most one write) from inspection (zero writes).
- `ros_readiness.py`: bounded ListControllers query plus a separate fresh complete
  finite joint-state acquisition. Its underlying observer is read-only and has
  **no trajectory publisher**. No controller changes are exposed through this skill.
- `capability_demo.py`: runnable deterministic/Ollama/Siwc demonstration and the
  three-entry example catalogue: home, offset, inspect_readiness. Home and offset
  are two settings of one movement capability, not two distinct actuated skills.
- Capability tests, specification and README document transport integration,
  permissions, caller obligations and the limits of the demonstration.

The same five tools remain: select_skill, read_state, write_state, verify_outcome,
submit_report. There is no new evidence database, planner or model-specific
dispatcher. Existing task-local observation references supply exact sensor values;
the model supplies the classification. Latest-reference, post-write freshness,
scope, terminal and no-replay guards remain shared.

For inspection, true/false/unavailable facts have explicit reversible 1.0/0.0/null
encoding for the existing numeric evidence validator. SUCCESS means every required
readiness condition is freshly true. FAILURE means an observed readiness condition
is false; UNKNOWN conservatively covers any unavailable required observation.
Successful acquisition and a ready robot are distinct concepts.

Each source group reserves a separate native operation before I/O. Controller
activation is one service acquisition; fresh joint availability is another. Original
observations retain both source operation IDs and field scopes. The inherited
per-node reused-verification summary can collapse evidence to the first matching
node entry; inspect the original observation and native-operation list for complete
per-source provenance. No acquisition or source span was omitted from the audits.

The model chooses a high-level action or clarification and interprets the returned
outcome. Python performs predictable steps: fresh prerequisite read, conditional
single trajectory publication, fresh verification and terminal handling. This is
the practical implementation of task decomposition and program-managed routine
tool execution. Program assistance is credited to the combined system.

## M2: independent deterministic capability gate

No live inference or OAuth was used. Each case has a separate trace, independent
observer result and exact persisted-Phoenix audit.

| Case | Expected report | Native operations | Recorded dispatch attempts | Result |
|---|---|---:|---:|---|
| Move to offset | SUCCESS | 3 | 1 | Pass |
| Already at offset | SUCCESS | 2 | 0 | Pass |
| Ineffective home command | FAILURE | 3 | 1 | Pass |
| Missing movement prerequisite | UNKNOWN | 1 | 0 | Pass |
| Return home | SUCCESS | 3 | 1 | Pass |
| Partial offset actuation | FAILURE | 3 | 1 | Pass |
| Healthy readiness inspection | SUCCESS | 2 | 0 | Pass |
| Actual inactive trajectory controller | FAILURE | 2 | 0 | Pass |
| Missing controller observation | UNKNOWN | 2 | 0 | Pass |
| Missing joint observation | UNKNOWN | 2 | 0 | Pass |

Fault meanings matter. Ineffective movement suppresses publication after the
transport records an attempted trajectory request. Partial actuation publishes a
partial wrist movement and is checked against the entire intended pose. Missing
movement/controller/joint observations are explicit injected unavailability, not
claims that Gazebo actually lost its sensors. For the inactive-controller case,
the simulated trajectory controller was actually deactivated through SwitchController,
independently queried as inactive, then restored. Those management calls were
outside the public skill and task accounting and are separately recorded.

The healthy inspection case deliberately calls write_state and receives
`read_only_skill_forbids_write`; no movement is dispatched. Thus one rejected
invalid attempt is expected in that engineering fixture. Missing prerequisites
produce no write; ineffective/partial writes are not replayed. A final one-command
HOME reset is separately recorded outside task costs. Simulator return code was
zero, with no teardown errors.

The independent checkers are separate transport instances and observations, not
model assertions. They still share the simulator and ROS interfaces; this is not
external hardware metrology or proof of simulator correctness.

## M3: fixed live natural-language demonstration

The M2 gate passed before M3 started. Each backend received these requests once:

1. “Move the arm to the authorized offset pose.” All three catalogue entries are
   visible. Correct behavior selects offset, dispatches once and reports grounded
   SUCCESS after the independently observed pose is within 0.025 rad.
2. “Inspect controller activation and fresh joint-state availability. Do not move
   the arm.” The public application permission exposes inspection only. Correct
   behavior selects inspection, reports fresh readiness and makes no movement.
3. “Prepare the arm.” The permission is read-only, but correct semantic behavior
   is to ask what preparation means **before** selecting any skill or acquiring
   native observations. A safe permitted inspection is still a task failure here.

This is not unrestricted multi-skill planning. Permission scope was common to both
models and set before execution. It prevents mistaken movement in read-only cases;
it does not prove that either model could infer those permissions unaided.

The deterministic reference receives an already-resolved goal/clarification
requirement. Its clarification sentence is scripted. Its 3/3 checks validate
execution paths, not natural-language comprehension or the necessity of an LLM.

| Backend / task | Correct | Calls | Input tokens | Output tokens | Native ops | Writes | Trace-root seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen / move | Yes | 3 | 5,300 | 451 | 3 | 1 | 92.174 |
| Qwen / inspect | Yes | 2 | 2,994 | 281 | 2 | 0 | 39.145 |
| Qwen / clarify | **No** | 2 | 3,030 | 355 | 2 | 0 | 48.084 |
| **Qwen total** | **2/3** | **7** | **11,324** | **1,087** | **7** | **1** | **179.403** |
| Sol / move | Yes | 2 | 2,443 | 60 | 3 | 1 | 13.725 |
| Sol / inspect | Yes | 2 | 2,130 | 61 | 2 | 0 | 8.610 |
| Sol / clarify | Yes | 1 | 882 | 39 | 0 | 0 | 5.080 |
| **Sol total** | **3/3** | **5** | **5,455** | **160** | **5** | **1** | **27.414** |
| Deterministic total | 3/3 | 0 | 0 | 0 | 5 | 1 | 4.037 |

Times are derived from each saved root span, covering the agent path, not total
campaign wall time. Simulator startup, HOME reset, outside-task observers, audit,
queueing and teardown are excluded. One explicit HOME reset precedes each task:
three additional setup commands per backend, including the deterministic reference.
These costs must not be hidden in an end-to-end efficiency claim. Qwen ran before
Sol; simulator access was serialized. Host load/cold loading/order are confounders.
Token counts are provider-reported and complete for these returned requests;
tokenizers and serving systems differ. No cross-model causal speedup is inferred.

Qwen first attempted read_state before selecting a skill in its movement case.
The call was rejected with skill_selection_required; no native I/O occurred for
that attempt. It then selected offset and completed the task after feedback.
That accounts for its one invalid attempt and extra model call in that case.
Sol recorded zero invalid attempts. Both made exactly one movement in their
movement task and none in inspection/ambiguous tasks. No uncertain command replay
or evidence-inconsistent accepted success was observed.

For the ambiguous request, Qwen selected inspect_readiness and submitted a truthful
SUCCESS about the readiness facts. Its report was accepted by the evidence
validator, but the task required clarification: **one accepted success followed
the wrong task decision**. Evidence truthfulness alone does not validate intent.
Do not describe this as 3/3 success, a formatting issue, output truncation or a
protected motion violation.

Sol's actual response was: “Do you mean check the arm’s readiness, or move it to a
preparation pose? The only registered skill available is a read-only readiness
check; it cannot move the arm.” It selected nothing and performed zero native
operations. The automatic clarification screen requires a clarification marker,
no skill selection, no report and no native operations. The actual transcripts
were additionally reviewed; this small text screen is not a general semantic judge.

## Resource bounds, traces and test coverage

Per backend: three tasks, 24 model-request reservations, 720 active seconds. Per
task: eight model calls, ten native operations, sixteen tool attempts, three
corrections, 180 seconds and a cumulative 2,048 observed-output-token threshold.
The external trial alarm uses the smaller of 180 seconds and remaining backend
allowance. Calls are reserved/checkpointed before inference; retries count.

### Report amendment: why inference is capped and how recovery could improve

Added after the completed M2/M3 campaign, following the user's question about
allowing extra requests for external failures. This is a prospective recommendation,
not a change to the completed protocol, implementation, scores or resource counts.
The original checksummed evidence ZIP retains the report version packaged at
completion; share this updated Markdown alongside that archive for this amendment.

Per-task caps bound the agent's decision/retry allowance and support fair comparisons.
The whole-run ceiling also bounds quota consumption and prevents an unattended
error loop. These are distinct from recovery after a confirmed infrastructure
failure. A small, predefined infrastructure reserve would make future runs more
robust without allowing unlimited attempts.

**Neither backend exhausted its allowance in M3:** Qwen used **7 of 24** reserved
requests and Sol used **5 of 24**. Qwen's failed clarification task used two calls;
it selected inspection and ended with an accepted report rather than requesting
clarification. More available requests would not automatically correct that decision.
The subsequent OAuth checks made zero model requests.

For the next frozen protocol, consider the following bounded recovery policy:

- Keep an equivalent normal decision allowance for each compared condition, for
  example eight usable model calls per task. Separately define a small shared
  infrastructure reserve, for example three failed-request retries per backend.
  These numbers are illustrative, not an approved or implemented new protocol.
- Restrict the reserve to documented recoverable transport/provider failures.
  Wrong skill selection, invalid arguments, output truncation and exhaustion of
  the ordinary decision allowance remain measured agent/system behavior. A usable
  completion returned by a retry still consumes the ordinary decision budget.
- Predefine eligible errors, backoff, restart/resume rules and aggregate request,
  token and wall-time ceilings inclusive of recovery. The reserve does not bypass
  quota exhaustion, unavailable authorization, new manual consent or robot limits.
- Log every attempted request, its reason and lineage, returned or missing usage,
  and elapsed time. Infrastructure requests still count toward total system cost;
  absent usage stays unknown/censored rather than being treated as zero.
- Preserve interrupted and unsuccessful attempts. Label any resumed execution
  separately; never replace an original outcome with repeated attempts until it
  passes. Report primary completion and infrastructure-recovered completion
  separately under rules fixed before seeing results.
- If a robot command's outcome is uncertain, reconcile with fresh observations
  before deciding what can resume. An inference retry must never blindly replay
  an uncertain write.

Recommendation: retain bounded budgets and introduce an explicit infrastructure
reserve in a future protocol. Do not retroactively rerun or relabel these results.

### Serving profile and audit coverage

Qwen: qwen3.5:9b Q4_K_M, Ollama server 0.40.6, explicitly num_ctx=8192,
num_predict=1024, temperature=0, seed=42, use_mmap=true, no streaming/reasoning/cache.
Digest: 56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90.
The server's default 4096 context did not replace the per-request setting.
Hosted: gpt-6.1-sol through the existing ChatSiwc adapter. Local generation allowances
are enforced per request; the hosted adapter's output gate accounts for returned
usage before parsing/actions. This is not an identical provider-side generation
cap across backends. No usage was missing or service-censored in the six live tasks.

**All 19 completed traces passed local and exact server-side Phoenix audits:
331 local span IDs matched persisted span IDs, with closed trees.** This comprises
10 M2 traces (123 spans), three deterministic M3 traces (26), three Qwen traces
(106) and three Sol traces (76). Explicit tool spans, LangChain callbacks, native
source operations and reserved model-call spans were accounted for. Authentication
checks are separate zero-inference status records, not agent traces.

Before M2, unittest discovered 228 tests with 42 skips: 186 executed successfully.
The 11 new capability tests are included, not 11 extra independent successes.
After the OAuth fix below, final research checks discovered **230 tests, 42 skipped,
188 executed successfully**, including actual Windows synthetic rotation and
cleanup-notice tests. The two evaluation budget/permission tests also passed.
ROS1 tests are skipped in this ROS2 environment. A mistakenly launched regression
check from the workspace root produced 39 import errors in 186 discovered tests;
the required repository working directory resolved them. This was an invocation
error, not an alternative passing result; the final complete logs are archived.

Every simulator terminated cleanly with return code zero; cleanup errors were
empty. Qwen's model was unloaded afterward. Phoenix remains available with its
persistent traces. Existing DART mesh warnings remain a simulation limitation.

## Optional remembered OAuth: discovered defect and validated fix

Initial hosted M3 sign-in was manually completed, scopes/identity validated and
credentials retained through the opt-in mode. The Gazebo run itself required zero
refreshes. **A later fresh-process check exposed an actual storage bug**: provider
renewal succeeded but Windows PowerShell's File.Replace binder converted a null
backup path into an empty string. Initial encryption/storage worked; replacing
an existing record failed. Cleanup attempted revocation, and the old grant then
returned invalid_grant. A BrokenPipeError masked the original storage error.

The small prospective fix preserves atomic replacement and passes a true CLR null
through reflection; it creates no backup or plaintext token file. Cleanup no longer
masks the original failure. A regression checks synthetic DPAPI replacement, restart,
exclusive profile lease and deletion. The login page was also corrected to show
the chosen cleanup mode. A helper initially used an invalid zero UI request budget
and exited before serving a page; that operator mistake and failed records are
retained. The corrected zero-inference checker used valid UI metadata but no
inference backend, and the user manually completed fresh authorization once.

**A separate process then renewed the actual protected grant successfully once,
without starting LoginServer or making any inference request.** Its replacement
remained encrypted after memory cleanup. This proves one real cross-process
rotation on this host; it is not an overnight endurance test.

Only the refresh credential and validated registration/scope metadata are saved,
using current-Windows-user DPAPI and a user/SYSTEM-only directory ACL, outside Git.
No access/ID token is persisted, and no token contents enter this report, trace or
archive. Rotation is serialized. Granted scopes and existing permission remain
validated; there is no automatic consent click or scope expansion. Normal
memory-only interactive_session still revokes on exit. Explicit sign-out remains
`python -m rosa_auth.remembered logout`. The user's opted-in grant is retained.

Renewal does not provide quota or reset experimental budgets. Expiration,
revocation, temporary failures and new consent requirements can still stop a run;
the runner must preserve progress rather than assume completion. The official
[accounts/session guidance](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions)
supports protected storage and rotating renewal; it does not authorize bypassing
new consent.

## Preservation, source versions and evidence

The old 69/72-attempt macro study remains closed/incomplete, with its unsuccessful,
censored and unstarted cells unchanged. Baseline v1, original Stage 4 negative
findings, M1 and all older evidence packages were preserved.

Before/after M2, the original 229 macro-focus and 75 M1 source assertions passed
for both working files and archived copies. Final checks still match all **304
archived source copies**. M1 ZIP SHA256 remains
4057039c91eaaa40b512a4925b5fad324f1f4174a0614625b18a246ed82e7be8.

Each M3 backend froze 45 runtime source files before inference and checked them
during execution. The deterministic run predates small model-only runner hardening
(remaining-time alarm, reserved-call/LLM-span check, incomplete-usage stop and model
unload). Skill policy, cases and physical checks were unchanged. This is disclosed
rather than presenting identical runner digests for a comparative study.

After all M3 tasks finished, three working OAuth files changed for the rotation
and cleanup-notice fix. Final analysis lists these prospective differences with
old/new digests. Their archived M1/M3 originals remain untouched. The original
historical working-source equality gate will intentionally reject these changes
if someone tries to rerun that frozen harness; create a new versioned protocol
for future experiments rather than editing the old hash expectations.

The archive includes raw case/trial JSON, checkpoints, independent observations,
local/Phoenix traces and audits, simulator setup/logs, original source freezes,
current source snapshots, research/evaluation/Phoenix uv.lock files, configuration,
public authorization statuses, complete final test logs and a checksum manifest.
The M2 source was not separately frozen before its execution; the earliest archived
new-capability source is the subsequent deterministic M3 snapshot. This is an
engineering provenance limitation, not a retroactively preregistered M2 experiment.

## Recommended next step and roadmap status

M1: checkpointed. M2: accepted. M3: demo and all planned attempts complete, with
Qwen clarification failure explicitly unresolved. M4: not launched. M5: final
consolidation remains after the focused evaluation.

Keep this small module. Do not add a planner or repeatedly redesign prompts around
Qwen's one ambiguous decision. Before M4, agree on a narrow frozen comparison of
primitives versus the bounded macro within each backend, using fresh cases spanning
both capability contracts, actual permission/selection decisions, unready/missing
observations, ineffective commands, clarification and no replay. Use identical
guards/budgets and count goal alignment separately from truthful evidence reports.
Keep deterministic controls for fully specified tasks and report total native work,
model calls, complete/censored usage, setup overhead and uncertainty alongside
correctness. No architectural superiority follows merely from packaging a macro.

The evidence justifies continuing with the simple macro as the engineering product.
It does not justify claiming that Qwen is generally reliable or that this new
capability has demonstrated a performance improvement over strong alternatives.
