# G1 revision 1: Sol held-out execution report

Date: **2026-11-19**. **Execution complete; final conclusions pending human clarification review.**

The authorized Sol mock batch retained all **76 scheduled attempts**: 38 fixed
AI-authored cases in each of the primitive and bounded-macro conditions. It used
**200/611 physical model requests**, with **0/3 eligible infrastructure retries**.
No failed trial was replayed or replaced. Qwen and catalogue-size testing have
not started. This is separate from the earlier M4 Gazebo study and lab reruns.

## Correctness and observability

| Effective result | Primitives | Macro | Total |
|---|---:|---:|---:|
| PASS | 33 | 36 | 69 |
| Evaluable FAIL | 0 | 0 | 0 |
| Pending human clarification judgment | 2 | 2 | 4 |
| Infrastructure censored | 3 | 0 | 3 |
| Scheduled attempts retained | 38 | 38 | 76 |

Known-goal evaluable correctness is **33/33 primitives and 36/36 macro**.
These denominators exclude both infrastructure-censored attempts and ambiguous
requests awaiting human judgment. They do not establish 76 successful trials.
The raw legacy boolean remains diagnostic; it does not replace the approved
human-adjudicated clarification layer.

**76/76 local audits and 76/76 persisted Phoenix audits passed.** All **3,796**
frozen source/input hashes match. Continuations additionally reverified **245**
previously retained trial files. All four owned Phoenix services stopped;
authorization scopes were unchanged and credentials were cleared from memory.
The opted-in encrypted refresh credential remains available for future authorized
runs. No new consent, source tuning, Git commit/push or upload occurred.

## Calls, tokens, time and native work

All scheduled attempts, including censored work and pending clarification cases:

| Metric | Primitives | Macro |
|---|---:|---:|
| Physical model requests | 126 | 74 |
| Recorded input tokens | 190,448 | 112,005 |
| Recorded output tokens | 3,666 | 2,522 |
| Records with incomplete usage | 3 | 0 |
| Native operations | 112 | 108 |
| Summed task time | 504.38 s | 317.70 s |
| Mean task time over 38 attempts | 13.27 s | 8.36 s |
| Median task time | 12.42 s | 7.50 s |

The three censored primitive attempts have incomplete usage. Their missing
tokens are **not recorded**, not zero, and have not been estimated. Unequal
censoring makes this all-attempt table insufficient as the sole efficiency view.

The **33 matched successful pairs** exclude three pairs with a censored arm and
two clarification pairs awaiting review:

| Metric | Primitives | Macro | Observed reduction |
|---|---:|---:|---:|
| Model requests | 118 | 66 | 44.1% |
| Input tokens | 183,745 | 100,679 | 45.2% |
| Output tokens | 3,503 | 2,138 | 39.0% |
| Summed task time | 480.67 s | 271.66 s | 43.5% |
| Native operations | 111 | 103 | 7.2% |

This is a descriptive matched-success comparison, not a final prediction verdict
or a claim about total system throughput. Campaign elapsed time, including
setup and pauses, was **35.08 minutes**. Per-task times above exclude those
pauses. The maximum start-time gap between a case's conditions was **313.62 s**;
no pair exceeded the frozen 30-minute flag.

Inspection call savings were usually one call per pair. Extra authorized reads
in two primitive trials changed the mean saving and native-work ratio at those
depths. The [completion addendum](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/completion-20261119/COMPLETION_ADDENDUM.md)
retains per-domain/depth tables, excluded pairs and complete gap records. These
small cells do not establish guaranteed native-operation equality.

## Interruptions and recovery

| Attempt | Observed failure | Analysis class | Requests | Native operations |
|---|---|---|---:|---:|
| G1r1-heldout-018-primitives | In-stream error | INFRA_CENSORED_POST_ACTION | 3 | 1 |
| G1r1-heldout-019-primitives | In-stream error | INFRA_CENSORED_POST_ACTION | 2 | 0 |
| G1r1-heldout-034-primitives | In-stream error | INFRA_CENSORED_PRE_OUTPUT | 1 | 0 |

These were generic stream events, not recorded HTTP error statuses. The
original provider code/type and underlying cause are **not recorded**. They
are not diagnosed as quota exhaustion or wrong model decisions. Post-action
includes tool execution; zero native operations alone does not mean no activity.

Each affected attempt was preserved. Three operational continuations verified
integrity, restored the already authorized grant and processed only unstarted
cells with the exact frozen trial function, model and inputs. Cumulative requests,
retry reserve and the original eight-hour origin were carried forward; no
budget/window reset or uncertain command replay occurred. Three censored trials
are below the frozen eight-trial operational-compromise threshold.

## Limits and next gate

The results are encouraging for reducing Sol orchestration overhead on this
fixed catalogue. They do not yet justify a final whole-study correctness or
prediction verdict. They do not show Qwen improvement, broad generalization,
superiority to stock ROSA, or physical-robot readiness. All cases are AI-authored;
the documented condition-wording confound and small template-group/depth samples
remain. Earlier results and negative findings remain unchanged.

An eligible uninvolved human must score the **four new held-out clarification
responses**. The older four development ratings cannot be reused. Send only the
[blinded review ZIP](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/heldout-human-review/G1_NEW_HELDOUT_HUMAN_REVIEW_2026-11-19.zip),
which includes instructions, the unchanged rubric, four transcripts, a blank
ratings CSV and an honest eligibility declaration. The private mapping is
excluded. No human ratings have been generated by the assistant.

After actual submission intake and content binding, the unchanged frozen
analysis can compute final V1 operational, V2 evaluable and V3 censor-as-failure
views, paired/group-bootstrap uncertainty and prediction statuses. Its current
[verdict record](artifacts/macro-generalization-20261113/revision-1/stage-4/analysis/verdict.json)
correctly remains **WITHHELD**. This report does not launch another stage.

## Evidence

- [Full actual-attempt report and all 76 effective rows](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/reports/20261119T073847Z/G1_SOL_ACTUAL_ATTEMPT_REPORT.md).
- [Machine-readable effective outcomes and costs](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/reports/20261119T073847Z/analysis.json).
- [Completion integrity, cleanup, interruption and gap checks](artifacts/macro-generalization-20261113/revision-1/stage-4/operator/completion-20261119/COMPLETION_CHECKS.json).
- [Final cumulative checkpoint](artifacts/macro-generalization-20261113/revision-1/stage-4/status.json).
- [Frozen inventory](artifacts/macro-generalization-20261113/revision-1/stage-4/freeze.json), SHA-256 `8e89f7688d9da342a6b519ba16ae00130a553afd418b403fdebca314268504ac`.
