from contextlib import contextmanager
import json
from experiments.reliability_v1.tracing import audit

PROJECT = 'rosa-workflow-reference-v1-20261022'


@contextmanager
def trace_trial(metadata, output):
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    provider = TracerProvider(resource=Resource.create({
        'service.name': PROJECT, 'openinference.project.name': PROJECT}))
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint='http://127.0.0.1:6006/v1/traces', timeout=5)))
    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=provider)
    tracer = provider.get_tracer(PROJECT)
    try:
        with tracer.start_as_current_span('rosa.workflow.live.trial') as root:
            root.set_attribute('openinference.span.kind', 'AGENT')
            root.set_attribute('metadata', json.dumps(metadata))
            yield tracer, root
    finally:
        flushed = provider.force_flush(timeout_millis=10000)
        instrumentor.uninstrument()
        output.write_text(json.dumps({'export_flush_completed': flushed,
            'spans': [json.loads(s.to_json()) for s in exporter.get_finished_spans()]}, indent=2) + '\n')
        provider.shutdown()
        if not flushed:
            raise RuntimeError('trace_export_flush_incomplete')
