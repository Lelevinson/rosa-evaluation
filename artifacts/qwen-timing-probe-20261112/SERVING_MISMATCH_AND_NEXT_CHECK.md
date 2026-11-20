# Retained hardware observation and proposed correction

Date: 2026-11-12. No approval for another inference request is implied here.

The single allowed inference returned in hardware-03 (33 generated tokens).
Version, model digest, 8192 context and decoded prompt token count matched.
The serving runtime did **not** match historical M4:

- Historical command: `--flash-attn auto -b 512 -ub 512`; runtime FA enabled.
- Probe command: `--cache-type-k f16 --cache-type-v f16 --flash-attn off -b 256 -ub 256`;
  runtime FA disabled.
- The probe incorrectly set OLLAMA_FLASH_ATTENTION to the literal string false,
  interpreting the historical startup display as an explicit environment value.
  The original launcher did not set that variable. An unset value and explicit
  false have different effects in this pinned server. This is a probe setup
  error, not evidence that M4 used FA disabled.

The one request is retained and must not be silently rerun or called a matching
baseline. It produced about 1.98 generation tokens/s, selected inspect_readiness
instead of historical stage_left, and executed no tools. It cannot establish a
speed regression or reproducibility failure under matched serving conditions.

Its log shows a 4657.81 MiB vision compute buffer versus 248.10 MiB historically.
API ps estimated size_vram about 7.52 GiB on a 6 GiB device; therefore its
27%/73% CPU/GPU display is not an independent measurement of physical residency.
Retain it verbatim alongside nvidia-smi and the layer/buffer log. Overcommit or
paging is a hypothesis, not directly measured here.

The future launcher correction is prepared: remove the process-local FA/cache
environment overrides, reproduce the original unset/auto policy, verify effective
FA enabled and the runner batch/buffer settings, and retain the same version,
weights, request, resource bounds and no-tool-execution rule. The existing global
reservation still blocks further inference. Nothing has reset that counter.

A corrected hardware check requires approval for **one additional Qwen inference
request**, maximum 1024 generated tokens, no inference retry, no Gazebo or Sol.
This would be a documented new observation, not replacement of hardware-03 or
approval for the 30-request Stage 1 comparison.

The script also raised an error during taskkill after unloading, before writing
its final status. A separate post-run check confirmed that both owned server and
runner PIDs had exited. Preserve this cleanup warning and reconciliation; do not
describe the original launcher as having exited successfully.
