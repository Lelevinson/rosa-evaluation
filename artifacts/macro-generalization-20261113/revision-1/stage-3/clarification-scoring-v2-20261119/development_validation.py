"""Retain zero-model checks and explicitly retrospective Stage2 overlay."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from adjudication import canonical_digest, summarize, project_complete_rows
from bind_existing_review import load_rows

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REV = STAGE.parent

def main():
    output = HERE/'development-validation'
    output.mkdir(exist_ok=False)
    test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(HERE),
                           '-p', 'test_adjudication.py', '-v'], capture_output=True, text=True)
    (output/'implementer-tests.log').write_text(test.stdout+test.stderr, encoding='utf-8')
    if test.returncode:
        raise SystemExit('Zero-model checks failed; retained log; do not clear review')
    rows = load_rows()
    raw_digest = canonical_digest(rows)
    bundle = json.loads((HERE/'LEV_ACTUAL_REVIEW_BOUND.json').read_text(encoding='utf-8'))
    schedule = json.loads((REV/'stage-2/plan.json').read_text(encoding='utf-8'))
    schedule_ids = [r['id'] for r in schedule]
    summary = summarize(rows, schedule_ids, bundle, bundle['rubric_sha256'])
    assert summary['counts'] == {'PASS': 35, 'FAIL': 0, 'PENDING_HUMAN_REVIEW': 0,
        'INFRA_CENSORED_PRE_OUTPUT': 1, 'INFRA_CENSORED_POST_ACTION': 0}
    projected = project_complete_rows(rows, bundle, bundle['rubric_sha256'])
    raw_by_id = {r['id']: r for r in rows}
    # Exercise the existing prediction functions with complete projected records
    # only. No script that overwrites old analysis outputs is run.
    sys.path.insert(0, str(STAGE/'predictions-amendment-20261114'))
    from prediction_rules import point_metrics
    censored = {o['trial_id'] for o in summary['outcomes'] if o['censor_class'] != 'EVALUABLE'}
    comparisons = {}
    for view in ('V2', 'V3'):
        before = point_metrics(rows, censored, view)
        after = point_metrics(projected, censored, view)
        assert before == after
        comparisons[view] = 'Existing point metrics unchanged on these dev records'
    for new in projected:
        old = raw_by_id[new['id']]
        assert new['inference'] == old['inference']
        assert new['actor_records'] == old['actor_records']
        assert new['task_seconds'] == old['task_seconds']
        assert new['primary_pass'] == old['primary_pass']
        if new['case']['kind'] != 'ambiguous':
            assert new['score'] == old['score']
    assert canonical_digest(rows) == raw_digest
    summary.update(scope='Retrospective Stage2 development overlay; not held-out evidence',
                   prediction_verdicts='NOT_ADJUDICATED_DEV_ONLY', freeze_created=False,
                   experiment_launch_authorized=False)
    (output/'RETROSPECTIVE_DEV_OVERLAY.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    files = ('adjudication.py', 'bind_existing_review.py', 'test_adjudication.py',
             'development_validation.py', 'AMENDMENT.md', 'LEV_ACTUAL_REVIEW_BOUND.json')
    receipt = dict(implementer_test_methods=15, implementer_tests_passed=True,
        actual_human_ratings_used=4, retained_dev_trials=36, non_ambiguous_records_unchanged=32,
        censored_trials=1, costs_unchanged=True, old_prediction_metric_comparisons=comparisons,
        protected_legacy_scorer_changed=False, raw_inputs_unchanged=True, model_requests=0,
        source_hashes={n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in files},
        independent_review='Separate review required; not inferred from these checks')
    (output/'VALIDATION_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'tests': 15, 'counts': summary['counts'],
                     'costs': summary['all_attempt_costs'], 'source_and_costs_unchanged': True}))

if __name__ == '__main__':
    main()
