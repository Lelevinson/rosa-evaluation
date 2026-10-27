# Exploratory uncertainty and paired analysis

Date: **2026-10-27**.

This is retrospective postprocessing, not a changed M4 protocol or a new experiment. The frozen engineering screen and primary scores are unchanged. Ten hand-authored families with two repeated cases do not form20 independent task families. The primary presentation is the family table and paired outcomes, not a pooled p-value.

| Backend | Both pass | Primitive-only pass | Macro-only pass | Both fail |
|---|---:|---:|---:|---:|
| Sol | 20 | 0 | 0 | 0 |
| Qwen | 13 | 2 | 1 | 4 |

## Independent-binomial references, not design-adjusted intervals

| Backend / condition | Pass /20 | Wilson95 reference |
|---|---:|---:|
| Sol / primitives | 20/20 | 83.9%–100.0% |
| Sol / macro | 20/20 | 83.9%–100.0% |
| Qwen / primitives | 15/20 | 53.1%–88.8% |
| Qwen / macro | 14/20 | 48.1%–85.5% |

Wilson intervals assume an independent-binomial model. They ignore pairing and family dependence here; they are not the final uncertainty, a guaranteed lower bound on it, or a proof of reliability preservation. The formula follows the [NIST proportions reference](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

## Whole-family resampling sensitivity

Resample ten entire families with replacement10,000 times, seed20261027. Preserve both repetitions and paired conditions within each family. Report linear-interpolated 2.5th/97.5th percentiles. This explores dependence on the observed family mix; these ranges are not calibrated population guarantees for unseen robots/tasks. In particular, resampling Sol's all-success observations cannot invent unseen failures. Its degenerate zero correctness-difference range must not be read as certainty of equivalence.

| Backend | Metric / cohort | 95% empirical family-resampling range | Valid draws |
|---|---|---:|---:|
| Sol | primary_difference_percentage_points | 0.0 to 0.0 | 10000 |
| Sol | all_attempts:requests_reduction_percent | 33.3 to 52.5 | 10000 |
| Sol | both_pass_pairs:requests_reduction_percent | 33.3 to 52.5 | 10000 |
| Sol | both_pass_pairs:task_seconds_reduction_percent | 26.2 to 49.1 | 10000 |
| Qwen | primary_difference_percentage_points | -30.0 to 15.0 | 10000 |
| Qwen | all_attempts:requests_reduction_percent | 25.0 to 53.9 | 10000 |
| Qwen | both_pass_pairs:requests_reduction_percent | 33.3 to 59.2 | 10000 |
| Qwen | both_pass_pairs:task_seconds_reduction_percent | 27.1 to 64.7 | 10000 |

Correctness difference is macro minus primitives, in percentage points. Resource reduction is100×(1−macro/primitive). A zero denominator is omitted from that metric's draws, not replaced with zero benefit. Matched-success resampling remains conditional on both systems passing; it does not recover costs on discordant cases.

Whole-cluster resampling and the difficulty of inference with few clusters are discussed by [Cameron and Miller](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf). That methodological source does not validate our designed task suite as a random sample.

The exact exploratory family sign-flip sensitivity gives two-sided p=1.0 for both backends (Sol has no observed correctness variation; Qwen has only two families with nonzero condition differences). This relies on an unestablished exchangeability assumption and is not a population-level hypothesis-test result. It supplies no evidence of equivalence, no proof of noise, and no reason to overturn the failed Qwen engineering screen. No multiple exploratory statistics were used to select a favorable claim or rerun tasks.
