# Leakage check: Gazebo D dev and held-out cases

F1 checker reused unchanged (`member/martin-f1:tools/f1_wording/leakage_check.py`, blob `595e60231e9ec386372d2feb22c68335b8a18e98`). References: 10 M4 requests, 68 F1 reference requests (M4/G1 length-stops, G1 held-out, G1 dev), 30 F1 held-out, and every other D case (dev vs held-out and within held-out). Rewrite if seq >= 0.6 or jac >= 0.5; REVIEW if seq >= 0.45 or jac >= 0.35. Pose names are not normalized (stricter).

**Summary:** {'dev': {'OK': 6, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}, 'heldout': {'OK': 20, 'REVIEW': 0, 'NEAR-PARAPHRASE': 0}}

| Case | Verdict | Nearest (word sequence) | seq | Nearest (content words) | jac |
|---|---|---|---:|---|---:|
| D-dev-01-move_constrained | OK | D D-heldout-11-inspect_healthy | 0.23 | M4 move_constrained | 0.18 |
| D-dev-02-partial_command | OK | D D-heldout-10-missing_prerequisite | 0.33 | D D-heldout-07-partial_command | 0.17 |
| D-dev-03-missing_prerequisite | OK | D D-heldout-09-missing_prerequisite | 0.23 | D D-heldout-11-inspect_healthy | 0.15 |
| D-dev-04-inspect_inactive | OK | D D-heldout-13-inspect_inactive | 0.36 | D D-heldout-11-inspect_healthy | 0.32 |
| D-dev-05-inspect_missing_controllers | OK | D D-heldout-17-inspect_missing_joint | 0.33 | D D-heldout-16-inspect_missing_controllers | 0.25 |
| D-dev-06-ambiguous_goal | OK | D D-heldout-19-ambiguous_goal | 0.42 | M4 ambiguous_goal | 0.12 |
| D-heldout-01-move_constrained | OK | M4 move_constrained | 0.32 | D D-heldout-08-partial_command | 0.33 |
| D-heldout-02-move_constrained | OK | M4 move_constrained | 0.35 | D D-heldout-08-partial_command | 0.22 |
| D-heldout-03-already_satisfied | OK | D D-heldout-07-partial_command | 0.22 | D D-dev-02-partial_command | 0.12 |
| D-heldout-04-already_satisfied | OK | D D-heldout-06-ineffective_command | 0.27 | M4 inspect_missing_joint | 0.21 |
| D-heldout-05-ineffective_command | OK | D D-heldout-10-missing_prerequisite | 0.21 | F1 F1-ho-003 | 0.14 |
| D-heldout-06-ineffective_command | OK | F1 F1-ho-011 | 0.33 | D D-heldout-10-missing_prerequisite | 0.14 |
| D-heldout-07-partial_command | OK | D D-heldout-06-ineffective_command | 0.28 | D D-dev-02-partial_command | 0.17 |
| D-heldout-08-partial_command | OK | M4 move_constrained | 0.38 | D D-heldout-01-move_constrained | 0.33 |
| D-heldout-09-missing_prerequisite | OK | F1 F1-ho-001 | 0.28 | M4 missing_prerequisite | 0.17 |
| D-heldout-10-missing_prerequisite | OK | D D-dev-02-partial_command | 0.33 | M4 missing_prerequisite | 0.21 |
| D-heldout-11-inspect_healthy | OK | M4 inspect_inactive | 0.38 | D D-dev-04-inspect_inactive | 0.32 |
| D-heldout-12-inspect_healthy | OK | M4 inspect_inactive | 0.37 | M4 inspect_inactive | 0.26 |
| D-heldout-13-inspect_inactive | OK | D D-dev-04-inspect_inactive | 0.36 | D D-heldout-11-inspect_healthy | 0.25 |
| D-heldout-14-inspect_inactive | OK | M4 inspect_inactive | 0.35 | D D-heldout-15-inspect_missing_controllers | 0.24 |
| D-heldout-15-inspect_missing_controllers | OK | D D-heldout-16-inspect_missing_controllers | 0.44 | D D-heldout-16-inspect_missing_controllers | 0.26 |
| D-heldout-16-inspect_missing_controllers | OK | D D-heldout-18-inspect_missing_joint | 0.31 | D D-heldout-15-inspect_missing_controllers | 0.26 |
| D-heldout-17-inspect_missing_joint | OK | M4 inspect_inactive | 0.36 | D D-heldout-11-inspect_healthy | 0.24 |
| D-heldout-18-inspect_missing_joint | OK | M4 inspect_missing_joint | 0.39 | M4 inspect_missing_joint | 0.25 |
| D-heldout-19-ambiguous_goal | OK | M4 ambiguous_goal | 0.42 | M4 ambiguous_goal | 0.22 |
| D-heldout-20-ambiguous_goal | OK | G1 dev-008 | 0.33 | D D-heldout-19-ambiguous_goal | 0.22 |
