"""Qwen-specific transport observations; unchanged human adjudication rules."""
from common import ROOT, ADJUDICATION, read, write
from adjudication import VERSION, adjudicate


def empty_bundle():
    rubric = read(ADJUDICATION / 'LEV_ACTUAL_REVIEW_BOUND.json')['rubric_sha256']
    return {'version': VERSION, 'rubric_sha256': rubric, 'records': []}


def journal_progress(folder, inference, inv, meter, actor, transport, start, timeout):
    saved = folder / 'failure-observations.json'
    observations = read(saved) if saved.exists() else []
    for metadata in transport.error_metadata_records[start + len(observations):]:
        observations.append({'metadata': metadata, 'analysis_failure_observation': {
            'surface': metadata['failure_surface'], 'completed_response_in_failed_call': False,
            'tool_executions_before_failure': len(meter.tool_inputs),
            'native_operations_before_failure': len(actor.records)}})
    write(folder.relative_to(ROOT) / 'failure-observations.json', observations)
    write(folder.relative_to(ROOT) / 'inference-progress.json', {
        'inference': inference, 'snapshot': inv.snapshot(),
        'error_metadata': transport.error_metadata_records[start:]})


def freeze_raw_result(row, folder, transport, start):
    row['legacy_primary_pass_role'] = 'DIAGNOSTIC_ONLY_USE_APPROVED_ADJUDICATION'
    row['error_metadata'] = transport.error_metadata_records[start:]
    if (folder / 'failure-observations.json').exists():
        events = read(folder / 'failure-observations.json')
        if events and not row.get('timeout_fired') and not row.get('score', {}).get('budget_exhaustion'):
            row['analysis_failure_observation'] = events[0]['analysis_failure_observation']


def evaluate_progress(row):
    bundle = empty_bundle()
    return adjudicate(row, bundle, bundle['rubric_sha256'])
