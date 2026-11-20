"""Read-only evidence checks and descriptive tables; no prediction adjudication."""
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common import read


def main():
    state = read(ROOT / 'status.json')
    assert state['completed'] == 76 and state['status'] == 'COMPLETE'
    assert read(HERE / 'recovery-manager/status.json')['status'] == 'ALL_SCHEDULED_ATTEMPTS_RETAINED'
    report = sorted((HERE / 'reports').glob('*/analysis.json'))[-1]
    summary = read(report)
    effective = {r['trial_id']: r for r in summary['outcomes']}
    rows = [read(p) for p in sorted((ROOT / 'trials').glob('*/result.json'))]
    plan = read(ROOT / 'plan.json')
    assert len(rows) == len({r['id'] for r in rows}) == 76
    assert {r['id'] for r in rows} == {r['id'] for r in plan}
    assert sum(r['inference']['calls'] for r in rows) == state['live_model_requests'] == 200
    assert state['campaign']['infrastructure_retries'] == 0
    previous_files = {}
    phases = [ROOT] + sorted(HERE.glob('continuation-*'))
    for phase in phases:
        if not phase.is_dir():
            continue
        receipt = phase / 'CONTINUATION_RECORD.json'
        if receipt.exists():
            for name, digest in read(receipt)['previous_trial_hashes'].items():
                assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
                previous_files[name] = digest
        service = read(phase / 'phoenix-service.json')
        assert service['stopped'] is True
        auth_file = phase / ('launch-authorization-status.json' if phase == ROOT else 'authorization-status.json')
        auth = read(auth_file)
        assert auth['scopes_unchanged'] and auth['memory_cleanup'] == 'CLEARED' and auth['credential_retained']
    pairs = defaultdict(dict)
    starts = {}
    for row in rows:
        pairs[row['case']['case_id']][row['mode']] = row
        trace = read(ROOT / 'trials' / row['id'] / 'trace.json')
        roots = [s for s in trace['spans'] if s['name'] == 'g1.sol.heldout']
        assert len(roots) == 1
        starts[row['id']] = datetime.fromisoformat(roots[0]['start_time'].replace('Z', '+00:00'))
    gaps = []
    table = defaultdict(list)
    for case, pair in sorted(pairs.items()):
        assert set(pair) == {'primitives', 'macro'}
        primitive, macro = pair['primitives'], pair['macro']
        gap = abs((starts[primitive['id']] - starts[macro['id']]).total_seconds())
        gaps.append({'case_id': case, 'gap_seconds': gap, 'over_30_minutes': gap > 1800})
        if primitive['case']['kind'] == 'ladder':
            table[(primitive['case']['domain'], primitive['case']['native_depth'])].append(pair)
    inspection = []
    for (domain, depth), candidates in sorted(table.items()):
        matched = [p for p in candidates if all(effective[r['id']]['primary_status'] == 'PASS' for r in p.values())]
        costs = {m: {'calls': sum(p[m]['inference']['calls'] for p in matched),
                     'native': sum(len(p[m]['actor_records']) for p in matched)} for m in ('primitives', 'macro')}
        inspection.append({'domain': domain, 'depth': depth, 'scheduled_pairs': len(candidates),
            'matched_success_pairs': len(matched), 'excluded_pairs': len(candidates) - len(matched),
            'mean_call_saving': (costs['primitives']['calls'] - costs['macro']['calls']) / len(matched) if matched else None,
            'macro_primitive_native_ratio': costs['macro']['native'] / costs['primitives']['native'] if matched else None,
            'costs': costs})
    failures = [{'trial_id': r['id'], 'class': effective[r['id']]['censor_class'],
                 'requests': r['inference']['calls'], 'native': len(r['actor_records']),
                 'error_metadata': r['error_metadata']} for r in rows if r['error']]
    record = {'date': '2026-11-19', 'scope': 'Descriptive completion checks; no frozen prediction decisions',
        'scheduled_attempts': len(rows), 'charged_requests': 200, 'eligible_retries_used': 0,
        'no_replay': True, 'prior_trial_files_reverified': len(previous_files),
        'source_mismatches': summary['source_mismatches'],
        'campaign_seconds_including_pauses': state['campaign']['elapsed_seconds'],
        'all_owned_phoenix_services_stopped': True, 'all_scopes_unchanged': True,
        'all_memory_credentials_cleared': True, 'encrypted_opt_in_credential_retained': True,
        'pair_start_gaps': gaps, 'inspection_matched_success': inspection,
        'infrastructure_censored': failures, 'final_prediction_status': 'WITHHELD_PENDING_HUMAN_REVIEW'}
    output = HERE / 'completion-20261119'
    output.mkdir(exist_ok=False)
    (output / 'COMPLETION_CHECKS.json').write_text(json.dumps(record, indent=2) + '\n')
    lines = ['# G1 Sol completion and interruption addendum', '',
        'Date: **2026-11-19**. Execution complete; final semantic adjudication remains pending.', '',
        'All 76 unique scheduled trial identifiers are present. Their physical-request sum equals the cumulative checkpoint: 200/611. Eligible retry reserve used: 0/3. No failed/censored trial was replayed. Three continuations processed only unstarted cells under the original time origin.', '',
        f"Original campaign elapsed time including pauses/setup: **{record['campaign_seconds_including_pauses'] / 60:.2f} minutes**. This differs from summed per-task latency. Earlier retained trial files reverified: **{len(previous_files)}**. All 3,796 source/input digests match. All four owned Phoenix services stopped; credentials were cleared from memory, with the opted-in encrypted credential retained and scopes unchanged.", '',
        'All three interruptions were generic in-stream error events, not recorded HTTP statuses. The provider code/type and underlying cause are not recorded. One attempt is pre-output censored and two are post-action censored. No uncertain action was replayed.', '',
        '| Trial | Censoring class | Requests | Native operations |', '|---|---|---:|---:|']
    for r in failures:
        lines.append(f"| {r['trial_id']} | {r['class']} | {r['requests']} | {r['native']} |")
    lines += ['', 'Descriptive inspection tables below use only pairs with both arms already adjudicated PASS. Each depth/domain has only three scheduled pairs; missing pairs are explicit. These are not final prediction verdicts, bootstrap results or independent generalization evidence.', '',
        '| Domain | Native depth | Matched / scheduled pairs | Excluded | Mean calls saved | Macro/primitive native ratio |', '|---|---:|---:|---:|---:|---:|']
    for r in inspection:
        lines.append(f"| {r['domain']} | {r['depth']} | {r['matched_success_pairs']}/{r['scheduled_pairs']} | {r['excluded_pairs']} | {r['mean_call_saving']:.3f} | {r['macro_primitive_native_ratio']:.3f} |")
    flagged = [p for p in gaps if p['over_30_minutes']]
    lines += ['', f"Paired start-time gaps above the frozen 30-minute flag: **{len(flagged)}**. Maximum gap: **{max(p['gap_seconds'] for p in gaps):.2f} seconds**. Full gaps are retained in COMPLETION_CHECKS.json.", '',
        'Native-operation differences include repeated authorized reads. They are charged, even when not incorrect. The small-sample pattern must not be described as guaranteed native-work equality or general reliability improvement.', '',
        'Next gate: an eligible uninvolved human reviews the four new held-out clarification responses in the separately prepared blinded packet. Old development ratings are not reused. After actual submission intake and content binding, the unchanged frozen analysis can compute its V1/V2/V3, paired tables, group bootstrap and prediction statuses. No new Qwen/catalogue stage is launched here.']
    (output / 'COMPLETION_ADDENDUM.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'previous_files_verified': len(previous_files), 'pair_gap_flags': len(flagged), 'requests': 200}))


if __name__ == '__main__':
    main()
