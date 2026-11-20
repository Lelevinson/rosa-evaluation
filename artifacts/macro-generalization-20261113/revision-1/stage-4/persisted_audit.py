"""Read one live trial's actual Phoenix span IDs before advancing."""
import argparse
import json
import time
from pathlib import Path
import httpx
from phoenix.client import Client

def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);folder=parser.parse_args().folder
    local=json.loads((folder/'trace.json').read_text())['spans']
    root=next(s for s in local if s['name']=='g1.sol.heldout')
    trace_id=root['context']['trace_id'].removeprefix('0x')
    expected={s['context']['span_id'].removeprefix('0x') for s in local}
    with httpx.Client(base_url='http://127.0.0.1:6006',timeout=15,trust_env=False) as http:
        client=Client(http_client=http)
        for _ in range(8):
            spans=client.spans.get_spans(project_identifier='rosa-g1-sol-heldout-20261119',trace_ids=[trace_id],limit=10000)
            received={s['context']['span_id'].removeprefix('0x') for s in spans}
            if received==expected:break
            time.sleep(.5)
    closed=bool(spans) and all(s.get('end_time') and (not s.get('parent_id') or
        s['parent_id'].removeprefix('0x') in received) for s in spans)
    result={'pass':expected==received and closed,'exact_span_ids':expected==received,'closed_tree':closed,
        'local_spans':len(expected),'persisted_spans':len(received),'trace_id':trace_id}
    (folder/'phoenix-trace.json').write_text(json.dumps(spans,indent=2)+'\n')
    (folder/'phoenix-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['pass']:raise SystemExit(1)

if __name__=='__main__':main()
