"""Inventory a BLOCKED preparation checkpoint; expressly not the G-g freeze."""
import ast
import csv
import hashlib
import json
import re
from common import ROOT, REV, read, write, digest, check_protected

def main():
    assert not (ROOT/'freeze.json').exists()
    assert not (ROOT/'PREPARATION_MANIFEST.json').exists(), 'Preserve the preparation inventory'
    syntax = []
    for path in sorted(ROOT.rglob('*.py')):
        ast.parse(path.read_text(encoding='utf-8'))
        syntax.append(path.relative_to(ROOT).as_posix())
    record = read(ROOT/'scorer-review/scorer-record.json')
    assert digest(REV/'stage-2/scoring.py') == record['sha256']
    assert record['reviewer_cases_received'] == 0 and not record['review_complete']
    packet = ROOT/'clarification-review/packet'
    transcripts = sorted(packet.glob('C*.md'))
    assert len(transcripts) == 4
    forbidden = re.compile(r'gpt-6|\bSol\b|\bQwen\b|\bprimitives\b|\bmacro\b|primary_pass|selection_correct|G1r1-dev', re.I)
    for path in transcripts:
        assert not forbidden.search(path.read_text(encoding='utf-8'))
    with (packet/'ratings-empty.csv').open(encoding='utf-8', newline='') as stream:
        ratings = list(csv.DictReader(stream))
    assert len(ratings) == 4
    assert all(not value for row in ratings for key, value in row.items() if key != 'case_id')
    assert len(read(ROOT/'clarification-review/private-key/packet-map.json')) == 4
    assert read(ROOT/'intake/requests-empty.json') == {'requests': []}
    # An empty intake exercise produces no new case or reviewer claim.
    from intake_requests import build
    empty = build([], [])
    assert empty['status'] == 'BLOCKED' and empty['cases'] is None and empty['teammate_cases'] == 0
    gates = read(ROOT/'stage3-gates.json')
    assert gates['G-a']['status'] == 'PASS'
    assert all(gates[key]['status'] == 'BLOCKED' for key in ('G-b','G-c','G-d','G-e','G-f','G-g','G-h'))
    probe = read(ROOT/'instrumentation/observability-boundary-tests.json')
    assert probe['six_boundary_fixtures_passed'] and not probe['instrumentation_complete']
    assert 'CANARY_STAGE3_SECRET_DO_NOT_RETAIN_' not in json.dumps(probe)
    assert probe['network_requests'] == probe['model_requests'] == 0
    analysis = read(ROOT/'analysis/dev-analysis.json')
    assert analysis['classes'] == {'EVALUABLE': 35, 'INFRA_CENSORED_PRE_OUTPUT': 1}
    assert read(ROOT/'analysis/unit-tests.json')['passed']
    preflight = read(ROOT/'LAUNCH_PREFLIGHT_RECORD.json')
    assert preflight['status'] == 'BLOCKED_NOT_LAUNCH_READY' and preflight['quota'].startswith('UNKNOWN')
    assert preflight['estimated_requests'] == 200 and preflight['total_physical_request_cap'] == 611
    assert not preflight['freeze_created'] and not preflight['stage4_authorized']
    for relative, value in preflight['candidate_prior_input_hashes'].items():
        assert digest(REV/relative) == value
    for relative, value in preflight['candidate_stage3_input_hashes'].items():
        assert digest(ROOT/relative) == value
    protected = check_protected()
    assert protected['pass']
    write('protected-check-final.json', protected)
    result = dict(preparation_checkpoint_valid=True, full_stage3_complete=False, freeze_created=False,
        syntax_checked_files=syntax, blinded_stage2_transcripts=4, human_ratings_generated=0,
        scorer_review_cases_received=0, model_requests=0, network_requests=0,
        protected_check=protected, gates={key: value['status'] for key, value in gates.items()},
        note='Zero network refers to Stage 3 tests/preparation, not historical evidence or future planned OAuth preflight.')
    write('preparation-validation.json', result)
    files = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(ROOT.rglob('*')) if path.is_file()
             and path.name not in ('PREPARATION_MANIFEST.json', 'PREPARATION_VERIFICATION.json')}
    write('PREPARATION_MANIFEST.json', dict(kind='BLOCKED PREPARATION INVENTORY; NOT A STUDY FREEZE',
        date='2026-11-14', files=files, pre_run_note_sha256=digest(ROOT/'PRE_RUN_NOTE.md'),
        freeze_gate_passed=False, model_requests=0, protected_check=protected))
    mismatches = [name for name, expected in files.items() if digest(ROOT/name) != expected]
    assert not mismatches
    receipt = dict(pass_=True, verified_files=len(files), mismatches=mismatches,
        manifest_sha256=digest(ROOT/'PREPARATION_MANIFEST.json'), kind='Preparation inventory, NOT freeze approval',
        full_stage3_complete=False, model_requests=0, protected_check=protected)
    receipt['pass'] = receipt.pop('pass_')
    write('PREPARATION_VERIFICATION.json', receipt)
    print(receipt)

if __name__ == '__main__':
    main()
