"""New owner-supplied rules; original Stage 3 checkpoint stays immutable."""
from collections import Counter, defaultdict
from fractions import Fraction

DEPTHS = (1, 2, 4, 6)
CATALOGUE_SIZES = (3, 5, 10)
DOMAINS = ('arm', 'base')

def p1_status(means):
    values = [value for value in means.values() if value is not None]
    spread = max(values)-min(values) if values else None
    if any(value < 0 or value > 2 for value in values) or spread is not None and spread > 1:
        return 'Against'
    if any(means.get(depth) is None for depth in DEPTHS):
        return 'Uninformative'
    return 'Support' if all(Fraction(1, 2) <= value <= Fraction(3, 2) for value in values) and spread <= Fraction(1, 2) else 'Uninformative'

def p2_status(ratios):
    observed = [value for value in ratios.values() if value is not None]
    if any(value < Fraction(3, 4) or value > Fraction(5, 4) for value in observed):
        return 'Against'
    return 'Support' if all(ratios.get(depth) is not None for depth in DEPTHS) else 'Uninformative'

def combine_domains(statuses):
    if any(value == 'Against' for value in statuses.values()):
        return 'Against'
    return 'Support' if all(statuses.get(domain) == 'Support' for domain in DOMAINS) else 'Uninformative'

def sensitivity(primary, alternative, compromised=False, campaign_complete=True):
    return 'Uninformative' if compromised or not campaign_complete or primary != alternative else primary

def p4_from_probe(probe_rows):
    # Records come from a separately frozen first-turn scorer; no probe is launched here.
    rows = [row for row in probe_rows if row['backend'] == 'qwen']
    if not rows:
        return dict(status='Uninformative', reason='No Qwen first-turn probe results', contrasts=[])
    pairs = defaultdict(dict)
    for row in rows:
        if row['catalogue_size'] not in CATALOGUE_SIZES:
            raise ValueError('catalogue_size_not_in_confirmed_3_5_10_design')
        key = (row['case_id'], row['catalogue_size'])
        assert row['catalogue_size'] not in pairs[row['case_id']], 'duplicate_probe_cell'
        assert type(row['selection_correct']) is bool
        pairs[row['case_id']][row['catalogue_size']] = row
    if any(set(pair) != set(CATALOGUE_SIZES) for pair in pairs.values()):
        return dict(status='Uninformative', reason='Incomplete paired catalogue-size cells', contrasts=[])
    accuracy = {}
    for size in CATALOGUE_SIZES:
        group = [pair[size] for pair in pairs.values()]
        if any(row.get('censored', False) for row in group):
            return dict(status='Uninformative', reason='Censored probe cells need explicit V2/V3 input views', contrasts=[])
        accuracy[size] = Fraction(sum(row['selection_correct'] for row in group), len(group))
    contrasts = [(small, large, accuracy[small]-accuracy[large])
                 for i, small in enumerate(CATALOGUE_SIZES) for large in CATALOGUE_SIZES[i+1:]]
    worst = max(drop for _, _, drop in contrasts)
    return dict(status='Against' if worst >= Fraction(1, 5) else 'Support',
        paired_cases=len(pairs), accuracy={size: float(value) for size, value in accuracy.items()},
        worst_accuracy_fall=float(worst), equality_boundary='Against at exactly 0.20, owner confirmed',
        contrasts=[dict(smaller=small, larger=large, accuracy_fall=float(drop)) for small, large, drop in contrasts])

def p4_views(probe_rows, compromised=False):
    censored_cases = {row['case_id'] for row in probe_rows if row.get('censored')}
    primary = p4_from_probe([row for row in probe_rows if row['case_id'] not in censored_cases])
    alternative = p4_from_probe([{**row, 'selection_correct': False if row.get('censored') else row['selection_correct'],
                                 'censored': False} for row in probe_rows])
    return dict(V2=primary, V3=alternative,
                final=sensitivity(primary['status'], alternative['status'], compromised),
                excluded_censored_cases=len(censored_cases))

def weighted_pairs(rows):
    counts = Counter(row['id'] for row in rows)
    pairs = defaultdict(dict)
    for row in rows:
        pairs[row['case']['case_id']][row['mode']] = row
    result = []
    for pair in pairs.values():
        if set(pair) == {'primitives', 'macro'}:
            p, m = pair['primitives'], pair['macro']
            assert counts[p['id']] == counts[m['id']], 'resample_must_keep_whole_pairs'
            result.append((p, m, counts[p['id']]))
    return result

def point_metrics(rows, censored, view):
    pairs = weighted_pairs(rows)
    metrics, cells = {}, []
    for domain in (*DOMAINS, 'pooled'):
        means, ratios = {}, {}
        for depth in DEPTHS:
            selected = [(p, m, weight) for p, m, weight in pairs
                if p['case']['kind'] == 'ladder' and p['case'].get('depth_analysis')
                and p['case']['native_depth'] == depth and (domain == 'pooled' or p['case']['domain'] == domain)]
            evaluable = [(p, m, weight) for p, m, weight in selected if p['id'] not in censored and m['id'] not in censored]
            matched = [(p, m, weight) for p, m, weight in evaluable if p['primary_pass'] and m['primary_pass']]
            count = sum(weight for p, m, weight in matched)
            means[depth] = Fraction(sum(weight*(p['inference']['calls']-m['inference']['calls']) for p, m, weight in matched), count) if count else None
            native_rows = evaluable if view == 'V2' else selected
            primitive = sum(weight*len(p['actor_records']) for p, m, weight in native_rows)
            macro = sum(weight*len(m['actor_records']) for p, m, weight in native_rows)
            ratios[depth] = Fraction(macro, primitive) if primitive and native_rows else None
            metrics[f'{domain}/depth{depth}/absolute_calls_saved'] = float(means[depth]) if means[depth] is not None else None
            metrics[f'{domain}/depth{depth}/native_ratio'] = float(ratios[depth]) if ratios[depth] is not None else None
            cells.append(dict(domain=domain, depth=depth, matched_success_pairs=count,
                excluded_censored_pairs=sum(weight for p, m, weight in selected if p['id'] in censored or m['id'] in censored),
                native_pair_count=sum(weight for p, m, weight in native_rows), primitive_native=primitive, macro_native=macro,
                absolute_calls_saved=metrics[f'{domain}/depth{depth}/absolute_calls_saved'],
                native_ratio=metrics[f'{domain}/depth{depth}/native_ratio'],
                undefined_native_ratio_reason='No comparable nonzero primitive denominator' if ratios[depth] is None else None))
        values = [value for value in means.values() if value is not None]
        metrics[domain+'/absolute_saving_spread'] = float(max(values)-min(values)) if len(values) == len(DEPTHS) else None
        metrics[domain+'/P1_prime_status'] = p1_status(means)
        metrics[domain+'/P2_status'] = p2_status(ratios)
    return metrics, cells

def p5_status(hosting_source_changes, fresh_controls_passed):
    if hosting_source_changes:
        return 'Against'
    return 'Support' if fresh_controls_passed else 'Uninformative'

def p6_descriptive(rows, censored, view):
    eligible = [row for row in rows if view == 'V3' or row['id'] not in censored]
    output = []
    for domain in (*DOMAINS, 'pooled'):
        for kind in ('ladder', 'unavailable_source', 'write', 'write_fault', 'missing_prerequisite'):
            for mode in ('primitives', 'macro'):
                group = [row for row in eligible if row['case']['kind'] == kind and row['mode'] == mode
                         and (domain == 'pooled' or row['case']['domain'] == domain)]
                output.append(dict(domain=domain, kind=kind, mode=mode, trials=len(group),
                    mean_calls=sum(row['inference']['calls'] for row in group)/len(group) if group else None))
    return dict(status='DESCRIPTIVE_ONLY', threshold=None, by_requested_kind=output,
        note='Healthy write, partial/ineffective write and missing prerequisite remain separate. No Support/Against verdict.')
