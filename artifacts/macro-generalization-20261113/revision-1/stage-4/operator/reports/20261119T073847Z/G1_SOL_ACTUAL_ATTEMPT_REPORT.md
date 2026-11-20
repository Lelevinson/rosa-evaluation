# G1 Sol held-out actual-attempt report

Date: **2026-11-19**. **Provisional; pending human review and/or unstarted trials.**

Retained **76/76** scheduled trials; **200/611** charged requests. No task was replayed or replaced.
Effective states: {"PASS": 69, "FAIL": 0, "PENDING_HUMAN_REVIEW": 4, "INFRA_CENSORED_PRE_OUTPUT": 1, "INFRA_CENSORED_POST_ACTION": 2}. Unstarted: **0**.

Local audits **76/76**; persisted Phoenix audits **76/76**. Frozen source mismatches: **0**.

| Metric | Primitives | Macro |
|---|---:|---:|
| Retained / scheduled | 38 | 38 |
| Known-goal evaluable correct | 33 | 36 |
| Known-goal evaluable denominator | 33 | 36 |
| Pending semantic judgments | 2 | 2 |
| Infrastructure censored | 3 | 0 |
| Physical model calls | 126 | 74 |
| Known input tokens | 190448 | 112005 |
| Known output tokens | 3666 | 2522 |
| Incomplete-usage records | 3 | 0 |
| Native operations | 112 | 108 |
| Task seconds, sum | 504.378 | 317.701 |
| Task seconds, mean | 13.273 | 8.361 |
| Task seconds, median | 12.423 | 7.496 |

Matched-success pairs: **33**. Costs: `{"primitives": {"calls": 118, "native_operations": 111, "task_seconds": 480.66572964399967}, "macro": {"calls": 66, "native_operations": 103, "task_seconds": 271.6641485240003}}`.

All-attempt costs include failed/censored work. Partial or unbalanced arms are not a fair complete-arm efficiency comparison. Unknown usage is not estimated. Task latency excludes interruption pauses and campaign setup; the cumulative deadline includes pauses. Call count alone is not whole-system efficiency.

Original in-stream errors have no recorded original provider code/type. Their cause is unknown. They are not called quota exhaustion or model selection failures. Their affected pairs are excluded from matched-success costs; sensitivity counting censored attempts as failures remains required in final analysis.

All cases are AI-authored. This is the original fixed G1 catalogue and condition wording; no independence/generalization or original-ROSA superiority claim is made. Qwen/catalogue stages are unstarted. New ambiguous outcomes require their own blinded human review; old dev ratings are not reused.

If the frozen eight-censored threshold is reached, this backend is operationally compromised and prediction conclusions are Uninformative. Remaining unstarted outcomes are unknown. Full final conclusions remain withheld while required human judgments are absent.

| Trial | Mode | Domain | Kind | Effective status | Calls | Native |
|---|---|---|---|---|---:|---:|
| G1r1-heldout-017-macro | macro | arm | ladder | PASS | 2 | 1 |
| G1r1-heldout-017-primitives | primitives | arm | ladder | PASS | 3 | 1 |
| G1r1-heldout-018-macro | macro | arm | ladder | PASS | 2 | 1 |
| G1r1-heldout-018-primitives | primitives | arm | ladder | INFRA_CENSORED_POST_ACTION | 3 | 1 |
| G1r1-heldout-019-macro | macro | arm | ladder | PASS | 2 | 1 |
| G1r1-heldout-019-primitives | primitives | arm | ladder | INFRA_CENSORED_POST_ACTION | 2 | 0 |
| G1r1-heldout-020-macro | macro | arm | ladder | PASS | 2 | 2 |
| G1r1-heldout-020-primitives | primitives | arm | ladder | PASS | 3 | 2 |
| G1r1-heldout-021-macro | macro | arm | ladder | PASS | 2 | 2 |
| G1r1-heldout-021-primitives | primitives | arm | ladder | PASS | 3 | 2 |
| G1r1-heldout-022-macro | macro | arm | ladder | PASS | 2 | 2 |
| G1r1-heldout-022-primitives | primitives | arm | ladder | PASS | 4 | 4 |
| G1r1-heldout-023-macro | macro | arm | ladder | PASS | 2 | 4 |
| G1r1-heldout-023-primitives | primitives | arm | ladder | PASS | 3 | 4 |
| G1r1-heldout-024-macro | macro | arm | ladder | PASS | 2 | 4 |
| G1r1-heldout-024-primitives | primitives | arm | ladder | PASS | 3 | 4 |
| G1r1-heldout-025-macro | macro | arm | ladder | PASS | 2 | 4 |
| G1r1-heldout-025-primitives | primitives | arm | ladder | PASS | 3 | 4 |
| G1r1-heldout-026-macro | macro | arm | ladder | PASS | 2 | 6 |
| G1r1-heldout-026-primitives | primitives | arm | ladder | PASS | 3 | 6 |
| G1r1-heldout-027-macro | macro | arm | ladder | PASS | 2 | 6 |
| G1r1-heldout-027-primitives | primitives | arm | ladder | PASS | 3 | 6 |
| G1r1-heldout-028-macro | macro | arm | ladder | PASS | 2 | 6 |
| G1r1-heldout-028-primitives | primitives | arm | ladder | PASS | 3 | 6 |
| G1r1-heldout-029-macro | macro | arm | write | PASS | 2 | 3 |
| G1r1-heldout-029-primitives | primitives | arm | write | PASS | 5 | 3 |
| G1r1-heldout-030-macro | macro | arm | write | PASS | 2 | 3 |
| G1r1-heldout-030-primitives | primitives | arm | write | PASS | 6 | 3 |
| G1r1-heldout-031-macro | macro | arm | write | PASS | 2 | 3 |
| G1r1-heldout-031-primitives | primitives | arm | write | PASS | 5 | 3 |
| G1r1-heldout-032-macro | macro | arm | missing_prerequisite | PASS | 2 | 1 |
| G1r1-heldout-032-primitives | primitives | arm | missing_prerequisite | PASS | 4 | 2 |
| G1r1-heldout-033-macro | macro | arm | ambiguous | PENDING_HUMAN_REVIEW | 1 | 0 |
| G1r1-heldout-033-primitives | primitives | arm | ambiguous | PENDING_HUMAN_REVIEW | 1 | 0 |
| G1r1-heldout-034-macro | macro | arm | write_fault | PASS | 2 | 3 |
| G1r1-heldout-034-primitives | primitives | arm | write_fault | INFRA_CENSORED_PRE_OUTPUT | 1 | 0 |
| G1r1-heldout-035-macro | macro | arm | unavailable_source | PASS | 2 | 2 |
| G1r1-heldout-035-primitives | primitives | arm | unavailable_source | PASS | 3 | 2 |
| G1r1-heldout-036-macro | macro | base | ladder | PASS | 2 | 1 |
| G1r1-heldout-036-primitives | primitives | base | ladder | PASS | 3 | 1 |
| G1r1-heldout-037-macro | macro | base | ladder | PASS | 2 | 1 |
| G1r1-heldout-037-primitives | primitives | base | ladder | PASS | 3 | 1 |
| G1r1-heldout-038-macro | macro | base | ladder | PASS | 2 | 1 |
| G1r1-heldout-038-primitives | primitives | base | ladder | PASS | 3 | 1 |
| G1r1-heldout-039-macro | macro | base | ladder | PASS | 2 | 2 |
| G1r1-heldout-039-primitives | primitives | base | ladder | PASS | 3 | 2 |
| G1r1-heldout-040-macro | macro | base | ladder | PASS | 2 | 2 |
| G1r1-heldout-040-primitives | primitives | base | ladder | PASS | 3 | 2 |
| G1r1-heldout-041-macro | macro | base | ladder | PASS | 2 | 2 |
| G1r1-heldout-041-primitives | primitives | base | ladder | PASS | 3 | 2 |
| G1r1-heldout-042-macro | macro | base | ladder | PASS | 2 | 4 |
| G1r1-heldout-042-primitives | primitives | base | ladder | PASS | 3 | 4 |
| G1r1-heldout-043-macro | macro | base | ladder | PASS | 2 | 4 |
| G1r1-heldout-043-primitives | primitives | base | ladder | PASS | 3 | 4 |
| G1r1-heldout-044-macro | macro | base | ladder | PASS | 2 | 4 |
| G1r1-heldout-044-primitives | primitives | base | ladder | PASS | 4 | 8 |
| G1r1-heldout-045-macro | macro | base | ladder | PASS | 2 | 6 |
| G1r1-heldout-045-primitives | primitives | base | ladder | PASS | 3 | 6 |
| G1r1-heldout-046-macro | macro | base | ladder | PASS | 2 | 6 |
| G1r1-heldout-046-primitives | primitives | base | ladder | PASS | 3 | 6 |
| G1r1-heldout-047-macro | macro | base | ladder | PASS | 2 | 6 |
| G1r1-heldout-047-primitives | primitives | base | ladder | PASS | 3 | 6 |
| G1r1-heldout-048-macro | macro | base | write | PASS | 2 | 3 |
| G1r1-heldout-048-primitives | primitives | base | write | PASS | 5 | 3 |
| G1r1-heldout-049-macro | macro | base | write | PASS | 2 | 3 |
| G1r1-heldout-049-primitives | primitives | base | write | PASS | 5 | 3 |
| G1r1-heldout-050-macro | macro | base | write | PASS | 2 | 3 |
| G1r1-heldout-050-primitives | primitives | base | write | PASS | 5 | 3 |
| G1r1-heldout-051-macro | macro | base | missing_prerequisite | PASS | 2 | 1 |
| G1r1-heldout-051-primitives | primitives | base | missing_prerequisite | PASS | 4 | 2 |
| G1r1-heldout-052-macro | macro | base | ambiguous | PENDING_HUMAN_REVIEW | 1 | 0 |
| G1r1-heldout-052-primitives | primitives | base | ambiguous | PENDING_HUMAN_REVIEW | 1 | 0 |
| G1r1-heldout-053-macro | macro | base | write_fault | PASS | 2 | 3 |
| G1r1-heldout-053-primitives | primitives | base | write_fault | PASS | 5 | 3 |
| G1r1-heldout-054-macro | macro | base | unavailable_source | PASS | 2 | 2 |
| G1r1-heldout-054-primitives | primitives | base | unavailable_source | PASS | 3 | 2 |
