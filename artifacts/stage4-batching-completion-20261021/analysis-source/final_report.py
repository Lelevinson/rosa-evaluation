"""Post-run analysis and evidence packaging; does not change frozen execution."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import random
import shutil
import statistics
import zipfile

from ..config import ROOT
from .runner import CAMPAIGN, PROJECT
from .protocol import verify


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def median(rows, field):
    return statistics.median(r[field] for r in rows) if rows else None


def gain(pairs, metric):
    denominator = sum(b[metric] for a, b in pairs)
    return 1 - sum(a[metric] for a, b in pairs) / denominator if denominator else None


def interval(pairs, metric):
    if not pairs:
        return [None, None]
    groups = defaultdict(list)
    for a, b in pairs:
        groups[a['scenario_id']].append((a, b))
    rng, keys = random.Random(20261021), sorted(groups)
    values = []
    for _ in range(2000):
        sample = [p for key in rng.choices(keys, k=len(keys)) for p in groups[key]]
        value = gain(sample, metric)
        if value is not None:
            values.append(value)
    values.sort()
    return [values[int(len(values) * .025)], values[min(len(values)-1, int(len(values)*.975))]] if values else [None, None]


def aggregate(rows):
    return {'attempted': len(rows), 'strict_passed': sum(r['strict_contract_pass'] for r in rows),
        'combined_passed': sum(r['combined_pass'] for r in rows),
        'api_failed': sum(r['api_failed'] for r in rows),
        'model_calls': sum(r['model_metrics']['calls'] for r in rows),
        'reported_input_tokens': sum(r['model_metrics']['input_tokens'] for r in rows),
        'reported_output_tokens': sum(r['model_metrics']['output_tokens'] for r in rows),
        'truncated_model_turns': sum(r['model_metrics']['truncated'] for r in rows),
        'wall_seconds': sum(r['wall_seconds'] for r in rows), 'median_wall_seconds': median(rows, 'wall_seconds'),
        'cli_commands': sum(r.get('cli_commands', 0) for r in rows),
        'server_rpcs': sum(r.get('server_rpcs', 0) for r in rows),
        'selector_seconds': sum(r.get('selector_seconds', 0) for r in rows)}


def batching_comparison(rows):
    lookup = {(r['scenario_id'], r['repetition'], r['policy']): r for r in rows}
    pairs = [(r, lookup[(r['scenario_id'], r['repetition'], 'model_selected')])
             for r in rows if r['policy'] == 'amortized_batching']
    successful = [(a, b) for a, b in pairs if a['combined_pass'] and b['combined_pass']]
    benefit = {metric: gain(successful, metric) for metric in ('wall_seconds', 'cli_commands', 'server_rpcs')}
    repeated = {metric: [gain([(a, b) for a, b in successful if a['repetition'] == rep], metric)
                          for rep in (0, 1)] for metric in ('wall_seconds', 'cli_commands')}
    adequate = lambda metric: (benefit[metric] is not None and benefit[metric] >= .10
        and all(value is not None and value >= 0 for value in repeated[metric]))
    no_loss = (sum(a['combined_pass'] for a, b in pairs) >= sum(b['combined_pass'] for a, b in pairs)
               and sum(a['strict_contract_pass'] for a, b in pairs) >= sum(b['strict_contract_pass'] for a, b in pairs))
    keep = bool(no_loss and (adequate('cli_commands') or adequate('wall_seconds')))
    return {'pairs': len(pairs), 'both_successful_pairs': len(successful),
        'excluded_pairs_from_successful_cost_summary': len(pairs) - len(successful),
        'candidate_only_success': sum(a['combined_pass'] and not b['combined_pass'] for a, b in pairs),
        'reference_only_success': sum(b['combined_pass'] and not a['combined_pass'] for a, b in pairs),
        'successful_pair_relative_reduction': benefit, 'reductions_by_repetition': repeated,
        'descriptive_cluster_intervals_95': {m: interval(successful, m) for m in ('wall_seconds', 'cli_commands')},
        'no_observed_completion_loss': no_loss, 'screening_retention_criterion_met': keep}


def main():
    frozen = verify()
    calibration_name = 'rosa-evaluation/artifacts/stage4-policy-20261021/ros-calibration/calibration.json'
    historical_freeze = read(ROOT / 'artifacts/stage4-policy-20261021/freeze.json')
    calibration_sha = sha(ROOT.parent / calibration_name)
    if calibration_sha != historical_freeze['source_sha256'][calibration_name]:
        raise RuntimeError('previously_frozen_calibration_changed')
    supervisor = read(CAMPAIGN / 'supervisor-status.json')
    reconciliation = read(CAMPAIGN / 'audit-reconciliation.json')
    if not reconciliation['all_records_accounted'] or reconciliation['live_trials'] != 160:
        raise RuntimeError('live_record_reconciliation_incomplete')
    for name, wanted in reconciliation['original_file_sha256'].items():
        if sha(CAMPAIGN / name) != wanted:
            raise RuntimeError('original_result_or_audit_changed:' + name)
    if sha(ROOT / 'experiments/stage4_batching/reconcile_audit.py') != reconciliation['analysis_source_sha256']:
        raise RuntimeError('reconciliation_source_changed')
    data, audits = {}, {}
    for backend in ('siwc', 'ollama'):
        data[backend] = read(CAMPAIGN / backend / 'result.json')
        audits[backend] = read(CAMPAIGN / backend / 'audit.json')
        accounted = [r for r in reconciliation['records'] if r['backend'] == backend]
        if data[backend]['status'] != 'COMPLETE' or len(data[backend]['trials']) != 80 or len(accounted) != 80 or not all(r['accounted'] for r in accounted):
            raise RuntimeError('incomplete_or_unaudited_backend:' + backend)
    summary = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'stage4_complete': True,
        'completion_meaning': 'planned attempts and final analysis closed with a documented audit exception; not all acceptance checks passed',
        'original_frozen_audit_acceptance_met': all(a['all_verified'] for a in audits.values()),
        'scope': 'simplified Stage 4 reliability plus matched-interface real-ROS batching; no full JTVR Runnable',
        'freeze_sha256': sha(CAMPAIGN / 'freeze.json'), 'backends': {},
        'calibration_sha256': calibration_sha,
        'audit_reconciliation': {k: v for k, v in reconciliation.items() if k != 'records'},
        'jtvr_policy_tier': read(ROOT / 'artifacts/stage4-policy-20261021/analysis.json')}
    runtime_path = CAMPAIGN / 'local-runtime-observation.json'
    if runtime_path.exists():
        summary['local_runtime_observation'] = read(runtime_path)
    resources = CAMPAIGN / 'resource-samples.csv'
    if resources.exists():
        with resources.open(encoding='utf-8-sig', newline='') as input_file:
            samples = list(csv.DictReader(input_file))
        summary['resource_sampling'] = {'samples': len(samples), 'interval_seconds': 10,
            'minimum_free_physical_mib': min(int(s['free_ram_kib']) for s in samples) / 1024,
            'minimum_free_virtual_mib': min(int(s['free_virtual_kib']) for s in samples) / 1024,
            'scope': 'host sampled free memory, not per-process peaks'}
    flat = []
    task_specs = {(job['stage'], job['spec']['id']): job['spec'] for job in read(CAMPAIGN / 'jobs.json')}
    for backend, batch in data.items():
        trials = batch['trials']
        per_turn_prompts, per_turn_completions = [], []
        for trial in trials:
            trace = read(CAMPAIGN / backend / 'trials' / trial['run_id'] / 'trace.json')
            for span in trace['spans']:
                if span['span_kind'] != 'LLM':
                    continue
                for key, output in (('llm.token_count.prompt', per_turn_prompts),
                                    ('llm.token_count.completion', per_turn_completions)):
                    value = span['attributes'].get(key)
                    if type(value) is int:
                        output.append(value)
        reli = [r for r in trials if r['stage'] == 'reliability']
        batch_rows = [r for r in trials if r['stage'] == 'batching']
        reliability = {}
        for arm in ('original', 'clarified', 'bounded_recovery', 'enforce_verification'):
            subset = [r for r in reli if r['intervention'] == arm]
            reliability[arm] = {**aggregate(subset),
                'physical_goal_achieved': sum(r['score']['oracle_goal_achieved'] for r in subset),
                'critical_prerequisite_violations': sum(r['contract']['critical_prerequisite_violations'] for r in subset),
                'report_argument_failures': sum(not r['contract']['report_arguments_compliant'] for r in subset),
                'automatic_verifications': sum(r['score'].get('automatic_verifications', 0) for r in subset),
                'orchestrator_recoveries': sum(r['orchestrator_recovery'] for r in subset)}
        by_family = {}
        for family in sorted({r['family'] for r in reli}):
            by_family[family] = {}
            for arm in reliability:
                subset = [r for r in reli if r['family'] == family and r['intervention'] == arm]
                by_family[family][arm] = {**aggregate(subset),
                    'critical_prerequisite_violations': sum(r['contract']['critical_prerequisite_violations'] for r in subset),
                    'rejected_action_attempts': sum(r['contract']['rejected_action_attempts'] for r in subset),
                    'false_success_at_report': sum(r['contract']['false_success_at_report'] for r in subset),
                    'unsupported_success_at_report': sum(r['contract']['unsupported_success_at_report'] for r in subset),
                    'verification_missing_at_report': sum(r['contract']['verification_missing_at_report'] for r in subset),
                    'iteration_limit_exits': sum(r['answer'] == 'Agent stopped due to max iterations.' for r in subset),
                    'report_argument_error_trials': sum(bool(r['contract']['report_argument_errors']) for r in subset),
                    'raw_argument_error_trials': sum(bool(r['contract']['raw_model_argument_errors']) for r in subset)}
        arms = {arm: aggregate([r for r in batch_rows if r['policy'] == arm])
                for arm in ('model_selected', 'amortized_batching')}
        paired_rows = {(r['scenario_id'], r['repetition'], r['policy']): r for r in batch_rows}
        same_native_vectors = 0
        for candidate in (r for r in batch_rows if r['policy'] == 'amortized_batching'):
            reference = paired_rows[(candidate['scenario_id'], candidate['repetition'], 'model_selected')]
            def tool_counts(row):
                evidence = read(CAMPAIGN / backend / 'trials' / row['run_id'] / 'evidence.json')
                return Counter(e['tool'] for e in evidence['native_events'])
            same_native_vectors += tool_counts(candidate) == tool_counts(reference)
        manifests = {}
        for arm in arms:
            subset = [r for r in batch_rows if r['policy'] == arm]
            evidence = [read(CAMPAIGN / backend / 'trials' / r['run_id'] / 'evidence.json') for r in subset]
            raw_helpers = [c for r in subset for c in r['raw_model_tool_calls'] if c['name'] == 'read_parameter_evidence']
            raw_well_typed = sum(isinstance(c['args'].get('names'), list)
                and all(type(n) is str for n in c['args']['names'])
                and isinstance(c['args'].get('report_names'), list)
                and isinstance(c['args'].get('expected_values'), dict)
                and all(type(v) is int for v in c['args']['expected_values'].values()) for c in raw_helpers)
            manifests[arm] = {'trials': len(evidence), 'requests': sum(e['manifest_requests'] for e in evidence),
                'raw_helper_calls': len(raw_helpers), 'raw_well_typed_helper_calls': raw_well_typed,
                'valid_requests': sum(e['valid_manifests'] for e in evidence),
                'first_valid': sum(e['first_manifest_valid'] is True for e in evidence),
                'bypassed_trials': sum(e['manifest_bypassed'] for e in evidence),
                'union_complete_trials': sum(e['manifest_union_complete'] for e in evidence),
                'phase_errors': sum(m.get('phase_valid') is False for e in evidence for m in e['manifests']),
                'preferred_strategies': dict(Counter(m['request']['strategy'] for e in evidence for m in e['manifests']))}
            arms[arm]['parser_seconds'] = sum(event.get('parser_seconds', 0) for e in evidence for event in e['native_events'])
            arms[arm]['native_seconds'] = sum(r['native_seconds'] for r in subset)
            arms[arm]['measured_model_seconds'] = sum(r['model_metrics']['elapsed_ms'] for r in subset) / 1000
            arms[arm]['schema_validation_abort_trials'] = sum(r['api_failed']
                and 'validation error' in r['answer'].lower() for r in subset)
            arms[arm]['flat_report_argument_trials'] = sum(any(
                c['name'] == 'submit_parameter_report'
                and isinstance(c['args'].get('observed_values'), dict)
                and any(not isinstance(v, dict) for v in c['args']['observed_values'].values())
                for c in r['raw_model_tool_calls']) for r in subset)
            arms[arm]['report_node_keys_missing_leading_slash_trials'] = sum(any(
                c['name'] == 'submit_parameter_report'
                and isinstance(c['args'].get('observed_values'), dict)
                and any(type(key) is str and not key.startswith('/')
                    and '/' + key in task_specs[('batching', r['scenario_id'])]['groups']
                    for key in c['args']['observed_values'])
                for c in r['raw_model_tool_calls']) for r in subset)
        summary['backends'][backend] = {'model': batch['model'], 'model_settings': batch['model_settings'],
            'started_utc': batch['started_utc'], 'finished_utc': batch['finished_utc'],
            'reliability': reliability, 'reliability_by_family': by_family,
            'batching_arms': arms, 'batching_comparison': batching_comparison(batch_rows),
            'manifests': manifests, 'total_model_calls': batch['total_model_calls'],
            'paired_identical_native_tool_count_vectors': same_native_vectors,
            'maximum_observed_native_commands': max(r['cli_commands'] for r in batch_rows),
            'observed_trials_over_24_native_commands': sum(r['cli_commands'] > 24 for r in batch_rows),
            'total_reported_tokens': batch['total_reported_tokens'],
            'trace_records_reviewed': len(audits[backend]['records']),
            'frozen_audit_verified': sum(r['verified'] for r in audits[backend]['records']),
            'session_cleanup': batch.get('session_cleanup'), 'refresh_count': batch.get('refresh_count')}
        summary['backends'][backend]['per_turn_token_observations'] = {
            'prompt_metadata_spans': len(per_turn_prompts),
            'completion_metadata_spans': len(per_turn_completions),
            'maximum_reported_prompt_tokens': max(per_turn_prompts, default=None),
            'maximum_reported_completion_tokens': max(per_turn_completions, default=None),
            'output_limit_turns_from_callback': sum(r['model_metrics']['truncated'] for r in trials)}
        summary['backends'][backend]['verification_step_only_failures'] = sum(
            not r['combined_pass'] and not r['api_failed']
            and r['contract']['outcome_classification_accurate']
            and r['contract']['report_arguments_compliant']
            and r['contract']['verification_missing_at_report'] > 0
            and not any(r['contract'][key] for key in ('critical_prerequisite_violations',
                'raw_model_argument_errors', 'instruction_sequence_violations', 'calls_after_report',
                'false_success_at_report', 'unsupported_success_at_report')) for r in reli)
        for row in trials:
            flat.append({key: row.get(key) for key in ('run_id', 'backend', 'model', 'stage', 'scenario_id', 'repetition',
                'intervention', 'policy', 'strict_contract_pass', 'combined_pass', 'api_failed', 'error_type',
                'wall_seconds', 'cli_commands', 'server_rpcs', 'selector_seconds', 'manifest_requests',
                'valid_manifests', 'manifest_bypassed', 'first_manifest_valid')} |
                {key: row['model_metrics'][key] for key in ('calls', 'input_tokens', 'output_tokens', 'truncated', 'tool_errors')})
    (CAMPAIGN / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
    with (CAMPAIGN / 'all-trials.csv').open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    write_report(summary, data, frozen)
    analysis_folder = CAMPAIGN / 'analysis-source'
    analysis_folder.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), analysis_folder / 'final_report.py')
    for source in (ROOT / 'experiments/stage4_batching/bounded_gateway.py',
                   ROOT / 'experiments/stage4_batching/runtime_snapshot.py',
                   ROOT / 'experiments/stage4_batching/offline_review.py',
                   ROOT / 'experiments/stage4_batching/reconcile_audit.py',
                   ROOT / 'experiments/stage4_batching/README.md',
                   ROOT / 'tests/test_stage4_hardening.py', ROOT / 'tests/test_stage4_analysis.py',
                   ROOT / 'tests/test_stage4_reconciliation.py'):
        shutil.copy2(source, analysis_folder / source.name)
    print(json.dumps({'report': str(CAMPAIGN / 'FINAL_REPORT_FOR_CHATGPT.md'), 'trials': len(flat),
                      'decisions': {b: s['batching_comparison']['screening_retention_criterion_met'] for b, s in summary['backends'].items()}}))


def fmt(value, percent=False):
    if value is None:
        return 'not estimable'
    return f'{value:.2%}' if percent else f'{value:.3f}'


def write_report(summary, data, frozen):
    output = ['# Stage 4 completion: results, conclusions and next steps', '',
        'This is the final report for the simplified Stage 4 authorized after the',
        'negative original-JTVR policy comparison. Both backend schedules and their',
        'state/Phoenix records have been reviewed, with eight explicitly documented',
        'missing recovery-stop tool spans. The frozen auditor/supervisor failure is',
        'preserved alongside a separate reconciliation. An unfavorable outcome is a valid stage',
        'completion; it is not a claim that batching or either model is robot-ready.', '',
        '## Decisions', '']
    for backend, result in summary['backends'].items():
        decision = result['batching_comparison']
        output.append(f"- **{result['model']}**: " + ('the predefined batching retention screen was met within this interface.' if decision['screening_retention_criterion_met'] else
            'the predefined batching retention screen was not met; keep model-selected planning as the reference and batching optional.'))
        if decision['both_successful_pairs'] == 0:
            output.append('  No pair completed successfully under both arms, so a successful-task cost/time benefit is not estimable. This is an unsuccessful integration screen, not proof that the selector is intrinsically ineffective for this model.')
    output += ['', 'Original bounded-lookahead JTVR remains paused. It tied strong amortized',
        'batching in all 96 primary policy fixtures; it offered zero additional',
        'modeled cost benefit and used more recorded selector time. Do not relabel batching',
        'as JTVR or infer that a full custom Runnable was implemented.', '',
        '## Scope and project history', '',
        'The shared Qwen/hosted ROSA interface, Phoenix tracing and stateful mock',
        'benchmark predate this campaign. Baseline v1 has 540 scripted and 120 live',
        'trials. Original hosted/local baseline handling scores remain 30/36 and',
        '24/36; retrospective stricter contract checks remain 30/36 and 12/36.',
        'Both originally verified all 18 achievable baseline goals. Wrong report',
        'arguments and attempted picks with UNKNOWN pose were material local issues;',
        'controller rejection is a protection, not credit for model policy.', '',
        'The canceled V2 hosted batch made zero model requests while awaiting',
        'consent. The fixed dependency bundle once named jtvr was never the original',
        'algorithm. Its 264 scripted controls and nine local diagnostics remain',
        'separate. The subsequent original-spec policy tier has 1,152 episodes plus',
        '15 real ROS smoke cases, with no model requests. The present campaign is',
        'the prospective live follow-up; none of those historical samples are pooled.', '',
        'The superseded 120-trial V2 live schedule, including the 60 expanded movement',
        'fixtures, was not resumed. This authorized simplified completion uses six',
        'development reliability fixtures and eight real-parameter templates. The',
        'expanded movement suite remains scripted-only; no held-out live movement',
        'generalization result is claimed.', '',
        '## Frozen methods and limits', '',
        f"Freeze time UTC: `{frozen['frozen_utc']}`. SHA-256: `{summary['freeze_sha256']}`.",
        '80 trials per backend: 48 independent reliability-intervention trials and',
        '32 end-to-end parameter-task trials. Two repeats, fresh agent/world/cache',
        'per trial, balanced arm order. Reliability has six development fixtures;',
        'batching has eight nominal templates. Repetitions are not new task families.', '',
        'The real ROSA AgentExecutor and existing backend factory run every live',
        'trial. Default ROSA tools are disabled for isolation: the parameter track',
        'registers six supported native schemas plus the shared helper/report tools.',
        'This is not a full-catalogue tool-confusion benchmark. Local Qwen uses the unchanged 8192/256, temperature0, seed42, mmaptrue',
        'profile. Hosted uses exact account-catalog model gpt-6.1-sol with account',
        'defaults. Provider sampling, context and hidden KV behavior are unequal.',
        'No model upgrades, episodic memory or unreported evaluation reruns.', '',
        'Per backend: hard cap 1,056 model requests, 240 seconds/trial and six hours.',
        'Reliability caps 14 model calls/trial; batching caps 12. The native parameter',
        'budget target is 24 operations/trial; the write-dispatch enforcement gap',
        'is disclosed below with observed counts. OAuth credentials stay in memory and are',
        'revoked; request records exclude transport-only private continuation data.', '',
        'The loaded local model identity and actual context were checked using read-only',
        'Ollama metadata during execution. The observation, quantization/digest and',
        'GPU snapshot are included in the package; they do not alter inference settings.',
        'Ten-second host memory samples are provided separately from per-trial timings.',
        'They are sampled host free memory, not process memory peaks or proof of a',
        'specific performance bottleneck. See analysis.json for exact runtime fields.', '',
        '### Completed run ledger', '',
        '| Backend | Start UTC | Finish UTC | Model requests / cap | Reported total tokens | Cleanup |',
        '| --- | --- | --- | ---: | ---: | --- |']
    for backend, result in summary['backends'].items():
        cleanup = result['session_cleanup'] or 'No OAuth session for local backend'
        output.append(f"| {backend} | {result['started_utc']} | {result['finished_utc']} | {result['total_model_calls']} / 1056 | {result['total_reported_tokens']} | {cleanup} |")
    output += ['',
        'The hosted refresh count is ' + str(summary['backends']['siwc']['refresh_count']) + '.',
        'Audit time and setup are outside per-trial agent timings. Total token',
        'metadata is retained as reported by each backend; the tokenizers and',
        'provider accounting differ, so totals are not directly comparable costs.', '',
        '| Backend | Turns with prompt metadata | Maximum reported prompt tokens | Maximum reported completion tokens | Output-limit turns |',
        '| --- | ---: | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        tokens = result['per_turn_token_observations']
        output.append(f"| {backend} | {tokens['prompt_metadata_spans']} | {tokens['maximum_reported_prompt_tokens']} | {tokens['maximum_reported_completion_tokens']} | {tokens['output_limit_turns_from_callback']} |")
    output += ['',
        'These are reported token observations, not an inspection of hidden context',
        'truncation or KV state. Output-limit events differ from iteration-limit exits;',
        'a bounded final narrative can be truncated even after a valid structured',
        'report. Diagnose performance and interface behavior separately before tuning.', '',
        '## Reliability results', '',
        'Each intervention arm has 12 trials: transfer, accepted failure and missing',
        'sensor, two variants and two repetitions. Controls use original instructions;',
        'clarification, bounded recovery and enforced verification are separate.', '',
        '| Backend | Intervention | Strict passes | Combined passes | Operational failures | Mock goal states reached | Critical prerequisite violations | Noncompliant / missing reports | Model calls | Auto verifications / guard recoveries |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        for arm, row in result['reliability'].items():
            output.append(f"| {backend} | {arm} | {row['strict_passed']}/12 | {row['combined_passed']}/12 | {row['api_failed']} | {row['physical_goal_achieved']} | {row['critical_prerequisite_violations']} | {row['report_argument_failures']} | {row['model_calls']} | {row['automatic_verifications']} / {row['orchestrator_recoveries']} |")
    output += ['', 'These goal states belong to the mock world; no robot moved. Goal achievement',
        'is expected only on achievable transfer cases. Correct',
        'failure/unknown handling is still required on the other cases. Strict',
        'compliance and operational completion are reported separately. Repairs',
        'belong to the combined system. No single intervention is silently credited',
        'with another intervention or with a controller rejecting unsafe attempts.',
        'The bounded guard can stop repetition but cannot erase an invalid action',
        'attempt that happened before activation; such trials retain their critical',
        'contract violations even when the orchestrator subsequently reports correctly.',
        'Compare prospective arms with each other; their 12-trial fixture mix differs',
        'from the original 36-trial baseline, so those percentages are not a direct',
        'before/after improvement estimate.',
        'The battery=-1 sentinel is a deliberately strict API convention, not a',
        'physical robotics requirement. Reporting the observed battery instead can',
        'fail this contract even when the goal was reached. That differs materially',
        'from an attempted action with UNKNOWN pose. Keep error severity separate;',
        'a future task-specific report schema can remove irrelevant fields, tested',
        'prospectively without rewriting these scores.', '']
    for backend, result in summary['backends'].items():
        reliability = result['reliability']
        original = reliability['original']['combined_passed']
        bounded = reliability['bounded_recovery']
        enforced = reliability['enforce_verification']
        output.append(f"{backend}: bounded recovery had {bounded['orchestrator_recoveries']} actual guard recoveries; enforced verification added {enforced['automatic_verifications']} automatic checks.")
        if not bounded['orchestrator_recoveries'] and bounded['combined_passed'] != original:
            output.append('The bounded-arm pass difference occurred without a guard recovery, so it is not demonstrated benefit from the repair mechanism; sampling/behavior variability remains an explanation.')
        output.append(f"Clarification alone produced {reliability['clarified']['combined_passed']}/12 combined passes versus {original}/12 with original instructions. This is a small within-profile screen, not a general model ranking or independently confirmed intervention effect.")
        output.append(f"{result['verification_step_only_failures']} failures across the reliability arms had accurate outcome classification and compliant report arguments, with the missing required verifier step as their recorded contract defect. In UNKNOWN sensor cases, this final verifier invocation is a task-contract requirement; omitting it is not equivalent to an unsafe action or a false claim of success.")
        output.append('')
    output += ['### Descriptive failure breakdown by fixture family', '',
        'Four attempts per family/arm. These are descriptive diagnostics, not extra',
        'retention tests. Critical counts are violating action indices, while rejected',
        'attempts count controller rejections. Missing reports differ from reports',
        'with bad arguments; the aggregate noncompliance column above includes both.', '',
        '| Backend | Family | Arm | Combined passes | Iteration-limit exits | Rejected actions | Critical violations | Bad report-argument trials | Raw argument-error trials | False / unsupported success claims | Missing verification at report |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        for family, arms in result['reliability_by_family'].items():
            for arm, row in arms.items():
                output.append(f"| {backend} | {family} | {arm} | {row['combined_passed']}/4 | {row['iteration_limit_exits']} | {row['rejected_action_attempts']} | {row['critical_prerequisite_violations']} | {row['report_argument_error_trials']} | {row['raw_argument_error_trials']} | {row['false_success_at_report']} / {row['unsupported_success_at_report']} | {row['verification_missing_at_report']} |")
    output.append('')
    output += [
        '## End-to-end batching: what was actually compared', '',
        'Both arms have the same primitive ROSA tools, strong cost guidance, evidence',
        'ledger and read_parameter_evidence convenience executor. Native helper',
        'arguments are the model-generated requirement manifest; no annotated manifest',
        'is supplied to the optimizer. Missing report/verification fields or targets',
        'produce a recorded error and no hidden reads. Primitive-tool fallback remains',
        'available. Invalid manifests are not silently filled by the evaluator.', '',
        'Reference honors the model-preferred direct/bulk/node_bulk plan. Candidate',
        'uses amortized selection over the same declared needs and capabilities.',
        'Both can execute discovery plus bulk in one model tool call. This is a',
        'matched orchestration baseline, stronger than withholding bulk from reference,',
        'and is not untouched upstream ROSA. Extra helper schemas are shared costs.', '',
        'Selector costs reuse the small development calibration from the earlier',
        'policy study (two samples per tool). Its separately frozen hash is verified',
        'again in this analysis; no test-outcome recalibration is performed. These',
        'weights guide selection but are not a latency guarantee on live tasks.', '',
        'The comparison isolates automatic plan selection on top of a shared batching',
        'executor. A primitive-only untouched-ROSA arm was not run. Consequently,',
        'this study cannot establish the helper/continuation speedup over upstream',
        'ROSA, or conclude that batching in general is unnecessary. Model-selected',
        'planning here still retains access to the tested batching executor.', '',
        'Eight templates: single, three cold, three warm, write/report/verify, mixed',
        'report/verification roles, node-summary overlap, two-node scope, and parameters',
        'plus topic details. Real scoped ROS parameter nodes are used; no robot motion.',
        'Resets and independent evaluator queries are logged outside agent work.',
        'Charged type warm-up, writes, failed attempts and automatic reads are included.', '',
        'The nominal two-node case initializes both nodes to the same numeric values.',
        'Its ledger checks separate acquisition and exact entity identifiers; it does',
        'not demonstrate discrimination of differing values across nodes. Independently',
        'varying node values is required in a broader scope/generalization campaign.', '',
        'Agent wall time includes agent construction, charged warm-up, model calls,',
        'tool work and generation of the final answer. It excludes outside-trial',
        'reset/evaluator operations, trace flush/export and artifact writes. Reported',
        'server RPC counts are the instrumented parameter-service callbacks, not all',
        'DDS traffic. Free-form final prose is preserved but not semantically graded;',
        'correctness uses the structured report and independent state/evidence.', '',
        '| Backend | Arm | Combined passes | Strict passes | Operational failures | Model calls | Input / output tokens | CLI commands | Server RPCs | Total / median trial s | Selector / parser elapsed s |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        for arm, row in result['batching_arms'].items():
            output.append(f"| {backend} | {arm} | {row['combined_passed']}/16 | {row['strict_passed']}/16 | {row['api_failed']} | {row['model_calls']} | {row['reported_input_tokens']} / {row['reported_output_tokens']} | {row['cli_commands']} | {row['server_rpcs']} | {fmt(row['wall_seconds'])} / {fmt(row['median_wall_seconds'])} | {fmt(row['selector_seconds'])} / {fmt(row['parser_seconds'])} |")
    output += ['', '### Matched successful pairs and retention screen', '',
        'Native work means actual CLI commands, fixed in the analysis clarification',
        'before any batching outcomes. RPC counts are secondary. No speed credit is',
        'given for early failed termination. All-attempt totals appear above.', '',
        'Relative reduction uses one minus the candidate/reference ratio of summed',
        'matched wall times or work, not the difference of medians. The median can',
        'move in a different direction when a few longer trials dominate the total.', '',
        '| Backend | Both successful pairs | Excluded pairs | Candidate-only / reference-only success | Time reduction | CLI reduction | Time interval | CLI interval | Retain screen |',
        '| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |']
    for backend, result in summary['backends'].items():
        row = result['batching_comparison']
        ci = row['descriptive_cluster_intervals_95']
        output.append(f"| {backend} | {row['both_successful_pairs']}/16 | {row['excluded_pairs_from_successful_cost_summary']} | {row['candidate_only_success']} / {row['reference_only_success']} | {fmt(row['successful_pair_relative_reduction']['wall_seconds'], True)} | {fmt(row['successful_pair_relative_reduction']['cli_commands'], True)} | {', '.join(fmt(v, True) for v in ci['wall_seconds'])} | {', '.join(fmt(v, True) for v in ci['cli_commands'])} | {row['screening_retention_criterion_met']} |")
    output += ['', 'Screen: no observed total completion loss plus >=10% matched successful',
        'time or CLI reduction, with nonnegative direction in both repetitions.',
        'Bootstrap intervals cluster by available task templates (at most eight), 2,000 resamples, seed',
        '20261021. They are descriptive, not proof of safety/noninferiority. The',
        'machine-readable analysis includes each repetition and every paired outcome.', '',
        'As an exploratory mechanism check, inspect whether paired primitive-tool',
        'count vectors differ. A timing-only screen result with identical native work',
        'does not by itself establish that deterministic selection caused a speedup;',
        'model serving and action-generation variability remain explanations.', '']
    for backend, result in summary['backends'].items():
        output.append(f"{backend}: {result['paired_identical_native_tool_count_vectors']}/16 paired trials had identical primitive-tool count vectors.")
    output += ['',
        '## Model communication of requirements', '',
        '| Backend | Arm | Raw helper calls | Raw well-typed calls | Recorded / post-schema valid requests | First-valid trials | Complete parameter-node union | Bypassed trials | Phase errors |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        for arm, row in result['manifests'].items():
            output.append(f"| {backend} | {arm} | {row['raw_helper_calls']} | {row['raw_well_typed_helper_calls']} | {row['requests']} / {row['valid_requests']} | {row['first_valid']}/16 | {row['union_complete_trials']}/16 | {row['bypassed_trials']} | {row['phase_errors']} |")
    output += ['', 'A passing task can bypass the helper using primitive reads; that is not a',
        'successful manifest extraction. A complete per-node union differs from a',
        'valid first request on only one node. Preferred strategy distributions,',
        'manifest contents, corrections and evidence are retained per trial. This',
        'tests a supported structured tool interface, not general language understanding.',
        'Queries explicitly name parameters. Union coverage refers to parameter-node',
        'requirements; graph/topic needs are checked separately in task compliance.',
        'Post-schema validity can differ from raw typing; strict scoring checks raw',
        'arguments too, and calls rejected before entering the helper remain visible',
        'in the raw-call denominator. No general manifest-extraction claim is made.', '',
        '### Report-interface failures', '',
        'The helper returns node_name plus a flat observed_values object for that',
        'node; the report tool requires observed_values nested by node. The model',
        'must perform that conversion. ROSA currently returns an error and aborts',
        'the trial on an unhandled tool-schema validation error, so this study does',
        'not measure whether a model could correct that error with bounded feedback.',
        'A valid read manifest followed by a malformed report is a combined-system',
        'failure, not evidence that the model could not identify its read requirements.', '',
        '| Backend | Arm | Schema-validation abort trials | Trials with flat raw report values | Report keys missing node leading slash |',
        '| --- | --- | ---: | ---: | ---: |']
    for backend, result in summary['backends'].items():
        for arm, row in result['batching_arms'].items():
            output.append(f"| {backend} | {arm} | {row['schema_validation_abort_trials']} | {row['flat_report_argument_trials']} | {row['report_node_keys_missing_leading_slash_trials']} |")
    output += ['',
        'Required structured fields and details are graded. Arbitrary additional',
        'claims and final prose are not exhaustively semantically evaluated. A future',
        'report contract should define and test extra-field/extra-claim behavior.', '',
        'The leading-slash diagnostic describes a raw identifier mismatch; it does',
        'not canonically rewrite identifiers or award retrospective passes. A correctly',
        'observed number can still be unsupported under an incorrectly scoped report key.', '',
        '## Every failed trial', '']
    for backend, batch in data.items():
        failed = [r for r in batch['trials'] if not r['combined_pass']]
        output.append(f'### {backend}: {len(failed)} failures out of 80 attempts')
        output.append('')
        if not failed:
            output += ['None under the frozen combined contract.', '']
        for row in failed:
            evidence = read(CAMPAIGN / backend / 'trials' / row['run_id'] / 'evidence.json')
            reasons = evidence.get('errors') if row['stage'] == 'batching' else {
                k: v for k, v in row['contract'].items() if k in ('strict_contract_pass',
                    'report_argument_errors', 'instruction_sequence_violations', 'critical_prerequisite_violations',
                    'verification_missing_at_report', 'false_success_at_report', 'unsupported_success_at_report')}
            output.append(f"- `{row['run_id']}` — {row['stage']} / {row['scenario_id']} / repeat {row['repetition']} / {row['intervention']} / {row['policy']}; operational failure={row['api_failed']}, exception={row['error_type']}, calls={row['model_metrics']['calls']}. Reasons: `{json.dumps(reasons, separators=(',', ':'))}`. [Raw evidence]({backend}/trials/{row['run_id']}/evidence.json).")
            if row['api_failed']:
                output.append('  Operational output: ' + json.dumps(row['answer']) + '.')
        output.append('')
    output += ['## Audits, preflight corrections and preservation', '',
        'All 160 live trials have separate state/raw-result and Phoenix records. Passing',
        'an audit means records agree; it does not mean the task passed. Evaluators',
        'are independent of model claims, but share trusted fixture code and some',
        'scoring functions; they are not independently authored or blinded. Native values',
        'were compared with separately recorded ROS server callbacks and independent',
        'final evaluator queries. Every actual native operation has an explicit actor',
        'span. Installed instrumentation parents these spans to the run, so actor',
        'provenance rather than assumed nesting distinguishes them from model dispatches.', '',
        '**Audit exception:** the frozen hosted audit passed 80/80; the frozen local',
        'audit passed 72/80 and failed eight bounded-recovery trials. Their state',
        'checks and model-call counts agree, but each lacks the final stopped tool',
        'span. InterventionStop derives from BaseException; the installed LangChain',
        'tool handler catches Exception/KeyboardInterrupt, so this signal bypasses',
        'its normal error/finish callback. The original supervisor remains FAILED.',
        'No missing span was fabricated and no task result was rerun or rescored.', '',
        'The originally specified full audit acceptance check was therefore not',
        'fully met. Stage completion here means closure of the planned experiment',
        'and its analysis with that exception, not a claim that every gate passed.', '',
        'The separate audit-reconciliation.json accounts for all 160 records using',
        'strict cross-checks: saved raw tool calls, the final LLM tool-call ID/arguments,',
        'callback dispatch count, exact world-call prefix, reconstructed guard predicate',
        'and attributed orchestrator report. All eight exceptions match that one',
        'pattern. Complete tool-span coverage is still false. Five focused checks',
        'cover the supported case and reject extra loss, tampering, absent reports',
        'and nonintervention trials. This is a post-run observability reconciliation,',
        'not an independently authored evaluator or a repair to the frozen auditor.', '',
        'Before live requests: 72 discovery tests passed, then the focused 11-test',
        'integration suite passed after two added fault/type tests (74 distinct tests',
        'across these runs). Sixteen actual-ROS scripted acceptance cases passed and',
        'a scripted native-message ROSA/Phoenix trace passed. These are controls, not',
        'paid model episodes. Preflight fixes addressed namespace test discovery,',
        'private ROS executor context, CLI graph readiness/timeout, separate Phoenix',
        'client environment, bounded local trace reads and explicit span provenance.',
        'Each failed preflight directory and disposition remains. No model outcome',
        'was discarded to fix these infrastructure errors.', '',
        'Historical reports and JTVR policy evidence remain frozen. Exact baseline',
        'archive and source identities are preserved rather than retrospectively',
        'rewritten. The new live freeze contains 137 source/input files, including',
        'the sibling research dependency snapshot. The evaluation commit therefore',
        'does not rely only on an uncommitted research checkout being available.', '',
        '## Practical limits and conclusions', '',
        'These small nominal parameter tasks test real tool interfaces, not robot',
        'physics, perception, manipulation or arbitrary ROS services. Local epochs',
        'cannot detect arbitrary external writers; no atomic snapshot is guaranteed.',
        'Only exact registered read services and authorized writes are allowed.',
        'A source audit found that the 24-operation guard blocks further native reads',
        'after 24 recorded events, while exact authorized writes lack an independent',
        'dispatch-count guard. Model/time caps still bound them. The observed maxima',
        'and any over-limit trials are reported below; the frozen code is preserved',
        'rather than silently repaired during evaluation. A global dispatch guard is',
        'required before any wider or actuator-facing use. The separate BoundedGateway',
        'class closes that gap and has two focused unit tests; it was not used by the',
        'frozen live study and is not credited with its results.',
        '; '.join(f"{backend}: maximum {result['maximum_observed_native_commands']} native commands, {result['observed_trials_over_24_native_commands']} trials above 24" for backend, result in summary['backends'].items()) + '.',
        'Failure handling is investigated separately in the movement mock track;',
        'real parameter fault/generalization campaigns have not been completed.', '',
        'The catalogue is small and mainly per-node separable. Strong model planning',
        'can already select the amortized optimum. Equal end-to-end results are a',
        'reason to simplify, not to invent harder tools or revive lookahead without',
        'a grounded need. Repairs and plan substitutions are combined-system effects.',
        'Shared helper execution deliberately removes unequal continuation savings.', '',
        'Both repetitions share fixtures, dependencies and host. User workloads,',
        'partial GPU offload, warm-up, provider routing and unresettable KV state can',
        'affect latency. Fixed local settings do not make models or token budgets',
        'equivalent. Low error counts do not prove robot safety. Reported tokens',
        'are provider metadata, not a financial cost estimate.', '',
        '## Recommended next steps and six-stage status', '',
        '1. Keep the simpler configuration unless this screen supports a scoped',
        '   batching benefit. Keep original-JTVR negative results visible.',
        '2. Choose a specific robot and a bounded Gazebo task: identify its ROS',
        '   distribution, URDF/controllers, planning/skill interface, scene and',
        '   success/verification contract before installing an arbitrary arm stack.',
        '3. Start with read-only state and deterministic arm skills, then test',
        '   high-level model requests under limits and independent verification.',
        '   First test a consistent task-specific report schema and bounded schema-',
        '   validation feedback as a separate prospective interface intervention.',
        '   Do not silently fill missing model fields. Evaluate finishing directly on',
        '   a validated final report to avoid an unnecessary narrative-generation',
        '   turn. These are future variants, not measured benefits of this study.',
        '   Keep a deterministic skill/planner control for fixed tasks. The LLM',
        '   should be evaluated on goal interpretation and flexible task choice,',
        '   not credited with deterministic checks already implemented in tools.',
        '4. Broaden real failure/generalization tasks before making reliability',
        '   claims. Revisit lookahead only if actual catalogue overlap defeats the',
        '   current amortized groups.',
        '5. Defer episodic memory until tasks require history and matched retrieval,',
        '   examples, token budgets, freshness and verification controls are defined.', '',
        '| Stage | Status |', '| --- | --- |',
        '| 1, shared backends | Demonstrated through actual ROSA; both used in this live campaign. |',
        '| 2, contract/scoring | State audits complete; eight tool-span gaps documented and reconciled separately. |',
        '| 3, baseline/reliability | V1 preserved; independent prospective interventions now evaluated. |',
        '| 4, caching/selection | Planned simplified screen and analysis closed with the documented audit exception; neither retention screen met. Full JTVR paused. |',
        '| 5, episodic memory | Not started; no prerequisite to simulator integration. |',
        '| 6, Gazebo/hardware | Simulator foundation installed; specific arm, skills and hardware remain unconfigured. |', '',
        '## Evidence, reproduction and repository publication', '',
        '- [Machine-readable analysis](analysis.json), [all 160 trial rows](all-trials.csv).',
        '- [Hosted audit](siwc/audit.json), [local audit](ollama/audit.json).',
        '- [Post-run audit reconciliation](audit-reconciliation.json).',
        '- [Frozen source/input hashes](freeze.json), [jobs](jobs.json).',
        '- [Frozen protocol](../../docs/STAGE4_BATCHING_COMPLETION_PROTOCOL.md).',
        '- [Offline review and reproduction guide](../../docs/STAGE4_EVIDENCE_GUIDE.md).',
        '- [Earlier JTVR report](../stage4-policy-20261021/REPORT_FOR_CHATGPT.md).', '',
        'Restore the byte-exact frozen evaluation AND research sources from the',
        'snapshot before hash verification; Git line-ending conversion can otherwise',
        'change working-file bytes. Reconstruct the research checkout, install its',
        'locked uv environment and ROS Jazzy dependencies, start the separate Phoenix',
        'service, and verify source hashes. Live commands are the runner/audit modules',
        'recorded in supervisor logs; hosted reruns need fresh consent and a separately',
        'named campaign. Never overwrite this campaign or silently rerun failed data.', '',
        'This analysis module was added after the execution freeze and performs only',
        'post-run analysis. Its exact source is archived under analysis-source. The',
        'analysis metric clarification was recorded before Track B outcomes.', '',
        'Publication target: Lelevinson/rosa-evaluation, member/martin. The final',
        'results commit includes code, curated evidence and this report. Its SHA is',
        'provided in the handoff/commit history, avoiding a circular self-hash in the',
        'report. Credentials, environments and raw local databases are excluded.', '',
        'For ChatGPT review: examine matched-baseline fairness, manifest omissions,',
        'whether interventions help independently, failure attribution and whether',
        'the retention decisions justify the next simulator experiment. The full',
        'evidence package is more informative than headline pass rates alone.']
    (CAMPAIGN / 'FINAL_REPORT_FOR_CHATGPT.md').write_text('\n'.join(output) + '\n')


if __name__ == '__main__':
    main()
