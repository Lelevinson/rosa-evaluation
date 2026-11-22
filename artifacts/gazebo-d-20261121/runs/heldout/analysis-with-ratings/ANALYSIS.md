# Gazebo D analysis: heldout

Descriptive, per model, never pooled. Zero model requests.

| Model | Arm | Known-goal V2 | V3 | Censored | Calls (all) | Native (all) | Matched pairs | R | D-P1 | D-P2 | D-P3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| sol | primitives | 18/18 | 18/18 | 0 | 70 | 41 | 18 | 0.4559 | Support | Support | Support |
| sol | macro | 18/18 | 18/18 | 0 | 39 | 41 | 18 | 0.4559 | Support | Support | Support |
| qwen | primitives | 12/18 | 12/18 | 0 | 91 | 50 | 11 | 0.4783 | Support | Against | Support |
| qwen | macro | 13/18 | 13/18 | 0 | 50 | 49 | 11 | 0.4783 | Support | Against | Support |
| ministral | primitives | 16/18 | 16/18 | 0 | 81 | 39 | 14 | 0.459 | Support | Support | Support |
| ministral | macro | 15/18 | 15/18 | 0 | 50 | 46 | 14 | 0.459 | Support | Support | Support |
| llama | primitives | 8/18 | 8/18 | 0 | 89 | 51 | 8 | 0.3333 | Support | Support | Support |
| llama | macro | 11/18 | 11/18 | 0 | 56 | 55 | 8 | 0.3333 | Support | Support | Support |

**sol:** discordant P-only 0, M-only 0, exact p None. Bootstrap: {'groups': 9, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 0], 'call_reduction_95': [0.3607, 0.5385], 'native_ratio_95': [0.8723, 1.1714], 'draws_without_matched_pairs': 0}.

**qwen:** discordant P-only 1, M-only 2, exact p 1.0. Bootstrap: {'groups': 9, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 3], 'call_reduction_95': [0.3939, 0.5593], 'native_ratio_95': [0.7857, 1.0], 'draws_without_matched_pairs': 0}.
D-P4 (Qwen inspection-first): {'failed': 15, 'inspection_first': 14, 'share': 0.9333333333333333, 'pending_ambiguous': 0, 'preliminary': False, 'status': 'Support'}

**ministral:** discordant P-only 2, M-only 1, exact p 1.0. Bootstrap: {'groups': 9, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [-4, 2], 'call_reduction_95': [0.3191, 0.557], 'native_ratio_95': [1.0, 1.2222], 'draws_without_matched_pairs': 0}.

**llama:** discordant P-only 0, M-only 3, exact p 0.25. Bootstrap: {'groups': 9, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 6], 'call_reduction_95': [0.1667, 0.5238], 'native_ratio_95': [0.8421, 1.3158], 'draws_without_matched_pairs': 4}.
