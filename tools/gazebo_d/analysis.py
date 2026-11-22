"""Gazebo D analysis (D0_PROTOCOL §7-§9). Stdlib only, deterministic, zero model calls, no trial reruns.

Reads artifacts/gazebo-d-20261121/runs/<stage>/*/result.json (written by experiments/gazebo_d/runner.py),
the D cases and schedule, and optional human clarification ratings (reviews.json:
{"<trial folder name>": {"pass": bool, "reason": str, "rater": str}}). Writes analysis.json + ANALYSIS.md.

Rules:
  censoring = G1 CENSORING_RULES_V1: a trial is INFRA_CENSORED when its last model request did not return
    (UNRETURNED / EXTERNAL_FAILURE) and the trial ended with an error that is not a task budget/deadline
    (ControlledStop, TimeoutError); PRE_OUTPUT if no native operation happened, else POST_ACTION.
  V1 all scheduled (correct / incorrect / censored / unstarted); V2 evaluable; V3 censored = failure.
  Prediction status follows V2; if V3 differs -> Uninformative. >= 5 of 40 held-out trials censored for a
  model -> operationally compromised -> all its predictions Uninformative.
  Ambiguous cases: excluded from known-goal statistics; their pass needs a human rating (PENDING otherwise).
  Bootstrap: whole template groups (known-goal groups only), 10,000 draws, seed 20261113, percentile 95%.

Usage:
  python -I -B tools/gazebo_d/analysis.py analyze <stage> [--runs DIR] [--out DIR] [--reviews FILE]
  python -I -B tools/gazebo_d/analysis.py d1-gate [--runs DIR]     # writes runs/dev/D1_GATE.json
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
D = REPO / 'artifacts/gazebo-d-20261121'
SEED, DRAWS = 20261113, 10000
NOT_CENSORING = {'ControlledStop', 'TimeoutError', None}
MODELS = ['sol', 'qwen', 'ministral', 'granite', 'llama']


# ---------------------------------------------------------------- loading

def load_cases():
    return {c['id']: c for s in ('dev', 'heldout')
            for c in json.loads((D / 'cases' / f'{s}.json').read_text(encoding='utf-8'))}


def load_rows(stage_dir):
    rows = []
    for path in sorted(Path(stage_dir).glob('*/result.json')):
        r = json.loads(path.read_text(encoding='utf-8'))
        r['_trial'] = path.parent.name
        rows.append(r)
    return rows


def censoring(r):
    events = (r.get('inference') or {}).get('events') or []
    last = events[-1]['status'] if events else None
    if r.get('error_type') in NOT_CENSORING or last not in ('UNRETURNED', 'EXTERNAL_FAILURE'):
        return None
    return 'POST_ACTION' if (r.get('snapshot') or {}).get('operations') else 'PRE_OUTPUT'


def enrich(r, cases, reviews):
    case = cases[r['case']]
    out = {'trial': r['_trial'], 'model': r['model'], 'arm': r['condition'], 'case': r['case'],
           'family': case['family'], 'd_type': case['d_type'], 'group': case['template_group'],
           'ambiguous': case['kind'] == 'clarification', 'censored': censoring(r)}
    s = r['score']
    passed = bool(r['primary_pass'] and (r.get('phoenix_audit') or {}).get('pass', False))
    review = None
    if out['ambiguous']:
        review = reviews.get(r['_trial'])
        passed = None if review is None else bool(passed and review['pass'])
    out.update(passed=passed, review=review, automated_pass=bool(r['primary_pass']),
               selection=bool(s['goal_correct']),
               execution=bool(s['goal_correct'] and s['selected_outcome_correct'] and not s['dispatch_violations']
                              and s['dispatches'] == case['writes'] and s['injected_fault_exercised'] is not False),
               selected_skill=(r.get('snapshot') or {}).get('selected_skill'), expected_skill=case['skill'],
               calls=r['inference']['calls'], decision_calls=r['inference'].get('decision_calls', r['inference']['calls']),
               input_tokens=r['inference']['known_input_tokens'], output_tokens=r['inference']['known_output_tokens'],
               usage_complete=r['inference'].get('usage_complete', True),
               native=s['native_operations'], seconds=r['wall_seconds'], offload=(r.get('offload') or {}).get('vram_fraction'))
    return out


# ---------------------------------------------------------------- statistics

def binom_two_sided(b, c):
    n = b + c
    if n == 0:
        return None
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def views(rows, scheduled):
    """V1/V2/V3 per arm over known-goal trials."""
    out = {}
    for arm in ('primitives', 'macro'):
        sub = [r for r in rows if r['arm'] == arm and not r['ambiguous']]
        sched = scheduled.get(arm, 0)
        correct = sum(r['passed'] for r in sub if not r['censored'])
        censored = sum(bool(r['censored']) for r in sub)
        evaluable = len(sub) - censored
        out[arm] = {'scheduled': sched, 'attempted': len(sub), 'unstarted': sched - len(sub),
                    'V1': {'correct': correct, 'incorrect': evaluable - correct, 'censored': censored,
                           'unstarted': sched - len(sub)},
                    'V2': {'passes': correct, 'evaluable': evaluable},
                    'V3': {'passes': correct, 'denominator': len(sub)}}
    return out


def pairs(rows):
    by = {}
    for r in rows:
        by.setdefault(r['case'], {})[r['arm']] = r
    return {c: p for c, p in by.items() if set(p) == {'primitives', 'macro'}}


def matched(rows):
    return [p for p in pairs(rows).values() if not p['primitives']['ambiguous']
            and p['primitives']['passed'] and p['macro']['passed']
            and not p['primitives']['censored'] and not p['macro']['censored']]


def discordant(rows, v3=False):
    b = c = 0
    for p in pairs(rows).values():
        if p['primitives']['ambiguous']:
            continue
        if not v3 and (p['primitives']['censored'] or p['macro']['censored']):
            continue
        ok = {a: bool(p[a]['passed']) and not p[a]['censored'] for a in p}
        b += ok['primitives'] and not ok['macro']
        c += ok['macro'] and not ok['primitives']
    return {'primitives_only': b, 'macro_only': c, 'exact_binomial_p_two_sided': binom_two_sided(b, c)}


def reduction(ps):
    cp = sum(p['primitives']['calls'] for p in ps)
    cm = sum(p['macro']['calls'] for p in ps)
    return None if cp == 0 else 1 - cm / cp


def native_ratio(ps):
    n = sum(p['primitives']['native'] for p in ps)
    return None if n == 0 else sum(p['macro']['native'] for p in ps) / n


def cost(rows):
    keys = ('calls', 'decision_calls', 'input_tokens', 'output_tokens', 'native', 'seconds')
    return {k: round(sum(r[k] for r in rows), 3) for k in keys} | {
        'trials': len(rows), 'usage_incomplete_trials': sum(not r['usage_complete'] for r in rows)}


def bootstrap(rows):
    known = [r for r in rows if not r['ambiguous']]
    groups = sorted({r['group'] for r in known})
    if not groups:
        return None
    by_group = {g: [r for r in known if r['group'] == g] for g in groups}
    rng = random.Random(SEED)
    diff, red, nat, no_pairs = [], [], [], 0
    for _ in range(DRAWS):
        sample = [r for g in (rng.choice(groups) for _ in groups) for r in by_group[g]]
        ev = {a: [r for r in sample if r['arm'] == a and not r['censored']] for a in ('primitives', 'macro')}
        diff.append(sum(r['passed'] for r in ev['macro']) - sum(r['passed'] for r in ev['primitives']))
        # pairs inside a draw: duplicate groups duplicate their pairs
        ps = []
        for g in {r['group'] for r in sample}:
            mult = sum(1 for r in sample if r['group'] == g) // max(1, len(by_group[g]))
            ps += matched(by_group[g]) * mult
        if ps:
            x, y = reduction(ps), native_ratio(ps)
            if x is not None:
                red.append(x)
            if y is not None:
                nat.append(y)
        else:
            no_pairs += 1

    def ci(v):
        if not v:
            return None
        v = sorted(v)
        return [round(v[int(.025 * (len(v) - 1))], 4), round(v[int(.975 * (len(v) - 1))], 4)]
    return {'groups': len(groups), 'draws': DRAWS, 'seed': SEED, 'pass_difference_macro_minus_primitives_95': ci(diff),
            'call_reduction_95': ci(red), 'native_ratio_95': ci(nat), 'draws_without_matched_pairs': no_pairs}


def structure(rows):
    out = {}
    for r in rows:
        if r['ambiguous'] or not r['passed']:
            continue
        out.setdefault(r['family'], {}).setdefault(r['arm'], []).append(r['decision_calls'])
    return {f: {a: sorted(v)[len(v) // 2] for a, v in arms.items()} for f, arms in out.items()}


def predictions(model, rows, scheduled_total, heldout):
    ms = matched(rows)
    n_censored = sum(bool(r['censored']) for r in rows)
    compromised = heldout and n_censored >= 5
    v = views(rows, {})
    res = {}
    r1 = reduction(ms)
    res['D-P1'] = {'matched_pairs': len(ms), 'R': None if r1 is None else round(r1, 4),
                   'status': 'Uninformative' if len(ms) < 5 or r1 is None else
                   'Support' if r1 >= .30 else 'Against' if r1 < .15 else 'Partial'}
    nm, np_ = sum(p['macro']['native'] for p in ms), sum(p['primitives']['native'] for p in ms)
    res['D-P2'] = {'native_macro': nm, 'native_primitives': np_,
                   'status': 'Uninformative' if len(ms) < 5 else 'Support' if nm >= np_ else 'Against'}
    def p3(view):
        pm, pp = v['macro'][view]['passes'], v['primitives'][view]['passes']
        return 'Support' if pm >= pp - 2 else 'Against'
    s2, s3 = p3('V2'), p3('V3')
    res['D-P3'] = {'V2': {a: v[a]['V2'] for a in v}, 'V3': {a: v[a]['V3'] for a in v},
                   'status': 'Uninformative' if s2 != s3 else s2}
    if model == 'qwen':
        failed = [r for r in rows if not r['censored'] and r['passed'] is False]
        pending = [r for r in rows if r['ambiguous'] and r['passed'] is None]
        insp = [r for r in failed if r['selected_skill'] == 'ur5e.inspect_readiness'
                and r['expected_skill'] != 'ur5e.inspect_readiness']
        share = len(insp) / len(failed) if failed else None
        res['D-P4'] = {'failed': len(failed), 'inspection_first': len(insp), 'share': share,
                       'pending_ambiguous': len(pending), 'preliminary': bool(pending),
                       'status': 'Uninformative' if len(failed) < 4 else
                       'Support' if share >= .5 and len(insp) >= 3 else 'Against'}
    if compromised:
        for k in res:
            res[k]['status'] = 'Uninformative'
            res[k]['reason'] = f'operationally compromised: {n_censored} censored'
    return res


def analyze(stage, runs, reviews_path=None):
    cases = load_cases()
    reviews = json.loads(Path(reviews_path).read_text()) if reviews_path else {}
    schedule = json.loads((D / 'schedule' / f'{stage}.json').read_text())['rows']
    rows = [enrich(r, cases, reviews) for r in load_rows(Path(runs) / stage)]
    present = sorted({r['model'] for r in rows}, key=MODELS.index)
    out = {'stage': stage, 'heldout': stage == 'heldout', 'models': {}, 'model_requests': 0,
           'note': 'descriptive; per model; never pooled across models'}
    for m in present:
        mr = [r for r in rows if r['model'] == m]
        sched = {a: sum(1 for s in schedule if s['model'] == m and s['arm'] == a and not cases[s['case']]['kind'] == 'clarification')
                 for a in ('primitives', 'macro')}
        by_type = {}
        for key in ('d_type', 'family'):
            by_type[key] = {}
            for t in sorted({r[key] for r in mr}):
                sub = [r for r in mr if r[key] == t]
                by_type[key][t] = {a: {'passes': sum(bool(r['passed']) for r in sub if r['arm'] == a and not r['censored']),
                                       'trials': sum(r['arm'] == a for r in sub),
                                       'pending': sum(r['passed'] is None for r in sub if r['arm'] == a)}
                                   for a in ('primitives', 'macro')}
        sel = {a: {'selection_correct': sum(r['selection'] for r in mr if r['arm'] == a and not r['ambiguous']),
                   'execution_correct_given_selection': sum(r['execution'] for r in mr if r['arm'] == a and not r['ambiguous'] and r['selection']),
                   'selection_denominator': sum(r['arm'] == a and not r['ambiguous'] for r in mr)} for a in ('primitives', 'macro')}
        ms = matched(mr)
        out['models'][m] = {
            'trials': len(mr), 'censored': sum(bool(r['censored']) for r in mr),
            'views_known_goal': views(mr, sched), 'discordant_V2': discordant(mr), 'discordant_V3': discordant(mr, v3=True),
            'by_type': by_type, 'selection_execution': sel,
            'ambiguous': [{'trial': r['trial'], 'arm': r['arm'], 'automated_pass': r['automated_pass'],
                           'human': r['review'], 'status': 'PENDING' if r['passed'] is None else r['passed']}
                          for r in mr if r['ambiguous']],
            'costs_all_attempts': {a: cost([r for r in mr if r['arm'] == a]) for a in ('primitives', 'macro')},
            'costs_matched_success': {a: cost([p[a] for p in ms]) for a in ('primitives', 'macro')} | {'pairs': len(ms)},
            'turn_structure_median_decision_calls': structure(mr),
            'offload_vram_fraction': sorted({f for r in mr for f in (r['offload'] or [])}),
            'bootstrap': bootstrap(mr),
            'predictions': predictions(m, mr, len(mr), stage == 'heldout')}
    return out


def to_markdown(a):
    md = [f"# Gazebo D analysis: {a['stage']}", '', 'Descriptive, per model, never pooled. Zero model requests.', '',
          '| Model | Arm | Known-goal V2 | V3 | Censored | Calls (all) | Native (all) | Matched pairs | R | D-P1 | D-P2 | D-P3 |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|']
    for m, x in a['models'].items():
        p = x['predictions']
        for arm in ('primitives', 'macro'):
            v = x['views_known_goal'][arm]
            c = x['costs_all_attempts'][arm]
            md.append(f"| {m} | {arm} | {v['V2']['passes']}/{v['V2']['evaluable']} | {v['V3']['passes']}/{v['V3']['denominator']} | "
                      f"{v['V1']['censored']} | {c['calls']} | {c['native']} | {x['costs_matched_success']['pairs']} | "
                      f"{p['D-P1']['R']} | {p['D-P1']['status']} | {p['D-P2']['status']} | {p['D-P3']['status']} |")
    for m, x in a['models'].items():
        d = x['discordant_V2']
        md += ['', f"**{m}:** discordant P-only {d['primitives_only']}, M-only {d['macro_only']}, exact p "
               f"{d['exact_binomial_p_two_sided']}. Bootstrap: {x['bootstrap']}."]
        if 'D-P4' in x['predictions']:
            md.append(f"D-P4 (Qwen inspection-first): {x['predictions']['D-P4']}")
        pend = sum(1 for z in x['ambiguous'] if z['status'] == 'PENDING')
        if pend:
            md.append(f'{pend} ambiguous transcript(s) PENDING human rating: PRELIMINARY.')
    return '\n'.join(md) + '\n'


def d1_gate(runs):
    """D1 auto-freeze criteria (D0 §9). Writes runs/dev/D1_GATE.json."""
    dev = Path(runs) / 'dev'
    status = json.loads((dev / 'status.json').read_text())
    ctrl = json.loads((Path(runs) / 'controls' / 'status.json').read_text())
    reasons = []
    if ctrl.get('status') != 'COMPLETE' or len(ctrl['trials']) != 52 or not all(t['primary_pass'] for t in ctrl['trials']):
        reasons.append('controls_not_52_of_52')
    if status.get('status') != 'COMPLETE':
        reasons.append('dev_stage_status_' + str(status.get('status')))
    if status.get('cleanup_errors') or (status.get('simulator_cleanup') or {}).get('returncode') not in (0, None):
        reasons.append('cleanup_errors')
    if not all(c['pass'] for c in status.get('reset_checks', [])):
        reasons.append('reset_check_failed')
    if status.get('interrupted_not_rerun'):
        reasons.append('interrupted_trials')
    try:
        a = analyze('dev', runs)
        engine_ok = bool(a['models'])
    except Exception as error:
        engine_ok, a = False, None
        reasons.append('analysis_engine_error_' + type(error).__name__)
    if not engine_ok:
        reasons.append('analysis_engine_no_rows')
    result = {'pass': not reasons, 'reasons': reasons, 'trials': len(status.get('trials', [])),
              'censored_by_model': {m: x['censored'] for m, x in (a or {'models': {}})['models'].items()}}
    (dev / 'D1_GATE.json').write_text(json.dumps(result, indent=1) + '\n')
    print('D1 GATE', 'PASS' if result['pass'] else 'FAIL', reasons)
    return result


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('analyze', 'd1-gate'))
    p.add_argument('stage', nargs='?')
    p.add_argument('--runs', default=str(D / 'runs'))
    p.add_argument('--out')
    p.add_argument('--reviews')
    args = p.parse_args(argv)
    if args.action == 'd1-gate':
        return d1_gate(args.runs)
    a = analyze(args.stage, args.runs, args.reviews)
    out = Path(args.out or Path(args.runs) / args.stage / 'analysis')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'analysis.json').write_text(json.dumps(a, indent=1, sort_keys=True) + '\n')
    (out / 'ANALYSIS.md').write_text(to_markdown(a))
    print(to_markdown(a))
    return a


if __name__ == '__main__':
    main(sys.argv[1:])
