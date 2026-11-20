"""Verify Phoenix ingestion and read-back without ROSA, ROS, or an LLM."""
import json
import time
from uuid import uuid4

from experiments.config import phoenix_url, run_dir, tool_output_dir
from .inspect_trace import fetch


def main():
    from phoenix.client import Client
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    run_id = str(uuid4())
    metadata = {'run_id': run_id, 'mode': 'phoenix-smoke', 'model': 'none'}
    output = run_dir(run_id)
    output.mkdir(parents=True)
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    provider = TracerProvider(resource=Resource.create({'openinference.project.name': 'rosa-smoke'}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint=phoenix_url() + '/v1/traces', headers={}, timeout=10)))
    try:
        with provider.get_tracer(__name__).start_as_current_span('phoenix.smoke') as span:
            span.set_attribute('openinference.span.kind', 'CHAIN')
            span.set_attribute('metadata', json.dumps(metadata))
            span.set_attribute('session.id', run_id)
            span.set_attribute('input.value', 'local smoke')
            span.set_attribute('output.value', 'received')
        if not provider.force_flush(timeout_millis=15000):
            raise RuntimeError('Smoke span export timed out.')
    finally:
        provider.shutdown()
    client = Client(base_url=phoenix_url())
    spans = []
    for _ in range(30):
        spans = fetch(client, 'rosa-smoke', run_id)
        if spans:
            break
        time.sleep(0.2)
    if len(spans) != 1 or spans[0]['name'] != 'phoenix.smoke':
        raise RuntimeError('Phoenix smoke span was not read back; ingestion is unverified.')
    export = tool_output_dir(run_id, 'phoenix') / 'smoke.json'
    export.parent.mkdir(parents=True, exist_ok=True)
    export.write_text(json.dumps({'run_id': run_id, 'spans': spans}, indent=2, default=str) + '\n')
    result = {**metadata, 'passed': True, 'export': str(export)}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
