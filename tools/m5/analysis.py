"""Post-hoc family-aware descriptive analysis of saved M4 results; no trial changes."""
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
M4 = ROOT / 'artifacts/macro-m4-20261027'
OUT = ROOT / 'artifacts/macro-m5-20261027'
METRICS = ('requests', 'input_tokens', 'output_tokens', 'native_operations', 'task_seconds')


def write_csv(path, records):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def costs(rows):
    return {'requests': sum(r['inference']['calls'] for r in rows),
            'input_tokens': sum(r['inference']['known_input_tokens'] for r in rows),
            'output_tokens': sum(r['inference']['known_output_tokens'] for r in rows),
            'native_operations': sum(r['score']['native_operations'] for r in rows),
            'task_seconds': sum(r['wall_seconds'] for r in rows)}


def reduction(reference, candidate):
    return 100 * (1 - candidate / reference) if reference else None


def percentile(values, q):
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * q
    lower = int(position)
    return values[lower] + (values[min(lower + 1, len(values) - 1)] - values[lower]) * (position - lower)


def wilson(successes, total):
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0, center - half), min(1, center + half)]


def analyze():
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = json.loads((M4 / 'analysis.json').read_text())
    assert frozen['complete'] and not frozen['clarification_review_pending']
    result = {'kind': 'Exploratory retrospective analysis; frozen M4 scores and screen unchanged',
        'bootstrap': {'unit': 'whole task family, retaining both repetitions and paired conditions',
                      'families': 10, 'resamples': 10000, 'seed': 20261027,
                      'interval': '2.5th/97.5th percentile empirical family-resampling range; not a population guarantee'},
        'input_sha256': {}, 'backends': {}}
    family_csv, paired_csv, efficiency_csv = [], [], []
    for backend in ('siwc', 'ollama'):
        path = M4 / backend / 'checkpoint.json'
        result['input_sha256'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        checkpoint = json.loads(path.read_text())
        rows = checkpoint['trials']
        assert checkpoint['status'] == 'COMPLETE' and len(rows) == 40
        assert all(r['inference']['usage_complete'] and r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
        groups = {}
        for row in rows:
            groups.setdefault((row['case'], row['repetition']), {})[row['condition']] = row
        assert len(groups) == 20 and all(set(pair) == {'primitives', 'macro'} for pair in groups.values())
        names = sorted(set(r['case'] for r in rows))
        assert len(names) == 10
        family = {}
        for name in names:
            pairs = [pair for (case, _), pair in groups.items() if case == name]
            assert len(pairs) == 2
            family[name] = {c: [p[c] for p in pairs] for c in ('primitives', 'macro')}
            for c in ('primitives', 'macro'):
                subset = family[name][c]
                family_csv.append({'backend': backend, 'family': name, 'condition': c, 'trials': 2,
                    'primary_passes': sum(r['primary_pass'] for r in subset), **costs(subset),
                    'invalid_attempts': sum(r['score']['invalid_attempts'] for r in subset),
                    'wrong_goal_successes': sum(r['score']['accepted_success_wrong_user_goal'] for r in subset)})
        counts = {'both_pass': 0, 'primitives_only': 0, 'macro_only': 0, 'both_fail': 0}
        for (name, repetition), pair in groups.items():
            p, m = pair['primitives'], pair['macro']
            label = ('both_pass' if p['primary_pass'] and m['primary_pass'] else
                     'primitives_only' if p['primary_pass'] else 'macro_only' if m['primary_pass'] else 'both_fail')
            counts[label] += 1
            paired_csv.append({'backend': backend, 'family': name, 'repetition': repetition,
                'primitives_primary_pass': p['primary_pass'], 'macro_primary_pass': m['primary_pass'],
                'paired_result': label, 'primitives_job': p['job']['id'], 'macro_job': m['job']['id']})
        summaries = {}
        for cohort in ('all_attempts', 'both_pass_pairs'):
            pairs = list(groups.values()) if cohort == 'all_attempts' else [p for p in groups.values() if all(r['primary_pass'] for r in p.values())]
            totals = {c: costs([p[c] for p in pairs]) for c in ('primitives', 'macro')}
            reductions = {k: reduction(totals['primitives'][k], totals['macro'][k]) for k in METRICS}
            summaries[cohort] = {'pairs': len(pairs), 'costs': totals, 'reduction_percent': reductions}
            for condition in ('primitives', 'macro'):
                efficiency_csv.append({'backend': backend, 'cohort': cohort, 'pairs': len(pairs),
                                       'condition': condition, **totals[condition]})
        data = {'paired_outcomes': counts, 'efficiency': summaries, 'conditions': {},
                'engineering_screen_pass': frozen['backends'][backend]['engineering_screen_pass']}
        for condition in ('primitives', 'macro'):
            sub = [r for r in rows if r['condition'] == condition]
            passed = sum(r['primary_pass'] for r in sub)
            assert passed == frozen['backends'][backend]['conditions'][condition]['primary_passes']
            data['conditions'][condition] = {'primary_passes': passed, 'trials': 20,
                'mean_task_seconds': sum(r['wall_seconds'] for r in sub) / 20,
                'median_task_seconds': median(r['wall_seconds'] for r in sub),
                'wilson95_independent_binomial_reference_only': wilson(passed, 20)}
        # Resample whole families, preserving the paired conditions/repetitions.
        distributions = {'primary_difference_percentage_points': []}
        for cohort in summaries:
            for key in METRICS:
                distributions[cohort + ':' + key + '_reduction_percent'] = []
        rng = random.Random(20261027)
        for _ in range(10000):
            chosen = [rng.choice(names) for _ in names]
            sample = {c: [r for name in chosen for r in family[name][c]] for c in ('primitives', 'macro')}
            distributions['primary_difference_percentage_points'].append(
                100 * (sum(r['primary_pass'] for r in sample['macro']) - sum(r['primary_pass'] for r in sample['primitives'])) / 20)
            for cohort in summaries:
                totals = {c: {key: 0 for key in METRICS} for c in ('primitives', 'macro')}
                for name in chosen:
                    for pair in [p for (case, _), p in groups.items() if case == name]:
                        if cohort == 'both_pass_pairs' and not all(r['primary_pass'] for r in pair.values()):
                            continue
                        for c in totals:
                            one = costs([pair[c]])
                            for key in METRICS:
                                totals[c][key] += one[key]
                for key in METRICS:
                    value = reduction(totals['primitives'][key], totals['macro'][key])
                    if value is not None:
                        distributions[cohort + ':' + key + '_reduction_percent'].append(value)
        data['family_resampling_ranges'] = {key: {'low': percentile(values, .025), 'high': percentile(values, .975),
                                                   'valid_resamples': len(values)} for key, values in distributions.items()}
        # Exact family-level sign-flip sensitivity, not a randomized-trial test.
        differences = [sum(r['primary_pass'] for r in family[name]['macro']) -
                       sum(r['primary_pass'] for r in family[name]['primitives']) for name in names]
        observed = abs(sum(differences))
        flipped = [abs(sum(s * d for s, d in zip(signs, differences))) for signs in itertools.product((-1, 1), repeat=10)]
        data['exploratory_family_sign_flip'] = {'p_two_sided': sum(v >= observed for v in flipped) / len(flipped),
            'assumption': 'Within-family condition-label exchangeability/symmetry; not established by this fixed designed suite.',
            'interpretation': 'Failure to reject is not equivalence or noninferiority.'}
        result['backends'][backend] = data
    write_csv(OUT / 'per-family-results.csv', family_csv)
    write_csv(OUT / 'paired-outcomes.csv', paired_csv)
    write_csv(OUT / 'efficiency-both-views.csv', efficiency_csv)
    (OUT / 'retrospective-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def uncertainty_report(data):
    lines = ['# Exploratory uncertainty and paired analysis', '', 'Date: **2026-10-27**.', '',
        'This is retrospective postprocessing, not a changed M4 protocol or a new experiment. '
        'The frozen engineering screen and primary scores are unchanged. Ten hand-authored '
        'families with two repeated cases do not form20 independent task families. The primary '
        'presentation is the family table and paired outcomes, not a pooled p-value.', '',
        '| Backend | Both pass | Primitive-only pass | Macro-only pass | Both fail |', '|---|---:|---:|---:|---:|']
    for b, label in (('siwc', 'Sol'), ('ollama', 'Qwen')):
        c = data['backends'][b]['paired_outcomes']
        lines.append(f"| {label} | {c['both_pass']} | {c['primitives_only']} | {c['macro_only']} | {c['both_fail']} |")
    lines += ['', '## Independent-binomial references, not design-adjusted intervals', '',
        '| Backend / condition | Pass /20 | Wilson95 reference |', '|---|---:|---:|']
    for b, label in (('siwc', 'Sol'), ('ollama', 'Qwen')):
        for c, row in data['backends'][b]['conditions'].items():
            low, high = row['wilson95_independent_binomial_reference_only']
            lines.append(f"| {label} / {c} | {row['primary_passes']}/20 | {100*low:.1f}%–{100*high:.1f}% |")
    lines += ['', 'Wilson intervals assume an independent-binomial model. They ignore pairing and '
        'family dependence here; they are not the final uncertainty, a guaranteed lower bound '
        'on it, or a proof of reliability preservation. The formula follows the '
        '[NIST proportions reference](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).', '',
        '## Whole-family resampling sensitivity', '',
        'Resample ten entire families with replacement10,000 times, seed20261027. Preserve '
        'both repetitions and paired conditions within each family. Report linear-interpolated '
        '2.5th/97.5th percentiles. This explores dependence on the observed family mix; these '
        'ranges are not calibrated population guarantees for unseen robots/tasks. In particular, '
        'resampling Sol\'s all-success observations cannot invent unseen failures. Its degenerate '
        'zero correctness-difference range must not be read as certainty of equivalence.', '',
        '| Backend | Metric / cohort | 95% empirical family-resampling range | Valid draws |',
        '|---|---|---:|---:|']
    for b, label in (('siwc', 'Sol'), ('ollama', 'Qwen')):
        ranges = data['backends'][b]['family_resampling_ranges']
        for key in ('primary_difference_percentage_points', 'all_attempts:requests_reduction_percent',
                    'both_pass_pairs:requests_reduction_percent', 'both_pass_pairs:task_seconds_reduction_percent'):
            row = ranges[key]
            lines.append(f"| {label} | {key} | {row['low']:.1f} to {row['high']:.1f} | {row['valid_resamples']} |")
    lines += ['', 'Correctness difference is macro minus primitives, in percentage points. Resource '
        'reduction is100×(1−macro/primitive). A zero denominator is omitted from that metric\'s '
        'draws, not replaced with zero benefit. Matched-success resampling remains conditional '
        'on both systems passing; it does not recover costs on discordant cases.', '',
        'Whole-cluster resampling and the difficulty of inference with few clusters are discussed '
        'by [Cameron and Miller](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf). '
        'That methodological source does not validate our designed task suite as a random sample.', '',
        'The exact exploratory family sign-flip sensitivity gives two-sided p=1.0 for both '
        'backends (Sol has no observed correctness variation; Qwen has only two families with '
        'nonzero condition differences). This relies on an unestablished exchangeability '
        'assumption and is not a population-level hypothesis-test result. It supplies no '
        'evidence of equivalence, no proof of noise, and no reason to overturn the failed '
        'Qwen engineering screen. No multiple exploratory statistics were used to select a '
        'favorable claim or rerun tasks.']
    (OUT / 'UNCERTAINTY_AND_PAIRED_ANALYSIS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    data = analyze()
    uncertainty_report(data)
    print(json.dumps({b: {'paired': d['paired_outcomes'], 'both_pass_costs': d['efficiency']['both_pass_pairs'],
                          'correctness_range': d['family_resampling_ranges']['primary_difference_percentage_points']}
                      for b, d in data['backends'].items()}, indent=2))


if __name__ == '__main__':
    main()
