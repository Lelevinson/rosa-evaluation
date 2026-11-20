"""Versioned analysis using new rules; never overwrite the earlier checkpoint."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
STAGE3 = HERE.parent
sys.path.insert(0, str(STAGE3))
from common import ROOT, REV, read, digest, check_protected
from censoring import annotate, pair_gap
from analysis import costs, pairs_of, both_success, percentile
sys.path.insert(0, str(HERE))
from prediction_rules import point_metrics, combine_domains, sensitivity, p4_views, p5_status, p6_descriptive

def verify_checkpoint():
    manifest = read(STAGE3/'PREPARATION_MANIFEST.json')
    receipt = read(STAGE3/'PREPARATION_VERIFICATION.json')
    assert digest(STAGE3/'PREPARATION_MANIFEST.json') == receipt['manifest_sha256']
    assert all(digest(STAGE3/name) == value for name, value in manifest['files'].items())
    protected = check_protected()
    assert protected['pass']
    return dict(original_stage3_files_verified=len(manifest['files']), prior_protected_check=protected)

def bootstrap(rows, censored, output):
    groups = defaultdict(list)
    for row in rows:
        groups[row['case']['template_group']].append(row)
    names = sorted(groups)
    rng = random.Random(20261113)
    samples, empty = defaultdict(list), Counter()
    points = {}
    for view in ('V2', 'V3'):
        metrics, _ = point_metrics(rows, censored, view)
        points.update({view+'/'+key: value for key, value in metrics.items() if not key.endswith('_status')})
    with gzip.open(output/'bootstrap-draws.jsonl.gz', 'wt', encoding='utf-8') as stream:
        for index in range(10000):
            indices = [rng.randrange(len(names)) for _ in names]
            drawn = [row for group in indices for row in groups[names[group]]]
            numeric = {}
            for view in ('V2', 'V3'):
                metrics, _ = point_metrics(drawn, censored, view)
                numeric.update({view+'/'+key: value for key, value in metrics.items() if not key.endswith('_status')})
            stream.write(json.dumps(dict(draw=index, group_indices=indices, metrics=numeric))+'\n')
            for key, value in numeric.items():
                if value is None:
                    empty[key] += 1
                else:
                    samples[key].append(value)
    intervals = {}
    for key, point in points.items():
        values = sorted(samples[key])
        intervals[key] = dict(point=point, lower=percentile(values, .025) if values else None,
            upper=percentile(values, .975) if values else None, empty_draws=empty[key],
            nonempty_draws=len(values), degenerate_nonempty=bool(values) and values[0] == values[-1],
            distinct_values=len(set(values)))
    return dict(draws=10000, seed=20261113, groups=names, unit='whole template group',
                intervals=intervals, threshold_role='descriptive uncertainty; new point-threshold rules remain separate')

def analyze(rows, schedule, locations, output, *, scope='dev', probe_rows=None, qwen_backend_compromised=None, hosting_source_changes=(), fresh_controls_passed=False):
    assert len(rows) == len({r['id'] for r in rows})
    scheduled_ids = {item['id'] for item in schedule}
    assert {row['id'] for row in rows} <= scheduled_ids
    annotations = {row['id']: annotate(row) for row in rows}
    censored = {key for key, value in annotations.items() if value['censor_class'] != 'EVALUABLE'}
    matched = both_success(rows, censored)
    complete = len(rows) == len(schedule)
    compromised = len(censored) >= 8
    cost_views = {}
    for name, group in [('V1_all_attempts', rows), ('V2_evaluable', [r for r in rows if r['id'] not in censored]),
                        ('matched_success', [r for r in rows if r['case']['case_id'] in matched])]:
        cost_views[name] = {mode: costs([r for r in group if r['mode'] == mode]) for mode in ('primitives', 'macro')}
    operational = {}
    for mode in ('primitives', 'macro'):
        group = [r for r in rows if r['mode'] == mode]
        evaluable = [r for r in group if r['id'] not in censored]
        correct = sum(r['primary_pass'] for r in evaluable)
        planned = sum(item['mode'] == mode for item in schedule)
        operational[mode] = dict(scheduled=planned, retained=len(group), unstarted=planned-len(group),
            correct_completed=correct, incorrect_evaluable=len(evaluable)-correct,
            censored=len(group)-len(evaluable), V2_correct=correct, V2_denominator=len(evaluable),
            V3_correct=correct, V3_denominator=planned)
    by_view = {}
    for view in ('V2', 'V3'):
        metrics, cells = point_metrics(rows, censored, view)
        domains = {prediction: {domain: metrics[domain+'/'+prediction+'_status'] for domain in ('arm','base')}
                   for prediction in ('P1_prime','P2')}
        by_view[view] = dict(metrics=metrics, cells=cells, domain_statuses=domains,
                             primary_domain_combined={key: combine_domains(value) for key, value in domains.items()})
    final = {key: sensitivity(by_view['V2']['primary_domain_combined'][key], by_view['V3']['primary_domain_combined'][key], compromised, complete)
             for key in ('P1_prime','P2')}
    final['P3'] = 'DROPPED'
    p4 = p4_views(probe_rows or [], compromised=bool(qwen_backend_compromised))
    if probe_rows and qwen_backend_compromised is None:
        p4['final'] = 'Uninformative'
        p4['backend_compromise_status'] = 'NOT_RECORDED; do not borrow Sol status'
    final['P4'] = p4['final']
    final['P5'] = p5_status(hosting_source_changes, fresh_controls_passed)
    if compromised or not complete:
        for key in ('P1_prime','P2','P5'):
            final[key] = 'Uninformative'
    final['P6'] = 'DESCRIPTIVE_ONLY'
    exclusions, gaps, tables = [], [], []
    for case_id, pair in pairs_of(rows).items():
        first = next(iter(pair.values()))
        if len(pair) < 2 or any(row['id'] in censored for row in pair.values()):
            exclusions.append(dict(case_id=case_id, domain=first['case']['domain'], depth=first['case']['native_depth'],
                reason='censored arm' if len(pair) == 2 else 'unstarted arm'))
        if len(pair) == 2:
            traces = [read(locations[pair[mode]['id']]/'trace.json')['spans'] for mode in ('primitives','macro')]
            gaps.append(dict(case_id=case_id, **pair_gap(*traces)))
    for domain in ('arm','base'):
        for depth in (None,1,2,4,6):
            group = [r for r in rows if r['case']['domain'] == domain and
                (depth is None or r['case']['kind'] == 'ladder' and r['case']['native_depth'] == depth)]
            discordant = Counter()
            for pair in pairs_of(group).values():
                if len(pair) < 2:
                    discordant['unstarted_arm'] += 1
                elif any(r['id'] in censored for r in pair.values()):
                    discordant['censored_pair'] += 1
                else:
                    p, m = (pair[mode]['primary_pass'] for mode in ('primitives','macro'))
                    discordant['both_correct' if p and m else 'primitive_only' if p else 'macro_only' if m else 'neither'] += 1
            tables.append(dict(domain=domain, depth=depth, discordant_pairs=dict(discordant),
                all_attempts={mode: costs([r for r in group if r['mode'] == mode]) for mode in ('primitives','macro')},
                matched_success_pairs=len(both_success(group,censored)),
                excluded_censored_pairs=sum(e['domain'] == domain and (depth is None or e['depth'] == depth) for e in exclusions)))
    result = dict(scope=scope, definitions_source='PREDICTIONS_AMENDMENT_2026-11-14.md',
        study_label='AI-authored cases; no independent teammate authorship or semantic-novelty review',
        official_verdicts='NOT_ADJUDICATED_DEV_ONLY' if scope == 'dev' else final,
        diagnostic_statuses=final, prediction_views=by_view, P4_probe=p4,
        P5_evidence=dict(required_hosting_source_changes=list(hosting_source_changes), fresh_controls_passed=fresh_controls_passed,
                         instrumentation_hook='Proposed, unapplied; not a required domain-hosting change'),
        P6={view: p6_descriptive(rows,censored,view) for view in ('V2','V3')},
        scheduled_trials=len(schedule), retained_trials=len(rows), complete=complete,
        censor_classes=dict(Counter(value['censor_class'] for value in annotations.values())),
        operational_views=operational, analysis_rows=list(annotations.values()), costs=cost_views,
        per_domain_depth=tables, excluded_pairs=exclusions, pair_gaps=gaps,
        batching_and_tool_sequences=[dict(trial_id=r['id'], censor_class=annotations[r['id']]['censor_class'],
            physical_calls=r['inference']['calls'], tool_calls_with_arguments=r.get('tool_inputs', []),
            native_operations=[op['kind'] for op in r['actor_records']]) for r in rows],
        matched_success_pairs=len(matched), operationally_compromised=compromised,
        bootstrap=bootstrap(rows,censored,output), model_requests=0, freeze_created=False)
    return result

def main():
    verification = verify_checkpoint()
    output = HERE/'analysis-output'
    output.mkdir(exist_ok=False)
    rows, locations = [], {}
    for segment in ('stage-2','stage-2-continuation-1'):
        for path in sorted((REV/segment/'trials').glob('*/result.json')):
            row = read(path)
            rows.append(row)
            locations[row['id']] = path.parent
    result = analyze(rows, read(REV/'stage-2/plan.json'), locations, output)
    assert [result['costs']['V1_all_attempts'][mode]['calls'] for mode in ('primitives','macro')] == [60,34]
    assert [result['costs']['matched_success'][mode]['calls'] for mode in ('primitives','macro')] == [59,32]
    assert result['censor_classes'] == {'EVALUABLE':35,'INFRA_CENSORED_PRE_OUTPUT':1}
    (output/'dev-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (output/'validation.json').write_text(json.dumps(dict(passed=True, original_checkpoint_unchanged=verify_checkpoint(),
        bootstrap_draws=10000, previous_total_reproduction=True, model_requests=0,
        stage2_predictions_adjudicated=False, freeze_created=False),indent=2)+'\n',encoding='utf-8')
    print(dict(censor_classes=result['censor_classes'], diagnostic_only=result['diagnostic_statuses'],
        original_checkpoint_files_verified=verification['original_stage3_files_verified'], model_requests=0))

if __name__ == '__main__':
    main()
