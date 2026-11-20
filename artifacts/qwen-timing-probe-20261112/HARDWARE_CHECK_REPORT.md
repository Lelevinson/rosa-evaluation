# Phase 0 live hardware observation: configuration mismatch

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
