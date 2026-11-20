"""Post-run descriptive checks; does not alter cases, scores or live execution."""
from collections import defaultdict
from common import ROOT, ORIGINAL, read, write, verify

def main():
    analysis = read(ROOT/'combined-analysis.json')
    rows = [read(p) for folder in (ORIGINAL, ROOT)
            for p in sorted((folder/'trials').glob('*/result.json'))]
    assert len(rows) == len({r['id'] for r in rows})
    assert sum(r['inference']['calls'] for r in rows) == analysis['cumulative_requests']
    assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
    deviations = [{'id': r['id'], 'actual': r['actual_turns'],
                   'expected': r['expected_scripted_turns'], 'error': r.get('error')}
                  for r in rows if not r['turns_match_scripted_expectation']]
    ratios = []
    for domain in ('arm', 'base'):
        for depth in (1, 2, 4, 6):
            group = [r for r in rows if r['case']['kind'] == 'ladder'
                     and r['case']['domain'] == domain and r['case']['native_depth'] == depth]
            totals = {m: sum(len(r['actor_records']) for r in group if r['mode'] == m)
                      for m in ('primitives', 'macro')}
            ratio = totals['macro']/totals['primitives'] if totals['primitives'] else None
            ratios.append(dict(domain=domain, depth=depth, **totals, ratio=ratio,
                               in_band=.75 <= ratio <= 1.25 if ratio is not None else None))
    diagnostics = {key: sum(bool(r['score'].get(key)) for r in rows)
        for key in ('dispatch_violation', 'unsupported_accepted_success',
                    'accepted_success_wrong_goal', 'budget_exhaustion', 'length_stop',
                    'clarification_review_required')}
    fault_rows = [{'id': r['id'], 'fault': r['case']['fault'],
                   'exercised': r['score'].get('fault_exercised'),
                   'dispatches': r['score'].get('dispatches'),
                   'accepted_status': r['score'].get('accepted_status'),
                   'primary_correct': r['primary_pass']}
                  for r in rows if r['case'].get('fault') not in (None, '', 'none')]
    paired = defaultdict(dict)
    for r in rows:
        paired[r['case']['case_id']][r['mode']] = r
    pair_counts = {}
    for domain in ('arm', 'base'):
        counts = dict(both_correct=0, primitive_only=0, macro_only=0, neither=0)
        for pair in paired.values():
            if next(iter(pair.values()))['case']['domain'] != domain or len(pair) != 2:
                continue
            p, m = (pair[key]['primary_pass'] for key in ('primitives', 'macro'))
            counts['both_correct' if p and m else 'primitive_only' if p else
                   'macro_only' if m else 'neither'] += 1
        pair_counts[domain] = counts
    savings = {}
    for view in ('all_attempt_costs', 'matched_success_costs'):
        p, m = (analysis[view][key] for key in ('primitives', 'macro'))
        savings[view] = {key: 100*(1-m[key]/p[key]) if p[key] else None
            for key in ('requests', 'known_input_tokens', 'known_output_tokens',
                        'task_seconds_sum', 'native_attempts')}
    result = dict(turn_expectation_deviations=deviations, native_ratios=ratios,
                  diagnostics=diagnostics, fault_trials=fault_rows, paired_by_domain=pair_counts,
                  descriptive_savings_percent=savings, protected_check=verify(),
                  predictions='NOT_ADJUDICATED_DEV_ONLY', independent_human_review=False)
    write('detailed-checks.json', result)
    lines = ['# Stage 2 detailed execution checks', '', 'Date: **2026-11-14**.', '',
        'This supplements [the combined report](COMBINED_STAGE2_REPORT.md). All figures combine '
        'the sealed original segment and its continuation. The original failed provider attempt '
        'is retained. This is dev validation, not a held-out test or a P1-P4 verdict.', '',
        '## Actual model turns', '',
        f'{len(deviations)} attempt(s) differed from the scripted turn comparator. '
        'The comparator was not forced on the live model.', '',
        '| Trial | Actual calls | Expected calls | Recorded error |', '|---|---:|---:|---|']
    for d in deviations:
        lines.append(f'| {d["id"]} | {d["actual"]} | {d["expected"]} | {d["error"]} |')
    lines += ['', '## Cost views', '',
        '| View | Calls saved | Known input tokens saved | Known output tokens saved | Task time saved | Native attempts saved |',
        '|---|---:|---:|---:|---:|---:|']
    for view, values in savings.items():
        formatted = ['unavailable' if v is None else f'{v:.2f}%' for v in values.values()]
        lines.append('| '+view+' | '+' | '.join(formatted)+' |')
    lines += ['', 'Known token sums omit unknown usage on the interrupted call. The matched-success '
        'view excludes that entire pair. A negative saving means more work. Timing includes local '
        'agent instrumentation and evaluator reads, and excludes subsequent persisted-trace audits. '
        'The long pause and fresh server/session segment limit causal timing interpretations.', '',
        '## Native-acquisition band', '',
        'The predefined band is **0.75-1.25** macro/primitive attempts per domain/depth. '
        'The failed Base depth-6 primitive attempt has no completed acquisition path; '
        'its ratio is undefined and cannot be treated as a measured band violation.', '',
        '| Domain | Depth | Primitive native | Macro native | Ratio | In band |',
        '|---|---:|---:|---:|---:|---|']
    for r in ratios:
        ratio = 'undefined' if r['ratio'] is None else f'{r["ratio"]:.2f}'
        lines.append(f'| {r["domain"]} | {r["depth"]} | {r["primitives"]} | {r["macro"]} | {ratio} | {r["in_band"]} |')
    lines += ['', '## Fault coverage and reporting', '',
        '| Trial | Injected fault | Exercised | Dispatches | Accepted status | Correct |',
        '|---|---|---|---:|---|---|']
    for r in fault_rows:
        lines.append(f'| {r["id"]} | {r["fault"]} | {r["exercised"]} | {r["dispatches"]} | {r["accepted_status"]} | {r["primary_correct"]} |')
    lines += ['', 'Diagnostics: '+', '.join(f'{key}={value}' for key, value in diagnostics.items())+'.', '',
        'Correctness includes appropriate failure/unknown reporting and preliminary clarification; '
        'it does not mean every request caused a successful movement. Clarification transcripts '
        'still lack independent semantic human adjudication. Fault-exercised status follows the '
        'frozen scorer and must not be inferred merely from an expected FAILURE label.', '',
        '## Interpretation and next gate', '',
        'The dev run checks execution paths, accounting, scorers and observability. No prompts, '
        'guards, conditions or cases were tuned from these results. The one permitted scorer '
        'amendment was consumed before live inference. No additional amendment was used.', '',
        'The provider interruption cannot establish an architecture correctness advantage. '
        'The condition-sentence confound and AI-only authorship remain. Stronger claims require '
        'the separately gated held-out study. Do not launch it, a distractor probe or Qwen here. '
        'For later stages P2 remains restricted to Against or Uninformative; Qwen also needs its '
        'reviewed GPU-idle gate.', '',
        'The owner authorized completion of this continuation and future evidence-preserving '
        'recovery from external interruptions. See [the standing instruction]'
        '(STANDING_INTERRUPTION_POLICY_2026-11-14.md). Normal remembered-credential cleanup '
        'retains encrypted sign-in and clears in-memory credentials. No new consent was automated.']
    (ROOT/'DETAILED_STAGE2_CHECKS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print({'diagnostics': diagnostics, 'turn_deviations': len(deviations),
           'paired_by_domain': pair_counts, 'savings': savings})

if __name__ == '__main__':
    main()
