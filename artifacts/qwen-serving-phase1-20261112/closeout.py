"""Read-only evidence checks and descriptive reporting after the serving run.

Does not invoke a model, execute tools, or modify frozen experiment sources.
"""
from pathlib import Path
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def verify(base, entries):
    mismatches = []
    for name, digest in entries.items():
        path = base / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            mismatches.append(name)
    return {'files': len(entries), 'mismatches': mismatches, 'pass': not mismatches}


def main():
    status = read(ROOT / 'status.json')
    assert status['status'] == 'COMPLETE', 'Wait for a completed coordinator checkpoint'
    analysis = read(ROOT / 'analysis.json')
    assert analysis['comparisons']['B']['complete']
    checks = {}
    frozen = read(ROOT / 'freeze.json')
    checks['phase1_frozen_sources'] = verify(ROOT, frozen['probe_files'])
    checks['continuation_sources'] = verify(ROOT / 'continuation', read(ROOT / 'continuation/freeze.json')['files'])
    checks['first_segment_snapshot'] = verify(ROOT / 'continuation/first-segment', read(ROOT / 'continuation/first-segment-manifest.json'))
    phase0 = ROOT.parent / 'qwen-timing-probe-20261112'
    checks['phase0_files'] = verify(phase0, read(phase0 / 'manifest.json'))
    m4 = ROOT.parent / 'macro-m4-20261027'
    checks['M4_evidence'] = verify(m4, read(phase0 / 'protected-m4-before.json'))
    checks['M4_sources'] = verify(WORKSPACE, read(m4 / 'freeze.json')['files'])
    checks['phase0_manifest_digest'] = {
        'pass': hashlib.sha256((phase0 / 'manifest.json').read_bytes()).hexdigest() == frozen['phase0_manifest_sha256']}
    cleanup = read(ROOT / 'post-run-process-check.json')
    checks['owned_server_cleanup'] = {'pass': cleanup['owned_servers_exited'],
                                     'active_model_server_processes': cleanup['active_model_server_processes']}
    reservations = list((ROOT / 'reservations').glob('*.json'))
    rows = []
    issues = []
    costs = {}
    for profile in ('A', 'B'):
        raw = [read(p) for p in sorted((ROOT / profile).glob('*/result.json'))]
        assert len([r for r in raw if r['stage'] != 'warmup']) == 14
        for r in raw:
            md, usage = r['metadata'], r['usage']
            if not (r['status'] == 'RETURNED' and usage['input_tokens'] == md['prompt_eval_count']
                    and usage['output_tokens'] == md['eval_count'] and r['tools_dispatched'] == 0
                    and r['prompt_count_matches'] and r['context_output_room'] >= 0):
                issues.append([profile, r['ordinal'], r['stage']])
            rows.append({
                'profile': profile, 'ordinal': r['ordinal'], 'stage': r['stage'], 'fixture': r['fixture'],
                'input_tokens': usage['input_tokens'], 'output_tokens': usage['output_tokens'],
                'generation_tokens_per_second': r['generation_tokens_per_second'],
                'client_seconds': r['client_seconds'],
                **{key + '_seconds': md[key] / 1e9 for key in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')},
                'finish_reason': md['done_reason'], 'cap_hit': r['cap_hit'],
                'matches_historical': r['matches_historical'],
                'tool_calls': json.dumps(r['tool_calls'], sort_keys=True),
                'invalid_tool_calls': json.dumps(r['invalid_tool_calls'], sort_keys=True),
                'prompt_count_matches': r['prompt_count_matches'], 'context_output_room': r['context_output_room']})
        measured = [r for r in raw if r['stage'] != 'warmup']
        costs[profile] = {}
        for label, subset in [('all_requests', raw), ('measured_requests', measured)]:
            costs[profile][label] = {
                'requests': len(subset),
                'input_tokens': sum(r['usage']['input_tokens'] for r in subset),
                'output_tokens': sum(r['usage']['output_tokens'] for r in subset),
                'client_seconds': sum(r['client_seconds'] for r in subset),
                **{key + '_seconds': sum(r['metadata'][key] / 1e9 for r in subset)
                   for key in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')},
                'invalid_call_records': sum(bool(r['invalid_tool_calls']) for r in subset),
                'multiple_tool_call_records': sum(len(r['tool_calls']) > 1 for r in subset)}
    checks['usage_prompt_and_dispatch_checks'] = {'records': len(rows), 'issues': issues, 'pass': not issues}
    paired_issues = []
    for ordinal in range(1, 15):
        left = read(ROOT / 'A' / f'{ordinal:02d}' / 'request.json')
        right = read(ROOT / 'B' / f'{ordinal:02d}' / 'request.json')
        if left != right:
            paired_issues.append(ordinal)
    checks['identical_paired_API_requests'] = {'pairs': 14, 'mismatches': paired_issues, 'pass': not paired_issues}
    checks['resource_accounting'] = {
        'reservations': len(reservations), 'returned_records': len(rows),
        'status_charged': status['charged_requests'], 'cap': 45,
        'pass': len(reservations) == len(rows) == status['charged_requests'] <= 45
            and sum(r['output_tokens'] for r in rows) == status['known_output_tokens']
            and sum(r['input_tokens'] for r in rows) == status['known_input_tokens']
            and status['unreturned_output_upper_bound'] == 0}
    checks['all_pass'] = all(c['pass'] for c in checks.values())
    write('closeout-validation.json', checks)
    assert checks['all_pass'], 'Evidence checks failed; inspect closeout-validation.json'
    write('cost-summary.json', costs)
    with (ROOT / 'request-summary.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    comp = analysis['comparisons']['B']
    text = ['# Qwen serving Phase 1: completed results', '', 'Date: **2026-11-13**.', '',
        '**Completed A/B replay screen.** These are known-input serving observations, not new robotic task scores. '
        'M4, Baseline v1 and M1-M5 results are preserved.', '',
        f'B reached **{comp["speed_ratio"]:.3f} times A throughput** against the prespecified 1.5-times requirement. '
        f'Its family tool-call agreement was **{comp["family_agreements"]}/10** against the 9/10 requirement. '
        f'The candidate screen **{"passed" if comp["candidate"] else "failed"}**. '
        'See [recorded Stage 2 decision](stage2-decision.json) for why C was not run.', '',
        '## Design and accounting', '',
        'A: original auto/enabled Flash Attention, f16 KV, 8192 context. '
        'B: explicit enabled Flash Attention, q8_0 K/V, same 8192 context. '
        'Ollama 0.40.6, Qwen3.5:9b Q4_K_M, temperature 0, seed 42, think=false, '
        '1024 generated-token cap per call, same recorded messages/tools and server prefix-cache policy. '
        'Ten first-turn family inputs plus the 4027-token longest-input safety fixture; three predetermined repeats. '
        'Primary throughput is the median of the eleven unique inputs, excluding repeats and warm-ups.', '',
        f'Actual cost: **{len(rows)} charged requests, {status["known_input_tokens"]} input tokens, '
        f'{status["known_output_tokens"]} returned output tokens, zero unreturned requests**. '
        'No robot tool dispatches, hosted model calls or OAuth operations. '
        'The original 45-request ceiling was retained. Reservation filenames are not chronological: '
        '31 is the recovery warm-up; the later B measured requests occupy 17-30. Count files, not the largest filename.', '',
        'The original B warm-up returned successfully, but the observer wrongly required the literal log phrase '
        '`Flash Attention enabled`. B instead records `flash_attn = enabled`; both K and V were q8_0. '
        'The first segment stopped on this validator error. Original sources, outputs and the failed status/report '
        'are retained. A separately frozen observer correction continued only unstarted B measured requests, '
        'with one additional discarded warm-up. Thus A has 15 returned requests and B has 16; each has 14 measured. '
        'This is a declared infrastructure deviation, not a clean uninterrupted original-protocol run. '
        'The frozen automatic report still labels its denominator /15; this closeout supplies the actual accounting. '
        'The fixed global deadline included the interruption. '
        'If B had passed, the full 15-request C block would not have fitted the remaining 14 slots.', '',
        '## Serving and behavior results', '',
        '| Measure | A | B |', '|---|---:|---:|']
    for label, key in [('Returned requests', 'returned'), ('Measured requests', 'measured'),
                       ('Unique-input median generation tokens/s', 'median_unique_tokens_per_second'),
                       ('Unique-input minimum tokens/s', 'min_unique_tokens_per_second'),
                       ('Unique-input maximum tokens/s', 'max_unique_tokens_per_second'),
                       ('Historical family-call matches /10', 'historical_family_matches'),
                       ('Repeat agreements /3', 'repeat_agreements'), ('Measured output-cap hits /14', 'measured_cap_hits')]:
        values = [analysis['profiles'][p][key] for p in ('A', 'B')]
        values = [f'{v:.3f}' if isinstance(v, float) else str(v) for v in values]
        text.append(f'| {label} | {values[0]} | {values[1]} |')
    text += ['', f'B versus A family agreement: {comp["family_agreements"]}/10; safety-input agreement: '
             f'{comp["safety_input_agrees"]}; prompt-equivalence/output-room check: '
             f'{comp["prompt_equivalence_and_room_pass"]}. '
             'Agreement compares parsed ordered tool names and arguments, excluding IDs. '
             'An empty-call match is not proof of correct prose, and matching a wrong historical call is not success. '
             'All mismatches, including repeats, appear in [full output comparisons](MISMATCHES.md).', '',
             '## Hardware and costs', '',
             '| Measure | A | B |', '|---|---|---|']
    hardware = {p: read(ROOT / p / 'hardware.json') for p in ('A', 'B')}
    for label, key in [('GPU offload layers', 'offload_layers'), ('GPU KV allocation MiB', 'gpu_KV_mib'),
                       ('Warm-up model-load seconds', 'warmup_load_seconds'), ('Effective KV precision', 'effective_KV')]:
        text.append(f'| {label} | {hardware["A"][key]} | {hardware["B"][key]} |')
    for p in ('A', 'B'):
        text += ['', f'{p} physical NVIDIA observation after warm-up (not a peak or directly synchronized pair):',
                 '```text', hardware[p]['physical_gpu_reading'].strip(), '```']
    text += ['', 'The GPU KV saving was 60 MiB; the offloaded layer count did not increase. '
             'Physical used/free readings include desktop and other allocations and are snapshots. '
             'Ollama ps reports an allocation estimate, not an independent measurement of physical residency.', '',
             '| Measured-block cost, 14 requests each | A | B |', '|---|---:|---:|']
    for key in ('input_tokens', 'output_tokens', 'client_seconds', 'total_duration_seconds',
                'load_duration_seconds', 'prompt_eval_duration_seconds', 'eval_duration_seconds',
                'invalid_call_records', 'multiple_tool_call_records'):
        vals = [costs[p]['measured_requests'][key] for p in ('A', 'B')]
        vals = [f'{v:.3f}' if isinstance(v, float) else str(v) for v in vals]
        text.append(f'| {key} | {vals[0]} | {vals[1]} |')
    text += ['', 'For these fourteen replay requests, B generated '
             f'{100 * (costs["B"]["measured_requests"]["output_tokens"] / costs["A"]["measured_requests"]["output_tokens"] - 1):.1f}% '
             'more output tokens. Summed measured client request time was '
             f'{costs["A"]["measured_requests"]["client_seconds"]:.3f} seconds for A and '
             f'{costs["B"]["measured_requests"]["client_seconds"]:.3f} seconds for B. '
             'These are replay-request totals, not completed robotic task times.']
    text += ['', 'Provider total_duration and client monotonic timings remain distinct cost views. '
             'Their difference is not asserted to be exact framework overhead; Phase 0 recorded clock inconsistencies. '
             'Token totals also reflect different generated responses, not just serving speed. '
             'Warm-up-inclusive costs are retained in [cost-summary.json](cost-summary.json); '
             'every request is listed in [request-summary.csv](request-summary.csv).', '',
             '## Matched request detail', '',
             '| Ordinal / fixture | A tokens/s | B tokens/s | A output tokens | B output tokens | Parsed calls agree |',
             '|---|---:|---:|---:|---:|---|']
    paired = {p: {r['ordinal']: r for r in rows if r['profile'] == p and r['stage'] != 'warmup'} for p in ('A', 'B')}
    for ordinal in range(1, 15):
        a, b = paired['A'][ordinal], paired['B'][ordinal]
        text.append(f'| {ordinal}: {a["fixture"]} ({a["stage"]}) | '
                    f'{a["generation_tokens_per_second"]:.3f} | {b["generation_tokens_per_second"]:.3f} | '
                    f'{a["output_tokens"]} | {b["output_tokens"]} | {a["tool_calls"] == b["tool_calls"]} |')
    text += ['',
             '## Interpretation and limitations', '',
             'This is a small exploratory screen on previously observed M4 inputs. It has one A block followed '
             'by B, an interruption/reload, and three stability repeats rather than independent repeated blocks. '
             'Order, thermals, cache history and response-content differences limit causal attribution. '
             'No confidence interval, general correctness claim, or Qwen/Sol parity claim is justified. '
             'Quantizing KV can change outputs despite unchanged weight digest. No reasoning-on, prompt repair, '
             'weight quantization change, Gazebo rerun or selection-scaffolding condition was tested.', '',
             'Keep the original serving reference unless a separately justified experiment establishes a better '
             'configuration. A failed cheap-serving screen supports stopping this path under its gates; it does '
             'not establish the best possible Qwen configuration or a fixed model capability ceiling. '
             'Any future intent/schema/examples or thinking-mode study remains a separate prospective decision.', '',
             '## Evidence protection', '',
             f'Checks passed: {checks["M4_evidence"]["files"]} protected M4 files, '
             f'{checks["M4_sources"]["files"]} M4 frozen sources, '
             f'{checks["phase0_files"]["files"]} Phase 0 manifest entries, '
             f'{checks["phase1_frozen_sources"]["files"]} Phase 1 frozen files, '
             f'{checks["continuation_sources"]["files"]} continuation files and '
             f'{checks["first_segment_snapshot"]["files"]} first-segment snapshot files. '
             'All returned usage counts match provider metadata; prompts retain expected counts and output room; '
             'reservation and output totals match the checkpoint. See [validation](closeout-validation.json). '
             'Owned model servers were confirmed stopped in [process check](post-run-process-check.json). '
             'Evidence remains local; no publication or Git push was performed.', '',
             'See [original protocol](PROTOCOL.md), [continuation declaration](continuation/CONTINUATION_NOTE.md), '
             '[machine analysis](analysis.json), profile request/response/result records and owned-server logs.']
    (ROOT / 'COMPLETED_REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
    print(json.dumps({'validation_pass': checks['all_pass'], 'charged_requests': len(rows),
                      'speed_ratio': comp['speed_ratio'], 'candidate': comp['candidate']}))


if __name__ == '__main__':
    main()
