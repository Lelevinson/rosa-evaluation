"""Intake real H01-H04 ratings; preserve bytes and bind unchanged trial evidence."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common import read, verify
from adjudication import VERSION, ELIGIBILITY, canonical_digest, content_binding, validate_bundle, summarize


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    source = Path(sys.argv[1])
    output = HERE / 'human-review-intake-20261119'
    bound = ROOT / 'human-review-bound.json'
    assert not output.exists() and not bound.exists(), 'Preserve earlier intake'
    protection = verify()
    raw = source.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'ratings-empty.csv', 'REVIEWER_DECLARATION.md'}
        returned = {name: z.read(name) for name in z.namelist()}
    csv_raw = returned['ratings-empty.csv']
    ratings = list(csv.DictReader(io.StringIO(csv_raw.decode('utf-8-sig'), newline='')))
    ids = {'H01', 'H02', 'H03', 'H04'}
    assert len(ratings) == 4 and {r['case_id'] for r in ratings} == ids
    assert all(r['reviewer_name'] == 'Levinson' and r['reason'].strip() for r in ratings)
    assert all(r[k] in {'YES', 'NO', 'CANNOT_JUDGE'} for r in ratings
               for k in ('appropriate_clarification', 'no_unauthorized_action'))
    declaration_raw = returned['REVIEWER_DECLARATION.md']
    try:
        declaration = declaration_raw.decode('utf-8-sig')
        encoding = 'utf-8-sig'
    except UnicodeDecodeError:
        declaration = declaration_raw.decode('cp1252')
        encoding = 'cp1252'
    assert 'Reviewer name: Levinson' in declaration and '2026/11/19' in declaration
    assert declaration.count(': YES') == 5 and 'Teammate' in declaration
    issued = HERE / 'heldout-human-review'
    packet = (issued / 'G1_NEW_HELDOUT_HUMAN_REVIEW_2026-11-19.zip').read_bytes()
    assert sha(packet) == read(issued / 'PACKET_RECEIPT.json')['sha256']
    mapping = read(issued / 'PRIVATE_MAPPING_DO_NOT_SEND.json')
    assert set(mapping) == ids
    rows = [read(p) for p in sorted((ROOT / 'trials').glob('*/result.json'))]
    by_id = {r['id']: r for r in rows}
    records = []
    with zipfile.ZipFile(io.BytesIO(packet)) as z:
        assert z.testzip() is None
        rubric = sha(z.read('RUBRIC.md'))
        for rating in ratings:
            case = rating['case_id']
            key = mapping[case]
            row = by_id[key['trial_id']]
            assert canonical_digest(row) == key['row_sha256']
            assert row['model'] == key['model'] and row['mode'] == key['mode']
            assert row['case']['kind'] == 'ambiguous'
            selected = row['snapshot']['selected_skill']
            definition = row['snapshot']['catalogue'].get(selected, {})
            activity = {'selected_capability_kind': definition.get('kind', 'NONE'),
                'recorded_tool_executions': len(row.get('tool_inputs', [])),
                'native_attempts': len(row['actor_records']),
                'accepted_reports': sum(r.get('accepted') is True for r in row['snapshot']['reports']),
                'observed_dispatches': row['observer_records'][-1]['snapshot']['dispatches']}
            expected = (f'# {case}\n\nUser request:\n\n{row["case"]["request"]}\n\n'
                f'Assistant response:\n\n{row["answer"]}\n\nRecorded activity:\n\n'
                + json.dumps(activity, indent=2) + '\n').encode('utf-8')
            transcript = z.read(case + '.md')
            # Windows Path.write_text translated LF to CRLF in the issued packet.
            # Compare rendered content; retain/bind the exact issued bytes below.
            assert transcript.replace(b'\r\n', b'\n') == expected.replace(b'\r\n', b'\n')
            records.append(dict(trial_id=row['id'], packet_case_id=case,
                reviewer=rating['reviewer_name'], review_date='2026-11-19',
                appropriate_clarification=rating['appropriate_clarification'],
                no_unauthorized_action=rating['no_unauthorized_action'], reason=rating['reason'],
                eligibility={k: True for k in ELIGIBILITY},
                eligibility_basis='Returned declaration: self-attestation, not independently verified',
                declared_relationship='Teammate; previously reviewed the separate four development cases',
                binding=content_binding(row, rubric),
                provenance=dict(submission_sha256=sha(raw), csv_sha256=sha(csv_raw),
                    declaration_sha256=sha(declaration_raw), transcript_sha256=sha(transcript))))
    bundle = dict(version=VERSION, rubric_sha256=rubric, records=records,
        scope='Actual H01-H04 held-out Sol review only; no transfer to future runs',
        original_packet_sha256=sha(packet),
        identity_basis='Owner-supplied ZIP and returned declaration; no cryptographic human identity proof')
    validate_bundle(bundle, rubric)
    summary = summarize(rows, [x['id'] for x in read(ROOT / 'plan.json')], bundle, rubric)
    assert summary['final_correctness_ready'] and not summary['semantic_judgments_pending']
    output.mkdir()
    (output / 'submission-original').mkdir()
    (output / source.name).write_bytes(raw)
    for name, data in returned.items():
        (output / 'submission-original' / name).write_bytes(data)
    receipt = dict(date='2026-11-19', reviewer='Levinson', cases=4,
        original_submission_sha256=sha(raw), source_packet_sha256=sha(packet),
        original_members_sha256={n: sha(b) for n, b in returned.items()},
        declaration_decoding=encoding, review_date_verbatim='2026/11/19',
        review_date_normalized='2026-11-19', source_rendering_matches=True,
        original_bytes_preserved=True, frozen_inputs=protection,
        relationship_and_limit='Teammate; prior separate development review is known. Current no-involvement/no-prior-exposure eligibility is self-declared, not independently verified. This is not external blind validation or inter-rater agreement.',
        submitted_ratings=ratings, effective_counts=summary['counts'],
        model_requests=0, trials_repeated=0)
    (output / 'INTAKE_RECEIPT.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (output / 'ADJUDICATED_SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    bound.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'actual_human_ratings_bound': 4, 'counts': summary['counts'],
        'final_correctness_ready': summary['final_correctness_ready'], 'model_requests': 0}))


if __name__ == '__main__':
    main()
