# G1 Sol completion and interruption addendum

Date: **2026-11-19**. Execution complete; final semantic adjudication remains pending.

All 76 unique scheduled trial identifiers are present. Their physical-request sum equals the cumulative checkpoint: 200/611. Eligible retry reserve used: 0/3. No failed/censored trial was replayed. Three continuations processed only unstarted cells under the original time origin.

Original campaign elapsed time including pauses/setup: **35.08 minutes**. This differs from summed per-task latency. Earlier retained trial files reverified: **245**. All 3,796 source/input digests match. All four owned Phoenix services stopped; credentials were cleared from memory, with the opted-in encrypted credential retained and scopes unchanged.

All three interruptions were generic in-stream error events, not recorded HTTP statuses. The provider code/type and underlying cause are not recorded. One attempt is pre-output censored and two are post-action censored. No uncertain action was replayed.

| Trial | Censoring class | Requests | Native operations |
|---|---|---:|---:|
| G1r1-heldout-018-primitives | INFRA_CENSORED_POST_ACTION | 3 | 1 |
| G1r1-heldout-019-primitives | INFRA_CENSORED_POST_ACTION | 2 | 0 |
| G1r1-heldout-034-primitives | INFRA_CENSORED_PRE_OUTPUT | 1 | 0 |

Descriptive inspection tables below use only pairs with both arms already adjudicated PASS. Each depth/domain has only three scheduled pairs; missing pairs are explicit. These are not final prediction verdicts, bootstrap results or independent generalization evidence.

| Domain | Native depth | Matched / scheduled pairs | Excluded | Mean calls saved | Macro/primitive native ratio |
|---|---:|---:|---:|---:|---:|
| arm | 1 | 1/3 | 2 | 1.000 | 1.000 |
| arm | 2 | 3/3 | 0 | 1.333 | 0.750 |
| arm | 4 | 3/3 | 0 | 1.000 | 1.000 |
| arm | 6 | 3/3 | 0 | 1.000 | 1.000 |
| base | 1 | 3/3 | 0 | 1.000 | 1.000 |
| base | 2 | 3/3 | 0 | 1.000 | 1.000 |
| base | 4 | 3/3 | 0 | 1.333 | 0.750 |
| base | 6 | 3/3 | 0 | 1.000 | 1.000 |

Paired start-time gaps above the frozen 30-minute flag: **0**. Maximum gap: **313.62 seconds**. Full gaps are retained in COMPLETION_CHECKS.json.

Native-operation differences include repeated authorized reads. They are charged, even when not incorrect. The small-sample pattern must not be described as guaranteed native-work equality or general reliability improvement.

Next gate: an eligible uninvolved human reviews the four new held-out clarification responses in the separately prepared blinded packet. Old development ratings are not reused. After actual submission intake and content binding, the unchanged frozen analysis can compute its V1/V2/V3, paired tables, group bootstrap and prediction statuses. No new Qwen/catalogue stage is launched here.
