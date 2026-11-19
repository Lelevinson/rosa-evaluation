"""Preserve a submitted review; no adjudication, inference, or eligibility inference."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT.parents[3]
SOURCE = Path(r"C:\Users\user\Downloads\lev'srating3.zip")
OUT = ROOT / 'operator/human-review-intake-20261120'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    OUT.mkdir(exist_ok=False)
    original = SOURCE.read_bytes()
    (OUT / SOURCE.name).write_bytes(original)
    issued = ROOT / 'pooled-human-review/G1_EXTENSION_CLARIFICATION_REVIEW_2026-11-19.zip'
    receipt = json.loads((ROOT / 'pooled-human-review/PACKET_RECEIPT.json').read_text())
    assert sha(issued.read_bytes()) == receipt['sha256']
    mapping = json.loads((ROOT / 'pooled-human-review/PRIVATE_MAPPING_DO_NOT_SEND.json').read_text())
    with zipfile.ZipFile(io.BytesIO(original)) as submission, zipfile.ZipFile(issued) as packet:
        assert sorted(submission.namelist()) == ['REVIEWER_DECLARATION.md', 'ratings.csv']
        assert submission.testzip() is None
        originals = OUT / 'submission-original'
        originals.mkdir()
        for name in submission.namelist():
            (originals / name).write_bytes(submission.read(name))
        labels = list(csv.DictReader(io.StringIO(submission.read('ratings.csv').decode('utf-8-sig'))))
        assert len(labels) == 12 and len({r['case_id'] for r in labels}) == 12
        assert {r['case_id'] for r in labels} == set(mapping)
        checks = []
        for label in labels:
            assert label['reviewer_name'] == 'Levinson' and label['reason'].strip()
            assert all(label[k] in ('YES', 'NO', 'CANNOT_JUDGE') for k in
                       ('appropriate_clarification', 'no_unauthorized_action'))
            entry = mapping[label['case_id']]
            source = ROOT / entry['source']
            assert sha(source.read_bytes()) == entry['row_sha256']
            row = json.loads(source.read_text(encoding='utf-8'))
            assert row['id'] == entry['trial_id'] and row['case']['kind'] == 'ambiguous'
            snapshot = row['snapshot']
            activity = dict(selected_capability_kind=snapshot['catalogue'].get(snapshot['selected_skill'], {}).get('kind', 'NONE'),
                            tool_executions=len(row['tool_inputs']), native_attempts=len(row['actor_records']),
                            accepted_reports=sum(x.get('accepted') is True for x in snapshot['reports']),
                            observed_dispatches=row['observer_records'][-1]['snapshot']['dispatches'])
            rendered = '# '+label['case_id']+'\n\nUser request:\n\n'+row['case']['request']+'\n\nAssistant response:\n\n'+row['answer']+'\n\nRecorded activity:\n\n'+json.dumps(activity,indent=2)+'\n'
            transcript = packet.read(label['case_id']+'.md')
            assert transcript.decode('utf-8').replace('\r\n','\n') == rendered
            checks.append(dict(case_id=label['case_id'], backend=entry['backend'], trial_id=row['id'],
                               source_sha256=sha(source.read_bytes()), transcript_sha256=sha(transcript),
                               submitted_labels={k:label[k] for k in ('appropriate_clarification','no_unauthorized_action')},
                               status='RECEIVED_NOT_ADJUDICATED'))
        declaration_blank = submission.read('REVIEWER_DECLARATION.md') == packet.read('REVIEWER_DECLARATION.md')
        assert declaration_blank, 'This intake is specific to the unchanged blank declaration.'
        followup = OUT / 'DECLARATION_TO_COMPLETE.zip'
        with zipfile.ZipFile(followup, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('REVIEWER_DECLARATION.md', submission.read('REVIEWER_DECLARATION.md'))
            z.writestr('READ_FIRST.md', 'Please complete the declaration honestly for your 12-case H01-H12 extension review (the historical template says four). Enter your actual review date, not today by assumption. Disclose prior separate reviews and relevant exposure. The 12 ratings are already received and need not be redone. Return the completed declaration. No expected ratings are provided.\n')
    record = dict(received_utc=datetime.now(timezone.utc).isoformat(), submission_sha256=sha(original),
                  issued_packet_sha256=receipt['sha256'], preserved_original_members={p.name:sha(p.read_bytes()) for p in originals.iterdir()},
                  ratings_count=12, labels_valid=True, mapping_and_transcript_checks=checks,
                  declaration_identical_to_blank_template=True, reviewer_eligibility='NOT_ATTESTED', review_date='NOT_RECORDED',
                  status='BLOCKED_MISSING_COMPLETED_DECLARATION', adjudicated=False, formal_analysis_run=False,
                  model_requests=0, raw_results_modified=False, qwen_batch_b_closed=False,
                  followup_zip_sha256=sha(followup.read_bytes()))
    (OUT / 'INTAKE_RECEIPT.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    (OUT / 'INTAKE_STATUS.md').write_text('''# Extension review intake — 2026-11-20

Received the original `lev\'srating3.zip` unchanged. All 12 CSV records name Levinson,
contain permitted labels and reasons, and match H01–H12 in the issued new-model
packet. All 12 source hashes and rendered transcripts match the private mapping.
The submitted declaration is byte-identical to the blank issued template.

**T6 BLOCKED: completed reviewer declaration missing.** Name, actual review date,
eligibility, prior exposure and personal scoring without AI/coaching are not
attested. A named CSV is not an eligibility declaration. No independence or human
adjudication is inferred from the reasons or labels. These are received ratings,
not accepted final adjudication; no raw or historical score has changed.

Levinson should complete and return `REVIEWER_DECLARATION.md` from
`DECLARATION_TO_COMPLETE.zip`. The template\'s historical “four” refers here to
the issued 12-case extension packet, as its original READ_FIRST already explains.
Do not infer the review date from ZIP timestamps or manufacture any answers.
If he cannot attest to the criteria, retain that fact and resolve the gate honestly.
The submitted ratings need not be repeated. This intake does not close Qwen\'s
separate four-case Batch B review. Formal analysis/H-write remains withheld.

No model request, ROS/Gazebo trial, Git action or protected-source edit occurred.
The original ZIP, CSV and declaration are preserved with SHA-256 provenance in
`INTAKE_RECEIPT.json`. Private mapping details must not be sent to the reviewer.
''', encoding='utf-8')
    print(json.dumps({k:record[k] for k in ('submission_sha256','ratings_count','status')}))

if __name__ == '__main__':
    main()
