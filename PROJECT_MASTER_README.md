# Improved ROSA — living progress report and master project record

Updated: **2026-10-30**. Maintained project context, decision history and evidence map.

This is the maintained progress report and main overview for handing this project to another chatbot, researcher
or teammate. It separates implemented software, measured results, unfinished work,
proposals and historical plans. It is a summary with links to detailed evidence,
not a substitute for every raw transcript or a claim that every hypothesis worked.
It contains no credentials. Dates are shown without a geographic location.

Start with [current work, progress, gates and next actions](#2-current-verified-status).
For a compact end-to-end summary, use the [M1–M5 recap](docs/M1_M5_RECAP_2026-10-30.md).
That section describes where the project stands now. The research history below
supports current decisions; it does not replace an up-to-date progress report.

**Read first:** the project improves ROSA's surrounding software, not the LLM's
weights. The current candidate is a small reusable **bounded macro component**.
Movement and read-only readiness inspection work in Gazebo. The final focused
comparison, **M4**, is complete: all80 trials and eight clarification reviews.
Sol passed20/20 tasks in both conditions; Qwen passed15/20 with primitives and
14/20 with macro. Sol met the preset retention screen; Qwen did not. M5
technical consolidation is complete locally; evaluation off-machine backup is
deferred by user choice. Eight human ratings were received on2026-10-29; on2026-10-30
the owner clarified an outcome-oriented preference. Stakeholder feedback is closed;
frozen-criterion independent human adjudication was not obtained. Do not restart
the populated experiment directories.

**Latest review:** the user supplied Claude's assessment of this overview.
Our [recorded assessment and proposed M5 priorities](docs/M4_EXTERNAL_REVIEW_ASSESSMENT_2026-10-27.md)
emphasize truthful evidence versus correct intent, a concise claim ledger,
appropriately qualified uncertainty and human clarification review. Qwen's failed
engineering gate is not proof of harm; the small study also does not establish
equivalent reliability or a difference that is definitely just noise. A suggested
selection diagnostic remains future work; M5 backup and delivery are now authorized.
The later [Claude/ChatGPT discussion recap](docs/M5_REVIEW_DISCUSSION_RECEIVED_2026-10-27.md)
converges on four proposed M5 gates: off-machine protection, existing-trace/human
review, final claims/analysis, then packaging/presentation. See the assessment
for current gate status and corrections to the suggested thesis. The user then
requested completion of M5. The four-trace review, family-aware postprocessing,
one-page claim ledger, ten-page report, installation acceptance and two recorded
Gazebo presentation runs are complete. Martin submitted eight human ratings on
2026-10-29, passing inspection and failing clarification. These oppose the frozen
clarification criterion. On2026-10-30, the owner clarified that practical outcomes
matter more to them and normal tasks should be concise and explicit. The review
is retained as stakeholder feedback, not validation under the frozen criterion.
See the [dated resolution and task-wording guidance](artifacts/macro-m5-20261027/HUMAN_REVIEW_RESOLUTION_2026-10-30.md).
Original ratings are preserved; frozen scores are unchanged. Research source was pushed and all86
remote-tarball files verified. On2026-10-28, the user chose to keep the evaluation
backup local. Its off-machine protection is deferred; no publication approval is
pending. The earlier rejected public push made no evaluation transfer.
See the [local-retention decision](docs/M5_LOCAL_RETENTION_DECISION_2026-10-28.md).
Both committed branches now also have verified local shallow-aware backups;
see the [M5 technical closeout and backup](docs/M5_CLOSEOUT_AND_LOCAL_BACKUP_2026-10-30.md).
The protected base revisions are research b13df0f and evaluation b5e94bf. This is
local protection of available history, not an off-machine evaluation backup.
M4 scores/archives are unchanged; no new research
experiment was launched. All M5 trace interpretation is retrospective.

## Contents

1. [Goals and research question](#1-goals-and-research-question)
2. [Current verified status](#2-current-verified-status)
3. [Repositories and evidence authority](#3-repositories-and-evidence-authority)
4. [What the current architecture actually does](#4-what-the-current-architecture-actually-does)
5. [Implementation map](#5-implementation-map)
6. [Environment and serving configuration](#6-environment-and-serving-configuration)
7. [OAuth, security and unattended execution](#7-oauth-security-and-unattended-execution)
8. [Experimental vocabulary and fair attribution](#8-experimental-vocabulary-and-fair-attribution)
9. [Research history and important results](#9-research-history-and-important-results)
10. [Roadmaps and numbering](#10-roadmaps-and-numbering)
11. [M4 protocol and current decision boundary](#11-m4-protocol-and-current-decision-boundary)
12. [Known limitations and unresolved questions](#12-known-limitations-and-unresolved-questions)
13. [Team package and compatibility](#13-team-package-and-compatibility)
14. [Evidence and archive index](#14-evidence-and-archive-index)
15. [Operational handoff](#15-operational-handoff)
16. [Maintenance and user preferences](#16-maintenance-and-user-preferences)
17. [Decision log and corrections](#17-decision-log-and-corrections)

## 1. Goals and research question

The team's objective is to **improve the reliability and/or efficiency of the
existing LLM-based robotic agent framework ROSA**, through changes to its software
architecture. This is an achievable undergraduate robotics research project.

We are not training a new model, developing a replacement foundation model,
obligated to make Qwen match a larger hosted backend, or required to implement
every algorithm explored during the project.

The overarching research question is:

> To what extent can changes to tool execution, feedback and outcome verification
> improve the reliability and efficiency of an LLM-based robotic agent in ROSA,
> particularly with the tested smaller local model?

Each experiment must ask a narrower question with a competent simpler reference.
The current question concerns **model-managed primitive execution versus a bounded
macro**, using both local Qwen and hosted Sol separately.

The intended deliverable is a maintainable reusable Python component integrated
with ROSA, a working Gazebo demonstration, and reproducible experimental evidence
of benefits and limitations. A small completed module is preferable to several
unfinished research systems. A negative result is acceptable.

Verification/reliability and tool-calling efficiency are related research interests,
not obligations to build two large independent architectures. JTVR was one candidate
method; it is not the project's identity. Episodic memory is optional future work.
Physical hardware and coordinated dual-arm manipulation are not current completion
requirements.

The [recorded project vision](../rosa-research/PROJECT_VISION.md) preserves the
user's earlier clarification. Its immediate experiment suggestions describe that
historical point; the M1–M5 priorities below reflect subsequent decisions.

## 2. Current verified status

This section is refreshed from existing files by
`python -m tools.project_context --refresh`. It makes no model calls, reads no
credential records and does not modify experimental inputs or trial results.
The figures are a snapshot, not a continuously refreshed dashboard. Refresh before
sharing this document or making a new claim about an active run.

<!-- PROJECT_STATUS_START -->
Last refreshed: **2026-10-30 01:33:25**. Saved-checkpoint snapshot.

### Current work and next actions

| Progress item | Current evidence / action |
|---|---|
| Current milestone | M5: TECHNICAL_DELIVERY_COMPLETE_EVALUATION_LOCAL_BY_USER_CHOICE. M5 technical delivery and outcome-oriented owner feedback complete. Both committed branches have verified shallow-aware local restores. Evaluation off-machine backup remains deferred; frozen-criterion independent human adjudication was not obtained. |
| M4 recorded execution | 80/80 trial rows; 0 cells without a recorded result, including any in-flight trial. |
| M4 operator clarification review | 8/8 valid operator reviews recorded; 0 still required. This is not independent human adjudication. |
| Current decision | Retain bounded module as optional engineering capability; Sol positive, Qwen failed reliability-preserving retention. No unqualified cross-model recommendation. |
| Next actions | Use the delivered report, claim ledger, video and installation guide. Retain local backups; off-machine evaluation backup and frozen-criterion independent human adjudication remain unfulfilled and unscheduled. Use concise explicit wording for future known-goal tasks. No new studies, runtime changes or GitHub uploads are scheduled. |
| Open gates / blockers | M5.1_backup: LOCAL_RESTORE_VERIFIED: research b13df0f and evaluation b5e94bf; shallow boundaries preserved. Research b13df0f separately verified remotely. Evaluation off-machine backup deferred by user.; M5.2_existing_evidence: TRACE_REVIEW_COMPLETE; STAKEHOLDER_FEEDBACK_CLOSED_8_RATINGS; FROZEN_CRITERION_INDEPENDENT_HUMAN_ADJUDICATION_NOT_OBTAINED; FROZEN_SCORES_UNCHANGED; M5.3_research_consolidation: COMPLETE: family table, paired outcomes, both cost views, exploratory family-aware uncertainty,10-page report and1-page ledger.; M5.4_deliverables: COMPLETE_LOCAL: validated wheel, two-backend Gazebo video,10-page report,1-page ledger,898-file verified delivery ZIP.. Eight ratings submitted by martin on2026-10-29 (four pass, four fail). Outcome-oriented owner preference clarified2026-10-30; stakeholder review closed. Frozen-criterion independent human adjudication was not obtained. Prior aggregate-result exposure is disclosed. |

| Backend | Saved status | Recorded / scheduled | Local + Phoenix audited | Reserved requests / cap |
|---|---|---:|---:|---:|
| Sol | COMPLETE | 40/40 | 40 | 106 / 323 |
| Qwen | COMPLETE | 40/40 | 40 | 144 / 323 |

M5 separately used **4 presentation inference requests** and **0 new research trials**. Human-review status: Eight ratings submitted by martin on2026-10-29 (four pass, four fail). Outcome-oriented owner preference clarified2026-10-30; stakeholder review closed. Frozen-criterion independent human adjudication was not obtained. Prior aggregate-result exposure is disclosed. The [eight-case packet](artifacts/macro-m5-20261027/ROSA_M5_HUMAN_REVIEW_PACKET.zip) is retained. The eight operator ratings above do not count as human review.

Recorded rows can include a row awaiting its audit. Reserved requests can include
an in-flight or failed request; they are not generated-token totals. Unfinished
cells are not assumed to pass. These counts do not establish process liveness.

- **Sol:** clarification reviews passed 4/4; failed 0; recorded answers pending/invalid review 0. Answers for unrecorded cells remain unreviewed.
- **Qwen:** clarification reviews passed 0/4; failed 4; recorded answers pending/invalid review 0. Answers for unrecorded cells remain unreviewed.

| Backend / condition | Audited automatic passes / recorded | Recorded requests | Native operations |
|---|---:|---:|---:|
| Sol / primitives | 20/20 | 68 | 38 |
| Sol / macro | 20/20 | 38 | 40 |
| Qwen / primitives | 15/20 | 91 | 50 |
| Qwen / macro | 14/20 | 53 | 48 |

Supervisor's saved phase: `EXECUTION_FINISHED_REVIEW_REQUIRED`. Frozen source check: 62 files; 0 mismatches.

The automatic primary-pass count is separate from required clarification review.
A final M4 decision also requires the frozen paired analysis and limits/audit checks.
Refresh with `python -m tools.project_context --refresh`; narrative sections still
need review when the study or roadmap changes.

The supervisor phase above is its preserved pre-review checkpoint. Final closure
is recorded in `closeout.json` and the [final M4 report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md).
Completed review includes four failed Qwen clarification cases; eight reviews does not mean eight passes.
<!-- PROJECT_STATUS_END -->

### Confirmed closed checkpoints

| Milestone | Confirmed result | Qualification |
|---|---|---|
| M1 reusable module | Engineering acceptance passed; no live model requests | Public API, installation into an empty target, scripted adapters and seven deterministic Gazebo checks; not a clean-OS installation test. |
| M2 second capability | 10/10 deterministic Gazebo cases | The second capability is read-only inspection, not a gripper or another actuator. |
| M3 demonstration | Deterministic 3/3; Sol 3/3; Qwen 2/3 | Eight of nine including scripted controls; actual model trials were five of six. Qwen failed ambiguity handling. |
| M2/M3 observability | 19/19 local and exact persisted-Phoenix audits; 331 spans | Does not repair earlier studies' audit exceptions. |
| M4 zero-model gate | 20/20 controls; 20/20 Phoenix audits; 202 spans | Prerequisite for the live comparison, not live model-performance evidence. |
| M4 Sol | Primitives 20/20; macro 20/20 | All40 audits and four clarification reviews passed; retention screen passed. |
| M4 Qwen | Primitives15/20; macro14/20 | All40 audits passed; all four clarification cases failed review; retention screen failed. |
| M4 complete study | All80 trial results; all80 audits; all8 required reviews recorded | Mixed findings; no unconditional two-backend reliability-preserving recommendation. |

Sol's closed M4 measurements: primitives **68 model requests and 38 native
operations**; macro **38 requests and 40 native operations**. This is **44.1% fewer
model requests and 5.3% more native operations** in the tested cases. It does not
establish general reliability, novelty or a causal cross-model speed ranking.

The [M4 efficiency and timing report](docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md)
adds known input/output tokens, task mean/median/total times, backend elapsed time
including overhead, and matched-success call/time/native-operation reductions.
It is refreshed from the same snapshot. Both backend runs are now complete;
fewer calls alone do not establish a more reliable system. The
[final M4 report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md) gives
the completed paired comparison, all failures, review decisions and next steps.

### Current M5 delivery outputs

- [Focused research report: Markdown](artifacts/macro-m5-20261027/M5_RESEARCH_REPORT.md)
  and [ten-page PDF](artifacts/macro-m5-20261027/ROSA_M5_RESEARCH_REPORT.pdf).
- [Claim/evidence/limitation ledger](artifacts/macro-m5-20261027/CLAIM_LEDGER.md)
  and [one-page PDF](artifacts/macro-m5-20261027/ROSA_M5_CLAIM_LEDGER.pdf).
- [Four-trace forensic review](artifacts/macro-m5-20261027/PARTIAL_COMMAND_FORENSIC_REVIEW.md),
  [family-level results](artifacts/macro-m5-20261027/per-family-results.csv),
  [paired outcomes](artifacts/macro-m5-20261027/paired-outcomes.csv),
  [both efficiency views](artifacts/macro-m5-20261027/efficiency-both-views.csv), and
  [exploratory uncertainty](artifacts/macro-m5-20261027/UNCERTAINTY_AND_PAIRED_ANALYSIS.md).
- [Human-review packet](artifacts/macro-m5-20261027/ROSA_M5_HUMAN_REVIEW_PACKET.zip):
  eight cases, labels/scores withheld, ratings empty. The operator key is separate.
  Eight human ratings received2026-10-29; outcome-oriented stakeholder feedback
  closed2026-10-30. Frozen-criterion independent adjudication was not obtained. Prior exposure and
  the owner's role are disclosed; response style can still reveal source.
- [50.4-second Gazebo demonstration](artifacts/macro-m5-20261027/ROSA_M5_GAZEBO_DEMONSTRATION.mp4)
  and [video provenance](artifacts/macro-m5-20261027/video-provenance.json). Both new
  presentation runs reached the explicit offset goal in two model calls each;
  four requests total, no retakes. Model/tool loop times were16.18 seconds for Sol
  and98.99 for Qwen, including presentation overhead, not a new speed benchmark.
  Waiting is labeled8x; the camera-motion segment is1x. No desktop capture.
- [Installation acceptance](artifacts/macro-m5-20261027/package/acceptance.json)
  and [module delivery guide](../rosa-research/docs/M5_MODULE_DELIVERY_README_2026-10-27.md):
  offline wheel build, empty target, both public capabilities, installed CLI help,
  no experiment imports. Existing dependencies/ROS retained; not a fresh-OS test.
- [Backup scan](artifacts/macro-m5-20261027/credential-scan.json),
  [off-machine verification status](artifacts/macro-m5-20261027/off-machine-verification.json)
  and [dependency-lock addendum](artifacts/macro-m5-20261027/lockfile-backup-addendum.json).
- [2026-10-30 committed backup record](artifacts/macro-m5-20261027/committed-backup-20261030.json):
  both branches restored into new bare repositories, exact protected trees matched,
  and Git object checks passed. Sources are shallow; the bundle and matching
  history-boundary marker are both required. Backup directory is outside Git.
- [Focused delivery ZIP](artifacts/ROSA_M5_DELIVERY_2026-10-27.zip) and
  [verification](artifacts/ROSA_M5_DELIVERY_2026-10-27.verification.json):898 file
  hashes verified,23,688,385 bytes, ZIP integrity and credential-pattern checks pass.
  SHA256: `e19b01e5940e848553c2cf36433199847c6c20f447e2aa112bd64c4ff7f97e72`.
  This is locally ready, not yet a verified off-machine evaluation backup.
  The packaged handoff snapshot precedes the outer checksum and this verification note.

The deeper review adds an observed recovery-path distinction: both primitive
partial-command runs first request a readiness read before selecting a skill.
That is rejected without acquisition, after which Qwen selects the movement skill.
Both macro runs select inspection immediately, then attempt the correct movement
skill but are rejected by the shared commitment rule. System prompts and tool
schemas are identical; user-message condition wording differs. This documents
action/feedback interaction, not a causal explanation of the first choice.

M5 engineering exceptions are preserved: two exact expired sentinel literals were
reviewed as noncredentials in the scan; an initial installation probe incorrectly
used an internal field and was corrected to the public snapshot API; the first
backup filter excluded14 historical uv.lock copies, now preserved by a separately
verified addendum. None required changing the frozen runtime or old evidence.

## 3. Repositories and evidence authority

| Component | Repository / local directory | Responsibility |
|---|---|---|
| Reusable runtime | [Lelevinson/rosa-research](https://github.com/Lelevinson/rosa-research), sibling `rosa-research/` | ROSA integration, model adapters, bounded execution/reporting, ROS transports, public module and demos. |
| Evaluation and record | [Lelevinson/rosa-evaluation](https://github.com/Lelevinson/rosa-evaluation), this repository | Frozen protocols, independent scorers, fixtures, tracing audits, raw attempts, reports and this handoff. |
| Workspace orchestration | Parent directory and its `reports/` | Machine-specific setup, detached supervisors, packaging and historical operator records; parent directory is not a Git repository. |

Both project repositories use the user's branch **`member/martin`**. Do not move
work onto another member's branch or publish to the default branch without the
user's instruction. A source copy inside an evidence ZIP does not replace an
implementation commit in the research repository.

Research implementation and the M5 delivery guide throughb13df0f were pushed to
member/martin; the remote tip and all86 source-tarball files were independently verified in M5.
Evaluation commits and retained-evidence backup remain local by the user's
2026-10-28 instruction. Off-machine evaluation backup is deferred; no upload is
scheduled. Some older files remain untracked individually
but are included in the retained-work backup; original unrelated working changes,
including the research README and Stage4 result edits, remain preserved. See the
M5 off-machine record for the precise backed-up revision instead of assuming that
every later local commit has been uploaded.

The [2026-10-30 GitHub access check](docs/GITHUB_ACCESS_CHECK_2026-10-30.md)
confirmed that GitHub CLI and Windows Git Credential Manager both authenticate as
fkilr50, with push permission to both repositories. No login/configuration repair
was required and no upload was performed. The earlier evaluation push rejection
concerned public disclosure authorization; the user's local-retention decision
remains in effect.

Important checkpoints, which need not be the latest documentation HEAD:

| Research commit | Meaning |
|---|---|
| `cc4a170` | M1 reusable bounded macro and necessary supporting runtime checkpoint. |
| `cf722cf` | Prospective Windows refresh-credential replacement and cleanup-notice fix. |
| `c0c61a0` | M2 inspection capability, M3 public Gazebo demonstration and documentation. |

| Evaluation commit | Meaning |
|---|---|
| `0c95c9b` | M1 evidence/acceptance checkpoint. |
| `ce7d2d4` | M2/M3 runner, raw evidence, report and archive. |
| `798bbb5` | Report amendment explaining inference caps and a future infrastructure reserve. |
| `8e5cdc5` | Date-only M2/M3 report heading. |
| `1e0cc27`, `4412f05` | Prospective M4 runner/protocol and corrected actual dependency-lock paths. |
| `763cbc6` | M4 freeze, passed controls and operator-source checkpoint. |
| `1054196` | Completed Sol M4 trials, audits and four clarification reviews. |

For historical facts, consult raw attempts and the protocol under which they were
recorded, together with explicit errata/continuation lineage. This overview is
derived. A new planning decision changes future priorities, not old scores. Never
silently resolve contradictory old progress messages by assuming the favorable
number is correct. Superseded RUNNING statuses and failed supervisors remain data.

## 4. What the current architecture actually does

```text
User request + application-authorized catalogue
                    |
                    v
 Qwen through Ollama OR Sol through ChatSiwc
       interpret intent / select skill / clarify
                    |
                    v
 ROSA executor + shared guards/report contract
       |                              |
       | primitives                   | bounded macro
       | model requests routine       | Python performs known
       | individual operations        | read/conditional-write/verify steps
       +------------------------------+
                    |
          bounded ROS 2 transport
                    |
              Gazebo UR5e
                    |
       fresh observations and evidence ID
                    |
       model classification, validated report,
       deterministic accepted-report termination

Separate evaluation observers score intent/outcome/fault exercise;
local traces are matched to actual persisted Phoenix spans.
```

### The user's divide-and-conquer suggestion

The application defines small, known skills. Python handles the predictable
substeps inside a selected skill. The model is freed from micromanaging controller
math and routine execution, while retaining semantic selection and unresolved
decisions. This is **pre-authored skill decomposition**, not an autonomous planner
that decomposes any arbitrary natural-language task into a new sequence.

### The user's program-based tool-selection suggestion

Program logic chooses the routine steps inside the authorized skill. It validates
arguments, obtains prerequisites, conditionally writes once and checks fresh state.
The model still chooses the high-level skill and classifies evidence. The five
public tools remain exposed; we have not implemented a generic router that exposes
exactly one possible tool at every turn across the entire ROSA catalogue.

### Public tools and ownership

| Tool | Role |
|---|---|
| `select_skill` | Model selects one permitted exact ID per invocation. Macro mode executes the bounded routine; primitive mode returns selected targets. |
| `read_state` | Obtains fresh permitted state; missing evidence remains explicit. |
| `write_state` | Exact authorized target only, known prerequisites, at most one movement dispatch. Forbidden for an inspection selection. |
| `verify_outcome` | Fresh observation and selected-goal/readiness check; may be invoked by the program inside a macro. |
| `submit_report` | Model supplies SUCCESS/FAILURE/UNKNOWN and the latest task-local observation ID; program supplies/checks recorded values and validates classification. |

An accepted report ends the task without another LLM acknowledgement. This removes
deterministic bookkeeping, but does not mean the LLM authored every numeric field
in the final JSON. A model may still make additional bounded observations after
uncertainty; bundling is not a guarantee that it never calls another tool.

### The two capability contracts

**Named-pose movement:** one bounded six-joint trajectory, conditional on current
known state and necessity. Already-at-goal should not dispatch a trajectory. All
targets must be the complete registered six-joint values unchanged and within
the existing transport's 0.4-rad home neighborhood. A receipt is not verification.

**Read-only readiness inspection:** query trajectory-controller activation,
joint-state-broadcaster activation and availability of a fresh complete finite
joint sample. It has zero writes and an observer with no trajectory publisher.
Controller query and joint acquisition are two separately metered native sources.
Boolean facts are explicitly encoded true=1.0, false=0.0, unavailable=null for
the existing validator. Observed unready means FAILURE; unavailable evidence means
UNKNOWN. Successful data acquisition is different from robot readiness.

`/ur5e` and `/ur5e_readiness` are registered logical evidence keys, not claims that
these exact names are independently discovered ROS nodes. Actual interfaces include
`/joint_states`, `/joint_trajectory_controller/joint_trajectory` and the controller
manager's ListControllers service. Controller switching is evaluation fault setup,
not an exposed inspection skill.

The model has **one selected skill per fresh invocation**. M3/M4 select different
capabilities in separate tasks. They do not demonstrate autonomous chaining of
inspection and movement into a larger multi-step task. A readiness observation
does not authorize a later movement or replace that later task's fresh evidence.

### Inheritance and scope

The simple policy reuses
`MacroSession -> ReferenceWorkflowSession -> WorkflowSession -> EvidenceSession -> ExecutionSession`.
Pausing the custom workflow comparison does not make its shared base code removable.
"Simple macro" describes the execution policy, not proof that all inherited
infrastructure disappeared or that a new selection algorithm was invented.

## 5. Implementation map

Research paths are relative to the sibling `rosa-research/`:

| Path | Purpose |
|---|---|
| `src/rosa/rosa.py` | Actual ROSA integration, optional default-tool disabling, tool-name introspection and prompt composition support. |
| `src/rosa_reliability/execution.py` | Strict outcome contract, native reservations, bounds, validation feedback and traces. |
| `src/rosa_reliability/tools.py` | Shared reliable tool schemas/wrappers. |
| `src/rosa_reliability/evidence.py` | Reuse of current trusted observations without requiring a particular named verification tool. |
| `src/rosa_reliability/reference.py` | Report by latest task-local observation ID instead of manually copying node keys and measurements. |
| `src/rosa_reliability/workflow.py` | Shared selection/session scaffolding and preserved state-tracked policy. |
| `src/rosa_reliability/macro.py` | Straight-line bounded routine using the shared guards. |
| `src/rosa_reliability/bounded_macro.py` | M1 StateSkill, SkillRegistry, MacroLimits and MacroInvocation, internal component 0.1.0. |
| `src/rosa_reliability/capabilities.py` | M2 CapabilityRegistry/InspectionSkill/CapabilityInvocation, additive component 0.2.0. |
| `src/rosa_reliability/macro_agent.py` | MacroROSA, inference metering and shared pre-parser resource gate. |
| `src/rosa_reliability/prompt_contract.py` | Backend-neutral bounded-tool prompt replacing a known incompatible generic prefix. |
| `src/rosa_reliability/completion.py` | Pre-parser completion handling; historical truncation-recovery mechanism. Current macro gate stops on length rather than enabling that experiment automatically. |
| `src/rosa_reliability/terminal.py` | Immediate validated-report termination and attribution spans. |
| `src/rosa_reliability/ros_arm.py` | Bounded UR5e trajectory transport and fresh joint-state observer. |
| `src/rosa_reliability/ros_readiness.py` | Bounded read-only controller/joint readiness acquisition. |
| `src/rosa_reliability/gazebo_demo.py` | Own-process headless simulator startup, controller readiness and cleanup. |
| `src/rosa_reliability/capability_demo.py` | Public two-capability deterministic/Ollama/Siwc demo. |
| `src/rosa_backends/chat_ollama.py` | Configured Ollama adapter preserving per-request serving options. |
| `src/rosa_backends/chat_siwc.py` | Native Sign in with ChatGPT Responses flow exposed as a LangChain tool-calling model. |
| `src/rosa_auth/oauth.py`, `responses.py`, `session.py` | Existing validation, in-memory renewal, bounded transport and default session cleanup. |
| `src/rosa_auth/protected_store.py`, `remembered.py` | Optional protected refresh-credential persistence and explicit sign-out. |

Evaluation paths:

| Path | Purpose |
|---|---|
| `experiments/macro_capabilities_v2/` | M2 controls, M3 fixed live demo, common local and persisted trace auditors. |
| `experiments/macro_m4/design.py` | Fresh cases, catalogue, paired order, common rules and resource limits. |
| `experiments/macro_m4/runner.py` | Freeze, controls, bounded live execution, independent observations and checkpoints. |
| `experiments/macro_m4/recovery.py` | Explicit prospective infrastructure reserve, separate from robot policy. |
| `experiments/macro_m4/scoring.py` | Goal alignment, outcome, fault exercise, violations and actor/cost components. |
| `experiments/macro_m4/analysis.py`, `report.py` | Saved-attempt aggregation and preliminary execution report; clarification overlay is separately required. |
| `tools/phoenix/` | Independently locked local Phoenix server/client/audit utilities. |
| `artifacts/` | Raw evidence, source freezes, reports and checksummed archives. |

The public module has no dependency on importing experiment packages. Evaluation
code may reuse runtime code; runtime should not import a benchmark's hidden case
labels or oracle. Trusted targets/permissions are application-defined and copied
into fresh invocations.

## 6. Environment and serving configuration

### Existing local environment

- Windows with WSL2, Ubuntu24.04, ROS2 Jazzy and Gazebo Harmonic.
- NVIDIA GeForce RTX4050 Laptop GPU: nvidia-smi reported 6141 MiB total, approximately 6 GB VRAM.
- Windows reported 15.71 GiB physical RAM available to the OS, consistent with the
  project's nominal 16 GB laptop specification. Do not confuse WSL's VM allowance
  with the machine's installed RAM.
- Python3.12.3 in the recorded research runtime. ROSA distribution `jpl-rosa`1.0.10.
- `uv` manages dependencies. The evaluation runner shares the research environment;
  there is **no evaluation-root pyproject/uv.lock**. Phoenix has its own project/lock.
- Research environment on Linux storage: `/home/martin/.local/share/rosa-envs/research`;
  Phoenix environment: `/home/martin/.local/share/rosa-envs/phoenix`. Repository-local
  environment links/wrappers resolve these paths. They are machine-specific.

Recorded M2/M3 runtime versions: LangChain0.3.30, langchain-core0.3.86,
langchain-ollama0.3.10, Ollama Python client0.6.3, Pydantic2.14.1,
OpenInference LangChain instrumentation0.1.79, OpenTelemetry SDK1.45.1,
PyJWT2.15.1. Phoenix is pinned20.23.0 with client3.5.0 in its separate project.
These are project snapshots, not claims about latest upstream releases.

System ROS/Gazebo and vendor robot dependencies are not fully reproduced by
`uv.lock`. The wheel acceptance test did not provision a fresh Windows/WSL/ROS
machine. Headless Gazebo tests do not establish current GUI acceleration; an
earlier GUI check reported llvmpipe. Do not rerun system installation to enter
the existing environment.

### Backends

| Backend | Fixed identity/settings in the current campaign |
|---|---|
| Local | `qwen3.5:9b`, Q4_K_M, pinned Ollama server 0.40.6, num_ctx8192, local per-response maximum 1024, temperature 0, seed 42, mmap true, reasoning/stream/cache disabled. |
| Hosted | Exact model slug `gpt-6.1-sol`, ChatSiwc through the existing OAuth adapter, provider defaults rather than an identical local sampling/compute profile. |

Qwen model digest:
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
The model weights/quantization were not changed to obtain later results.

The Ollama application's context slider and a server default of 4096 do not prove
that an experiment used 4K: these requests explicitly set 8192. Context size and
generated-output allowance are different. Do not increase context/output settings
inside a frozen study. Larger context is not an automatic reasoning improvement
and can increase memory pressure on this machine. CPU/GPU offload, loading and
host activity limit latency comparisons.

The same **maximum budgets within a backend** do not imply equal actual usage,
tokenization, hardware or provider-side hard limits across backends. A model name
does not expose an immutable hosted server revision.

### Simulated skill

Six-joint HOME is `(0, -1.57, 1.57, -1.57, -1.57, 0)` for pan, lift, elbow,
wrist1, wrist2, wrist3. Commands use standard ROS2 trajectory control, a three-second
trajectory and bounded observation waits. The default final joint tolerance is
0.025 rad. The controller and transport retain their original bounds.

Startup once exposed a HOME-spawn mismatch. The accepted helper generates a
top-level Xacro copy that supplies the existing initial_positions argument; it
does not change installed geometry, controller configuration or tolerances.
Independent cold starts and deterministic controls validated the correction.
Existing DART mesh/collision warnings remain. Final joint agreement is not proof
of collision-free paths, obstacle avoidance, torque safety, grasping or real hardware safety.

## 7. OAuth, security and unattended execution

**Original adapter renewal already existed.** The repeated sign-ins largely came
from deliberate memory-only revoke-on-exit sessions, not absence of refresh support.
Do not rebuild OAuth or automate consent clicks to solve that cleanup choice.

The user explicitly chose **secure remembered sign-in across restarts with an
explicit sign-out**. The opt-in remembered context reuses existing identity,
scope and refresh validation. It stores only a refresh credential and validated
registration/grant metadata under current-Windows-user DPAPI, in a user/SYSTEM-only
directory outside Git. Access/ID tokens are not persisted by this mode. A Windows
named-mutex lease serializes use and rotating refresh across processes.

Requested permissions in the implementation include OpenID/profile/email,
offline_access, resource.invoke and chatgpt.tokens.use.direct; actual grants are
validated against the existing allowed/required scope contract. No scope expansion,
API-key billing fallback, credential sharing or automatic approval of new consent
is authorized. No password/token should be pasted into a chatbot.

**Live defect and repair:** initial DPAPI saving succeeded, but Windows PowerShell
converted File.Replace's null backup argument to an empty path during replacement.
A cross-process renewal test exposed this; the provider had rotated credentials,
storage failed and cleanup attempted revocation. An unusable old grant then returned
invalid_grant. A cleanup BrokenPipeError masked the original failure. The small
prospective fix passes a true CLR null to atomic replacement and prevents stream
closure from masking errors. No plaintext fallback or token-backup file was added.
The sign-in notice was corrected to match the selected cleanup mode.

Synthetic Windows replacement/restart/lease/deletion regression passed. After
fresh **manual** authorization, a separate process renewed the real protected grant
without a browser or inference. M4 Sol then successfully started through protected
refresh and completed 40 trials; its public cleanup status records one refresh,
cleared memory and retained encrypted authorization. This is not proof of overnight
endurance or immunity to revocation, expiry, outages or quota exhaustion.

Normal `interactive_session` retains its memory-only/revoke-on-exit behavior.
Remembered mode is optional; successful exit clears memory while retaining the
encrypted refresh credential by user preference. Explicit sign-out is
`python -m rosa_auth.remembered logout`. `status` checks local presence, not provider
validity. `login` may require manual consent and must not be launched incidentally
during an active leased session.

M4 refuses to initiate a new login when a protected grant is absent. Authorization
loss stops hosted requests and preserves progress; it never implies remaining
trials passed. Refresh does not create quota or reset experimental budgets.
Detached workers are separate from chat turns, but still depend on an awake
computer, WSL, network and backend authorization/quota. Loss of coding-assistant
updates is not itself proof the worker stopped; inspect checkpoints/process identity.

Never put credentials, protected records, authorization codes, hinted authorize
URLs or transport-only private continuation material into logs, Phoenix, reports,
Git or archives. See the [specific repair/validation record](../rosa-research/docs/REMEMBERED_AUTH_ROTATION_VALIDATION_2026-10-27.md).

## 8. Experimental vocabulary and fair attribution

| Term | Meaning and required distinction |
|---|---|
| Scheduled / attempted / completed / passed | Separate counts. A completed run may contain failed tasks; unstarted cells have no observed outcome. |
| Primary pass | Full frozen task contract. Appropriate FAILURE/UNKNOWN in fault cases can pass; it is not a robot-movement success percentage. |
| Physical goal attained | Separate independent final-state observation; reaching the pose does not automatically complete reporting/intent requirements. |
| Correct user goal | Selected skill satisfies the request, or valid clarification occurs before action. Truth about another goal is insufficient. |
| Accepted report | Shared validator accepted evidence/classification. It is not a universal semantic intent or free-prose verifier. |
| Invalid attempt | Schema/permission/prerequisite/correction rejection. Some are injected busy conditions; counts are not automatically unsafe reasoning errors. |
| Model versus system | Corrected responses after feedback and automatic Python execution belong to the combined system, not an improvement in model weights. |
| Native operation | Actual bounded read/service/controller acquisition or command attempt; one bundled model tool can perform several. Failed source attempts still count. |
| Model request | Metered request reservation/attempt, including failures. Censored generation usage is unknown, not zero. |
| Output allowance | Per-call maximum or observed cumulative gate, not actual generated tokens. `256 * 8` is not a measured usage total. |
| Evidence independence | Separate evaluator state/transport and records, not independent authorship or a separate physical sensing technology. |
| Trace quality | Local callback/tool/native accounting plus exact persisted span IDs and closed trees; unrelated to whether a model solved the task. |
| Latency | Label whether agent/root time, task wall time or complete campaign overhead; loading, reset, audit and host load are not interchangeable. |

Report all-attempt costs and matched-success costs together. An arm that fails
early may look cheap; that is not successful-task efficiency. Small repeated
template sets do not become many independent task families. Within-backend
comparisons are primary. Do not pool different protocols, repaired interfaces or
serving profiles into an aggregate "project success rate."

## 9. Research history and important results

The following are separate campaigns. Historical values are taken from their
named reports; their definitions, fixtures and budgets differ. They are not a
single longitudinal controlled experiment.

### 9.1 Initial shared integration, stateful benchmark and simple caching

The initial setup established Windows/WSL/ROS2/Gazebo, actual local/hosted ROSA
tool calling, Phoenix and an isolated stateful world with independent scoring.
This answered the original Gates1–4 through **simple caching**, not original JTVR.

The clean Baseline v1 collection contains **540 scripted controls and 120 live
trials**. Its baseline terminal-handling scores were hosted 30/36 and local 24/36;
both verified all 18 achievable baseline goals. A separately labeled retrospective
stricter contract check gave hosted 30/36 and local 12/36. Do not substitute one
score definition for the other or add their denominators together.

Conservative caching saved 25% of eligible scripted reads, without demonstrated
live model-call savings. A local cached task timed out; apparent saved calls/work
from that failed attempt were not a valid cache efficiency benefit. Baseline v1
and its failures remain frozen. See the [baseline examination](artifacts/historical-stage4-context/BASELINE_V1_REVIEW_REPORT.md).

### 9.2 Original JTVR concept and actual policy comparison

The [original specification](../JTVR_Final_Technical_Specification_ID%281%29.md)
proposed joint deduplicated task/verification evidence obligations, conservative
validity/invalidation, cost-aware bounded prefix-plus-residual acquisition selection,
and guarded read-only continuations that can avoid additional inference. The strong
comparison includes amortized batching with the same reuse and continuation access.
It is not merely dependency filtering, a fixed bundle or a cache renamed JTVR.

The policy study ran **1,152 audited episodes plus 15 actual ROS smoke episodes,
with zero LLM requests**. On 96 primary paired fixtures, complete modeled costs
were greedy523.5915, batching482.7105 and JTVR482.7105. Batching/JTVR saved 7.81%
against greedy; JTVR added 0% over batching, tying all 96. Selector CPU was higher
for JTVR. Sensitivity included two JTVR losses. The 96 fixtures were not96
independent semantic task families.

The predefined criterion for full model integration was not met. A general custom
JTVR Runnable with live model approval/manifest extraction was not established as
a successful product. **Full JTVR remains paused.** This limited negative result
is not a theorem about all possible ROSA workloads. See the [policy report](artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md).

### 9.3 Closed simplified Stage 4 reliability/batching campaign

This ran **160 live attempts**,80/backend:48 reliability-intervention trials and
32 real-ROS-parameter trials per backend. The parameter comparison shared a
batching helper/evidence/continuation capabilities; it tested selection above that
helper, not helper speedup over untouched upstream ROSA.

| Parameter track | Reference | Automatic batching |
|---|---:|---:|
| Hosted strict completion | 16/16 | 16/16 |
| Hosted model requests | 67 | 67 |
| Hosted native CLI operations | 48 | 48 |
| Qwen strict completion | 0/16 | 0/16 |
| Qwen model requests | 60 | 60 |
| Qwen native CLI operations | 66 | 54 |

Neither retention screen passed. Qwen's lower work occurred in failed report
contracts, so a completed-task benefit was unestimable. The full campaign used
429 hosted and 576 local requests, below its frozen ceilings.

**Audit exception:** the frozen auditor passed 152/160 and found eight missing
recovery-stop spans. State checks passed; a separately labeled reconciliation used
raw requests/callbacks/world records. It did not manufacture missing spans or turn
the original FAILED supervisor into a full-audit pass. Later tracing fixes do not
retroactively repair these records. See [Stage 4 results](STAGE4_RESULTS.md) and
the [complete report](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md).

### 9.4 Reliability v1: repairs and initial one-joint Gazebo

This separate engineering study implemented consistent node-keyed contracts,
recoverable feedback, operation/write accounting and corrected trace-stop behavior.
Its A/B/C/D conditions were shared repaired reference, structured feedback,
automatic fresh verification and their combination.

Each backend completed **36/36** combined-system checks:32 mock plus 4 Gazebo
trials. The first physics fixture was **one joint**, not the later full UR5e.
The combined intervention did not meet its limited benefit screen over the
competent reference. Automatic checks sometimes added native work without more
correct outcomes. Guard-assisted correction is not error-free model behavior.
The named-verifier requirement in that early contract was itself a limitation;
later shared evidence reuse avoids requiring a redundant named tool merely for
its name. See [Reliability v1](artifacts/reliability-v1-20261022/REPORT_FOR_CHATGPT.md).

### 9.5 Reliability v2 and full-arm transfer

This collection contains **96 live trials and 482 model calls across versions**.
The first process completed 80 validation/mock trials, then failed an independent
UR5e reset before model-driven arm trials. A separately frozen controller-readiness
follow-up added 16 arm trials after four deterministic controls. This was not an
uninterrupted original run.

In the32-trial main mock matrix, Sol passed 32/32. **Qwen completed 32 but passed 28**:
A6/8, B8/8, C8/8, D6/8. Earlier progress claiming32/32 was corrected. On the UR5e,
Sol passed 4/4 in each A/D condition; Qwen passed 1/4 in each. The combined design
did not meet retention screens. Six Qwen arm failures stopped at output length
before a movement command; other errors must not be attributed to truncation.

The mixed write receipt `goal_verified=false` alongside a nested successful
automatic check was recorded as an interface ambiguity, not a proven cause.
See the [joined v2/UR5e report](artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md).

### 9.6 Qwen output-budget, concise-instruction and truncation-recovery diagnostic

This was Qwen-only; old 96-trial results stayed frozen. It compared L256/L512/L1024
output allowances, C256 concise tool-first instructions and R256 bounded length
recovery, with common context 8192 and cumulative/call/time limits.

| Condition | Correct scored trials | Healthy /2 | Recorded calls in scored trials | Known output tokens |
|---|---:|---:|---:|---:|
| L256 | 2/8 | 0/2 | 24 | 3,466 |
| L512 | 3/8 | 0/2 | 42 | 7,589 |
| L1024 | 5/8 | 1/2 | 48 | 8,425 |
| C256 | 1/8 | 0/2 | 25 | 3,520 |
| R256 | 2/8 | 0/2 | 49 | 7,791 |

There were **41 attempts:40 scored completions plus one unscorable external
interruption**, with a separately documented five-entry restart. The interrupted
entry's original attempt remains; its explicitly labeled replacement is not a
silent successful rerun. Some usage is incomplete, so known token counts are
lower bounds and scored-only cost tables exclude additional interrupted cost.

Larger output sometimes allowed physical action but did not meet the strict
benefit screen; concise prompting and length recovery also failed their screens.
R256 used 12 recoveries, adding calls without more correct outcomes than L256.
Do not claim1024 tokens solved Qwen, or that a256-token cap explained every failure.
The later profile 1024 is frozen explicitly in later studies, not applied backward.
See the [complete diagnostic](artifacts/output-budget-v1-resume-20261022/REPORT_FOR_CHATGPT.md).

### 9.7 Program-managed workflow live feasibility

Six cases/backend compared model-managed steps with program-managed execution.

| Backend | Model-managed | Program-managed | Model calls |
|---|---:|---:|---:|
| Qwen | 6/6 | 5/6 | 35 to28 |
| Sol | 6/6 | 6/6 | 29 to15 |

The two-backend progression gate failed. Qwen's problem included copying the
wrong entity key in reporting, motivating a **minimal shared observation-reference
interface**, not a model-specific repair or a new evidence database. See the
[live feasibility report](artifacts/workflow-live-v1-20261022/REPORT_FOR_CHATGPT.md).

### 9.8 Minimal report reference and initial UR5e workflow transfer

The common model interface now cites an existing observation ID rather than
reconstructing node keys and values. It reuses current evidence/validators.

| Environment / backend | Model-managed correctness | Program-managed correctness | Model calls |
|---|---:|---:|---:|
| Mock / Qwen | 4/4 | 4/4 | 26 to12 |
| Mock / Sol | 4/4 | 4/4 | 18 to9 |
| Gazebo / Qwen | 3/4 | 4/4 | 18 to14 |
| Gazebo / Sol | 4/4 | 4/4 | 19 to8 |

There were 32 live-trial audits. One run per case/condition establishes feasibility,
not a reliable generalized advantage. Qwen's baseline failure omitted execution
and truthfully reported FAILURE; a fault case was not fully exercised by that
reference. Some candidate native work increased. An earlier ZIP omitted one frozen
uv.lock copy; later packages explicitly include the actual applicable locks.
See [common reporting and transfer](artifacts/workflow-reference-v1-20261022/REPORT_FOR_CHATGPT.md).

### 9.9 Strong macro-skill reference and bounded continuation

The next three-condition pilot compared primitives, ordinary macro and custom
workflow on six cases/backend. Its joined36-cell matrix is complete, with the
original hosted quota interruption retained separately and only the four remaining
hosted cells completed under documented continuation.

| Backend | Primitives correct; calls | Macro correct; calls | Workflow correct; scoreable calls |
|---|---:|---:|---:|
| Qwen | 4/6;39 | 5/6;22 | 5/6;21 |
| Sol | 6/6;29 | 6/6;14 | 6/6;14 |

Sol workflow used 15 all-attempt requests including the interrupted generation,
not just14 scoreable calls. Macro/workflow shared the same acquisition policy.
A shared default ROSA prompt instructed unavailable discovery tools despite the
task requiring select_skill first. That instruction mismatch blocked clean broader
readiness conclusions. A trace/schema pass does not prove prompt consistency.
See the [joined report](artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md).

### 9.10 Separate prompt repair and validation

The bounded prompt adapter replaces only a recognized generic prefix, preserves
robot instructions and rejects unknown layouts rather than stripping arbitrary
content. Both conditions/backends share the repair.

Known-case validation ended with Qwen 9/9 and Sol 9/9 scoreable correct outcomes.
Sol has10 total attempt rows including one service-censored attempt; its all-attempt
request count is32. Qwen used 34 requests. A zero-inference continuation setup abort
and the initial service failure remain preserved. The generic service error did
not establish quota exhaustion. Three cold starts and 18 deterministic controls
validated the generated HOME-spawn correction before the final continuation.

Qwen still attempted an unjustified write with missing prerequisites; the guard
blocked it before dispatch and it corrected its report. The validation is not
evidence of error-free intrinsic model behavior or broad causal prompt benefit.
See the [final joined validation](artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_VALIDATION_REPORT.md).

### 9.11 Fresh macro-focus pilot:72 scheduled,69 recorded

This used six pose-domain cases, two repetitions, three conditions, two backends:
**72 scheduled cells, one underlying movement capability**.

| Backend | Primitives: primary passes; requests | Macro | Custom workflow |
|---|---:|---:|---:|
| Qwen | 8/11;61 | 9/11;31 | 7/11;34 |
| Sol | 12/12;60 | 12/12;32 | 12/12;32 |

Sol completed 36/36. Qwen recorded 33/36 before its frozen backend deadline;
the last recorded row is deadline-censored and three cells were unstarted.
All69 recorded attempt audits passed;12 deterministic controls passed. Six
Qwen requests have missing usage. The formal two-backend retention result is
**incomplete**, not an all-gates-passed study. It remains closed at its original
allowance; M4 is not its silent continuation.

Sol's macro saved 46.7% model requests over primitives, with 36 to38 native operations.
Among eight Qwen pairs where both macro/primitives passed, calls were 40 to22
(45% fewer), native24 to26. These subsets supplement all-attempt accounting.
Five Qwen task timeouts, three retry-policy failures and one backend-deadline
interruption have different meanings. Physical attainment without reporting can
still fail the task contract. The custom workflow showed no sufficient incremental
benefit; one apparent loss was censored, not intrinsic incompetence.

Decision: prefer finishing the simpler macro as an **engineering candidate**,
preserve the custom comparator and avoid another speculative mechanism. See the
[pilot report](artifacts/macro-focus-v2-20261026/REPORT.md) and
[accepted decision/roadmap](artifacts/macro-module-v1-20261027/ROADMAP_RECEIVED.md).

### 9.12 M1 reusable component

M1 separated the reusable module from experiment runners without deleting shared
workflow/session dependencies. Acceptance included strict registry/argument/scope
guards, copied permissions, stale/cross-task evidence checks, no uncertain-write
replay, pre-dispatch budgets, late-output withholding, immediate terminal handling,
actual adapter classes with fake transports, installation and examples.

Final focused tests 36/36 passed; other regression execution counts overlap and
must not be summed as unique tests. Twelve scripted paths matched543 persisted
spans; seven deterministic Gazebo cases matched87 spans. No live Qwen/Sol requests
were made during M1. The wheel retained upstream distribution version 1.0.10 with
internal component 0.1.0; it was not published or a fresh-OS installation test.
See [M1 acceptance](artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md).

### 9.13 M2 second capability and M3 live demonstration

M2 introduced read-only readiness with separately metered controller and joint
sources. Its ten deterministic Gazebo cases covered movement, already-satisfied
state, ineffective/partial execution, missing prerequisites, healthy/unready
inspection, missing sources and a deliberately rejected inspection write. Actual
controller deactivation differs from injected missing-source observations.
All10 passed with independent checks and no inspection trajectory publisher.

M3 ran movement, inspection and ambiguous preparation once per backend, plus
resolved deterministic references. Permission scope restricted read-only tasks;
the movement task exposed both capability types.

| M3 backend | Correct /3 | Model calls | Known input tokens | Known output tokens | Native ops | Agent root seconds |
|---|---:|---:|---:|---:|---:|---:|
| Deterministic reference | 3/3 | 0 | 0 | 0 | 5 | 4.037 |
| Qwen | 2/3 | 7 | 11,324 | 1,087 | 7 | 179.403 |
| Sol | 3/3 | 5 | 5,455 | 160 | 5 | 27.414 |

For “Prepare the arm,” Qwen inspected and submitted a factually correct SUCCESS
about readiness rather than asking what the user meant. It made no movement, but
failed goal alignment. This is neither a formatting problem nor an output-budget
failure. Sol asked for clarification without action. Qwen also corrected one
pre-selection read rejection in its successful movement case.

M2/M3 have19 passing trace audits and 331 matched spans. An outside-task HOME reset
precedes each M3 task; reset/audit/setup are not included in the table's agent-root
times. The deterministic runner predates small model-only timeout/accounting
hardening; per-backend source freezes retain that version difference. M2 lacked a
separate before-execution source freeze of its new capability files; earliest new
source snapshot is the subsequent deterministic M3 run. These engineering provenance
limits are disclosed rather than retroactively preregistered.

Final post-fix research discovery:230 tests,42 skipped,188 executed successfully;
two evaluation bound tests passed. M4 later skipped the optional Windows integration
test too:230 discovered,43 skipped,187 executed. Different counts are different
environment opt-ins, not silently lost test successes.

See the [combined report](docs/M2_M3_COMBINED_REPORT_2026-10-27.md). It contains later
amendments not present in the original immutable evidence ZIP: date-only heading,
inference-reserve recommendation and corrected dependency-lock wording.

## 10. Roadmaps and numbering

### Historical opening Gates1–4

Native Qwen tool calling; stateful mock/evaluator; actual ROSA compatibility;
simple caching/invalidation. The hosted comparator was a parallel track. A
completed Gate 4 rerun was not original JTVR or memory evaluation.

### Historical six research work packages

| Stage | Subject | Current interpretation |
|---|---|---|
| 1 | Shared local/hosted integration | Implemented and repeatedly exercised with actual ROSA. |
| 2 | Stateful benchmark and independent scoring | Implemented, subsequently revised prospectively; old contract/audit limitations retained. |
| 3 | Baseline/reliability experiments | Multiple separately versioned studies completed; no universal reliability improvement claim. |
| 4 | Caching/JTVR/batching | Agreed campaigns closed with negative/inconclusive findings and explicit audit exception; full JTVR paused. |
| 5 | Verified episodic memory | Deferred/unstarted; not a prerequisite or current required deliverable. |
| 6 | Gazebo, potentially later hardware | Bounded UR5e integration now demonstrated; physical hardware untested/unspecified. |

The [old six-stage document](docs/PROJECT_ROADMAP_SIX_STAGES.md) records its
2026-10-21 state. Its “arm not configured” and future-work wording is historical,
not the current state. Stage 6 was allowed to precede Stage 5.

### Current product-completion roadmap

| Milestone | Goal | Status / next boundary |
|---|---|---|
| M1 | Package the existing bounded macro as a reusable component | Checkpointed; engineering acceptance complete. |
| M2 | Demonstrate a genuinely different capability | Accepted: read-only readiness plus movement; no second actuator. |
| M3 | Runnable natural-language selection/demo, deterministic reference and faults | Demonstration/attempts complete; Qwen ambiguity failure remains a documented limitation. |
| M4 | One final focused paired primitives-versus-macro evaluation | Closed:80/80 recorded/audited and8/8 reviews; Sol passes retention, Qwen fails. |
| M5 | Consolidate the project deliverable and research conclusions | Technical delivery complete locally: trace review, packet, tables, report, ledger, wheel and video. Eight human ratings preserved; owner-feedback interpretation closed2026-10-30. Independent human adjudication under the frozen criterion not obtained. Evaluation off-machine backup deferred; local retention selected2026-10-28. |

**M4 is not historical Stage 4, and M5 is not historical Stage 5 memory.** The
October 30 return plan was later resumed by explicit user instructions; its old
date is not an instruction to suspend current work until that date.

## 11. M4 protocol and current decision boundary

The [frozen M4 protocol](docs/M4_MACRO_PROTOCOL_2026-10-27.md) and
[`freeze.json`](artifacts/macro-m4-20261027/freeze.json) are authoritative for this
campaign. Current read-only results do not authorize a protocol change.

### Design

Ten families x two repetitions x two conditions x two backends =80 live trials,
40/backend and 20/condition/backend. Paired condition order is counterbalanced;
the second repetition rotates cases and the other backend reverses condition
order. Sol runs first, Qwen second; simulator access is serialized.

Families: constrained named-pose selection; already-satisfied goal; suppressed
ineffective command; actual partial wrist command; missing movement prerequisite;
healthy inspection; actually inactive trajectory controller; missing controller
observation; missing joint observation; ambiguous intent requiring clarification.

M4 catalogue binds stage_left pan=-0.14/wrist3=0.20 and park_right pan=0.16/wrist3=-0.12,
plus home and readiness inspection. All targets remain in the existing bounds.
M3's offset pan0.18/wrist3=0.16 is a different example, not a silently changed
M4 target. No prior failed live trial is replaced by an M4 cell.

### Limits and recovery

| Budget | M4 value |
|---|---|
| Charged model calls/task | 8 |
| Observed generated-token threshold/task | 2,048 |
| Local per-call generation maximum | 1,024 within remaining allowance |
| Native operations / tool attempts / corrections | 10 /16 /3 |
| Movement dispatches | At most 1; some cases require0 |
| Task wall allowance | 360 seconds, common to both conditions/backends |
| Backend ordinary request slots | 320 |
| Separate backend infrastructure reserve | 3 |
| Backend / combined request ceiling | 323 /646 |
| Backend wall ceiling | 8 hours including setup/audit/recovery; not a forecast |

The new360-second allowance is prospective; old 180-second results remain unchanged.
The larger campaign ceiling is intended to accommodate the whole bounded schedule
rather than reproduce the earlier aggregate-deadline censoring.

Only explicit eligible HTTP 502/503/504 can use the reserve: one retry/logical call,
one-second backoff, three shared reserve slots/backend. Auth/scope/quota categories,
HTTP 429, transport timeouts, truncation and invalid tool output are not automatic
infrastructure retries. A returned retry completion still consumes a normal
decision slot. Every attempted request and unknown usage remain in cost accounting.
The pre-parser request may retry; a whole trial or uncertain robot command may not.
Primary completion and completion including infrastructure recovery stay separate.

### Retention and interpretation

The per-backend **engineering screen**, fixed before results, requires complete
paired cells, all quality audits, no dispatch violations, no greater number of
primary failed tasks than primitives, at least 25% fewer model requests on jointly
successful pairs, and at most 25% extra native operations on those pairs. It is not
a population-level equivalence/noninferiority proof. All-attempt costs, paired
wins/losses and failures accompany the matched-success subset.

All eight live clarification transcripts were reviewed with the frozen rubric:
four Sol passes and four Qwen failures. Operator review by Codex is not independent
human adjudication. The initial automatic report was a checkpoint; the final
report and closeout record now document the completed interpretation.

### Completed M4 result and decision

Sol:20/20 in each condition,68→38 requests,328.36→194.58 task seconds,
38→40 native operations. Macro saved44.1% calls and40.7% task time with5.3% more
native work. Mean task time16.42→9.73 seconds. Closed backend runtime17.68 minutes.

Qwen:15/20 primitives versus14/20 macro;91→53 requests,2,669.72→1,703.63
task seconds,50→48 native operations. Mean task time133.49→85.18 seconds;
closed backend runtime81.97 minutes. These all-attempt savings accompany a loss
of one primary pass and do not meet the preset no-greater-failure requirement.
On13 jointly successful pairs, calls53→28 (47.2% fewer), native31→29. The macro
has one paired win and two losses; both losses are partial-command cases.

All11 Qwen failures selected readiness inspection, including seven explicit
movement requests and four ambiguous requests that required clarification.
Five later terminated on output length; this does not establish truncation as
the cause of the preceding wrong capability choice. Qwen accepted five grounded
readiness SUCCESS reports for the wrong/unresolved goal (two primitive, three
macro). Unsupported selected-evidence success attempts and dispatch violations
were zero; those metrics do not establish correct user intent.

All80 live audits matched3,290 persisted spans; controls add202 spans. Both
simulators cleaned up;250 total model requests, no infrastructure retry, incomplete
usage, censored or unstarted cells. The old supervisor phase still says review
required; `closeout.json` records subsequent completed review and mixed findings.

Decision: keep the module as an optional bounded engineering capability, document
the positive Sol result and failed Qwen screen together, and consolidate in M5.
Do not claim a general local-model reliability improvement or adopt macro as an
unconditional cross-model default. No new experiment or architecture was launched.

If results show useful efficiency without observed correctness loss, retaining
the module for consolidation may be justified. If correctness falls, examine the
trade-off rather than hiding it. If no useful advantage exists, prefer the simpler
effective solution. If incomplete, preserve all attempts and consider a separately
documented continuation only if justified and authorized. Do not silently extend
time/request limits or rerun failures until they pass.

## 12. Known limitations and unresolved questions

1. No broad held-out task, model, robot or hardware generalization is established.
   Ten M4 families with two repetitions do not make80 independent task families.
2. Only one actuated movement capability is configured. Inspection is real but
   modest; it is not perception, grasping, dual-arm coordination or a second actuator.
3. M3/M4 are separate skill invocations, not general multi-skill task planning.
4. Explicit application permissions and strict controller guards protect actions;
   their success does not prove that a model inferred intent or acted error-free.
5. A truthful accepted report can answer the wrong user goal. Free prose is not
   exhaustively verified; structured-claim metrics have narrower scope.
6. The read-only readiness skill is not a certificate of collision safety or a
   reusable authorization token. Current evidence is required for later actions.
7. The snapshot's `selected_max_writes` defaults to1 before selection, even for a
   read-only catalogue. It is a diagnostic limitation, not the actual permission
   boundary; catalogue/dispatch guards still enforce zero inspection writes.
8. The inherited per-node reused-verification summary can retain only the first
   same-node source entry. Original inspection observations/native ledgers retain
   both source IDs. Do not claim the compact summary is complete field-level provenance.
9. Hosted/local generation controls are not identical hard provider-side token
   caps. Missing usage, cold loads, partial offload, order and host activity limit
   compute/latency conclusions.
10. Some earlier studies have prompt-contract, tracing or continuation exceptions.
    Later repairs do not make those old studies clean or erase their failures.
11. A working clean-target wheel test is not complete portability across fresh
    operating systems/ROS installations or all teammate adapters.
12. A macro's call savings can follow ordinary packaging. Novelty beyond prior
    skill/macro-action/workflow ideas has not been established by these experiments.
13. Successful protected renewal across processes is not an overnight endurance
    guarantee. Backend quota/service availability remains independent of token renewal.
14. Local commits are not off-machine backup. Some evidence is local/untracked;
    publication requires checking intended commits/files and actually pushing them.
15. M4's Windows supervisor may leave process exit_code null; authoritative outcome
    evidence is the backend checkpoint, closed audits and cleanup, not inventing
    a zero exit code from absent launcher metadata.

Do not address each individual Qwen mistake by inventing a new architecture. A
concrete engineering defect may warrant a separately tested repair; an unfavorable
model outcome may simply need to remain a documented limitation.

## 13. Team package and compatibility

The teammate's [TEAM_SETUP copy](docs/TEAM_SETUP_RECEIVED_2026-10-26.md) describes
`rosa-llm[langchain]==0.1.0`, `create_client`, `ChatRosaLLM`, provider configuration
and OAuth login. That is a proposed/common **backend integration package**, not
the bounded execution/evidence/skill module itself. Its setup instructions are
context; their inclusion here does not authorize installing/migrating during M4.

Our experiments currently use ConfiguredChatOllama and ChatSiwc with their existing
validation, usage, continuation and cleanup behavior. A future adapter bridge may
be feasible but is not100% compatibility already demonstrated. Check tool binding,
schemas, response/finish metadata, token accounting, callback spans, cancellation,
private continuation, client lifetime and credential isolation before changing it.
Use fake-provider/contract tests before a separately versioned live comparison.

The user asked to park the migration and finish the accepted roadmap. It remains
parked; Docker, another backend package, or a paid API key is not a current milestone
prerequisite. Each teammate must use their own credentials.

Verified episodic memory is also parked. A future study would require tasks where
history changes a decision, matched no-memory/fixed-example/unverified-memory
references, token/context controls and provenance/freshness tests. Stored success
must not replace current observation or authorize movement. No memory subsystem
has been experimentally validated here.

## 14. Evidence and archive index

Paths below are local project evidence. Their presence does not prove remote
publication. A chatbot receiving only this Markdown has the summary and references,
not the raw files; upload relevant reports/ZIPs for deeper independent examination.
An archive's SHA256 sidecar establishes byte identity, not scientific validity.

| Subject | Main readable record |
|---|---|
| Preserved baseline / Gates1–4 | [Baseline examination](artifacts/historical-stage4-context/BASELINE_V1_REVIEW_REPORT.md) |
| Original-spec acquisition study | [Policy report](artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md) |
| Closed Stage 4 live study | [Final Stage 4 report](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md) |
| Reliability v1 | [First repair/one-joint report](artifacts/reliability-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Reliability v2 / UR5e | [Joined full-arm report](artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md) |
| Output/truncation diagnostic | [Joined diagnostic report](artifacts/output-budget-v1-resume-20261022/REPORT_FOR_CHATGPT.md) |
| Program-managed feasibility | [Workflow live report](artifacts/workflow-live-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Observation-reference transfer | [Reporting/transfer report](artifacts/workflow-reference-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Strong macro reference / continuation | [Joined macro report](artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md) |
| Final known-case prompt validation | [Joined validation report](artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_VALIDATION_REPORT.md) |
| Incomplete fresh 72-cell pilot | [Macro-focus report](artifacts/macro-focus-v2-20261026/REPORT.md) |
| Accepted M1–M5 plan | [Decision/roadmap received](artifacts/macro-module-v1-20261027/ROADMAP_RECEIVED.md) |
| M1 | [Acceptance report](artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md) |
| M2/M3 | [Current combined report](docs/M2_M3_COMBINED_REPORT_2026-10-27.md) |
| Public module | [v0.2 README](../rosa-research/docs/MACRO_CAPABILITIES_V2_README.md), [specification](../rosa-research/docs/MACRO_CAPABILITIES_V2_SPEC.md) |
| OAuth repair | [Live renewal validation](../rosa-research/docs/REMEMBERED_AUTH_ROTATION_VALIDATION_2026-10-27.md) |
| Completed M4 | [Final report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md), [timing](docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md), [protocol](docs/M4_MACRO_PROTOCOL_2026-10-27.md), [status entry](MILESTONE_M4_STATUS.md), [freeze](artifacts/macro-m4-20261027/freeze.json) |

Major archives, each with a corresponding `.sha256` sidecar:

| Campaign | ZIP |
|---|---|
| Original policy tier | [stage 4-policy-20261021-evidence.zip](artifacts/stage4-policy-20261021-evidence.zip) |
| Closed Stage 4 live tier | [ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip](artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip) |
| Reliability v1 | [ROSA_RELIABILITY_V1_COMPLETE_REVIEW_2026-10-22.zip](artifacts/ROSA_RELIABILITY_V1_COMPLETE_REVIEW_2026-10-22.zip) |
| Reliability v2 / arm | [ROSA_RELIABILITY_V2_UR5E_COMPLETE_EVIDENCE_2026-10-22.zip](artifacts/ROSA_RELIABILITY_V2_UR5E_COMPLETE_EVIDENCE_2026-10-22.zip) |
| Output diagnostic | [ROSA_OUTPUT_BUDGET_V1_COMPLETE_REVIEW_2026-10-22.zip](artifacts/ROSA_OUTPUT_BUDGET_V1_COMPLETE_REVIEW_2026-10-22.zip) |
| Workflow feasibility | [ROSA_WORKFLOW_LIVE_V1_COMPLETE_EVIDENCE_2026-10-22.zip](artifacts/ROSA_WORKFLOW_LIVE_V1_COMPLETE_EVIDENCE_2026-10-22.zip) |
| Report-reference transfer | [ROSA_WORKFLOW_REFERENCE_V1_EVIDENCE_2026-10-22_COMPLETE.zip](artifacts/ROSA_WORKFLOW_REFERENCE_V1_EVIDENCE_2026-10-22_COMPLETE.zip) |
| Joined macro reference | [ROSA_MACRO_TRANSFER_V1_COMPLETE_WITH_CONTINUATION_2026-10-23.zip](artifacts/ROSA_MACRO_TRANSFER_V1_COMPLETE_WITH_CONTINUATION_2026-10-23.zip) |
| M1 | [ROSA_MACRO_MODULE_V1_M1_ENGINEERING_2026-10-27.zip](artifacts/ROSA_MACRO_MODULE_V1_M1_ENGINEERING_2026-10-27.zip) |
| M2/M3 | [ROSA_MACRO_M2_M3_ENGINEERING_AND_LIVE_DEMO_2026-10-27.zip](artifacts/ROSA_MACRO_M2_M3_ENGINEERING_AND_LIVE_DEMO_2026-10-27.zip) |
| M4 final reviewed study | [ROSA_M4_FINAL_REVIEW_2026-10-27.zip](artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.zip), [verification](artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.verification.json) |

M1 ZIP SHA256:
`4057039c91eaaa40b512a4925b5fad324f1f4174a0614625b18a246ed82e7be8`.
M2/M3 ZIP SHA256:
`bbb06874a10b54e77e4054853eb5d4ea1479d2ce0701e4f6fccd0d6193b71415`.
M2/M3's382 manifest file hashes matched archived bytes. Its original packaged
report remains immutable; the newer canonical report includes labeled amendments.

M4 final package:947 manifest file hashes verified, ZIP integrity and secret-pattern
scan passed. SHA256:
`fb3a47aecfaaa380cb295ef5bfa8cca5d4511f2c842dc783144b5ba6a747b0ab`.
The original pre-review execution ZIP is preserved; its933 manifest entries were
also rechecked. The packaged handoff snapshot predates this archive-verification
note; it already records the completed experiment and mixed scientific findings.

M4 checkpoint and per-trial records (execution is now closed):

```text
artifacts/macro-m4-20261027/freeze.json
artifacts/macro-m4-20261027/controls/checkpoint.json
artifacts/macro-m4-20261027/operator/status.json
artifacts/macro-m4-20261027/operator/<backend>-stdout.log
artifacts/macro-m4-20261027/<backend>/checkpoint.json
artifacts/macro-m4-20261027/<backend>/<job>/inference-progress.json
artifacts/macro-m4-20261027/<backend>/<job>/result.json
artifacts/macro-m4-20261027/<backend>/<job>/trace.json
artifacts/macro-m4-20261027/<backend>/<job>/phoenix-audit.json
artifacts/macro-m4-20261027/clarification-review.json
```

The supervisor generated analysis.json, M4_EXECUTION_REPORT.md and the
ROSA_M4_EXECUTION_CHECKPOINT_2026-10-27.zip/sidecar before final Qwen review.
That original archive is preserved. The reviewed analysis and detailed final
report are later derived products; pre-review versions are retained under
`review-history/execution-checkpoint/`. The final review package is separately
named ROSA_M4_FINAL_REVIEW_2026-10-27.zip with its own manifest and sidecars.
Consult its verification file before claiming final-package integrity.

## 15. Operational handoff

### Safe inspection during the active study

M4 has now finished; the restrictions below describe active frozen campaigns,
not a requirement to keep a completed worker or simulator running. Do not rerun
the closed populated M4 directories. Next work is consolidation, not a restart.

Read checkpoints/logs and verify actual process identity/start time before
concluding a worker is alive or dead. PIDs can be reused. A progress count records
trial rows, not necessarily finished audits; the last row may temporarily lack its
persisted audit while that audit is running. Never infer the remaining cells from
one backend's successes or the last log line.

Do not restart WSL, rerun a populated backend, edit frozen sources/prompts/scorers,
upgrade dependencies, change Ollama settings or launch a second simulator while
M4 is active. A configuration change needs a separately versioned prospective
study. This is about reproducibility and process continuity, not a claim that
every editor update necessarily kills every detached process.

The existing supervisor is `reports/m4-run.ps1` at workspace level; it starts
Sol then Qwen and packages an execution checkpoint. Do not invoke it again on the
same populated outputs. It does not create a temporary automatic sleep hold;
keep the machine running and awake. Do not assume an older study's sleep hold
still protects the current campaign.

### Environment access, not system reinstallation

The original setup-robotics.ps1 installs system prerequisites. It is not an
activation script to rerun every time. In WSL, for read-only documentation refresh:

```bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
/home/martin/.local/share/rosa-envs/research/bin/python -B -m tools.project_context --refresh
```

For later module development, source ROS2 Jazzy and use the existing research
environment. The public [capability README](../rosa-research/docs/MACRO_CAPABILITIES_V2_README.md)
contains demo commands; **do not run those simulators concurrently with M4**.
Phoenix's local UI is http://127.0.0.1:6006. Use existing wrappers for its separate
environment. Do not casually uv-sync/update a frozen environment during a campaign.

### After execution stops

1. Confirm per-backend status, scheduled/attempted/completed/unstarted counts,
   audit completeness, cleanup and actual request/usage accounting.
2. Review all required clarification transcripts; retain automated scores and
   review overlay, with matched answer digests and reviewer attribution.
3. Aggregate all attempts and matched-success pairs, actor/native work, faults,
   latency/overhead and paired correctness. Distinguish unknown usage from zero.
4. Apply the frozen engineering screen without changing its thresholds after
   seeing results; document uncertainty and any incomplete schedule.
5. Produce the final interpretation/evidence package and update this overview.
   Commit intended files on member/martin, preserving unrelated working changes.
   Do not claim remote publication without actually checking/pushing it.
6. Decide whether to consolidate in M5 or report a limitation/negative result.
   Do not launch memory, JTVR, another architecture or hardware as an automatic
   response to an unfavorable comparison.

This document is context, **not blanket authorization** for a new experiment,
consent flow, package migration, destructive cleanup, publication or hardware action.
Current user instructions and frozen experimental boundaries still apply.

## 16. Maintenance and user preferences

The user explicitly requested this continuing master record so a new chatbot does
not reconstruct the project from incomplete conversation memory. Keep this file
as the single main overview; add detailed reports as evidence rather than replacing
the whole history with the most recent favorable result.

- Update after a milestone, material result, correction, roadmap decision or
  implementation change. Refresh the status block before sharing/reporting live work.
- Treat this as an ongoing progress report. Maintain current work, measured
  completion, blockers/open gates, decisions and the next concrete actions near
  the front. Do not merely append another historical entry after completing work.
- Before a substantive project handoff, reconcile current status, roadmap,
  experiment interpretation, limitations and decision log with the evidence.
  Mark completed, stopped, waiting and unstarted work accurately; remove obsolete
  present-tense statements while preserving historical results.
- Record date, evidence source, actual denominator, study version and exceptions.
  Keep numbers and status conditional when work is active/unreviewed.
- Preserve original protocols, source freezes, scores, failed attempts and ZIPs.
  Add errata/continuation reports instead of retroactive repairs.
- Separate a user-approved decision from a chatbot suggestion or an attached
  plan's instructions. Do not execute a quoted proposal merely because it appears here.
- Be objective and direct. Do not sugarcoat Qwen failures or sell ordinary
  engineering as a new algorithm. Also do not conclude permanent model incapability
  from one small, constrained or interrupted experiment.
- Prefer small model-independent interfaces and competent simpler comparisons.
  Keep model behavior, feedback-corrected outcomes and automatic assistance distinct.
- Avoid unnecessary confirmations. The user has opted into encrypted remembered
  sign-in; ask for actual new consent only when necessary, never auto-approve it.
- Keep reports easy to share with ChatGPT/another assistant, with dates but no
  geographic heading. Never include tokens/secrets in the "complete" information dump.
- Preserve branch member/martin, existing uv environments, pinned serving profiles
  and installed model weights unless a new authorized task requires a change.

The refresh helper is read-only with respect to experiments. It updates this
file's marked status block, PROJECT_LIVE_STATUS.json and the linked M4 efficiency/
timing checkpoint only. It does not silently
maintain every narrative paragraph: the assistant must update the interpretation
when a result/decision changes. Do not advertise automatic realtime maintenance.
Background trials do not rewrite the narrative by themselves. During active work,
refresh when inspecting/reporting progress; after a run closes or a decision
changes, update the narrative and next actions as well. Do not imply that this
assistant continuously edits files while no assistant task or refresh process runs.

## 17. Decision log and corrections

| Decision/correction | Current consequence |
|---|---|
| Shared ROSA interface for local and hosted backends | Keep both as valid candidates; compare architecture within each backend. |
| Preserve Baseline v1 and separate retrospective scoring | Never rewrite history to make a repair look like an old success. |
| Original JTVR did not beat strong batching | Pause full JTVR; do not rename fixed bundles/caching as that algorithm. |
| Closed Stage 4 audit had eight missing spans | Preserve original failure plus separate reconciliation; no all-audits-passed claim. |
| Correct interface/tracing/budget issues before wider integration | Repairs are prerequisite engineering, not automatically research gains. |
| Qwen v2 mock32/32 progress claim was wrong | Correct result28/32; read aggregates, not just final log entries. |
| More output/concise prompting/length recovery did not meet screens | Retain diagnostic findings; no endless serving rescue campaign. |
| Minimal observation-reference reporting | Remove deterministic copying without a new evidence subsystem. |
| Generic prompt required unavailable tools | Repair prospectively and validate separately; preserve old inconsistent studies. |
| Fresh72-cell pilot recorded only69 attempts | No complete two-backend retention claim; three cells unstarted, one recorded deadline-censored. |
| Simple macro matched the custom policy closely | Finish the simpler engineering candidate; preserve shared base infrastructure. |
| No configured gripper/second actuator | Choose honest read-only readiness as the second capability. |
| M3 Qwen reported true readiness for ambiguous intent | Goal correctness and evidence truth must be scored separately. |
| Protected credential rotation failed after initial saving worked | Apply focused Windows atomic-replacement fix; retain failure and verify real resume. |
| M4 recovery reserve approved prospectively | Keep ordinary budgets, charge every attempt, restrict retries and never replay robot commands. |
| Some README/status sections are historical | This overview and dated actual checkpoints determine current planning; old files remain evidence. |
| M4 completed with mixed backend findings | Sol meets the retention screen; Qwen fails15/20→14/20 despite savings. Keep optional module, consolidate honestly; no universal reliability claim. |

For a new assistant: read this document, refresh/inspect actual current state,
then follow the user's requested task. Do not claim the project is finished,
all stages passed, the full ROSA catalogue was benchmarked, Qwen was trained,
memory/JTVR was completed, or physical robot safety was demonstrated.
