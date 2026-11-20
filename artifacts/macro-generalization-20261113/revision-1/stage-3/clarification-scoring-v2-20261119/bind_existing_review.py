"""Bind the real returned four-case review without modifying its original bytes."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
from adjudication import VERSION, ELIGIBILITY, content_binding, validate_bundle, evaluate_dataset

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REV = STAGE.parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load_rows():
    return [json.loads(p.read_text(encoding='utf-8')) for name in ('stage-2', 'stage-2-continuation-1')
            for p in sorted((REV/name/'trials').glob('*/result.json'))]

def main():
    output = HERE/'LEV_ACTUAL_REVIEW_BOUND.json'
    if output.exists():
        raise SystemExit('Preserve existing binding; do not overwrite')
    intake = STAGE/'human-review-20261119'
    receipt = json.loads((intake/'INTAKE_RECEIPT.json').read_text(encoding='utf-8'))
    submitted = (intake/'lev ratings.zip').read_bytes()
    assert digest(submitted) == receipt['submission_zip_sha256']
    with zipfile.ZipFile(io.BytesIO(submitted)) as z:
        assert z.testzip() is None
        csv_bytes = z.read('ratings-empty.csv')
        declaration_bytes = z.read('REVIEWER_DECLARATION.md')
    for name, raw in [('ratings-empty.csv', csv_bytes), ('REVIEWER_DECLARATION.md', declaration_bytes)]:
        assert digest(raw) == receipt['original_members_sha256'][name]
        assert (intake/'submission-original'/name).read_bytes() == raw
    declaration = declaration_bytes.decode(receipt['declaration_decoding_for_validation'])
    assert declaration.count(': YES') == 5 and 'Reviewer name: Levinson' in declaration
    assert '2026/11/19' in declaration and 'TEAMMATE of the group' in declaration
    ratings = list(csv.DictReader(io.StringIO(csv_bytes.decode('utf-8-sig'), newline='')))
    assert len(ratings) == 4 and {r['case_id'] for r in ratings} == {'C01', 'C02', 'C03', 'C04'}
    rows = load_rows()
    by_id = {r['id']: r for r in rows}
    assert len(rows) == len(by_id) == 36
    key = json.loads((STAGE/'clarification-review/private-key/packet-map.json').read_text(encoding='utf-8'))
    packet_raw = (STAGE/'resolution-guide-20261117/G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip').read_bytes()
    assert digest(packet_raw) == receipt['source_packet_sha256']
    records = []
    with zipfile.ZipFile(io.BytesIO(packet_raw)) as z:
        assert z.testzip() is None
        manifest = json.loads(z.read('PACKET_MANIFEST.json'))
        assert all(digest(z.read(n)) == d for n, d in manifest['files'].items())
        rubric_digest = digest(z.read('RUBRIC.md'))
        for rating in ratings:
            case_id = rating['case_id']
            row = by_id[key[case_id]['trial_id']]
            assert key[case_id]['model'] == row['model'] and key[case_id]['condition'] == row['mode']
            assert row['case']['kind'] == 'ambiguous'
            # Normalize file newlines only to compare rendered packet content to
            # source. Bind and preserve exact original transcript bytes separately.
            expected = (f'# {case_id}\n\nUser request:\n\n{row["case"]["request"]}\n\n'
                        f'Assistant response:\n\n{row["answer"]}\n\nRecorded tool executions: '
                        f'{len(row["tool_inputs"])}. Native attempts: {len(row["actor_records"])}.\n')
            normalize = lambda s: s.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
            transcript_raw = z.read(case_id+'.md')
            assert normalize(transcript_raw.decode('utf-8')) == normalize(expected)
            assert rating['reviewer_name'] == 'Levinson'
            records.append(dict(trial_id=row['id'], packet_case_id=case_id,
                reviewer=rating['reviewer_name'], review_date='2026-11-19',
                appropriate_clarification=rating['appropriate_clarification'],
                no_unauthorized_action=rating['no_unauthorized_action'], reason=rating['reason'],
                eligibility={k: True for k in ELIGIBILITY},
                eligibility_basis='Actual returned declaration; self-attestation, not independent verification',
                declared_relationship='TEAMMATE of the group', binding=content_binding(row, rubric_digest),
                provenance=dict(submission_sha256=digest(submitted), csv_sha256=digest(csv_bytes),
                    declaration_sha256=digest(declaration_bytes), transcript_sha256=digest(transcript_raw))))
    bundle = dict(version=VERSION, rubric_sha256=rubric_digest, records=records,
                  scope='Actual four-case G1 Stage2 review; no synthetic ratings or new held-out judgments',
                  original_packet_sha256=digest(packet_raw),
                  identity_basis='Original C01-C04 mapping and exact issued content; no reviewer cryptographic signature')
    validate_bundle(bundle, rubric_digest)
    outcomes = evaluate_dataset(rows, bundle, rubric_digest)
    assert sum(o['human_review_status'] == 'REVIEWED_PASS' for o in outcomes) == 4
    output.write_text(json.dumps(bundle, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'actual_ratings_bound': len(records), 'source_rendering_matches': True,
                      'original_submission_unchanged': True, 'model_requests': 0}))

if __name__ == '__main__':
    main()
