"""Query actual persisted spans using the isolated pinned Phoenix environment."""
import json
from pathlib import Path
import time
import httpx
from phoenix.client import Client

ROOT=Path(__file__).resolve().parent
PROJECT='rosa-g1-ai-authored-controls-20261113'

def main():
    results=[]
    with httpx.Client(base_url='http://127.0.0.1:6006',timeout=15,trust_env=False) as http:
        client=Client(http_client=http)
        for folder in sorted((ROOT/'trials').iterdir()):
            local=json.loads((folder/'trace.json').read_text())['spans']
            root=next(s for s in local if s['name']=='g1.scripted.control')
            trace_id=root['context']['trace_id'].removeprefix('0x')
            expected={s['context']['span_id'].removeprefix('0x') for s in local}
            for _ in range(8):
                spans=client.spans.get_spans(project_identifier=PROJECT,trace_ids=[trace_id],limit=10000)
                received={s['context']['span_id'].removeprefix('0x') for s in spans}
                if received==expected:break
                time.sleep(.5)
            closed=bool(spans) and all(s.get('end_time') and (not s.get('parent_id') or
                s['parent_id'].removeprefix('0x') in received) for s in spans)
            result={'id':folder.name,'pass':expected==received and closed,'exact_span_ids':expected==received,
                    'closed_tree':closed,'local_spans':len(expected),'persisted_spans':len(received),
                    'trace_id':trace_id,'project':PROJECT}
            (folder/'phoenix-trace.json').write_text(json.dumps(spans,indent=2)+'\n')
            (folder/'phoenix-audit.json').write_text(json.dumps(result,indent=2)+'\n')
            results.append(result)
            if not result['pass']:break
    summary={'pass':len(results)==132 and all(r['pass'] for r in results),'trials':len(results),
             'local_spans':sum(r['local_spans'] for r in results),
             'persisted_spans':sum(r['persisted_spans'] for r in results),'rows':results}
    (ROOT/'persisted-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'}))
    if not summary['pass']:raise SystemExit(1)

if __name__=='__main__':main()
