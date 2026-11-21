# Parity amendment 01 (2026-11-21): overlap with teammates' work

Owner instruction, 2026-11-21. No change to tasks, criteria, scorer or thresholds (ACCEPTANCE_CRITERIA.md stays frozen).

**Source:** teammates' reported evidence in Lelevinson/rosa-contexts (public), `origin/member/levinson` at `87eb2bd`
and `origin/member/krln` at `8072aaf`. **Reported by the teammates; not verified by us.**

| Topic | Classification | Record |
|---|---|---|
| Parity / argument handling | **ADJACENT** | Levinson's team decided on **no argument coercion in any arm** (`exam_prep_20261121`, update 2). Consequence here: native-schema-v1's SDK normalization (list-strings turned into arrays) and ChatOllama's shallow JSON-decoding of string arguments must be **reported as assistance**, separate from the model's own schema compliance. Parity uses no extra coercion; the acceptance scorer counts only what the harness accepts. |
| Macro verification | **CONSISTENT** | Levinson's report-gate screen found 0 claim/final-state contradictions in 128 dev action episodes. Our reports must **not** claim the macro catches false reports. Its supported value is call efficiency. |

Future work (for the report): reuse Levinson's original-ROSA baseline harness to add a stock-ROSA arm to the
macro comparison.
