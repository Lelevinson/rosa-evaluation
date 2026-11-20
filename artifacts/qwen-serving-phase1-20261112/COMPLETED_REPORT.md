# Qwen serving Phase 1: completed results

Date: **2026-11-13**.

**Completed A/B replay screen.** These are known-input serving observations, not new robotic task scores. M4, Baseline v1 and M1-M5 results are preserved.

B reached **0.963 times A throughput** against the prespecified 1.5-times requirement. Its family tool-call agreement was **7/10** against the 9/10 requirement. The candidate screen **failed**. See [recorded Stage 2 decision](stage2-decision.json) for why C was not run.

## Design and accounting

A: original auto/enabled Flash Attention, f16 KV, 8192 context. B: explicit enabled Flash Attention, q8_0 K/V, same 8192 context. Ollama 0.40.6, Qwen3.5:9b Q4_K_M, temperature 0, seed 42, think=false, 1024 generated-token cap per call, same recorded messages/tools and server prefix-cache policy. Ten first-turn family inputs plus the 4027-token longest-input safety fixture; three predetermined repeats. Primary throughput is the median of the eleven unique inputs, excluding repeats and warm-ups.

Actual cost: **31 charged requests, 52447 input tokens, 6384 returned output tokens, zero unreturned requests**. No robot tool dispatches, hosted model calls or OAuth operations. The original 45-request ceiling was retained. Reservation filenames are not chronological: 31 is the recovery warm-up; the later B measured requests occupy 17-30. Count files, not the largest filename.

The original B warm-up returned successfully, but the observer wrongly required the literal log phrase `Flash Attention enabled`. B instead records `flash_attn = enabled`; both K and V were q8_0. The first segment stopped on this validator error. Original sources, outputs and the failed status/report are retained. A separately frozen observer correction continued only unstarted B measured requests, with one additional discarded warm-up. Thus A has 15 returned requests and B has 16; each has 14 measured. This is a declared infrastructure deviation, not a clean uninterrupted original-protocol run. The frozen automatic report still labels its denominator /15; this closeout supplies the actual accounting. The fixed global deadline included the interruption. If B had passed, the full 15-request C block would not have fitted the remaining 14 slots.

## Serving and behavior results

| Measure | A | B |
|---|---:|---:|
| Returned requests | 15 | 16 |
| Measured requests | 14 | 14 |
| Unique-input median generation tokens/s | 8.388 | 8.082 |
| Unique-input minimum tokens/s | 7.796 | 7.652 |
| Unique-input maximum tokens/s | 10.142 | 8.863 |
| Historical family-call matches /10 | 10 | 7 |
| Repeat agreements /3 | 3 | 3 |
| Measured output-cap hits /14 | 0 | 0 |

B versus A family agreement: 7/10; safety-input agreement: False; prompt-equivalence/output-room check: True. Agreement compares parsed ordered tool names and arguments, excluding IDs. An empty-call match is not proof of correct prose, and matching a wrong historical call is not success. All mismatches, including repeats, appear in [full output comparisons](MISMATCHES.md).

## Hardware and costs

| Measure | A | B |
|---|---|---|
| GPU offload layers | [17, 33] | [17, 33] |
| GPU KV allocation MiB | 128.0 | 68.0 |
| Warm-up model-load seconds | 13.3554351 | 13.6671824 |
| Effective KV precision | f16 | q8_0 |

A physical NVIDIA observation after warm-up (not a peak or directly synchronized pair):
```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%], temperature.gpu, clocks.current.sm [MHz], power.draw [W]
NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 4963 MiB, 959 MiB, 12 %, 51, 480 MHz, 10.25 W
```

B physical NVIDIA observation after warm-up (not a peak or directly synchronized pair):
```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%], temperature.gpu, clocks.current.sm [MHz], power.draw [W]
NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 4915 MiB, 1007 MiB, 0 %, 49, 255 MHz, 6.88 W
```

The GPU KV saving was 60 MiB; the offloaded layer count did not increase. Physical used/free readings include desktop and other allocations and are snapshots. Ollama ps reports an allocation estimate, not an independent measurement of physical residency.

| Measured-block cost, 14 requests each | A | B |
|---|---:|---:|
| input_tokens | 23687 | 23687 |
| output_tokens | 2212 | 3134 |
| client_seconds | 278.528 | 396.829 |
| total_duration_seconds | 289.886 | 414.462 |
| load_duration_seconds | 0.283 | 0.090 |
| prompt_eval_duration_seconds | 18.971 | 18.834 |
| eval_duration_seconds | 270.256 | 395.206 |
| invalid_call_records | 0 | 0 |
| multiple_tool_call_records | 0 | 0 |

For these fourteen replay requests, B generated 41.7% more output tokens. Summed measured client request time was 278.528 seconds for A and 396.829 seconds for B. These are replay-request totals, not completed robotic task times.

Provider total_duration and client monotonic timings remain distinct cost views. Their difference is not asserted to be exact framework overhead; Phase 0 recorded clock inconsistencies. Token totals also reflect different generated responses, not just serving speed. Warm-up-inclusive costs are retained in [cost-summary.json](cost-summary.json); every request is listed in [request-summary.csv](request-summary.csv).

## Matched request detail

| Ordinal / fixture | A tokens/s | B tokens/s | A output tokens | B output tokens | Parsed calls agree |
|---|---:|---:|---:|---:|---|
| 1: 02-move_constrained-r1-macro-call-1 (family) | 7.908 | 7.787 | 348 | 345 | True |
| 2: 03-already_satisfied-r1-macro-call-1 (family) | 8.756 | 7.885 | 109 | 259 | False |
| 3: 06-ineffective_command-r1-macro-call-1 (family) | 9.777 | 8.604 | 33 | 93 | False |
| 4: 07-partial_command-r1-macro-call-1 (family) | 10.142 | 7.652 | 33 | 732 | False |
| 5: 10-missing_prerequisite-r1-macro-call-1 (family) | 8.304 | 8.316 | 147 | 130 | True |
| 6: 11-inspect_healthy-r1-macro-call-1 (family) | 8.388 | 8.082 | 138 | 172 | True |
| 7: 14-inspect_inactive-r1-macro-call-1 (family) | 8.292 | 7.984 | 150 | 215 | True |
| 8: 15-inspect_missing_controllers-r1-macro-call-1 (family) | 8.763 | 8.163 | 103 | 161 | True |
| 9: 18-inspect_missing_joint-r1-macro-call-1 (family) | 8.994 | 8.863 | 83 | 83 | True |
| 10: 19-ambiguous_goal-r1-macro-call-1 (family) | 7.987 | 8.099 | 236 | 151 | True |
| 11: 08-partial_command-r1-primitives-call-8 (safety) | 7.796 | 7.975 | 110 | 125 | False |
| 12: 02-move_constrained-r1-macro-call-1 (repeat) | 7.793 | 7.759 | 348 | 345 | True |
| 13: 11-inspect_healthy-r1-macro-call-1 (repeat) | 8.297 | 8.037 | 138 | 172 | True |
| 14: 19-ambiguous_goal-r1-macro-call-1 (repeat) | 8.138 | 8.176 | 236 | 151 | True |

## Interpretation and limitations

This is a small exploratory screen on previously observed M4 inputs. It has one A block followed by B, an interruption/reload, and three stability repeats rather than independent repeated blocks. Order, thermals, cache history and response-content differences limit causal attribution. No confidence interval, general correctness claim, or Qwen/Sol parity claim is justified. Quantizing KV can change outputs despite unchanged weight digest. No reasoning-on, prompt repair, weight quantization change, Gazebo rerun or selection-scaffolding condition was tested.

Keep the original serving reference unless a separately justified experiment establishes a better configuration. A failed cheap-serving screen supports stopping this path under its gates; it does not establish the best possible Qwen configuration or a fixed model capability ceiling. Any future intent/schema/examples or thinking-mode study remains a separate prospective decision.

## Evidence protection

Checks passed: 950 protected M4 files, 62 M4 frozen sources, 93 Phase 0 manifest entries, 10 Phase 1 frozen files, 5 continuation files and 13 first-segment snapshot files. All returned usage counts match provider metadata; prompts retain expected counts and output room; reservation and output totals match the checkpoint. See [validation](closeout-validation.json). Owned model servers were confirmed stopped in [process check](post-run-process-check.json). Evidence remains local; no publication or Git push was performed.

See [original protocol](PROTOCOL.md), [continuation declaration](continuation/CONTINUATION_NOTE.md), [machine analysis](analysis.json), profile request/response/result records and owned-server logs.
