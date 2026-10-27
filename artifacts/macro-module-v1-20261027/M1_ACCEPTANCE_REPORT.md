# M1 complete: reusable bounded macro prototype 0.1.0

Date: 2026-10-27, Asia/Taipei. This is engineering acceptance, not a new live
model-performance experiment. Live Qwen requests: **0**. Live hosted requests:
**0**. No new browser authorization or real credential was used.

The numeric-state macro is now importable and usable without copying an
experiment runner. M1 stops here; the second capability, new demonstration
campaign and final model comparison have not started. Optional protected OAuth
persistence was implemented separately at the user's explicit request.

## Deliverables and responsibilities

Research code:

- `rosa-research/src/rosa_reliability/bounded_macro.py`: public `StateSkill`,
  `SkillRegistry`, `MacroLimits`, `MacroInvocation`, internal version 0.1.0.
- `macro_agent.py`: public `MacroROSA`, inference limits and usage gate using
  the existing common prompt, pre-parser and accepted-terminal seams.
- `macro_demo.py`: runnable deterministic in-memory example with failure modes.
- `gazebo_demo.py` and `ur5e_macro_demo.py`: research-side simulator lifecycle
  and seven-case example, with no experiment-package import.
- `rosa-research/docs/MACRO_MODULE_V1_SPEC.md` and
  `MACRO_MODULE_V1_README.md`: contract, install/API/examples and limitations.

The application registers allowed fixed target parameters. The model selects an
authorized ID, handles unresolved decisions and classifies evidence. Python owns
routine bundled execution. Transport supplies bounded native I/O. Independent
experimental scoring stays outside the module. No private fault/answer label is
passed into the core policy. The core has no hard-coded UR5e node or pose name.

This first version intentionally supports **one selected single-node numeric
state skill per fresh invocation**, at most one dispatched write. Multiple IDs
test routing; they do not establish distinct robot capabilities. Target arguments
are bound by trusted application code at registration. This is not a generic
arbitrary-callback skill framework or an autonomous planner.

Existing `MacroSession -> ReferenceWorkflowSession -> WorkflowSession` inheritance
is reused, not deleted. Historical modules, prompt repair, controller transport,
reporting and terminal implementations are unchanged. New opt-in entry validation
rejects incomplete/changed target writes and unknown prerequisite state even if
a custom transport lacks its own prerequisite flag. It also rejects malformed
budget objects rather than silently accepting a default and blocks tools/reports
after the task deadline. Model returns after the deadline are metered and withheld
before tool parsing.

## M1 acceptance checklist

| Requirement | Status | Evidence / qualification |
|---|---|---|
| Import/register without copying a runner | PASS | Public registry and wheel installed into an empty target; `package-03/result.json`. |
| Same API with scripted and Gazebo transport | PASS | `scripted-03/result.json`; `gazebo-01/result.json`. |
| Two IDs resolve without fixed target selection | PASS | Unit routing tests, left/right demo IDs and home/offset Gazebo IDs. These are pose alternatives, not two capabilities. |
| Unauthorized/malformed arguments rejected before dispatch | PASS | Unknown IDs, extra arguments, invalid target registration, changed/incomplete writes, malformed budgets and permission-copy isolation tested. |
| Already-at-goal does not write | PASS | Unit tests and Gazebo already-home/already-offset checks; fresh reads retained. |
| Missing prerequisite state prevents writes | PASS | Both public execution modes tested; Gazebo missing-before-home produced UNKNOWN with zero dispatches. |
| Ineffective/partial actuation is not verified success | PASS | Scripted and Gazebo FAILURE outcomes; unsupported SUCCESS classification rejected in unit tests. |
| Uncertain receipt cannot replay | PASS | Synthetic write applies an effect then raises; further macro selection/write is blocked. No real uncertain controller receipt was induced. |
| Evidence is task-scoped and invalidated after applicable writes | PASS | Stale, cross-task, failed-partial-write and unknown reference tests. Fresh physical acquisition remains an adapter responsibility. |
| Report correction and deterministic terminal handling | PASS | Actual ROSA executor, both real adapter classes with fake transports; wrong report corrected, accepted report ends without another model call. |
| Native/tool/correction/time/model limits and attribution | PASS within documented boundary | Pre-dispatch reservations, deadline withholding, output/call limits, unknown usage and batch callback tested. External cancellation remains caller/transport responsibility. |
| Regression and trace checks | PASS | `offline-04`: 276 passing regression test executions; final 36 focused test methods, including three subsequently added simulator-helper methods. These counts overlap and must not be summed. `offline-05` confirms final malformed-budget assertions. |
| Installation and examples in supported dependency environment | PASS | Offline wheel build/install in empty target, isolated imports verified from installed wheel, in-memory execution and real Gazebo module example. Existing pinned dependencies reused. |
| Entirely fresh OS/ROS/dependency installation | NOT YET TESTED | Not claimed by the clean-target wheel check; no dependency installation/migration required in M1. |
| Historical source/protocol/score preservation | PASS | Prior campaign `verify_freeze()` checks before/after scripted and Gazebo work and again during packaging of evidence. Old study remains 69/72, no continuation. |
| New live Qwen/Sol behavior after packaging | NOT YET TESTED | Only adapter-contract/fake-provider checks; no new performance conclusion. |
| Genuinely different second capability | NOT YET TESTED | M2 only; do not count the two registered poses as completion. |

No unresolved FAIL remains within the declared M1 scope. Preserved development
failures below are evidence of repairs, not silently removed attempts.

## Validation details

Final focused suites: 14 public macro methods, 7 agent/inference methods,
3 simulator-description/freshness methods, and 12 remembered-auth methods:
**36/36 passed**. Both actual adapter classes were exercised with mocked native
transports in macro and primitive modes. They retained the five-tool contract,
Ollama context/temperature/seed/mmap options, usage accounting and immediate
terminal behavior. This does not show that live models make identical decisions.

The final scripted validation has **12/12** passing paths: six fixtures in each
condition. Original local audits pass, and **543/543** local spans match actual
persisted Phoenix span IDs with closed trees. Fixture answers are scripted and
not credited as learned model behavior.

The headless UR5e example has **7/7** deterministic checks passing:

| Case | Report | Dispatched writes |
|---|---|---:|
| Already home | SUCCESS | 0 |
| Move to offset | SUCCESS | 1 |
| Already at offset | SUCCESS | 0 |
| Ineffective return home | FAILURE | 1 |
| Missing prerequisite before return | UNKNOWN | 0 |
| Return home | SUCCESS | 1 |
| Partial offset movement | FAILURE | 1 |

Separate read-only ROS contexts/subscriptions checked physical outcomes. These
checks did not supply the caller's classification or authorize writes. In-session
native operations: 17. Explicit tool spans and LangChain tool callbacks: 31 each.
**87/87** actual persisted Phoenix spans match, with a closed tree. Final HOME
reset is explicitly outside invocation accounting (one additional command), and
the simulator exited normally with return code 0. No geometry, controller,
tolerance or installed simulator package was edited. Existing mesh-collision
warnings remain: this verifies joint outcomes, not collision/path safety.

The final wheel is `package-03/jpl_rosa-1.0.10-py3-none-any.whl`. The parent
distribution retains its existing version; the new opt-in component documents
internal research-prototype version **0.1.0**. The wheel is not published. Both
ROSA and the public module were asserted to import from the empty installed
target rather than the editable checkout. Current dependencies are Python
3.12.3, LangChain 0.3.30, langchain-core 0.3.86, Pydantic 2.14.1 and
langchain-ollama 0.3.10, with original lockfile captured.

## Optional remembered authorization: separate maintenance result

The user explicitly selected secure persistence across restarts and explicit
sign-out. New opt-in files are `rosa_auth/protected_store.py` and `remembered.py`.
Existing `interactive_session`, `MemorySession`, `ChatSiwc`, all frozen runners
and their normal memory-only revoke-on-exit behavior are unchanged.

The protected mode reuses existing identity/scope checks and refresh protocol.
It stores only the refresh credential plus registration/grant metadata using
Windows-current-user DPAPI under `%LOCALAPPDATA%\ROSAResearch\OAuth`, outside Git
and experiment artifacts. Directory permissions restrict access to the Windows
user and SYSTEM. An exclusive Windows profile lease prevents concurrent rotation
in the supported Windows/WSL logon session. Atomic replacement follows refresh;
metadata is pinned to the existing account/client/host; scope changes stop use.
Access/ID tokens are not persisted. No secrets enter command arguments or logs.

Initial authorization remains manual. Routine resume refreshes without a browser.
Revocation/terminal refresh failures stop without automatically requesting consent;
temporary errors preserve the protected grant. Sign-out attempts remote revocation,
clears the local record and reports an unconfirmed remote result explicitly.
Fresh authorization never resets inference or execution budgets.

All 12 synthetic protocol tests passed. An **actual Windows DPAPI round trip and
concurrent-profile exclusion test passed**, using a dedicated dummy profile that
was deleted afterward. **Real-provider persistent login/resume remains NOT YET
TESTED.** No real remembered grant has been provisioned. A future hosted run needs
one initial manual sign-in and must explicitly use `remembered_session`; revoked
historical sessions cannot be recovered. This feature does not auto-click approval
or transparently modify historical experiments.

Instructions and explicit login/status/logout commands:
`rosa-research/docs/REMEMBERED_CHATGPT_AUTH.md`.

## Preserved development failures

- `offline-01` and `offline-02`: fake Ollama transport returned one response object
  when the adapter requested an iterable stream. Two adapter subcases failed.
  The fixture was corrected; the production adapter and auditor were not weakened.
- `scripted-01`: Phoenix was not running; export/persisted audit failed. Failure
  was retained, existing loopback service restarted with its original storage,
  then `scripted-02` and finalized `scripted-03` passed.
- `package-01`: non-login shell lacked uv on PATH. The runner was changed to use
  the already-installed uv executable's absolute path. `package-02` passed;
  `package-03` rebuilt the final input-validation revision and also passed.

These were engineering attempts, not failed live model trials. They are not
pooled into or substituted for any historical benchmark outcomes.

## M2 handoff and project limits

The observed simulator has active `joint_trajectory_controller` and
`joint_state_broadcaster`. MoveIt and generic gripper-controller software are
installed, but the top-level model has no gripper reference and no functioning
gripper was demonstrated. Installed software is not evidence of a configured
second actuator, perception stack or validated collision planner.

The smallest grounded M2 candidate is a **read-only arm/controller-readiness
inspection skill**, with its own permissions and truthful known/unavailable
outcome contract. It can distinguish an inspection request from a movement
request without installing new robot hardware. It must be labeled read-only,
not grasping or second-actuator support. Implementing it requires a small explicit
capability-contract extension; numeric pose IDs alone do not already provide it.
If the team requires gripper actuation, investigate the actual model/controller
integration separately before committing to that larger scope.

Next milestone is M2 only after reviewing this handoff. No M2 implementation,
live performance study, planner, episodic memory, JTVR, teammate-adapter migration
or physical robot deployment was launched.

Both repositories remain on `member/martin`. Substantial pre-existing dirty work
is preserved. No staging/commit/push was performed in M1; source snapshots and
digests, not the old Git HEAD alone, identify this working implementation.

Evidence is finalized by `experiments.macro_module_v1.finalize`: source and lock
snapshots, source manifest, original failed attempts, final checks, deterministic
observations, exact Phoenix span copies, wheel and checksummed ZIP. The final
archive excludes credentials and does not overwrite earlier evidence packages.
