"""Run one unchanged ROSA checkout in one process with optional OTLP tracing."""
import argparse
import json
import os
from pathlib import Path
import sys
import platform
import subprocess
from importlib.metadata import version
from uuid import uuid4

from .tracing import trace_run
from .config import ROOT, rosa_checkout, phoenix_project, phoenix_url, run_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracing', choices=['on', 'off'], default='on')
    parser.add_argument('--project', default=phoenix_project())
    parser.add_argument('--model')
    parser.add_argument('--reasoning', choices=['default', 'on', 'off'], default='default')
    parser.add_argument('--base-url')
    parser.add_argument('--query', default='Use ros2_node_list to list the currently running ROS 2 nodes. Report the actual tool result, including any error.')
    args = parser.parse_args()
    rosa_root = rosa_checkout()
    # Prevent external LangSmith tracing inherited from an interactive shell.
    for key in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    if Path(sys.prefix).resolve() != (rosa_root.resolve() / '.venv').resolve():
        raise RuntimeError('Run with the selected checkout own .venv/bin/python.')
    source = rosa_root.resolve() / 'src'
    if 'rosa' in sys.modules:
        raise RuntimeError('ROSA was imported before source selection.')
    sys.path.insert(0, str(source))
    import rosa
    if not Path(rosa.__file__).resolve().is_relative_to(source):
        raise RuntimeError(f'Wrong ROSA source: {rosa.__file__}; expected {source}')
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    load_dotenv(rosa_root.resolve() / '.env')
    model = args.model or os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
    base_url = args.base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    metadata = {'run_id': str(uuid4()),
                'rosa_source': str(Path(rosa.__file__).resolve()),
                'python_prefix': sys.prefix, 'python_version': platform.python_version(),
                'rosa_commit': subprocess.check_output(['git', '-C', str(rosa_root), 'rev-parse', 'HEAD'], text=True).strip(),
                'langchain_version': version('langchain'), 'langchain_core_version': version('langchain-core'),
                'query': args.query, 'model': model,
                'reasoning': args.reasoning, 'ollama_base_url': base_url}
    metadata['tools'] = ({'phoenix': {'url': phoenix_url(), 'project': args.project}}
                         if args.tracing == 'on' else {})
    output = run_dir(metadata['run_id'])
    output.mkdir(parents=True)
    metadata['output_dir'] = str(output)
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata), flush=True)
    with trace_run(args.tracing == 'on', project=args.project, metadata=metadata, endpoint=phoenix_url() + '/v1/traces') as span:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model=model, base_url=base_url, temperature=0,
                         streaming=False, client_kwargs={'timeout': 120},
                         **({} if args.reasoning == 'default' else {'reasoning': args.reasoning == 'on'}))
        agent = rosa.ROSA(ros_version=2, llm=llm,
                          streaming=False, max_iterations=5, accumulate_chat_history=False)
        answer = agent.invoke(args.query)
        failed = (not answer or not answer.strip() or answer.startswith('An error occurred:')
                  or answer == 'Agent stopped due to max iterations.')
        if span is not None:
            metadata['trace_id'] = format(span.get_span_context().trace_id, '032x')
            span.set_attribute('input.value', args.query)
            span.set_attribute('output.value', answer or '')
            if failed:
                from opentelemetry.trace import Status, StatusCode
                span.set_status(Status(StatusCode.ERROR, answer or 'Empty ROSA answer'))
        result = {**metadata, 'answer': answer, 'api_failed': failed,
                  'tracing': args.tracing}
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
