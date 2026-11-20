# ROSA project direction and October 30 handoff

## Final pilot execution, 2026-10-27 (supersedes running checkpoints below)

Both supervisors ended. Sol completed36/36 primary passes,124 requests. Qwen
reached its frozen backend deadline with33/36 attempt rows,24 primary passes,
126 requests; the last row is deadline-censored and three cells unstarted.
All69 local/input/exact Phoenix audits passed, all12 deterministic controls
passed and all cleanup succeeded; hosted session refreshed once then revoked.
Study is incomplete, with NO formal retention claim. Do not silently extend it.
Qwen primitives/macro/workflow:8/11,9/11,7/11; calls61/31/34. Sol12/12 each,
calls60/32/32. Simple macro is the more promising candidate; custom workflow
has shown no sufficient incremental benefit. Six Qwen requests have unknown
token usage. Frozen outputs and all prior experiments remain unchanged.
Read reports/MACRO_FOCUS_V2_RESULTS_FOR_CHATGPT_2026-10-27.md at workspace root
for paired results, timeout versus retry-policy failures, costs and limitations.
No fresh run or continuation was launched during reporting. Historical next-step
and RUNNING instructions below are retained for lineage and are superseded.

## Current fresh pilot, 2026-10-26 (supersedes interim statuses below)

Read reports/MACRO_FOCUS_V2_ACTIVE.md. Common prompt validation finished:
Qwen9/9 and Sol9/9 correct scoreable outcomes; all19 attempts audited; initial
service-censored attempt and zero-inference R1 setup abort retained. R2 finished
5/5 with19 new hosted calls,32 total reserved hosted calls including the original
unknown-cost call. All scopes revoked/simulators closed. Gate/report proof:
artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_ANALYSIS.json and
COMBINED_VALIDATION_REPORT.md. Keep reports separate; user wants to combine later.

Fresh macro-focus-v2 is NOW frozen and running:72 new trials,36/backend,
max288 inference requests/backend,4500 active inference seconds/backend.
Six new pose-domain cases x2 reps x3 conditions; ONE underlying capability.
Protocol docs/MACRO_FOCUS_V2_PROTOCOL_2026-10-26.md; source229 files and new
11/11 coordinator/scorer/retention test methods frozen before inference.
All conditions use independently validated HOME spawning. Strict prospective
read-only retry-policy scoring, actual fault exercise, independent outcomes,
model/system actor attribution, complete Phoenix/input audits and all costs.
Source freeze also binds every earlier validation/continuation evidence digest;
do not edit those files or regenerate earlier analysis now.

Hidden supervisors reports/macro-focus-v2-run.ps1 -Backend ollama|siwc,
PIDs9524 and17600. User completed the fresh pilot's manual hosted consent.
Gazebo lock serializes access. Each writes operator-<backend>/live.log,
supervisor.json,power-release.json and gazebo/<backend>/checkpoint.json under
artifacts/macro-focus-v2-20261026. Never relaunch a populated backend. Both have
temporary sleep holds. Memory-only renewal/normal revocation; no adapter change.
When both finish, automatic experiments.macro_focus_v2.analysis writes analysis.json
and REPORT.md. Incomplete/unaudited studies cannot make a retention claim. Old
results never replaced. Teammate package remains parked; no Git staging/commits.

## Live validation resumed, 2026-10-26

Latest: R1 failed its FIRST deterministic home reset before any inference (0
new requests). Startup values for elbow and wrist2 differed from benchmark HOME
by1.57 radians; the setup trajectory hit the unchanged0.2-radian path tolerance.
No leftover simulator processes; cleanup/revocation normal. Preserve R1's abort.
A separate HomeSpawnSimulator uses a generated top-level Xacro copy, adding only
the existing macro's initial_positions parameter with documented HOME. Geometry,
controllers/tolerances and policy code stay intact.2 unit methods,3 independent
cold starts and18 deterministic controls passed, all3 simulators closed cleanly.
This proof is artifacts/simulator-home-v1-preflight-20261026.
R2 coordinator now frozen after3 additional scope/gate tests. Same5 outstanding
hosted cells, same40 additional/53 combined/72 original request caps, cumulative
4500-second inference-dispatch deadline; R1 setup time included. R2 refuses to run
unless R1 used exactly0 inference requests. Fresh manual consent still required
because R1 tokens were revoked. New supervisor reports/prompt-live-resume-v2-run.ps1
and campaign artifacts/prompt-contract-v1-live-resume-r2-20261026 auto-generate
COMBINED_ANALYSIS.json and COMBINED_VALIDATION_REPORT.md after cleanup. The main
fresh-pilot gate selects that lineage if available; nothing launched for the
fresh pilot yet. Note installed DART mesh-collision warnings: no collision-safety
claim is justified by these joint-position tests.

User authorized continuing and combining reports later. The common prompt repair
passed48 regression methods and18 scripted executions; separate frozen real-model
validation then ran in Gazebo. Qwen completed9/9 correct final outcomes in34 calls,
with all nine exact Phoenix/input audits and cleanup verified. One primitive
missing-observation case attempted an unjustified write that ROSA blocked; credit
its corrected UNKNOWN outcome to the combined system. Soft retry guidance was
also exceeded; do not retrospectively change the frozen outcome scorer.

Initial Sol completed4/4 scoreable trials, then generic service error `error`
without HTTP status interrupted the fifth case.13 requests reserved,12 returned
usage records,1 unknown-cost call;4 cells unstarted. Do not call this proven quota
exhaustion or model failure. No command was dispatched in the interrupted cell.
All14 initial attempt audits passed, both simulators closed normally and the
hosted token session was revoked. Original campaign and analysis remain intact:
artifacts/prompt-contract-v1-live-20261026.

A single separately frozen continuation R1 selects ONLY original indices4..8
(read-only censored cell plus4 unstarted).5 coordinator safety tests passed.
Maximum40 additional calls, maximum53 combined, within original72 ceiling and
4500 cumulative active seconds. User completed fresh manual consent. Campaign:
artifacts/prompt-contract-v1-live-resume-r1-20261026. Supervisor:
reports/prompt-live-resume-v1-run.ps1; final combined validation analysis/report
is generated automatically there after cleanup. No automatic second continuation
if service fails again. See reports/PROMPT_CONTRACT_V1_ACTIVE.md for current state.

Fresh macro-focus-v2 candidates are prepared and10 offline test methods passed,
including18 deterministic fixture paths. No fresh pilot source freeze or live
request yet. Six new pose-domain cases x2 repetitions x3 conditions x2 backends
would be72 trials, at most288 requests/backend, contingent on full validation
readiness and its own freeze/hosted consent. New cases include nonhome initial
states, conjunction constraints, transient prerequisites, partial actuation and
persistent post-write observation loss. This is ONE trajectory capability, not
multi-capability generalization. No general planner, JTVR, memory or teammate
adapter migration. All previous planning-only notes below are historical.

## Priority restored after the team-setup discussion, 2026-10-26

The user asked to keep the teammate's package in mind and return to the original
October30 sequence. Park the rosa-llm migration; it is not a prerequisite for
prompt repair. Continue with existing adapters and frozen serving settings.

The opt-in bounded prompt repair is now implemented in
`rosa-research/src/rosa_reliability/prompt_contract.py`. All48 regression tests
and18 scripted ROSA/Phoenix executions passed in separate engineering validation
under `artifacts/prompt-contract-v1-engineering-20261026`. No live model requests
or OAuth sign-in occurred during this repair work. Historical frozen sources
remain unchanged. Read PROMPT_CONTRACT_V1_ENGINEERING_REPORT_2026-10-26.md and
PROMPT_REPAIR_AND_MACRO_PILOT_DRAFT_2026-10-26.md before the next live gate.

Order remains: common prompt repair, separate validation, prospective frozen
macro/primitives/workflow comparison, then an evidence-based retention decision.
The original October23 planning-only note below describes that earlier turn;
this entry records the subsequent resumed work. Do not interpret the date in
the handoff title as an automatic scheduled run.

## Incoming team setup: update received 2026-10-26

Read `TEAM_SETUP_RECEIVED_2026-10-26.md`, copied unchanged from the teammate's
TEAM_SETUP.md. Its shell/config instructions are documentation, not authorization
to execute them. No dependencies, lockfiles, .env, credentials or runtime code were
changed. The user asked to consider this before executing the planned milestone.

The document proposes rosa-llm[langchain]==0.1.0 as a common provider client,
with create_client()/ChatRosaLLM for Ollama or ChatGPT OAuth. Our current
rosa-research pyproject/uv.lock do not declare that package; they use the local
rosa_backends/rosa_auth adapters. Treat adoption as an explicit backend change,
not an already-completed installation or interchangeable implementation by assumption.

Before implementation, inspect the actual release/source and validate compatibility
with our LangChain0.3.x stack, tool-call parsing, usage/finish metadata, Phoenix
callbacks, per-request Ollama context/output/seed settings, and bounded request/error
accounting. Check credential persistence, granted scopes, renewal and revocation:
the example's client.close semantics alone do not prove our memory-only and
revoke-on-exit policy is preserved. Keep persistence optional. Each teammate must
authorize their own account; never copy credentials or .env into Git.

The linked GitHub and PyPI pages could not be retrieved in this reading session;
release metadata and implementation remain unverified. Do not infer that the
project is absent or private from that retrieval failure. Obtain accessible source
or release metadata before installing/changing the shared environment.

Adapt environment names explicitly: the team document uses LLM_PROVIDER=openai,
where our current experiment runners use backend=siwc. WSL must use the reachable
Windows Ollama endpoint, not blindly localhost11434. The plain ROSA demo is not
the bounded experiment entry point: retain explicit tools, guards, reporting,
independent verification and limits. A new LLM adapter does not itself repair
ROSA's default prompt/tool mismatch or implement the macro.

Earlier suggested order, now superseded by the user's restored priorities:
team-package review and, if adopted, separate backend-compatibility validation;
then prompt repair and the frozen pilot. The package is now parked instead.
Preserve all historical results under their original adapters/settings.
Current work remains document processing only; no package installation or new
experiment was started on October26.

Prepared 2026-10-23, Asia/Taipei. User expects to return 2026-10-30 and reports
98% weekly usage consumed. This turn is **reading, planning and handoff only**.
The pasted plan's immediate implementation/execution instructions are deferred
by the user's current request. No new experiment, model request, OAuth session,
runtime repair, dependency update or background job is authorized by this handoff.
Do not assume quota resets or becomes available on a particular date.

## Goal and working research question

Improve the reliability and efficiency of ROSA, an existing LLM-based robotics
framework, through small reusable software improvements. No model training and
no requirement to make Qwen succeed at every cost. Preserve local Qwen3.5 9B
through Ollama and hosted Sol through the existing OAuth adapter as backends.

Can deterministic orchestration of routine robotic skills improve verified task
completion and inference efficiency over model-managed execution, and does a
simple bounded macro provide essentially the same benefit as the custom workflow?

The intended product is a practical module/integration with reproducible evidence
of benefits and limits. Positive results, negative results and simplifying the
architecture are all legitimate outcomes. JTVR and memory are optional candidate
ideas, not project identities or mandatory deliverables.

## What was implemented

- Shared bounded tools, validation, correction/resource accounting and independent
  scoring; actual Phoenix export and exact persisted-span audits.
- Trusted reporting by observation reference: model supplies classification and
  observation_id; ROSA retrieves recorded values and checks scope/freshness.
- Validated-report termination without requiring another LLM acknowledgment.
- A guarded UR5e trajectory capability in real ROS2/Gazebo, independently observed
  through a separate read-only ROS node. Near-home joint envelope, one command per
  trial, fresh prerequisite/outcome observations; no physical robot.
- Model-managed primitive calls versus two bundled implementations. The model
  selects an authorized pose; program reads, conditionally writes, freshly verifies
  and hands uncertainty/reporting back to the model. The macro and workflow have
  the same acquisition policy; the workflow adds explicit intermediate state tracking.

This is predefined decomposition of one bounded task, not arbitrary task planning.
The model still interprets the goal, chooses the skill, handles some recovery and
classifies the result. Four pose entries are variants of one movement primitive.

## Latest completed evidence: all 36 cells

Six cases x three conditions x two backends, one run per cell. The four remaining
hosted cells were completed under a separately frozen continuation after quota
interruption. No previously completed outcome was rerun or replaced.

| Backend | Condition | Correct /6 | Scoreable model calls | Native operations | Invalid attempts |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen | Primitive tools | 4/6 | 39 | 25 | 4 |
| Qwen | Simple macro | 5/6 | 22 | 19 | 5 |
| Qwen | Workflow | 5/6 | 21 | 19 | 4 |
| Sol | Primitive tools | 6/6 | 29 | 17 | 0 |
| Sol | Simple macro | 6/6 | 14 | 17 | 0 |
| Sol | Workflow | 6/6 | 14 | 17 | 0 |

Sol's two bundles match observed correctness/calls/native work. Qwen's bundles
complete one more case than primitive tools and use fewer calls. This is promising
combined-system evidence, not proof of general reliability or algorithmic novelty.
Qwen macro fails the old strict no-additional-calls retention screen by one call
against workflow on matched-correct pairs; do not relabel it a pass. Sol passes
that numerical screen. Neither result overrides the shared prompt audit exception.

Qwen failed already_home in every condition: it asked for task details without
calling tools, despite receiving the goal. These were not truncated responses.
The primitive-tool missing-prerequisite case exhausted8 calls on repeated reads
without an UNKNOWN report; both bundles reported UNKNOWN. Genuine task failures
remain in the data. The trusted program cannot help before the model invokes it.

There are37 saved attempt records:36 scored cells plus one original hosted quota
interruption. All37 local/persisted trace audits passed and saved scores were
recomputed. All196 frozen source copies are archived;591 manifest entries verified.
Original data/hashes and the explicit unknown token usage of the quota attempt
remain preserved. The continuation used15 requests. Total hosted attempts58,
including the quota request; Qwen82. Tokens were memory-only, session cleanup
revoked authorization, simulators exited cleanly and sleep holds were released.

Evidence:

- `artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md`
- `artifacts/macro-transfer-v1-resume-r1-20261023/combined-analysis.json`
- `artifacts/ROSA_MACRO_TRANSFER_V1_COMPLETE_WITH_CONTINUATION_2026-10-23.zip`
- ZIP SHA256: `27652480fb1a6f8a341025399a503b2c40bbcef64472b4de0bab77aae7303200`
- Current historical handoff: `../../reports/MACRO_TRANSFER_V1_ACTIVE.md`.

## Exact defect and proposed minimal repair

`rosa-research/src/rosa/rosa.py`, ROSA._get_prompts near line303, always prepends
the default system_prompts before appending RobotSystemPrompts. Setting
load_default_tools=False restricts tools but does not restrict those instructions.

`rosa-research/src/rosa/prompts.py` near lines74-106 requires discovery before
action and specifically mandates rosnode_list/rostopic_list. Other defaults
require math tools and suggest retries. Those tools are absent from this bounded
catalog, whose task contract instead requires select_skill before other tools.
Actual recorded LLM inputs contain both. This is a real shared instruction
inconsistency, but its causal effect on any particular failure is untested.

Proposed repair, not implemented:

1. Add a small opt-in bounded-task prompt implementation in rosa_research's
   reliability package. Use ROSA's _get_prompts seam; preserve its user/history/
   scratchpad scaffold and existing executor/parser/callback integration.
2. For this bounded mode, replace incompatible generic instructions with an
   explicit common contract grounded in self.tool_names (already initialized
   before _get_prompts). Do not merely append another contradictory paragraph.
   Preserve robot-specific permissions, required safety instructions and task
   semantics. Leave default upstream ROSA behavior unchanged when not opted in.
3. State authorized selection, prerequisite observations, allowed ordering,
   one-command/no-replay rules, fresh evidence, uncertainty/reporting, correction
   and resource limits consistently. Do not require absent discovery/math/memory
   tools. Define any observation-retry ceiling precisely if it is intended to be
   enforceable/scored; distinguish guidance from hard limits.
4. Use the same common corrected contract for Qwen and Sol and every condition.
   The only declared condition difference should describe who coordinates the
   bundle. Macro/workflow prompts should remain identical. No Qwen-specific hints.

First inspect how RobotSystemPrompts carries robot-specific instructions before
choosing exact template replacement mechanics; do not accidentally drop safety
content or access private ROSA attributes unnecessarily.

## Roadmap from this checkpoint

1. **Prompt repair:** implement the opt-in common contract in rosa-research.
2. **Separate repair validation:** test the actual composed model input and tool
   registry, then use a small separately labeled integration validation. Confirm
   no absent tool is mandatory, ordering is coherent, user goal is included,
   reporting/freshness/guards/termination still work, legacy mode is unchanged,
   and actual Phoenix span trees are complete. Do not tune on the next test set.
3. **Freeze the focused comparison:** A primitives, B bounded macro, C existing
   workflow; fresh cases, repetitions, counterbalanced order, same capabilities,
   budgets, permissions, reporting and independent evaluator. Prespecify resource
   caps, infrastructure-censoring rules, meaningful benefit, acceptable reliability
   loss and an engineering stopping rule before any live requests.
4. **Run the bounded pilot with both backends:** assess each against its own
   baseline. Retain model parameters; no silent output/context/prompt tuning from
   emerging results. Preserve every failure and all extra assistance/costs.
5. **Decide and consolidate:** if macro is sufficient, favor it; keep workflow as
   a reference without expanding it. If neither helps enough, report that and
   stop architectural expansion. Larger studies require a new protocol.

This uses the existing Gazebo foundation; it does not restart simulator integration.
The historical six-stage roadmap dated2026-10-21 is an archived checkpoint, not
current status: shared backends/scoring exist; earlier baselines/reliability and
Stage4 campaigns are preserved; original JTVR failed to beat strong batching in
the tested study and remains on hold; Stage5 memory is deferred; Stage6 UR5e
Gazebo has now been demonstrated. Hardware remains out of scope. Do not overwrite
that historical roadmap to erase earlier failures or imply every old gate passed.

## Proposed fresh pilot design: decisions to finalize before freezing

Cover already-satisfied goals, selection between authorized skills, unavailable
observations, attempted ineffective commands and a meaningful recovery/escalation
decision. Require actual fault exercise for attempted-failure scenarios. Score
goal attainment, correct FAILURE/UNKNOWN, unsupported structured claims, invalid
attempts, completion/termination, escalation, model calls/tokens, native operations,
latency and attribution of model versus program assistance separately.

Add repetitions and counterbalance condition order. Six fresh cases with two
repetitions per condition/backend would mean72 trials and a worst-case288 model
requests per backend at8/trial. This is a planning option, **not a frozen protocol
or authorized job**; size and caps should be finalized after repair validation
and a resource review. Do not assume a small pilot proves statistical equivalence.

Where practical, consider an independently scored read-only inspection capability
in addition to motion. The existing WorkflowSession supports one selected,
single-node numeric-target skill and one write. A true inspection-success contract
differs from matching a pose; it needs an explicit minimal contract and independent
scoring shared across conditions. Do not call another pose a different capability,
or add a general planner to satisfy that aspiration. If scope cannot support a
second capability cleanly, keep motion-only scope and label its limits.

Likewise, current guards reject stale observation references. Do not pretend that
this automatically validates arbitrary stale sensor packets: sensor-age/provenance
faults require an explicit trusted freshness mechanism and tested injection. Use
supported cases or validate that narrow extension separately. Do not ask the
one-shot prototype to execute multi-skill plans/reselection it currently forbids.

Keep all-attempt costs, matched-outcome comparisons and infrastructure interruptions
visible; failed early exits are not efficiency improvements. Accepted UNKNOWN
after unavailable observations must not be described as dishonest simply because
the private evaluator knows the physical state. Distinguish honest uncertainty
from completion of an achievable recover-and-verify objective.

## Repository and resume instructions

Implementation belongs in rosa-research; protocols, tests, data, traces and reports
belong in rosa-evaluation. Both repos were on member/martin. Recheck branches and
existing dirty files before any edits/commit; do not stage unrelated work. Preserve
all sealed archives, freeze digests and original failures. Use new module/campaign
names for prospective repairs/experiments; never edit frozen runtime files and
silently rerun their historical campaign.

Research interpreter: /home/martin/.local/share/rosa-envs/research/bin/python.
Phoenix interpreter: /home/martin/.local/share/rosa-envs/phoenix/bin/python.
WSL Ubuntu-24.04, user martin. reports/v2-command.sh sources ROS2 Jazzy and enters
rosa-evaluation. Phoenix uses localhost6006; ROSA manual OAuth uses localhost1455.
Existing service helpers start pinned Ollama and persistent loopback Phoenix.
Do not print .env or credentials. Existing OAuth supports memory renewal under
validated grants; keep manual initial consent and normal revocation. Request fresh
consent only after the concrete frozen request cap is ready. Quota errors stop
and preserve progress; new consent/refresh must never bypass quota.

Suggested return message: "Resume the October30 handoff. Start with the opt-in
prompt/tool-contract repair and separate validation; preserve the completed macro
study and do not launch the new pilot before its protocol is frozen."

Source plan read this turn:
`C:/Users/user/.codex/attachments/a16fab2b-a08b-4abd-9af6-308bda9b2ebc/Pasted text.txt`.
Its technical direction is accepted as the next milestone; its immediate-run
instructions do not override the user's current planning-only request.
