# Phase 1 preparation and preflight checkpoint

Date: **2026-11-13**. Phase 1 was authorized and frozen on 2026-11-12.

**Status: ready implementation; live model execution has not started.** The first
coordinator launch stopped at the GPU gate before starting a server or dispatching
a request. Two subsequent metadata-only rechecks also failed the quiet-GPU
condition. **Zero Phase 1 model requests, generated tokens or robot operations.**

The original Phase 0 requests remain separate. Their spent allowances are not
used to block or silently reset this separately authorized campaign.

## What is ready

| Item | Frozen definition / validation |
|---|---|
| A reference | Same pinned model/server; effective auto/enabled FA, f16 KV, 8192 context |
| B | Same weights/server/context; explicit FA enabled, q8_0 KV |
| Conditional C | B at 6144 context, only if B passes all fixed gates |
| Model configuration | Qwen3.5:9b Q4_K_M; temperature 0, seed 42, reasoning false, 1024 output tokens/call |
| Serving implementation | Existing ConfiguredChatOllama; internally streamed API assembled for caller; no tool execution |
| Inputs | Ten frozen family first turns plus actual 4027-token later-turn safety input |
| Per-profile schedule | One warm-up, 11 unique measured requests, three fixed repeats |
| Stage 1 A/B budget | 30 requests including warm-ups; at most 30720 output tokens |
| Conditional C budget | At most 15 additional requests / 15360 output tokens |
| Entire Phase 1 bound | 45 requests / 46080 possible output tokens; 9000-second campaign limit |
| Request deadlines | 180-second request timeout; 210-second external request deadline; no inference retries |
| Candidate rule | At least 1.5x fresh A median generation throughput, 9/10 family agreement, no prompt-count mismatch or additional cap hits |
| Cost/quality reporting | All raw outputs, first-call mismatches, stability, timing fields, effective settings and physical GPU readings retained |
| Offline validation | All 11 payloads built through pinned adapter; six decision-boundary checks passed |
| Preservation | All 950 M4 files and 62 frozen source files verified unchanged |

Freeze SHA-256:
`f95790c506e919f2d6d19d57e0ef8a1eed838cf194304c4749306c2b27fb6369`.

## Why live execution stopped

The protocol's conservative gate rejects non-display GPU-engine activity above
2%, and requires each of three pre-request NVIDIA samples to be at most 10%.
Those settings were fixed before any Phase 1 output.

The first launch recorded Chrome 3D activity at about 2.77%, although its NVIDIA
total samples were only 2%, 0%, 2%. It stopped before server creation. A recheck
recorded total utilization 18%, 31%, 5%; the next recorded 3%, 11%, 11%. Both
failed the declared total-utilization rule. No settings were relaxed in response.

These failures establish that the samples did not meet the declared gate. They
do **not** establish that another model or dedicated compute workload was running;
desktop activity and adapter attribution remain relevant limitations. No Qwen
performance or reliability result can be inferred from metadata-only stops.

## Preservation and continuation

The original zero-call launch is preserved under
[`preflight-attempt-01/`](../artifacts/qwen-serving-phase1-20261112/preflight-attempt-01/manifest.json),
including its checkpoint, GPU samples, report, process inventory and successful
M4/source preservation audit. Only runtime markers and generated outputs were
archived to prepare a new preflight; no request reservation was removed or reset.
Frozen inputs, code and decision thresholds remain unchanged.

The owner has been asked to pause videos/GPU-heavy applications and indicate
readiness. The existing instruction authorizes the bounded comparison; no extra
OAuth or inference approval is required for this campaign. Launch may proceed
only after reviewed preflight evidence meets the condition. The coordinator will
also check before each request and monitor long requests. It will stop and retain
charged/censored records on a later failure rather than retry until success.

There is no active Phase 1 model worker. C has not been triggered, and D remains
outside the authorized schedule. No new claim of speed, first-call agreement or
robotic correctness is available yet.

## Evidence

- [Living roadmap](CLAUDE_QWEN_ROADMAP_LIVE.md).
- [Frozen protocol](../artifacts/qwen-serving-phase1-20261112/PROTOCOL.md) and
  [freeze record](../artifacts/qwen-serving-phase1-20261112/freeze.json).
- [Current status](../artifacts/qwen-serving-phase1-20261112/status.json) and
  [current results report](../artifacts/qwen-serving-phase1-20261112/PHASE1_REPORT.md).
- [First recheck](../artifacts/qwen-serving-phase1-20261112/recheck-after-zero-call-stop.json)
  and [second recheck](../artifacts/qwen-serving-phase1-20261112/idle-recheck-02.json).
- [Offline adapter validation](../artifacts/qwen-serving-phase1-20261112/offline-validation.json)
  and [decision-rule validation](../artifacts/qwen-serving-phase1-20261112/decision-rule-validation.json).

## Later pre-inference update, 2026-11-13

After the owner confirmed apps paused, a fresh check still recorded Chrome GPU
activity. DXGI adapter enumeration was used to identify NVIDIA and Intel counters
instead of assuming all Windows GPU engines belong to the tested device. Chrome
did have a small NVIDIA 3D reading, not only integrated-graphics activity.

With **zero Phase 1 requests**, a documented amendment corrected ordinary browser
display classification: Chrome 3D rendering <=5% is allowed alongside existing
Code/dwm desktop exceptions. Video-decode/compute >2% and the three-sample <=10%
total NVIDIA requirement remain unchanged. No model inputs, profiles, statistical
gates, request/token ceilings or deadlines changed. All original frozen files
are preserved; this update does not silently rewrite the earlier rule.

The amended recheck still failed: Chrome video decoding was about 3.2%, and
NVIDIA total samples included 18%. The owner has been asked to fully exit Chrome;
no server or model request has started. Existing Phase 1 authorization remains
valid; only the environment condition is unresolved.

Amended freeze SHA-256:
`138beb9c0d3e5a68164e50a815b0ef7672fb9ace87f27cc2c52a1befc89af195`.
See the [amendment](../artifacts/qwen-serving-phase1-20261112/PRE_INFERENCE_AMENDMENT_01.md),
[adapter inventory](../artifacts/qwen-serving-phase1-20261112/adapter-inventory.json)
and [latest failed check](../artifacts/qwen-serving-phase1-20261112/amended-owner-ready-preflight.json).
