"""Read immutable v1 records; write explicitly retrospective additional metrics."""
import argparse
import hashlib
import json
from pathlib import Path
from .contract import assess


def main():
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=root / 'reports/clean-stage1-4-20261021-r1')
    parser.add_argument('--output', type=Path, default=root / 'reports/phase4-v2/retrospective.json')
    args = parser.parse_args()
    campaign = json.loads((args.evidence / 'campaign.json').read_text())
    archive = root / 'reports/ROSA_STAGE1_TO_4_CLEAN_RERUN_2026-10-21.zip'
    before = hashlib.sha256(archive.read_bytes()).hexdigest()
    result = {'type': 'retrospective_additional_contract_checks_not_a_rerun',
              'original_scores_unchanged': True, 'source_campaign': campaign['campaign'], 'backends': {}}
    for backend in ('local', 'hosted'):
        batch_id = campaign['steps'][backend]['run_id']
        batch = json.loads((args.evidence / 'evidence/runs' / batch_id / 'result.json').read_text())
        records = []
        for row in batch['trials']:
            evidence = json.loads((args.evidence / 'evidence/runs' / row['run_id'] / 'oracle.json').read_text())
            records.append({'run_id': row['run_id'], 'scenario_id': row['scenario_id'],
                'policy': row['policy'], 'operational_completion': not row['api_failed'],
                **assess(evidence['oracle'], evidence['calls'], row['score'])})
        baseline = [r for r in records if r['policy'] == 'none']
        result['backends'][backend] = {'baseline_attempts': len(baseline),
            'strict_contract_completed': sum(r['strict_contract_pass'] and r['operational_completion'] for r in baseline),
            'trials_without_compliant_report': sum(not r['report_arguments_compliant'] for r in baseline),
            'trials_with_invalid_report_arguments': sum(bool(r['report_argument_errors']) for r in baseline),
            'critical_prerequisite_violations': sum(r['critical_prerequisite_violations'] for r in baseline),
            'records': records}
    result['v1_archive_sha256_before'] = before
    result['v1_archive_sha256_after'] = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert before == result['v1_archive_sha256_after']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({b: {k: v for k, v in r.items() if k != 'records'}
                      for b, r in result['backends'].items()}, indent=2))


if __name__ == '__main__':
    main()
