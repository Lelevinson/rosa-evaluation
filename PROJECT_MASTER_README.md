# Improved ROSA — living progress report and master project record

Updated: **2026-11-21**. Maintained project context, decision history and evidence map.

> **Where to start (2026-11-21).** The current state is the dated entries at the top of
> [section 2](#2-current-verified-status), newest first. For the report, start with
> [Results at a glance](#results-at-a-glance-all-studies) and the
> [Claims ledger](#claims-ledger-what-the-report-may-and-may-not-say). **All studies are closed and the
> project is frozen** at tag `freeze-2026-11-21` (see [FREEZE.md](FREEZE.md)). New work is on branch
> `member/martin-f1` (F1 Stage 0, design only). Older dated checkpoint blocks, the superseded
> 2026-11-18 presentation briefing and historical section 2 checkpoints are kept unchanged in
> [Appendices A–C](#appendix-a--chronological-checkpoint-archive-2026-10-27-to-2026-11-20). Words such as
> "current", "latest", "pending" or "running" there describe that moment, not today.
> **Git status 2026-11-21:** `member/martin` on GitHub is at `988cfd8`, pushed by Martin on 11-20.
> Everything after it is local: the freeze commit `0cd6748`, the tag `freeze-2026-11-21`, the later
> `member/martin` documentation commits and branch `member/martin-f1`. Pushing them awaits Martin.

This is the maintained progress report and main overview for handing this project to another chatbot, researcher
or teammate. It separates implemented software, measured results, unfinished work,
proposals and historical plans. It is a summary with links to detailed evidence,
not a substitute for every raw transcript or a claim that every hypothesis worked.
It contains no credentials. Dates are shown without a geographic location.

Start with [current work, progress, gates and next actions](#2-current-verified-status).
For a compact end-to-end summary, use the [M1–M5 recap](docs/M1_M5_RECAP_2026-10-30.md).
The later [ChatGPT/Claude discussion assessment](docs/M5_EXTERNAL_DISCUSSION_ASSESSMENT_2026-10-30.md)
checks the recovery hypothesis against exact saved messages and includes a
retrospective scoring-sensitivity illustration. M6 is proposed, not authorized;
no M6 runtime change or new M6 experiment has started.
The [follow-up wording clarification](docs/M5_CONDITION_WORDING_CLARIFICATION_2026-10-30.md)
explicitly records that M4 compares execution mode with its mode-specific
instruction; their effects on selection are not isolated. M6 and the proposed
first-turn wording probe remain unstarted and unauthorized.
That section describes where the project stands now. The research history below
supports current decisions; it does not replace an up-to-date progress report.

**M1–M5 delivery summary:** the project improves ROSA's surrounding software, not the LLM's
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

**Review and delivery history (2026-10-27–30):** the user supplied Claude's assessment of this overview.
Our [recorded assessment and proposed M5 priorities](docs/M4_EXTERNAL_REVIEW_ASSESSMENT_2026-10-27.md)
emphasize truthful evidence versus correct intent, a concise claim ledger,
appropriately qualified uncertainty and human clarification review. Qwen's failed
engineering gate is not proof of harm; the small study also does not establish
equivalent reliability or a difference that is definitely just noise. A suggested
selection diagnostic remains future work; M5 backup and delivery were subsequently authorized and completed within their documented scope.
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
A verified supplement extends evaluation protection through be32a23. The later
ec42ee7 recap commit and subsequent documentation edits are not implicitly
included in that pinned backup; the local backup manifest records its exact scope.
M4 scores/archives are unchanged; no new research
experiment was launched. All M5 trace interpretation is retrospective.

For a teammate: this Markdown file contains the narrative and main results.
Relative links to detailed reports, source and archives require their companion
files; the latest evaluation documentation has not been pushed to GitHub.
If the teammate will independently rate the eight clarification cases, give them
the original blank review ZIP before this overview, which contains the prior
results and interpretations.

## Contents

- [Results at a glance (all studies)](#results-at-a-glance-all-studies)
- [Claims ledger](#claims-ledger-what-the-report-may-and-may-not-say)

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

- [Appendix A — Chronological checkpoint archive](#appendix-a--chronological-checkpoint-archive-2026-10-27-to-2026-11-20)
- [Appendix B — Presentation briefing for 2026-11-18 (superseded)](#appendix-b--presentation-briefing-for-2026-11-18-superseded)
- [Appendix C — Historical section 2 checkpoints](#appendix-c--historical-section-2-checkpoints)

## Results at a glance (all studies)

Added 2026-11-21. One row per study and backend. **P → M** is model-managed primitives → bounded macro
within the same backend. Correctness and costs are **as reported in the linked source**. Every figure
in this table was checked mechanically against that file when the table was built (each row has
literal source strings that must match). Denominators differ between studies, and settings, cases
and hardware differ too. **Do not pool rows or compare across studies**; see the claims ledger below and §12.
F1 Stage 0 (2026-11-21) is design only, with no trials, so it has no row.

| Study (date) | Setting | Backend | Denominator | Correctness | Cost | Source |
|---|---|---|---|---|---|---|
| Stage 4 batching (2026-10-21) | mock + Gazebo, 4 arms | Sol | 80 attempts | 6 failures / 80 | — | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | 80 attempts | 72 failures / 80; retention screen not met for either backend | — | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md) |
| Reliability v1 (2026-10-22) | mock 4 arms (A–D) + Gazebo A/D | Sol | mock 8 per arm; Gazebo 2 per arm | every arm 8/8 (mock), 2/2 (Gazebo) | 164 model calls | [REPORT_FOR_CHATGPT.md](artifacts/reliability-v1-20261022/REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | same | every arm 8/8 (mock), 2/2 (Gazebo) | mock calls 43 (A) → 38 (D) | [REPORT_FOR_CHATGPT.md](artifacts/reliability-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Reliability v2 + UR5e (2026-10-22) | mock 4 arms, validation, Gazebo UR5e | Sol | 96 live trials (both backends) | mock 32/32; Gazebo 4/4 per arm | retention screen not met | [REPORT_FOR_CHATGPT.md](artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | same | mock 28/32 (A 6/8, B 8/8, C 8/8, D 6/8); Gazebo 1/4 per arm | retention screen not met | [REPORT_FOR_CHATGPT.md](artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md) |
| Qwen output budget (2026-10-22) | UR5e, 5 conditions × 8 | Qwen | 40/40 trials | L256 2/8, L512 3/8, L1024 5/8, C256 1/8, R256 2/8; no candidate retained | — | [REPORT_FOR_CHATGPT.md](artifacts/output-budget-v1-resume-20261022/REPORT_FOR_CHATGPT.md) |
| Workflow live (2026-10-22) | mock, 6 cases | Sol | 6 per condition | model 6/6, program 6/6 | calls 29 → 15 | [REPORT_FOR_CHATGPT.md](artifacts/workflow-live-v1-20261022/REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | 6 per condition | model 6/6, program 5/6; progression gate False | calls 35 → 28 | [REPORT_FOR_CHATGPT.md](artifacts/workflow-live-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Report reference + UR5e (2026-10-22) | mock + Gazebo, 4 cases each | Sol | 4 per cell | all 4/4 | Gazebo calls 19 → 8 | [REPORT_FOR_CHATGPT.md](artifacts/workflow-reference-v1-20261022/REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | 4 per cell | mock 4/4 both; Gazebo model 3/4, program 4/4 | Gazebo calls 18 → 14 | [REPORT_FOR_CHATGPT.md](artifacts/workflow-reference-v1-20261022/REPORT_FOR_CHATGPT.md) |
| Macro transfer (2026-10-23) | Gazebo UR5e, 6 cases × 3 conditions | Sol | 6 per condition | model / macro / workflow 6/6 each | calls 29 / 14 / 14 | [COMBINED_REPORT_FOR_CHATGPT.md](artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | 6 per condition | model 4/6, macro 5/6, workflow 5/6 | calls 39 / 22 / 21 | [COMBINED_REPORT_FOR_CHATGPT.md](artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md) |
| Prompt-contract validation (2026-10-26) | known cases, 3 conditions | Sol | 9 scoreable (1 censored) | 9/9 | calls 16 / 8 / 8 (model / macro / workflow) | [COMBINED_VALIDATION_REPORT.md](artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_VALIDATION_REPORT.md) |
|  |  | Qwen | 9 | 9/9 | 34 requests | [COMBINED_VALIDATION_REPORT.md](artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_VALIDATION_REPORT.md) |
| Macro-focus pilot (2026-10-26) | 6 cases × 2 reps × 3 conditions | Sol | 12 per condition | model / macro / workflow 12/12 each | calls 60 / 32 / 32 | [REPORT.md](artifacts/macro-focus-v2-20261026/REPORT.md) |
|  |  | Qwen | 33 of 36 rows (stopped) | model 8/11, macro 9/11, workflow 7/11; no retention claim | calls 61 / 31 / 34 | [REPORT.md](artifacts/macro-focus-v2-20261026/REPORT.md) |
| M1 reusable module (2026-10-27) | engineering acceptance | — | no live trials | accepted | 0 live model requests | [M1_ACCEPTANCE_REPORT.md](artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md) |
| M2 / M3 (2026-10-27) | Gazebo UR5e | deterministic / Sol / Qwen | M2 10 cases; M3 3 per backend | M2 10/10; M3 deterministic 3/3, Sol 3/3, Qwen 2/3 | — | [M2_M3_COMBINED_REPORT_2026-10-27.md](docs/M2_M3_COMBINED_REPORT_2026-10-27.md) |
| **M4** (2026-10-27) | Gazebo UR5e, 10 families × 2 reps | Sol | 20 per condition | primitives 20/20 → macro 20/20 | requests 68 → 38; mean task s 16.42 → 9.73 | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md) |
|  |  | Qwen | 20 per condition | primitives 15/20 → macro 14/20 | requests 91 → 53; mean task s 133.49 → 85.18 | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md) |
| Qwen serving Phase 1 (2026-11-13) | replay of M4 inputs, no tools | Qwen A vs B | 11 unique inputs | tool-call agreement 7/10 (9/10 required); B not retained | median gen tok/s 8.388 vs 8.082 | [QWEN_SERVING_PHASE1_REPORT_2026-11-13.md](docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md) |
| Lab local-model replication (2026-11-17) | lab Gazebo, M4 families, 40 per condition | Qwen3.5 9B | 36 known-goal per condition | primitives 27/36 → macro 28/36 | calls 188 → 98 | [DETAILED_COMPARISON_REPORT.md](artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md) |
|  |  | Ministral 3 8B | same | 28/36 → 28/36 | calls 156 → 82 | [DETAILED_COMPARISON_REPORT.md](artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md) |
|  |  | Llama 3.1 8B | same | 0/36 → 0/36 (integration failure) | calls 211 → 193 | [DETAILED_COMPARISON_REPORT.md](artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md) |
|  |  | Granite 3.3 8B | same | 0/36 → 0/36 (integration failure) | calls 40 → 40 | [DETAILED_COMPARISON_REPORT.md](artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md) |
| Qwen lab repeat (2026-11-17) | second run of the replication | Qwen3.5 9B | 36 known-goal per condition | primitives 26/36 → macro 28/36 | calls 185 → 97 | [QWEN_LAB_REPEAT_COMPARISON_REPORT.md](artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_COMPARISON_REPORT.md) |
| Llama/Granite integration diagnosis (2026-11-17) | native-call probes, no robot | Llama, Granite | 48 requests | template/interface defects found (see report) | 48 requests | [INTEGRATION_FINDINGS_2026-11-17.md](artifacts/lab-integration-20261117/evidence/INTEGRATION_FINDINGS_2026-11-17.md) |
| Integration repair rerun (2026-11-17) | lab Gazebo, M4 families, repaired profile | Llama 3.1 8B | 36 known-goal per condition | primitives 21/36 → macro 28/36 | calls 190 → 113 | [INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md](artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md) |
|  |  | Granite 3.3 8B | same | primitives 5/36 → macro 9/36 | calls 210 → 193 | [INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md](artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md) |
| G1 Stage 2 dev (2026-11-14) | G1 mock arm/base, dev | Sol | 18 per condition | primitives 17/18 → macro 18/18 | inference attempts 60 → 34 | [STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md](artifacts/macro-generalization-20261113/revision-1/STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md) |
| **G1 held-out** (2026-11-19/20) | G1 mock arm/base, held-out, 38 per condition | Sol | 38 per condition; 3 primitive attempts censored | V2 35/35 → 38/38; V3 35/38 → 38/38 | calls 126 → 74; mean task s 13.273 → 8.361 | [G1_SOL_ADJUDICATED_REPORT_2026-11-19.md](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md) |
|  |  | Qwen3.5 9B | 38 per condition (36 known-goal + 2 ambiguous) | all 26/38 → 31/38; known-goal 26/36 → 30/36; ambiguous 0/2 → 1/2 | calls 123 → 75; mean task s 8.48 → 6.31 | [G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md) |
|  |  | Ministral 3 8B | same | all 29/38 → 35/38; known-goal 28/36 → 33/36 | calls 154 → 83; mean task s 5.32 → 3.18 | [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
|  |  | Granite 3.3 8B | same | all 1/38 → 0/38; known-goal 0/36 → 0/36 | calls 38 → 38 | [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
|  |  | Llama 3.1 8B | same | all 0/38 → 1/38; known-goal 0/36 → 1/36 | calls 203 → 185 | [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
| F1 step 0 (2026-11-20) | trace classification, no runs | Qwen | 116 trials scanned (M4 40 + G1 76) | 12 length stops: 8 class A, 4 class C | — | [F1_STEP0_LENGTH_STOPS_2026-11-20.md](docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md) |

Source checks: 100 literal strings across 37 rows, all found.

## Claims ledger (what the report may and may not say)

Added 2026-11-21. It starts from the novelty review's "claims we must NOT make" table, plus §12 and §17.
"Allowed" claims still need their qualification in the report text. Figures quoted here were checked
mechanically against the linked evidence (`tools/master_readme/claims_ledger.py`). Results per study: see
[Results at a glance](#results-at-a-glance-all-studies). Suggested wording for the contribution statement:
[novelty review §4](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md).

| Claim | Status | Qualification / reason | Evidence |
|---|---|---|---|
| A reusable bounded-skill component for NASA-JPL ROSA was built: the LLM selects one registered skill; Python performs its reads, at most one write and a fresh verification | Allowed | Engineering contribution; not an algorithmic novelty. | [M1_ACCEPTANCE_REPORT.md](artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md), [M2_M3_COMBINED_REPORT_2026-10-27.md](docs/M2_M3_COMBINED_REPORT_2026-10-27.md) |
| The macro cut LLM calls for every backend with working tool calls | Allowed, with the stated qualification | All-attempt G1: Sol 126 → 74, Qwen 123 → 75, Ministral 154 → 83; M4 Sol 44.1% fewer requests. The saving is per model turn, not per unit of robot work. | [G1_SOL_ADJUDICATED_REPORT_2026-11-19.md](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md), [G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md), [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md), [FINAL_REPORT_FOR_CHATGPT.md](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md) |
| Savings track model turns, not native acquisition depth (P1′) | Allowed, with the stated qualification | This was predicted by design (the primitive read already batches sources) and supported for Sol; present it as a confirmed design consequence, not a discovery. | [G1_SOL_ADJUDICATED_REPORT_2026-11-19.md](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md), [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Predictions were frozen before held-out runs | Allowed, with the stated qualification | Say "frozen internally before held-out runs", **not** "pre-registered": they were amended after dev data, are not on a public registry, and three backends were added after Sol/Qwen results. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Costs are reported for all attempts and for matched successes, with infrastructure censoring | Allowed | State both views; never quote only the favourable one. | [G1_SOL_ADJUDICATED_REPORT_2026-11-19.md](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md) |
| Correctness effects were mixed and small | Allowed | M4 Qwen went 15/20 → 14/20; G1 Qwen known-goal 26/36 → 30/36. Say "mixed", not "improved". | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md), [G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md) |
| Repairing the Ollama integration profile made Llama and Granite usable | Allowed, with the stated qualification | Llama known-goal 21/36 → 28/36, Granite 5/36 → 9/36 (P → M), from 0/36 before. The three repairs changed together, so their individual effects are not isolated; G1 used the old profile. | [INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md](artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md) |
| Qwen's length stops are selection failures, not a need for more output tokens | Allowed, with the stated qualification | Inference (H) from 12 traces (8 class A, 4 class C); the F1 wording fix built on it is untested. | [F1_STEP0_LENGTH_STOPS_2026-11-20.md](docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md) |
| Clarification behaviour was human-reviewed | Allowed, with the stated qualification | Say "rated by one teammate with self-attested eligibility"; not independent or external validation. | [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md), [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| A new algorithm or novel mechanism | **Not allowed** | AWO, PyRUA-Lean, BT-Agent, LLMCompiler, ReWOO and SayCan cover the mechanism. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| First work to improve or benchmark ROSA | **Not allowed** | MetaTool/ROS (vs vanilla ROSA) and ROSClaw (parity protocol vs ROSA) exist. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Better than (stock) ROSA | **Not allowed** | Unmodified ROSA was never run as a baseline (§12 item 20). | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md), this README |
| Improves reliability | **Not allowed** | M4 Qwen 15/20 → 14/20; G1 gains are small, grouped, AI-authored and confounded with condition wording. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md), [FINAL_REPORT_FOR_CHATGPT.md](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md) |
| Generalizes to new tasks or robots | **Not allowed** | AI-authored, reused cases; mock domains; one Gazebo arm; no physical robot. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Small local models reach parity with Sol | **Not allowed** | Different hardware and provenance; Qwen and Ministral stay below Sol on the same G1 cases. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Fewer calls means less robot work | **Not allowed** | Native operations rose with the macro (G1 Qwen 100 → 106, Ministral 102 → 127). | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md), [G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md), [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
| Savings grow with task depth | **Not allowed** | The opposite was predicted and supported (P1′); the depth-growth idea (Stage 0 P1) was dropped before testing. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Granite/Llama results show the macro does not help | **Not allowed** | Those G1 results are tool-call integration failures, not macro evidence. | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md), [G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
| Reliability across repeated runs (pass^k) | **Not allowed** | Each G1 case/condition ran once. (The separate M4-family Qwen lab repeat is one replication, not pass^k.) | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Independent or externally validated human review | **Not allowed** | One teammate reviewer, self-attested eligibility (§12 item 23). | [NOVELTY_AND_RELATED_WORK_2026-11-20.md](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| Lab timing shows a controlled speed difference | **Not allowed** | The GPU was shared with another project's Ollama server; timing is contextual (§12 item 22). | [LAB_CONTAINER_CHECK_2026-11-20.md](docs/LAB_CONTAINER_CHECK_2026-11-20.md) |
| Batching (Stage 4) or the serving change (Phase 1) was an improvement | **Not allowed** | Both failed their predefined retention screens. | [FINAL_REPORT_FOR_CHATGPT.md](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md), [QWEN_SERVING_PHASE1_REPORT_2026-11-13.md](docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md) |
| The F1 catalogue wording fixes Qwen | **Not allowed** | F1 is designed but untested (Stage 0 only); no F1 model run has happened. | this README |
| Qwen was trained or its weights improved; JTVR or episodic memory was completed; physical-robot safety was shown; the full ROSA catalogue was benchmarked | **Not allowed** | None of these happened (§17 closing note). | this README |

Ledger checks: 33 literal strings across 24 rows, all found.

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
The completed M4 question concerned **model-managed primitive execution versus a
bounded macro**, using both local Qwen and hosted Sol separately. The later
timing/offload screen is complete with no new serving profile retained. Current
G1 preparation examines bounded macro behavior across arm/base mock domains and
inspection acquisition depths. Its native depth is not sequential model-decision
depth; the primitive read tool already batches sources. These studies do not
establish difficult general planning, independent case generalization or parity
between Qwen and Sol.

The intended deliverable is a maintainable reusable Python component integrated
with ROSA, a working Gazebo demonstration, and reproducible experimental evidence
of benefits and limitations. A small completed module is preferable to several
unfinished research systems. A negative result is acceptable.

Verification/reliability and tool-calling efficiency are related research interests,
not obligations to build two large independent architectures. JTVR was one candidate
method; it is not the project's identity. Episodic memory is optional future work.
Physical hardware and coordinated dual-arm manipulation are not current completion
requirements.

The [recorded project vision](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/PROJECT_VISION.md) preserves the
user's earlier clarification. Its immediate experiment suggestions describe that
historical point; the M1–M5 priorities below reflect subsequent decisions.

## 2. Current verified status
### 2026-11-21 — D12 approved; F1 classified against Levinson's work (D13–D15)

No model inference. On branch `member/martin-f1`, F1 `PROTOCOL.md` §12 and §14:
- **D13 (Martin):** D12 approved. S-base and S-new run in the same laptop environment **back to back**,
  so environment drift since G1 affects both arms equally and does not bias the F1 comparison. A
  fingerprint match with G1 would matter only for F1-vs-G1 Sol comparisons, and the protocol makes none.
  The code-hash check against the lab copy stays.
- **D14 (Martin):** the laptop zero-model controls dry run is approved once the lab controls pass. If the lab
  is still down it may run first, labelled **laptop-only**. It does not replace G1 on the lab.
- **D15:** `rosa-contexts` was read with Martin's access (`main` = `member/krln` `26ac7bd9`, shared-only;
  `member/levinson` `70e61ae8`, 2026-11-19). **F1 is new, with adjacent overlap; it is not a replication.**
  The closest items are reported evidence, not rerun: Levinson's tool-description compaction (FULL 32 vs
  COMPACT 33 /40, "no benefit shown") and headroom Stage 3d (six generic prompt sentences on Qwen:
  20/24 vs 24/24, and two unrequested service-call attempts). Stage 3d is the closest negative and backs
  F1's P-c guard and P-f′ veto. No F1 threshold, arm, case or gate changed.

### 2026-11-21 — F1 safety veto revised (D11); where G1 Sol ran; Sol plan (D12)

No model inference, network call or credential refresh. On branch `member/martin-f1`:
- **D11 (Martin, before any run):** the **P-f′** veto replaces P-f. Adoption is vetoed if Q-new selects a
  movement skill on more of the 16 non-movement no-dispatch cases (8 inspection, 2 unavailable-source,
  6 ambiguous) than Q-base. P-f (actual dispatches) is now a diagnostic, and Sol is diagnostic only.
- **New limitation:** mock worlds refuse wrong writes, so unsafe selections are masked in G1 and F1 (§12
  item 26).
- **Where G1 Sol ran:** on the **laptop**, in WSL Ubuntu-24.04, with
  `~/.local/share/rosa-envs/research` (`stage-4/launch.py` → `runner.py`, three continuations). The frozen
  stage-4 code re-verifies 3,795/3,796; the one mismatch is the documented M5 `status.json` edit. The
  environment is fingerprinted (Python 3.12.3, langchain 0.3.30). **D12:** F1's Sol arms will run there as
  a documented exception to the lab-only rule, if code hashes match the lab copy (pending, lab
  unreachable).
- **Correction:** Stage 0 wrongly said the laptop had no LangChain/ROSA environment. The W2 LangChain
  quote (`output_parsers/tools.py:34-41`: no tool calls → `AgentFinish`) is now in the F1 wording diff.
- Record: `artifacts/f1-catalogue-wording-20261121/SOL_ENVIRONMENT_2026-11-21.md` (branch `member/martin-f1`).

### 2026-11-21 — F1 decisions recorded; gate G1 blocked (lab unreachable)

No model inference. Recorded on branch `member/martin-f1`
(`artifacts/f1-catalogue-wording-20261121/PROTOCOL.md` §12 and `GATES_STATUS_2026-11-21.md`):
- **Martin's decisions:** thresholds confirmed. **P-c** now covers 10 cases (8 inspection + 2
  unavailable-source, at most 1 loss). New **P-f safety veto**: any Q-new dispatch on a no-dispatch case
  that Q-base didn't make blocks adoption. **P-a = net ≥ +3, fixed.** Code location, leakage thresholds
  and run order confirmed.
- **New finding:** P-f as defined can't fire by construction. The program refuses the write on all 20
  no-dispatch cases (`worlds.py:213-214`; `macro.py:22-23`; `bounded_macro.py:79-81`). A diagnostic P-f′
  (write attempts and movement-skill selections) was added; Martin decides whether it becomes the veto.
- **Correction:** the F1 dev set is the **18** G1 dev cases, not 16. Two `write_fault` dev cases, added by
  G1 `stage-1/prepare.py:31`, had been missed. The held-out set is unchanged.
- **Sol access:** a remembered credential record is present on the laptop, but its validity can't be
  known without a provider token refresh, which was not done. It is laptop-bound (Windows DPAPI), so Sol
  on the lab would need a new sign-in. Martin decides.
- **Gate G1 (zero-model scripted controls) not run:** the lab was unreachable again at
  2026-11-20T17:08:07Z (port 22 timeout). G3 (analysis + runner) and G4 (readiness) were not started,
  per the gate order. There is no Stage 1a command yet. Stage 1 remains unauthorized.

### 2026-11-21 — master README audited and repaired

At Martin's request, this record was checked for completeness, since it is the main reference for the
final report.
- **Formatting defect fixed.** On 2026-11-17 the file was rewritten with `\r\r\n` line endings, and
  the later cleanup turned each one into an extra blank line. About 700 sentences were split
  mid-line and **26 tables did not render**. 1,768 inserted blank lines were removed, using the
  pre-cleanup backup as a map; the repair changed no non-blank line. Result: 0 broken tables.
- **Stale statements corrected:** the push status, "Qwen Batch B pending" (now closed), the §15
  handoff and the G1 roadmap line. The old wording stays visible, struck through or marked superseded.
  A "where to start" note at the top labels the old bold checkpoint blocks as a chronological
  archive. A note above the generated M4/M5 block marks it as a 2026-11-05 snapshot.
- **Integrated the 11-17 to 11-21 findings into the reference sections:**
  - §12 limitations 20–25: no stock-ROSA baseline, lenient clarification scorer, contextual lab
    timing, self-attested reviewer, Granite/Llama as integration failures, length stops as selection
    failures;
  - §14 evidence rows for every 11-19 to 11-21 report;
  - §17 decision-log rows for 11-17 to 11-21.

### 2026-11-21 — F1 Stage 0 designed on branch `member/martin-f1` (no model calls)

F1 tests whether honest catalogue wording (W1: movement skills' routines read the current target
coordinates, write at most once and verify; no readiness checks) plus a stated clarification route (W2:
a plain-text question, no tool) fix Qwen's selection failures. The comparison is macro only: Qwen and Sol,
each with base and new wording. The cases are 30 fresh AI-authored held-out cases plus the G1 dev cases. Study (on branch `member/martin-f1`):
`artifacts/f1-catalogue-wording-20261121/STAGE0_STATUS.md`;
code: `tools/f1_wording/`. The static wrapper check passes, and the leakage check is 30/30 OK. **The
zero-model scripted controls have not run, because the lab was unreachable on 2026-11-21.** Thresholds
await Martin. Stage 1 (any inference) is not authorized. Caution from the frozen G1 data: only 1 of Qwen's
6 G1 macro failures was inspection-first.

### 2026-11-21 — project frozen

**Martin froze the project himself on 2026-11-21.** This supersedes the 2026-11-20 note that
Levinson would do it. It was done before any new study, with no model calls and no trials. All
frozen material is pinned by the annotated tag `freeze-2026-11-21` on `member/martin`. Its
SHA-256 manifest, `FREEZE_MANIFEST_2026-11-21.json`, covers the tracked files under `artifacts/`,
`docs/`, `tools/` and the root reports. `python -I -B tools/freeze/verify_freeze.py` must pass on
any later branch. **New work goes on a new branch and into new output directories only**; see
[FREEZE.md](FREEZE.md). The untracked raw traces and duplicates are in an out-of-git backup
archive with a git bundle and SHA-256 lists, which Martin will copy to an external drive. The
push of the freeze commit and tag awaits Martin. A designed-but-unstarted F1 Stage 0
(catalogue wording) was paused for the freeze; nothing for it was written.

### 2026-11-20 — current status

No model requests and no new trials. Lab work today was read-only checks plus one
zero-inference formal analysis (the Qwen closeout). Git: `37a7e19` (review, F1 and M4/M5
corrections) was pushed to `member/martin` with owner approval. ~~`8a85af0` (Qwen closeout) and the
later docs are local until approved.~~ (Superseded the same day: Martin pushed `member/martin` to
`988cfd8` and `rosa-research` `member/martin` to `8713f9b`; both verified against GitHub.)

| Item | State | Record |
|---|---|---|
| G1 three-model extension (Ministral, Granite, Llama) | **Closed, adjudicated.** 228 attempts; known-goal P→M Ministral 28/36→33/36, Granite 0/36→0/36, Llama 0/36→1/36. H-write Uninformative for all. Granite/Llama are tool-call integration failures | [adjudicated report](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) |
| G1 Sol | Closed: 73 PASS, 3 censored; P1′ Support, P2 Uninformative, P5 Support | [Sol report](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md) |
| G1 Qwen (Batch B closeout) | **Closed, adjudicated 2026-11-20 on the lab, zero inference.** All-task P→M 26/38→31/38; known-goal 26/36→30/36; ambiguous 0/2→1/2. 57 PASS / 19 FAIL, none censored. Calls 123→75 (all attempts), 87→52 (25 matched pairs); native operations 100→106. P1′ Uninformative (diagnostic), **P2 Against** (depth-1 cells), P5 Support, P4 not run; H-write not tested on Qwen (post-hoc origin). Ratings H01 NO/YES, H02 NO/NO, H03 YES/YES, H04 NO/YES; declaration item 5 relayed by Martin, recorded separately. Attempt 01 of the driver stopped on a hash-method assertion before writing; retained | [Qwen report](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md), [intake](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/operator/human-review-intake-20261120/INTAKE_STATUS.md) |
| Prediction label map | Three label systems exist (stopped Stage 0, revision 1, frozen P1′–P6 amendment). **P1′ was Support for Sol**, not Against; only Ministral's diagnostic P1′ was Against. The refuted "savings grow with depth" idea was Stage 0 P1, replaced before testing | [label map](docs/PREDICTION_LABEL_MAP_2026-11-20.md) |
| Novelty / related work | **Mechanism well covered; a narrow evaluation niche remains.** AWO meta-tools, PyRUA-Lean, BT-Agent, LLMCompiler and SayCan cover the mechanism. MetaTool/ROS and ROSClaw already compare against stock ROSA. Our **missing stock-ROSA baseline** is the main exposed weakness (new runs would be needed; not authorized) | [novelty doc](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| F1 step 0 (Qwen length stops) | 12 length stops (M4 5, G1 7): **8 A** (after a wrong selection or blocked action), **4 C** (first-call deliberation that had already named the correct skill). All 12 are selection-related; 0 on inspection tasks. 3 M4 stops hit the 2,048 task budget, not the 1,024 per-call cap. Source check: movement macros read the target's current state before writing, but not the readiness checks, and the catalogue never says so. Candidate F1 hypothesis (descriptions + clarification route) recorded, **not designed or run** | [F1 doc](docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md), [script](tools/f1/length_stops.py) |
| Lab container check (read-only) | Two running containers: ours, `marvel-g1-extension-20261119`, and another project's, `rosa-exam-main`. Both use host networking, ROS domains 0 vs 220, and no GPU attachment. **Two host Ollama servers share the one GPU** (ours v0.40.6 :11439, theirs v0.40.16 :11435) with no coordination. No ROS 2 or Gazebo process runs anywhere; Phoenix :6006 is ours alone. Root disk 98% full. **Completed runs:** G1 used mock worlds + Ollama only (no ROS/Gazebo, confirmed from code). Qwen ran before the other project started. The multi-model runs overlapped it, but 393 telemetry samples show no foreign GPU process, so correctness has no plausible exposure; timing interference is not proven absent. The ROS cross-talk test did not run (`ros2` not on PATH); can't tell | [check](docs/LAB_CONTAINER_CHECK_2026-11-20.md), [raw output](artifacts/lab-container-check-20261120/lab_check_20261120.txt) |
| Repository completeness and freeze | **Selection decided 2026-11-20 (owner delegated the choice).** Of 10,666 untracked files (1.16 GB): **commit about 7,935 (216 MB)**, i.e. everything current conclusions and reruns depend on (reports, protocols, code, configs, per-trial results and scores, analyses, review intakes, one canonical evidence archive per study). **Out-of-git backup with a SHA-256 list:** raw span trace dumps (732 MB), duplicate delivery packages, the repo git bundle, the G1 exact-inputs tarball, pre-update snapshots and the teammate repo snapshot. **Local only:** the private chat handoff and scratch. Lab vs laptop hashes for G1 `revision-1`: 4,901/4,905 match (4 lab logs grew after copy-back). Committed 2026-11-20 as `7260cb8` (evidence) and `fe623b7` (docs), plus `rosa-research` `8713f9b`. **Freeze done by Martin on 2026-11-21:** annotated tag `freeze-2026-11-21`, manifest `FREEZE_MANIFEST_2026-11-21.json` (10,735 tracked files under `artifacts/`, `docs/`, `tools/` and root reports; living documents excluded), and an out-of-git backup archive plus a git bundle, each with a SHA-256 list. ~~Martin decided the freeze manifest, tag and out-of-git backup will be done by Levinson, as the single person running the next trials; Martin did not create them~~ (superseded 2026-11-21: Martin did the freeze himself) | [FREEZE.md](FREEZE.md); commit `7260cb8` message lists every exclusion |

~~**Dead-link flag:** `docs/CLAUDE_QWEN_ROADMAP_LIVE.md` and
`docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md` exist locally but are **untracked**.~~
Resolved: both were committed in `7260cb8` (2026-11-20), so the links now work on GitHub.

All five G1 backends are now adjudicated. Key-based SSH from the laptop to the lab was set
up 2026-11-20 with owner approval. No further action is currently authorized. F1 candidate
testing, a stock-ROSA baseline, a Granite/Llama tool-call smoke test and the P4 catalogue
probe each need separate authorization. Levinson's new trials will be a separate study, run on
his own branch and output roots.

### Working on the lab — operational summary (public-safe)

This replaces the private local handoff for everyday use. Host address, account and VPN
details are deliberately not recorded here. Verified 2026-11-20 unless marked otherwise.

| Topic | Current facts |
|---|---|
| Access | SSH alias `lab-rosa` from Martin's laptop (key-based since 2026-11-20). The campus VPN is needed off campus. All tests, trials and formal analysis run **on the lab**; the laptop is for editing and read-only evidence inspection |
| Hardware | NVIDIA RTX 4080 SUPER 16,376 MiB, driver 570.195.03 (CUDA compatibility 12.8), host Python 3.13.3 (verified today); Ubuntu 25.04 host (per the 2026-11-20 handoff inventory) |
| Project root | `/media/naeem/d1/marvel proj` (quote the space; the symlink `marvel-proj` also exists). Models are in `models/`, the Ollama binary in `runtime/bin/ollama`, Python envs in `runtime/envs/{research,phoenix}` |
| G1 execution mirror | `preparation/g1-sol-review-and-lab-replication-20261119/workspace/rosa-evaluation/…/revision-1`. **Not a Git checkout.** The lab's root `rosa-evaluation` checkout is older (`ec42ee7`); don't sync one over the other |
| Container | `marvel-g1-extension-20261119`, image `sha256:306205ffce29…`, ROS 2 Jazzy, host network, project root mounted at `/work` (rw), `ROS_DOMAIN_ID=0`, `ROS_LOCALHOST_ONLY=1` (verified today). Per the handoff inventory: research venv Python 3.12.3; inside the container, ROS needs `source /opt/ros/jazzy/setup.bash`. The earlier Qwen container (started 2026-11-17 per run telemetry; image `sha256:472fb430…` per handoff) no longer exists |
| Ollama (ours) | Host process `runtime/bin/ollama serve`, **v0.40.6**, `127.0.0.1:11439`. Installed tags: `qwen3.5:9b`, `ministral-3:8b-instruct-2512-q4_K_M`, `granite3.3:8b`, `llama3.1:8b-instruct-q4_K_M` (Q4_K_M; digests in each backend's `MODEL_CONFIG.json`/`freeze.json`) |
| Frozen serving settings (G1) | Taken from a recorded Qwen request: `num_ctx 8192`, `num_predict 1024`, temperature 0, seed 42, `use_mmap true`, `think false`, API `stream true`. Per the preflight records (not re-verified today): flash attention on, f16 KV cache, all layers on the GPU (Qwen 33/33, Ministral 35/35, Granite 41/41, Llama 33/33) |
| Phoenix (ours) | `127.0.0.1:6006`, running inside our container from the extension's `operator/phoenix_server.py` |
| Shared with another project | `rosa-exam-main` container and its own Ollama v0.40.16 on `:11435` share the GPU. **Do not stop, reuse or reconfigure it.** Check `nvidia-smi` and coordinate GPU time before any model load |
| Safe read-only checks | `docker ps`, `nvidia-smi`, `curl 127.0.0.1:11439/api/ps` (and `/api/version`), `curl 127.0.0.1:6006/healthz`. A model load or generation **is** a charged request; never do one casually |
| Verify frozen G1 inputs (zero inference) | In the mirror's `stage-4-multimodel-20261119`: `python3 -B -c "import runpy;assert runpy.run_path('operator/run_sequence.py')['verify']()"`. Never run `run_sequence.py --execute`, `launch.py` or completed analysis drivers as checks |
| Disk | Root `/` is 98% full; write outputs under `/media/naeem/d1` (386 GB free) |

### M4/M5 generated status block — retired 2026-11-21

The auto-generated M4/M5 status block (last refreshed 2026-11-05) is **retired**. For results, use
[Results at a glance](#results-at-a-glance-all-studies): the M4 rows give the final figures, and
[Confirmed closed checkpoints](#confirmed-closed-checkpoints) below gives the milestone results. The block is kept
unchanged in [Appendix C](#appendix-c--historical-section-2-checkpoints) (C.3). Its markers were renamed, so
`python -m tools.project_context --refresh` now stops with an error before writing anything. It can no
longer overwrite this file, `PROJECT_LIVE_STATUS.json` or the frozen M4 timing report.

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
  and [module delivery guide](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/M5_MODULE_DELIVERY_README_2026-10-27.md):
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

The deeper review adds an observed action/feedback distinction. Both primitive
partial-command outputs already name park_right as the correct movement goal
before an invalid pre-selection readiness read is rejected. They then select
park_right. Both macro runs first select inspection, then request park_right on
call two; the shared single-selection rule rejects the change. One macro run
ends in accepted readiness SUCCESS and the other on response length. The guard
is conservative; relaxing it would require a defined evidence, permission and
cumulative-budget policy, and would not permit replay after a dispatched write.

System prompts and tool schemas are identical, but the execution-condition
sentence differs. Repeated first inputs and visible outputs match within each
condition under fixed serving settings. Since the first output precedes tool
execution, wording is the strongest observed explanation for this request's
first-action difference. **M4 compares execution mode with its mode-specific
instruction; their effects on selection are not separately identified.** The
observed configuration-level costs and outcomes remain valid within that scope.

The [post-hoc label-sensitivity illustration](artifacts/macro-m5-20261027/external-discussion-20261030/retrospective-label-sensitivity.json)
keeps the ambiguity dispute separate from the seven explicit movement-related
failures. Four of those explicit failures concern unavailable prerequisites:
correct behavior required withholding movement and reporting UNKNOWN.

| Interpretation | Sol primitives / macro | Qwen primitives / macro |
|---|---|---|
| Frozen M4 criterion | 20/20 /20/20 | 15/20 /14/20 |
| Exclude the ambiguity family | 18/18 /18/18 | 15/18 /14/18 |
| Apply the owner's submitted labels only to ambiguity | 18/20 /18/20 | 17/20 /16/20 |

The last row is stakeholder-preference sensitivity, not independent adjudication
or a replacement score. It does not prove that inspection fulfilled the
unspecified user intent. No runtime intervention or clearer-prompt benefit has
been tested. Fresh-case wording and recovery experiments remain optional proposals.

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
Git or archives. See the [specific repair/validation record](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/REMEMBERED_AUTH_ROTATION_VALIDATION_2026-10-27.md).

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

The [original specification](../JTVR_Final_Technical_Specification_ID%281%29.md) (a local workspace file, not in any repository)
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

### M1–M5 product-completion roadmap — completed delivery record

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

### Current separate G1 roadmap

G1 numbering is distinct from M1–M5, the historical six stages and the completed
Qwen serving Phase 0/1. Its current state is completed Sol and three-model extension analysis, ~~with the separate Qwen Batch B review still pending~~ and, since 2026-11-20, the adjudicated Qwen closeout. **G1 is closed for all five backends** and frozen at `freeze-2026-11-21`. Read the newest top-of-file status and dated handoff first. The initial stopped Stage 0 design and the revision-1 design are
separate retained records; do not combine their counts or interpret old pending
authorship notes as the latest decision.

The scope is mock arm/base inspection acquisition ladders at native depths
1/2/4/6 plus movement, missing prerequisites, unavailable observations, partial
writes and ambiguity. Each domain hosts five registered skills. The baseline
inspection bundles registered reads, so its expected select/read/report sequence
is three model turns versus two for a macro, independent of native depth.
Healthy primitive movement expects five versus two. Real dev turns matched those
comparators on completed paths; they were not imposed on live model decisions.
Both observer and actor use the same authoritative world through separated
channels/records. This is not independent physical sensing or independently
authored ground truth. No Gazebo/base transfer was tested by G1.

The owner confirmed the prospective P1′–P6 interpretation on November 14:

| Endpoint | Current definition / rule |
|---|---|
| P1′ | Sol matched-success inspection call saving is about one at each native depth. Support requires every mean in [0.5, 1.5] and depth spread at most 0.5; Against if any mean lies outside [0, 2] or spread exceeds 1.0; otherwise Uninformative. Required separately in both domains; pooled results secondary. |
| P2 | Macro/primitive native-operation ratio is within [0.75, 1.25] at every depth, separately in both domains; outside is Against and missing/undefined cells are Uninformative. |
| P3 | Dropped; longer-horizon reliability needs a separately designed G2 extension. |
| P4 | Qwen selection accuracy at catalogue sizes 3/5/10: a decrease of exactly 20 percentage points or more is Against. All ordered smaller-to-larger contrasts considered; missing data are Uninformative. Same-domain near-duplicate catalogue extension remains off. |
| P5 | Both domains hosted with zero required hosting-source changes; report any required diff. Passing controls does not itself establish model generalization. |
| P6 | Descriptive write-versus-inspection model-call counts, with no Support/Against threshold; report healthy and partial writes separately from missing-prerequisite cases. |

Analysis distinguishes all-scheduled operational outcomes (V1), evaluable
correctness (V2) and a sensitivity view counting infrastructure-censored attempts
as failures (V3). A censored pair is excluded from matched-pair efficiency with
its exclusion reported. Component scores in the overlay are NOT_EVALUABLE,
leaving raw scorer flags untouched. If V2/V3 change a prediction's status, report
Uninformative. At least eight censored trials out of 76 flags a backend as
operationally compromised and its statuses Uninformative under current rules.
Pair gaps over 30 minutes are flagged; uncertainty resamples whole template
groups with 10,000 draws and seed 20261113. Dev data do not adjudicate endpoints.

Per-task limits remain eight calls, 2,048 observed generated tokens, ten native
operations, sixteen tool attempts including nested calls, three corrections,
at most one permitted movement and 360 seconds. Read-only/ambiguous cases permit
zero movements. Proposed held-out limits are 608 ordinary plus three reserve
physical requests/backend and an eight-hour backend window; roughly 200 requests
is a planning estimate, not a launch or quota guarantee. Only eligible explicit
HTTP 502/503/504 failures may use the existing one-retry/logical-call reserve.
No in-stream retry, uncertain command replay, failed-trial replacement, budget
reset or new manual consent is authorized by a standing continuation instruction.
These are protocol bounds, not evidence that later stages have been launched.

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
    The local restore-verified bundle/supplement protects only its pinned revisions;
    later documentation is not automatically covered.
15. M4's Windows supervisor may leave process exit_code null; authoritative outcome
    evidence is the backend checkpoint, closed audits and cleanup, not inventing
    a zero exit code from absent launcher metadata.
16. G1 uses AI-authored requests without independent semantic-novelty review.
    Held-out designation does not mean fixture definitions were hidden during
    engineering. Its grouped reads do not test long sequential planning horizons.
17. G1's automatic clarification regex has six reachable counterexamples in the
    separate review. A human-review-required flag does not correct its automatic
    primary score. Do not describe completed dev clarification as human-validated.
18. The G1 outer observability wrapper cannot recover all required HTTP error
    metadata. The owner declined the proposed protected hook; neither the source
    constraint nor the missing-field requirement has been silently waived.
19. Four scorer provenance bypasses in adversarial tests required forged trusted
    internal records. They are defense-in-depth findings, not demonstrated current
    model-accessible exploits. Reassess if the trust boundary changes.
20. **No stock-ROSA baseline** (added 2026-11-21). Every comparison is primitives vs bounded macro
    *inside* the modified ROSA. Nearby work (MetaTool/ROS, ROSClaw) compares against unmodified ROSA;
    this project cannot claim an improvement over original ROSA without new runs
    ([novelty review](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md)). The mechanism itself (meta-tools,
    fixed skills, program-run routines) is well covered in the literature; only a narrow evaluation
    niche is new.
21. **Clarification scoring is lenient** (added 2026-11-21). The G1 regex
    (`\?|clarif|which|whether|would you|specif`) passes any text containing those words. Qwen's G1 033
    "clarification" was deliberation text that passed this way, and the human reviewer failed a
    comparable case (H04). Ambiguous-case results are only as good as their human rating.
22. **Lab timing is contextual, not controlled** (added 2026-11-21). Two Ollama servers (ours `:11439`,
    rosa-exam's `:11435`) share one GPU. The three-model extension overlapped the other project's
    uptime; 393 telemetry samples show no foreign GPU process, but brief use between 10-second samples
    can't be excluded ([lab check](docs/LAB_CONTAINER_CHECK_2026-11-20.md)). Correctness is unaffected
    (mock worlds, temperature 0).
23. **Reviewer eligibility is self-attested** (added 2026-11-21). Levinson is a teammate. His
    declarations are retained and the relationship is disclosed, but they are not external
    validation.
24. **Granite and Llama results measure tool-call integration, not task reasoning** (added
    2026-11-21). Their near-zero G1 scores are dominated by tool-call format failures. Don't read
    them as model capability rankings.
25. **Qwen's length stops are selection failures** (added 2026-11-21). All 12 (8 class A, 4 class C)
    were on movement-type requests; none were on inspection tasks
    ([F1 step 0](docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md)). A larger output allowance is not
    indicated. The F1 wording fix is designed but **untested**. In the G1 macro arm only 1 of Qwen's
    6 known-goal failures was inspection-first, so expect a modest effect at most.
26. **Mock worlds mask unsafe selections** (added 2026-11-21). In G1 and F1 the worlds refuse wrong
    writes: unauthorized requests are refused in `worlds.py`, and unknown poses by the prerequisite guard.
    A wrong movement selection therefore produces no dispatch and may still end in an acceptable
    outcome. On a real robot without these guards, the same selection would act. This is why F1's veto
    counts selections (P-f′), and why no G1/F1 result is evidence of physical safety.

Do not address each individual Qwen mistake by inventing a new architecture. A
concrete engineering defect may warrant a separately tested repair; an unfavorable
model outcome may simply need to remain a documented limitation.

## 13. Team package and compatibility

**Provider and authorship:** Levinson, Martin's teammate, provided the
`rosa-contexts` repository and his research snapshot. Martin relayed it for
contextual review. The teammate's published research is not authored by Martin
and must remain separately credited in reports, presentations and comparisons.

The private [rosa-contexts repository](https://github.com/Lelevinson/rosa-contexts)
is a different component from the teammate's backend package below. Its shared
protocol uses member branches for curated one-way context snapshots. The
[November 16–17 review](docs/team-context-review-20261116/ROSA_CONTEXTS_REVIEW_2026-11-16.md)
records `main` and `member/krln` at the same shared-only commit and Levinson's
100-file branch separately. We checked the published manifest and table arithmetic,
not the excluded raw experiments. Of the 91 research source files, 90 were ignored
and one modified; none matched bytes in the recorded source HEAD. Published
file hashes identify the shared snapshot. Existing local repositories remain
authoritative; no member branch, sync setup or publishing configuration was changed.

Levinson's historical fixed-loop comparison reports C1 70/80, Forge 55/80 and
modified stock-executor A1 47/80. His later fresh control is 67/80; apparent
answer-gate/list benefits were not attributable to their mechanisms. These are
read-only synthetic ROS-query development workloads with different settings
from our UR5e/M4 suite. No result pooling, direct performance ranking against
our backends or tested runtime compatibility follows. Shared coordination is
useful now; runtime integration would need separately authorized source and
contract checks. Our master is in `rosa-evaluation`, while his sample allowlist
uses `rosa-research`; it cannot be blindly synchronized under the same paths.

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
| **Freeze 2026-11-21** | [FREEZE.md](FREEZE.md), [manifest](FREEZE_MANIFEST_2026-11-21.json), [verifier](tools/freeze/verify_freeze.py); out-of-git backup (archive + git bundle + SHA-256 lists) kept off-repo by Martin |
| **F1 Stage 0 (catalogue wording), design only** | status (`artifacts/f1-catalogue-wording-20261121/STAGE0_STATUS.md`, branch `member/martin-f1`), protocol (`artifacts/f1-catalogue-wording-20261121/PROTOCOL.md`, branch `member/martin-f1`), wording diff (`artifacts/f1-catalogue-wording-20261121/WORDING_DIFF.md`, branch `member/martin-f1`), cases + leakage (`artifacts/f1-catalogue-wording-20261121/cases/README.md`, branch `member/martin-f1`), lab plan (`artifacts/f1-catalogue-wording-20261121/LAB_PLAN_STAGE1.md`, branch `member/martin-f1`); branch `member/martin-f1` |
| **G1 Qwen (closed 2026-11-20)** | [Adjudicated report](G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md), [lab execution report](G1_QWEN_LAB_REPORT_2026-11-19.md) |
| **G1 three-model extension (closed 2026-11-20)** | [Adjudicated report](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md), [execution report](G1_MULTIMODEL_REPORT_2026-11-19.md) |
| **G1 Sol (closed 2026-11-19)** | [Adjudicated report](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md), [held-out report](G1_SOL_HELDOUT_REPORT_2026-11-19.md) |
| **Prediction labels across G1 revisions** | [Label map](docs/PREDICTION_LABEL_MAP_2026-11-20.md): Stage 0 / revision 1 / P1′–P6 |
| **Novelty and related work** | [Review](docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md) |
| **Qwen length stops (F1 step 0)** | [Classification and source check](docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md), [script](tools/f1/length_stops.py) |
| **Lab container / interference check** | [Check](docs/LAB_CONTAINER_CHECK_2026-11-20.md), [raw output](artifacts/lab-container-check-20261120/lab_check_20261120.txt) |
| Team-context review | [Review, scope and compatibility](docs/team-context-review-20261116/ROSA_CONTEXTS_REVIEW_2026-11-16.md), [snapshot hashes](docs/team-context-review-20261116/SNAPSHOT_VERIFICATION.json), [offline arithmetic checks](docs/team-context-review-20261116/READ_ONLY_CHECKS.json) |
| G1 gates and decisions (historical, Nov 15) | [November 15 Stage 3 status](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-15.md), [source-unchanged disposition](artifacts/macro-generalization-20261113/revision-1/stage-3/owner-decisions-20261115/INSTRUMENTATION_DECISION.md) |
| G1 separate-model scorer review | [Astra report](artifacts/macro-generalization-20261113/revision-1/stage-3/scorer-review/astra-review-20261115/REVIEW_REPORT.md), [case results](artifacts/macro-generalization-20261113/revision-1/stage-3/scorer-review/astra-review-20261115/review-summary.json), [verification](artifacts/macro-generalization-20261113/revision-1/stage-3/owner-decisions-20261115/review-verification.json) |
| G1 prospective endpoints | [Owner-confirmed P1′–P6 amendment](artifacts/macro-generalization-20261113/revision-1/stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md) |
| G1 development results | [Stage 2 results and problems](artifacts/macro-generalization-20261113/revision-1/STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md), [audit addendum](artifacts/macro-generalization-20261113/revision-1/stage-3/STAGE2_AUDIT_ADDENDUM.md) |
| G1 engineering controls | [Original Stage 1](artifacts/macro-generalization-20261113/revision-1/stage-1/STAGE1_REPORT.md), [fresh Stage 3 rerun](artifacts/macro-generalization-20261113/revision-1/stage-3/controls-rerun-20261114/CONTROL_RERUN_REPORT.md) |
| Master refresh preservation | [November 16 update record](docs/master-readme-refresh-20261116/UPDATE_RECORD.md); pre-update master bytes retained separately, earlier evidence unchanged |
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
| Public module | [v0.2 README](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/MACRO_CAPABILITIES_V2_README.md), [specification](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/MACRO_CAPABILITIES_V2_SPEC.md) |
| OAuth repair | [Live renewal validation](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/REMEMBERED_AUTH_ROTATION_VALIDATION_2026-10-27.md) |
| Completed M4 | [Final report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md), [timing](docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md), [protocol](docs/M4_MACRO_PROTOCOL_2026-10-27.md), [status entry](MILESTONE_M4_STATUS.md), [freeze](artifacts/macro-m4-20261027/freeze.json) |

Major archives, each with a corresponding `.sha256` sidecar:

| Campaign | ZIP |
|---|---|
| G1 Stage 2 results and retained evidence | [ROSA_G1_STAGE2_RESULTS_2026-11-14.zip](artifacts/macro-generalization-20261113/revision-1/stage-2-share-20261114/ROSA_G1_STAGE2_RESULTS_2026-11-14.zip) — Stage 2 only; does not contain the later Astra review |
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

**Current handoff (2026-11-21):** start from the dated entries at the top of section 2. All
studies are closed; the project is frozen at tag `freeze-2026-11-21`. Run
`python -I -B tools/freeze/verify_freeze.py` (it must PASS) before and after any new work. New work goes
only on a new branch and into new directories ([FREEZE.md](FREEZE.md)). Open work: F1 Stage 0 on
`member/martin-f1`. Its zero-model scripted controls are still to be run on the lab
(plan (`artifacts/f1-catalogue-wording-20261121/LAB_PLAN_STAGE1.md`, branch `member/martin-f1`)); F1 Stage 1 inference is not
authorized. The paragraph below is the 2026-11-20 handoff, kept for history.

**Handoff (2026-11-20):** start from the dated entry at the top of section 2.
Lab-access details are in a private local handoff, not in this repository. G1 Stage3 was subsequently resolved through documented owner decisions, review,
freeze and launch acknowledgments. Sol held-out and the three-model extension
are now closed; Qwen execution is complete but its separate BatchB four-response
human review is pending (superseded: closed and adjudicated on 2026-11-20). No new backend/study launch is authorized by this note.
The latest evaluation commit was explicitly approved and pushed to member/martin;
main was unchanged. Old M4/G1 launch commands below are historical references,
not instructions to rerun completed directories. All future tests and formal
analysis execute on the lab via SSH. Preserve raw evidence and cumulative budgets;
never replay failed/censored or uncertain actions. A genuinely new launch still
needs its applicable protocol and owner acknowledgment. Recheck the lab execution
mirror, authorization boundaries and current shared GPU occupancy before any run.



### Safe inspection during the active study

M4 has now finished; the restrictions below describe active frozen campaigns,
not a requirement to keep a completed worker or simulator running. Do not rerun
the closed populated M4 directories. M5 consolidation subsequently completed;
current separate G1 work is described above, not a restart of M4.

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
activation script to rerun every time. In WSL, for read-only documentation refresh (**retired 2026-11-21**:
the command below now stops with an error by design; see the retired-block note in section 2):

```bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
/home/martin/.local/share/rosa-envs/research/bin/python -B -m tools.project_context --refresh
```

For later module development, source ROS2 Jazzy and use the existing research
environment. The public [capability README](https://github.com/Lelevinson/rosa-research/blob/8713f9b205033a25f8ed8d9549610e9ad0b8bfde/docs/MACRO_CAPABILITIES_V2_README.md)
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
| Presentation handoff prepared 2026-11-17 for 2026-11-18 | Embedded three-slide briefing includes goals, M4 costs/correctness, latest G1 limitations and conditional future steps. Teammate-provided context explicitly attributed to Levinson; no new experiment or source change. |
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
| Post-closeout raw first-turn inspection | Primitive visible text already names the correct movement goal before protocol feedback. Macro call two requests that goal but the shared commitment rule blocks it. Preserve the distinct terminal outcomes. |
| Execution mode and its instruction changed together | Attribute measured results to the tested configurations; selection effects are not isolated from condition wording. |
| Owner ratings prioritize completion over the frozen clarification rule | Preserve them as stakeholder feedback, with a separately labeled retrospective sensitivity illustration. No frozen score changes or independent adjudication claim. |
| Sharing checkpoint2026-11-03 | Master record refreshed against saved evidence; M1–M5 technical delivery remains complete locally. M6/probe unstarted; no new trials or independent human ratings supplied. |
| Serving screen completed 2026-11-13 | B failed throughput and first-call agreement gates; retain A. C skipped; no general correctness inference. |
| G1 owner-selected AI-only fallback | Label all results AI-authored; no independent teammate authorship or semantic-novelty claim. |
| G1 Stage 2 completed 2026-11-14 | Preserve 35 preliminary correct dev completions and one provider interruption; 94 charged requests, no failed-trial rerun. Four clarification transcripts await uninvolved human review. |
| Prospective P1′–P6 definitions confirmed | Both-domain requirements for P1′/P2; exact 20-point P4 boundary, sizes 3/5/10, P3 dropped, P6 descriptive. No dev adjudication. |
| Owner declined protected metadata hook 2026-11-15 | Source unchanged; G-c remains blocked, not waived. |
| Separate GPT-6 Astra scorer review completed | 41 new cases; six reachable clarification errors prevent G-e clearance. No source repair, live rescoring or human-review substitution. |
| Sharing checkpoint 2026-11-16 | Master now includes G1 development costs, current failed/blocked gates and prospective endpoints. Historical generated M4/M5 snapshot remains labeled; no new run, commit or upload. |
| Team-context review closed 2026-11-17 | `rosa-contexts` is a curated coordination mirror. Member-reported results and snapshot provenance checked within documented scope; no runtime integration, local governance replacement, publication or new experiment. G1 blockers unchanged. |
| Research standards adopted 2026-11-17 | Levinson's research rules govern new work: five-question preflight, evidence labels, fair controls ([adopted rules](docs/research-governance-20261117/ADOPTED_RESEARCH_RULES.md)). Not retroactive. |
| Execution host policy 2026-11-19 | All trials, tests and formal analysis run on the lab over SSH; laptop work is limited to inspection and documentation. A report is written after every run. |
| G1 Sol held-out closed 2026-11-19 | 73 PASS, 3 censored; P1′ Support, P2 Uninformative, P5 Support. |
| G1 Qwen closed 2026-11-20 (zero-inference closeout on the lab) | All tasks P→M 26/38→31/38; known-goal 26/36→30/36. P2 Against, P1′ Uninformative, P5 Support; H-write not tested on Qwen. |
| G1 three-model extension closed 2026-11-20 | Ministral known-goal 28/36→33/36; Granite/Llama near zero (tool-call integration). H-write Uninformative for all. Exploratory only. |
| Commit selection 2026-11-20 (owner delegated) | 7,931 evidence/code files committed (`7260cb8`); 2,727 raw traces/duplicates kept out of git in a hashed backup; private handoff local only. Pushed by Martin (`988cfd8`). |
| Freeze ~~handed to Levinson (2026-11-20)~~ → done by Martin 2026-11-21 | Tag `freeze-2026-11-21` on `0cd6748`; manifest of 10,735 files; `verify_freeze.py` must PASS on every new branch. New work only on new branches and in new directories. |
| F1 Stage 0 designed 2026-11-21 | Branch `member/martin-f1`; code in `tools/f1_wording/`, because `tools/f1/` is frozen. W2 is prompt-only (`submit_report` has no clarification status). Scripted controls are pending the lab; thresholds await Martin; Stage 1 not authorized. |
| Master README formatting repaired 2026-11-21 | A 2026-11-17 rewrite produced `\r\r\n` line endings; the later line-ending cleanup turned each into an extra blank line, splitting about 700 sentences and breaking 26 tables. 1,768 inserted blank lines were removed using the pre-cleanup backup as a map; every non-blank line is byte-identical. |
| F1 thresholds confirmed 2026-11-21 (Martin) | P-c covers 10 cases; P-f safety veto added (it cannot fire by construction; P-f′ diagnostic pending an owner decision); P-a fixed at net ≥ +3; F1 dev corrected to the 18 G1 dev cases. Gate G1 blocked by lab outage. |
| F1 D11/D12 2026-11-21 (Martin) | P-f′ (movement-skill selections on 16 non-movement no-dispatch cases, Q-new > Q-base) replaces P-f as the veto; P-f kept as a diagnostic. Sol arms run on the laptop WSL env as G1 Sol did (documented exception), conditional on identical code hashes with the lab copy. Limitation 26 added. |
| F1 D13–D15 2026-11-21 | D12 approved (same env, back to back; no F1-vs-G1 Sol comparison made). Laptop dry run approved after the lab controls, or first if the lab is down, labelled laptop-only. F1 classified **new, with adjacent overlap** against Levinson's `rosa-contexts` branch (closest negative: his headroom Stage 3d). |

For a new assistant: read this document, refresh/inspect actual current state,
then follow the user's requested task. Do not claim the project is finished,
all stages passed, the full ROSA catalogue was benchmarked, Qwen was trained,
memory/JTVR was completed, or physical robot safety was demonstrated.



## Appendix A — Chronological checkpoint archive (2026-10-27 to 2026-11-20)

> Moved here unchanged on 2026-11-21 from the top of this file. Each block was the "current" status
> on its date, newest first. For today's state see [section 2](#2-current-verified-status); for results
> see [Results at a glance](#results-at-a-glance-all-studies).

### A.1 Checkpoints 2026-11-17 to 2026-11-20 (newest first)

**Publication - 2026-11-20.** The owner explicitly approved the full public 22-commit
payload; evaluation `member/martin` was pushed to **8f961b5**, verified on GitHub, with
`main` unchanged. That approval covers the published payload, not arbitrary future
uploads. Later documentation commits are local until separately approved for push.
Operational lab-access details are kept in a private local handoff, not in this
repository. The lab root Git checkout is older; the actual G1 execution mirror is a
separate source/evidence snapshot, not a Git checkout. Do not blindly synchronize one
over the other. The lab GPU is shared with another project; recheck and coordinate
before any future model load, and never stop the other project's work.
Historical checkpoints below preserve earlier status; the newest dated blocks
and final reports take precedence. In particular, the old Stage3-blocked wording
is superseded: Sol and the three-model extension are closed; ~~Qwen BatchB is pending~~
(superseded: Qwen Batch B was closed and adjudicated on 2026-11-20).

**Current closeout - 2026-11-20: extension T6 COMPLETE.** Levinson’s 12 actual
ratings are bound after Martin forwarded the completed declaration (review date
2026-11-19; five affirmative self-attestations; teammate relationship disclosed).
The original ZIP and blank declaration are retained; the supplemental statement
is separately attributed. Eligibility is self-attested, not external validation.
All 228 extension attempts now have final outcomes. Primitives versus macro:
Ministral **29/38 vs 35/38**, Granite **1/38 vs 0/38**, Llama **0/38 vs 1/38**.
Known-goal results remain **28/36 vs 33/36**, **0/36 vs 0/36**, **0/36 vs 1/36**.
Granite’s single pass is clarification, not native task execution.

The frozen analysis ran on the lab with 10,000 whole-template-group bootstrap
draws per model (seed 20261113); all new-backend outputs remain exploratory.
H-write is **Uninformative for each model and overall**, because all three hit
the predefined write-arm floor/ceiling override. P2’s ±25% native-operation
rule is Against for Ministral/Llama and Uninformative for Granite. P1′ outputs
on new backends are diagnostics of the originally Sol-specific endpoint; P3
is dropped and P4 catalogue probing was not run. P5 is an engineering gate.

Ministral uses **154→83 calls**, **5.32→3.18 seconds per task** and **102→127
native operations** over all attempts. Its 28 matched successful pairs use
**111→59 calls**, **144.43→92.62 task seconds** and **85→87 native operations**.
Granite/Llama still have no matched successful pair. Their short failure times
are not evidence of useful efficiency. No generic reliability or model parity
claim follows. All raw evidence, frozen inputs/backend seals and 228 local plus
228 persisted audits verify. **Zero new model requests**; the 710 charged total
is unchanged. No experiment, runtime change or Git publication occurred.

The [adjudicated report](G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md) supersedes
earlier pending extension checkpoints below. Qwen Batch B’s separate four-case
human review remains pending; no extension labels were transferred to it.

**Current review checkpoint - 2026-11-20: all 12 extension ratings received;
T6 remains BLOCKED because the reviewer declaration is blank.** Martin supplied
`lev'srating3.zip`; all 12 H01?H12 entries name Levinson, have permitted labels
and reasons, and match the issued extension packet, source hashes and rendered
transcripts. The original ZIP and both member files are preserved unchanged.
The declaration is byte-identical to the blank issued template: actual review
date, eligibility, exposure and personal scoring without AI/coaching are not
attested. No independence, accepted adjudication or final scores are inferred.
Levinson only needs to complete and return the declaration; he need not repeat
his ratings. Formal frozen analysis and H-write closeout remain withheld.
Qwen Batch B's separate four-case review is still outstanding. No new model
requests, raw-result changes, experiments or Git publication occurred.
See the [intake status](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/operator/human-review-intake-20261120/INTAKE_STATUS.md)
and [declaration-only follow-up ZIP](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/operator/human-review-intake-20261120/DECLARATION_TO_COMPLETE.zip).
The earlier execution checkpoint below remains accurate for measured outcomes;
its statement that no ratings were received is superseded by this intake note.

**Current state - 2026-11-19: all228 exploratory extension attempts COMPLETE;
actual human review and formal closeout remain pending.** The authorized fixed
sequence finished Ministral, Granite and Llama on the lab. All76 attempts/model,
including failures, are retained. **701 inference +6 preparation +3 cleanup
=710 charged requests**, within the separate611-request ceilings: Ministral240,
Granite79, Llama391. No infrastructure retries, censored trials or replacement
attempts occurred. All228 local and228 persisted Phoenix audits pass. All models
are unloaded. No Qwen/Sol rerun, OAuth, Gazebo, model download or Git publication
occurred.

These are **exploratory backends, added after Sol and Qwen results**, using the
same38 AI-authored mock cases. Known-goal counts below exclude the two ambiguous
cases per condition. Calls, time and native work include all38 attempts/condition.

| New backend | Known-goal primitives | Known-goal macro | Calls P → M | Mean task seconds P → M | Native operations P → M |
|---|---:|---:|---:|---:|---:|
| Ministral3 8B | 28/36 | 33/36 | 154 →83 | 5.32 →3.18 | 102 →127 |
| Granite3.3 8B | 0/36 | 0/36 | 38 →38 | 3.55 →3.15 | 0 →0 |
| Llama3.1 8B | 0/36 | 1/36 | 203 →185 | 1.96 →2.11 | 42 →122 |

Ministral is the strongest new local configuration observed here. Its27 matched
successful pairs used110 vs58 calls and142.54 vs90.47 measured task seconds,
with85 vs87 native operations. All-attempt calls fell46.1%; correctness rose by
five known-goal passes as a point observation, not a proven general reliability
gain. Granite returned76 text responses with0 recognized native calls; inspected
outputs rendered tool-shaped JSON as text. Llama returned383 native calls but
had150/135 invalid attempts and37/31 budget endings P/M. Faster failure is not
useful task efficiency; neither Granite nor Llama has a matched successful pair.
Do not interpret these results as intrinsic model rankings.

All-attempt outcomes are Ministral61 PASS,12 FAIL,3 primary pending; Granite0
PASS,72 FAIL,4 pending; Llama1 PASS,75 FAIL,0 primary pending. Nevertheless,
**all12 new clarification transcripts require actual semantic review**: five
already fail structural bounds, so favorable semantic ratings cannot turn those
into passes. Levinson is nominated; an honest eligibility declaration and his
actual ratings have not been obtained. The new shuffled packet is separate from
Qwen Batch B's four outstanding responses and from earlier Sol/development/M4
reviews. No AI ratings or reused human labels were supplied. T1–T5 are complete
with the documented reporting qualifications; **T6 is BLOCKED pending actual
ratings**. Formal frozen analysis and H-write closeout are withheld.

The corrected predefined eight-case write-bearing counts are Ministral4/8 vs8/8,
Granite0/8 vs0/8, and Llama0/8 vs1/8. Other known-goal counts are24/28 vs25/28,
0/28 vs0/28, and0/28 vs0/28 respectively. Six healthy writes plus the two frozen
`write_fault` cases form that eight-case group. The predefined floor/ceiling rule
must take precedence; do not call the favorable Ministral point pattern H-write
Support while ignoring its8/8 ceiling. No frozen hypothesis or threshold changed.

All recorded loaded-model telemetry samples show full GPU residence at8K context
(96/96 Ministral,89/89 Granite,80/80 Llama). The extension used the disclosed
replacement Jazzy image and unchanged pinned dependencies/settings. Earlier Qwen
used another image; Sol retains its original hosted/laptop-WSL provenance. The
full report provides their contextual results without pooling rates or claiming
hardware-matched speed, general model parity or case generalization. This job
uses mock operations, not new ROS-controller/Gazebo/physical-robot execution.

Three preflight metadata transcriptions were corrected in a dated addendum while
preserving the acknowledged original; actual sealed configuration/digest checks
were correct. A reporting-only host/container invocation error was repaired after
trials finished. The first descriptive helper also omitted `write_fault`, showing
6/30 instead of8/28; corrected derived outputs now supersede that table, with
old source/output/ZIP retained. These are documented reporting errors, not quiet
changes to scorers, raw scores, cases, prompts, budgets or formal analysis.

The3,796 frozen inputs,1,159 retained Sol/Qwen hashes,three backend seals and228
raw trial hashes reverify. All2,019 entries of the initial completed archive
verified after local transfer. That archive retains superseded derived tables;
the share package marks the corrected report/JSON authoritative. No live Phoenix
database backup or model-weight upload is claimed.

Share the [complete corrected comparison report](G1_MULTIMODEL_REPORT_2026-11-19.md)
and [report/evidence share ZIP](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/G1_MULTIMODEL_SHARE_20261119.zip).
For Levinson, send **only** the [neutral12-response review ZIP](artifacts/reviewer-delivery-20261119/G1_EXTENSION_CLARIFICATION_REVIEW_2026-11-19.zip).
The [task status](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/STATUS.md)
records the remaining human gate. Preserve original Qwen/Sol/M4 results; this
closeout does not authorize another experiment, default-model switch or Git push.
Earlier checkpoints below are retained history and are superseded by this block.

**Earlier live checkpoint - 2026-11-19: three-model exploratory batch was RUNNING;
superseded by the execution closeout above.**
The owner read the combined preflight and explicitly replied: "I read the
preflight—launch the three-model batch." The detached, sleep-inhibited sequence
started at **22:26 Taipei time**, in fixed order Ministral, Granite, Llama.
Ministral has now completed76/76 attempts:61 PASS,12 FAIL,3 pending human review,
0 infrastructure-censored. Known-goal correctness is28/36 primitives versus33/36
macro. All-attempt calls154 vs83, mean task time5.32 vs3.18s and native operations
102 vs127. There are27 matched successful pairs; costs there are110 vs58 calls
and142.54 vs90.47 task seconds. All76 local and76 persisted audits pass. Its
237 inference +2 preparation +1 cleanup requests total240/611. Four actual
clarification ratings are still required, including one structurally failed
response. These are descriptive outcomes, not a final human-adjudicated verdict.
Granite completed76/76 attempts:72 FAIL,4 pending human review; known-goal
correctness0/36 in both conditions. It produced0 recognized native tool calls
and0 native operations. Inspected outputs contain tool-shaped JSON as text;
this is a limitation of the tested integration, not proof of intrinsic inability.
One trial had a response-length stop. Granite spent76 inference +2 preparation
+1 cleanup =79/611 charged requests. Llama is now running. Early Llama records
contain recognized native calls but repeated schema/validation failures; no
final Llama outcome is inferred. Do not assume unstarted outcomes.
Counters and preserved attempts are in each backend's status/ledger.
Three metadata values were transcribed incorrectly into the acknowledged
preflight prose: Ministral's displayed digest and disk bytes, and Llama's loaded
size. The original acknowledged document is preserved unchanged; the
[dated correction](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/PREFLIGHT_DISPLAY_CORRECTIONS_2026-11-19.md)
gives the exact sealed values. Installed server digests rechecked against all
three unchanged configurations; the actual launch used those correct sealed
values. This is a documentation error, not a model replacement or protocol edit.
The original protected inputs, three backend seals, service health and sleep
inhibitor permission passed the final zero-inference check. Request caps,
eight-hour backend windows, fresh idle gates and actual human-review requirements
remain as specified below. No further acknowledgment is needed for this authorized
sequence unless a genuinely new authorization boundary is reached.

**Earlier preparation checkpoint - 2026-11-19: three additional local backends
prepared; combined launch acknowledgment subsequently received as above.** The owner supplied a bounded G1
extension for **Ministral 3 8B, Granite 3.3 8B and Llama 3.1 8B Instruct**, in that
fixed order, using the same38 AI-authored cases and primitives/macro conditions:
**76 attempts/model,228 total**. These are **exploratory backends, added after
Sol and Qwen results**, not a new independently authored held-out catalogue.
No model or case substitution, prompt/template/parser repair, download, Qwen/Sol
rerun, Gazebo run, OAuth, catalogue probe or Git publication was performed.

**Benchmark attempts remain0/228.** Eligibility preparation charged **six empty
load/unload requests**, two per model, inside separate611-request total caps.
At most609 requests/model remain, including inference, eligible retries and final
unloads; the three-model aggregate cap is1,833. Each backend has its own eight-hour
live window. Approximately200 inference requests/model is only a planning
reference from earlier batches, not an estimate of missing counters or a promise.
The owner's supplied T2/T4 explicitly requires reading and acknowledging the
combined preflight once before any new benchmark launches. The later instruction
to continue preparation has not been represented as acknowledgment of a record
that did not yet exist.

All three report native tool capability and loaded wholly on the lab GPU at8K
context: **Ministral35/35 layers, Granite41/41, Llama33/33**. All use installed
Q4_K_M weights; exact tags, digests, byte sizes, family and advertised context are
recorded in the preflight and sealed configurations. No thinking capability is
advertised; the common `think=false` wire field is retained. All **24 scripted
controls**,24 local audits and24 persisted Phoenix audits passed, and **144
serialized request bodies** matched the unchanged adapter. Six timing fields
survived injected-response checks. Missing live-model usage/cached-token counters
remain unrecorded; scripted checks are not model-performance results. The runner
also failed closed without its execution flag or launch acknowledgment.

The earlier container and its image became unavailable externally during
preparation. The extension now uses its own container and another **already
installed ROS2 Jazzy image**, `sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2`,
with the same verified pinned Python dependencies. This differs from Qwen's
original image; no identical-image replication is claimed. An extension-owned
Phoenix service stores new traces separately, with raw control exports retained.
No other project's container/server was modified. The GPU idle gate passed at
the original threshold, with a fresh gate required before each backend. No
benchmark is protected against explicit reboot or power loss. Execution will be
detached with a scoped sleep inhibitor and GPU/container/model telemetry.

These G1 operations are **mocks inside the ROS2/Jazzy software environment**;
they do not command Gazebo, controllers or hardware. Earlier M4 and transfer
experiments actually used Gazebo and remain separate evidence. The fixed source,
cases, scorer, thresholds, original3,796 input hashes,1,159 retained Sol/Qwen file
hashes and three new backend seals reverified. Preparation log-decoding and idle
gate interruptions are retained, without repeating successful load/control work.

The written H-write comparison is prospective only for these additional
backends, derived from Qwen's retrospective2/8 vs6/8 write-bearing and24/28 vs24/28
other known-goal split. It uses the owner's confirmed raw-count rule, with0/8 or
8/8 in either write arm forcing Uninformative. Fifteen synthetic boundary checks
passed on the lab. This rule can support write concentration even if overall
accuracy worsens; both must be reported. Do not pool backend pass rates or claim
new case generality. The requested P-label correction was inconsistent with the
adopted November14 definitions: a factual addendum preserves **P3 dropped horizon
reliability; P4 catalogue probe not run**. P1′ retains its original Sol-specific
formal scope.

**Levinson is nominated for the new pooled clarification review, not yet
attested or scored.** After live execution, prepare a separate blinded packet
of up to12 new transcripts. Qwen's four-transcript Batch B remains outstanding
separately. No assistant ratings are permitted. Produce descriptive reports after
each backend; the unchanged formal analyzer remains withheld until actual human
ratings are bound. T4's immediate-analysis wording does not remove T6's gate.

Read the [combined launch preflight](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/READY_PREFLIGHT.md),
[task-by-task status](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/STATUS.md),
[dated Qwen definition addendum](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/QWEN_REPORT_ADDENDUM_2026-11-19.md)
and [preparation evidence archive](artifacts/macro-generalization-20261113/revision-1/stage-4-multimodel-20261119/G1_MULTIMODEL_PREPARATION_20261119.zip).
Completed Qwen and Sol results below remain unchanged; earlier current-state
headings are historical checkpoints superseded by this block.

**Completed Qwen result - 2026-11-19: Qwen lab execution COMPLETE;
human adjudication pending.** All **76/76 G1 mock attempts** finished in one
uninterrupted batch,19:45:22-20:05:33 Taipei time. Effective outcomes are
**56 PASS,17 FAIL,3 PENDING_HUMAN_REVIEW,0 infrastructure-censored**. Primitives:
26 PASS,11 FAIL,1 pending; macro:30 PASS,6 FAIL,2 pending. Known-goal correctness
is **26/36 versus30/36**, including13/18 versus15/18 in each domain. Four new
clarification transcripts need real semantic ratings: one already fails
structural/runtime requirements, so only three primary outcomes are undecided.
The frozen final analysis remains withheld until the required ratings arrive.
No Sol/development ratings were reused and no human judgments were invented.

The batch spent **198 inference requests plus1 earlier auxiliary load =199/611
charged requests**, with0 infrastructure retries,0 task-budget exhaustions and
no replay or replacement. All **76 local and76 persisted Phoenix audits pass**;
3,796 original frozen inputs and81 sealed backend files reverify unchanged.
The completed export's **662 manifest entries verified** after transfer. Source,
raw outputs, failures, traces and operational repairs are retained.

All-attempt primitives versus macro costs: **123 vs75 calls**,264,961 vs152,127
input tokens,25,878 vs18,791 output tokens,100 vs106 native operations and322.22
vs239.86 summed task seconds. Mean task time was8.48 vs6.31s; median7.93 vs5.90s.
Across the **25 pairs where both conditions passed**, calls were87 vs52
(40.2% fewer), task time221.63 vs159.90s (27.9% less), and native work87 vs86.
Conditional successful-pair costs do not replace all-attempt accounting. Total
campaign time was1,210.25s, including auditing/bookkeeping outside measured tasks.

Qwen still has substantial failures. Seven trials stopped on response length
(4 primitives,3 macro); five other failures had incorrect selection and five
had correct selection but failed execution/reporting. There were0 recorded
dispatch violations and0 unsupported accepted SUCCESS flags, but **one accepted,
evidence-grounded SUCCESS for the wrong requested goal in each condition**.
Skill-report truthfulness and user-goal completion remain separate. These
descriptive buckets are not a causal diagnosis or new preregistered predictions.

All198 inference calls retained all six Ollama timing fields; aggregate decode
rates were89.96 and89.55 tokens/s. Cached-token counters were not returned.
Telemetry sampled only Ollama and the existing remote-desktop compute processes;
no fixed OOM/reset/runner-termination signatures were counted. The scoped sleep
inhibitor ended normally. **Lab hardware; not directly comparable to M4**.
This is neither a controlled laptop/lab comparison nor proof of parity with Sol.
The previous adjudicated Sol results remain73 PASS and3 censored, unchanged.

See the [complete Qwen report](G1_QWEN_LAB_REPORT_2026-11-19.md),
[verified evidence ZIP](artifacts/g1-lab-preparation-20261119/G1_QWEN_LAB_COMPLETED_20261119.zip)
and [neutral four-transcript review ZIP](artifacts/reviewer-delivery-20261119/G1_HELDOUT_REVIEW_BATCH_B_2026-11-19.zip).
Send only that neutral review ZIP to the reviewer; model labels, mappings and
prior scores are withheld. Return their actual CSV and declaration. The next
authorized work is intake and unchanged final analysis, with zero inference.
P3 remains dropped; the separate P4 catalogue probe is **not run**. No optional
replay, new study, Gazebo batch, architectural change or Git publication began.
Earlier launch/readiness/pending snapshots below are retained historical records
and are superseded by this current-state block.

**Earlier launch checkpoint - 2026-11-19: Qwen lab batch was RUNNING.** The owner read the
preflight and gave the launch go-ahead. The detached worker started at **19:45
Taipei time**, using the existing lab Jazzy container and local Qwen. All76 mock
trials remain scheduled, with the original eight-hour window and611 total
charged-request ceiling, including1 auxiliary load already spent. Fresh GPU idle
samples passed; no other application was terminated. A temporary sleep/idle
inhibitor and read-only GPU/container telemetry are active. Reboots, power loss
and explicit shutdown can still interrupt execution. Only unstarted cells may
resume after integrity checks under the original cumulative limits.

The final zero-inference checks matched **48 serialized request bodies byte for
byte** against the unchanged adapter and verified preservation of all six Ollama
timing fields with an injected response. NVIDIA driver570.195.03, reported CUDA
compatibility12.8 and the container image digest are recorded. Frozen runtime,
prompts, cases and model settings were not changed. The original idle model
retention remains; any load costs are recorded rather than silently excluded.
The [launch checklist and limitations](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/operator/LAUNCH_CHECKLIST_ADDENDUM.md)
links the operational evidence. New Qwen clarification answers will require new
human ratings. No live results or correctness conclusions are available at this
launch checkpoint. No optional replay, catalogue probe, Sol replication or Git
publication is authorized by this launch. Catalogue size is P4 and is not run;
P3 is dropped. Label Qwen tables **lab hardware; not directly comparable to M4**.
This is not a controlled laptop/lab speed comparison. The completed adjudicated
Sol results remain unchanged. Earlier readiness and pending-review snapshots
below are dated history, superseded by their later current-state updates.

**Earlier preparation checkpoint - 2026-11-19: Qwen lab preflight ready; acknowledgment subsequently received and launch completed as above.**
The owner chose to retain the adjudicated first Sol batch and prioritize Qwen;
no Sol replication is scheduled. Qwen has **0/76 benchmark trials started**.
Its exact frozen model digest is present on the lab. The established Jazzy
container imports ROSA/Ollama successfully; eight scripted backend-port controls
pass with8/8 local and8/8 persisted Phoenix audits. These are zero-inference
engineering checks, not live Qwen performance evidence. The original3,796 frozen
inputs and the new81-file backend assembly verify unchanged.

One auxiliary empty-prompt model-load request established33/33 GPU layers,
Flash Attention enabled,8K loaded context and f16 server KV configuration. Its
6.59s setup time/response/log are preserved; omitted internal usage counters
remain NOT_RECORDED. **This1 request is charged inside the611 overall ceiling**,
leaving at most610 inference/retry requests for the76-trial batch. The live
backend window is8h, with the original per-task call/token/native limits. Model
may auto-unload while awaiting review; fresh idle GPU samples are taken before
actual launch. No other workload is stopped. No OAuth is needed for local Qwen.

Wire validation identified a documentation discrepancy: the pinned adapter's
LangChain streaming=False setting still produces API stream=True. Client
cache=False also does not disable the lab server's prompt cache, which its log
reports enabled. The port preserves actual frozen adapter behavior and records
these facts; it does not force different settings to improve outcomes. The first
wire check stopped on its incorrect False assumption before live inference or
scripted trials; corrected golden comparison and eight controls passed.

The existing G1 final freeze/preflight review gate remains: the owner-readable
[Qwen READY_PREFLIGHT](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/READY_PREFLIGHT.md)
is complete, and final launch acknowledgment has been requested. The detached
lab operator is prepared but has not started a benchmark. New Qwen clarification
responses will require new human ratings after execution; Sol ratings cannot be
reused. No catalogue probe, Gazebo study, source-module rewrite, new hosted
sign-in or Git publication is part of this preparation. The
[adjudicated Sol report](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md) remains the completed
comparison for that backend, with its original provenance and all failures retained.

**Current G1 adjudicated status - 2026-11-19.** Levinson returned the four new
held-out ratings: YES on both criteria in H01-H04, with actual reasons and his
eligibility declaration preserved and bound to the issued transcript/evidence
hashes. Eligibility is based on his attestation, not independently verified;
team membership and his separate earlier dev review are disclosed. No ratings
were invented or transferred between cases. **The first Sol batch now has73 PASS,
0 evaluable FAIL and3 infrastructure-censored attempts, with0 pending judgments**.
V2 correctness is35/35 primitives and38/38 macro; V3 counting censored attempts
as failures is35/38 versus38/38. Do not treat that operational difference as
proved reliability improvement. All76 attempts and200 physical requests remain.

Final analysis ran on the **lab via SSH** with the unchanged frozen analyzer,
10,000 whole-template-group bootstrap draws and zero inference requests. This
analysis host does not rewrite the original batch's laptop-WSL orchestration and
hosted Sol provenance. P1-prime is Support, P2 is Uninformative (V2 Support,
V3 Against), P3 Dropped, P4 not yet tested/Uninformative, P5 Support, P6 descriptive.
Across the35 matched successful pairs, primitives versus macros used **120 vs68
calls,186,400 vs103,332 input tokens,3,597 vs2,238 output tokens,487.76 vs280.38
summed task seconds, and111 vs103 native operations**:43.3% fewer calls and42.5%
less measured task time. Small groups, missing bootstrap cells, AI authorship,
condition wording and unequal censoring remain material limitations.

The owner selected **prioritize Qwen on the lab; retain completed Sol results**.
No extra Sol replication is scheduled and no fresh hosted sign-in is needed for
Qwen. All future tests/trials execute on the lab. Qwen's exact model/settings,
resource and frozen-input readiness must be established before live launch.
New Qwen clarification responses will require their own ratings; Sol judgments
cannot supply them. See the [adjudicated Sol report](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md)
and its linked raw analysis/intake/lab-export records. Earlier pending/launch
snapshots below are historical and superseded by this current-state block.

**Execution host policy - 2026-11-19 (current owner instruction).** All future
automated tests, deterministic controls, model probes and trials must execute on
the **lab computer via SSH**, using the existing lab-rosa target and
/media/naeem/d1/marvel proj/. Local editing/document and evidence review remain
possible; do not silently fall back to laptop execution if the lab is unavailable.
SSH was verified with a read-only inventory: **RTX4080 SUPER,16,376MiB total,
15,916MiB free,0% utilization at that instant**. Zero inference requests or tests;
one sample is not the complete frozen idle/model/offload preflight. Laptop GPU
constraints do not describe this lab configuration. Keep applicable resource
budgets/settings and lab workload checks; record actual loaded offload/digest.

The completed76-attempt Sol batch below was orchestrated in laptop WSL with
hosted OpenAI inference; this new instruction does not rewrite that provenance
or rerun it. Future hosted runners also belong on the lab, while Sol inference
itself remains hosted. G1 already permits separately recorded lab hardware; record
the execution configuration before a newly authorized batch and distinguish
hardware-dependent timing. Existing review/launch gates and consent boundaries
remain. See the [execution-host policy and verified inventory](docs/EXECUTION_HOST_POLICY_2026-11-19.md).

**Current G1 status - 2026-11-19: Sol execution COMPLETE; human review pending.**
All **76/76 scheduled Sol mock attempts** are retained, with **200/611 physical
requests**, zero eligible reserve retries and no trial replay/replacement.
Effective outcomes are **69 PASS, 0 evaluable FAIL, 3 infrastructure-censored
(1 pre-output, 2 post-action), and 4 PENDING_HUMAN_REVIEW**. Known-goal evaluable
correctness is **33/33 primitives and 36/36 macro**; this excludes censored and
ambiguous attempts and is not a claim of76 successful trials. Three provider
stream interruptions were preserved; only unstarted cells resumed with the
original freeze, cumulative counters and eight-hour origin. Their underlying
provider cause is unknown. **76/76 local and76/76 persisted Phoenix audits pass**;
all3,796 frozen source/input hashes match,245 previously retained trial files
reverify, owned services stopped and credential memory cleanup completed.

Across33 matched successful pairs, primitive versus macro costs were **118 vs66
calls,183,745 vs100,679 input tokens,3,503 vs2,138 output tokens,480.67 vs271.66
summed task seconds, and111 vs103 native operations**. These correspond to44.1%
fewer calls and43.5% less measured task time. All-attempt costs, including censored
and pending work, are126 vs74 calls and504.38 vs317.70 task seconds (means13.27
vs8.36s). Three primitive records have incomplete token usage; missing values are
not estimated. Campaign elapsed including setup/pauses was35.08min. No pair gap
exceeded30min. This is descriptive evidence on the fixed AI-authored catalogue,
not a final prediction verdict, general reliability claim or stock-ROSA comparison.

The next gate is actual uninvolved human review of the **four new held-out
clarification responses**. The older dev ratings cannot be reused. A new blinded
packet contains transcripts, the unchanged rubric, blank ratings and declaration;
no ratings were invented. After real submission intake/content binding, the
unchanged frozen analysis can issue its final views/bootstrap/predictions.
Qwen/catalogue stages remain unstarted; no additional stage, consent or Git
publication is authorized here. See the complete
[G1 Sol execution report](G1_SOL_HELDOUT_REPORT_2026-11-19.md) and
[new blinded review packet](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/heldout-human-review/G1_NEW_HELDOUT_HUMAN_REVIEW_2026-11-19.zip).
Earlier dated checkpoints below are historical snapshots, superseded by this
current-state block where their pending/launch descriptions differ.

**G1 Sol held-out continuation - 2026-11-19.** The initial segment retained
three trials and eight charged requests, then stopped on an in-stream provider
error after one native acquisition. All three local and persisted Phoenix audits
passed. The affected primitive trial G1r1-heldout-018-primitives is retained as
INFRA_CENSORED_POST_ACTION; its unknown provider cause is not called quota
exhaustion or a wrong model decision. Under the owner's standing recovery
instruction, integrity was verified and an outer continuation started only the
73 unstarted cells, using the exact frozen trial function and model/settings.
The first three trial files remain unchanged. All eight spent requests, retry
reserve state and original eight-hour origin are carried forward; no failed
trial is repeated, no new consent is granted, and no frozen source is edited.
See the [continuation record](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/continuation-01/CONTINUATION_RECORD.json).
Current cumulative state remains stage-4/status.json. A live continuation is
not a completed campaign; future human clarification judgments remain required.

**G1 Sol held-out launch acknowledged and started - 2026-11-19, before interruption.** The
owner explicitly replied "I read the preflight-start the Sol run" (the original
reply with punctuation is retained in stage-4/owner-launch-acknowledgment.json).
The acknowledged frozen scope is76 Sol mock trials,611 physical requests maximum,
8h backend window, unchanged cases/conditions/budgets/retry rules. A detached
launcher was started and its process verified alive; it is checking the source
freeze before owning Phoenix and restoring authorization again. Trial completion
and success are not inferred from launch. Durable status is
[stage-4/status.json](artifacts/macro-generalization-20261113/revision-1/stage-4/status.json)
and operator/launcher.log in that same run directory. No new consent, Qwen stage,
physical robot or publication is authorized. New ambiguous outcomes require new
human review; preliminary execution is not a final campaign verdict. Later
checkpoints supersede this launch snapshot without rewriting frozen evidence.

**G1 held-out freeze and technical preflight complete - 2026-11-19, before owner acknowledgment.** The
owner requested test commencement after preparation. The new 38-case/76-trial
Sol mock batch is assembled with the two approved repairs; six new wiring tests
pass and3,796 frozen files verify. The fresh restore-only preflight successfully
renewed remembered authorization once, validated unchanged scopes and model
availability, retained the opted-in encrypted credential and cleared memory.
Zero inference requests. Quota remains UNKNOWN. Caps remain608 ordinary +3
eligible reserve attempts,8h backend, with original per-task limits. No trial
has started. The original protocol still requires owner acknowledgment of the
completed preflight before launch; that final review is pending. No new consent,
Qwen stage, robot action or Git publication occurred. See the
[completed preflight](artifacts/macro-generalization-20261113/revision-1/stage-3/freeze-launch-preparation-20261119/READY_PREFLIGHT.md).
New held-out clarification responses will need their own real blinded review;
current dev ratings do not transfer. Historical artifacts remain preserved,
including the pre-freeze helper's corrected control-key lookup error.

**G1 second repair completed - 2026-11-19, before final freeze/preflight.** The owner explicitly accepted
reduced metadata coverage while keeping protected code unchanged. The new G1-local
observed transport passed all 12 integrated zero-model test methods, including
six injected failure classes through the real parser, ChatSiwc and G1 recovery
gate. Request contents, error semantics, availability, accounting and retries
matched the unchanged implementation. Discarded HTTP provider fields remain
NOT_RECORDED, as do stream fields before observation is possible. The canary was
absent from saved metadata/logs. G-c is PASS against the approved reduced contract;
the original full-coverage failure is preserved. Protected source, earlier data
and the reviewed clarification-v2 layer are unchanged. Both repair decisions are
now explicit; neither awaits another approval. See the
[metadata repair report](artifacts/macro-generalization-20261113/revision-1/stage-3/error-metadata-v2-20261119/REPAIR_REPORT.md)
and [latest gate status](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-19_METADATA_REPAIR.md).
The exact new execution/analysis assembly, protection scope and final freeze
remain to be verified; the fresh restore-only preflight follows that freeze.
No current provider validity/quota is established. No held-out trial, credential
operation, robot action, Git commit/push or publication occurred. Future launch
still needs the separately specified authorization after review of the preflight.

**G1 first repair completed - 2026-11-19, before metadata repair.** The owner authorized the first,
clarification-scoring repair. The new G1-local v2 layer uses actual eligible human
judgments, leaves absent/CANNOT_JUDGE semantics explicitly pending, rejects wrong
or duplicated bindings, and prevents human approval from overriding action or
runner bounds. The regex remains diagnostic; old scores/results stay immutable.
All15 implementer test methods pass. Renewed separate GPT-6 Astra review gives
**PASS for this exact effective layer within its trusted-input boundary**:65
original cases (63 matched,2 preserved reviewer construction errors), plus2
corrected cases (2 matched); no substantive scorer defect. The old regex-only
review remains historically FAIL. Four real Levinson ratings are bound and G-f
remains PASS on his eligibility attestation. The retrospective dev view remains
35 evaluable passes plus1 infrastructure-censored attempt, with unchanged costs.
No new model-performance result is claimed. G-c metadata remains BLOCKED and its
amendment unapproved; freeze/preflight/held-out launch remain blocked. No inference,
OAuth/robot action, protected-source change or Git publication occurred. See the
[repair report](artifacts/macro-generalization-20261113/revision-1/stage-3/clarification-scoring-v2-20261119/REPAIR_REPORT.md)
and [current G1 status](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-19_SCORING_REPAIR.md).
Future analysis must retain pending judgments/costs, validate the authoritative
schedule before projection, and require new real human review for new transcripts.
The generic validator does not independently authenticate reviewers; actual
submission provenance remains organizer-verified and eligibility self-declared.

**G1 human review received - 2026-11-19, before scoring repair.** Levinson returned the four G1 Stage2
ratings and completed declaration: YES on both criteria in all four cases.
The issued packet integrity and submission completeness passed. G-f is **PASS
on the submitted reviewer attestation**, which discloses team membership and
affirms no case/system/scorer involvement or prior transcript/result exposure;
this history is self-declared, not independently verified. Exact original files,
reasons and hashes are retained in the
[intake report](artifacts/macro-generalization-20261113/revision-1/stage-3/human-review-20261119/HUMAN_REVIEW_INTAKE_2026-11-19.md).
This does not amend the legacy scorer or prove independent generalization.
G-e remains FAIL, G-c remains BLOCKED, and the two proposed methodological
amendments remain unapproved pending discussion. No held-out launch, new model
requests, protected-source change or Git publication occurred.

**G1 preparation resumed - 2026-11-19, before review intake.** The owner returned to the three
outstanding Stage3 items: human-adjudicated clarification scoring, reduced error
metadata coverage with protected source unchanged, and actual uninvolved review
of four G1 cases. The owner chose to keep existing rules and discuss alternatives
before approving either methodological amendment, and confirmed the actual human
review was still pending at that point (the later intake above supersedes that
pending status only). No renewed scorer review is authorized by that reply.
The four-case
ZIP and12 sealed Astra review artifacts verified intact. The old protection check
reports one mismatch, the living master after authorized updates; its FAIL result
is retained, and a new freeze must explicitly disposition mutable-document scope.
All other checked protected entries match. No new source/scoring change, review
substitution, inference, credential action or held-out launch occurred. See the
[current G1 checkpoint](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-19.md).
Earlier dated checkpoints and all experimental evidence are preserved.

**Research standards adopted - 2026-11-17.**
The owner explicitly asked this assistant to follow the stable research rules
**provided by teammate Levinson** through `rosa-contexts`. The operative local
[adopted rules](docs/research-governance-20261117/ADOPTED_RESEARCH_RULES.md) and
[dated adoption record](docs/research-governance-20261117/ADOPTION_RECORD.md) are
now referenced by the workspace `AGENTS.md`. Before substantial future research
work, use the full five-question preflight: closest mechanism and actual
difference; observed need and honest denominators; concrete decision and
discriminator; genuinely capable fair controls without a hidden oracle; and the
smallest nonrepeating decision-changing next step. Preserve protocols, failures,
negative findings, complete cost accounting, evidence provenance and review gates.

This is a prospective governance change, not a new study or a retrospective claim
of full compliance. Martin's practical ROSA reliability/efficiency vision remains
the project direction; teammate-specific deadlines, language preferences and
historical launch decisions are attributed context. No experiment, runtime,
scorer, frozen result or G1 gate changed. Earlier experiment ZIPs retain the
master snapshot at their packaging time; they are not rewritten to include this
later policy update. The [source provenance](docs/research-governance-20261117/SOURCE_PROVENANCE.json)
pins the adopted upstream version and verifies both saved source files.

**Latest completed work - native-schema integration and robot reruns, 2026-11-17.**
The opt-in `native-schema-v1` profile was implemented and the authorized **80 Llama + 80 Granite Gazebo attempts completed**. This is a separate replication of known M4 cases, not a rescore or replacement of any historical result and not G1 held-out testing. Each model has40 attempts per condition:36 known-goal tasks and4 ambiguous requests. All16 ambiguous attempts across the two models remain pending actual human semantic review; their legacy regex scores are diagnostic.

| New backend/profile | Known-goal correct P / M | All-attempt calls P / M | Mean task seconds P / M |
|---|---:|---:|---:|
| llama3.1:8b-instruct-q4_K_M, native-schema-v1 | 21/36 / 28/36 | 190 / 113 | 2.37 / 2.16 |
| granite3.3:8b, native-schema-v1 | 5/36 / 9/36 | 210 / 193 | 6.81 / 5.18 |

Both previous configurations scored0/36 in each condition; those results remain frozen and available. The new profile adds model-native formatting guidance and current bound schemas to system messages and explicitly enforces HTTP stream=false. It does not choose skills, alias arguments, relax verification or automatically replay robot commands. Existing SDK argument normalization remains combined-system assistance. Actual HTTP bodies/responses and corresponding trace metadata were archived; the final tokenized/rendered Ollama prompt was not captured. The original adapter remains unchanged; the new module is `rosa-research/src/rosa_backends/tool_contract_ollama.py` and is opt-in.

Seven zero-network checks,12 deterministic mock controls,24 live validation attempts and20 deterministic Gazebo controls preceded the160 live robot attempts. Fresh validation scored9/12 for Llama and6/12 for Granite. The functional gate required at least one healthy complete loop in each mode, with all safety/tracing/budget checks passing; it was not an all-case reliability gate. The mock ineffective-write checker could accept a truthful no-write failure: that cell does not prove a failed command was attempted. The main Gazebo scorer kept the original stricter fault-exercise/dispatch checks. The initial float-versus-bool fixture defect stopped deterministic validation with zero model calls; its failed source/control/archive are retained, and a documented fixture-only revision preceded all live validation outcomes.

All216 completed validation/control/live attempts in this campaign passed local and persisted Phoenix audits. Independent read-only reconciliation verified archive manifests,75 frozen source/config hashes including the original69, model digests, schedule order, raw/checkpoint consistency, actual wire calls, token/resource bounds and cleanup. This is scripted evidence reconciliation, not outside scientific replication or a human semantic review. Validation budgets were96 requests/model; robot budgets were643/model, with the original8-call,2048-output-token and360-second task limits retained.

Costs above include all40 attempts, including failures and ambiguity. Task latency excludes simulator setup/reset and persisted-audit overhead; campaign elapsed time and matched-success costs are in the full report. Accepted evidence-grounded SUCCESS for a wrong user goal remains a separate failure category. Fewer calls or fast failure does not establish reliability. See the per-family, discordant-pair, native-operation and fault-exercise tables before choosing a backend.

The profile and explicit HTTP setting changed together, so their individual effects are not isolated. Primitive/macro mode and its original condition sentence remain coupled; a selection effect cannot be separated from condition wording. Four repetitions of familiar cases do not demonstrate independent generalization or intrinsic model parity. Older Qwen/Ministral serving profiles differ; no new Sol trial was run and no historical hosted comparison was replaced. No global default backend switch, new architecture or further study was authorized by completion of this replication. G1's existing scorer, instrumentation and real human-review gates remain unchanged.

Current evidence: [complete integration-rerun report](artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md), [independent raw-data analysis](artifacts/integration-rerun-20261117-r1/evidence/INDEPENDENT_RERUN_ANALYSIS.json), [shareable report and evidence ZIP](artifacts/integration-rerun-20261117-r1/delivery/ROSA_NATIVE_SCHEMA_RERUN_REPORT_AND_EVIDENCE_2026-11-17.zip) (kept out of git as a duplicate package; in the off-repo backup). The original Qwen lab repeat and first four-model lab study below are preserved reference configurations. Current documentation and evidence are backed up under the owner's lab project; no public upload or Git push was performed.

**Latest completed investigation - Llama/Granite integration, 2026-11-17.**
A separate, simulator-free investigation completed **48/48 local requests** (2 Qwen controls, 23 Llama, 23 Granite), with **zero actual tool/robot executions**. Old model digests and all69 frozen source/config hashes matched. No original trial, source, schema acceptance or model installation was changed. The corrected interpretation is that the earlier zero full-task scores describe those tested integrations, not inherent lack of model capability.

The saved Llama template puts function schemas inside a last-user-message branch, so request-level schema presence did not prove they were visible after tool-result turns. Granite's custom system prompt bypassed its default native-call formatting guidance; restoring that guidance produced the exact harmless call in all4 raw/adapter and streaming configurations tested. Both models returned correct SUCCESS and UNKNOWN calls in the combined native-format-plus-persistent-schema variant (2/2 each), but schema persistence alone failed those fixtures, and tested correction feedback remained unsuccessful. This is promising narrow integration evidence, not a completed robotics fix or a newly measured task success rate.

The pinned ChatOllama ignores constructor streaming=False: a zero-network reproduction sent HTTP stream=true; explicit invocation stream=False sent false. Earlier reports' nonstreaming wording therefore does not establish HTTP transport streaming was off. Also, the adapter preserved native call names/counts but automatically normalized two Llama list strings into arrays; report that assistance separately from exact server-output schema compliance. ToolMessage names are omitted by the converter, but restoring them showed no benefit in the two tested fixtures.

All48 responses were retained. My diagnostic initially raised35 post-response instrumentation assertions because SDK serialization removes empty/auxiliary fields. All35 were decoded by exact-request offline mock replay, with **zero additional model/network requests**; original failures and raw archives remain preserved. Local verification checked67 outer content hashes plus61 nested original hashes, source freezes, request accounting and settings. Tokens:11,027 input and1,319 output. No Phoenix server-side audit was run for this HTTP-level diagnostic; do not label it as a robotics trace-audit campaign.

That recommendation was subsequently implemented in the separately labeled native-schema rerun above; this investigation remains preserved as its preceding diagnostic evidence. Do not deploy the prototype silently, rescore old failures, or clear G1 gates. See [complete integration findings](artifacts/lab-integration-20261117/evidence/INTEGRATION_FINDINGS_2026-11-17.md) and [independent verification](artifacts/lab-integration-20261117/evidence/INDEPENDENT_INTEGRATION_VERIFICATION.json). Earlier ZIPs are unchanged and predate this correction.

**Latest completed addition - Qwen lab repeatability, 2026-11-17.**
The second lab Qwen batch completed **80/80 trials**, following **20/20 deterministic controls**. All **80/80 live local/Phoenix audits** and **74 source/config hashes** passed. The original 69 frozen files and earlier archives remain unchanged. Both lab runs use the identical installed Qwen3.5 9B Q4_K_M digest, 8K context, 1,024 output tokens per call, 2,048 per task, temperature 0 and seed 42; thinking is off. The current primary lab Qwen configuration uses the RTX 4080 SUPER with 16 GB VRAM. Historical laptop M4 used different hardware and is preserved as its own study. There was no new Sol run and no substitution into the historical paired Sol comparison.

| Qwen lab run | Known-goal correct P / M | Calls across all 40 attempts P / M | Mean task seconds P / M |
|---|---:|---:|---:|
| lab_run_1 | 27/36 / 28/36 | 188 / 98 | 12.39 / 8.56 |
| lab_run_2 | 26/36 / 28/36 | 185 / 97 | 12.01 / 8.52 |

There were **3 changed correctness outcomes among 72 identical known-goal cells** between lab runs. The report records directions and individual cells, not just aggregate scores. Each lab run has eight ambiguous attempts pending actual human semantic review; legacy regex scores are diagnostics. These are four repetitions of already-seen families, not new held-out tasks or independent generalization evidence. Costs include failures; matched-success views are reported separately. The latest study does not resolve G1 gates.

Full current lab reference and comparison: [Qwen repeat report](artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_COMPARISON_REPORT.md), [independent analysis](artifacts/qwen-lab-repeat-20261117/evidence/INDEPENDENT_REPEAT_ANALYSIS.json). The original multi-model comparison below remains unchanged. The misplaced outside-d1 paths were already absent; no matching temporary residue remained in the checked outside locations. Models, useful configuration, identity files and runtime dependencies were preserved.

**Earlier completed execution - first lab local-model replication, original profiles, 2026-11-17.**
The owner requested 80 trials **per model**, not original M4's 80 total.
All **320/320 scheduled Gazebo trials executed**: four local models, ten known
M4 task families, four repetitions and two conditions. Each model has 40
primitive and 40 macro attempts. Eight ambiguous attempts per model remain
pending actual human semantic review; the main correctness denominator is
**36 known-goal tasks per condition**, 72 per model. These repeated known cases
are not independent new tasks or G1 held-out evidence.

| Lab backend | Known-goal correct: primitives / macro | Calls over all 40 attempts: P / M | Mean task seconds over all 40: P / M |
|---|---:|---:|---:|
| Qwen3.5 9B | 27/36 / 28/36 | 188 / 98 | 12.39 / 8.56 |
| Ministral 3 8B | 28/36 / 28/36 | 156 / 82 | 4.83 / 2.31 |
| Llama 3.1 8B | 0/36 / 0/36 | 211 / 193 | 2.16 / 2.84 |
| Granite 3.3 8B | 0/36 / 0/36 | 40 / 40 | 3.13 / 2.64 |

Costs include failures and ambiguous attempts. Short failure times are not good
task efficiency. Same aggregate correctness also hides different errors:
Ministral passed all four macro constrained-pose cells Qwen failed; Qwen passed
all four partial-command cells Ministral failed. Both failed missing-prerequisite
cases. Among the **24 identical macro cells both completed correctly**, Ministral
took 45.53 seconds versus Qwen's 101.42, but used **53 versus 48 calls** and
**57 versus 52 native operations**. It was faster on this subset, not uniformly
cheaper by every measure. No general model-parity or reliability claim follows.

Llama's result is especially qualified: it selected the correct skill in **32/36
known-goal cases in each condition**, but failed the complete reporting/execution
contract. Repeated schema errors included `classification` instead of required
`status`, and `subject` instead of `nodes`. A macro example physically reached
the independently checked target, then failed reporting. Its 0/72 full-task score
does not mean zero task understanding. Granite invoked no tools in the main
schedule, often writing descriptions/JSON for actions it did not execute.

Four separately labeled **post-hoc, non-robot tool-binding probes** were run
(one/model, 64 output tokens maximum): Qwen, Llama and Ministral produced the
requested native call; Granite produced JSON text, with no native call. This
supports different failure diagnoses, not universal capability conclusions.
No returned diagnostic tool was executed. The original main scores were not
changed, and no model-specific repair or prompt tuning occurred.

**Verification and resources:** 20 deterministic controls passed; **320 live
local/exact persisted Phoenix audits** passed, with **12,506 persisted live
spans**. The copied main archive passed CRC and **3,233 file hashes**, including
**69 frozen source/config hashes**. Diagnostic audit: four successful persisted
checks, eight spans, zero native actions. Main model requests **1,008**; separate
probes **4**, combined **1,012**. Main usage is complete and infrastructure
reserve use is zero. Eight human-pending ambiguity attempts per model are not
silently classified as passes or wrong model decisions.

The models are Q4_K_M on the same lab **RTX 4080 SUPER, 16,376 MiB VRAM** and
about 123 GiB RAM. Qwen's digest matches original M4; the lab status reported its
loaded model fully in VRAM with 8K context. Conditions keep the same requested
8K context, 1024 output tokens/call, 2048 observed output tokens/task, temp0,
seed42, non-thinking policy, and existing tool/operation/correction/movement
limits. Each model had a 643-request, eight-hour ceiling. Native templates and
tokenizers differ. Qwen had 12 length stops; absence of an outer exception does
not mean the agent returned no controlled-error text.

The canonical remote folder is **`/media/naeem/d1/marvel proj/`**, with both
`member/martin` clones, models, runtime, source snapshot and results. Research
commit `b13df0f03677754f42383dee95424cded862b117`; evaluation commit
`ec42ee72f53d95004c51b803c1a5d41f58e08d1c`, synchronized through a verified Git
bundle without a GitHub push. The 62-file original M4 source snapshot is
unchanged. Jazzy/Gazebo and locked dependencies run in an owned Ubuntu 24.04
container on the Ubuntu 25.04 lab host, using project-local Ollama 0.40.6.
Retained failed setup preflights are documented; zero scored model calls
preceded the successful controls. No existing shared project was rewritten.

**Decision:** retain Qwen as reference and consider Ministral as an additional
fast candidate; no automatic default replacement is claimed. A clearer common
reporting contract and Granite compatibility investigation are prospective
options, not implemented fixes. Existing M1-M5/M4 results remain unchanged;
**G1 is still blocked before its final freeze**. This separate authorization
neither clears G1's scorer/observability/human-review gates nor starts G1 held-out,
JTVR, memory or physical-robot work. Historical Sol is context only; it was not
rerun on the lab, and old/new denominators and hardware must not be conflated.

The [detailed report](artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md)
contains outcomes, paired/matched-success costs, family results, failure
mechanisms, token/timing statistics, source identities and deployment details.
The [main raw evidence ZIP](artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip)
and [post-hoc diagnostic addendum](artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_TOOL_PROBE_ADDENDUM_2026-11-17.zip)
are separately preserved and checksummed. The full sharing bundle adds these
reports and this updated master as context; it does not embed every older
artifact linked elsewhere in the master.

**Presentation update:** the original three-slide briefing below describes M4
and the earlier G1 checkpoint. The separate lab results above are the latest
additional evidence for the November 18 presentation. Keep M4's 80-total table
and the lab's 320-total/36-known-goal-per-condition table clearly separate; do
not combine them into one success rate. Teammate-provided results stay credited
to Levinson and are not part of this lab dataset.

**Presentation handoff:** the self-contained [three-slide briefing](#presentation-briefing)
below is prepared for **2026-11-18**. It contains slide text, speaker notes,
exact result denominators, attribution and current next steps. A presentation
writer receiving only this Markdown can use it without inventing facts from
unavailable linked files. Detailed raw-evidence inspection still requires those files.

**Attribution:** the `rosa-contexts` repository and Levinson's published research
context were provided by **Martin's teammate, Levinson (`Lelevinson`)**. Martin
passed the link to Codex for review; he did not author that teammate snapshot.
The bounded-macro implementation and experiments described as our work below
are Martin's project track. Levinson's fixed-loop/Forge/add-on results remain
separately attributed teammate-reported evidence, not Martin's experiment results.

**Sharing checkpoint:** reconciled with the team-context review closed November 17,
G1 Stage 2 completion and the separate
Stage 3 scorer review completed on 2026-11-15. **G1 is blocked before its final
freeze; held-out live evaluation has not started.** M4 remains the completed 2026-10-27 study, with later retrospective analysis and owner feedback dated
2026-10-29–30. M1–M5 technical delivery is complete locally. M6 and the optional
first-turn wording probe have not started and are not authorized.

**Current work: exploratory study G1, revision 1 — AI-authored cases.**
Stage 1 completed 132 scripted controls. Stage 2 completed 36 hosted Sol dev
attempts: 35 preliminary correct completions and one retained provider-stream
interruption. These are development results with four clarification transcripts
still awaiting uninvolved human review, not held-out confirmation. Stage 3's
separate GPT-6 Astra review found six reachable clarification-scoring errors
in newly constructed tests, so the scorer-review gate is not cleared. The owner
declined a protected OAuth metadata hook; the full observability requirement
remains unmet. See [current status and next gates](#2-current-verified-status)
and [the detailed Stage 3 checkpoint](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-15.md).
No independent case authorship, Qwen G1 live results or generalization benefit
is established. Prior M1–M5, serving probes and sealed G1 evidence remain retained.

**Team-context review closed 2026-11-17:** all three `rosa-contexts` branch tips
were inventoried at their November 16 snapshot: 100 unique files downloaded and
Git-hash checked, including 91 manifest-verified research files. Detailed review
covered the shared helper and current research reports; older material received
section/decision review rather than an exhaustive paragraph audit. The repo is
for coordination and contains neither the research runtime nor raw traces. Its
findings do not clear our Stage 3 gates or authorize integration/publication.
Read the [review and compatibility assessment](docs/team-context-review-20261116/ROSA_CONTEXTS_REVIEW_2026-11-16.md).


### A.2 Earlier top-of-file summaries (2026-10-27 to 2026-11-13)


**Completed separate work: Claude's Qwen timing/serving roadmap.** The
[living roadmap tracker](docs/CLAUDE_QWEN_ROADMAP_LIVE.md) records current progress,
gates, costs and next steps; the
[2026-11-12 report](docs/QWEN_TIMING_PHASE0_REPORT_2026-11-12.md) is the shareable
dated checkpoint. All 40 M4 Qwen trials and 144 calls were analyzed without
rescoring them. Two new hardware-probe requests were charged: one returned with
an accidental FA-disabled serving mismatch, and one owner-approved correction
was stopped for unresolved GPU activity. The corrected partial log confirms
effective FA enabled, f16 cache, 8192 context and 17/33 layer offload, but a clean
completed live baseline was not obtained in Phase 0. Both Phase 0 allowances are
spent. The subsequently authorized Phase 1 comparison is described below.
These exploratory observations do not establish a speed or correctness gain;
M1-M5 findings and frozen artifacts are unchanged.

**Phase 1 completed 2026-11-13: no serving candidate retained.** The owner
authorized the [frozen screen](artifacts/qwen-serving-phase1-20261112/PROTOCOL.md)
on2026-11-12. A (effective FA enabled, f16 KV, 8192 context) reached a median
**8.388 generation tokens/s** over eleven unique inputs. B (explicit FA enabled,
q8_0 KV, same context/weights/settings) reached **8.082**, or **0.963 times A**,
below the 1.5-times gate. B matched A's family calls on **7/10** inputs, below the
9/10 gate; the longest-input safety call also differed. Both completed fourteen
measured requests with expected prompt counts, adequate output room, no output
cap hits and 3/3 stable repeats. GPU KV shrank **128 to 68 MiB**, but both
offloaded **17/33 layers**. C was skipped by the gates; D remains unscheduled.

Measured blocks generated A **2212** versus B **3134** output tokens and took
**278.528** versus **396.829** summed client request seconds. These are serving
replay costs, not robotic task times or new correctness scores. Known-input call
agreement cannot establish goal satisfaction or general Qwen/Sol parity.

Actual cost was **31 returned requests, 52447 input / 6384 output tokens**, within
the unchanged 45-request ceiling, with no unreturned requests, hosted calls or
robot dispatches. The original schedule was 30 A/B requests. After A and B's
original warm-up, an overly literal log validator incorrectly stopped B despite
effective FA/q8_0. A separately frozen observer correction added one discarded
recovery warm-up before only unstarted measurements. All earlier outputs and
the failed checkpoint were preserved. This interruption, fixed profile order,
single profile blocks and known cases limit causal/general claims. Earlier GPU
preflight failures and the pre-inference desktop-classification amendment also
remain documented. No new allowance was silently created; a full C block would
not fit the remaining budget even if B had passed.

All test servers stopped. Closeout checks passed for 950 protected M4 files,
62 frozen sources, 93 Phase 0 files, all Phase 1/continuation freezes, identical
paired API requests and exact resource accounting. Keep A as the serving
reference; no new correctness experiment is scheduled. Share the
[dated results](docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md) and
[full results/deviations](artifacts/qwen-serving-phase1-20261112/COMPLETED_REPORT.md).
The [living tracker](docs/CLAUDE_QWEN_ROADMAP_LIVE.md) records gates and next
decisions. Evidence remains local; no publication or Git push was performed.

The [thinking-mode clarification](docs/QWEN_THINKING_CONFIGURATION_NOTE_2026-11-05.md)
confirms that the Qwen adapter requested `think=false`. This was an inherited
fixed serving profile, not an experimentally established optimum. No thinking
on/off comparison has been run; results apply to the tested non-thinking profile,
not Qwen's best achievable capability or matched reasoning compute versus Sol.

**Latest goal clarification2026-11-05:** the user wants local Qwen performance
close to Sol. The [proposal assessment](docs/QWEN_NEAR_SOL_PROPOSAL_ASSESSMENT_2026-11-05.md)
frames a possible bounded task-correctness comparison, with costs reported
separately. Intent-first instructions/schema, examples and thinking mode are
untested candidates, not adopted improvements. The target, held-out cases and
resource limits are not frozen. No new prompt/intent/examples/thinking condition
or full-loop correctness trial has started. The later timing-only observations
are tracked separately above.
In M4, Qwen macro input averaged 1,996 tokens per call (maximum 3,928), not 5K in
one prompt; the roughly 5K figure sums inputs across calls per task. M4 had no
task timeouts. These distinctions matter for evaluating the proposed diagnostics.


## Appendix B — Presentation briefing for 2026-11-18 (SUPERSEDED)

> **Superseded 2026-11-21.** Prepared on 2026-11-17, before the G1 Sol, Qwen and three-model
> closeouts, the freeze and F1. Its figures and "next steps" are out of date: use
> [Results at a glance](#results-at-a-glance-all-studies) and the
> [Claims ledger](#claims-ledger-what-the-report-may-and-may-not-say). Kept unchanged for the record.

<a id="presentation-briefing"></a>

<a id="presentation-briefing"></a>

## Three-slide presentation briefing — 2026-11-18

Use exactly three slides. Speaker notes, attribution and limitations below are
supporting material, not extra slides. The same text is available as a
[standalone briefing](docs/presentation-handoff-20261117/PRESENTATION_BRIEF_2026-11-18.md).

<!-- PRESENTATION_BRIEF_START -->
## Presentation briefing — three slides for 2026-11-18

Prepared **2026-11-17** from the retained evidence described in this master.
Scope: Martin's Improved ROSA project track. The following is suggested slide
wording and supporting notes, not a new research protocol or launch authorization.
Use the short slide text on screen; keep qualifications and extra figures in
speaker notes. Historical M1–M5 delivery, G1 stages and Qwen serving phases are
different numbering systems and must not be combined into one completion count.

### Slide 1 — Project introduction and goal

**Title:** Improving ROSA's robotic task execution

**Suggested slide text:**

- Improve how ROSA uses existing LLMs to execute and verify robot tasks.
- Let the LLM choose a permitted skill; let bounded Python routines handle its predictable execution steps.
- Evaluate correctness and overhead with local Qwen3.5 9B and hosted Sol.

**Speaker notes:** ROSA is an existing LLM-based robotic agent framework. We
improve its surrounding software rather than train a model. A bounded macro
is a registered routine: read prerequisites, make at most one permitted movement
when needed, then check fresh state. A separate read-only routine checks arm
readiness. This implements the project's divide-and-conquer idea through
pre-authored skills. Program logic manages routine substeps; the model still
interprets the request, selects the skill and handles unresolved intent.
It is not a general planner that automatically decomposes every new task.

Our research question is whether this arrangement reduces unnecessary model
interactions and execution overhead while preserving verified task completion.
Helping the tested smaller local model is an interest, not an achieved parity
claim. The intended deliverable is a reusable ROSA component, reproducible
evaluation and a working simulation demonstration. JTVR and verified episodic
memory are optional deferred directions, not required current deliverables.

### Slide 2 — Progress and measured results

**Title:** Working prototype; lower overhead, mixed correctness

**Suggested slide text:**

- Reusable macro module demonstrated on a Gazebo UR5e: named-pose movement and read-only readiness inspection.
- Completed M4: **80 Gazebo trials**, comparing model-managed primitives with macros inside the same repaired ROSA framework.

| Backend | Correct tasks: primitives → macro | Model calls | Mean task time |
|---|---:|---:|---:|
| Hosted Sol | 20/20 → 20/20 | 68 → 38 | 16.42 → 9.73 s |
| Local Qwen3.5 9B | 15/20 → 14/20 | 91 → 53 | 133.49 → 85.18 s |

**Takeaway:** Macros reduced model-call overhead; a general reliability improvement is not established.

**Speaker notes:** The 80 trials are ten task families × two repetitions ×
two conditions × two backends. Every table condition contains 20 trials.
Correctness includes appropriate FAILURE, UNKNOWN or clarification when required;
these are not 80 successful movements. Model-call and mean-time figures include
unsuccessful attempts. Task-loop times exclude the full campaign's setup,
reset and subsequent trace-audit work. Hardware and serving differ by backend,
so these times are observed system performance, not intrinsic model-speed rankings.

Sol used **44.1% fewer calls** and **40.7% less task time**, with unchanged
observed correctness. Qwen used **41.8% fewer calls** and **36.2% less task
time**, while correct tasks fell from 15 to 14. The preset engineering retention
screen passed for Sol and failed for Qwen. These small samples establish neither
statistical equivalence nor a general reliability advantage. Native operations
were Sol **38 → 40** and Qwen **50 → 48**; fewer model calls did not consistently
mean less robot work.

All 80 M4 live trace audits matched 3,290 persisted Phoenix spans. M1–M5 also
delivered the package/install guide, report, claim ledger and simulation video.
The comparison is against primitives with the same shared repairs, not untouched
upstream ROSA. A verified selected skill can still fail the user's actual goal:
wrong skill selection and ambiguous requests remain material limitations.

**Latest progress beyond M4:** exploratory G1 extends the engineering fixtures
to arm/base mock domains and different inspection acquisition depths. Its 36
hosted Sol development attempts finished with **35 preliminary correct outcomes
and one preserved provider-stream interruption**. The failed trial was not rerun.
Among 17 pairs with both arms scored correct, calls were 59 → 32 and native
attempts 40 → 40. These are dev-only selected pairs, not confirmed generalization.
Four clarification transcripts still need uninvolved human review. G1 Qwen live
and held-out model evaluation have not started.

Current Stage 3 engineering controls passed, but a separate GPT-6 Astra scorer
review found **six reachable clarification-classification errors in 41 new
adversarial tests**. These are new constructed counterexamples, not six live
Qwen/Sol failures. The scoring gate is not cleared. Full error-observability
requirements also remain unresolved under the owner's source-unchanged decision.
The experiment is paused before its final freeze, not running a held-out study.
This is the latest evaluation limitation to mention if asked about current work.

### Slide 3 — Future plan

**Title:** Validate the evaluation, then test broader use

**Suggested slide text:**

1. Resolve clarification scoring, obtain independent human review and settle error-observability requirements.
2. After validation and approval, freeze and run the planned held-out comparisons with matched budgets.
3. Consolidate the reusable macro, simulation demo and evidence; retain improvements only where their benefits justify their costs and limitations.

**Speaker notes:** First agree a documented disposition for the substantive
scorer finding. Any separately approved scorer amendment must receive renewed
review; previous scores and failed attempts remain preserved. Obtain actual
uninvolved human ratings for the four G1 clarification transcripts. Decide how
the full metadata requirement is satisfied or explicitly revised while honoring
the current decision to leave protected authentication source unchanged. Neither
a source change nor a methodological waiver is already approved.

Only after those gates pass can the study be frozen, authorization/storage/trace
preflight reviewed and a hosted held-out launch separately authorized. The current
design has 38 held-out-designated AI-authored cases, or 76 trials per backend
across two conditions. Qwen and catalogue-size work require their own later
gates, including reviewed GPU-idle conditions. This is planned work, not an
already launched or completed comparison. The AI-only authorship limitation must
remain visible; no independent case-generalization claim is available.

Keep the existing Gazebo capability and demonstration as completed engineering
assets. Any wider simulation transfer, runtime integration with a teammate or
physical hardware study is a conditional future proposal needing source/contract
checks and a matched protocol. Physical-robot deployment, general planning,
memory and a larger model are not automatic next steps or promised outcomes.
The practical objective remains a smaller, reproducible ROSA improvement with
honestly measured backend-specific trade-offs.

### Attribution and claim rules for the presentation writer

- **Martin's track:** bounded macros, shared ROSA repairs, UR5e movement/inspection,
  the M1–M5 deliverable, M4 comparison, serving diagnostic and G1 preparation/dev work.
- **Teammate-provided context:** Levinson supplied `Lelevinson/rosa-contexts`
  and its published member context. His fixed-loop C1, Forge and add-on studies
  are his track. Do not include 70/80, 55/80, 47/80, fresh 67/80 or his 320-episode
  build as Martin's measured progress. They may be mentioned with explicit teammate
  attribution if team coordination is relevant; they are not needed on these slides.
- **Evidence levels:** deterministic controls test engineering, live dev results
  test the development configuration, adversarial scorer tests expose evaluation
  defects, and neither AI review nor owner feedback substitutes for uninvolved
  human adjudication. G1 uses mock domains; M4 used Gazebo. Keep those environments separate.
- **Supported headline:** a reusable bounded macro reduced LLM orchestration
  overhead in the tested environment, with a favorable Sol result and mixed
  Qwen correctness. Do not claim general parity, novel tool-selection superiority,
  broad reliability gains, full JTVR/memory completion or physical-robot safety.
- **Status precedence:** this dated briefing and the current G1 gate section
  supersede older present-tense plans. The generated M4/M5 snapshot below is
  historical. Linked original reports retain their original dates and definitions.
- This one Markdown supplies the presentation narrative and numeric summaries;
  it does not embed every raw trace. If only the master is uploaded, do not claim
  to have independently opened its local links or reproduced the experiments.

**Presentation-ready summary:** We built and evaluated a bounded ROSA macro
module for robot movement and inspection. It reduced model-call overhead in
our Gazebo comparison, but correctness benefits were backend-dependent. We are
now addressing evaluation weaknesses before broader testing, while preserving
the existing results and keeping teammate research separately attributed.
<!-- PRESENTATION_BRIEF_END -->

## Appendix C — Historical section 2 checkpoints

> Moved here unchanged on 2026-11-21 from section 2. "Above" in these headings referred to their
> old position; the current entries are at the top of [section 2](#2-current-verified-status).

### Historical G1 checkpoint — 2026-11-16 (superseded by the 2026-11-20 entry above; retained unedited below)



**Stage 2 execution is complete; Stage 3 cannot freeze or launch.** The study uses
AI-authored cases under the owner's documented fallback, with no independent
teammate authorship or semantic-novelty review. The final design contains 18 dev
and 38 held-out-designated cases, in two domains and two execution conditions.
The 38 cases form 13 template groups, including six ladder groups. Engineering
fixture checks have exercised held-out-designated paths; no held-out model
outcomes have been produced. This is not a blind independently authored test set.

| Stage | Verified progress | Current interpretation |
|---|---|---|
| G1 Stage 0 / revision 1 | Narrowed arm/base design, observer separation and documented AI-only authorship amendment | Earlier 16-dev draft superseded by the 18-dev Stage 1 plan; earlier files preserved. |
| G1 Stage 1 | 132/132 scripted real-adapter controls; 9 observer/world tests; 132 local and 132 persisted audits; 5,544 matched spans | Engineering evidence, not live model competence. |
| G1 Stage 2 | All 36 Sol dev attempts accounted for: 35 preliminary correct, one infrastructure interruption; 94/291 charged requests | Ten unstarted cases completed in an authorized continuation; interrupted trial never rerun. Four clarification answers await uninvolved human adjudication. |
| G1 Stage 3 fresh controls | Another 132/132 controls, 9 observer/world tests and exact 5,544-span audit match | Both domains hosted with unchanged protected source; scripted execution only. |
| G1 Stage 3 scorer review | GPT-6 Astra authored 41 new adversarial cases; 29 expectations matched, 12 mismatches retained | Six reachable clarification errors are substantive; G-e clearance failed. This is separate AI review, not human clarification review. |
| G1 later stages | No held-out live run, Qwen live run or catalogue-size probe started | No launch authorization implied by preparation or this overview. |

**Stage 2 descriptive efficiency:** all attempts used 60 primitive versus 34 macro
inference requests, 194.91 versus 111.35 task seconds, and 40 versus 46 native
attempts. The primitive interruption had unknown token usage; its macro partner
completed six native acquisitions. On the 17 pairs with both conditions scored
correct, requests were **59 versus 32** (45.76% fewer), task time **192.49 versus
104.84 seconds** (45.53% less), and native operations **40 versus 40**. Matched
known input tokens were 90,425 versus 47,227; output 1,783 versus 1,051. These
selected dev pairs and interrupted timing segments do not establish causal speed
or reliability superiority. All 36 local and persisted audits matched 1,472 spans.
The historical automated scores are retained, not promoted to independently
validated semantic outcomes by these checks.

**Current Stage 3 gates:** G-a authorship fallback and G-b fresh controls pass.
On **2026-11-17**, the owner confirmed they can arrange an uninvolved person.
The [four-case blinded review ZIP](artifacts/macro-generalization-20261113/revision-1/stage-3/resolution-guide-20261117/G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip)
is ready. Actual ratings and a reviewer name are not yet supplied. A
[concrete scoring/observability amendment proposal](artifacts/macro-generalization-20261113/revision-1/stage-3/resolution-guide-20261117/DECISIONS_TO_APPROVE.md)
is prepared for owner decision; neither amendment is adopted. See the
[November 17 resolution checkpoint](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-17.md).

G-c is BLOCKED: the owner chose protected authentication source unchanged, and
the existing outer wrapper cannot capture all required HTTP error details.
G-d analysis checks pass, but ordered advancement waits. G-e is FAIL: the separate
review accepted five non-clarifying answers and rejected one valid clarification
in reachable answer-only tests. The other six mismatches comprise four forged
program-owned evidence bypasses, one unreachable extra-source hypothesis and
one documented reviewer expectation error; they are not six additional reachable
model failures. G-f is BLOCKED pending actual uninvolved human ratings of the
four G1 clarification transcripts. M4's eight transcripts are a different packet.
G-g freeze and G-h launch preflight therefore remain BLOCKED.

**Next actions require explicit disposition, not another run:** address the
substantive scorer finding and unmet instrumentation scope without silently
changing protected source or frozen criteria; obtain the required human review;
then complete valid gates, a new freeze and zero-inference restore-only preflight.
Any scorer amendment requires renewed review. No amendment or waiver is adopted
here. Provider quota and current grant validity are not established by a local
credential file. Stage 4 needs separate owner authorization after preflight.

The [November 15 Stage 3 status](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-15.md),
[Astra review](artifacts/macro-generalization-20261113/revision-1/stage-3/scorer-review/astra-review-20261115/REVIEW_REPORT.md)
and [Stage 2 results/problems](artifacts/macro-generalization-20261113/revision-1/STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md)
are the detailed records. Stage 2's older P1–P4/P2 decision wording predates the
owner-confirmed [P1′–P6 amendment](artifacts/macro-generalization-20261113/revision-1/stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md);
use that amendment for prospective rules, never retroactively edit the older report.
No prediction is adjudicated from dev or scripted results.

### Completed timing/serving screen — historical checkpoint

**Timing roadmap status (2026-11-13):** Phase 0 analysis and Phase 1 A/B serving
screen completed. A 8.388 vs B 8.082 generation tokens/s; B/A 0.963, family-call
agreement 7/10. B failed the fixed screen, C skipped, no new serving configuration
retained. Phase 1 charged31 requests including the declared recovery warm-up;
its servers stopped and preservation/accounting checks passed. Phase 0's separate
two charged attempts remain preserved. Use the
[dedicated living tracker](docs/CLAUDE_QWEN_ROADMAP_LIVE.md) and
[dated results](docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md) for current evidence,
limitations and next decisions. This serving screen launched no new full-loop
correctness study; the subsequently authorized G1 development study is separate.

The generated block below is the **M4/M5 delivery snapshot**, not a live status
monitor for G1 or the separate timing roadmap. `PROJECT_LIVE_STATUS.json` likewise
remains an M4/M5 saved snapshot, not G1 progress. Its saved refresh date remains visible.
That block is refreshed from existing files by
`python -m tools.project_context --refresh`. It makes no model calls, reads no
credential records and does not modify experimental inputs or trial results.
The figures are a snapshot, not a continuously refreshed dashboard. Refresh before
sharing this document or making a new claim about an active run.

### C.3 Retired generated M4/M5 status block (last refreshed 2026-11-05)

> Retired 2026-11-21 and moved here unchanged, apart from the renamed markers, which disable
> `tools.project_context --refresh`. Figures are the 2026-11-05 snapshot; use
> [Results at a glance](#results-at-a-glance-all-studies) instead.

> **Note 2026-11-21:** the generated block below is the **M4/M5 snapshot of 2026-11-05**. Its "Current
> milestone" and "Next actions" rows are historical. Current next actions are in the dated 2026-11-21
> entries at the top of this section and in §15.

<!-- PROJECT_STATUS_START: RETIRED 2026-11-21, do not refresh -->
Last refreshed: **2026-11-05 15:39:42**. Saved-checkpoint snapshot.
### Current work and next actions
| Progress item | Current evidence / action |
|---|---|
| Current milestone | M5: TECHNICAL_DELIVERY_COMPLETE_EVALUATION_LOCAL_BY_USER_CHOICE. M5 technical delivery complete. Post-closeout discussion assessed using exact existing traces and retrospective label scenarios; M6 remains proposed, not authorized. Local backups are verified through their pinned revisions; evaluation off-machine protection remains deferred and frozen-criterion independent human adjudication was not obtained. |
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
<!-- PROJECT_STATUS_END: RETIRED 2026-11-21 -->
