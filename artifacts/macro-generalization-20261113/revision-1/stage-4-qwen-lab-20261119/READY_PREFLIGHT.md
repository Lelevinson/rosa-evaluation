# Qwen lab launch preflight

Date: **2026-11-19**. **Technically prepared; owner acknowledgment pending. No benchmark inference started.**

- Scope: the same38 frozen AI-authored G1 mock cases, both conditions,76 attempts. No Sol rerun or catalogue probe.
- Existing lab Jazzy container; RTX4080 SUPER16GB; exact Qwen3.5 9B Q4_K_M digest matches. Ollama0.40.6. No new model download.
- Measured loaded offload: **33/33 layers on GPU**, context8192, flash attention enabled, KVf16. All three fresh post-load GPU samples are at or below5% utilization. GPU gate is refreshed before actual launch if stale.
- Local model authentication: no OAuth or API key required.
- Eight scripted controls passed with8/8 local and8/8 persisted Phoenix audits, zero inference requests. Wire settings match the unchanged frozen configured adapter.
- Client settings: context8192, output1024/call, task output2048, temperature0, seed42, thinkingFalse, streamingFalse, cacheFalse, use_mmapTrue. Actual API streaming isTrue; server prompt cache is enabled. These are documented distinctions, not changed settings.
- Budget: **611 total charged requests**, including the1 already spent empty-prompt model-load request; at most610 inference/retry requests remain. Eight calls/task,360s/task,8h live backend window,10 native operations,16 tool attempts,3 corrections, at most1 dispatch. Only HTTP502/503/504 qualify for the unchanged narrow reserve of at most3 retries; total cap always takes precedence.
- Model load took approximately6.59s, evaluated no task request and returned empty task text. Omitted internal usage counters remain NOT_RECORDED; no missing usage is estimated. This is setup, not a scored trial or correctness evidence.
- Preserve every attempt. Continue only unstarted cells after integrity checks with cumulative counters and the original live deadline. Do not rerun failures or repeat uncertain actions.
- Phoenix is the existing healthy loopback service; do not stop it. New Qwen project spans receive exact persisted-identity/tree audits. Keep machine/container/model service available; detached lab execution must not depend on the laptop terminal staying connected.
- New Qwen clarification responses require a new real blinded review. Sol's ratings are not reused. P4 catalogue work is not part of this batch.
- Original3796 frozen inputs verify unchanged. The new backend port is separately sealed below. No module, case, prompt or scorer change. Existing Sol data retain their original host/provenance.

See EXECUTION_NOTE.md, LAB_INVENTORY.json, MODEL_LOAD_PREFLIGHT.json, GPU_GATE_AFTER_LOAD.json, zero-model-validation-attempt02/VALIDATION.json and freeze.json.

Frozen G1 requires review of the preflight and a final backend launch acknowledgment. The owner's choice to prioritize Qwen authorized preparation; this record is now available for that final review.

Freeze SHA256: d4cee8306affa5a55d24ea3aec64367039d0f676fef74db37721caa63a98102c
