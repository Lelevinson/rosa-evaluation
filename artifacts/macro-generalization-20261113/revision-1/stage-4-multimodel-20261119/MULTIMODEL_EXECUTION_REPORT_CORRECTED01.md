# G1 additional local models — execution and descriptive results

Date: **2026-11-19**. **Exploratory backends, added after Sol and Qwen results.**

**228/228 scheduled attempts are retained. Formal analysis and clarification semantics await actual human review.**

Same 38 AI-authored mock cases, two architectures, fixed prompts and limits. This is not Gazebo, a physical-robot study, independent case generalization, an intrinsic model ranking or a comparison against unmodified ROSA.

| Model | Primitives: known-goal PASS/evaluable | Macro: known-goal PASS/evaluable | All-attempt calls P → M | Mean task seconds P → M | Charged / 611 |
|---|---:|---:|---:|---:|---:|
| ministral | 28/36 | 33/36 | 154 → 83 | 5.32 → 3.18 | 240 |
| granite | 0/36 | 0/36 | 38 → 38 | 3.55 → 3.15 | 79 |
| llama | 0/36 | 1/36 | 203 → 185 | 1.96 → 2.11 | 391 |

## ministral

{'primitives': {'PASS': 28, 'FAIL': 9, 'PENDING_HUMAN_REVIEW': 1}, 'macro': {'PASS': 33, 'FAIL': 3, 'PENDING_HUMAN_REVIEW': 2}}

Paired outcomes: {'both_pass': 27, 'neither': 2, 'macro_only': 6, 'pending_human': 2, 'primitive_only': 1}. Matched successful pairs: 27. Human-pending and censored pairs are not silently treated as failures or successes.

| Cost | All attempts: primitives | All attempts: macro | Matched success: primitives | Matched success: macro |
|---|---:|---:|---:|---:|
| attempts | 38 | 38 | 27 | 27 |
| calls | 154 | 83 | 110 | 58 |
| input_tokens | 289754 | 149219 | 207603 | 103276 |
| output_tokens | 17691 | 9814 | 12455 | 7310 |
| native_operations | 102 | 127 | 85 | 87 |
| task_seconds | 202.129516126588 | 120.75645585171878 | 142.53995810449123 | 90.4690751414746 |
| mean_seconds | 5.319197792804947 | 3.1778014697820733 | 5.279257707573749 | 3.3507064867212817 |
| median_seconds | 5.397361951414496 | 3.024836427066475 | 5.166881979443133 | 3.555920380167663 |
| invalid_attempts | 40 | 5 | 21 | 2 |
| length_stops | 0 | 0 | 0 | 0 |
| budget_endings | 4 | 1 | 0 | 0 |
| incomplete_usage | 0 | 0 | 0 | 0 |

All-attempt call reduction: 46.1%. Conditional matched-success call reduction: 47.27272727272727%. Conditional costs do not replace the all-attempt ledger.

Campaign elapsed: 964.79s, including bookkeeping/auditing outside measured task time. Inference 237 + preparation 2 + cleanup 1 = 240 charged. Eligible reserve retries: 0. All 76 local and 76 persisted audits passed.

Write/partial-write versus other known-goal counts: {'write_bearing': {'primitives': {'PASS': 4, 'FAIL': 4}, 'macro': {'PASS': 8}}, 'other_known_goal': {'primitives': {'PASS': 24, 'FAIL': 4}, 'macro': {'PASS': 25, 'FAIL': 3}}}.

Accepted report truth and requested-goal correctness remain separate. Diagnostic flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}.

Returned timing coverage and rates: {'primitives': {'physical_records': 154, 'field_presence': {'total_duration': 154, 'load_duration': 154, 'prompt_eval_count': 154, 'prompt_eval_duration': 154, 'eval_count': 154, 'eval_duration': 154}, 'recorded_sums': {'total_duration': 198320296893, 'load_duration': 130365741, 'prompt_eval_count': 289754, 'prompt_eval_duration': 12165822999, 'eval_count': 17691, 'eval_duration': 177296549999}, 'cached_count_presence': 0, 'decode_tokens_per_second': 99.78197545355384, 'prompt_tokens_per_second': 23817.048795121962, 'missing_values_estimated': False}, 'macro': {'physical_records': 83, 'field_presence': {'total_duration': 83, 'load_duration': 83, 'prompt_eval_count': 83, 'prompt_eval_duration': 83, 'eval_count': 83, 'eval_duration': 83}, 'recorded_sums': {'total_duration': 117642271876, 'load_duration': 3968992936, 'prompt_eval_count': 149219, 'prompt_eval_duration': 9518627000, 'eval_count': 9814, 'eval_duration': 97986879999}, 'cached_count_presence': 0, 'decode_tokens_per_second': 100.15626581946641, 'prompt_tokens_per_second': 15676.525616562136, 'missing_values_estimated': False}}. Missing values are not estimated. See JSON for per-family costs and whether injected faults actually executed.

## granite

{'primitives': {'FAIL': 36, 'PENDING_HUMAN_REVIEW': 2}, 'macro': {'FAIL': 36, 'PENDING_HUMAN_REVIEW': 2}}

Paired outcomes: {'neither': 36, 'pending_human': 2}. Matched successful pairs: 0. Human-pending and censored pairs are not silently treated as failures or successes.

| Cost | All attempts: primitives | All attempts: macro | Matched success: primitives | Matched success: macro |
|---|---:|---:|---:|---:|
| attempts | 38 | 38 | 0 | 0 |
| calls | 38 | 38 | 0 | 0 |
| input_tokens | 60371 | 60333 | 0 | 0 |
| output_tokens | 12567 | 10856 | 0 | 0 |
| native_operations | 0 | 0 | 0 | 0 |
| task_seconds | 134.76754218619317 | 119.71863587666303 | 0 | 0 |
| mean_seconds | 3.546514268057715 | 3.150490417806922 | None | None |
| median_seconds | 3.4446238642558455 | 2.9742732723243535 | None | None |
| invalid_attempts | 0 | 0 | 0 | 0 |
| length_stops | 1 | 0 | 0 | 0 |
| budget_endings | 0 | 0 | 0 | 0 |
| incomplete_usage | 0 | 0 | 0 | 0 |

All-attempt call reduction: 0.0%. Conditional matched-success call reduction: not defined%. Conditional costs do not replace the all-attempt ledger.

Campaign elapsed: 894.16s, including bookkeeping/auditing outside measured task time. Inference 76 + preparation 2 + cleanup 1 = 79 charged. Eligible reserve retries: 0. All 76 local and 76 persisted audits passed.

Write/partial-write versus other known-goal counts: {'write_bearing': {'primitives': {'FAIL': 8}, 'macro': {'FAIL': 8}}, 'other_known_goal': {'primitives': {'FAIL': 28}, 'macro': {'FAIL': 28}}}.

Accepted report truth and requested-goal correctness remain separate. Diagnostic flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}.

Returned timing coverage and rates: {'primitives': {'physical_records': 38, 'field_presence': {'total_duration': 38, 'load_duration': 38, 'prompt_eval_count': 38, 'prompt_eval_duration': 38, 'eval_count': 38, 'eval_duration': 38}, 'recorded_sums': {'total_duration': 133802718802, 'load_duration': 36126347, 'prompt_eval_count': 60371, 'prompt_eval_duration': 5650698000, 'eval_count': 12567, 'eval_duration': 125885227000}, 'cached_count_presence': 0, 'decode_tokens_per_second': 99.82902918386127, 'prompt_tokens_per_second': 10683.81286701218, 'missing_values_estimated': False}, 'macro': {'physical_records': 38, 'field_presence': {'total_duration': 38, 'load_duration': 38, 'prompt_eval_count': 38, 'prompt_eval_duration': 38, 'eval_count': 38, 'eval_duration': 38}, 'recorded_sums': {'total_duration': 118536583878, 'load_duration': 1587663008, 'prompt_eval_count': 60333, 'prompt_eval_duration': 5926607000, 'eval_count': 10856, 'eval_duration': 108633726999}, 'cached_count_presence': 0, 'decode_tokens_per_second': 99.93213249601509, 'prompt_tokens_per_second': 10180.023747145711, 'missing_values_estimated': False}}. Missing values are not estimated. See JSON for per-family costs and whether injected faults actually executed.

## llama

{'primitives': {'FAIL': 38}, 'macro': {'FAIL': 37, 'PASS': 1}}

Paired outcomes: {'neither': 37, 'macro_only': 1}. Matched successful pairs: 0. Human-pending and censored pairs are not silently treated as failures or successes.

| Cost | All attempts: primitives | All attempts: macro | Matched success: primitives | Matched success: macro |
|---|---:|---:|---:|---:|
| attempts | 38 | 38 | 0 | 0 |
| calls | 203 | 185 | 0 | 0 |
| input_tokens | 287906 | 295800 | 0 | 0 |
| output_tokens | 5374 | 5419 | 0 | 0 |
| native_operations | 42 | 122 | 0 | 0 |
| task_seconds | 74.57015304267406 | 80.13425550889224 | 0 | 0 |
| mean_seconds | 1.9623724484914227 | 2.108796197602427 | None | None |
| median_seconds | 1.9231761968694627 | 2.061093036085367 | None | None |
| invalid_attempts | 150 | 135 | 0 | 0 |
| length_stops | 0 | 0 | 0 | 0 |
| budget_endings | 37 | 31 | 0 | 0 |
| incomplete_usage | 0 | 0 | 0 | 0 |

All-attempt call reduction: 8.9%. Conditional matched-success call reduction: not defined%. Conditional costs do not replace the all-attempt ledger.

Campaign elapsed: 802.87s, including bookkeeping/auditing outside measured task time. Inference 388 + preparation 2 + cleanup 1 = 391 charged. Eligible reserve retries: 0. All 76 local and 76 persisted audits passed.

Write/partial-write versus other known-goal counts: {'write_bearing': {'primitives': {'FAIL': 8}, 'macro': {'FAIL': 7, 'PASS': 1}}, 'other_known_goal': {'primitives': {'FAIL': 28}, 'macro': {'FAIL': 28}}}.

Accepted report truth and requested-goal correctness remain separate. Diagnostic flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}.

Returned timing coverage and rates: {'primitives': {'physical_records': 203, 'field_presence': {'total_duration': 203, 'load_duration': 203, 'prompt_eval_count': 203, 'prompt_eval_duration': 203, 'eval_count': 203, 'eval_duration': 203}, 'recorded_sums': {'total_duration': 70779517393, 'load_duration': 166770134, 'prompt_eval_count': 287906, 'prompt_eval_duration': 13193199999, 'eval_count': 5374, 'eval_duration': 46411892998}, 'cached_count_presence': 0, 'decode_tokens_per_second': 115.78928703105427, 'prompt_tokens_per_second': 21822.302399859193, 'missing_values_estimated': False}, 'macro': {'physical_records': 185, 'field_presence': {'total_duration': 185, 'load_duration': 185, 'prompt_eval_count': 185, 'prompt_eval_duration': 185, 'eval_count': 185, 'eval_duration': 185}, 'recorded_sums': {'total_duration': 74828394670, 'load_duration': 1966064697, 'prompt_eval_count': 295800, 'prompt_eval_duration': 14654786998, 'eval_count': 5419, 'eval_duration': 47326693992}, 'cached_count_presence': 0, 'decode_tokens_per_second': 114.50197643038442, 'prompt_tokens_per_second': 20184.530832168974, 'missing_values_estimated': False}}. Missing values are not estimated. See JSON for per-family costs and whether injected faults actually executed.

## Interpretation and remaining work

The complete experiment package includes execution architecture and condition wording; these effects are not isolated. Macros remove routine decision boundaries and may perform more native work. Fewer calls or faster failure alone is not useful efficiency. Use verified correctness, all-attempt accounting and matched-success costs together.

The original Sol batch used hosted inference with its original laptop/WSL execution provenance. Qwen and the new backends use the lab; the new container image also differs from the old Qwen image. No direct hardware-matched speed or intrinsic-model superiority claim follows. Sol retained 33/33 versus 36/36 known-goal correctness among evaluable attempts (three primitive infrastructure-censored); Qwen retained 26/36 versus 30/36, with four separate clarification reviews outstanding. These contextual results are not pooled with this extension.

A pooled, blinded packet contains only the new models’ four ambiguous responses each. Levinson is nominated; eligibility and ratings must be honestly returned. No assistant ratings, copied prior ratings or human adjudication are supplied. Formal prediction analysis, H-write closeout and final aggregate interpretation remain withheld until required reviews. H-write is descriptive and its raw-count rule may support concentration even when total accuracy worsens; floors/ceilings force Uninformative.

P3 is dropped horizon reliability; the P4 catalogue probe was not run. P1′ remains formally Sol-specific. All protected source, frozen inputs, old Sol/Qwen artifacts and backend seals reverified unchanged. No inference requests were made for reporting.
