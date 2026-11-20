"""Append the single live hardware observation to the Phase 0 report."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    reservation = read(ROOT / 'hardware-dispatch-reservation.json')
    folder = ROOT / reservation['attempt']
    result = read(folder / 'result.json')
    attempt_path = folder / 'attempt-status.json'
    attempt = read(attempt_path if attempt_path.exists() else folder / 'post-run-reconciliation.json')
    assert result['status'] == 'RETURNED'
    assert attempt['status'] in ('COMPLETE', 'COMPLETE_REQUEST_WITH_SERVING_MISMATCH')
    assert result['requests_reserved'] == result['requests_returned'] == 1
    assert result['tools_dispatched'] == 0
    loaded = read(folder / 'loaded-model.json')
    model = next(m for m in loaded['models'] if m['name'] == 'qwen3.5:9b')
    before = read(folder / 'gpu-before.json')
    gpu = read(folder / 'gpu-loaded.json')
    verified = read(folder / 'verified-server-model.json')
    pre = read(folder / 'pre-dispatch.json')
    log = (folder / 'server-stderr.log').read_text(encoding='utf-8', errors='replace')
    patterns = ('offloaded', 'model buffer size', 'KV buffer size', 'K (f16)',
                'RS buffer size', 'Flash Attention enabled', 'flash_attn ',
                'prompt cache is enabled', 'truncated =', 'model size:')
    excerpts = [{'line': i+1, 'text': line} for i, line in enumerate(log.splitlines())
                if any(p in line for p in patterns)]
    offload = re.findall(r'offloaded (\d+)/(\d+) layers to GPU', log)
    gpu_kv = re.findall(r'CUDA0 KV buffer size\s*=\s*([\d.]+) MiB', log)
    cpu_model = re.findall(r'CPU_Mapped model buffer size\s*=\s*([\d.]+) MiB', log)
    processor = (folder / 'ollama-ps.txt').read_text(encoding='utf-8-sig').strip()
    summary = {'scope': 'Single cold-load request, not Stage 1 or M4',
        'attempt': folder.name, 'requests': 1, 'tools_dispatched': 0,
        'server_version': verified['version']['version'], 'digest': model['digest'],
        'context': model.get('context_length'), 'loaded_size_bytes': model['size'],
        'loaded_vram_allocation_bytes': model['size_vram'], 'ollama_ps': processor,
        'layers_offloaded': list(map(int, offload[-1])) if offload else None,
        'gpu_kv_mib': float(gpu_kv[-1]) if gpu_kv else None,
        'cpu_model_buffer_mib': float(cpu_model[-1]) if cpu_model else None,
        'effective_flash_attention_enabled': 'Flash Attention enabled' in log,
        'effective_f16_kv_recorded': 'K (f16)' in log and 'V (f16)' in log,
        'server_prompt_cache_enabled': 'prompt cache is enabled' in log,
        'historical_serving_configuration_matched': False,
        'configuration_mismatch': 'Explicit FA=false disabled FA and changed runtime batching/buffers; historical FA was auto/enabled.',
        'cleanup': attempt,
        'gpu_before': before['gpu'], 'gpu_loaded': gpu['gpu'],
        'result': result, 'excerpts': excerpts, 'phase1_started': False,
        'retained_setup_failures': ['hardware-01: pre-dispatch transport assertion',
                                    'hardware-02: pre-dispatch PowerShell variable collision']}
    (ROOT / 'hardware-summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    md = result['metadata']
    lines = ['## Phase 0 live observation: serving mismatch retained', '',
        'Date: **2026-11-12**. Unity Editor processes had closed; only desktop GPU use remained in the captured inventory. WSL had no Gazebo/experiment worker. A separate hidden pinned server ran on the WSL-private address, port 11436, and was stopped after collection.', '',
        f'**Exactly one inference request** returned; {md["eval_count"]} generated tokens, finish reason `{md["done_reason"]}`. No robot tools ran. Stage 1 remains unstarted. **This is not a matched M4 baseline:** the probe incorrectly used an explicit false environment override, disabling Flash Attention. Historical M4 used unset/auto and effective FA enabled. An additional corrected check requires approval; no second inference was made.', '',
        '| Current measured item | Value |', '|---|---|',
        f'| Ollama | {summary["server_version"]} |',
        '| Model | qwen3.5:9b Q4_K_M |',
        f'| Model digest | `{summary["digest"]}`; matches M4 |',
        f'| Context | {summary["context"]} |',
        f'| Offload | {summary["layers_offloaded"][0]}/{summary["layers_offloaded"][1]} layers |',
        f'| Loaded allocation size from API ps | {model["size"]} bytes ({model["size"]/2**30:.3f} GiB) |',
        f'| GPU allocation from API ps | {model["size_vram"]} bytes ({model["size_vram"]/2**30:.3f} GiB) |',
        f'| Effective FA / f16 KV / server prompt cache | {summary["effective_flash_attention_enabled"]} / {summary["effective_f16_kv_recorded"]} / {summary["server_prompt_cache_enabled"]} |',
        f'| GPU KV buffer | {summary["gpu_kv_mib"]} MiB |',
        f'| CPU model buffer | {summary["cpu_model_buffer_mib"]} MiB |',
        f'| Expected / observed prompt tokens | {pre["expected_historical_input_tokens"]} / {md["prompt_eval_count"]} |',
        f'| Generated tokens | {md["eval_count"]} |',
        f'| Generation throughput | {result["generation_tokens_per_second"]:.3f} tokens/s |',
        f'| Same parsed tool call(s) as historical input | {result["first_call_matches_historical"]} |', '',
        'Pinned `ollama ps` output:', '', '```text', processor, '```', '',
        'GPU before model load:', '', '```text', before['gpu'].strip(), '```', '',
        'GPU immediately after request, model still loaded:', '', '```text', gpu['gpu'].strip(), '```', '',
        '**Memory reporting caveat:** API ps reports size_vram above the physical 6 GiB device capacity. Its 73% GPU display is retained verbatim, not accepted as proof of physical residency. nvidia-smi reports the actual device reading separately. The live log shows 16/33 layers and a 4657.81 MiB vision compute buffer, versus 17/33 and 248.10 MiB in the historical log. Do not add these heterogeneous allocations into a claimed physical VRAM total. Paging/overcommit explanations remain unverified.', '',
        '| Current request component | Seconds |', '|---|---:|']
    for field in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration'):
        lines.append(f'| {field} | {md[field]/1e9:.6f} |')
    lines += [f'| Client monotonic elapsed | {result["client_monotonic_seconds"]:.6f} |', '',
        'Cold-load time is included in this one request. Do not compare its total latency with M4 warm task means or infer a throughput regression/improvement from one observation. Serving mode, batch size, buffers and placement differ from M4. The first-call mismatch therefore does not establish a reproducibility failure under matched settings. This reading does not revise the historical 17/33 value.', '',
        'The six original timing/count fields are recorded in the response. `prompt_eval_cached_count` is ' + ('recorded.' if 'prompt_eval_cached_count' in md else '**not returned** for this request.'), '',
        'Adapter preflight discovered that LangChain `streaming=False` still uses internally streamed Ollama transport (`stream=true`); the response is assembled for the caller. This preserves the pinned adapter rather than silently switching wire behavior. `think=false` was verified. Client response cache=False and effective server prompt caching remain distinct.', '',
        'Two setup errors preceded generation: an overly strict transport assertion and a PowerShell variable collision. Both stopped before inference reservation and sent zero generation requests. Their logs are retained; they are not Qwen failures. The third setup attempt performed the single globally reserved request. It then hit a cleanup-command race/error before writing the original final status. Post-run PID checks confirmed both owned server and runner had exited. That reconciliation is preserved separately, without claiming the launcher exited successfully. No inference was retried.', '',
        '**Next decision:** approve or decline one additional corrected hardware request before considering Stage 1. The corrected launcher clears FA/cache environment overrides to reproduce the original unset/auto policy, and remains blocked by the existing global one-request reservation. See `SERVING_MISMATCH_AND_NEXT_CHECK.md`. This observation does not trigger Stage 1 or justify any serving improvement claim.', '',
        'Evidence: `hardware-summary.json`, `hardware-03/`, `hardware-dispatch-reservation.json`, `PRE_RUN_AMENDMENT_01.md`, `SETUP_ATTEMPTS.md`. Full output and parsed calls are retained in `hardware-03/response.json` and `result.json`.']
    section = '\n'.join(lines)+'\n'
    (ROOT / 'HARDWARE_CHECK_REPORT.md').write_text('# Phase 0 live hardware observation: configuration mismatch\n\n'+section, encoding='utf-8')
    report_path = ROOT / 'PHASE0_REPORT.md'
    report = report_path.read_text(encoding='utf-8')
    report = report.split('\n## Completed Phase 0 live hardware check')[0]
    report = report.split('\n## Phase 0 live observation: serving mismatch retained')[0]
    report = report.replace('**Archived analysis complete; live hardware check deferred because GPU process inventory includes Unity Editor processes and exclusive timing conditions are unconfirmed. Phase 1 not started.**',
        '**Archived Phase 0 analysis complete; one live request retained with a serving-configuration mismatch. A corrected hardware check needs approval. Phase 1 not started.**')
    report = report.replace('No new inference requests, Sol requests, robot commands or simulator runs.',
        'One isolated Qwen inference request for the hardware check; zero Sol requests, robot commands or simulator runs.')
    report = report.replace('Current preflight: GPU has 6141 MiB total. Exact readings/process list are in `current-hardware-preflight.json`. The list includes three Unity Editor processes, so a clean live load/inference check was deferred. WSL process inspection found no simulator or experiment worker. No unrelated process was stopped. Loaded current offload, free VRAM while loaded, current pinned server status and current effective settings remain **not measured**.',
        'Initial preflight found Unity Editor processes and deferred the live check. After the owner closed Unity, a fresh check cleared that gate. One request returned but the effective FA configuration did not match M4. The measured values and mismatch are appended below. No unrelated application was stopped by the probe.')
    report = report.replace('1. Resolve the competing GPU workload and perform the one-request Phase 0 hardware check; stop on digest/version mismatch or unresolved contention.',
        '1. **Partly completed:** Unity Editor closed, one request returned, pinned version/digest verified, isolated server stopped. Effective FA differed from M4; corrected hardware observation requires approval before another inference.')
    report = report.replace('No Git commit, public upload, new inference or automatic progression was performed.',
        'No Git commit, public upload or automatic progression was performed. One Qwen hardware-check inference request was completed.')
    report = report.replace('python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/render_report.py\n```',
        'python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/render_report.py\npython -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/hardware_report.py\n```')
    report_path.write_text(report.rstrip()+'\n\n'+section, encoding='utf-8')
    status = read(ROOT / 'status.json')
    status.update(live_hardware_check='RETURNED_WITH_CONFIGURATION_MISMATCH_CORRECTED_CHECK_NEEDS_APPROVAL', probe_inference_requests=1,
                  hardware_attempt=folder.name, setup_failures_preserved=2,
                  tool_dispatches=0, phase1='NOT_STARTED_SETTINGS_AND_THRESHOLDS_PENDING_CONFIRMATION')
    (ROOT / 'status.json').write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8')
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in ROOT.rglob('*') if p.is_file() and p != ROOT/'manifest.json'}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ('attempt', 'requests', 'layers_offloaded',
        'gpu_kv_mib', 'effective_flash_attention_enabled', 'ollama_ps')}, indent=2))


if __name__ == '__main__':
    main()
