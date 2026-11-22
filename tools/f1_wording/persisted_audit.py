"""F1 copy of the frozen G1 persisted trace audit (revision-1/stage-4/persisted_audit.py).
Only the Phoenix project and root span name are parameters. Run with the Phoenix env.
Usage: persisted_audit.py <trial folder> <project> <root span>"""
import json
import sys
import time
from pathlib import Path
import httpx
from phoenix.client import Client


def main():
    folder, project, root_span = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    local = json.loads((folder / 'trace.json').read_text())['spans']
    root = next(s for s in local if s['name'] == root_span)
    trace_id = root['context']['trace_id'].removeprefix('0x')
    expected = {s['context']['span_id'].removeprefix('0x') for s in local}
    spans, received = [], set()
    with httpx.Client(base_url='http://127.0.0.1:6006', timeout=15, trust_env=False) as http:
        client = Client(http_client=http)
        for _ in range(8):
            spans = client.spans.get_spans(project_identifier=project, trace_ids=[trace_id], limit=10000)
            received = {s['context']['span_id'].removeprefix('0x') for s in spans}
            if received == expected:
                break
            time.sleep(.5)
    closed = bool(spans) and all(s.get('end_time') and (not s.get('parent_id') or
                                 s['parent_id'].removeprefix('0x') in received) for s in spans)
    result = {'pass': expected == received and closed, 'exact_span_ids': expected == received, 'closed_tree': closed,
              'local_spans': len(expected), 'persisted_spans': len(received), 'trace_id': trace_id, 'project': project}
    (folder / 'phoenix-trace.json').write_text(json.dumps(spans, indent=2) + '\n')
    (folder / 'phoenix-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    if not result['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
