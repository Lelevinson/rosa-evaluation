"""M1-only trace project; reuses the unchanged local auditor."""
from contextlib import contextmanager
import json
from experiments.reliability_v1.tracing import audit
from experiments.macro_focus_v2.runner import Meter

PROJECT = 'rosa-macro-module-v1-20261027'
ROOT_SPAN = 'rosa.macro.module.validation'


@contextmanager
def trace_check(output, metadata):
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
        with tracer.start_as_current_span(ROOT_SPAN) as root:
            root.set_attribute('openinference.span.kind', 'AGENT')
            root.set_attribute('metadata', json.dumps({**metadata, 'live_model_requests': 0}))
            yield tracer
    finally:
        flushed = provider.force_flush(timeout_millis=10000)
        instrumentor.uninstrument()
        output.write_text(json.dumps({'export_flush_completed': flushed,
            'spans': [json.loads(s.to_json()) for s in exporter.get_finished_spans()]}, indent=2))
        provider.shutdown()
        if not flushed: raise RuntimeError('trace_export_flush_incomplete')
