# M4 efficiency and timing checkpoint

Date: **2026-10-27**. Derived from saved trial rows; no new inference.

Positive reduction means less resource use or time in macro mode. Correctness and
review completeness must be considered alongside savings. Partial runs are not final results.

| Backend / condition | Recorded /20 | Audited automatic passes | Requests | Native ops | Known input tokens | Known output tokens | Incomplete-usage rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sol / primitives | 20/20 | 20 | 68 | 38 | 95,333 | 2,221 | 0 |
| Sol / macro | 20/20 | 20 | 38 | 40 | 48,754 | 1,145 | 0 |
| Qwen / primitives | 16/20 | 12 | 67 | 39 | 145,860 | 13,383 | 0 |
| Qwen / macro | 17/20 | 13 | 41 | 37 | 76,468 | 9,301 | 0 |

| Backend / condition | Total recorded task seconds | Mean seconds/task | Median seconds/task |
|---|---:|---:|---:|
| Sol / primitives | 328.36 | 16.42 | 13.18 |
| Sol / macro | 194.58 | 9.73 | 8.57 |
| Qwen / primitives | 1,845.61 | 115.35 | 57.20 |
| Qwen / macro | 1,274.92 | 75.00 | 46.50 |

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
| Qwen | RUNNING | 11/20 | 42 → 23 | +45.2% | 25 → 24 | +4.0% | 1,040.19 → 562.86 | +45.9% |

## Campaign time and measurement limits

- Sol: **17.68 minutes** (1,060.78 seconds), closed backend run.
- Qwen: **60.97 minutes** (3,658.26 seconds), saved elapsed checkpoint; still incomplete.

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
runner, scores and original reports remain unchanged. The final M4 report should
include these measures using the completed schedule and required review overlay.
