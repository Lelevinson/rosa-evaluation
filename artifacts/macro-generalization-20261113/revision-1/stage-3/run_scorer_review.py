"""Execute only actual reviewer-authored submissions against the unchanged scorer."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
import sys
from uuid import uuid4
from common import ROOT, REV, REPO, read, digest, dev_rows

def patch_value(document, change):
    parts = [part.replace('~1', '/').replace('~0', '~') for part in change['path'].split('/')[1:]]
    assert parts and parts[0] in ('case', 'snapshot', 'observer_records', 'answer')
    target = document
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    key = int(parts[-1]) if isinstance(target, list) else parts[-1]
    if change['op'] == 'remove':
        del target[key]
    elif change['op'] in ('add', 'replace'):
        target[key] = deepcopy(change['value'])
    else:
        raise ValueError('unsupported_patch_operation')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('submission')
    args = parser.parse_args()
    submission_path = __import__('pathlib').Path(args.submission)
    submission = read(submission_path)
    if not submission.get('reviewer_name') or not submission.get('new_cases_not_prior_counterfactual_replays') or not submission.get('cases'):
        raise SystemExit('BLOCKED: named reviewer and actual new reviewer-authored cases required; empty template is not a review')
    assert submission['reviewer_name'] != 'Codex'
    scorer_path = REV/'stage-2/scoring.py'
    expected_hash = read(ROOT/'scorer-review/scorer-record.json')['sha256']
    assert digest(scorer_path) == expected_hash
    sys.path[:0] = [str(REV), str(REPO)]
    spec = importlib.util.spec_from_file_location('g1_review_scorer', scorer_path)
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    baselines = {row['id']: row for row in dev_rows()}
    output = ROOT/'scorer-review/runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8])
    output.mkdir(parents=True)
    (output/'submission-exact.json').write_bytes(submission_path.read_bytes())
    outcomes = []
    for case in submission['cases']:
        assert case.get('case_id') and case.get('description') and case.get('changes') and case.get('expected')
        row = deepcopy(baselines[case['baseline_trial_id']])
        for change in case['changes']:
            patch_value(row, change)
        try:
            actual = scorer.score(row['case'], row['snapshot'], row['answer'], row['observer_records'])
        except Exception as error:
            actual = {'exception_type': type(error).__name__}
        matched = all(actual.get(key) == value for key, value in case['expected'].items())
        outcomes.append(dict(case_id=case['case_id'], expected=case['expected'], actual=actual,
                             expected_outcome_matched=matched, reviewer_changes=case['changes'], operator_edits=[]))
    assert digest(scorer_path) == expected_hash
    result = dict(reviewer=submission['reviewer_name'], submission_sha256=digest(submission_path),
        scorer_sha256_before=expected_hash, scorer_sha256_after=digest(scorer_path), outcomes=outcomes,
        unresolved_mismatches=sum(not row['expected_outcome_matched'] for row in outcomes), model_requests=0,
        gate_pass_not_inferred='Reviewer must report coverage and whether defects are substantive; harness success alone is not review completion.')
    (output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print({'retained_review_cases': len(outcomes), 'mismatches': result['unresolved_mismatches'], 'model_requests': 0})

if __name__ == '__main__':
    main()
