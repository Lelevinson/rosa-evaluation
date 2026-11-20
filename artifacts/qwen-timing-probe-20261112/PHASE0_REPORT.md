# Qwen Phase 0 timing and serving assessment

Date: **2026-11-12**. Exploratory analysis separate from M4. **Archived analysis complete. Two live requests charged: one serving mismatch and one authorized correction stopped for GPU activity. A clean live baseline remains incomplete; Phase 1 not started.**

Two Qwen inference requests charged for the hardware work: one returned under mismatched settings and one stopped for unresolved GPU activity. Zero Sol requests, robot commands or simulator runs. No M4 files, frozen sources or M1-M5 reports changed. All new outputs are in this directory. The pre-run note and hash receipt precede any live request.

## Main findings

- All six requested Ollama timing/count fields exist on **144/144 calls**, across **40 trials**. Cached-token count is **not recorded** in the retained per-call metadata.
- Generation is **95.60%** of server-reported request duration. Historical median generation throughput is **7.807 tokens/s**. This is historical recorded throughput, not a new hardware measurement.
- Historical server startup shows **17/33 layers offloaded**, effective **Flash Attention enabled**, and **f16 K/V cache**. The startup environment flag alone would have been misleading: it said false while the runtime reported auto/enabled.
- The GPU KV buffer was only **128 MiB**. Estimated q8_0 savings are about **60 MiB** at 8192 context, or **77 MiB** with q8_0 at 6144 context. Those do not eliminate roughly 2554 MiB of CPU model weights. They do not establish zero possible speed gain.
- Five response-length-stop trials consumed **27.91%** of recorded Qwen task time. Reducing unneeded generation is a substantial engineering target, but a shorter output is only useful if goal correctness is retained.

## 0.1 Field inventory

| Field | Calls recorded | Granularity |
|---|---:|---|
| `total_duration` | 144/144 | Per call |
| `load_duration` | 144/144 | Per call |
| `prompt_eval_count` | 144/144 | Per call |
| `prompt_eval_duration` | 144/144 | Per call |
| `eval_count` | 144/144 | Per call |
| `eval_duration` | 144/144 | Per call |
| `prompt_eval_cached_count` | 0/144 | Not recorded |

Source: each `ConfiguredChatOllama` span, JSON-decoded `attributes.output.value`, `generations[0][0].generation_info`. Metadata also appears in the message response; that duplicate is not an extra observation. Counts and usage were checked against all 144 inference-ledger entries.

The historical server log shows prompt reuse/checkpoints, but no per-call cached-token count was reconstructed from it. LangChain `cache=False` controls client response caching; it did **not** disable the server prompt/KV cache. Preserve this distinction in future comparisons.

## 0.2-0.3 Time decomposition and clock reconciliation

| Ollama server component | Total seconds | Share of server total |
|---|---:|---:|
| Generation | 4223.744 | 95.60% |
| Prompt processing | 160.613 | 3.64% |
| Loading | 19.285 | 0.44% |
| Other server time | 14.323 | 0.32% |
| **Total server requests** | **4417.966** | **100%** |

Server other time = total minus generation, prompt processing and loading. It is not total ROSA overhead. Ollama durations are converted from nanoseconds.

| Recorded clock/boundary | Seconds |
|---|---:|
| Task duration: WSL `time.monotonic()` | 4373.357 |
| Native operation union: snapshot monotonic intervals | 36.489 |
| Task minus native: non-native elapsed estimate, not pure inference | 4336.868 |
| OpenTelemetry root timestamp duration | 4469.190 |
| OpenTelemetry LLM timestamp durations | 4422.413 |
| OpenTelemetry native timestamp interval union | 37.484 |
| Root minus LLM and native timestamp intervals | 9.293 |

The trace root timestamps and task monotonic records also disagree, not just client versus server. The task timer surrounds invocation plus trace finalization; the shorter monotonic total cannot be explained by calling server duration task time. These are uncalibrated clock domains. The archives do not identify the physical cause; clock-rate/adjustment explanations are hypotheses. Preserve each recorded measurement and do not subtract server totals from monotonic task time to manufacture negative overhead. The trace-timestamp decomposition is a separate view, not a correction of frozen task metrics.

Native time includes actual waits inside dispatched reads/writes. Setup/reset and the independent observer outside the task are excluded. Failed tasks often dispatch no movement. Do not insert a nominal trajectory wait when no command ran.

## 0.4 Descriptive regressions

Model: seconds = intercept + b_output * output tokens + b_input * input tokens. Negative intercepts are descriptive fit artifacts, not physical startup times.

| Unit/outcome | n | Intercept s | b_output s/token | b_input s/token | R squared | Input/output r |
|---|---:|---:|---:|---:|---:|---:|
| task_seconds | 40 | -4.07839 | 0.133405 | 0.000868 | 0.99314 | 0.83159 |
| task_minus_native_seconds | 40 | -4.36696 | 0.135548 | 0.000570 | 0.99405 | 0.83159 |
| total_seconds | 144 | -1.77991 | 0.138988 | 0.000738 | 0.99059 | 0.31136 |
| client_span_seconds | 144 | -1.76280 | 0.138789 | 0.000765 | 0.99040 | 0.31136 |
| eval_seconds | 144 | -3.48958 | 0.137912 | 0.001014 | 0.99596 | 0.31136 |

Trial-level predictors are strongly correlated (r=0.832); do not interpret separate slopes as isolated costs. Call-level correlation is lower (r=0.311), but calls are clustered in trials and repeated families. Input counts include reused prompt prefixes, so input-token slopes do not measure uncached prefill speed. No causal claim, independent-sample significance test or extrapolated speed prediction is made.

## 0.5 Final ending types

| Ending | Trials | Mean task s | Total task s | Share of total |
|---|---:|---:|---:|---:|
| correct | 29 | 88.540 | 2567.658 | 58.71% |
| wrong_skill_or_goal | 5 | 71.356 | 356.781 | 8.16% |
| response_length_stop | 5 | 244.104 | 1220.522 | 27.91% |
| validation_retry_exhaustion | 1 | 228.396 | 228.396 | 5.22% |

These are mutually exclusive **ending labels**, not mutually exclusive causes. Selection/commitment errors can precede length stops. Wrong skill/goal covers five accepted readiness reports that did not meet the frozen user-goal criterion; it does not mean every one of eleven failures was a false success.

## 0.6 All attempts and matched both-pass subset

| Subset / condition | n | Correct | Mean task s | Mean calls | Mean input tokens | Mean output tokens |
|---|---:|---:|---:|---:|---:|---:|
| all_attempts / primitives | 20 | 15 | 133.486 | 4.550 | 10397.90 | 972.25 |
| all_attempts / macro | 20 | 14 | 85.182 | 2.650 | 5288.95 | 625.95 |
| both_pass_pairs / primitives | 13 | 13 | 109.018 | 4.077 | 8812.00 | 787.00 |
| both_pass_pairs / macro | 13 | 13 | 53.597 | 2.154 | 3759.38 | 396.08 |

Both-pass = 13 matched family/repetition pairs. This conditional subset excludes failures and cannot establish an unconditional reliability advantage. Per-task input totals sum across calls, not context length.

## Historical hardware/settings versus current hardware

Historical sources: retained `outside-task-ollama-status.json` for all 40 Qwen trials, pinned preflight, and the original M4 server log. Relevant log lines and its SHA-256 are retained in `historical-server-log-excerpts.json`.

- Model: qwen3.5:9b Q4_K_M, Ollama 0.40.6; digest `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
- Runtime context 8192; offload 17/33 layers; CPU model buffer 2553.89 MiB; GPU model buffer 2803.99 MiB.
- f16 KV buffers: CPU 128 MiB + GPU 128 MiB; recurrent state CPU/GPU about 25.13 MiB each. A separate vision projector was loaded even for these text requests; the log describes its model size as 878.99 MiB. Do not assume every auxiliary byte is captured in a layer count.
- Runtime Flash Attention explicitly enabled. Server prompt cache explicitly enabled. The server context default 4096 did not override the request context 8192.
- 40 historical loaded-model records. Unique (loaded size, size_vram, context, digest) configurations: 1. Loaded-model size and device allocation are not disk weight sizes or GPU compute percentages. Full source records are provided.
- Historical free VRAM while loaded and an `ollama ps` PROCESSOR text line: **not recorded in these trial-status files**. The server log contains allocation/fitter diagnostics but no new post-hoc measurement is substituted.

Initial preflight found Unity Editor processes and deferred the live check. After the owner closed Unity, a fresh check cleared that gate. One request returned but the effective FA configuration did not match M4. The measured values and mismatch are appended below. No unrelated application was stopped by the probe.

The PATH-installed Ollama client is 0.24.0 rather than the project pin. Its status command attempted an automatic app startup, failed on denied external log writes and returned no server status. No model request was sent. Use the pinned binary/API for a later check; do not upgrade or replace the historical pin.

## Headroom screen and proposed profiles

The following are **proposals awaiting confirmation**, not measured configurations:

| Profile | Context | Effective FA | KV cache | Estimated GPU KV saving versus historical A |
|---|---:|---|---|---:|
| A | 8192 | historical auto/enabled, verify | f16 | 0 MiB |
| B | 8192 | explicit on, verify | q8_0 | about 60 MiB |
| C, gated | 6144 | explicit on, verify | q8_0 | about 77 MiB |

Estimate assumes unchanged placement and nominal q8_0 block storage (34 bytes per 32 values versus f16 64). The format definition is documented in the [GGML source](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h); [Ollama documents cache quantization](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache). These current references explain the estimate, not verified support in the pinned runtime. Alignment, backend support, graph buffers, auxiliary/recurrent allocations and relocation can change actual results. The historical fitter displayed a roughly 155 MiB difference between candidate adjacent placements, but layers are heterogeneous; this is not a universal one-layer threshold. Savings clearly cannot move all CPU weights to GPU. They do not prove that zero layers can move or that direct runtime effects cannot help. A definitive no-benefit headroom stop is not established from memory arithmetic alone.

The longest recorded prompt was **4027 tokens**, primitive partial_command repetition 1 call 8. A 4096 context cannot accommodate that plus the possible 1024-token response; C=6144 is proposed instead. This safety input is a later-turn input, not a first-turn selection task.

## What must be established before live Stage 1

1. **Partly completed:** Unity Editor closed, one request returned, pinned version/digest verified, isolated server stopped. Effective FA differed from M4; corrected hardware observation requires approval before another inference.
2. Confirm A/B definitions and whether a roughly 60 MiB saving justifies the small screen. FA already being enabled removes one presumed source of benefit.
3. Confirm thresholds: proposed >=1.5x median generation throughput, >=9/10 first-call agreement on family inputs, no newly truncated prompts, no increase in cap hits. The context-safety input is separate, and every mismatch is disclosed. Agreement preserves errors too; it is not correctness.
4. Freeze server cache/keep-alive policy, profile order and thermal/background controls. Repeated prompts may benefit from server prefix reuse even with client cache disabled. Record effective settings and all timing fields per request.
5. Freeze the 11-input manifest and three repeated cases already proposed before any new output: movement, healthy inspection, ambiguous request. A/B = 30 calls including warm-ups, no automatic inference retries; choose explicit external per-call/batch deadlines and a charged token ceiling before launch.

C is conditional; D is unscheduled and would change weight quantization/digest. No automatic progression to Phase 1. No new speed or reliability claim follows from first-call agreement.

## Per-trial appendix

The CSV contains additional decompositions and raw identifiers. Times below retain the original task timer.

| Trial | Ending | Calls | Input | Output | Task s | Native s |
|---|---|---:|---:|---:|---:|---:|
| 01-move_constrained-r1-primitives | correct | 7 | 18709 | 1213 | 194.895 | 4.016 |
| 02-move_constrained-r1-macro | correct | 2 | 4047 | 627 | 95.444 | 4.017 |
| 03-already_satisfied-r1-macro | correct | 3 | 5982 | 732 | 103.462 | 0.016 |
| 04-already_satisfied-r1-primitives | correct | 5 | 12603 | 1712 | 243.130 | 0.014 |
| 05-ineffective_command-r1-primitives | correct | 6 | 15755 | 1225 | 177.730 | 4.024 |
| 06-ineffective_command-r1-macro | correct | 2 | 3753 | 269 | 42.917 | 4.015 |
| 07-partial_command-r1-macro | wrong_skill_or_goal | 4 | 8920 | 1183 | 182.261 | 0.023 |
| 08-partial_command-r1-primitives | correct | 8 | 22924 | 1354 | 191.547 | 4.022 |
| 09-missing_prerequisite-r1-primitives | response_length_stop | 6 | 15355 | 2048 | 286.837 | 0.032 |
| 10-missing_prerequisite-r1-macro | response_length_stop | 5 | 12099 | 2048 | 278.215 | 0.009 |
| 11-inspect_healthy-r1-macro | correct | 2 | 3193 | 304 | 39.856 | 0.009 |
| 12-inspect_healthy-r1-primitives | correct | 3 | 4980 | 423 | 56.996 | 0.008 |
| 13-inspect_inactive-r1-primitives | correct | 3 | 4934 | 450 | 55.491 | 0.008 |
| 14-inspect_inactive-r1-macro | correct | 2 | 3205 | 331 | 42.086 | 0.007 |
| 15-inspect_missing_controllers-r1-macro | correct | 2 | 3167 | 374 | 46.503 | 0.007 |
| 16-inspect_missing_controllers-r1-primitives | correct | 3 | 4941 | 456 | 57.460 | 0.007 |
| 17-inspect_missing_joint-r1-primitives | correct | 3 | 4836 | 367 | 45.592 | 0.002 |
| 18-inspect_missing_joint-r1-macro | correct | 2 | 3163 | 299 | 37.035 | 0.002 |
| 19-ambiguous_goal-r1-macro | wrong_skill_or_goal | 2 | 3144 | 278 | 34.254 | 0.007 |
| 20-ambiguous_goal-r1-primitives | wrong_skill_or_goal | 3 | 4934 | 424 | 52.884 | 0.009 |
| 21-inspect_healthy-r2-macro | correct | 2 | 3088 | 170 | 21.385 | 0.010 |
| 22-inspect_healthy-r2-primitives | correct | 3 | 4965 | 403 | 49.556 | 0.009 |
| 23-inspect_inactive-r2-primitives | correct | 3 | 4931 | 444 | 54.036 | 0.007 |
| 24-inspect_inactive-r2-macro | correct | 2 | 3205 | 415 | 52.266 | 0.009 |
| 25-inspect_missing_controllers-r2-macro | correct | 2 | 3165 | 375 | 46.556 | 0.007 |
| 26-inspect_missing_controllers-r2-primitives | correct | 3 | 4941 | 461 | 57.398 | 0.007 |
| 27-inspect_missing_joint-r2-primitives | correct | 3 | 4834 | 364 | 47.902 | 0.002 |
| 28-inspect_missing_joint-r2-macro | correct | 2 | 3163 | 282 | 35.354 | 0.001 |
| 29-ambiguous_goal-r2-macro | wrong_skill_or_goal | 2 | 3144 | 278 | 34.917 | 0.008 |
| 30-ambiguous_goal-r2-primitives | wrong_skill_or_goal | 3 | 4931 | 418 | 52.465 | 0.008 |
| 31-move_constrained-r2-primitives | response_length_stop | 5 | 11287 | 1621 | 221.691 | 0.009 |
| 32-move_constrained-r2-macro | correct | 2 | 4045 | 608 | 84.411 | 4.016 |
| 33-already_satisfied-r2-macro | correct | 3 | 5985 | 728 | 97.999 | 0.017 |
| 34-already_satisfied-r2-primitives | correct | 5 | 12333 | 1445 | 198.322 | 0.016 |
| 35-ineffective_command-r2-primitives | correct | 6 | 15794 | 1268 | 178.723 | 4.021 |
| 36-ineffective_command-r2-macro | correct | 2 | 3756 | 243 | 35.894 | 4.017 |
| 37-partial_command-r2-macro | response_length_stop | 3 | 6058 | 1276 | 164.422 | 0.011 |
| 38-partial_command-r2-primitives | correct | 7 | 18766 | 1301 | 177.712 | 4.017 |
| 39-missing_prerequisite-r2-primitives | response_length_stop | 6 | 15205 | 2048 | 269.358 | 0.010 |
| 40-missing_prerequisite-r2-macro | validation_retry_exhaustion | 7 | 19497 | 1699 | 228.396 | 0.032 |

## Files and reproducibility

- `analyze.py`: offline extraction, all ledger/trace usage checks, source/freeze preservation checks; no network calls.
- `render_report.py`: renders this report from extraction outputs.
- `field-inventory.json`, `per-trial.csv`, `per-call.csv`, `ending-type-summary.csv`, `matched-comparison.csv`, `regressions.json`, `analysis.json`.
- `historical-loaded-status.json`, `historical-server-log-excerpts.json`, `current-hardware-preflight.json`, `headroom-estimates.json`.
- `replay-inputs.json`: 20 first-turn inputs plus the actual maximum-length later-turn input, preserving decoded messages/tools and original outputs; source hashes included. Not held-out material.
- `proposed-stage1-inputs.json`, `PRE_RUN_NOTE.md`, `pre-run-note.sha256.json`, `source-integrity.json`, `protected-m4-before.json`.

Regenerate locally from the workspace root:

```powershell
python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/analyze.py
python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/render_report.py
python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/hardware_report.py
python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/corrected_hardware_report.py
```

No Git commit, public upload or automatic progression was performed. Two Qwen hardware-check requests were charged; one returned and one was stopped before a complete response. Existing research results remain unchanged.

## Phase 0 live observation: serving mismatch retained

Date: **2026-11-12**. Unity Editor processes had closed; only desktop GPU use remained in the captured inventory. WSL had no Gazebo/experiment worker. A separate hidden pinned server ran on the WSL-private address, port 11436, and was stopped after collection.

**Exactly one inference request** returned; 33 generated tokens, finish reason `stop`. No robot tools ran. Stage 1 remains unstarted. **This is not a matched M4 baseline:** the probe incorrectly used an explicit false environment override, disabling Flash Attention. Historical M4 used unset/auto and effective FA enabled. An additional corrected check requires approval; no second inference was made.

| Current measured item | Value |
|---|---|
| Ollama | 0.40.6 |
| Model | qwen3.5:9b Q4_K_M |
| Model digest | `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`; matches M4 |
| Context | 8192 |
| Offload | 16/33 layers |
| Loaded allocation size from API ps | 11089655886 bytes (10.328 GiB) |
| GPU allocation from API ps | 8071445216 bytes (7.517 GiB) |
| Effective FA / f16 KV / server prompt cache | False / True / True |
| GPU KV buffer | 128.0 MiB |
| CPU model buffer | 2671.19 MiB |
| Expected / observed prompt tokens | 1691 / 1691 |
| Generated tokens | 33 |
| Generation throughput | 1.978 tokens/s |
| Same parsed tool call(s) as historical input | False |

Pinned `ollama ps` output:

```text
NAME          ID              SIZE     PROCESSOR          CONTEXT    RUNNER      UNTIL                   
qwen3.5:9b    56671c2ab938    11 GB    27%/73% CPU/GPU    8192       llamacpp    About a minute from now
```

GPU before model load:

```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%]

NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 1173 MiB, 4749 MiB, 2 %
```

GPU immediately after request, model still loaded:

```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%]

NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 5582 MiB, 340 MiB, 0 %
```

**Memory reporting caveat:** API ps reports size_vram above the physical 6 GiB device capacity. Its 73% GPU display is retained verbatim, not accepted as proof of physical residency. nvidia-smi reports the actual device reading separately. The live log shows 16/33 layers and a 4657.81 MiB vision compute buffer, versus 17/33 and 248.10 MiB in the historical log. Do not add these heterogeneous allocations into a claimed physical VRAM total. Paging/overcommit explanations remain unverified.

| Current request component | Seconds |
|---|---:|
| total_duration | 61.118413 |
| load_duration | 37.284974 |
| prompt_eval_duration | 6.968455 |
| eval_duration | 16.682012 |
| Client monotonic elapsed | 59.744797 |

Cold-load time is included in this one request. Do not compare its total latency with M4 warm task means or infer a throughput regression/improvement from one observation. Serving mode, batch size, buffers and placement differ from M4. The first-call mismatch therefore does not establish a reproducibility failure under matched settings. This reading does not revise the historical 17/33 value.

The six original timing/count fields are recorded in the response. `prompt_eval_cached_count` is **not returned** for this request.

Adapter preflight discovered that LangChain `streaming=False` still uses internally streamed Ollama transport (`stream=true`); the response is assembled for the caller. This preserves the pinned adapter rather than silently switching wire behavior. `think=false` was verified. Client response cache=False and effective server prompt caching remain distinct.

Two setup errors preceded generation: an overly strict transport assertion and a PowerShell variable collision. Both stopped before inference reservation and sent zero generation requests. Their logs are retained; they are not Qwen failures. The third setup attempt performed the single globally reserved request. It then hit a cleanup-command race/error before writing the original final status. Post-run PID checks confirmed both owned server and runner had exited. That reconciliation is preserved separately, without claiming the launcher exited successfully. No inference was retried.

**Next decision:** approve or decline one additional corrected hardware request before considering Stage 1. The corrected launcher clears FA/cache environment overrides to reproduce the original unset/auto policy, and remains blocked by the existing global one-request reservation. See `SERVING_MISMATCH_AND_NEXT_CHECK.md`. This observation does not trigger Stage 1 or justify any serving improvement claim.

Evidence: `hardware-summary.json`, `hardware-03/`, `hardware-dispatch-reservation.json`, `PRE_RUN_AMENDMENT_01.md`, `SETUP_ATTEMPTS.md`. Full output and parsed calls are retained in `hardware-03/response.json` and `result.json`.

## Latest outcome: authorized corrected request stopped for GPU activity

**2026-11-12: the owner approved one additional corrected request. That allowance was used once and is now spent. Phase 1 remains unstarted.** This section supersedes earlier pending-approval and one-request-only status statements for the live hardware work; original observations remain retained.

Attempt hardware-04 used the original unset/auto Flash Attention policy. Its actual runtime log confirms **Flash Attention enabled**, **f16 KV cache**, **8192 context**, **17/33 layers offloaded**, and 512-sized runtime batches. Version and full model digest match M4. Those are direct partial hardware observations, not estimates.

The preflight GPU samples were 24%, 40% and 31% utilization. A subsequent Windows GPU-engine sample showed Chrome video-decode and 3D activity in addition to desktop work. The probe was launched before that sample was fully reviewed, contrary to the intended sequential idle gate. Adapter-specific absence of contention was not established. The owned request/server tree was stopped conservatively; Chrome and other applications were left running. This is an execution/protocol exception, not a Qwen task failure.

The client recorded `ReadError` after the server was stopped, with **no complete model response**. The server progress log shows at least **267 generated tokens**, but this is a lower bound, not final returned usage. Charge the request at its full **1024-token upper bound** for resource accounting. No inference retry occurred.

The interim log prints generation-rate samples, but there is no final `eval_duration`/`eval_count` pair for this request. Do not substitute the interim rates into the profile comparison or call them a new measured Qwen speed. Final tool-call agreement, output-cap outcome, loaded `ollama ps` output and free VRAM while loaded are **not obtained** for this corrected request.

The first mismatched request remains exactly as originally recorded (33 returned tokens, FA disabled). Across both charged requests there are **33 known returned output tokens plus at most 1024 unreturned tokens**. Server progress supplies an additional lower-bound observation, not an exact total. No Sol requests, robot commands, Gazebo runs or Phase 1 calls occurred.

Both the first mismatched request and this contention-stopped request are excluded from any claim of a clean historical-baseline reproduction or A/B speed improvement. Current partial logs support 17/33 offload and a 128 MiB GPU KV allocation, consistent with the historical memory evidence. They do not justify a measured benefit for cache quantization or lower context.

The archived 40-trial/144-call analysis remains complete. **A clean live baseline observation remains incomplete.** Continuation requires a quiet GPU interval (including pausing browser video/other GPU-heavy work), a fresh preflight reviewed before launch, and an explicitly bounded new allowance. No further call is scheduled or authorized here. Stage 1 settings/threshold confirmation is still separate.

Evidence: `corrected-hardware-summary.json`, `hardware-04/`, `corrected-hardware-dispatch-reservation.json`, `corrected-check-authorization.json`, `corrected-check-idle-samples.json`, `corrected-check-gpu-engine-samples.json`, and `PRE_RUN_AMENDMENT_02.md`. The original pre-run note and both amendment hashes were checked before dispatch. The previous attempt files passed preservation checks.
