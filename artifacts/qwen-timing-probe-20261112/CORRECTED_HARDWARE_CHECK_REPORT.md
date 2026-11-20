# Corrected Phase 0 hardware request: contention stop

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
