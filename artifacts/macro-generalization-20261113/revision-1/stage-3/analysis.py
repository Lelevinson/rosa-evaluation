"""Prospective analysis candidate. Not frozen while requested P1-prime/P6 are undefined."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
import math
from pathlib import Path
import random
from statistics import mean, median
from common import ROOT, REV, read, write
from censoring import annotate, pair_gap

MODES = ('primitives', 'macro')
READ_KINDS = ('ladder', 'unavailable_source')
DRAWS = 10000
SEED = 20261113

def costs(rows):
    times = [r['task_seconds'] for r in rows]
    return dict(trials=len(rows), correct=sum(r['primary_pass'] for r in rows),
        calls=sum(r['inference']['calls'] for r in rows),
        logical_decisions=sum(r['inference'].get('decision_calls', r['inference']['calls']) for r in rows),
        known_input_tokens=sum(r['inference']['known_input_tokens'] for r in rows),
        known_output_tokens=sum(r['inference']['known_output_tokens'] for r in rows),
        usage_incomplete=sum(not r['inference']['usage_complete'] for r in rows),
        task_seconds=sum(times), mean_seconds=mean(times) if times else None,
        median_seconds=median(times) if times else None,
        native_attempts=sum(len(r['actor_records']) for r in rows),
        invalid_attempts=sum(r['snapshot']['validation_errors'] for r in rows),
        budget_endings=sum(bool(r['score'].get('budget_exhaustion')) for r in rows),
        length_endings=sum(bool(r['score'].get('length_stop')) for r in rows))

def pairs_of(rows):
    pairs = defaultdict(dict)
    for row in rows:
        pairs[row['case']['case_id']][row['mode']] = row
    return pairs

def saving(rows):
    totals = {mode: sum(r['inference']['calls'] for r in rows if r['mode'] == mode) for mode in MODES}
    return 1-totals['macro']/totals['primitives'] if totals['primitives'] and totals['macro'] else None

def both_success(rows, censored):
    return {key for key, pair in pairs_of(rows).items() if len(pair) == 2 and
            all(r['primary_pass'] and r['id'] not in censored for r in pair.values())}

def metric_vector(rows, censored):
    metrics = {}
    for view in ('V2', 'V3'):
        eligible = [r for r in rows if view == 'V3' or r['id'] not in censored]
        for domain in ('arm', 'base'):
            group = [r for r in eligible if r['case']['domain'] == domain]
            fractions = []
            for mode in MODES:
                arm = [r for r in group if r['mode'] == mode]
                fractions.append(sum(r['primary_pass'] and r['id'] not in censored for r in arm)/len(arm) if arm else None)
            prefix = view+'/'+domain+'/'
            metrics[prefix+'correctness_delta'] = fractions[1]-fractions[0] if None not in fractions else None
            reads = [r for r in group if r['case']['kind'] in READ_KINDS]
            metrics[prefix+'read_all_saving'] = saving(reads)
            matched = both_success(reads, censored)
            shared = [r for r in reads if r['case']['case_id'] in matched]
            metrics[prefix+'read_matched_saving'] = saving(shared)
            endpoints = [saving([r for r in shared if r['case']['kind'] == 'ladder' and
                                r['case']['native_depth'] == depth]) for depth in (1, 6)]
            metrics[prefix+'depth6_minus_depth1'] = endpoints[1]-endpoints[0] if None not in endpoints else None
    return metrics

def percentile(values, q):
    position = (len(values)-1)*q
    low = math.floor(position)
    high = math.ceil(position)
    return values[low]+(values[high]-values[low])*(position-low)

def bootstrap(rows, censored, output_name):
    groups = defaultdict(list)
    for row in rows:
        groups[row['case']['template_group']].append(row)
    names = sorted(groups)
    point = metric_vector(rows, censored)
    samples = {key: [] for key in point}
    empty = Counter()
    rng = random.Random(SEED)
    output_path = ROOT/'analysis'/output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output_path, 'wt', encoding='utf-8') as retained:
        for index in range(DRAWS):
            group_indices = [rng.randrange(len(names)) for _ in names]
            drawn = [row for group_index in group_indices for row in groups[names[group_index]]]
            values = metric_vector(drawn, censored)
            retained.write(json.dumps(dict(draw=index, group_indices=group_indices, metrics=values))+'\n')
            for key, value in values.items():
                if value is None:
                    empty[key] += 1
                else:
                    samples[key].append(value)
    intervals = {}
    for key, values in samples.items():
        values.sort()
        intervals[key] = dict(point=point[key], lower=percentile(values, .025) if values else None,
            upper=percentile(values, .975) if values else None, empty_draws=empty[key],
            nonempty_draws=len(values), distinct_values=len(set(values)),
            degenerate_nonempty=bool(values) and values[0] == values[-1])
    return dict(draws=DRAWS, seed=SEED, unit='whole template group, both domains and paired arms together',
                template_groups=len(names), group_index=names, retained_draws=output_name, intervals=intervals)

def existing_rules(rows, censored, boot, compromised):
    """Existing P1-P4 diagnostic logic only; not invented P1-prime or P6 rules."""
    ci = boot['intervals']
    statuses = {}
    for view in ('V2', 'V3'):
        p1_domains, p2_domains, p4_domains = [], [], []
        for domain in ('arm', 'base'):
            reads = [r for r in rows if r['case']['domain'] == domain and r['case']['kind'] in READ_KINDS]
            matched = both_success(reads, censored)
            checks = [ci[view+'/'+domain+'/'+metric] for metric in ('read_all_saving', 'read_matched_saving')]
            if len(matched) < 4 or any(c['lower'] is None for c in checks):
                p1_domains.append('Uninformative')
            elif all(c['point'] is not None and c['point'] >= .20 and c['lower'] > 0 for c in checks):
                p1_domains.append('Support')
            elif any(c['upper'] <= 0 for c in checks):
                p1_domains.append('Against')
            else:
                p1_domains.append('Uninformative')
            correctness = ci[view+'/'+domain+'/correctness_delta']
            violation = any(r['score'].get('dispatch_violation') for r in rows if r['mode'] == 'macro' and r['case']['domain'] == domain)
            p2_domains.append('Against' if violation or correctness['upper'] is not None and correctness['upper'] < -.05 else 'Uninformative')
            endpoints = [len(both_success([r for r in reads if r['case']['kind'] == 'ladder' and
                                          r['case']['native_depth'] == depth], censored)) for depth in (1, 6)]
            contrast = ci[view+'/'+domain+'/depth6_minus_depth1']
            if min(endpoints) < 2 or contrast['lower'] is None:
                p4_domains.append('Uninformative')
            elif contrast['lower'] >= -.10 and contrast['upper'] <= .10:
                p4_domains.append('Support')
            elif contrast['lower'] > .10 or contrast['upper'] < -.10:
                p4_domains.append('Against')
            else:
                p4_domains.append('Uninformative')
        def combine(values):
            return 'Support' if all(v == 'Support' for v in values) else 'Against' if 'Against' in values else 'Uninformative'
        statuses[view] = {'P1': combine(p1_domains), 'P2': combine(p2_domains), 'P3': 'Uninformative', 'P4': combine(p4_domains)}
    final = {key: ('Uninformative' if compromised or statuses['V2'][key] != statuses['V3'][key]
                   else statuses['V2'][key]) for key in statuses['V2']}
    return dict(statuses_by_view=statuses, sensitivity_adjusted=final,
                label='Diagnostic implementation of existing rules; Stage 2 is dev-only, no predictions adjudicated',
                P3_note='No first-turn catalogue probe input; no P3 verdict beyond Uninformative.',
                P5_note='Existing P5 is an engineering-control gate; see unchanged Stage 1 receipts.',
                requested_P1_prime_through_P6='BLOCKED: definitions not supplied; no aliases invented')

def analyze(rows, locations, schedule, scope='dev'):
    assert len(rows) == len({r['id'] for r in rows})
    annotations = {r['id']: annotate(r) for r in rows}
    censored = {key for key, value in annotations.items() if value['censor_class'] != 'EVALUABLE'}
    matched = both_success(rows, censored)
    classes = Counter(a['censor_class'] for a in annotations.values())
    costs_by_view = {}
    for view, subset in [('V1_all_attempts', rows), ('V2_evaluable', [r for r in rows if r['id'] not in censored]),
                         ('matched_success', [r for r in rows if r['case']['case_id'] in matched])]:
        costs_by_view[view] = {mode: costs([r for r in subset if r['mode'] == mode]) for mode in MODES}
    operational = {}
    for mode in MODES:
        group = [r for r in rows if r['mode'] == mode]
        scheduled = sum(item['mode'] == mode for item in schedule)
        count_censored = sum(r['id'] in censored for r in group)
        evaluable = [r for r in group if r['id'] not in censored]
        correct = sum(r['primary_pass'] for r in evaluable)
        operational[mode] = dict(scheduled=scheduled, retained=len(group), not_started=scheduled-len(group),
            V1_correct_completed=correct, infrastructure_censored=count_censored,
            incorrect_evaluable=len(evaluable)-correct, V2_correct=correct, V2_denominator=len(evaluable),
            V3_correct=correct, V3_denominator=scheduled)
    exclusions = []
    gaps = []
    for name, pair in pairs_of(rows).items():
        first = next(iter(pair.values()))
        if any(r['id'] in censored for r in pair.values()) or len(pair) < 2:
            exclusions.append(dict(case_id=name, domain=first['case']['domain'], depth=first['case']['native_depth'],
                                   reason='censored arm' if len(pair) == 2 else 'unstarted arm'))
        if len(pair) == 2:
            spans = [read(locations[pair[mode]['id']]/'trace.json')['spans'] for mode in MODES]
            gaps.append(dict(case_id=name, **pair_gap(*spans)))
    tables = []
    for domain in ('arm', 'base'):
        for depth in (None, 1, 2, 4, 6):
            group = [r for r in rows if r['case']['domain'] == domain and
                     (depth is None or r['case']['kind'] == 'ladder' and r['case']['native_depth'] == depth)]
            counts = Counter()
            for pair in pairs_of(group).values():
                if len(pair) != 2:
                    counts['unpaired'] += 1
                elif any(r['id'] in censored for r in pair.values()):
                    counts['censored_pair'] += 1
                else:
                    p, m = (pair[mode]['primary_pass'] for mode in MODES)
                    counts['both_correct' if p and m else 'primitive_only' if p else 'macro_only' if m else 'neither'] += 1
            tables.append(dict(domain=domain, depth=depth, discordant_pair_counts=dict(counts),
                all_attempts={mode: costs([r for r in group if r['mode'] == mode]) for mode in MODES},
                excluded_censored_pairs=sum(e['domain'] == domain and (depth is None or e['depth'] == depth) for e in exclusions),
                rows=[{'trial_id': r['id'], 'censor_class': annotations[r['id']]['censor_class']} for r in group]))
    sequence = []
    for row in rows:
        sequence.append(dict(trial_id=row['id'], domain=row['case']['domain'], kind=row['case']['kind'],
            depth=row['case']['native_depth'], mode=row['mode'], censor_class=annotations[row['id']]['censor_class'],
            native_operations=[r['kind'] for r in row['actor_records']],
            tools=[entry.get('name', entry.get('tool', 'NOT_RECORDED')) for entry in row.get('tool_inputs', [])],
            tool_calls_with_arguments=row.get('tool_inputs', []),
            logical_model_calls=row['inference'].get('decision_calls'), physical_model_calls=row['inference']['calls']))
    boot = bootstrap(rows, censored, scope+'-bootstrap-draws.jsonl.gz')
    return dict(scope='Stage 2 dev-data validation; no P1-P4 adjudication' if scope == 'dev' else 'Held-out analysis under an approved freeze',
        study_label='AI-authored cases; no independent teammate authorship or semantic-novelty review',
        retained_trials=len(rows), scheduled_trials=len(schedule), matched_success_pairs=len(matched),
        classes=dict(classes), analysis_rows=list(annotations.values()), operational_views=operational,
        costs=costs_by_view, excluded_pairs=exclusions, pair_gaps=gaps,
        pair_gap_flags=sum(gap['flagged'] for gap in gaps), per_domain_depth=tables,
        batching_and_tool_sequence=sequence, bootstrap=boot,
        operationally_compromised=len(censored) >= 8, censored_flag_threshold=8,
        diagnostic_existing_rule_logic=existing_rules(rows, censored, boot, len(censored) >= 8),
        freeze_ready=False, stage3_model_requests=0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-roots', nargs='+', type=Path, default=[REV/'stage-2', REV/'stage-2-continuation-1'])
    parser.add_argument('--schedule', type=Path, default=REV/'stage-2/plan.json')
    parser.add_argument('--scope', choices=('dev', 'heldout'), default='dev')
    args = parser.parse_args()
    if args.scope == 'heldout':
        raise SystemExit('Held-out analysis disabled until missing prediction definitions and freeze gates are resolved; do not infer a completed freeze.')
    rows, locations = [], {}
    for folder in args.result_roots:
        for path in sorted((folder/'trials').glob('*/result.json')):
            row = read(path)
            rows.append(row)
            locations[row['id']] = path.parent
    result = analyze(rows, locations, read(args.schedule), scope=args.scope)
    write('analysis/dev-analysis.json', result)
    assert result['retained_trials'] == 36
    assert result['classes'].get('INFRA_CENSORED_PRE_OUTPUT') == 1
    assert result['classes'].get('EVALUABLE') == 35
    assert result['matched_success_pairs'] == 17
    assert [result['costs']['V1_all_attempts'][m]['calls'] for m in MODES] == [60, 34]
    assert [result['costs']['matched_success'][m]['calls'] for m in MODES] == [59, 32]
    failed = next(row for row in result['analysis_rows'] if row['trial_id'] == 'G1r1-dev-012-primitives')
    assert all(value == 'NOT_EVALUABLE' for value in failed['component_columns'].values())
    write('analysis/dev-validation.json', dict(existing_rule_engine_test='PASS',
        full_A4_gate='BLOCKED_MISSING_P1_PRIME_P6_DEFINITIONS', bootstrap_draws=DRAWS,
        seed=SEED, stage2_totals_reproduced=True, censored_trial_class_correct=True,
        raw_scorer_unchanged=True, model_requests=0))
    print(json_summary(result))

def json_summary(result):
    return {key: result[key] for key in ('retained_trials', 'classes', 'matched_success_pairs', 'pair_gap_flags', 'operational_views', 'freeze_ready')}

if __name__ == '__main__':
    main()
