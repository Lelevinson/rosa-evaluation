# M4 execution checkpoint

Date: 2026-10-27.

This report is generated from saved attempts. Unstarted cells are not assumed successful.

| Backend / condition | Attempts | Primary passes | Completion incl. recovery | Requests | Known output tokens | Native ops | Task seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| siwc / primitives | 20/20 | 20 | 20 | 68 | 2221 | 38 | 328.36 |
| siwc / macro | 20/20 | 20 | 20 | 38 | 1145 | 40 | 194.58 |

siwc: COMPLETE.
Complete paired cells: 20/20; jointly successful pairs: 20. Engineering screen: True.
Macro paired wins: []; losses: [].
| ollama / primitives | 20/20 | 15 | 15 | 91 | 19445 | 50 | 2669.72 |
| ollama / macro | 20/20 | 14 | 14 | 53 | 12519 | 48 | 1703.63 |

ollama: COMPLETE.
Complete paired cells: 20/20; jointly successful pairs: 13. Engineering screen: False.
Macro paired wins: ['move_constrained/r2']; losses: ['partial_command/r1', 'partial_command/r2'].

Clarification transcripts awaiting operator review: 4.

Do not treat automated clarification scores or an incomplete schedule as final acceptance. Known usage can be a lower bound when requests are unreturned or externally failed. Task wall times exclude setup, independent outside-task observations and persisted audit. Compare conditions within each backend; do not infer a causal speed ranking across models.

M2/M3 and earlier studies remain unchanged. This study adds no planner, JTVR, memory or robot hardware.
