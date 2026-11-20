"""Render Phase 0 findings from the new, read-only extraction outputs."""
from pathlib import Path
import csv
import hashlib
import json

OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def main():
    a = read('analysis.json')
    totals = a['totals']
    inventory = read('field-inventory.json')
    with (OUT / 'per-trial.csv').open(encoding='utf-8', newline='') as f:
        trials = list(csv.DictReader(f))
    hist = read('historical-loaded-status.json')
    models = [m for record in hist for m in record.get('models', [])]
    model_states = {(m['size'], m['size_vram'], m['context_length'], m['digest']) for m in models}
    headroom = {'status': 'ILLUSTRATIVE_ESTIMATES_NOT_MEASUREMENTS',
        'basis': 'historical 8192-context f16 GPU KV buffer 128 MiB; q8_0 nominal 34 bytes per 32 values vs f16 64',
        'historical_gpu_kv_mib': 128, 'historical_cpu_kv_mib': 128,
        'B_gpu_kv_mib_estimate': 128 * 34/64,
        'B_gpu_kv_saving_mib_estimate': 128 * (1-34/64),
        'C_gpu_kv_mib_estimate': 128 * 34/64 * 6144/8192,
        'C_gpu_kv_saving_mib_estimate': 128 * (1-34/64 * 6144/8192),
        'excluded': 'alignment, actual backend support, changed layer placement, compute/graph/vision buffers, recurrent state, desktop load',
        'historical_CPU_model_buffer_mib': 2553.89,
        'conclusion': 'Cannot bridge the historical roughly 2.5 GiB CPU weight allocation. Small layer-count or direct kernel gains remain unmeasured; insufficient evidence to declare all B/C speed benefits impossible.'}
    (OUT / 'headroom-estimates.json').write_text(json.dumps(headroom, indent=2)+'\n', encoding='utf-8')
    lines = ['# Qwen Phase 0 timing and serving assessment', '',
        'Date: **2026-11-12**. Exploratory analysis separate from M4. **Archived analysis complete; live hardware check deferred because GPU process inventory includes Unity Editor processes and exclusive timing conditions are unconfirmed. Phase 1 not started.**', '',
        'No new inference requests, Sol requests, robot commands or simulator runs. No M4 files, frozen sources or M1-M5 reports changed. All new outputs are in this directory. The pre-run note and hash receipt precede any live request.', '',
        '## Main findings', '',
        f'- All six requested Ollama timing/count fields exist on **144/144 calls**, across **40 trials**. Cached-token count is **not recorded** in the retained per-call metadata.',
        f'- Generation is **{100*totals["server_eval_seconds"]/totals["server_total_seconds"]:.2f}%** of server-reported request duration. Historical median generation throughput is **{a["median_recorded_generation_tokens_per_second"]:.3f} tokens/s**. This is historical recorded throughput, not a new hardware measurement.',
        '- Historical server startup shows **17/33 layers offloaded**, effective **Flash Attention enabled**, and **f16 K/V cache**. The startup environment flag alone would have been misleading: it said false while the runtime reported auto/enabled.',
        '- The GPU KV buffer was only **128 MiB**. Estimated q8_0 savings are about **60 MiB** at 8192 context, or **77 MiB** with q8_0 at 6144 context. Those do not eliminate roughly 2554 MiB of CPU model weights. They do not establish zero possible speed gain.',
        '- Five response-length-stop trials consumed **27.91%** of recorded Qwen task time. Reducing unneeded generation is a substantial engineering target, but a shorter output is only useful if goal correctness is retained.', '',
        '## 0.1 Field inventory', '', '| Field | Calls recorded | Granularity |', '|---|---:|---|']
    for field in ('total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'prompt_eval_cached_count'):
        n = inventory['per_request_recorded'].get(field, 0)
        lines.append(f'| `{field}` | {n}/144 | {"Per call" if n else "Not recorded"} |')
    lines += ['', 'Source: each `ConfiguredChatOllama` span, JSON-decoded `attributes.output.value`, `generations[0][0].generation_info`. Metadata also appears in the message response; that duplicate is not an extra observation. Counts and usage were checked against all 144 inference-ledger entries.', '',
        'The historical server log shows prompt reuse/checkpoints, but no per-call cached-token count was reconstructed from it. LangChain `cache=False` controls client response caching; it did **not** disable the server prompt/KV cache. Preserve this distinction in future comparisons.', '',
        '## 0.2-0.3 Time decomposition and clock reconciliation', '',
        '| Ollama server component | Total seconds | Share of server total |', '|---|---:|---:|']
    for label, key in [('Generation', 'server_eval_seconds'), ('Prompt processing', 'server_prompt_eval_seconds'),
                       ('Loading', 'server_load_seconds'), ('Other server time', 'server_server_other_seconds')]:
        lines.append(f'| {label} | {totals[key]:.3f} | {100*totals[key]/totals["server_total_seconds"]:.2f}% |')
    lines += [f'| **Total server requests** | **{totals["server_total_seconds"]:.3f}** | **100%** |', '',
        'Server other time = total minus generation, prompt processing and loading. It is not total ROSA overhead. Ollama durations are converted from nanoseconds.', '',
        '| Recorded clock/boundary | Seconds |', '|---|---:|',
        f'| Task duration: WSL `time.monotonic()` | {totals["task_seconds"]:.3f} |',
        f'| Native operation union: snapshot monotonic intervals | {totals["native_monotonic_seconds"]:.3f} |',
        f'| Task minus native: non-native elapsed estimate, not pure inference | {totals["task_minus_native_seconds"]:.3f} |',
        f'| OpenTelemetry root timestamp duration | {totals["trace_root_seconds"]:.3f} |',
        f'| OpenTelemetry LLM timestamp durations | {totals["client_llm_span_seconds"]:.3f} |',
        f'| OpenTelemetry native timestamp interval union | {totals["trace_native_seconds"]:.3f} |',
        f'| Root minus LLM and native timestamp intervals | {totals["trace_root_minus_client_llm_and_native_seconds"]:.3f} |', '',
        'The trace root timestamps and task monotonic records also disagree, not just client versus server. The task timer surrounds invocation plus trace finalization; the shorter monotonic total cannot be explained by calling server duration task time. These are uncalibrated clock domains. The archives do not identify the physical cause; clock-rate/adjustment explanations are hypotheses. Preserve each recorded measurement and do not subtract server totals from monotonic task time to manufacture negative overhead. The trace-timestamp decomposition is a separate view, not a correction of frozen task metrics.', '',
        'Native time includes actual waits inside dispatched reads/writes. Setup/reset and the independent observer outside the task are excluded. Failed tasks often dispatch no movement. Do not insert a nominal trajectory wait when no command ran.', '',
        '## 0.4 Descriptive regressions', '',
        'Model: seconds = intercept + b_output * output tokens + b_input * input tokens. Negative intercepts are descriptive fit artifacts, not physical startup times.', '',
        '| Unit/outcome | n | Intercept s | b_output s/token | b_input s/token | R squared | Input/output r |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in a['regressions']:
        lines.append(f'| {r["outcome"]} | {r["n"]} | {r["intercept_seconds"]:.5f} | {r["output_token_coefficient_seconds"]:.6f} | {r["input_token_coefficient_seconds"]:.6f} | {r["r_squared"]:.5f} | {r["input_output_predictor_correlation"]:.5f} |')
    lines += ['', 'Trial-level predictors are strongly correlated (r=0.832); do not interpret separate slopes as isolated costs. Call-level correlation is lower (r=0.311), but calls are clustered in trials and repeated families. Input counts include reused prompt prefixes, so input-token slopes do not measure uncached prefill speed. No causal claim, independent-sample significance test or extrapolated speed prediction is made.', '',
        '## 0.5 Final ending types', '', '| Ending | Trials | Mean task s | Total task s | Share of total |', '|---|---:|---:|---:|---:|']
    for r in a['ending_types']:
        lines.append(f'| {r["ending_type"]} | {r["trials"]} | {r["mean_task_seconds"]:.3f} | {r["total_task_seconds"]:.3f} | {r["share_total_task_percent"]:.2f}% |')
    lines += ['', 'These are mutually exclusive **ending labels**, not mutually exclusive causes. Selection/commitment errors can precede length stops. Wrong skill/goal covers five accepted readiness reports that did not meet the frozen user-goal criterion; it does not mean every one of eleven failures was a false success.', '',
        '## 0.6 All attempts and matched both-pass subset', '',
        '| Subset / condition | n | Correct | Mean task s | Mean calls | Mean input tokens | Mean output tokens |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in a['comparisons']:
        lines.append(f'| {r["subset"]} / {r["condition"]} | {r["trials"]} | {r["correct"]} | {r["mean_task_seconds"]:.3f} | {r["mean_calls"]:.3f} | {r["mean_input_tokens"]:.2f} | {r["mean_output_tokens"]:.2f} |')
    lines += ['', 'Both-pass = 13 matched family/repetition pairs. This conditional subset excludes failures and cannot establish an unconditional reliability advantage. Per-task input totals sum across calls, not context length.', '',
        '## Historical hardware/settings versus current hardware', '',
        'Historical sources: retained `outside-task-ollama-status.json` for all 40 Qwen trials, pinned preflight, and the original M4 server log. Relevant log lines and its SHA-256 are retained in `historical-server-log-excerpts.json`.', '',
        '- Model: qwen3.5:9b Q4_K_M, Ollama 0.40.6; digest `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.',
        '- Runtime context 8192; offload 17/33 layers; CPU model buffer 2553.89 MiB; GPU model buffer 2803.99 MiB.',
        '- f16 KV buffers: CPU 128 MiB + GPU 128 MiB; recurrent state CPU/GPU about 25.13 MiB each. A separate vision projector was loaded even for these text requests; the log describes its model size as 878.99 MiB. Do not assume every auxiliary byte is captured in a layer count.',
        '- Runtime Flash Attention explicitly enabled. Server prompt cache explicitly enabled. The server context default 4096 did not override the request context 8192.',
        f'- {len(models)} historical loaded-model records. Unique (loaded size, size_vram, context, digest) configurations: {len(model_states)}. Loaded-model size and device allocation are not disk weight sizes or GPU compute percentages. Full source records are provided.',
        '- Historical free VRAM while loaded and an `ollama ps` PROCESSOR text line: **not recorded in these trial-status files**. The server log contains allocation/fitter diagnostics but no new post-hoc measurement is substituted.', '',
        'Current preflight: GPU has 6141 MiB total. Exact readings/process list are in `current-hardware-preflight.json`. The list includes three Unity Editor processes, so a clean live load/inference check was deferred. WSL process inspection found no simulator or experiment worker. No unrelated process was stopped. Loaded current offload, free VRAM while loaded, current pinned server status and current effective settings remain **not measured**.', '',
        'The PATH-installed Ollama client is 0.24.0 rather than the project pin. Its status command attempted an automatic app startup, failed on denied external log writes and returned no server status. No model request was sent. Use the pinned binary/API for a later check; do not upgrade or replace the historical pin.', '',
        '## Headroom screen and proposed profiles', '',
        'The following are **proposals awaiting confirmation**, not measured configurations:', '',
        '| Profile | Context | Effective FA | KV cache | Estimated GPU KV saving versus historical A |',
        '|---|---:|---|---|---:|',
        '| A | 8192 | historical auto/enabled, verify | f16 | 0 MiB |',
        '| B | 8192 | explicit on, verify | q8_0 | about 60 MiB |',
        '| C, gated | 6144 | explicit on, verify | q8_0 | about 77 MiB |', '',
        'Estimate assumes unchanged placement and nominal q8_0 block storage (34 bytes per 32 values versus f16 64). The format definition is documented in the [GGML source](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h); [Ollama documents cache quantization](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache). These current references explain the estimate, not verified support in the pinned runtime. Alignment, backend support, graph buffers, auxiliary/recurrent allocations and relocation can change actual results. The historical fitter displayed a roughly 155 MiB difference between candidate adjacent placements, but layers are heterogeneous; this is not a universal one-layer threshold. Savings clearly cannot move all CPU weights to GPU. They do not prove that zero layers can move or that direct runtime effects cannot help. A definitive no-benefit headroom stop is not established from memory arithmetic alone.', '',
        'The longest recorded prompt was **4027 tokens**, primitive partial_command repetition 1 call 8. A 4096 context cannot accommodate that plus the possible 1024-token response; C=6144 is proposed instead. This safety input is a later-turn input, not a first-turn selection task.', '',
        '## What must be established before live Stage 1', '',
        '1. Resolve the competing GPU workload and perform the one-request Phase 0 hardware check; stop on digest/version mismatch or unresolved contention.',
        '2. Confirm A/B definitions and whether a roughly 60 MiB saving justifies the small screen. FA already being enabled removes one presumed source of benefit.',
        '3. Confirm thresholds: proposed >=1.5x median generation throughput, >=9/10 first-call agreement on family inputs, no newly truncated prompts, no increase in cap hits. The context-safety input is separate, and every mismatch is disclosed. Agreement preserves errors too; it is not correctness.',
        '4. Freeze server cache/keep-alive policy, profile order and thermal/background controls. Repeated prompts may benefit from server prefix reuse even with client cache disabled. Record effective settings and all timing fields per request.',
        '5. Freeze the 11-input manifest and three repeated cases already proposed before any new output: movement, healthy inspection, ambiguous request. A/B = 30 calls including warm-ups, no automatic inference retries; choose explicit external per-call/batch deadlines and a charged token ceiling before launch.', '',
        'C is conditional; D is unscheduled and would change weight quantization/digest. No automatic progression to Phase 1. No new speed or reliability claim follows from first-call agreement.', '',
        '## Per-trial appendix', '',
        'The CSV contains additional decompositions and raw identifiers. Times below retain the original task timer.', '',
        '| Trial | Ending | Calls | Input | Output | Task s | Native s |', '|---|---|---:|---:|---:|---:|---:|']
    for r in trials:
        lines.append(f'| {r["trial"]} | {r["ending_type"]} | {r["calls"]} | {r["input_tokens"]} | {r["output_tokens"]} | {float(r["task_seconds"]):.3f} | {float(r["native_monotonic_seconds"]):.3f} |')
    lines += ['', '## Files and reproducibility', '',
        '- `analyze.py`: offline extraction, all ledger/trace usage checks, source/freeze preservation checks; no network calls.',
        '- `render_report.py`: renders this report from extraction outputs.',
        '- `field-inventory.json`, `per-trial.csv`, `per-call.csv`, `ending-type-summary.csv`, `matched-comparison.csv`, `regressions.json`, `analysis.json`.',
        '- `historical-loaded-status.json`, `historical-server-log-excerpts.json`, `current-hardware-preflight.json`, `headroom-estimates.json`.',
        '- `replay-inputs.json`: 20 first-turn inputs plus the actual maximum-length later-turn input, preserving decoded messages/tools and original outputs; source hashes included. Not held-out material.',
        '- `proposed-stage1-inputs.json`, `PRE_RUN_NOTE.md`, `pre-run-note.sha256.json`, `source-integrity.json`, `protected-m4-before.json`.',
        '', 'Regenerate locally from the workspace root:', '',
        '```powershell', 'python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/analyze.py',
        'python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/render_report.py', '```', '',
        'No Git commit, public upload, new inference or automatic progression was performed. Existing research results remain unchanged.']
    (OUT / 'PHASE0_REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    integrity = read('source-integrity.json')
    status = {'date': '2026-11-12', 'archived_analysis': 'COMPLETE',
        'live_hardware_check': 'DEFERRED_PENDING_GPU_WORKLOAD_RESOLUTION',
        'phase1': 'NOT_STARTED_SETTINGS_AND_THRESHOLDS_PENDING_CONFIRMATION',
        'probe_inference_requests': 0, 'trials_analyzed': 40, 'calls_analyzed': 144,
        'protected_m4_files': integrity['protected_m4_file_count'],
        'all_m4_files_unchanged': integrity['all_m4_files_unchanged_after_analysis'],
        'frozen_sources_verified': len(integrity['frozen_source_checks']), 'report': 'PHASE0_REPORT.md'}
    (OUT / 'status.json').write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8')
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir()
                if p.is_file() and p.name != 'manifest.json'}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(status, indent=2))
    # Never leave the generated live status saying zero calls after a retained
    # hardware request. Reapply its explicit outcome without any model request.
    if (OUT / 'hardware-dispatch-reservation.json').exists():
        from hardware_report import main as append_hardware
        append_hardware()
    if (OUT / 'corrected-hardware-dispatch-reservation.json').exists():
        from corrected_hardware_report import main as append_corrected_hardware
        append_corrected_hardware()


if __name__ == '__main__':
    main()
