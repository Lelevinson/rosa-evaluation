"""Independent persisted-span readback in the separate Phoenix environment."""
import argparse
import json
from pathlib import Path
import time
from .tracing import PROJECT
from .runner import DESTINATION, write


def main():
    from phoenix.client import Client
    import httpx
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',choices=('validation','mock','gazebo'),required=True)
    parser.add_argument('--backend',choices=('siwc','ollama'))
    args=parser.parse_args()
    rows=[]
    paths=sorted((DESTINATION/args.phase).glob((args.backend or '*')+'/result.json'))
    with httpx.Client(base_url='http://127.0.0.1:6006',timeout=60,trust_env=False) as http:
        client=Client(http_client=http)
        for path in paths:
            status=json.loads(path.read_text())
            for row in status['trials']:
                local=json.loads((path.parent/row['run_id']/'trace.json').read_text())['spans']
                expected={s['context']['span_id'].removeprefix('0x') for s in local}
                for attempt in range(4):
                    trace=client.spans.get_spans(project_identifier=PROJECT,trace_ids=[row['trace_id']],limit=10000)
                    received={s['context']['span_id'].removeprefix('0x') for s in trace}
                    if expected==received:
                        break
                    if attempt<3:
                        time.sleep(2)
                closed=bool(trace) and all(s.get('end_time') and (not s.get('parent_id') or
                    s['parent_id'].removeprefix('0x') in received) for s in trace)
                rows.append({'backend':row['backend'],'run_id':row['run_id'],'local_spans':len(expected),
                    'persisted_spans':len(received),'exact_ids_match':expected==received,'closed_tree':closed,
                    'local_audit_pass':row['audit']['pass']})
                write(path.parent/row['run_id']/'phoenix-trace.json',trace)
    result={'pass':bool(rows) and all(r['exact_ids_match'] and r['closed_tree'] and r['local_audit_pass'] for r in rows),
        'phase':args.phase,'rows':rows}
    write(DESTINATION/(args.phase+'-phoenix-'+(args.backend or 'all')+'.json'),result)
    print(json.dumps({'pass':result['pass'],'traces':len(rows),'phase':args.phase}),flush=True)
    if not result['pass']:
        raise SystemExit(1)


if __name__=='__main__':
    main()

