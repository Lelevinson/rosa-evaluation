# Addendum: F1 catalogue wording for Qwen (DRAFT, results empty)

**Source of truth:** branch `member/martin-f1`, `artifacts/f1-catalogue-wording-20261121/PROTOCOL.md` (decisions
D1-D16, plus D17 if a dev wording revision is made), `WORDING_DIFF.md` and the frozen analysis outputs. This draft
only lays out the report section. It does not restate or change any F1 rule.

## What was tested
Whether honest catalogue wording (W1) and an explicit clarification route (W2) reduce Qwen's inspection-first
selections and raise its G1-mock macro pass rate, without hurting Sol. Arms: Q-base, Q-new, S-base, S-new
(macro only). 30 fresh AI-authored held-out cases, one attempt each, seeded order (seed 20261121).
Machine: laptop (D16) for Qwen; Sol hosted, run from the laptop WSL env.

## Gates
| Gate | Criterion | Result |
|---|---|---|
| G1 controls | C1 46/46 identical behaviour; C2 8/8 no-tool route; dry run with 0 model requests and 0 errors | |
| Stage 1a dev | ≤ 1 wording revision (D17), readiness-deliberation diagnostic logged, then freeze | |
| Stage 1b stops | no C1 mismatch, no frozen-input hash mismatch, censoring ≤ 20% per arm | |

## Results (held-out)
| Arm | Known-goal passes /24 | All passes /30 | Calls | Native ops | Length stops | Censored | GPU layers |
|---|---:|---:|---:|---:|---:|---:|---|
| Q-base | | | | | | | |
| Q-new | | | | | | | |
| S-base | | | | | | | – |
| S-new | | | | | | | – |

| Prediction | Threshold (frozen) | Observed | Status |
|---|---|---|---|
| P-a: Q-new beats Q-base | discordant net ≥ +3 over 24 pairs | | |
| P-b: inspection-first on movement types | Q-new < Q-base | | |
| P-c: inspection guard | Q-new loses ≤ 1 of 10 | | |
| P-d: Sol guard | ≤ 1 per F1 type | | |
| P-e: length stops | Q-new < Q-base | | |
| P-f′: movement-choice veto | Q-new ≤ Q-base on the 16 cases | | |
| **Decision** | adopt only if P-a, P-c and P-d hold and P-f′ does not fire | | |

Ambiguous cases stay PRELIMINARY until the blinded kit is rated by a human (Levinson). No AI ratings.

## Limits to state
AI-authored cases; G1 mock world, not Gazebo; laptop partial offload, not comparable to lab G1 speed;
"not adopted" is a valid outcome; this is a Qwen-only wording question, not a general prompt claim.
