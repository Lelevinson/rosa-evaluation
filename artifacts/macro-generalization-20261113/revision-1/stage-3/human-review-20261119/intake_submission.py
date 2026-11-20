"""Preserve and validate a real submission; no experiment scoring changes."""
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
SOURCE = Path(r'C:\Users\user\Downloads\lev ratings.zip')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    raw = SOURCE.read_bytes()
    assert sha(raw) == '9606fb256fa1c5113cd1641d9b18738494cc3327941f17265115d6c414e2e77f'
    target = HERE / 'lev ratings.zip'
    assert not target.exists(), 'Preserve prior intake instead of overwriting'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'ratings-empty.csv', 'REVIEWER_DECLARATION.md'}
        returned = {n: z.read(n) for n in z.namelist()}
    rows = list(csv.DictReader(io.StringIO(returned['ratings-empty.csv'].decode('utf-8-sig'), newline='')))
    assert len(rows) == 4 and {r['case_id'] for r in rows} == {'C01', 'C02', 'C03', 'C04'}
    assert all(set(r) == {'case_id', 'reviewer_name', 'appropriate_clarification', 'no_unauthorized_action', 'reason'} for r in rows)
    assert all(r['reviewer_name'] == 'Levinson' and r['reason'].strip() for r in rows)
    assert all(r[k] in {'YES', 'NO', 'CANNOT_JUDGE'} for r in rows for k in ('appropriate_clarification', 'no_unauthorized_action'))
    packet_path = STAGE / 'resolution-guide-20261117/G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip'
    packet_raw = packet_path.read_bytes()
    assert sha(packet_raw) == '890390f8c8c9f1debdeaeed09e283a99f7aef0167d153bd3cdbada5de4332b3f'
    with zipfile.ZipFile(io.BytesIO(packet_raw)) as z:
        assert z.testzip() is None
        manifest = json.loads(z.read('PACKET_MANIFEST.json'))
        for name, digest in manifest['files'].items():
            assert sha(z.read(name)) == digest, name
        reviewed_hashes = {n: sha(z.read(n)) for n in ['C01.md', 'C02.md', 'C03.md', 'C04.md', 'RUBRIC.md']}
    # Check the unaltered declaration manually as evidence; do not invent a signature.
    declaration_raw = returned['REVIEWER_DECLARATION.md']
    try:
        declaration = declaration_raw.decode('utf-8-sig')
        encoding = 'utf-8-sig'
    except UnicodeDecodeError:
        declaration = declaration_raw.decode('cp1252')
        encoding = 'cp1252'
    assert 'Reviewer name: Levinson' in declaration
    assert '2026/11/19' in declaration
    assert declaration.count(': YES') == 5
    assert 'TEAMMATE of the group' in declaration
    mapping = json.loads((STAGE / 'clarification-review/private-key/packet-map.json').read_text(encoding='utf-8'))
    assert set(mapping) == {r['case_id'] for r in rows}
    target.write_bytes(raw)
    submission_dir = HERE / 'submission-original'
    submission_dir.mkdir(exist_ok=False)
    for name, data in returned.items():
        (submission_dir / name).write_bytes(data)
    receipt = {
        'intake_date': '2026-11-19',
        'reviewer': 'Levinson',
        'review_date_verbatim': '2026/11/19',
        'review_date_normalized': '2026-11-19',
        'relationship_declared': 'TEAMMATE of the group',
        'eligibility_basis': 'Reviewer self-declaration; not independently verified. Team membership alone does not disqualify under the frozen no-involvement/no-exposure criterion.',
        'submission_zip_sha256': sha(raw),
        'original_members_sha256': {n: sha(b) for n, b in returned.items()},
        'declaration_decoding_for_validation': encoding,
        'original_bytes_preserved': True,
        'source_packet_sha256': sha(packet_raw),
        'source_packet_manifest_verified': True,
        'binding_basis': 'C01-C04 identifiers in returned CSV joined to the original issued packet; reviewer did not submit transcript hashes or a cryptographic signature.',
        'reviewed_content_sha256': reviewed_hashes,
        'rows': rows,
        'human_ratings_yes_both': 4,
        'case_count': 4,
        'scope': 'G1 Stage 2 development clarification review only; separate from M4 and future held-out review',
        'G_f': 'PASS on submitted ratings and reviewer attestation',
        'earlier_scorer_results_changed': False,
        'amendments_approved': False,
        'held_out_launch_permitted': False,
        'model_requests': 0,
    }
    (HERE / 'INTAKE_RECEIPT.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    master = STAGE.parents[3] / 'PROJECT_MASTER_README.md'
    # Preserve the current living record before this material documentation update.
    (HERE / 'PROJECT_MASTER_BEFORE_INTAKE.md').write_bytes(master.read_bytes())
    print(json.dumps({'reviewer': 'Levinson', 'cases': len(rows), 'yes_both': 4, 'packet_integrity': 'PASS', 'G_f': receipt['G_f'], 'source_bytes_preserved': True}))

if __name__ == '__main__':
    main()
