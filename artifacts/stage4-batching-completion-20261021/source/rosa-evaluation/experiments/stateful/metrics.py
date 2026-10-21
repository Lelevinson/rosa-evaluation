"""Descriptive, scenario-clustered summaries; not a model parity significance test."""
from collections import defaultdict
import random
import statistics


def quantile(values, fraction):
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * fraction
    low = int(position)
    return values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (position - low)


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['policy']].append(row)
    result = {}
    for policy, items in groups.items():
        clusters = defaultdict(list)
        for item in items:
            clusters[item['scenario_id']].append(float(item['score']['correct_terminal_handling'] and not item['api_failed']))
        means = [statistics.mean(values) for values in clusters.values()]
        rng = random.Random(20261021)
        samples = [statistics.mean(rng.choices(means, k=len(means))) for _ in range(1000)]
        result[policy] = {'attempted': len(items), 'distinct_scenarios': len(clusters),
            'correct_terminal_handling': sum(item['score']['correct_terminal_handling'] and not item['api_failed'] for item in items),
            'verified_goal_successes': sum(item['score']['verified_task_success'] and not item['api_failed'] for item in items),
            'false_success_claims': sum(bool(item['score']['false_success_claim']) for item in items),
            'unsupported_success_claims': sum(bool(item['score']['unsupported_success_claim']) for item in items),
            'api_failures': sum(item['api_failed'] for item in items),
            'unsafe_executions': sum(item['score']['unsafe_executions'] for item in items),
            'prohibited_attempts': sum(item['score']['prohibited_action_attempts'] for item in items),
            'stale_observations': sum(item['score']['stale_observations_served'] for item in items),
            'eligible_sensor_reads': sum(item['score']['sensor_backend_reads'] for item in items),
            'mandatory_sensor_reads': sum(item['score']['mandatory_sensor_reads'] for item in items),
            'cache_hits': sum(item['score']['cache_hits'] for item in items),
            'llm_calls': sum(item['model_metrics']['calls'] for item in items),
            'median_wall_seconds': statistics.median(item['wall_seconds'] for item in items),
            'p95_wall_seconds': quantile([item['wall_seconds'] for item in items], .95),
            'terminal_handling_scenario_bootstrap_95': [quantile(samples, .025), quantile(samples, .975)]}
    matched = {(r['scenario_id'], r['repetition']): r for r in rows if r['policy'] == 'none'}
    paired = {}
    for policy in ('ttl', 'conservative'):
        pairs = [(matched[(r['scenario_id'], r['repetition'])], r) for r in rows
                 if r['policy'] == policy and (r['scenario_id'], r['repetition']) in matched]
        if pairs:
            paired[policy] = {'paired_trials': len(pairs),
                'distinct_scenarios': len({a['scenario_id'] for a, b in pairs}),
                'eligible_reads_saved': sum(a['score']['sensor_backend_reads'] - b['score']['sensor_backend_reads'] for a, b in pairs),
                'mandatory_read_delta': sum(b['score']['mandatory_sensor_reads'] - a['score']['mandatory_sensor_reads'] for a, b in pairs),
                'verified_success_delta': sum(int(b['score']['verified_task_success']) - int(a['score']['verified_task_success']) for a, b in pairs),
                'terminal_handling_delta': sum(int(b['score']['correct_terminal_handling'] and not b['api_failed']) -
                                               int(a['score']['correct_terminal_handling'] and not a['api_failed']) for a, b in pairs),
                'model_calls_saved': sum(a['model_metrics']['calls'] - b['model_metrics']['calls'] for a, b in pairs),
                'median_total_seconds_saved': statistics.median(a['wall_seconds'] - b['wall_seconds'] for a, b in pairs),
                'sensor_backend_ms_saved': sum(a['score']['sensor_backend_ms'] - b['score']['sensor_backend_ms'] for a, b in pairs),
                'cache_policy_ms': sum(b['score']['cache_policy_ms'] for a, b in pairs)}
    result['_paired_cache_comparisons'] = paired
    return result
