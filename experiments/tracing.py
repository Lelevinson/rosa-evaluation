"""Backend-neutral OTLP setup. No tracing dependencies are imported when disabled."""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from urllib.parse import urlparse
from .config import phoenix_url

_active_provider = ContextVar('rosa_trace_provider', default=None)


@contextmanager
def trace_operation(name, *, kind, model=None):
    """Explicit native-backend spans; callers supply sanitized attributes only."""
    provider = _active_provider.get()
    if provider is None:
        yield None
        return
    with provider.get_tracer(__name__).start_as_current_span(name) as span:
        span.set_attribute('openinference.span.kind', kind)
        if model:
            span.set_attribute('llm.model_name', model)
        yield span


@contextmanager
def trace_run(enabled, *, project, metadata, endpoint=None, name='rosa.run', kind='AGENT'):
    if not enabled:
        yield None
        return
    from openinference.instrumentation import using_attributes
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import SpanLimits, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoint = endpoint or os.getenv('ROSA_OTLP_ENDPOINT') or phoenix_url() + '/v1/traces'
    # Remote backends require an intentional code/configuration change for this local experiment.
    if urlparse(endpoint).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise ValueError('This local setup requires a loopback OTLP endpoint.')
    provider = TracerProvider(span_limits=SpanLimits(max_attributes=2048), resource=Resource.create({
        'service.name': 'rosa', 'openinference.project.name': project,
    }))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint=endpoint, headers={}, timeout=10,
    )))
    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=provider)
    provider_token = _active_provider.set(provider)
    try:
        with using_attributes(session_id=metadata['run_id'], metadata=metadata):
            with provider.get_tracer(__name__).start_as_current_span(name) as span:
                span.set_attribute('openinference.span.kind', kind)
                span.set_attribute('metadata', json.dumps(metadata))
                yield span
    finally:
        _active_provider.reset(provider_token)
        instrumentor.uninstrument()
        flushed = provider.force_flush(timeout_millis=15000)
        provider.shutdown()
        if not flushed:
            raise RuntimeError('OTLP flush timed out; trace completeness is unknown.')
