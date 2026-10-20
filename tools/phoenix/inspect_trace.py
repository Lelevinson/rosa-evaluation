"""Read/export Phoenix spans; derive a small dispatch summary, never a second recorder."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from experiments.config import phoenix_project, phoenix_url, tool_output_dir


def summarize(spans):
    by_id = {s['context']['span_id']: s for s in spans}
    roots = [s for s in spans if s['name'] == 'rosa.run' and not s['parent_id']]
    complete = len(roots) == 1 and all(
        s.get('end_time') and (not s['parent_id'] or s['parent_id'] in by_id) for s in spans)
    tools = []
    for span in sorted(spans, key=lambda s: (s['start_time'], s['context']['span_id'])):
        if span['span_kind'] != 'TOOL':
            continue
        ancestor = span['parent_id']
        scope = 'agent'
        seen = set()
        while ancestor:
            if ancestor in seen or ancestor not in by_id:
                scope = 'unknown'
                break
            seen.add(ancestor)
            parent = by_id[ancestor]
            if parent['span_kind'] == 'TOOL':
                scope = 'internal'
                break
            ancestor = parent['parent_id']
        attrs = span['attributes']
        tools.append({'name': span['name'], 'span_id': span['context']['span_id'],
            'scope': scope, 'status': span['status_code'],
            'input': attrs.get('input.value'), 'output': attrs.get('output.value'),
            'duration_seconds': (datetime.fromisoformat(span['end_time']) -
                                 datetime.fromisoformat(span['start_time'])).total_seconds(),
            'events': span['events']})
    requested = []
    for span in sorted(spans, key=lambda s: s['start_time']):
        if span['span_kind'] == 'LLM':
            requested.extend(value for key, value in span['attributes'].items()
                if key.startswith('llm.output_messages.') and key.endswith('tool_call.function.name'))
    return {'span_count': len(spans), 'run_status': roots[0]['status_code'] if roots else 'INCOMPLETE',
            'trace_complete': complete,
            'count_is_lower_bound': not complete,
            'agent_tool_dispatches_observed': sum(t['scope'] == 'agent' for t in tools),
            'internal_tool_dispatches_observed': sum(t['scope'] == 'internal' for t in tools),
            'llm_calls': sum(s['span_kind'] == 'LLM' for s in spans),
            'llm_requested_tools': requested, 'tools_in_start_order': tools}


def fetch(client, project, run_id):
    return client.spans.get_spans(project_identifier=project,
        attributes={'metadata.run_id': run_id}, limit=10000)


def main():
    from phoenix.client import Client
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default=phoenix_project())
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    spans = fetch(Client(base_url=phoenix_url()), args.project, args.run_id)
    result = {'run_id': args.run_id, 'summary': summarize(spans), 'spans': spans}
    args.output = args.output or tool_output_dir(args.run_id, 'phoenix') / 'trace.json'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps(result['summary'], indent=2, default=str))
    print(f'Export: {args.output}')


if __name__ == '__main__':
    main()
