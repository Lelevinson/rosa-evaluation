"""Publish audited v2 results with explicit missing-work and go/no-go decisions."""
from collections import defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
import random
import shutil
import statistics
import zipfile
from ..config import ROOT, run_dir
from .runner import CAMPAIGN


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def aggregate(rows):
    return {'attempted': len(rows),
        'strict_completed': sum(r['contract']['strict_contract_pass'] and not r['api_failed'] for r in rows),
        'physical_goals': sum(r['score']['oracle_goal_achieved'] for r in rows),
        'accurate_outcomes': sum(r['contract']['outcome_classification_accurate'] and not r['api_failed'] for r in rows),
        'invalid_argument_reports': sum(bool(r['contract']['report_argument_errors']) for r in rows),
        'raw_model_argument_violations': sum(len(r['contract']['raw_model_argument_errors']) for r in rows),
        'instruction_sequence_violations': sum(len(r['contract']['instruction_sequence_violations']) for r in rows),
        'critical_prerequisite_violations': sum(r['contract']['critical_prerequisite_violations'] for r in rows),
        'missed_verification': sum(r['contract']['verification_missing_at_report'] for r in rows),
        'unsupported_success': sum(r['contract']['unsupported_success_at_report'] for r in rows),
        'false_success': sum(r['contract']['false_success_at_report'] for r in rows),
        'operational_failures': sum(r['api_failed'] for r in rows),
        'model_calls': sum(r['model_metrics']['calls'] for r in rows),
        'eligible_reads': sum(r['score']['sensor_backend_reads'] for r in rows),
        'mandatory_reads': sum(r['score']['mandatory_sensor_reads'] for r in rows),
        'cache_hits': sum(r['score']['cache_hits'] for r in rows),
        'stale_observations': sum(r['score']['stale_observations_served'] for r in rows),
        'orchestrator_verifications': sum(r['score']['automatic_verifications'] for r in rows),
        'orchestrator_reports': sum(r['score']['system_reports'] for r in rows),
        'median_seconds': statistics.median([r['wall_seconds'] for r in rows]) if rows else None}


def paired(rows, candidate='jtvr', reference='conservative'):
    ref = {r['scenario_id']: r for r in rows if r['stage'] == 'information' and r['policy'] == reference}
    pairs = [(ref[r['scenario_id']], r) for r in rows if r['stage'] == 'information' and r['policy'] == candidate and r['scenario_id'] in ref]
    successful = [(a, b) for a, b in pairs if not a['api_failed'] and not b['api_failed'] and a['contract']['strict_contract_pass'] and b['contract']['strict_contract_pass']]
    a, b = aggregate([a for a, _ in pairs]), aggregate([b for _, b in pairs])
    reliability_ok = all(b[k] <= a[k] for k in ('critical_prerequisite_violations', 'missed_verification', 'unsupported_success', 'false_success')) and b['strict_completed'] >= a['strict_completed']
    result = {'reference': reference, 'candidate': candidate, 'pairs': len(pairs), 'successful_pairs': len(successful),
              'reference_all_attempts': a, 'candidate_all_attempts': b, 'observed_reliability_preserved': reliability_ok,
              'excluded_from_efficiency': [x['scenario_id'] for x, y in pairs if (x, y) not in successful],
              'scenario_pairs': [{'scenario': x['scenario_id'], 'reference': x['run_id'], 'candidate': y['run_id'],
                                  'both_strictly_completed': (x, y) in successful} for x, y in pairs]}
    for key, label in (('wall_seconds', 'time'), ('model_calls', 'calls'), ('sensor_reads', 'reads')):
        def value(row):
            return row['wall_seconds'] if key == 'wall_seconds' else row['model_metrics']['calls'] if key == 'model_calls' else row['score']['sensor_backend_reads']
        denominator = sum(value(x) for x, _ in successful)
        improvement = 1 - sum(value(y) for _, y in successful) / denominator if denominator else None
        grouped = defaultdict(list)
        for x, y in successful:
            grouped[x['family']].append((value(x), value(y)))
        clusters = list(grouped.values())
        rng = random.Random(20261022)
        samples = []
        if clusters:
            for _ in range(1000):
                chosen = [pair for cluster in rng.choices(clusters, k=len(clusters)) for pair in cluster]
                total = sum(x for x, y in chosen)
                if total:
                    samples.append(1 - sum(y for x, y in chosen) / total)
        samples.sort()
        bounds = [samples[int((len(samples) - 1) * q)] for q in (.025, .975)] if samples else [None, None]
        result[f'{label}_fraction_saved_on_successful_pairs'] = improvement
        result[f'{label}_family_bootstrap_95'] = bounds
    sufficient = len(successful) >= 10 and len(pairs) == 12
    benefit = any(result[f'{label}_fraction_saved_on_successful_pairs'] is not None
                  and result[f'{label}_fraction_saved_on_successful_pairs'] >= threshold
                  and result[f'{label}_family_bootstrap_95'][0] > 0 for label, threshold in (('time', .10), ('calls', .20)))
    result['screening_decision'] = ('INCONCLUSIVE_INSUFFICIENT_SUCCESSFUL_PAIRS' if not sufficient else
                                    'NO_GO_RELIABILITY' if not reliability_ok else
                                    'PASS_EFFICIENCY_SCREEN' if benefit else 'NO_GO_EFFICIENCY_NOT_ESTABLISHED')
    return result


def main():
    frozen = read(CAMPAIGN / 'freeze.json')
    changes = [name for name, digest in frozen['source_sha256'].items() if hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest() != digest]
    if changes:
        raise RuntimeError('Frozen code changed; cannot silently report this as the same experiment')
    batches = {}
    audits = {}
    for backend in ('scripted', 'siwc', 'ollama'):
        reference = CAMPAIGN / f'{backend}-batch.json'
        if reference.exists():
            identifier = read(reference)['batch_id']
            batches[backend] = read(run_dir(identifier) / 'result.json')
            path = run_dir(identifier) / 'phase4-audit.json'
            audits[backend] = read(path) if path.exists() else None
    complete = len(batches) == 3 and all(b['status'] == 'COMPLETE' for b in batches.values()) and all(a and a['all_verified'] and a['trials_audited'] == len(batches[name]['trials']) for name, a in audits.items())
    summary = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'phase4_complete': complete,
               'source_changes_after_freeze': changes, 'batches': {}, 'decisions': {}}
    lines = ['# Phase 4 v2: contract, reliability and information acquisition', '',
             f'Campaign complete: **{complete}**. A completed batch may contain failed tasks. Missing or unaudited work is not treated as a passing result.', '',
             'This is a mock engineering screen. New live baselines cover 60 distinct fixtures once per backend, across 12 mechanisms; six development and six evaluation families differ in mechanism. The evaluator/scenario authors know both sets. Evaluation families were frozen before inference and were not used for prompt tuning. This is not independently authored or statistically powered held-out validation.', '',
             'The original v1 results and archive are preserved. Additional retrospective checks are in retrospective.json. Keep physical goal achievement, argument compliance, outcome classification, critical attempted commands, and strict completed handling separate. Every non-refusal task requires verification before reporting. The original -1 report sentinel is retained; a reporting-API redesign was not mixed into these experiments.', '',
             '## Fixed design', '',
             'See PHASE4_V2_PLAN.md, freeze.json, scenario-manifest.json and source/. Reliability trials compare four independent configurations on six v1 development fixtures: original instructions, clarified instructions, bounded recovery, or report-time verification enforcement. New-world baselines use one common explicit v2 contract and do not have recovery guards. Comparing them directly to v1 percentages does not isolate a model improvement.', '',
             'The minimal JTVR prototype only gathers observations for a requested action using explicit dependency lists and publicly delivered invalidations. It never chooses a goal, executes an action, verifies an outcome, or submits a report. The eager bundle uses the same composite API but gathers every information type. The deterministic planner uses only public task parameters and observations. Conservative cache, eager bundle, and JTVR all keep controller checks and verification uncached. Observation freshness is logical ticks with simulator-provided notification reliability, not a production reliability estimator.', '',
             'Per live backend: 24 reliability trials, 60 new no-cache cases, 36 paired information-policy cases = 120 attempts. At most 14 model calls and 240 seconds per trial; 1,680 requests per backend. Fresh worlds, agents and caches per trial; provider-managed KV caching remains. Local settings remain 8192 context, 256 output, temperature 0, seed 42, mmap enabled. Performance-profile experiments are separate; their faster settings are not silently adopted.', '',
             '## Results', '']
    ledger = []
    for backend, batch in batches.items():
        rows = batch['trials']
        groups = {}
        for stage in ('reliability', 'new_baseline', 'information'):
            subset = [r for r in rows if r['stage'] == stage]
            arms = sorted({r['intervention'] if stage == 'reliability' else r['policy'] for r in subset})
            groups[stage] = {arm: aggregate([r for r in subset if (r['intervention'] if stage == 'reliability' else r['policy']) == arm]) for arm in arms}
        groups['new_baseline_by_family'] = {family: aggregate([r for r in rows if r['stage'] == 'new_baseline' and r['family'] == family]) for family in sorted({r['family'] for r in rows if r['stage'] == 'new_baseline'})}
        summary['batches'][backend] = {'batch_id': batch['batch_id'], 'status': batch['status'], 'attempted': len(rows),
            'planned': batch['protocol']['planned_trials'], 'model': batch.get('model'), 'model_settings': batch.get('model_settings'),
            'model_calls': batch['total_model_calls'], 'reported_tokens': batch['total_reported_tokens'],
            'audit_verified': bool(audits[backend] and audits[backend]['all_verified']),
            'session_cleanup': batch.get('session_cleanup'), 'refresh_count': batch.get('refresh_count'), 'groups': groups}
        if backend != 'scripted':
            comparison = paired(rows)
            eager = paired(rows, reference='eager')
            incremental = (eager['reads_fraction_saved_on_successful_pairs'] is not None and eager['reads_fraction_saved_on_successful_pairs'] >= .1 and eager['observed_reliability_preserved'] and eager['successful_pairs'] >= 10)
            summary['decisions'][backend] = {'vs_conservative': comparison, 'vs_eager_bundle': eager,
                'dependency_selection_incremental_read_benefit': incremental,
                'overall': 'PASS_SMALL_ENGINEERING_SCREEN_NEEDS_EXTERNAL_VALIDATION' if comparison['screening_decision'] == 'PASS_EFFICIENCY_SCREEN' and incremental else
                           'INCONCLUSIVE_OR_NO_GO_SEE_PAIRED_EVIDENCE'}
        lines.extend([f'### {backend}', '', '```json', json.dumps(summary['batches'][backend], indent=2), '```', ''])
        if backend in summary['decisions']:
            lines.extend(['```json', json.dumps(summary['decisions'][backend], indent=2), '```', ''])
        for row in rows:
            ledger.append({'backend': backend, 'run_id': row['run_id'], 'scenario': row['scenario_id'], 'family': row['family'],
                'stage': row['stage'], 'policy': row['policy'], 'intervention': row['intervention'], 'operational_failure': row['api_failed'],
                'strict_completed': row['contract']['strict_contract_pass'] and not row['api_failed'],
                'physical_goal': row['score']['oracle_goal_achieved'], 'argument_compliance': row['contract']['report_arguments_compliant'],
                'critical_attempts': row['contract']['critical_prerequisite_violations'], 'model_calls': row['model_metrics']['calls'],
                'seconds': row['wall_seconds'], 'eligible_reads': row['score']['sensor_backend_reads'],
                'mandatory_reads': row['score']['mandatory_sensor_reads'], 'system_reports': row['score']['system_reports'],
                'system_verifications': row['score']['automatic_verifications']})
    lines.extend(['## Interpretation and limits', '',
        'All attempted tasks remain in reliability denominators. Efficiency comparisons use only pairs where both arms strictly completed, list excluded cases and require at least 10/12 such pairs. Family-clustered bootstrap intervals use 1,000 resamples with seed 20261022 and are descriptive, not safety guarantees or powered model comparisons. Aborted tasks never earn optimization credit.', '',
        'The acceptance screen requires preserved observed critical-contract metrics plus >=10% paired time reduction or >=20% model-call reduction against conservative caching, with a positive lower descriptive interval bound. Dependency selection additionally needs >=10% fewer eligible reads than eager bundling without worse contract completion. If only the shared composite API helps, credit bundling; do not claim dependency reasoning caused it.', '',
        'The state and original score share a trusted simulation process; the agent has a separate allowlisted IPC channel and cannot query the evaluator. The read-back auditor reconstructs state and counts from saved records with separate code, but this is not independent physical verification or a formal security sandbox. There are no ROS actuator calls, real collisions, contact dynamics, cameras or physical grasps.', '',
        'The scripted planner is an essential simpler comparator. Success on these small workflows does not establish a need for an LLM or research novelty. A negative/inconclusive JTVR outcome is a reason to simplify or design a separately justified follow-up, not silently tune on these evaluation cases.', '',
        'No episodic-memory or Gazebo claims are made. Memory needs tasks with useful historical dependence and fixed-example controls. A later simulator integration still requires robot models, controllers, skills and physically meaningful measurements.', '',
        '## Every failed or repaired live attempt', ''])
    for backend, batch in batches.items():
        if backend == 'scripted':
            continue
        for row in batch['trials']:
            if row['api_failed'] or not row['contract']['strict_contract_pass'] or row['orchestrator_recovery']:
                lines.extend([f'### {backend} {row["scenario_id"]} {row["intervention"]}/{row["policy"]}', '', '```json',
                              json.dumps(row, indent=2), '```', ''])
    lines.extend(['## Evidence and reproduction', '',
        'Every run includes result, oracle and metadata files. Live Phoenix traces and read-back audits are included. Source snapshots, the frozen plan/manifest, retrospective analysis, local diagnostics and resource samples are included. Tool descriptions and full ordered backend observations are preserved in source and oracle files. OAuth credentials, .env, registration, browser state, model weights and virtual environments are excluded. Runtime JSON evidence is scanned before packaging.', ''])
    (CAMPAIGN / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (CAMPAIGN / 'REVIEW_REPORT.md').write_text('\n'.join(lines) + '\n')
    if ledger:
        with (CAMPAIGN / 'trials.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(ledger[0]))
            writer.writeheader()
            writer.writerows(ledger)
    evidence_root = CAMPAIGN / 'evidence/runs'
    runtime = []
    for batch in batches.values():
        ids = [batch['batch_id']] + [r['run_id'] for r in batch['trials']]
        for identifier in ids:
            for source in run_dir(identifier).rglob('*.json'):
                destination = evidence_root / identifier / source.relative_to(run_dir(identifier))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                runtime.append(destination)
    import re
    forbidden = re.compile(r'"(?:access_token|refresh_token|id_token|authorization|client_secret)"\s*:|Bearer\s+[A-Za-z0-9_.-]{16,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}', re.I)
    runtime += list(CAMPAIGN.glob('*.json')) + [CAMPAIGN / 'REVIEW_REPORT.md']
    flagged = [str(p.relative_to(CAMPAIGN)) for p in runtime if forbidden.search(p.read_text(errors='replace'))]
    (CAMPAIGN / 'privacy-scan.json').write_text(json.dumps({'flagged_paths': flagged, 'files_scanned': len(runtime)}, indent=2) + '\n')
    if flagged:
        raise RuntimeError('Runtime evidence flagged; inspect privately before packaging')
    excluded = {'supervisor.log', 'supervisor-status.json', 'campaign.json', 'report.log', 'monitor.stop', 'artifact-manifest.json'}
    files = [p for p in CAMPAIGN.rglob('*') if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
    manifest = {str(p.relative_to(CAMPAIGN)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    path = CAMPAIGN / 'artifact-manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    archive = CAMPAIGN.parent / 'ROSA_PHASE4_V2_EVIDENCE.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in files + [path]:
            bundle.write(path, path.relative_to(CAMPAIGN))
    print(json.dumps({'phase4_complete': complete, 'report': str(CAMPAIGN / 'REVIEW_REPORT.md'), 'archive': str(archive)}, indent=2))
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
