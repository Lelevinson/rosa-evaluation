"""Record the new checkpoint without altering the sealed 62-file preparation."""
import ast
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from run_analysis import verify_checkpoint
sys.path.insert(0,str(HERE.parent))
from common import read, digest

def write(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (HERE/'AMENDMENT_MANIFEST.json').exists()
    verification = verify_checkpoint()
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    data=read(HERE/'analysis-output/dev-analysis.json')
    tests=read(HERE/'prediction-tests.json')
    assert tests['passed'] and tests['methods']==20
    counts={key:0 for key in data['bootstrap']['intervals']}
    with gzip.open(HERE/'analysis-output/bootstrap-draws.jsonl.gz','rt',encoding='utf-8') as stream:
        n=0
        for n,line in enumerate(stream,1):
            draw=json.loads(line)
            assert draw['draw']==n-1
            for key,value in draw['metrics'].items():
                counts[key]+=value is None
        assert n==10000
    assert all(counts[key]==value['empty_draws'] for key,value in data['bootstrap']['intervals'].items())
    assert data['official_verdicts']=='NOT_ADJUDICATED_DEV_ONLY'
    cells=data['prediction_views']['V2']['cells']
    lines=['# Prediction-definition update and dev validation','', 'Date: **2026-11-14**.','',
        'The owner supplied P1-prime through P6 and confirmed the domain and P4-boundary interpretations. '
        'The missing-definition blocker is resolved. This is a prospective analysis amendment for future held-out data, '
        'validated retrospectively on Stage 2. No model requests were made and no new performance claim is adjudicated.','',
        'The old Stage 3 checkpoint remains unchanged: all **62 inventory files** verified. '
        '**20 prediction/analysis tests passed**. All **10000 whole-template bootstrap draws**, seed 20261113, '
        'are retained; empty draw counts were checked directly against the draw file.','',
        '## Primary V2 diagnostic depth table','',
        '| Domain | Depth | Matched-success pairs | Calls saved per pair | Native ratio | Censored pair exclusions |',
        '|---|---:|---:|---:|---:|---:|']
    for cell in cells:
        if cell['domain']=='pooled':
            continue
        value=lambda v:'not evaluable' if v is None else f'{v:.2f}'
        lines.append(f'| {cell["domain"]} | {cell["depth"]} | {cell["matched_success_pairs"]} | '
            f'{value(cell["absolute_calls_saved"])} | {value(cell["native_ratio"])} | {cell["excluded_censored_pairs"]} |')
    lines += ['', 'All fully measured dev cells show one call saved per successful inspection pair and a native ratio of 1.00. '
        'The interrupted Base depth-6 primitive attempt leaves that required domain/depth cell unevaluable. '
        'Pooled values cannot fill that gap under the confirmed per-domain rules. This is a missing-data check, '
        'not a held-out Support/Against finding.','',
        'P6 remains descriptive. In evaluable Stage 2 rows, primitive ladder inspections averaged 3 calls; '
        'healthy writes and partial writes each averaged 5; missing-prerequisite cases averaged 3. '
        'The corresponding macro means were 2. No dedicated unavailable-source dev mean exists. '
        'Kinds and denominators remain separate in the JSON output.','',
        '## Current gate implications','',
        '- G-d missing definitions: resolved; new-rule dev arithmetic and boundary checks PASS. Gate advancement still waits on earlier ordered gates.',
        '- G-b: fresh final-fixture controls and exact persisted audits have not rerun.',
        '- G-c: proposed HTTP observability hook remains unapplied and unapproved; integrated instrumentation validation is incomplete.',
        '- G-e/G-f: no new independent scorer review or uninvolved clarification ratings were supplied.',
        '- G-g/G-h: no final freeze or live restore-only preflight. Stage 4 remains unauthorized.','',
        'See [the adopted rules](PREDICTIONS_AMENDMENT_2026-11-14.md), '
        '[owner confirmation](OWNER_CONFIRMATION.json), [dev analysis](analysis-output/dev-analysis.json) '
        'and [test results](prediction-tests.json). '
        'The earlier missing-definition statements remain correct historical checkpoint records and are superseded '
        'by this amendment; their files were not edited.']
    (HERE/'UPDATE_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    status=dict(date='2026-11-14', definitions_received=True, interpretations_owner_confirmed=True,
        analysis_rule_component_tests='PASS_20', dev_reproduction='PASS', full_bootstrap_draws_retained=10000,
        Gd_definition_blocker='RESOLVED', Gd_ordered_gate='BLOCKED_UPSTREAM_GB_GC',
        remaining_blockers=['fresh controls','instrumentation approval and integration tests',
            'actual independent scorer review','uninvolved clarification review','final freeze','restore-only preflight'],
        protected_checkpoint=verification, model_requests=0, freeze_created=False, stage4_authorized=False)
    write(HERE/'UPDATE_STATUS.json',status)
    current=HERE.parent/'CURRENT_STATUS.md'
    assert not current.exists(), 'Preserve an existing current-status file'
    current.write_text('''# G1 Stage 3 current status

Updated: **2026-11-14**. **Prediction definitions received and analysis component updated; freeze remains blocked.**

The owner supplied P1-prime through P6 and confirmed: require P1-prime/P2 separately in both domains; P4 is
Against at an accuracy fall of exactly 20 percentage points; keep catalogue sizes 3/5/10. P3 is dropped to G2.
P6 is descriptive only. These replace the earlier endpoint definitions prospectively, with the old files preserved.

Read [the update report](predictions-amendment-20261114/UPDATE_REPORT.md) and
[the adopted amendment](predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md).
Twenty new threshold/analysis tests passed, Stage 2 totals were reproduced, and all 10000 bootstrap draws retained.
Stage 2 remains dev-only; no held-out verdict was produced.

The earlier [STAGE3_STATUS.md](STAGE3_STATUS.md) is a preserved checkpoint. Its missing-definition blocker is now
resolved. Other blockers remain: fresh controls, instrumentation disposition and validation, actual scorer review,
uninvolved clarification review, final freeze and restore-only preflight. The requested names alone are not reviews.

No protected source or earlier evidence changed. No live model requests, source-hook approval, Git action or
Stage 4 launch occurred. The earlier draft preflight is not launch readiness and needs the new analysis hashes
in the eventual freeze. The new amendment inventory is also not a freeze.
''',encoding='utf-8')
    files={path.relative_to(HERE).as_posix():digest(path) for path in sorted(HERE.rglob('*')) if path.is_file()
        and path.name not in ('AMENDMENT_MANIFEST.json','AMENDMENT_VERIFICATION.json')}
    write(HERE/'AMENDMENT_MANIFEST.json',dict(kind='Prediction amendment inventory, NOT a study freeze',date='2026-11-14',
        files=files,current_status_sha256=digest(current),previous_preparation_sha256=digest(HERE.parent/'PREPARATION_MANIFEST.json')))
    assert all(digest(HERE/name)==value for name,value in files.items())
    final=verify_checkpoint()
    write(HERE/'AMENDMENT_VERIFICATION.json',dict(passed=True,verified_files=len(files),mismatches=[],
        manifest_sha256=digest(HERE/'AMENDMENT_MANIFEST.json'),previous_checkpoint=final,
        current_status_sha256=digest(current),model_requests=0,freeze_created=False))
    print(dict(verified_files=len(files),old_checkpoint_unchanged=True,tests=20,bootstrap_draws=10000,
        missing_definitions_resolved=True,freeze_created=False,model_requests=0))

if __name__=='__main__':
    main()
