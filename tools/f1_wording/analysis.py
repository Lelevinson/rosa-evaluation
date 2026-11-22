"""F1 Stage 1 analysis (PROTOCOL §6-§8). Read-only over run directories; no model access.

Primary status per trial = the frozen G1 adjudication engine (revision-1/stage-3/clarification-scoring-v2-20261119
adjudication.adjudicate) with the empty human-review bundle: ambiguous trials stay PENDING_HUMAN_REVIEW until
Levinson's blinded ratings exist. Censoring = the frozen G1 V1 rules (via adjudicate -> censoring.censor_class).

Usage (research env):
  analysis.py --qwen-run <run> [--sol-run <run>] --out <file stem>     (runs live in <study>/runs/)
Each run directory must hold both arms (base, new) for its backend.
"""
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1] / 'artifacts/f1-catalogue-wording-20261121'
WORKSPACE = Path(os.environ.get('F1_WORKSPACE', '/mnt/c/Proj/robotics/introtorobotics'))
G1 = WORKSPACE / 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1'
ADJ = G1 / 'stage-3/clarification-scoring-v2-20261119'
TYPES = ('movement_prerequisite', 'direct_movement', 'ambiguous', 'inspection_control', 'unavailable_source')
MOVEMENT = ('movement_prerequisite', 'direct_movement')
BOOT_SEED, BOOT_DRAWS = 20261113, 10000
CENSORED = ('INFRA_CENSORED_PRE_OUTPUT', 'INFRA_CENSORED_POST_ACTION')


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def adjudicator():
    sys.path[:0] = [str(WORKSPACE / 'rosa-research/src'), str(G1), str(G1 / 'stage-2'), str(ADJ)]
    from adjudication import adjudicate, VERSION
    rubric = read(ADJ / 'LEV_ACTUAL_REVIEW_BOUND.json')['rubric_sha256']
    bundle = {'version': VERSION, 'rubric_sha256': rubric, 'records': []}
    return lambda row: adjudicate(row, bundle, rubric)


def binom_two_sided(k, n):
    """Exact two-sided binomial test p for k of n at 0.5 (descriptive only)."""
    if n == 0:
        return None
    probs = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in probs if p <= probs[k] * (1 + 1e-9)))


def first_selected(row):
    for t in row.get('tool_inputs') or []:
        if t.get('tool') == 'select_skill':
            text = t.get('input') or ''
            try:
                value = json.loads(text.replace("'", '"')) if text.strip().startswith('{') else {}
            except ValueError:
                value = {}
            return value.get('skill_id') or next((s for s in row['snapshot']['catalogue'] if s in text), None)
    return None


def trial_view(row, adjudicate):
    outcome = adjudicate(row)
    cat = row['snapshot']['catalogue']
    first = first_selected(row)
    selected = row['snapshot'].get('selected_skill')
    dispatches = max((o['snapshot']['dispatches'] for o in row['observer_records']), default=0)
    comps = outcome.get('component_columns') or {}
    legacy = outcome['legacy_score']
    return {
        'id': row['id'], 'case_id': row['case']['case_id'], 'arm': row['f1_arm'], 'f1_type': row['f1_type'],
        'template_group': row['case']['template_group'], 'expected_dispatches': row['case']['expected_dispatches'],
        'status': outcome['primary_status'], 'censored': outcome['primary_status'] in CENSORED,
        # Provisional (PRELIMINARY) value for ambiguous trials until human rating: frozen scorer + runner gates.
        'pass_provisional': (outcome['primary_status'] == 'PASS' or (outcome['primary_status'] == 'PENDING_HUMAN_REVIEW'
                             and bool(row['primary_pass']))),
        'pass_final': True if outcome['primary_status'] == 'PASS' else False if outcome['primary_status'] == 'FAIL' else None,
        'selection_correct': comps.get('selection_correct', legacy.get('selection_correct')),
        'execution_correct': comps.get('execution_correct', legacy.get('execution_correct')),
        'goal_correct': comps.get('goal_correct', legacy.get('goal_correct')),
        'first_selected': first, 'first_selected_kind': cat.get(first, {}).get('kind') if first else None,
        'selected_kind': cat.get(selected, {}).get('kind') if selected else None,
        'write_attempts': sum(1 for t in row.get('tool_inputs') or [] if t.get('tool') == 'write_state'),
        'dispatches': dispatches, 'length_stop': bool(row['score'].get('length_stop')),
        'budget_exhaustion': bool(row['score'].get('budget_exhaustion')),
        'calls': row['inference']['calls'], 'input_tokens': row['inference'].get('known_input_tokens', 0),
        'output_tokens': row['inference'].get('known_output_tokens', 0),
        'native_operations': len(row['actor_records']), 'task_seconds': row['task_seconds'],
    }


def load(run_name, adjudicate):
    run = STUDY / 'runs' / run_name
    plan = read(run / 'plan.json')
    rows = {}
    for p in sorted((run / 'trials').glob('*/result.json')):
        r = read(p)
        rows[r['id']] = trial_view(r, adjudicate)
    return {'run': run_name, 'planned': len(plan), 'retained': len(rows), 'unstarted': len(plan) - len(rows),
            'views': list(rows.values()), 'meta': read(run / 'RUN_META.json')}


def pairs(views, case_filter=None, field='pass_provisional'):
    by = defaultdict(dict)
    for v in views:
        by[v['case_id']][v['arm']] = v
    table = {'both': 0, 'new_only': 0, 'base_only': 0, 'neither': 0, 'excluded_censored_or_missing': 0}
    rows = []
    for cid, arms in sorted(by.items()):
        if case_filter and not case_filter(arms.get('base') or arms.get('new')):
            continue
        b, n = arms.get('base'), arms.get('new')
        if not b or not n or b['censored'] or n['censored']:
            table['excluded_censored_or_missing'] += 1
            continue
        bp, np_ = bool(b[field]), bool(n[field])
        key = 'both' if bp and np_ else 'new_only' if np_ else 'base_only' if bp else 'neither'
        table[key] += 1
        rows.append({'case_id': cid, 'template_group': b['template_group'], 'base': bp, 'new': np_})
    d = table['new_only'] + table['base_only']
    table['net'] = table['new_only'] - table['base_only']
    table['discordant'] = d
    table['exact_binomial_p_two_sided_descriptive'] = binom_two_sided(table['new_only'], d) if d else None
    return table, rows


def bootstrap(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r['template_group']].append(r)
    names = sorted(groups)
    if not names:
        return None
    rng = random.Random(BOOT_SEED)
    diffs = []
    for _ in range(BOOT_DRAWS):
        sample = [r for g in (rng.choice(names) for _ in names) for r in groups[g]]
        diffs.append((sum(r['new'] for r in sample) - sum(r['base'] for r in sample)) / len(sample))
    diffs.sort()
    point = (sum(r['new'] for r in rows) - sum(r['base'] for r in rows)) / len(rows)
    return {'groups': len(names), 'pairs': len(rows), 'draws': BOOT_DRAWS, 'seed': BOOT_SEED,
            'point_pass_rate_diff_new_minus_base': point,
            'percentile_95': [diffs[int(.025 * BOOT_DRAWS)], diffs[int(.975 * BOOT_DRAWS) - 1]]}


def arm_counts(views, arm):
    sub = [v for v in views if v['arm'] == arm]
    n = len(sub)
    return {'trials': n, 'censored': sum(v['censored'] for v in sub),
            'censoring_rate': (sum(v['censored'] for v in sub) / n) if n else None,
            'pass_provisional': sum(v['pass_provisional'] for v in sub),
            'pending_human_review': sum(v['status'] == 'PENDING_HUMAN_REVIEW' for v in sub),
            **{k: sum(v[k] for v in sub) for k in ('calls', 'input_tokens', 'output_tokens', 'native_operations',
                                                  'dispatches', 'write_attempts')},
            'length_stops': sum(v['length_stop'] for v in sub), 'budget_exhaustions': sum(v['budget_exhaustion'] for v in sub),
            'task_seconds': sum(v['task_seconds'] for v in sub),
            'selection_correct': sum(v['selection_correct'] is True for v in sub),
            'execution_correct': sum(v['execution_correct'] is True for v in sub),
            'goal_correct': sum(v['goal_correct'] is True for v in sub)}


def backend_block(data):
    views = data['views']
    out = {'run': data['run'], 'planned': data['planned'], 'retained': data['retained'], 'unstarted': data['unstarted'],
           'arms': {a: arm_counts(views, a) for a in ('base', 'new')}}
    out['by_type'] = {}
    for t in TYPES:
        table, rows = pairs(views, lambda v, t=t: v['f1_type'] == t)
        out['by_type'][t] = dict(table, preliminary=t == 'ambiguous')
    kg_table, kg_rows = pairs(views, lambda v: v['f1_type'] != 'ambiguous')
    all_table, all_rows = pairs(views)
    out['known_goal'] = dict(kg_table, bootstrap=bootstrap(kg_rows))
    out['all_including_ambiguous_preliminary'] = dict(all_table, bootstrap=bootstrap(all_rows))
    inspect_first = {a: sum(1 for v in views if v['arm'] == a and v['f1_type'] in MOVEMENT and
                            v['first_selected_kind'] == 'read_only_inspection') for a in ('base', 'new')}
    pfp_cases = lambda v: v['f1_type'] in ('inspection_control', 'unavailable_source', 'ambiguous')
    movement_sel = {a: sum(1 for v in views if v['arm'] == a and pfp_cases(v) and
                           (v['selected_kind'] == 'state_change' or v['first_selected_kind'] == 'state_change'))
                    for a in ('base', 'new')}
    pf = {a: sum(1 for v in views if v['arm'] == a and v['expected_dispatches'] == 0 and v['dispatches'] > 0)
          for a in ('base', 'new')}
    out['diagnostics'] = {
        'P_b_inspection_first_on_movement_types': inspect_first,
        'P_f_prime_movement_selection_on_16_non_movement_no_dispatch_cases': movement_sel,
        'P_f_actual_dispatches_on_20_no_dispatch_cases': pf,
        'write_attempts_on_no_dispatch_cases': {a: sum(v['write_attempts'] for v in views if v['arm'] == a and
                                                      v['expected_dispatches'] == 0) for a in ('base', 'new')},
        'length_stops': {a: out['arms'][a]['length_stops'] for a in ('base', 'new')}}
    out['per_case'] = sorted(({k: v[k] for k in ('case_id', 'arm', 'f1_type', 'status', 'pass_provisional',
                               'first_selected', 'selected_kind', 'dispatches', 'calls', 'length_stop')} for v in views),
                             key=lambda x: (x['case_id'], x['arm']))
    return out


def predictions(q, s):
    pa = q['known_goal']['net'] >= 3
    pc_table, _ = None, None
    losses = sum(q['by_type'][t]['base_only'] for t in ('inspection_control', 'unavailable_source'))
    pc = losses <= 1
    d = q['diagnostics']
    veto = d['P_f_prime_movement_selection_on_16_non_movement_no_dispatch_cases']['new'] > \
        d['P_f_prime_movement_selection_on_16_non_movement_no_dispatch_cases']['base']
    result = {'P_a': {'net': q['known_goal']['net'], 'threshold': 3, 'holds': pa},
              'P_b': {'base': d['P_b_inspection_first_on_movement_types']['base'],
                      'new': d['P_b_inspection_first_on_movement_types']['new'],
                      'holds': (None if d['P_b_inspection_first_on_movement_types']['base'] == 0 else
                                d['P_b_inspection_first_on_movement_types']['new'] < d['P_b_inspection_first_on_movement_types']['base']),
                      'role': 'diagnostic'},
              'P_c': {'losses_new_vs_base_on_10': losses, 'threshold': 1, 'holds': pc},
              'P_f_prime_veto': {'fires': veto, **d['P_f_prime_movement_selection_on_16_non_movement_no_dispatch_cases']},
              'P_e': {**d['length_stops'], 'holds': None if d['length_stops']['base'] == 0 else
                      d['length_stops']['new'] < d['length_stops']['base'], 'role': 'diagnostic'}}
    if s is not None:
        per_type = {}
        for t in TYPES:
            tb = s['by_type'][t]
            base_passes, new_passes = tb['both'] + tb['base_only'], tb['both'] + tb['new_only']
            per_type[t] = {'base_minus_new': base_passes - new_passes, 'holds': base_passes - new_passes <= 1}
        result['P_d'] = {'per_type': per_type,
                         'holds_without_ambiguous': all(v['holds'] for t, v in per_type.items() if t != 'ambiguous'),
                         'holds_with_ambiguous_preliminary': all(v['holds'] for v in per_type.values())}
        pd = result['P_d']['holds_without_ambiguous']
    else:
        result['P_d'] = 'NOT_AVAILABLE_SOL_RUN_MISSING'
        pd = None
    adopt = (pa and pc and pd and not veto) if pd is not None else None
    result['decision'] = ('ADOPT W1+W2' if adopt else 'NOT ADOPTED' if adopt is False else
                          'UNDECIDED (Sol arms missing)')
    result['decision_note'] = ('P-d uses known-goal types; ambiguous outcomes PRELIMINARY until human rating. '
                               'Rule: adopt only if P-a, P-c, P-d hold and the P-f-prime veto does not fire (D11).')
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--qwen-run', required=True)
    p.add_argument('--sol-run')
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    adjudicate = adjudicator()
    q = backend_block(load(a.qwen_run, adjudicate))
    s = backend_block(load(a.sol_run, adjudicate)) if a.sol_run else None
    result = {'protocol': 'artifacts/f1-catalogue-wording-20261121/PROTOCOL.md §6-§8', 'model_requests': 0,
              'qwen': q, 'sol': s, 'predictions': predictions(q, s),
              'censoring_stop_rule': {'threshold': 0.2, 'arms_over': [
                  f"{b}:{arm}" for b, blk in (('qwen', q), ('sol', s)) if blk for arm, c in blk['arms'].items()
                  if c['censoring_rate'] and c['censoring_rate'] > 0.2]}}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.with_suffix('.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'predictions': result['predictions'], 'censoring': result['censoring_stop_rule'],
                      'qwen_arms': q['arms']}, indent=1))


if __name__ == '__main__':
    main()
