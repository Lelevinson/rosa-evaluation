# Gazebo D analysis: dev

Descriptive, per model, never pooled. Zero model requests.

| Model | Arm | Known-goal V2 | V3 | Censored | Calls (all) | Native (all) | Matched pairs | R | D-P1 | D-P2 | D-P3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| sol | primitives | 5/5 | 5/5 | 0 | 20 | 11 | 5 | 0.4737 | Support | Support | Support |
| sol | macro | 5/5 | 5/5 | 0 | 11 | 11 | 5 | 0.4737 | Support | Support | Support |
| qwen | primitives | 4/5 | 4/5 | 0 | 29 | 14 | 3 | 0.5 | Uninformative | Uninformative | Support |
| qwen | macro | 3/5 | 3/5 | 0 | 20 | 14 | 3 | 0.5 | Uninformative | Uninformative | Support |
| ministral | primitives | 3/5 | 3/5 | 0 | 24 | 11 | 3 | 0.5 | Uninformative | Uninformative | Support |
| ministral | macro | 4/5 | 4/5 | 0 | 16 | 15 | 3 | 0.5 | Uninformative | Uninformative | Support |
| llama | primitives | 1/5 | 1/5 | 0 | 28 | 15 | 1 | 0.3333 | Uninformative | Uninformative | Support |
| llama | macro | 2/5 | 2/5 | 0 | 22 | 17 | 1 | 0.3333 | Uninformative | Uninformative | Support |

**sol:** discordant P-only 0, M-only 0, exact p None. Bootstrap: {'groups': 5, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 0], 'call_reduction_95': [0.3333, 0.5652], 'native_ratio_95': [1.0, 1.0], 'draws_without_matched_pairs': 0}.
2 ambiguous transcript(s) PENDING human rating: PRELIMINARY.

**qwen:** discordant P-only 1, M-only 0, exact p 1.0. Bootstrap: {'groups': 5, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [-3, 0], 'call_reduction_95': [0.3333, 0.6], 'native_ratio_95': [1.0, 1.3333], 'draws_without_matched_pairs': 107}.
D-P4 (Qwen inspection-first): {'failed': 3, 'inspection_first': 3, 'share': 1.0, 'pending_ambiguous': 2, 'preliminary': True, 'status': 'Uninformative'}
2 ambiguous transcript(s) PENDING human rating: PRELIMINARY.

**ministral:** discordant P-only 0, M-only 1, exact p 1.0. Bootstrap: {'groups': 5, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 3], 'call_reduction_95': [0.3333, 0.6], 'native_ratio_95': [1.0, 1.3333], 'draws_without_matched_pairs': 107}.
2 ambiguous transcript(s) PENDING human rating: PRELIMINARY.

**llama:** discordant P-only 0, M-only 1, exact p 1.0. Bootstrap: {'groups': 5, 'draws': 10000, 'seed': 20261113, 'pass_difference_macro_minus_primitives_95': [0, 3], 'call_reduction_95': [0.3333, 0.3333], 'native_ratio_95': [1.0, 1.0], 'draws_without_matched_pairs': 3244}.
2 ambiguous transcript(s) PENDING human rating: PRELIMINARY.
