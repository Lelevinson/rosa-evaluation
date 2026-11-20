"""Retain and summarize the authorized corrected request stopped for contention."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    reservation = read(ROOT / 'corrected-hardware-dispatch-reservation.json')
    folder = ROOT / reservation['attempt']
    result = read(folder / 'result.json')
    attempt = read(folder / 'attempt-status.json')
    stop = read(folder / 'contention-stop.json')
    assert result['status'] == 'FAILED_OR_CENSORED_NO_RETRY'
    assert result['requests_reserved'] == 1 and result['requests_returned'] == 0
    assert result['tools_dispatched'] == 0
    log = (folder / 'server-stderr.log').read_text(encoding='utf-8', errors='replace')
    layers = re.findall(r'offloaded (\d+)/(\d+) layers to GPU', log)
    progress = [int(n) for n in re.findall(r'n_gen\s*=\s*(\d+)', log)]
    selected_lines = [{'line': i+1, 'text': line} for i, line in enumerate(log.splitlines())
        if any(s in line for s in ('offloaded', 'KV buffer size', 'K (f16)',
            'Flash Attention enabled', 'flash_attn ', 'n_batch ', 'n_ubatch ',
            'compute buffer size', 'model buffer size', 'n_gen ='))]
    matched = bool('Flash Attention enabled' in log and '--flash-attn auto' in log
                   and 'K (f16)' in log and 'V (f16)' in log)
    old = read(ROOT / 'retained-before-corrected-check.json')
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in old.items())
    summary = {'date': '2026-11-12', 'attempt': folder.name,
        'authorization': read(ROOT / 'corrected-check-authorization.json'),
        'status': 'STOPPED_FOR_UNRESOLVED_GPU_CONTENTION_NO_RETRY',
        'request_reserved': 1, 'request_returned': 0, 'total_probe_requests_reserved': 2,
        'tools_dispatched': 0, 'final_usage': None, 'output_upper_bound': 1024,
        'server_progress_generated_token_lower_bound': max(progress) if progress else None,
        'effective_FA_auto_and_f16_verified': matched,
        'layer_offload': list(map(int, layers[-1])) if layers else None,
        'loaded_ollama_ps': None, 'loaded_free_vram': None, 'final_generation_throughput': None,
        'source_excerpts': selected_lines, 'contention_stop': stop,
        'retained_prior_attempt_files_unchanged': len(old), 'phase1_started': False,
        'protocol_deviation': 'The request launched before the new GPU-engine preflight result was fully reviewed. Active browser video/3D activity then triggered a conservative stop. Adapter-specific exclusion was not established; no clean speed claim.'}
    (ROOT / 'corrected-hardware-summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    section = '\n'.join([
        '## Latest outcome: authorized corrected request stopped for GPU activity', '',
        '**2026-11-12: the owner approved one additional corrected request. That allowance was used once and is now spent. Phase 1 remains unstarted.** This section supersedes earlier pending-approval and one-request-only status statements for the live hardware work; original observations remain retained.', '',
        'Attempt hardware-04 used the original unset/auto Flash Attention policy. Its actual runtime log confirms **Flash Attention enabled**, **f16 KV cache**, **8192 context**, **17/33 layers offloaded**, and 512-sized runtime batches. Version and full model digest match M4. Those are direct partial hardware observations, not estimates.', '',
        'The preflight GPU samples were 24%, 40% and 31% utilization. A subsequent Windows GPU-engine sample showed Chrome video-decode and 3D activity in addition to desktop work. The probe was launched before that sample was fully reviewed, contrary to the intended sequential idle gate. Adapter-specific absence of contention was not established. The owned request/server tree was stopped conservatively; Chrome and other applications were left running. This is an execution/protocol exception, not a Qwen task failure.', '',
        f'The client recorded `{result["error_type"]}` after the server was stopped, with **no complete model response**. The server progress log shows at least **{summary["server_progress_generated_token_lower_bound"]} generated tokens**, but this is a lower bound, not final returned usage. Charge the request at its full **1024-token upper bound** for resource accounting. No inference retry occurred.', '',
        'The interim log prints generation-rate samples, but there is no final `eval_duration`/`eval_count` pair for this request. Do not substitute the interim rates into the profile comparison or call them a new measured Qwen speed. Final tool-call agreement, output-cap outcome, loaded `ollama ps` output and free VRAM while loaded are **not obtained** for this corrected request.', '',
        'The first mismatched request remains exactly as originally recorded (33 returned tokens, FA disabled). Across both charged requests there are **33 known returned output tokens plus at most 1024 unreturned tokens**. Server progress supplies an additional lower-bound observation, not an exact total. No Sol requests, robot commands, Gazebo runs or Phase 1 calls occurred.', '',
        'Both the first mismatched request and this contention-stopped request are excluded from any claim of a clean historical-baseline reproduction or A/B speed improvement. Current partial logs support 17/33 offload and a 128 MiB GPU KV allocation, consistent with the historical memory evidence. They do not justify a measured benefit for cache quantization or lower context.', '',
        'The archived 40-trial/144-call analysis remains complete. **A clean live baseline observation remains incomplete.** Continuation requires a quiet GPU interval (including pausing browser video/other GPU-heavy work), a fresh preflight reviewed before launch, and an explicitly bounded new allowance. No further call is scheduled or authorized here. Stage 1 settings/threshold confirmation is still separate.', '',
        'Evidence: `corrected-hardware-summary.json`, `hardware-04/`, `corrected-hardware-dispatch-reservation.json`, `corrected-check-authorization.json`, `corrected-check-idle-samples.json`, `corrected-check-gpu-engine-samples.json`, and `PRE_RUN_AMENDMENT_02.md`. The original pre-run note and both amendment hashes were checked before dispatch. The previous attempt files passed preservation checks.',
    ])+'\n'
    (ROOT / 'CORRECTED_HARDWARE_CHECK_REPORT.md').write_text('# Corrected Phase 0 hardware request: contention stop\n\n'+section, encoding='utf-8')
    report_path = ROOT / 'PHASE0_REPORT.md'
    report = report_path.read_text(encoding='utf-8')
    report = report.split('\n## Latest outcome: authorized corrected request stopped for GPU activity')[0]
    old_header = '**Archived Phase 0 analysis complete; one live request retained with a serving-configuration mismatch. A corrected hardware check needs approval. Phase 1 not started.**'
    new_header = '**Archived analysis complete. Two live requests charged: one serving mismatch and one authorized correction stopped for GPU activity. A clean live baseline remains incomplete; Phase 1 not started.**'
    report = report.replace(old_header, new_header)
    report = report.replace('One isolated Qwen inference request for the hardware check; zero Sol requests, robot commands or simulator runs.',
        'Two Qwen inference requests charged for the hardware work: one returned under mismatched settings and one stopped for unresolved GPU activity. Zero Sol requests, robot commands or simulator runs.')
    report = report.replace('python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/hardware_report.py\n```',
        'python -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/hardware_report.py\npython -B rosa-evaluation/artifacts/qwen-timing-probe-20261112/corrected_hardware_report.py\n```')
    report = report.replace('One Qwen hardware-check inference request was completed.',
        'Two Qwen hardware-check requests were charged; one returned and one was stopped before a complete response.')
    report_path.write_text(report.rstrip()+'\n\n'+section, encoding='utf-8')
    status = read(ROOT / 'status.json')
    status.update(live_hardware_check='INCOMPLETE_CORRECTED_REQUEST_STOPPED_FOR_GPU_ACTIVITY',
        probe_inference_requests=2, known_returned_output_tokens=33,
        unreturned_output_upper_bound=1024, hardware_attempt=folder.name,
        corrected_request_authorized=True, correction_allowance_remaining=0,
        effective_FA_auto_and_f16_verified=matched, protocol_exception_recorded=True,
        further_inference_scheduled=False, phase1='NOT_STARTED_SETTINGS_AND_THRESHOLDS_PENDING_CONFIRMATION')
    (ROOT / 'status.json').write_text(json.dumps(status, indent=2)+'\n', encoding='utf-8')
    manifest = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in ROOT.rglob('*') if p.is_file() and p != ROOT/'manifest.json'}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('status','total_probe_requests_reserved',
        'effective_FA_auto_and_f16_verified','layer_offload','server_progress_generated_token_lower_bound')}, indent=2))


if __name__ == '__main__':
    main()
