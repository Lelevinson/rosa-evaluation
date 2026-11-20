"""Read actual M1 Phoenix spans using the existing isolated Phoenix environment."""
import argparse
import json
from pathlib import Path
import time

PROJECT = 'rosa-macro-module-v1-20261027'
ROOT_SPAN = 'rosa.macro.module.validation'


def main():
    import httpx
    from phoenix.client import Client
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=Path, required=True)
    folder = parser.parse_args().folder
    local = json.loads((folder / 'trace.json').read_text())['spans']
    root = next(s for s in local if s['name'] == ROOT_SPAN)
    trace_id = root['context']['trace_id'].removeprefix('0x')
    expected = {s['context']['span_id'].removeprefix('0x') for s in local}
    with httpx.Client(base_url='http://127.0.0.1:6006', timeout=15, trust_env=False) as http:
        client = Client(http_client=http)
        for _ in range(8):
            spans = client.spans.get_spans(project_identifier=PROJECT, trace_ids=[trace_id], limit=10000)
            received = {s['context']['span_id'].removeprefix('0x') for s in spans}
            if received == expected: break
            time.sleep(0.5)
    closed = bool(spans) and all(s.get('end_time') and (not s.get('parent_id') or
        s['parent_id'].removeprefix('0x') in received) for s in spans)
    result = {'pass': expected == received and closed, 'exact_span_ids': expected == received,
        'closed_tree': closed, 'local_spans': len(expected), 'persisted_spans': len(received),
        'trace_id': trace_id, 'project': PROJECT}
    (folder / 'phoenix-trace.json').write_text(json.dumps(spans, indent=2))
    (folder / 'phoenix-audit.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    if not result['pass']: raise SystemExit(1)


if __name__ == '__main__': main()
