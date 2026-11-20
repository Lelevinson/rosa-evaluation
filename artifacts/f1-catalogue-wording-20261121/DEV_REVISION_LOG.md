# F1 wording revision log (dev only; at most 2 revisions)

| Revision | Date | Basis | Change | Dev result (Qwen, macro, G1 dev ~~16~~ 18) | Readiness / inspect-first deliberation (pre-registered diagnostic, PROTOCOL §5) |
|---|---|---|---|---|---|
| `f1-w-r0` | 2026-11-21 | Source check (WORDING_DIFF.md), before any F1 run | Initial W1a + W1b + W2 | not run | not run. Record per trial: keyword hits (`readiness`, `inspect first`, `inspect … before`, `check … before`, `before moving`), then the manual-read verdict, and whether W1a's "does not read any readiness check" sentence triggered it |

Rules: revisions use G1 dev results only. No held-out case, no length-stop trial and no G1 held-out case
may inform them. Each revision records the dev evidence that motivated it and keeps every sentence
source-justified in WORDING_DIFF.md. After the last revision the wording is frozen before any held-out run.
