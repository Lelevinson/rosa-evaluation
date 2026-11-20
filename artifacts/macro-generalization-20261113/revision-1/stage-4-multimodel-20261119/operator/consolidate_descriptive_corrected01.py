"""Post-launch descriptive reporting only; no scorer/prediction/input changes.

Run on the lab after all three batches complete. Human semantics and the frozen
formal analysis remain withheld until actual reviews. No inference requests.
"""
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import hashlib
import json
import runpy
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['ministral', 'granite', 'llama']
MODES = ['primitives', 'macro']
FIELDS = ['total_duration', 'load_duration', 'prompt_eval_count',
          'prompt_eval_duration', 'eval_count', 'eval_duration']


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def costs(rows):
    times = [r['task_seconds'] for r in rows]
    return dict(attempts=len(rows), calls=sum(r['inference']['calls'] for r in rows),
                input_tokens=sum(r['inference']['known_input_tokens'] for r in rows),
                output_tokens=sum(r['inference']['known_output_tokens'] for r in rows),
                incomplete_usage=sum(not r['inference']['usage_complete'] for r in rows),
                native_operations=sum(len(r['actor_records']) for r in rows),
                task_seconds=sum(times), mean_seconds=statistics.mean(times) if times else None,
                median_seconds=statistics.median(times) if times else None,
                invalid_attempts=sum(r['score']['invalid_attempts'] for r in rows),
                length_stops=sum(bool(r['score']['length_stop']) for r in rows),
                budget_endings=sum(bool(r['score']['budget_exhaustion']) for r in rows))


def compare(rows):
    return {m: costs([r for r in rows if r['mode'] == m]) for m in MODES}


def savings(p, m):
    return (p - m) / p * 100 if p else None


def main():
    assert sys.platform == 'linux'
    assert read(ROOT / 'SEQUENCE_STATUS.json')['status'] == 'EXECUTION_COMPLETE_HUMAN_REVIEW_PENDING'
    verification = runpy.run_path(str(ROOT / 'operator/run_sequence.py'))
    assert verification['verify']()
    result = {'label': 'exploratory backend, added after Sol and Qwen results',
              'scope': 'descriptive accounting; no frozen formal predictions computed',
              'cases': 'same 38 AI-authored cases; no independent case-generality claim',
              'model_requests_for_reporting': 0, 'models': {},
              'H_write': 'WITHHELD_UNTIL_ACTUAL_REVIEW_AND_T6_CLOSEOUT',
              'P3': 'DROPPED horizon reliability', 'P4': 'NOT RUN catalogue probe',
              'P1_prime_scope': 'original formal endpoint is Sol-specific',
              'source_sha256': sha(Path(__file__))}
    all_raw = {}
    for slug in ORDER:
        b = ROOT / 'backends' / slug
        desc = read(b / 'DESCRIPTIVE_RESULTS.json')
        state = read(b / 'status.json')
        assert state['status'] == 'COMPLETE' and state['completed'] == 76
        paths = sorted((b / 'trials').glob('*/result.json'))
        rows = [read(p) for p in paths]
        assert len(rows) == len({r['id'] for r in rows}) == 76
        assert {r['id'] for r in rows} == {r['id'] for r in read(b / 'plan.json')}
        for p, row in zip(paths, rows):
            assert row['local_audit']['pass'] and read(p.parent / 'phoenix-audit.json')['pass']
            all_raw[str(p.relative_to(ROOT))] = sha(p)
        outcomes = {o['trial_id']: o for o in desc['summary']['outcomes']}
        pairs = defaultdict(dict)
        for row in rows:
            pairs[row['case']['case_id']][row['mode']] = row
        pairs_ok = {k for k, pair in pairs.items()
                    if all(outcomes[r['id']]['primary_status'] == 'PASS' for r in pair.values())}
        pair_counts = Counter()
        for pair in pairs.values():
            statuses = [outcomes[pair[m]['id']]['primary_status'] for m in MODES]
            if any(s.startswith('INFRA_CENSORED') for s in statuses):
                pair_counts['censored'] += 1
            elif any(s == 'PENDING_HUMAN_REVIEW' for s in statuses):
                pair_counts['pending_human'] += 1
            elif statuses == ['PASS', 'PASS']:
                pair_counts['both_pass'] += 1
            elif statuses[0] == 'PASS':
                pair_counts['primitive_only'] += 1
            elif statuses[1] == 'PASS':
                pair_counts['macro_only'] += 1
            else:
                pair_counts['neither'] += 1
        arm_outcomes = {m: dict(Counter(outcomes[r['id']]['primary_status'] for r in rows if r['mode'] == m)) for m in MODES}
        groups = {}
        for kind, predicate in [('known_goal', lambda r: r['case']['kind'] != 'ambiguous'),
                                ('write_bearing', lambda r: r['case']['kind'] in ['write', 'write_fault']),
                                ('other_known_goal', lambda r: r['case']['kind'] not in ['ambiguous', 'write', 'write_fault'])]:
            groups[kind] = {m: dict(Counter(outcomes[r['id']]['primary_status'] for r in rows if predicate(r) and r['mode'] == m)) for m in MODES}
        assert all(sum(groups['write_bearing'][m].values()) == 8 and sum(groups['other_known_goal'][m].values()) == 28 for m in MODES), 'wrong_frozen_group_denominators'
        family = []
        for key in sorted({(r['case']['domain'], r['case']['kind'], r['case']['native_depth']) for r in rows}):
            subset = [r for r in rows if (r['case']['domain'], r['case']['kind'], r['case']['native_depth']) == key]
            family.append({'domain': key[0], 'kind': key[1], 'depth': key[2], 'outcomes': {
                m: dict(Counter(outcomes[r['id']]['primary_status'] for r in subset if r['mode'] == m)) for m in MODES}, 'costs': compare(subset)})
        timing = {}
        for m in MODES:
            records = [x for r in rows if r['mode'] == m for x in r.get('sanitized_request_records', [])]
            info = [x.get('generation_info') or {} for x in records]
            presence = {f: sum(isinstance(x.get(f), (int, float)) for x in info) for f in FIELDS}
            totals = {f: sum(x[f] for x in info if isinstance(x.get(f), (int, float))) for f in FIELDS}
            timing[m] = {'physical_records': len(records), 'field_presence': presence,
                         'recorded_sums': totals, 'cached_count_presence': sum('prompt_eval_cached_count' in x for x in info),
                         'decode_tokens_per_second': totals['eval_count'] / (totals['eval_duration'] / 1e9) if totals['eval_duration'] else None,
                         'prompt_tokens_per_second': totals['prompt_eval_count'] / (totals['prompt_eval_duration'] / 1e9) if totals['prompt_eval_duration'] else None,
                         'missing_values_estimated': False}
        assert sum(r['inference']['calls'] for r in rows) == state['live_model_requests']
        auxiliary = read(b / 'AUXILIARY_REQUESTS.json')['charged_requests']
        cleanup_path = ROOT / 'operator/live' / slug / 'cleanup.json'
        cleanup = 1 if cleanup_path.exists() and read(cleanup_path).get('reserved_before_dispatch') else 0
        charged = state['charged_total_requests'] + cleanup
        assert state['charged_total_requests'] == state['live_model_requests'] + auxiliary and charged <= 611
        item = {'model': desc['model'], 'outcomes_per_arm': arm_outcomes, 'groups': groups,
                'pairs': dict(pair_counts), 'matched_success_pairs': len(pairs_ok),
                'all_attempt_costs': compare(rows),
                'matched_success_costs': compare([r for r in rows if r['case']['case_id'] in pairs_ok]),
                'per_family': family, 'timing': timing, 'auxiliary_charged': auxiliary,
                'inference_requests': state['live_model_requests'], 'cleanup_charged': cleanup,
                'total_charged': charged, 'infrastructure_retries': state['campaign']['infrastructure_retries'],
                'campaign_seconds': (datetime.fromisoformat(state['completed_utc']) - datetime.fromisoformat(state['started_utc'])).total_seconds(),
                'local_audits': 76, 'persisted_audits': 76,
                'goal_reporting_flags': {f: sum(bool(r['score'].get(f)) for r in rows) for f in ['dispatch_violation', 'unsupported_accepted_success', 'accepted_success_wrong_goal']},
                'fault_cases': [{'trial': r['id'], 'kind': r['case']['kind'], 'fault': r['case'].get('fault'),
                                 'exercised': r['score'].get('fault_exercised'), 'dispatches': r['score'].get('dispatches')}
                                for r in rows if r['case'].get('fault') is not None],
                'formal_analysis': 'WITHHELD_PENDING_REAL_HUMAN_RATINGS'}
        result['models'][slug] = item
    result['raw_result_sha256'] = all_raw
    result['total_charged_requests'] = sum(x['total_charged'] for x in result['models'].values())
    assert result['total_charged_requests'] <= 1833
    (ROOT / 'DESCRIPTIVE_EXTENSION_RESULTS_CORRECTED01.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# G1 additional local models — execution and descriptive results', '',
             'Date: **2026-11-19**. **Exploratory backends, added after Sol and Qwen results.**', '',
             '**228/228 scheduled attempts are retained. Formal analysis and clarification semantics await actual human review.**', '',
             'Same 38 AI-authored mock cases, two architectures, fixed prompts and limits. This is not Gazebo, a physical-robot study, independent case generalization, an intrinsic model ranking or a comparison against unmodified ROSA.', '',
             '| Model | Primitives: known-goal PASS/evaluable | Macro: known-goal PASS/evaluable | All-attempt calls P → M | Mean task seconds P → M | Charged / 611 |',
             '|---|---:|---:|---:|---:|---:|']
    for slug, d in result['models'].items():
        g = d['groups']['known_goal']; c = d['all_attempt_costs']
        rates = {m: str(g[m].get('PASS', 0)) + '/' + str(g[m].get('PASS', 0) + g[m].get('FAIL', 0)) for m in MODES}
        lines.append(f"| {slug} | {rates['primitives']} | {rates['macro']} | {c['primitives']['calls']} → {c['macro']['calls']} | {c['primitives']['mean_seconds']:.2f} → {c['macro']['mean_seconds']:.2f} | {d['total_charged']} |")
    for slug, d in result['models'].items():
        lines += ['', '## ' + slug, '', str(d['outcomes_per_arm']), '',
                  f"Paired outcomes: {d['pairs']}. Matched successful pairs: {d['matched_success_pairs']}. Human-pending and censored pairs are not silently treated as failures or successes.", '',
                  '| Cost | All attempts: primitives | All attempts: macro | Matched success: primitives | Matched success: macro |', '|---|---:|---:|---:|---:|']
        for key in ['attempts','calls','input_tokens','output_tokens','native_operations','task_seconds','mean_seconds','median_seconds','invalid_attempts','length_stops','budget_endings','incomplete_usage']:
            a = d['all_attempt_costs']; c = d['matched_success_costs']
            lines.append(f"| {key} | {a['primitives'][key]} | {a['macro'][key]} | {c['primitives'][key]} | {c['macro'][key]} |")
        a = d['all_attempt_costs']; c = d['matched_success_costs']
        lines += ['', f"All-attempt call reduction: {savings(a['primitives']['calls'], a['macro']['calls']):.1f}%. Conditional matched-success call reduction: {savings(c['primitives']['calls'], c['macro']['calls']) if c['primitives']['calls'] else 'not defined'}%. Conditional costs do not replace the all-attempt ledger.", '',
                  f"Campaign elapsed: {d['campaign_seconds']:.2f}s, including bookkeeping/auditing outside measured task time. Inference {d['inference_requests']} + preparation {d['auxiliary_charged']} + cleanup {d['cleanup_charged']} = {d['total_charged']} charged. Eligible reserve retries: {d['infrastructure_retries']}. All 76 local and 76 persisted audits passed.", '',
                  'Write/partial-write versus other known-goal counts: ' + str({k:v for k,v in d['groups'].items() if k != 'known_goal'}) + '.', '',
                  'Accepted report truth and requested-goal correctness remain separate. Diagnostic flags: ' + str(d['goal_reporting_flags']) + '.', '',
                  'Returned timing coverage and rates: ' + str(d['timing']) + '. Missing values are not estimated. See JSON for per-family costs and whether injected faults actually executed.']
    lines += ['', '## Interpretation and remaining work', '',
              'The complete experiment package includes execution architecture and condition wording; these effects are not isolated. Macros remove routine decision boundaries and may perform more native work. Fewer calls or faster failure alone is not useful efficiency. Use verified correctness, all-attempt accounting and matched-success costs together.', '',
              'The original Sol batch used hosted inference with its original laptop/WSL execution provenance. Qwen and the new backends use the lab; the new container image also differs from the old Qwen image. No direct hardware-matched speed or intrinsic-model superiority claim follows. Sol retained 33/33 versus 36/36 known-goal correctness among evaluable attempts (three primitive infrastructure-censored); Qwen retained 26/36 versus 30/36, with four separate clarification reviews outstanding. These contextual results are not pooled with this extension.', '',
              'A pooled, blinded packet contains only the new models’ four ambiguous responses each. Levinson is nominated; eligibility and ratings must be honestly returned. No assistant ratings, copied prior ratings or human adjudication are supplied. Formal prediction analysis, H-write closeout and final aggregate interpretation remain withheld until required reviews. H-write is descriptive and its raw-count rule may support concentration even when total accuracy worsens; floors/ceilings force Uninformative.', '',
              'P3 is dropped horizon reliability; the P4 catalogue probe was not run. P1′ remains formally Sol-specific. All protected source, frozen inputs, old Sol/Qwen artifacts and backend seals reverified unchanged. No inference requests were made for reporting.']
    (ROOT / 'MULTIMODEL_EXECUTION_REPORT_CORRECTED01.md').write_text('\n'.join(lines) + '\n')
    assert all(sha(ROOT / n) == h for n, h in all_raw.items())
    assert verification['verify']()
    print(json.dumps({'models': len(result['models']), 'retained_attempts': len(all_raw),
                      'total_charged': result['total_charged_requests'], 'reporting_requests': 0,
                      'formal_analysis': 'WITHHELD_PENDING_REAL_HUMAN_RATINGS'}))


if __name__ == '__main__':
    main()
