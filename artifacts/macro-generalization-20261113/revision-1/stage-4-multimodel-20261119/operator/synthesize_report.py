"""Lab-only descriptive synthesis after execution; no formal verdict or inference."""
from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT.parent
REPO = REV.parents[2]
MODES = ['primitives', 'macro']


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sys.platform == 'linux'
    verifier = runpy.run_path(str(ROOT / 'operator/run_sequence.py'))
    assert verifier['verify']()
    data = read(ROOT / 'DESCRIPTIVE_EXTENSION_RESULTS_CORRECTED01.json')
    diag = read(ROOT / 'INTEGRATION_DIAGNOSTICS.json')
    q = read(REV / 'stage-4-qwen-lab-20261119/operator/completed-report/results.json')
    sol = read(REV / 'stage-4/analysis/current.json')
    context = []
    for name, folder, summary, costs in [
        ('Retained Sol', REV / 'stage-4', sol, sol['all_attempt_costs']),
        ('Retained Qwen3.5 9B', REV / 'stage-4-qwen-lab-20261119', q['summary'], q['all_attempt_costs']),
    ]:
        rows = [read(p) for p in (folder / 'trials').glob('*/result.json')]
        outcomes = {o['trial_id']: o['primary_status'] for o in summary['outcomes']}
        groups = {m: dict(collections.Counter(outcomes[r['id']] for r in rows
                  if r['case']['kind'] != 'ambiguous' and r['mode'] == m)) for m in MODES}
        context.append(dict(name=name, known_goal=groups,
                            calls={m: costs[m]['calls'] for m in MODES},
                            mean_seconds={m: costs[m]['task_seconds'] / 38 for m in MODES}))
    lines = ['# G1 exploratory multi-model extension — results and comparison', '',
             'Date: **2026-11-19**. **Exploratory backends, added after Sol and Qwen results.**', '',
             '**228/228 scheduled mock attempts completed.** 701 inference +6 preparation +3 cleanup = **710/1,833 total charged requests**, with separate611-request and eight-hour limits per model. No infrastructure retries, failed-trial replacement, hosted requests, new downloads or Git publication occurred. All228 local and228 persisted Phoenix audits pass.', '',
             '**Execution is complete; human adjudication and formal analysis are not.** Twelve new semantic ratings are required, including structurally failed responses. Seven primary outcomes remain pending. Qwen Batch B has four separate outstanding ratings. No ratings were generated or reused.', '',
             '## Main comparison', '',
             'Known-goal rows exclude the two ambiguous cases per condition. Calls and latency use all38 attempts per arm, including failures. Counts are correct/evaluable. Do not pool backend pass rates.', '',
             '| Backend | Primitives known-goal | Macro known-goal | Calls P → M | Mean task seconds P → M |',
             '|---|---:|---:|---:|---:|']
    for item in context:
        g = item['known_goal']
        rate = {m: str(g[m].get('PASS', 0)) + '/' + str(g[m].get('PASS', 0) + g[m].get('FAIL', 0)) for m in MODES}
        lines.append(f"| {item['name']} | {rate['primitives']} | {rate['macro']} | {item['calls']['primitives']} → {item['calls']['macro']} | {item['mean_seconds']['primitives']:.2f} → {item['mean_seconds']['macro']:.2f} |")
    for slug, item in data['models'].items():
        g = item['groups']['known_goal']; c = item['all_attempt_costs']
        lines.append(f"| {slug} | {g['primitives'].get('PASS', 0)}/36 | {g['macro'].get('PASS', 0)}/36 | {c['primitives']['calls']} → {c['macro']['calls']} | {c['primitives']['mean_seconds']:.2f} → {c['macro']['mean_seconds']:.2f} |")
    lines += ['', 'Sol has three censored primitive attempts and retains its original hosted/laptop-WSL provenance. Qwen retains its old lab container; the extension uses another disclosed installed Jazzy image. These times are contextual per-backend measurements, not a controlled model-speed ranking. Ministral33/36 versus Sol36/36 does not establish parity.', '',
              '## New-model details', '', 'P/M means primitives/macro. Native operations count attempted acquisitions/actions, not only accepted calls. Unknown usage is not zero.']
    for slug, item in data['models'].items():
        c = item['all_attempt_costs']; t = item['timing']; z = diag['models'][slug]
        lines += ['', '### ' + slug, '', str(item['outcomes_per_arm']), '',
                  f"Requests: **{item['inference_requests']} inference +2 preparation +1 cleanup = {item['total_charged']}/611**. Full backend elapsed: {item['campaign_seconds']/60:.2f}min, including auditing/bookkeeping outside measured task time. Paired outcomes over38 pairs: {item['pairs']}.", '',
                  '| Metric | Primitives | Macro |', '|---|---:|---:|']
        for key in ['calls', 'input_tokens', 'output_tokens', 'native_operations', 'task_seconds', 'mean_seconds', 'median_seconds', 'invalid_attempts', 'length_stops', 'budget_endings', 'incomplete_usage']:
            v = [c[m][key] for m in MODES]
            v = [f'{x:.3f}' if isinstance(x, float) else str(x) for x in v]
            lines.append('| ' + key + ' | ' + v[0] + ' | ' + v[1] + ' |')
        lines += ['', f"Recognized native calls: {z['recognized_native_calls']}. Parser-level invalid-tool-call records: {z['invalid_tool_call_records']} (separate from schema/argument validation errors). Native call names: {z['native_call_names']}.", '',
                  f"Aggregate recorded decode rate P/M: {t['primitives']['decode_tokens_per_second']:.2f}/{t['macro']['decode_tokens_per_second']:.2f}tokens/s, in each model's tokenizer units. All six timing-field coverage counts and sums are in the corrected JSON. Cached-token counts were not returned; none are estimated.", '',
                  'Goal/report flags: ' + str(item['goal_reporting_flags']) + '. These are structured accepted-report flags, not a certification of every prose statement or physical safety.']
    lines += ['', '## Conditional successful-pair efficiency', '',
              'Ministral has27 pairs where both conditions passed: calls110 →58 (47.3% fewer), input207,603 →103,276, output12,455 →7,310, native85 →87, task time142.54 →90.47s (36.5% less). Those conditional costs exclude failed/pending pairs and do not replace all-attempt accounting. Its all-attempt call saving is46.1%, while native work rises102 →127. The evidence supports lower LLM orchestration overhead here, not universally lower robot work.', '',
              'Granite and Llama have zero matched successful pairs. A successful-pair efficiency comparison is undefined; shorter failed-task times are not useful task efficiency.', '',
              '## Predefined write-bearing contrast — counts only', '',
              'Six healthy writes plus two frozen write_fault cases form the predefined8-case group; the other known-goal group has28. These are not eight healthy writes.', '',
              '| Backend | Write P /8 | Write M /8 | Other P /28 | Other M /28 |', '|---|---:|---:|---:|---:|',
              '| Qwen, retrospective origin | 2 | 6 | 24 | 24 |']
    for slug, item in data['models'].items():
        g = item['groups']
        assert all(sum(g['write_bearing'][m].values()) == 8 and sum(g['other_known_goal'][m].values()) == 28 for m in MODES)
        lines.append('| ' + slug + ' | ' + ' | '.join(str(g[group][m].get('PASS', 0)) for group in ['write_bearing', 'other_known_goal'] for m in MODES) + ' |')
    lines += ['', 'The observed write-arm floors/ceilings are important: Ministral macro8/8, Granite0/8, Llama primitive0/8. The predefined rule gives those boundaries precedence over a favorable difference. Do not label the positive Ministral pattern H-write Support while ignoring that rule. Formal H-write computation remains withheld under T6 until actual review.', '',
              (ROOT / 'operator/REPORT_INTERPRETATION_NOTES.md').read_text()]
    target = REPO / 'G1_MULTIMODEL_REPORT_2026-11-19.md'
    assert not target.exists()
    target.write_text('\n'.join(lines) + '\n')
    (ROOT / 'RETAINED_BACKEND_COMPARISON_CONTEXT.json').write_text(json.dumps(context, indent=2) + '\n')
    receipt = {'utc': datetime.now(timezone.utc).isoformat(), 'report': target.name,
               'report_sha256': sha(target), 'corrected_results_sha256': sha(ROOT / 'DESCRIPTIVE_EXTENSION_RESULTS_CORRECTED01.json'),
               'integration_diagnostics_sha256': sha(ROOT / 'INTEGRATION_DIAGNOSTICS.json'),
               'source_sha256': sha(Path(__file__)), 'model_requests': 0,
               'scope': 'post-run descriptive synthesis, not frozen formal analysis'}
    (ROOT / 'FINAL_REPORT_SOURCE_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert verifier['verify']()
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
