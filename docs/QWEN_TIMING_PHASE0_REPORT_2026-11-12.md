# ROSA Qwen timing investigation: Phase 0 report

Date: **2026-11-12**. Dated checkpoint for sharing with teammates, Claude or ChatGPT.

**Result:** archived analysis is complete for all 40 M4 Qwen trials and 144
requests. A clean completed live hardware baseline is **not obtained**. Two new
inference requests were charged: one returned under mismatched serving settings;
the authorized correction was stopped for unresolved GPU activity. No Phase 1
comparison, Sol request, Gazebo run or robot action occurred.

Use the [living Claude roadmap tracker](CLAUDE_QWEN_ROADMAP_LIVE.md) for subsequent
progress. This report describes this checkpoint; it must not be silently rewritten
to include later outcomes. The [full Phase 0 technical report](../artifacts/qwen-timing-probe-20261112/PHASE0_REPORT.md)
contains the 40-trial appendix and links to raw evidence.

## Purpose and boundaries

The project improves the software around ROSA's existing LLM backends. The broader
proposed objective is to bring local Qwen's verified correctness closer to the
hosted reference on a bounded task suite while measuring costs. This timing
investigation is a separate diagnostic: determine where Qwen's time goes, then
consider a small serving-configuration screen before returning to fresh correctness
experiments. Speed and first-call agreement do not establish robotic correctness.

M4 remains the original frozen study. M1-M5 findings, source freezes, raw results
and original reports were not revised. Existing Baseline v1 remains preserved.
The new probe files are under `artifacts/qwen-timing-probe-20261112/`.

## 1. Archived field inventory

All six requested Ollama fields exist in the retained metadata on **144/144
requests**. They are inside JSON strings in `ConfiguredChatOllama` trace spans,
not directly exposed as keys in the checkpoint ledger. Duplicate metadata copies
were not counted twice. Input/output usage matched all corresponding ledger entries.

| Field | Availability | Unit / interpretation |
|---|---|---|
| `total_duration` | 144/144, per call | Server nanoseconds |
| `load_duration` | 144/144, per call | Server nanoseconds |
| `prompt_eval_count` | 144/144, per call | Prompt token count |
| `prompt_eval_duration` | 144/144, per call | Server nanoseconds |
| `eval_count` | 144/144, per call | Generated token count |
| `eval_duration` | 144/144, per call | Server nanoseconds |
| `prompt_eval_cached_count` | Not recorded | No historical per-call count reconstructed |

Source: [field inventory](../artifacts/qwen-timing-probe-20261112/field-inventory.json)
and [144-call extraction](../artifacts/qwen-timing-probe-20261112/per-call.csv).
The proposed fallback of estimating old model time from a newly measured token
rate is unnecessary: direct historical server durations exist.

## 2. Recorded time costs

| Historical server component | Total seconds | Share of server request time |
|---|---:|---:|
| Generation | 4,223.744 | 95.60% |
| Prompt processing | 160.613 | 3.64% |
| Loading | 19.285 | 0.44% |
| Other server time | 14.323 | 0.32% |
| **Total** | **4,417.966** | **100%** |

Median per-call historical generation throughput was **7.807 tokens/s**. This is
an archive-derived measurement, not a new speed result. Generation, rather than
prompt processing, dominates the retained server durations.

The timer sources disagree and cannot be forced into one additive decomposition:

| Recorded view | Total seconds |
|---|---:|
| Task durations, WSL monotonic timer | 4,373.357 |
| Native-operation interval union, same monotonic clock | 36.489 |
| Task minus native, non-native elapsed estimate | 4,336.868 |
| Trace root timestamp durations | 4,469.190 |
| Trace LLM timestamp durations | 4,422.413 |
| Trace native timestamp intervals | 37.484 |
| Trace root minus LLM and native intervals | 9.293 |

The monotonic task timer surrounds the invocation and trace finalization, yet its
total is shorter than the trace-root total. Server durations also exceed task
durations. The existing records do not establish the physical cause of these clock
differences. They must be reported separately; negative framework overhead must
not be invented by subtracting incompatible clock totals. No retrospective
correction was applied to the original M4 task-time figures.

Native time includes recorded read/write waits. It excludes outside-task setup,
reset and independent observations. A nominal movement wait was not added to a
failed task that never dispatched movement.

## 3. Regression and ending-type analysis

Descriptive fit: `seconds = intercept + b_output * output_tokens + b_input * input_tokens`.

| Unit / dependent variable | n | Intercept s | Output coefficient s/token | Input coefficient s/token | R squared | Predictor correlation |
|---|---:|---:|---:|---:|---:|---:|
| Trial task time | 40 | -4.07839 | 0.133405 | 0.000868 | 0.99314 | 0.83159 |
| Trial task minus native time | 40 | -4.36696 | 0.135548 | 0.000570 | 0.99405 | 0.83159 |
| Call server total time | 144 | -1.77991 | 0.138988 | 0.000738 | 0.99059 | 0.31136 |

These are associations, not causal cost coefficients. Trial predictors are
strongly correlated; turns and repeated cases are dependent. Prompt token counts
can include reused prefixes, so the input coefficient is not uncached prefill
speed. Negative intercepts are fit artifacts. No independent-sample significance
or generalized latency prediction is claimed. Additional fits are in
[regressions.json](../artifacts/qwen-timing-probe-20261112/regressions.json).

| Final ending type | Trials | Mean task seconds | Total task seconds | Share of Qwen task time |
|---|---:|---:|---:|---:|
| Correct under frozen scoring | 29 | 88.540 | 2,567.658 | 58.71% |
| Wrong skill/goal with accepted report | 5 | 71.356 | 356.781 | 8.16% |
| Response-length stop | 5 | 244.104 | 1,220.522 | **27.91%** |
| Validation-retry exhaustion | 1 | 228.396 | 228.396 | 5.22% |

Ending labels describe the final state; they do not isolate the initial cause.
Selection and commitment problems can precede a length stop. The five accepted
readiness reports did not satisfy the frozen requested-goal criterion; the other
six failed trials ended in errors. Eleven failures must not be described as eleven
false SUCCESS reports.

## 4. All attempts and matched-success comparison

| Subset / condition | Tasks | Correct | Mean task s | Mean calls | Mean input tokens/task | Mean output tokens/task |
|---|---:|---:|---:|---:|---:|---:|
| All / primitives | 20 | 15 | 133.486 | 4.550 | 10,397.90 | 972.25 |
| All / macro | 20 | 14 | 85.182 | 2.650 | 5,288.95 | 625.95 |
| Both-pass / primitives | 13 | 13 | 109.018 | 4.077 | 8,812.00 | 787.00 |
| Both-pass / macro | 13 | 13 | 53.597 | 2.154 | 3,759.38 | 396.08 |

The 13 both-pass pairs condition on success and exclude failures. They cannot
erase the all-attempt correctness difference. Input totals per task sum across
calls; they are not single-request context lengths. See the
[matched-comparison CSV](../artifacts/qwen-timing-probe-20261112/matched-comparison.csv).

## 5. Historical configuration and memory headroom

Historical M4 sources show:

- Ollama **0.40.6**, `qwen3.5:9b`, Q4_K_M; full digest
  `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
- Request context **8192**, output maximum **1024/call**, temperature **0**, seed
  **42**, thinking disabled. This is one fixed profile, not Qwen's proven optimum.
- **17/33 layers** offloaded; CPU model buffer **2553.89 MiB**, GPU model buffer
  **2803.99 MiB**.
- Runtime **Flash Attention enabled**. Historical launch used `--flash-attn auto`.
- f16 KV cache: **128 MiB GPU + 128 MiB CPU**. Recurrent state is a separate
  allocation; it must not be treated as ordinary context-scaled KV cache.
- Server prompt caching was active. LangChain `cache=False` disables its response
  cache; it does not establish that the server prompt cache was disabled.
- LangChain `streaming=False` still used internally streamed Ollama transport
  assembled into one response. It did not set API `stream=false` in this adapter.

The actual maximum prompt across both conditions was **4027 tokens**, not 3928.
It came from repetition-1 primitive `partial_command`, call 8. A 4096 context
would not leave room for a possible 1024-token output.

For the proposed B and C profiles, nominal q8_0 storage yields about **60 MiB**
GPU KV savings at 8192 context, or **77 MiB** with q8_0 at 6144 context, compared
with the historical 128 MiB f16 GPU KV buffer. These are illustrative estimates
assuming unchanged placement; alignment, backend support and other buffers can
change actual results. They cannot bridge roughly 2.5 GiB of CPU model weights.
They also do not prove zero possible layer movement or runtime benefit. No
headroom-based claim of impossibility or measured speed improvement is justified.

See [historical log excerpts](../artifacts/qwen-timing-probe-20261112/historical-server-log-excerpts.json)
and [headroom assumptions](../artifacts/qwen-timing-probe-20261112/headroom-estimates.json).

## 6. Every live/setup attempt and its disposition

| Attempt | Generation requests charged | Observation | Disposition |
|---|---:|---|---|
| hardware-01 | 0 | Version/digest verified; incorrect local assertion expected API stream=false | Stopped before invocation; logs retained |
| hardware-02 | 0 | PowerShell loop variable collided with a case-insensitive validated parameter | Stopped before client launch; logs retained |
| hardware-03 | 1 | 33 returned tokens; explicit FA=false disabled FA; 16/33 offload | Serving mismatch; excluded from matched baseline claims |
| hardware-04 | 1 | Owner-approved correction; auto FA enabled, f16, 8K, 17/33 offload | Stopped for unresolved GPU activity; no complete response |

The first two failures and the FA override were probe implementation errors,
not Qwen task failures. The cleanup command for hardware-03 also raised a
process-exit race/error; subsequent checks confirmed the owned server and runner
had exited. That warning was retained rather than describing the launcher as
having exited successfully.

**hardware-03:** the first parsed tool call selected inspection instead of the
historical `ur5e.stage_left`. Reported generation throughput was about 1.978
tokens/s, but FA was disabled and buffers differed. This is neither a valid M4
speed-regression result nor proof of failed reproducibility under matched serving.
The API/CLI estimated GPU allocation exceeded physical device capacity; the
27%/73% CPU/GPU display is not proof of actual physical residency. Physical readings
were retained separately: 5582 MiB used and 340 MiB free on a 6141 MiB device.

**hardware-04:** the owner approved exactly one additional request. Unity Editor
was closed, but GPU samples showed 24-40% use; a further engine sample included
Chrome video-decode/3D activity. The request was launched before that result was
fully reviewed. Adapter-specific absence of contention was not established, so
only the owned server/request tree was stopped conservatively. This preflight
ordering failure is an execution/protocol exception. No user's browser or other
application was closed by the probe.

Its client recorded `ReadError` after termination. The server log reached at
least **267 generated tokens**, but no final usage or complete response returned.
Interim generation rates are not a final throughput result. Final first-call
agreement, output-cap outcome, loaded CLI status and free VRAM while loaded were
not obtained for this corrected attempt. The observed runtime settings/offload
are valid partial observations; a clean completed baseline is still missing.

Both generation requests count. Accounting is **33 known returned output tokens
plus an unreturned request bounded by 1024 tokens**; the progress log is a lower
bound, not exact final usage. There were no automatic inference retries or robot
tool executions. Both authorized allowances are spent, and no further request
is scheduled. The original records were not replaced by a retry.

Sources: [first live observation](../artifacts/qwen-timing-probe-20261112/HARDWARE_CHECK_REPORT.md),
[corrected stopped observation](../artifacts/qwen-timing-probe-20261112/CORRECTED_HARDWARE_CHECK_REPORT.md),
[current status](../artifacts/qwen-timing-probe-20261112/status.json).

## 7. Conclusions and next decision

The strongest archived timing result is that generation dominates server request
time. Length-stop trials account for a substantial share of task time. This
supports investigating unnecessary output and bounded output handling, but does
not establish that any proposed intervention improves verified task correctness.

The assumed easy memory win is less convincing: historical FA was already enabled
and GPU KV cache was only 128 MiB. A large cache-driven speed improvement remains
unproven. The experiment must be allowed to conclude "no demonstrated benefit."

Before more live work, establish a quiet GPU interval, review all preflight results
**before** launch, and agree a new bounded allowance for a clean baseline check.
Then review the Phase 0 findings and explicitly confirm profiles, thresholds,
cache policy, profile order and resource limits before Stage 1. Original quoted
defaults and proposed B/C definitions are not a frozen or approved protocol.

No 30-request A/B screen, C test, lower-weight quantization, thinking-on condition,
prompt intervention or full-loop correctness study has run in this investigation.

## 8. Preservation and verification

At this checkpoint, **950 M4 files**, **62 frozen source files** and **34 retained
prior-attempt files** passed unchanged checks. The probe manifest verified **93
entries** at the preceding technical checkpoint. These counts identify that
verification, not a permanently fixed count after new documentation is added.
Both owned model/server trees were confirmed stopped. No credentials were read
or included, and no public upload or Git commit was made for this work.

The [detailed report](../artifacts/qwen-timing-probe-20261112/PHASE0_REPORT.md),
[per-trial table](../artifacts/qwen-timing-probe-20261112/per-trial.csv),
[per-call table](../artifacts/qwen-timing-probe-20261112/per-call.csv),
[analysis](../artifacts/qwen-timing-probe-20261112/analysis.json) and
[source integrity](../artifacts/qwen-timing-probe-20261112/source-integrity.json)
remain the evidence behind this recap. This dated report and the living tracker
add documentation; they launch no experiments and change no frozen scores.
