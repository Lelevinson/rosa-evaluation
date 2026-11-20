"""Read back all40 traces, preserving the original accounting exception."""
import json
import time
from .recover_evidence import DESTINATION,ROOT,write
from .tracing import PROJECT


def main():
    import httpx
    from phoenix.client import Client
    original=ROOT/'artifacts/output-budget-v1-20261022'
    previous=ROOT/'artifacts/output-budget-v1-followup-20261022'
    rows=[]
    with httpx.Client(base_url='http://127.0.0.1:6006',timeout=60,trust_env=False) as http:
        client=Client(http_client=http)
        for campaign,project in ((original,'rosa-output-budget-v1-20261022'),
                (previous,'rosa-output-budget-v1-followup-20261022'),(DESTINATION,PROJECT)):
            status=json.loads((campaign/'gazebo/ollama/result.json').read_text())
            for row in status['trials']:
                folder=campaign/'gazebo/ollama'/row['run_id']
                local=json.loads((folder/'trace.json').read_text())['spans']
                expected={s['context']['span_id'].removeprefix('0x') for s in local}
                for attempt in range(4):
                    trace=client.spans.get_spans(project_identifier=project,trace_ids=[row['trace_id']],limit=10000)
                    received={s['context']['span_id'].removeprefix('0x') for s in trace}
                    if expected==received:break
                    if attempt<3:time.sleep(2)
                closed=bool(trace) and all(s.get('end_time') and (not s.get('parent_id') or
                    s['parent_id'].removeprefix('0x') in received) for s in trace)
                exception=(campaign==original and row['audit']['errors']==['completed_usage_records'])
                rows.append({'run_id':row['run_id'],'project':project,'local_spans':len(expected),
                    'persisted_spans':len(received),'exact_ids_match':expected==received,
                    'closed_tree':closed,'original_local_audit_pass':row['audit']['pass'],
                    'preserved_accounting_exception':exception,
                    'pass':expected==received and closed and (row['audit']['pass'] or exception)})
                target=DESTINATION/'recovered-evidence'/row['run_id']/'phoenix-trace.json' if campaign!=DESTINATION else folder/'phoenix-trace.json'
                write(target,trace)
    result={'pass':len(rows)==40 and all(r['pass'] for r in rows),'rows':rows,
            'original_metadata_accounting_exception_preserved':1}
    write(DESTINATION/'gazebo-phoenix-ollama.json',result)
    print(json.dumps({'pass':result['pass'],'traces':len(rows)}),flush=True)
    if not result['pass']:raise SystemExit(1)


if __name__=='__main__':main()

