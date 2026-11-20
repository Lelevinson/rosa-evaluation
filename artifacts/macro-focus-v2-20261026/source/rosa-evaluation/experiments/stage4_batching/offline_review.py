"""Read-only consistency review of frozen sources, saved state audits and traces.

Uses no Phoenix server, OAuth session, model or running ROS graph. This is a
post-run replay of the recorded audit logic, not independently authored scoring.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .audit import batching_check
from .runner import CAMPAIGN
from . import reconcile_audit
from .trace_accounting import counts
from ..phase4.audit import check as reliability_check
from tools.phoenix.inspect_trace import summarize


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, default=CAMPAIGN)
    args = parser.parse_args()
    folder = args.campaign.resolve()
    reconciliation = read(folder / 'audit-reconciliation.json')
    if not reconciliation['all_records_accounted']:
        raise RuntimeError('unaccounted_audit_mismatches')
    for name, wanted in reconciliation['original_file_sha256'].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != wanted:
            raise RuntimeError('original_audit_or_result_hash_mismatch:' + name)
    if hashlib.sha256(Path(reconcile_audit.__file__).read_bytes()).hexdigest() != reconciliation['analysis_source_sha256']:
        raise RuntimeError('reconciliation_code_identity_mismatch')
    frozen = read(folder / 'freeze.json')
    for name, wanted in frozen['source_sha256'].items():
        actual = hashlib.sha256((folder / 'source' / name).read_bytes()).hexdigest()
        if actual != wanted:
            raise RuntimeError('archived_source_hash_mismatch:' + name)
    if hashlib.sha256((folder / 'jobs.json').read_bytes()).hexdigest() != frozen['jobs_sha256']:
        raise RuntimeError('jobs_hash_mismatch')
    policy_folder = folder.parent / 'stage4-policy-20261021'
    calibration_name = 'rosa-evaluation/artifacts/stage4-policy-20261021/ros-calibration/calibration.json'
    calibration_sha = hashlib.sha256((policy_folder / 'ros-calibration/calibration.json').read_bytes()).hexdigest()
    if calibration_sha != read(policy_folder / 'freeze.json')['source_sha256'][calibration_name]:
        raise RuntimeError('historical_calibration_hash_mismatch')
    reviewed, gap_count = {}, 0
    reconciled = {(r['backend'], r['run_id']): r for r in reconciliation['records']}
    for backend in ('siwc', 'ollama'):
        batch = read(folder / backend / 'result.json')
        audit = read(folder / backend / 'audit.json')
        if batch['status'] != 'COMPLETE' or len(batch['trials']) != 80:
            raise RuntimeError('incomplete_backend:' + backend)
        saved = {r['run_id']: r for r in audit['records']}
        run_ids = [r['run_id'] for r in batch['trials']]
        if len(set(run_ids)) != 80 or set(saved) != set(run_ids):
            raise RuntimeError('audit_trial_identity_mismatch:' + backend)
        for row in batch['trials']:
            trial = folder / backend / 'trials' / row['run_id']
            if read(trial / 'result.json') != row:
                raise RuntimeError('trial_batch_result_mismatch:' + row['run_id'])
            evidence = read(trial / 'evidence.json')
            state = reliability_check(row, evidence) if row['stage'] == 'reliability' else batching_check(row, evidence)
            trace = read(trial / 'trace.json')
            trace_summary = summarize(trace['spans'])
            actors = counts(trace['spans'])
            record = saved[row['run_id']]
            if not (state['verified']
                    and state == record['state_audit']
                    and trace_summary == trace['summary'] == record['trace_summary']
                    and actors == record['actor_accounting']):
                raise RuntimeError('saved_audit_replay_mismatch:' + row['run_id'])
            if not record['verified']:
                if row['stage'] != 'reliability' or not row['orchestrator_recovery']:
                    raise RuntimeError('unexplained_frozen_audit_failure:' + row['run_id'])
                gap = reconcile_audit.guard_gap_checks(row, evidence, trace, trace_summary, actors)
                if not gap['accounted'] or gap != reconciled[(backend, row['run_id'])]['known_trace_gap']:
                    raise RuntimeError('reconciliation_replay_mismatch:' + row['run_id'])
                gap_count += 1
            elif not record['trace_audit']:
                raise RuntimeError('inconsistent_recorded_audit:' + row['run_id'])
        reviewed[backend] = {'reviewed_trials': len(run_ids),
            'strict_passes': sum(r['strict_contract_pass'] for r in batch['trials']),
            'combined_passes': sum(r['combined_pass'] for r in batch['trials']),
            'model_requests': batch['total_model_calls']}
    if gap_count != reconciliation['known_gap_trials']:
        raise RuntimeError('reconciliation_gap_count_mismatch')
    print(json.dumps({'status': 'PASSED_WITH_DOCUMENTED_TRACE_GAPS',
        'known_trace_gap_trials': gap_count, 'full_tool_span_coverage': False,
        'archived_sources_verified': len(frozen['source_sha256']),
        'historical_calibration_verified': True,
        'backends': reviewed, 'new_model_requests': 0,
        'scope': 'Saved audit consistency replay; not independent authorship or fresh ROS/Phoenix observations.'}, indent=2))


if __name__ == '__main__':
    main()
