"""Bind approved metadata and analysis to the new trial path, without tool changes."""
from common import ROOT,STAGE3,read,write,ADJUDICATION
from adjudication import adjudicate,VERSION

def empty_bundle():
    rubric=read(ADJUDICATION/'LEV_ACTUAL_REVIEW_BOUND.json')['rubric_sha256']
    return {'version':VERSION,'rubric_sha256':rubric,'records':[]}

def journal_progress(folder,inference,inv,meter,actor,transport,metadata_start,timeout):
    snapshot=inv.snapshot()
    metadata=transport.error_metadata_records[metadata_start:]
    saved=read(folder/'failure-observations.json') if (folder/'failure-observations.json').exists() else []
    while len(saved)<len(metadata):
        entry=metadata[len(saved)]
        surface=entry['failure_surface']
        recognized=surface in ('HTTP','IN_STREAM','STREAM_ENDED','TIMEOUT','TRANSPORT')
        observation=None
        if recognized and not timeout['fired']:
            observation={'surface':'IN_STREAM' if surface=='STREAM_ENDED' else surface,
                'completed_response_in_failed_call':False,
                'tool_executions_before_failure':len(meter.tool_inputs),
                'native_operations_before_failure':len(actor.records)}
        saved.append({'metadata':entry,'analysis_failure_observation':observation})
    write(folder.relative_to(ROOT)/'failure-observations.json',saved)
    write(folder.relative_to(ROOT)/'inference-progress.json',{'inference':inference,'snapshot':snapshot,
        'error_metadata':metadata})

def freeze_raw_result(row,folder,transport,metadata_start):
    # Raw legacy flags are explicitly diagnostic. Effective judgments stay separate.
    row['legacy_primary_pass_role']='DIAGNOSTIC_ONLY_USE_APPROVED_ADJUDICATION'
    row['error_metadata']=transport.error_metadata_records[metadata_start:]
    if (folder/'failure-observations.json').exists():
        observed=read(folder/'failure-observations.json')
        actual=next((o['analysis_failure_observation'] for o in observed if o['analysis_failure_observation']),None)
        if actual is not None and not row.get('timeout_fired') and not row.get('score',{}).get('budget_exhaustion'):
            row['analysis_failure_observation']=actual

def evaluate_progress(row):
    bundle=empty_bundle()
    return adjudicate(row,bundle,bundle['rubric_sha256'])
