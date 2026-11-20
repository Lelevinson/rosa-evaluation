"""Verify, without altering, the separate review's sealed artifacts and input hashes."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE3 = HERE.parent
WORKSPACE = STAGE3.parents[4]
REVIEW = STAGE3 / 'scorer-review/astra-review-20261115'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    seal = read(REVIEW / 'seal-manifest.json')
    inputs = read(REVIEW / 'input-manifest.json')
    summary = read(REVIEW / 'review-summary.json')
    for mapping in (seal['artifacts_sha256'], inputs['input_sha256']):
        for name, expected in mapping.items():
            assert digest(WORKSPACE / name) == expected, name
    assert summary['cases'] == 41
    assert summary['matched_original_expectations'] == 29
    assert summary['mismatches_preserved'] == 12
    assert summary['scorer_sha256_before'] == summary['scorer_sha256_after'] == seal['scorer_sha256']
    assert not summary['launch_clearance']
    assert not summary['source_repairs']
    receipt = {
        'date_local': '2026-11-15',
        'passed': True,
        'sealed_artifacts_verified': len(seal['artifacts_sha256']),
        'unchanged_review_inputs_verified': len(inputs['input_sha256']),
        'seal_sha256': digest(REVIEW / 'seal-manifest.json'),
        'reviewer': summary['reviewer'],
        'cases': summary['cases'],
        'G_e_clearance': summary['G_e_clearance'],
        'launch_clearance': False,
        'experimental_backend_requests': 0,
        'note': 'Artifact integrity verification is not scorer or study launch clearance.'
    }
    (HERE / 'review-verification.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
