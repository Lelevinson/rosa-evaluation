# Authorized corrected hardware observation

Date: 2026-11-12. Recorded before the additional inference.

The owner explicitly approved: "Run one corrected hardware-check request."
This grants exactly one additional Qwen request, at most 1024 generated tokens,
no automatic inference retry, no tool execution, no Gazebo/Sol calls. Phase 1
is not authorized by this approval. The original request and failures remain.

Attempt hardware-04 removes the explicit Flash Attention and KV-cache process
environment overrides. This reproduces the original launcher's unset/auto FA
policy and default f16 cache rather than interpreting its startup false display
as an explicit disable instruction. Effective FA, cache type, batch and buffer
settings will be checked in the actual runtime log. A mismatch will be reported,
never silently rerun. All original model, context, sampling, payload, adapter,
180-second request and 420-second outer limits remain in effect.

A separate exclusive corrected-hardware-dispatch-reservation.json records the
additional charge before dispatch. The original reservation is never removed or
reset. Both allowances together cap this entire Phase 0 probe at two generation
requests and 2048 possible generated tokens, counting errors/censored requests.

Unity Editor, Ollama and Gazebo processes are absent at the initial recheck.
GPU samples show 24-40% activity; Windows GPU-engine counters attribute the
observed activity to desktop composition (dwm) and VS Code. This is not an idle
dedicated benchmark machine. Desktop activity is documented; no other user's
applications are terminated. This one cold hardware observation must not be
presented as steady-state speed or a controlled A/B performance comparison.

Runtime script copies and source hashes are captured with the attempt. Only
the owned server tree is unloaded/stopped; cleanup command errors are retained,
and process existence is checked independently afterward.
