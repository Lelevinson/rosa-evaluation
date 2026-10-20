"""Integration checks against the real local Phoenix API and unchanged ROSA APIs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from uuid import uuid4

from .inspect_trace import fetch, summarize
from .config import ROOT, load_config, resolve_path, phoenix_url, validation_dir


def checkout(name):
    # Only the ROSA integration checks need the repository's checkout settings.
    return resolve_path(load_config(ROOT)['checkouts'][name], ROOT)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', action='append', help='Checkout to validate; repeat for comparisons. Default: research.')
    args = parser.parse_args()
    variants = args.variant or ['research']
    for variant in variants:
        if not checkout(variant).is_dir():
            parser.error(f'Missing checkout for {variant!r}: {checkout(variant)}')
    from phoenix.client import Client
    client = Client(base_url=phoenix_url())
    project = 'rosa-validation-' + str(uuid4())[:8]
    output = validation_dir(project, 'phoenix')
    output.mkdir(parents=True)
    records = []
    cases = ['success', 'execution-error', 'validation-error', 'reported-error', 'nested', 'unknown-tool']
    for variant in variants:
        for case in cases + ['success-off', 'interrupted']:
            off = case == 'success-off'
            cmd = [str(ROOT / 'run.sh'), variant, '--mode', 'controlled', '--case',
                   'success' if off else case, '--project', project, '--tracing', 'off' if off else 'on']
            env = dict(os.environ, OTEL_BSP_SCHEDULE_DELAY='100')
            interrupted = False
            try:
                process = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True,
                                         text=True, timeout=8 if case == 'interrupted' else 30)
                stdout, stderr, returncode = process.stdout, process.stderr, process.returncode
            except subprocess.TimeoutExpired as error:
                interrupted = True
                stdout = (error.stdout or b'').decode()
                stderr = (error.stderr or b'').decode()
                returncode = 'timeout'
            (output / f'{variant}-{case}.jsonl').write_text(stdout)
            (output / f'{variant}-{case}.stderr').write_text(stderr)
            messages = [json.loads(line) for line in stdout.splitlines() if line.startswith('{')]
            assert messages, (variant, case, stdout, stderr)
            run_id = messages[0]['run_id']
            spans = []
            for _ in range(40):
                spans = fetch(client, project, run_id)
                if off or interrupted or any(s['name'] == 'rosa.run' for s in spans):
                    break
                time.sleep(0.1)
            summary = summarize(spans)
            result = messages[-1]
            assert result['rosa_source'].startswith(str(checkout(variant) / 'src'))
            if off:
                assert not spans and result['body_entries'] == ['fixture_read', 'fixture_read']
                assert returncode == 0 and result['answer'] == 'DONE'
            elif interrupted:
                assert spans and not summary['trace_complete'] and summary['count_is_lower_bound']
            else:
                assert summary['trace_complete'], (variant, case, summary)
                tools = summary['tools_in_start_order']
                expected = 2 if case == 'success' else 1
                assert summary['agent_tool_dispatches_observed'] == expected, summary
                assert summary['llm_calls'] == (3 if case == 'success' else 1 if 'error' in case and case != 'reported-error' else 2), summary
                if case in ('execution-error', 'validation-error'):
                    assert returncode == 1 and tools[0]['status'] == 'ERROR' and tools[0]['events']
                    assert len(result['body_entries']) == (0 if case == 'validation-error' else 1)
                else:
                    assert returncode == 0
                if case == 'reported-error':
                    assert tools[0]['status'] == 'OK' and 'error' in tools[0]['output']
                if case == 'nested':
                    assert summary['internal_tool_dispatches_observed'] == 1
                    assert result['body_entries'] == ['fixture_nested', 'fixture_read']
                assert all(t['input'] is not None and t['duration_seconds'] >= 0 for t in tools)
            record = {'variant': variant, 'case': case, 'run_id': run_id,
                      'returncode': returncode, 'summary': summary, 'spans': spans}
            records.append(record)
            print(f'PASS {variant} {case}: dispatches={summary["agent_tool_dispatches_observed"]}, complete={summary["trace_complete"]}', flush=True)
    (output / 'verified.json').write_text(json.dumps(records, indent=2, default=str) + '\n')
    print(f'Validated {len(records)} runs; {output}')


if __name__ == '__main__':
    main()
