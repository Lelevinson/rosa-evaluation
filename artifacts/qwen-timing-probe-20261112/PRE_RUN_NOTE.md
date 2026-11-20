# Qwen timing probe: pre-run boundaries

Date: 2026-11-12. Exploratory serving analysis, separate from M4.

The owner authorized starting Phase 0 on 2026-11-12. Phase 1 settings and
thresholds still require confirmation after the Phase 0 findings. This note
precedes any inference for this probe; its SHA-256 is recorded separately.

## Preservation and sources

- All new files stay in this directory. Do not edit M4 artifacts, frozen sources,
  the M4 freeze, or M1-M5 reports. Record source hashes and check preservation.
- Analyze all 40 archived Qwen trials and their 144 requests. Decode the JSON
  strings in LLM spans; do not count duplicate metadata copies as extra calls.
- Use the original frozen scores. Ending categories describe final outcomes,
  not exclusive causal diagnoses: correct, wrong skill/goal, response-length
  stop, validation-retry exhaustion. Preserve the underlying selected skill.
- Use snapshot native-operation monotonic intervals for native time. Merge
  overlaps. Keep task monotonic, OpenTelemetry timestamp, and Ollama server
  durations distinct. Do not force different clocks into an additive breakdown.
- Unavailable values are null / "not recorded". Do not estimate missing historical
  hardware readings using current readings. Regression is retrospective and
  descriptive; report predictor correlation and non-independent repeated cases.

## Phase 0 live hardware check, if the idle gate permits

- No Sol, OAuth, Gazebo, ROS commands, robot tool dispatch or model downloads.
- Check Windows and WSL processes, GPU use, endpoint version and model digest.
  Desktop display use is unavoidable; a competing workload must be resolved.
- Use only the existing pinned Ollama 0.40.6 binary and existing qwen3.5:9b
  Q4_K_M digest
  `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
- If needed, start a separate hidden server on a private local/WSL address and
  unused port. Use process-local environment, one slot and one loaded model;
  disable cloud and model pruning. Do not reconfigure/restart the M4 server.
- Make at most ONE inference request: the archived repetition-1 macro
  move_constrained first turn, including its exact decoded messages and tools.
  Use ConfiguredChatOllama, num_ctx=8192, num_predict=1024, temperature=0,
  seed=42, use_mmap=True, reasoning=False, streaming=False, client cache=False.
  Preserve the original model template and effective server prompt-cache policy.
- The result is inspected only: no returned tool call is executed. At most
  1,024 generated tokens, no automatic inference retry, a 180-second request
  timeout and a 420-second outer allowance including server setup. A failed or
  censored request still consumes the one-request budget and is retained.
- Capture effective runtime settings, layer offload, buffers, GPU total/used/free
  memory, loaded size/context, version, digest and all available timing/count
  fields. Keep cold loading separate from steady generation speed.
- Stop on a digest/version mismatch, unresolved GPU contention, failure to verify
  the intended server or unavailable authorization. Preserve completed analysis.
- Stop/unload only the server/model started by this probe. Do not kill other
  applications or change persistent user environment settings.

## Proposed profiles: NOT YET APPROVED

- A: pinned historical configuration, context 8192, observed effective Flash
  Attention and f16 KV cache. Verify rather than interpreting the startup
  OLLAMA_FLASH_ATTENTION flag alone. Historical logs show runtime FA enabled.
- B: same weights/version/options/context; explicit FA on and q8_0 KV cache.
  This tests the serving package; FA may already be enabled in A.
- C: B with context 6144, only if B helps or Phase 0 establishes a context
  limitation. 4096 is unsuitable for the recorded 4027-token maximum input plus
  a possible 1024-token output. Verify actual full prompt length before use.
- D: optional lower weight quantization, not scheduled or downloaded. Different
  digest/configuration, requiring separate correctness evaluation.

Stage 1 proposal: ten repetition-1 macro first-turn inputs, one per family,
plus the actual maximum-input request from either condition. One pass each;
three predetermined inputs repeated once (move_constrained, inspect_healthy,
ambiguous_goal). One discarded warm-up per profile. If all inputs are distinct,
A/B requires 30 inference requests including warm-ups. No Phase 1 request is
covered by the one-request Phase 0 hardware allowance.

Proposed screening thresholds, pending owner confirmation: median generation
tokens/s at least 1.5 times A; first-tool-call agreement at least 90% on the ten
family inputs (9/10), with the context-safety input reported separately; no newly
truncated prompts and no increase in output-cap hits. Compare parsed names and
arguments, not opaque call IDs; retain missing/malformed/multiple calls and every
mismatch. Repetitions check stability, not independent sample size. A's match to
the historical outputs must also be reported. These are candidate-screening
rules, not a robotic correctness or equivalence claim. Profile order, cache
policy and thermal controls must be finalized before Phase 1.

No new Qwen task-speed or reliability claim follows from this first-turn probe.
A candidate needs a separate full-loop comparison with fresh correctness cases.
