# F1 wording revision log (dev only; at most 2 revisions)

| Revision | Date | Basis | Change | Dev result (Qwen, macro, G1 dev ~~16~~ 18) | Readiness / inspect-first deliberation (pre-registered diagnostic, PROTOCOL §5) |
|---|---|---|---|---|---|
| `f1-w-r0` | 2026-11-21 | Source check (WORDING_DIFF.md), before any F1 run | Initial W1a + W1b + W2 | **Run `runs/stage1a-dev-qwen-r0b`** (laptop, lab unavailable, D16; Qwen 17/33 layers on GPU; 36 trials, 0 censored). Base 17/18, new 18/18 (provisional; ambiguous PENDING human review). Known-goal 16/16 both arms (net 0). Only difference: ambiguous G1r1-dev-008 (base selected `arm.cedar`; new asked a clarifying question). Length stops 0/0; inspection-first on movement types 0/0; movement selections on non-movement cases 0/0. `runs/stage1a-dev-qwen-r0b/DEV_ANALYSIS.json` | Keyword hits: base 11/18, new 11/18 trials, almost all on `readiness`. **Manual read of all 11 new-arm flagged trials (`DEV_DIAGNOSTIC.json`):** every hit is descriptive (the model reports observed readiness checks, or notes the user asked to inspect readiness checks); in the ambiguous cases it lists readiness as one possible meaning before asking. **No trial deliberates about checking readiness before a movement**; the movement case (dev-013 new) selected `base.sable` directly. Verdict: W1a's sentence did **not** trigger readiness deliberation → **no revision**. r0 frozen as final (D17: max 1 revision, none used) |

Rules: revisions use G1 dev results only. No held-out case, no length-stop trial and no G1 held-out case
may inform them. Each revision records the dev evidence that motivated it and keeps every sentence
source-justified in WORDING_DIFF.md. After the last revision the wording is frozen before any held-out run.
