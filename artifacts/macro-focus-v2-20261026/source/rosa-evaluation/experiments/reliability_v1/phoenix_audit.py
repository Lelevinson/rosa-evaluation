"""Independent Phoenix read-back using its separate client environment."""
import argparse
import json
from pathlib import Path


def main():
    from phoenix.client import Client
    import httpx
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    with httpx.Client(base_url='http://127.0.0.1:6006', timeout=60, trust_env=False) as http:
        client = Client(http_client=http)
        if args.controls:
            spans = client.spans.get_spans(project_identifier='rosa-reliability-v1-20261022', limit=10000)
            rows = []
            for trace_id in sorted({s['context']['trace_id'] for s in spans}):
                trace = [s for s in spans if s['context']['trace_id'] == trace_id]
                ids = {s['context']['span_id'] for s in trace}
                complete = all(s.get('end_time') and (not s.get('parent_id') or s['parent_id'] in ids) for s in trace)
                rows.append({'trace_id': trace_id, 'persisted_spans': len(trace), 'closed_tree': complete})
        else:
            rows = []
            for status_path in sorted(args.destination.glob('*/result.json')):
                status = json.loads(status_path.read_text())
                for row in status['trials']:
                    trace = client.spans.get_spans(project_identifier='rosa-reliability-v1-20261022',
                                                  trace_ids=[row['trace_id']], limit=10000)
                    local = json.loads((status_path.parent / row['run_id'] / 'trace.json').read_text())['spans']
                    expected = {s['context']['span_id'].removeprefix('0x') for s in local}
                    received = {s['context']['span_id'].removeprefix('0x') for s in trace}
                    closed = all(s.get('end_time') and (not s.get('parent_id') or s['parent_id'].removeprefix('0x') in received) for s in trace)
                    result = {'backend': row['backend'], 'run_id': row['run_id'],
                              'local_spans': len(expected), 'persisted_spans': len(received),
                              'exact_span_ids_match': expected == received, 'closed_tree': closed}
                    rows.append(result)
                    (status_path.parent / row['run_id'] / 'phoenix-trace.json').write_text(json.dumps(trace, indent=2, default=str))
    result = {'pass': bool(rows) and all(r['closed_tree'] and r.get('exact_span_ids_match', True) for r in rows), 'traces': rows}
    args.destination.mkdir(parents=True, exist_ok=True)
    (args.destination / ('control-phoenix-audit.json' if args.controls else 'phoenix-audit.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps({'pass': result['pass'], 'traces': len(rows)}))
    if not result['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
