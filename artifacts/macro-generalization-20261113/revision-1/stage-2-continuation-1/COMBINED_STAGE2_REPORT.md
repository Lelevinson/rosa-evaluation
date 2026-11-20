# G1 Stage 2 combined continuation report

Date: **2026-11-14**.

Finalized attempts: **36/36** (26 original + 10 continuation). Correct completed trials: **35**. Unstarted trials: **0**.

The original provider-interrupted trial remains recorded as failed/censored execution. It was not rerun or replaced, and it does not establish a wrong Sol decision. This is AI-authored exploratory dev, without independent teammate authorship or semantic-novelty review. P1-P4 are not adjudicated.

Cumulative inference attempts: **94/291**, including **66 original + 28 new**. No new case/scorer amendment cycle was used.

| Condition, all attempts | Correct | Physical calls | Known input / output tokens | Native attempts | Mean / median task seconds |
|---|---:|---:|---:|---:|---:|
| primitives | 17/18 | 60 | 90425 / 1783 | 40 | 10.83 / 9.88 |
| macro | 18/18 | 34 | 50552 / 1108 | 46 | 6.19 / 6.09 |

Matched-primary-success subset: **17 paired cases**. Full cost views are in [combined-analysis.json](combined-analysis.json). Failed-call usage is unknown, not zero; known token sums are incomplete for those calls. Do not interpret the provider interruption as an architectural reliability advantage. Task timings are monotonic and exclude subsequent server-side audit work; cross-segment timing/state differences limit causal interpretation.

| Condition, matched-success pairs | Calls | Input / output tokens | Native attempts | Mean / median task seconds |
|---|---:|---:|---:|---:|
| primitives | 59 | 90425 / 1783 | 40 | 11.32 / 9.96 |
| macro | 32 | 47227 / 1051 | 40 | 6.17 / 6.07 |

In this descriptive matched subset, macros used **45.76% fewer calls** and **45.53% less measured task time**, with equal native attempts. These dev observations do not establish a held-out efficiency or reliability result. The all-attempt view has 40 versus 46 native attempts because the interrupted primitive trial performed none of the six acquisitions completed by its macro counterpart.

Local audits passed: **36/36**. Persisted audits passed: **36/36**, with **1472** matched spans.

All 35 correct completions matched their scripted turn comparators; the sole count deviation was the interrupted call. There were no invalid attempts, dispatch violations, unsupported accepted SUCCESS reports, wrong-goal accepted SUCCESS reports, output-length endings or budget endings. All eight injected-fault trials exercised their fault. Four clarification transcripts still require independent semantic review. See [detailed execution checks](DETAILED_STAGE2_CHECKS.md) and [machine-readable diagnostics](detailed-checks.json).

The native ratio was 1.00 in all seven fully measured domain/depth cells, inside the predefined 0.75-1.25 band. Base depth 6 remains undefined because its primitive attempt was interrupted; it must not be counted as a completed native-cost comparison.

The original eight-hour wall-clock window had expired before this continuation. A separate explicit owner approval was required for the bounded new 30-minute window; the old request count and cumulative active-execution allowance were carried forward. The original deadline was not silently reset. See [the continuation plan](CONTINUATION_PLAN_2026-11-14.md) and window-approval.json. Fresh restore-only authorization was reviewed and rechecked at launch. Provider quota remained unknown. No new OAuth consent or scope expansion was permitted.

The continuation ran from **08:46:49 to 08:50:11 UTC on 2026-11-14**, including its final input-integrity check. It made 28 new requests, used no infrastructure-reserve retries, and stayed within its new 30-minute window. The earlier segment used 66 requests. Cleanup cleared in-memory credentials and retained only the existing protected remembered credential; the owned Phoenix process stopped normally. The original sanitized error was `SafeError(code=error)` without a retained provider status or raw payload. Its underlying cause and failed-call usage remain unknown; there is no basis to label it a quota failure or Sol decision error.

The owner's [standing recovery instruction](STANDING_INTERRUPTION_POLICY_2026-11-14.md) now authorizes evidence-preserving continuation after external interruptions without repeatedly requesting confirmation. Frozen conditions, cumulative hard limits and manual new-consent requirements still apply.

| Trial | Primary correct | Calls | Native attempts | Error |
|---|---:|---:|---:|---|
| G1r1-dev-001-macro | True | 2 | 1 |  |
| G1r1-dev-001-primitives | True | 3 | 1 |  |
| G1r1-dev-002-macro | True | 2 | 2 |  |
| G1r1-dev-002-primitives | True | 3 | 2 |  |
| G1r1-dev-003-macro | True | 2 | 4 |  |
| G1r1-dev-003-primitives | True | 3 | 4 |  |
| G1r1-dev-004-macro | True | 2 | 6 |  |
| G1r1-dev-004-primitives | True | 3 | 6 |  |
| G1r1-dev-005-macro | True | 2 | 3 |  |
| G1r1-dev-005-primitives | True | 5 | 3 |  |
| G1r1-dev-006-macro | True | 2 | 3 |  |
| G1r1-dev-006-primitives | True | 5 | 3 |  |
| G1r1-dev-007-macro | True | 2 | 1 |  |
| G1r1-dev-007-primitives | True | 3 | 1 |  |
| G1r1-dev-008-macro | True | 1 | 0 |  |
| G1r1-dev-008-primitives | True | 1 | 0 |  |
| G1r1-dev-009-macro | True | 2 | 1 |  |
| G1r1-dev-009-primitives | True | 3 | 1 |  |
| G1r1-dev-010-macro | True | 2 | 2 |  |
| G1r1-dev-010-primitives | True | 3 | 2 |  |
| G1r1-dev-011-macro | True | 2 | 4 |  |
| G1r1-dev-011-primitives | True | 3 | 4 |  |
| G1r1-dev-012-macro | True | 2 | 6 |  |
| G1r1-dev-012-primitives | False | 1 | 0 | error |
| G1r1-dev-partial-arm-macro | True | 2 | 3 |  |
| G1r1-dev-partial-arm-primitives | True | 5 | 3 |  |
| G1r1-dev-013-macro | True | 2 | 3 |  |
| G1r1-dev-013-primitives | True | 5 | 3 |  |
| G1r1-dev-014-macro | True | 2 | 3 |  |
| G1r1-dev-014-primitives | True | 5 | 3 |  |
| G1r1-dev-015-macro | True | 2 | 1 |  |
| G1r1-dev-015-primitives | True | 3 | 1 |  |
| G1r1-dev-016-macro | True | 1 | 0 |  |
| G1r1-dev-016-primitives | True | 1 | 0 |  |
| G1r1-dev-partial-base-macro | True | 2 | 3 |  |
| G1r1-dev-partial-base-primitives | True | 5 | 3 |  |

The frozen original request, condition wording, public tools, limits, scorer and native-operation accounting rules were retained. The original condition-wording confound remains. Clarification results still require semantic human review; an automated question screen is not independent adjudication. The original Base depth-6 primitive interruption leaves that native-cost pair incomplete; do not invent its missing acquisitions.

No later stage or Qwen run was launched. No Git commit, push or upload was performed. The original reports/manifests remain unchanged; this combined report is a separate artifact.

For the full unchanged thresholds, exact Base units/tolerance suffix, task limits, later-stage caps and scope restrictions, read [the original confirmation](../stage-2/CONFIRMATION_2026-11-14.md). The [original report](../stage-2/STAGE2_REPORT.md) remains a sealed record of the interrupted segment. This combined report supplies its completion update. Stage 2 execution and reporting are complete with the original censored attempt retained; P1-P4 remain unadjudicated.
