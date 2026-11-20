"""Analysis-only censoring. Never edit retained scorer columns or replay a task."""
from datetime import datetime

NOT_EVALUABLE = 'NOT_EVALUABLE'
COMPONENTS = ('selection_correct', 'execution_correct', 'report_correct', 'goal_correct')

def censor_class(row):
    supplied = row.get('analysis_failure_observation')
    if supplied is not None:
        if supplied.get('surface') not in ('HTTP', 'IN_STREAM', 'TRANSPORT', 'TIMEOUT'):
            raise ValueError('unclassified_failure_surface')
        if supplied.get('completed_response_in_failed_call') is not False:
            return None
        activity = supplied.get('tool_executions_before_failure', 0) or supplied.get('native_operations_before_failure', 0) or supplied.get('dispatches_before_failure', 0)
        return 'INFRA_CENSORED_POST_ACTION' if activity else 'INFRA_CENSORED_PRE_OUTPUT'
    error = row.get('error') or {}
    events = row.get('inference', {}).get('events', [])
    failed_calls = [e for e in events if e.get('status') in ('UNRETURNED', 'EXTERNAL_FAILURE')]
    if not failed_calls:
        return None
    if not error and row.get('infrastructure_recovered'):
        # A later successful retry must not make us guess when the failed call occurred.
        raise ValueError('recovered_failure_requires_explicit_pre_failure_activity_record')
    if row.get('score', {}).get('budget_exhaustion') or row.get('timeout_fired'):
        return None
    if error.get('type') not in ('SafeError', 'TimeoutError', 'URLError', 'ConnectionError', 'OSError'):
        return None
    snapshot = row.get('snapshot', {})
    activity = bool(row.get('actor_records') or snapshot.get('operations') or row.get('tool_inputs')
                    or row.get('score', {}).get('dispatches', 0))
    return 'INFRA_CENSORED_POST_ACTION' if activity else 'INFRA_CENSORED_PRE_OUTPUT'

def annotate(row):
    classification = censor_class(row)
    return dict(trial_id=row['id'], censor_class=classification or 'EVALUABLE',
        component_columns={key: NOT_EVALUABLE if classification else row.get('score', {}).get(key)
                           for key in COMPONENTS},
        primary_correct_v2=NOT_EVALUABLE if classification else bool(row['primary_pass']),
        primary_correct_v3=bool(row['primary_pass']) if not classification else False,
        raw_primary_pass_unchanged=row['primary_pass'],
        observer_record_retained=bool(row.get('observer_records')))

def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def pair_gap(first_spans, second_spans, minutes=30):
    starts = [min(timestamp(s['start_time']) for s in spans) for spans in (first_spans, second_spans)]
    gap = abs((starts[1]-starts[0]).total_seconds())
    return dict(timestamp_basis='earliest retained local trace start per arm; absolute start-to-start gap',
                seconds=gap, threshold_minutes=minutes, flagged=gap > minutes*60)
