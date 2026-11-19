# M4 final efficiency and timing

Date: **2026-11-05**. Derived from saved trial rows; no new inference.

Positive reduction means less resource use or time in macro mode. Correctness and
review completeness must be considered alongside savings. Partial runs are not final results.

| Backend / condition | Recorded /20 | Audited automatic passes | Requests | Native ops | Known input tokens | Known output tokens | Incomplete-usage rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sol / primitives | 20/20 | 20 | 68 | 38 | 95,333 | 2,221 | 0 |
| Sol / macro | 20/20 | 20 | 38 | 40 | 48,754 | 1,145 | 0 |
| Qwen / primitives | 20/20 | 15 | 91 | 50 | 207,958 | 19,445 | 0 |
| Qwen / macro | 20/20 | 14 | 53 | 48 | 105,779 | 12,519 | 0 |

| Backend / condition | Total recorded task seconds | Mean seconds/task | Median seconds/task |
|---|---:|---:|---:|
| Sol / primitives | 328.36 | 16.42 | 13.18 |
| Sol / macro | 194.58 | 9.73 | 8.57 |
| Qwen / primitives | 2,669.72 | 133.49 | 117.59 |
| Qwen / macro | 1,703.63 | 85.18 | 46.53 |

These tables include unsuccessful recorded attempts. An early failure can look fast
or cheap. They exclude any request still in flight without a recorded task result;
the master checkpoint separately reports campaign reservations. Unknown token usage
is not zero; known totals are lower bounds where usage is incomplete.

## Same-case pairs where both conditions passed

This descriptive subset requires both audits and valid recorded clarification reviews
when applicable. Pending/failed clarification reviews exclude that pair. It supplements
all-attempt accounting and is not the final frozen engineering-screen decision.

| Backend | Saved status | Qualifying pairs /20 | Requests primitives → macro | Request reduction | Native ops primitives → macro | Native reduction | Task seconds primitives → macro | Time reduction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Sol | COMPLETE | 20/20 | 68 → 38 | +44.1% | 38 → 40 | -5.3% | 328.36 → 194.58 | +40.7% |
| Qwen | COMPLETE | 13/20 | 53 → 28 | +47.2% | 31 → 29 | +6.5% | 1,417.23 → 696.76 | +50.8% |

## Campaign time and measurement limits

- Sol: **17.68 minutes** (1,060.78 seconds), closed backend run.
- Qwen: **81.97 minutes** (4,918.20 seconds), closed backend run.

Task wall time covers the bounded model/tool loop, including waits and recovery.
It excludes simulator setup/reset, outside-task independent scoring observations and
persisted trace audits. Backend elapsed time also includes those overheads and, when
closed, cleanup; it does not include waiting for the other backend's serialized turn.
Means and medians cover recorded rows only; incomplete trials can distort comparisons.
All-attempt costs and final reporting must retain infrastructure-censored attempts too.

Compare architecture within each backend first. Qwen runs on the laptop with partial
CPU/GPU offload; Sol uses a remote service with different sampling, tokenization and
compute. Observed elapsed-time differences describe this setup, not a controlled
hardware-independent model-speed ranking. No energy, dollar cost or pure generation
tokens/second was measured by these task-wall aggregates.

Regenerate with `python -m tools.project_context --refresh`. The frozen experiment
runner and trial scores remain unchanged. Derived reports reflect the saved review overlay.

Execution and all required reviews are complete. See the
[final M4 report](../artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md)
for the screen decision: Sol passes; Qwen fails the correctness condition despite savings.
