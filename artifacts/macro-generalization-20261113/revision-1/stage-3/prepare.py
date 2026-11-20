"""Snapshot protection and carry forward documented owner decisions, not reviews."""
import shutil
from common import ROOT, REV, WORKSPACE, read, write, digest, check_protected

def main():
    assert not (ROOT/'protected-before.json').exists(), 'Do not replace the before snapshot'
    protected = read(REV/'stage-2-continuation-1/protected-before.json')
    assert all(digest(WORKSPACE/name) == value for name, value in protected.items())
    for path in REV.rglob('*'):
        if path.is_file() and ROOT not in path.parents:
            protected[path.relative_to(WORKSPACE).as_posix()] = digest(path)
    write('protected-before.json', protected)
    result = check_protected()
    assert result['pass']
    write('protected-check-before.json', result)
    for name in ('STAGE2_AUDIT_ADDENDUM.md', 'STAGE2_AUDIT_ADDENDUM.json', 'stage2_audit_addendum.py'):
        shutil.copyfile(REV/'stage-3-preparation'/name, ROOT/name)
    write('owner-inputs.json', {
        'owner': 'Martin', 'scorer_reviewer_requested': 'Martin',
        'scorer_review_completed': False, 'clarification_reviewer_requested': 'Martin',
        'clarification_reviewer_uninvolved': False,
        'clarification_reviewer_exposure_note': 'Owner has seen prior aggregate results; not established as uninvolved.',
        'authorship_option': 'B',
        'authorship_basis': 'Carry forward explicit owner-selected AI-authored fallback for the same G1 revision; owner asked to fill inputs from existing records.',
        'authorship_evidence': '../amendments/ai-authored-20261113/AUTHORSHIP_AMENDMENT.md',
        'teammate_requests_file': 'NOT PROVIDED', 'near_duplicate_catalogue_for_4b': False,
        'censored_backend_flag_threshold': 8, 'scheduled_trials_per_backend': 76,
        'pair_gap_flag_minutes': 30, 'stage3_inference_allowance': 0,
        'stage4_authorized': False,
        'not_a_review_attestation': True})
    print(result)

if __name__ == '__main__':
    main()
