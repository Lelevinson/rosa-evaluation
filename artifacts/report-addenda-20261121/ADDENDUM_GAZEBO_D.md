# Addendum: Gazebo D, macro vs primitives on fresh UR5e cases (DRAFT, results empty)

**Source of truth:** branch `member/martin-gazebo`, `artifacts/gazebo-d-20261121/` (D0_PROTOCOL.md approved and
frozen, D0_APPROVAL, D0_AMENDMENT_01, the runbook, the wrapper freeze record, the runs and the frozen analysis).

## Prior Gazebo evidence (D is not the first multi-model Gazebo study)
- **M4** (laptop, 2026-10-27): Sol 20/20 in both arms (requests 68 → 38); Qwen 15/20 vs 14/20.
- **2026-11-17 lab M4-based replication** (known M4 families, 4 repetitions): Qwen 27/36 → 28/36 known-goal,
  calls 188 → 98; Ministral 28/36 → 28/36, calls 156 → 82; Llama and Granite 0/36 with the original adapter.
  Source: `artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md` (commit `7260cb8`).
- **2026-11-17 lab native-schema-v1 rerun:** Llama 21/36 → 28/36, Granite 5/36 → 9/36. Source:
  `artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md`.

**What D adds:**
- fresh cases (26, leakage-checked against M4, G1 and F1);
- Sol in the same campaign as the local models;
- one simultaneous harness: all models interleaved by case in one Gazebo instance, under one schedule and one set
  of bounds;
- Granite and Llama only through the frozen Phase B parity adapters.

D numbers are not hardware-matched to the 11-17 lab runs.

## Design (frozen)
The frozen M4 harness, scorer and bounds are used unchanged (62/62 files verified). The model-visible wording is
the frozen M4 wording, which equals the G1 wording. 20 held-out cases = 10 M4 families × 2 (the template groups):
18 known-goal and 2 ambiguous. 6 dev cases. Arms: primitives and macro. The stock-ROSA arm is excluded for time
(future work).

## Gates
| Gate | Criterion | Result |
|---|---|---|
| D1 controls | 52/52 zero-model Gazebo controls pass, with clean teardown | |
| D1 dev | no harness or scorer crash; all dev trials done or V1-censored; every reset check passes; analysis runs end to end | |
| D2 | one attempt per case × arm × model; no row started after Mon 06:00 | |

## Results (held-out, per model, never pooled)
| Model | Label | Known-goal P (V2) | Known-goal M (V2) | V3 P / M | Discordant P-only / M-only (exact p) | Calls all P → M | Matched pairs | R | Native matched P → M | GPU offload |
|---|---|---:|---:|---|---|---|---:|---:|---|---|
| Sol | hosted | /18 | /18 | | | | | | | – |
| Qwen | plain | /18 | /18 | | | | | | | |
| Ministral | plain | /18 | /18 | | | | | | | |
| Granite | adapted, if admitted | /18 | /18 | | | | | | | |
| Llama | adapted, if admitted | /18 | /18 | | | | | | | |

| Prediction (frozen from G1) | Rule | Sol | Qwen | Ministral | Granite | Llama |
|---|---|---|---|---|---|---|
| D-P1: ~40% fewer calls (matched pairs) | Support if R ≥ 0.30; Against if R < 0.15 | | | | | |
| D-P2: native ops not lower in macro | Σ M ≥ Σ P | | | | | |
| D-P3: macro not worse on known-goal | M ≥ P − 2 | | | | | |
| D-P4: Qwen failures are inspection-first | ≥ 50% and ≥ 3 | – | | – | – | – |

Also report: results by type and family; selection vs execution; whole-group bootstrap intervals (10,000 draws,
seed 20261113); all-attempt and matched-success costs; censoring under V1/V2/V3. Ambiguous cases stay
PRELIMINARY until human-rated.

## Limits to state
AI-authored cases; only the 3 registered poses and the M4 fault set; 10 groups, so intervals are wide; laptop
partial offload; Sol is hosted; no stock-ROSA arm, so no claim of improvement over original ROSA; no physical robot.

Teammate overlap (reported by the teammates in rosa-contexts `member/levinson` `87eb2bd`, `member/krln` `8072aaf`; not verified by us): Gazebo D is NEW (Levinson's Gazebo stage is Nav2/TurtleBot read-then-act, method M). Macro verification is CONSISTENT with Levinson's report-gate screen (0 claim/final-state contradictions in 128 dev action episodes): do not claim the macro catches false reports; its supported value is call efficiency. See D0_AMENDMENT_02.

Future work: reuse Levinson's original-ROSA baseline harness to add a stock-ROSA arm to the macro comparison.
