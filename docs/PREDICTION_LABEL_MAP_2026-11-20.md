# G1 prediction label map

Date: 2026-11-20. Read-only reconciliation; no analysis was run and no earlier file was edited.
Purpose: the same labels P1–P5 mean different things in three G1 documents. This table
maps each older label to the frozen amendment label and states the final verdict per model.

## Sources opened

| Short name | File | Status |
|---|---|---|
| **S0** (stopped Stage 0) | `artifacts/macro-generalization-20261113/PREDICTIONS_AND_THRESHOLDS.md` | Superseded design; retained |
| **R1** (revision 1) | `artifacts/macro-generalization-20261113/revision-1/PREDICTIONS_AND_THRESHOLDS.md` (confirmed for dev use in `revision-1/stage-2/CONFIRMATION_2026-11-14.md`) | Replaced before held-out runs |
| **A** (frozen amendment) | `artifacts/macro-generalization-20261113/revision-1/stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md` | Authoritative for all held-out verdicts |
| Verdicts | `G1_SOL_ADJUDICATED_REPORT_2026-11-19.md`, `G1_QWEN_LAB_REPORT_2026-11-19.md`, `G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md` | Final for Sol and the extension; Qwen withheld |

## Mapping: old label → amendment label

| S0 label | R1 label | Subject | Amendment label | Change |
|---|---|---|---|---|
| P1 — fractional call saving *grows* with depth (d6 − d1 ≥ 15 pp) | P4 — fractional saving does *not* grow with depth (d6 − d1 interval within ±0.10) | Depth contrast | **P1′** — *absolute* calls saved per inspection task ≈ 1 at every depth (Sol, matched success) | S0's direction was reversed in R1; A replaced the fractional contrast with an absolute endpoint |
| P2 — call saving transfers to both domains (≥ 20 %) | P1 — call saving ≥ 20 % in both domains | Call-saving size | *(none)* | Replaced; the both-domains requirement moved into P1′ and P2. Call savings are now reported descriptively only |
| P4 — correctness within 5 pp loss | P2 — correctness within 5 pp loss | Correctness non-inferiority | *(none)* | **Dropped as a prediction.** A's P2 is a different endpoint (native operations) |
| P3 — catalogue 12 vs 3, error rise ≥ 10 pp | P3 — catalogue 10 vs 3, error rise ≥ 10 pp | Catalogue size | **P4** — Qwen first-turn accuracy at sizes 3/5/10; fall ≥ 20 pp is Against | Renumbered, threshold and sizes changed |
| P5 — acquisition contract fits unchanged API | P5 — unchanged API, safety/observability preserved | Hosting | **P5** — both domains hosted with zero required hosting-source changes | Same number, narrowed wording |
| — | — | Native work | **P2** — macro/primitive native-operation ratio within [0.75, 1.25] at every depth, per domain | New in A |
| — | — | Horizon reliability | **P3** — DROPPED, deferred to a G2 | New label, dropped |
| — | — | Write vs inspection cost | **P6** — descriptive only | New in A |
| — | — | Write-bearing contrast | **H-write** (not a P-label) | Frozen 2026-11-19, before the three added models ran; derived from Qwen's post-hoc split |

## Final verdicts (amendment labels)

| Endpoint | Sol | Qwen | Ministral | Granite | Llama |
|---|---|---|---|---|---|
| P1′ | **Support** (formal; Sol-specific endpoint) | Withheld (Batch B pending) | Against *(diagnostic only)* | Uninformative *(diagnostic)* | Uninformative *(diagnostic)* |
| P2 | Uninformative (V2 Support, V3 Against in arm) | Withheld | Against | Uninformative | Against |
| P3 | Dropped | Dropped | Dropped | Dropped | Dropped |
| P4 | Not run | Not run | Not run | Not run | Not run |
| P5 | Support | Withheld | Support | Support | Support |
| P6 | Descriptive (primitive writes 5.17 vs inspections 3.09 calls; macro 2 for both) | Withheld | Descriptive | Descriptive | Descriptive |
| H-write | n/a (origin was Qwen) | n/a (post-hoc origin) | Uninformative (8/8 ceiling) | Uninformative (0/8 floor) | Uninformative (0/8 floor) |

Old S0/R1 endpoints have **no verdicts**. They were replaced before any held-out run, so
none of them was tested, and none should be described as Supported or Against.

## Points that are easy to get wrong

1. **P1′ did not go Against for Sol.** It went **Support**. P1′ predicts a *constant*
   saving of about one call per inspection task at every depth. That is the turn-based
   pattern (primitive select/read/report = 3 vs macro 2). The prediction refuted by the
   bundled `read_state` design was **S0 P1** ("savings grow with depth"). It was revised
   before testing, not tested and failed.
2. **"P2" means correctness in R1 and native operations in A.** A sentence such as "P2 was
   Against" is ambiguous unless the document version is named.
3. **Correctness non-inferiority is no longer a frozen prediction.** Correctness results
   (e.g. Sol 33/33 → 36/36) are descriptive outcomes, not a P2 verdict.
4. Ministral/Granite/Llama P1′ values come from applying the Sol-specific rule. They are
   diagnostics, not a broadened endpoint.
5. P4 "Uninformative" in the engine output is a no-probe fallback, not observed data.
