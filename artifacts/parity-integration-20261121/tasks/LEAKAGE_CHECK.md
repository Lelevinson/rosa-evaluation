# Leakage check: parity scratch and acceptance tasks

F1 checker reused unchanged: `member/martin-f1:tools/f1_wording/leakage_check.py` (git blob `595e60231e9ec386372d2feb22c68335b8a18e98`). References: 98 for scratch (F1 set: M4/G1 length-stops, G1 held-out, G1 dev; plus 30 F1 held-out), 110 for acceptance (adds the 12 scratch tasks). Rewrite if seq >= 0.6 or jac >= 0.5; REVIEW if seq >= 0.45 or jac >= 0.35.

**Summary:** {'scratch': {'OK': 12, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}, 'acceptance': {'OK': 10, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}}. **Within-set:** {'scratch': {'OK': 12, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}, 'acceptance': {'OK': 10, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}}.

| Task | Type | Verdict | Nearest (word sequence) | seq | Nearest (content words) | jac |
|---|---|---|---|---:|---|---:|
| PAR-sc-001 | inspection | OK | F1 F1-ho-023 | 0.29 | G1 heldout-022 | 0.06 |
| PAR-sc-002 | inspection | OK | F1 F1-ho-023 | 0.37 | F1 F1-ho-023 | 0.07 |
| PAR-sc-003 | inspection | OK | G1 dev-007 | 0.36 | F1 F1-ho-013 | 0.07 |
| PAR-sc-004 | inspection | OK | F1 F1-ho-019 | 0.26 | F1 F1-ho-027 | 0.11 |
| PAR-sc-005 | write | OK | length-stop G1 031-macro | 0.33 | F1 F1-ho-029 | 0.06 |
| PAR-sc-006 | write | OK | F1 F1-ho-009 | 0.32 | length-stop G1 030-primitives | 0.10 |
| PAR-sc-007 | write | OK | F1 F1-ho-009 | 0.34 | F1 F1-ho-015 | 0.08 |
| PAR-sc-008 | write | OK | G1 dev-006 | 0.30 | F1 F1-ho-011 | 0.08 |
| PAR-sc-009 | missing_prerequisite | OK | F1 F1-ho-001 | 0.28 | F1 F1-ho-001 | 0.09 |
| PAR-sc-010 | missing_prerequisite | OK | F1 F1-ho-007 | 0.31 | F1 F1-ho-007 | 0.06 |
| PAR-sc-011 | ambiguous | OK | G1 dev-008 | 0.32 | G1 dev-008 | 0.00 |
| PAR-sc-012 | ambiguous | OK | F1 F1-ho-015 | 0.40 | G1 heldout-029 | 0.07 |
| PAR-acc-001 | inspection | OK | parity PAR-sc-001 | 0.29 | F1 F1-ho-009 | 0.08 |
| PAR-acc-002 | inspection | OK | F1 F1-ho-023 | 0.30 | F1 F1-ho-001 | 0.10 |
| PAR-acc-003 | inspection | OK | F1 F1-ho-023 | 0.40 | F1 F1-ho-017 | 0.09 |
| PAR-acc-004 | inspection | OK | F1 F1-ho-029 | 0.32 | parity PAR-sc-005 | 0.07 |
| PAR-acc-005 | write | OK | G1 dev-001 | 0.39 | length-stop G1 031-macro | 0.14 |
| PAR-acc-006 | write | OK | parity PAR-sc-007 | 0.30 | F1 F1-ho-003 | 0.10 |
| PAR-acc-007 | write | OK | F1 F1-ho-009 | 0.31 | parity PAR-sc-008 | 0.08 |
| PAR-acc-008 | missing_prerequisite | OK | parity PAR-sc-009 | 0.35 | parity PAR-sc-006 | 0.10 |
| PAR-acc-009 | inspection | OK | F1 F1-ho-029 | 0.38 | F1 F1-ho-029 | 0.17 |
| PAR-acc-010 | ambiguous | OK | F1 F1-ho-019 | 0.38 | F1 F1-ho-019 | 0.00 |

Within-set nearest neighbour (max seq / jac):

- PAR-sc-001: parity PAR-sc-002 0.27 / 0.00 (OK)
- PAR-sc-002: parity PAR-sc-001 0.27 / 0.00 (OK)
- PAR-sc-003: parity PAR-sc-005 0.25 / 0.08 (OK)
- PAR-sc-004: parity PAR-sc-002 0.22 / 0.08 (OK)
- PAR-sc-005: parity PAR-sc-007 0.29 / 0.00 (OK)
- PAR-sc-006: parity PAR-sc-005 0.28 / 0.07 (OK)
- PAR-sc-007: parity PAR-sc-005 0.29 / 0.00 (OK)
- PAR-sc-008: parity PAR-sc-005 0.27 / 0.00 (OK)
- PAR-sc-009: parity PAR-sc-007 0.31 / 0.05 (OK)
- PAR-sc-010: parity PAR-sc-009 0.30 / 0.05 (OK)
- PAR-sc-011: parity PAR-sc-012 0.30 / 0.00 (OK)
- PAR-sc-012: parity PAR-sc-011 0.30 / 0.00 (OK)
- PAR-acc-001: parity PAR-acc-003 0.25 / 0.00 (OK)
- PAR-acc-002: parity PAR-acc-004 0.30 / 0.00 (OK)
- PAR-acc-003: parity PAR-acc-009 0.27 / 0.00 (OK)
- PAR-acc-004: parity PAR-acc-009 0.32 / 0.00 (OK)
- PAR-acc-005: parity PAR-acc-010 0.31 / 0.00 (OK)
- PAR-acc-006: parity PAR-acc-010 0.23 / 0.00 (OK)
- PAR-acc-007: parity PAR-acc-005 0.29 / 0.00 (OK)
- PAR-acc-008: parity PAR-acc-010 0.23 / 0.00 (OK)
- PAR-acc-009: parity PAR-acc-004 0.32 / 0.00 (OK)
- PAR-acc-010: parity PAR-acc-005 0.31 / 0.00 (OK)
