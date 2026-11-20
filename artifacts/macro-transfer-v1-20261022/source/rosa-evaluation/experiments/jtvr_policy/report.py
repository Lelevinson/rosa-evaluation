"""Post-run analysis of frozen policy evidence; never edits the policy artifacts."""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil
import statistics

from .audit import check, check_real
from .campaign import DEFAULT, ROOT, assert_frozen, json_write


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def matched(rows, left='jtvr', right='batching'):
    lookup = {(r['fixture_id'], r['policy']): r for r in rows}
    return [(row, lookup[(row['fixture_id'], right)]) for row in rows if row['policy'] == left]


def comparison(rows, left='jtvr', right='batching'):
    pairs = matched(rows, left, right)
    groups = defaultdict(list)
    wins = ties = losses = sequences = 0
    for a, b in pairs:
        groups[a['template']].append((a['modeled_cost'], b['modeled_cost']))
        delta = b['modeled_cost'] - a['modeled_cost']
        wins += delta > 1e-8
        ties += abs(delta) <= 1e-8
        losses += delta < -1e-8
        sequences += a['acquisition_sequence'] == b['acquisition_sequence']
    def gain(values):
        denominator = sum(b for a, b in values)
        return 1 - sum(a for a, b in values) / denominator if denominator else 0.0
    clustered = []
    rng, keys = random.Random(20261021), sorted(groups)
    for _ in range(2000):
        draw = [v for k in rng.choices(keys, k=len(keys)) for v in groups[k]]
        clustered.append(gain(draw))
    clustered.sort()
    return {'left': left, 'right': right, 'pairs': len(pairs), 'wins': wins, 'ties': ties,
        'losses': losses, 'identical_sequences': sequences,
        'relative_complete_cost_reduction': gain([v for values in groups.values() for v in values]),
        'descriptive_cluster_interval_95': [clustered[49], clustered[1949]],
        'left_passed': sum(a['verified_contract_pass'] for a, b in pairs),
        'right_passed': sum(b['verified_contract_pass'] for a, b in pairs)}


def totals(rows):
    return {'episodes': len(rows), 'contract_passed': sum(r['verified_contract_pass'] for r in rows),
        **{metric: sum(r[metric] for r in rows) for metric in (
            'modeled_cost', 'acquisition_cost', 'tool_wrappers', 'cli_commands',
            'modeled_server_rpcs', 'policy_decisions', 'selector_seconds', 'parser_seconds')},
        'acquisition_executions': sum(len(r['acquisition_sequence']) for r in rows)}


def main():
    destination = DEFAULT
    frozen = assert_frozen(destination)
    rows = lines(destination / 'policy-episodes.jsonl')
    fixtures = {s['id']: s for s in json.loads((destination / 'fixtures.json').read_text())}
    audits = [check(row, fixtures[row['fixture_id']]) for row in rows]
    if len(rows) != frozen['total_policy_episodes'] or not all(a['passed'] for a in audits):
        raise RuntimeError('incomplete_or_failed_policy_audit')
    profiles, pairs = {}, {}
    for profile in ('calibrated', 'unit_cost', 'prior_type_allowed'):
        subset = [r for r in rows if r['profile'] == profile and r['depth'] == 2 and not r['role_separated']]
        profiles[profile] = {p: totals([r for r in subset if r['policy'] == p])
                             for p in ('greedy', 'batching', 'jtvr')}
        pairs[profile] = comparison(subset)
    primary = [r for r in rows if r['profile'] == 'calibrated' and r['depth'] == 2 and not r['role_separated']]
    opportunity = comparison([r for r in primary if r['opportunity']])
    jg = comparison(primary, right='greedy')
    ablations = {}
    lookup = {(r['fixture_id'], r['policy'], r['profile'], r['depth'], r['role_separated']): r for r in rows}
    for name, p, d, separated in (('jtvr_depth_one', 'jtvr', 1, False),
        ('batching_role_separated', 'batching', 2, True), ('jtvr_role_separated', 'jtvr', 2, True)):
        variant = [r for r in rows if r['profile'] == 'calibrated' and r['policy'] == p
                   and r['depth'] == d and r['role_separated'] == separated]
        ablations[name] = {'episodes': len(variant), 'passed': sum(r['verified_contract_pass'] for r in variant),
            'cost_ties_with_primary': sum(abs(r['modeled_cost'] - lookup[(r['fixture_id'], p, 'calibrated', 2, False)]['modeled_cost']) < 1e-8 for r in variant),
            'complete_cost': sum(r['modeled_cost'] for r in variant),
            'primary_complete_cost': sum(lookup[(r['fixture_id'], p, 'calibrated', 2, False)]['modeled_cost'] for r in variant)}
    real_path = destination / 'ros-comparison'
    real = lines(real_path / 'episodes.jsonl')
    real_captures = lines(real_path / 'captures.jsonl')
    native = json.loads((real_path / 'native-commands.json').read_text())
    real_audits = check_real(real, real_captures, native)
    if len(real) != 15 or not all(a['passed'] for a in real_audits):
        raise RuntimeError('real_comparison_incomplete_or_audit_failed')
    json_write(destination / 'real-audit.json', {'episodes': len(real_audits),
        'passed': sum(a['passed'] for a in real_audits), 'records': real_audits})
    criterion = (opportunity['left_passed'] >= opportunity['right_passed']
        and opportunity['relative_complete_cost_reduction'] >= 0.10
        and opportunity['descriptive_cluster_interval_95'][0] > 0)
    summary = {'analyzed_utc': datetime.now(timezone.utc).isoformat(), 'policy_episodes': len(rows),
        'policy_audit_passed': sum(a['passed'] for a in audits), 'profiles': profiles,
        'jtvr_vs_batching': pairs, 'opportunity_subset': opportunity, 'jtvr_vs_greedy': jg,
        'ablations': ablations, 'real_episodes': len(real),
        'real_contract_passed': sum(r['verified_contract_pass'] for r in real),
        'real_audit_passed': sum(a['passed'] for a in real_audits),
        'proceed_to_full_runnable_criterion_met': criterion, 'model_requests': 0,
        'full_stage4_complete': False}
    json_write(destination / 'analysis.json', summary)
    old_freeze = json.loads((ROOT.parent / 'reports/phase4-v2/freeze.json').read_text())
    changed = [name for name, wanted in old_freeze['source_sha256'].items()
               if hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest() != wanted]
    baseline_hash = hashlib.sha256((ROOT.parent / 'reports/ROSA_STAGE1_TO_4_CLEAN_RERUN_2026-10-21.zip').read_bytes()).hexdigest()
    if changed or baseline_hash != '721d5960d82f49ea4b0c6f6470ad2c2b02e4e4379720f4b6936a67f13cd3fcad':
        raise RuntimeError('historical_evidence_changed:' + repr(changed))
    json_write(destination / 'preservation-check.json', {
        'baseline_v1_archive_sha256': baseline_hash, 'original_v2_frozen_source_files': len(old_freeze['source_sha256']),
        'changed_original_v2_sources': changed, 'new_policy_sources_also_match_new_freeze': True})
    output = [
        '# Stage 4 three-algorithm comparison: results and recap', '',
        'Date: 2026-10-21. This report completes the frozen policy-only comparison and',
        'the small real ROS validation. It does not complete the separate V2 live',
        'reliability work or establish end-to-end manifest quality. Baseline v1 is unchanged.', '',
        '## Verdict', '',
        ('The predefined criterion for full JTVR model integration was met in this bounded suite.' if criterion else
         'The predefined criterion for full JTVR model integration was not met. Do not build the full custom Runnable or launch the larger model JTVR study on these results alone.'), '',
        f"JTVR versus batching: {pairs['calibrated']['wins']} lower-cost, {pairs['calibrated']['ties']} cost-tied, {pairs['calibrated']['losses']} higher-cost paired fixtures out of 96. Identical acquisition sequences: {pairs['calibrated']['identical_sequences']}/96.", '',
        f"On the 30-fixture predefined opportunity subset, complete modeled-cost reduction versus batching was {opportunity['relative_complete_cost_reduction']:.2%}; the 95% template-cluster descriptive interval was [{opportunity['descriptive_cluster_interval_95'][0]:.2%}, {opportunity['descriptive_cluster_interval_95'][1]:.2%}]. The required threshold was at least 10% with a positive lower bound.", '',
        'These are operation-cost simulations using fixed development timing weights,',
        'not measured end-to-end ROS/model speed. Selector CPU and parser time are',
        'reported separately and cannot turn equal acquisition work into a benefit.', '',
        '## What ran', '',
        f'- {len(rows)} persisted policy episodes; {sum(a["passed"] for a in audits)} passed the separate read-back audit.',
        f'- 288 primary episodes: 96 fixtures each for greedy, amortized batching and JTVR.',
        '- 576 sensitivity episodes: unit-cost and prior-service-type profiles.',
        '- 96 depth-one JTVR episodes and 192 role-separated-with-shared-reuse episodes.',
        f'- {len(real)} real ROS episodes across five templates and all three policies; {sum(r["verified_contract_pass"] for r in real)} contract passes and {sum(a["passed"] for a in real_audits)} separate server-value audit passes.',
        '- Zero model requests. No OAuth sign-in or tokens used. No robot motion or Gazebo arm.',
        '- 39 validation tests passed: 22 new policy/evidence/audit tests plus 17 existing Phase 4 tests.', '',
        'The full protocol, bounds and stop rule were frozen before the evaluation run:',
        '[protocol](../../docs/STAGE4_POLICY_PROTOCOL_2026-10-21.md), [freeze](freeze.json),',
        '[fixtures](fixtures.json), [machine-readable analysis](analysis.json).', '',
        '## Primary results', '',
        '| Policy | Contract passes | Complete modeled cost | Acquisition cost | Acquisition executions | All CLI commands | Modeled parameter RPCs | Selector CPU ms |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p, v in profiles['calibrated'].items():
        output.append(f"| {p} | {v['contract_passed']}/{v['episodes']} | {v['modeled_cost']:.4f} | {v['acquisition_cost']:.4f} | {v['acquisition_executions']} | {v['cli_commands']} | {v['modeled_server_rpcs']} | {v['selector_seconds'] * 1000:.3f} |")
    output += ['', 'Complete costs include common bootstrap, charged metadata warm-up, controlled',
        'writes and all acquisition attempts. Acquisition costs exclude those common',
        'setup/write phases. Simulated RPC counts are modeled from the captured',
        'contracts; real server-counted RPCs appear in the real-validation table.', '',
        f"JTVR complete modeled-cost reduction versus greedy: {jg['relative_complete_cost_reduction']:.2%}. This alone does not establish a contribution beyond batching.", '',
        f"Against greedy, JTVR won {jg['wins']}, tied {jg['ties']} and lost {jg['losses']} fixtures. The 15 losses are 10 wrong-type and five partial-output cases: exploration can waste work when its nominal output assumptions fail. All eventually resolved their requirements; these are cost losses rather than unreported task failures.", '',
        '### Results by task template', '',
        '| Template, 12 fixtures each | Greedy mean complete cost | Batching mean | JTVR mean | J/B cost ties |',
        '| --- | ---: | ---: | ---: | ---: |']
    for template in dict.fromkeys(r['template'] for r in primary):
        group = [r for r in primary if r['template'] == template]
        means = {p: statistics.mean(r['modeled_cost'] for r in group if r['policy'] == p) for p in ('greedy', 'batching', 'jtvr')}
        output.append(f"| {template} | {means['greedy']:.4f} | {means['batching']:.4f} | {means['jtvr']:.4f} | {comparison(group)['ties']}/12 |")
    output += ['', '## Sensitivity and ablations', '',
        '| Profile | J/B lower / tied / higher cost | Identical sequences | J/B total cost reduction |',
        '| --- | ---: | ---: | ---: |']
    for profile, v in pairs.items():
        output.append(f"| {profile} | {v['wins']} / {v['ties']} / {v['losses']} | {v['identical_sequences']}/96 | {v['relative_complete_cost_reduction']:.2%} |")
    output += ['', '| Ablation | Contract passes | Cost ties with own primary arm | Ablation / primary total cost |',
        '| --- | ---: | ---: | ---: |']
    for name, v in ablations.items():
        output.append(f"| {name} | {v['passed']}/{v['episodes']} | {v['cost_ties_with_primary']}/{v['episodes']} | {v['complete_cost']:.4f} / {v['primary_complete_cost']:.4f} |")
    output += ['', 'The role-separated arms keep the same evidence ledger. Reuse is not removed',
        'to manufacture an advantage for joint obligations. A depth-one prefix still',
        'has a greedy completion estimate; a tie with depth two is plausible.', '',
        'The two J/B losses under prior-type access are the wrong-type node-summary',
        'cases. J retains an equal-estimated-cost greedy plan that attempts bulk first;',
        'B reads the already-required node summary first, discovers the actual wrong',
        'type, and avoids that failed bulk attempt. J wastes one bulk invocation in',
        'each case. This is a concrete limit of nominal-cost selection and the tie',
        'rule, not a reason to retune against these frozen cases.', '',
        'Joint versus role-separated acquisition saves work in nine cases for BOTH',
        'B and J. The mixed-role request can batch verification-only fields alongside',
        'the task field before the phase boundary. The same shared cache is retained',
        'in the separated arm; this is a scheduling/batching benefit available to B,',
        'not evidence of an exclusive JTVR lookahead contribution.', '',
        '## Was the selection problem genuinely difficult?', '',
        'The tested catalogue provides genuine cold discovery, full versus partial bulk',
        'reads, shared node-summary/type acquisition, per-node scope, changing cost',
        'estimates and mixed parameter/topic obligations. Targeted tests also change',
        'the requirements and require replanning. Node information is never credited',
        'with parameter values or topic QoS. Thus this is broader than triplet queries.', '',
        'It is nevertheless a small, mostly separable catalogue: compatible parameter',
        'batches are per node, there are only two discovery providers, and topic details',
        'have a separate provider. The amortized baseline explicitly credits every',
        'such overlap and setup cost. There is no demonstrated hard cross-group',
        'selection problem here. This is the central limitation of the current',
        'research opportunity, not evidence that more artificial tools should be added.', '',
        'The two seeds vary values and partial-output shape, not task semantics.',
        'Several warm conditions repeat an already-warm state; ambiguous-write faults',
        'are inert on read-only tasks. Treat eight templates, not 96 independent',
        'families, as the diversity unit. The suite is not independently authored or',
        'blinded. No global theorem about every ROSA request follows from these runs.', '',
        '## Real ROS validation', '',
        'These episodes used the existing ROSA wrapper implementations with a common',
        'bounded argv subprocess helper on isolated ROS Jazzy nodes. Real parameter',
        'callbacks recorded values separately from CLI parsing. Server counts exclude',
        'DDS discovery. One episode per template/policy is a smoke check; wall times',
        'include startup/scheduling noise and do not support a model speed claim.', '',
        '| Policy | Passes | Wrapper / CLI executions | Server RPCs | Actual summed CLI wall time, s |',
        '| --- | ---: | ---: | ---: | ---: |']
    for policy in ('greedy', 'batching', 'jtvr'):
        subset = [r for r in real if r['policy'] == policy]
        output.append(f"| {policy} | {sum(r['verified_contract_pass'] for r in subset)}/{len(subset)} | {sum(r['tool_wrappers'] for r in subset)} / {sum(r['cli_commands'] for r in subset)} | {sum(r['server_rpcs'] for r in subset)} | {sum(r['actual_cli_wall_seconds'] for r in subset):.3f} |")
    output += ['', 'See [real raw episodes](ros-comparison/episodes.jsonl),',
        '[real native commands and RPC values](ros-comparison/native-commands.json),',
        '[real audit](real-audit.json), and [cleanup status](ros-comparison/status.json).', '',
        'B and J performed the same amount of native work. The observed difference',
        'in wall time across single repetitions is not a demonstrated JTVR selection',
        'speedup; scheduling, CLI discovery and warm-up can dominate such samples.', '',
        'Development calibration used two samples per tool. Its probe was developed',
        'before the evaluation freeze; callback value logging was added for the later',
        'real comparison. The retained development captures are the frozen cost input.',
        'They are too small to characterize latency distributions or transfer to a',
        'different graph, host load or robot. Real injected-fault campaigns have not run.', '',
        '## Manifest and model dependency', '',
        'All policies received the same annotated required fields, roles, targets and',
        'phases. They did not receive hidden current values, failure labels or optimal',
        'actions. Strict validation tests reject omitted fields/roles, altered targets',
        'and expanded scope. This validates a supported structured contract, not',
        'general natural-language interpretation. Neither Qwen nor the hosted model',
        'generated manifests in this experiment. Their end-to-end omission rates and',
        'fallback behavior remain unknown. Zero inference savings are claimed.', '',
        '## Original JTVR implementation scope', '',
        'Implemented in this isolated experiment: joint deduplicated obligations,',
        'provenance/epoch/phase-qualified evidence, conservative write barriers,',
        'scoped CLI parsers, shared actual-result-checked two-read fragments,',
        'greedy/reference cost completion, strong per-node amortized grouping, and',
        'bounded JTVR prefix-plus-residual selection with a switching margin.', '',
        'Not implemented: model root approval, same-inference manifest extraction,',
        'production custom Runnable/formatter, native history integration, dynamic',
        'ROSA tool menus, automatic writes or recovery, and asynchronous continuations.',
        'The real check drives unchanged wrappers directly, not AgentExecutor.', '',
        '## Reliability, Baseline v1 and remaining stages', '',
        'Baseline v1 still contains 540 scripted controls plus 120 live trials.',
        'Original hosted/local baseline handling scores remain 30/36 and 24/36.',
        'Additional retrospective strict scores remain 30/36 and 12/36. The local',
        'drop exposed report-argument and prerequisite-attempt problems; it is not',
        'a new model run or a changed 18/18 achievable-goal result.', '',
        'The prior V2 hosted batch stopped before consent with zero model requests.',
        'Its failed-supervisor status was an intentional scope-change cancellation.',
        'V2 live reliability interventions have not now been run. This policy study',
        'does not replace that comparison or establish safer model behavior.', '',
        '| Stage | Status after this study |',
        '| --- | --- |',
        '| 1, shared ROSA backends | Previously demonstrated in mock tools. |',
        '| 2, contract/scoring | Working foundation; new scoped evidence contracts tested. |',
        '| 3, baselines/reliability | V1 preserved; prospective isolated interventions pending. |',
        '| 4, acquisition/caching | Policy tier and real smoke complete; full integration decision recorded above; separate reliability work incomplete. |',
        '| 5, verified episodic memory | Not started; requires history-dependent cases and matched controls. |',
        '| 6, Gazebo arm/hardware | Base simulator installed; arm, controllers, skills and platform contract pending. |', '',
        'The user requested a final results commit on `member/martin` after the newly',
        'tested Stage 4 is complete. That full-stage condition is not met. No final',
        'Stage 4 completion commit is claimed by this report. Evidence for this tier',
        'already resides inside the experiments repository for explicit later staging.', '',
        '## Recommended next decision', '',
        ('Review the opportunity and manifest limits before considering full model integration.' if criterion else
         'Use amortized batching as the current selection reference and pause full JTVR integration in this catalogue. Finish the separately controlled reliability/manifest questions before spending on a large end-to-end study. Revisit lookahead only if an actual supported workflow introduces a grounded decision that B cannot already handle as efficiently.'), '',
        'For ChatGPT review: assess whether the registered real catalogue contains a',
        'missing legitimate overlap or prerequisite pattern, whether the strong B',
        'definition is fair, and whether the negative/tied outcome warrants simplifying',
        'the project. Do not infer value merely from the sophistication of the design.', '',
        '## Reproduction and evidence integrity', '',
        'From the prepared WSL research environment in the evaluation checkout:', '',
        '```bash',
        'python -B -m experiments.jtvr_policy.campaign verify',
        'python -B -m experiments.jtvr_policy.report',
        '```', '',
        'The original prepare/run actions refuse overwrite. A modified protocol needs',
        'a separately named campaign rather than overwriting this evidence. The',
        'source snapshot and input hashes are in `freeze.json` and `source/`.',
        'The analysis module was added after freezing selection code; it performs',
        'read-only analysis and is recorded in the final evidence manifest.', '',
        'One Windows launch misclassified unittest stderr as a native-command error',
        'despite 39 tests reporting OK. Its original log is preserved. A clean',
        'Python test runner repeated the same 39 tests with explicit exit code zero;',
        'both logs remain. No failed model trials are hidden in this correction.', '',
        'The original Baseline v1 archive hash and every previously frozen V2 source',
        'file were checked unchanged in [preservation-check.json](preservation-check.json).',
        'The detailed pre-policy history remains in',
        '[the earlier checkpoint](../../docs/RECAP_FOR_CHATGPT_2026-10-21.md).', '',
        'Local-only report links may not work in a bare ChatGPT attachment. Supply',
        'this Markdown with the evidence archive if raw inspection is needed.']
    (destination / 'REPORT_FOR_CHATGPT.md').write_text('\n'.join(output) + '\n')
    analysis_source = destination / 'analysis-source'
    analysis_source.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), analysis_source / 'report.py')
    hashes = {}
    for path in sorted(destination.rglob('*')):
        if path.is_file() and path.name != 'evidence-manifest.json':
            hashes[str(path.relative_to(destination))] = hashlib.sha256(path.read_bytes()).hexdigest()
    json_write(destination / 'evidence-manifest.json', hashes)
    print(json.dumps({'report': str(destination / 'REPORT_FOR_CHATGPT.md'),
        'policy_episodes': len(rows), 'real_episodes': len(real), 'criterion_met': criterion}))


if __name__ == '__main__':
    main()
