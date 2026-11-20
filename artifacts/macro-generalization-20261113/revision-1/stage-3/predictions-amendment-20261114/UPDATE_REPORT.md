# Prediction-definition update and dev validation

Date: **2026-11-14**.

The owner supplied P1-prime through P6 and confirmed the domain and P4-boundary interpretations. The missing-definition blocker is resolved. This is a prospective analysis amendment for future held-out data, validated retrospectively on Stage 2. No model requests were made and no new performance claim is adjudicated.

The old Stage 3 checkpoint remains unchanged: all **62 inventory files** verified. **20 prediction/analysis tests passed**. All **10000 whole-template bootstrap draws**, seed 20261113, are retained; empty draw counts were checked directly against the draw file.

## Primary V2 diagnostic depth table

| Domain | Depth | Matched-success pairs | Calls saved per pair | Native ratio | Censored pair exclusions |
|---|---:|---:|---:|---:|---:|
| arm | 1 | 1 | 1.00 | 1.00 | 0 |
| arm | 2 | 1 | 1.00 | 1.00 | 0 |
| arm | 4 | 1 | 1.00 | 1.00 | 0 |
| arm | 6 | 1 | 1.00 | 1.00 | 0 |
| base | 1 | 1 | 1.00 | 1.00 | 0 |
| base | 2 | 1 | 1.00 | 1.00 | 0 |
| base | 4 | 1 | 1.00 | 1.00 | 0 |
| base | 6 | 0 | not evaluable | not evaluable | 1 |

All fully measured dev cells show one call saved per successful inspection pair and a native ratio of 1.00. The interrupted Base depth-6 primitive attempt leaves that required domain/depth cell unevaluable. Pooled values cannot fill that gap under the confirmed per-domain rules. This is a missing-data check, not a held-out Support/Against finding.

P6 remains descriptive. In evaluable Stage 2 rows, primitive ladder inspections averaged 3 calls; healthy writes and partial writes each averaged 5; missing-prerequisite cases averaged 3. The corresponding macro means were 2. No dedicated unavailable-source dev mean exists. Kinds and denominators remain separate in the JSON output.

## Current gate implications

- G-d missing definitions: resolved; new-rule dev arithmetic and boundary checks PASS. Gate advancement still waits on earlier ordered gates.
- G-b: fresh final-fixture controls and exact persisted audits have not rerun.
- G-c: proposed HTTP observability hook remains unapplied and unapproved; integrated instrumentation validation is incomplete.
- G-e/G-f: no new independent scorer review or uninvolved clarification ratings were supplied.
- G-g/G-h: no final freeze or live restore-only preflight. Stage 4 remains unauthorized.

See [the adopted rules](PREDICTIONS_AMENDMENT_2026-11-14.md), [owner confirmation](OWNER_CONFIRMATION.json), [dev analysis](analysis-output/dev-analysis.json) and [test results](prediction-tests.json). The earlier missing-definition statements remain correct historical checkpoint records and are superseded by this amendment; their files were not edited.
