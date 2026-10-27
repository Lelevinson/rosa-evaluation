"""Self-contained engineering audit; same invariants as the earlier auditor."""
from contextlib import contextmanager
import json

from langchain_core.callbacks import BaseCallbackHandler

PROJECT = 'rosa-macro-capabilities-v2-20261027'
ROOT_SPAN = 'rosa.capability.demo'


class Meter(BaseCallbackHandler):
    def __init__(self): self.tool_starts, self.tool_ends, self.tool_errors = [], [], []
    def on_tool_start(self, serialized, input_str, **kwargs): self.tool_starts.append(str(kwargs['run_id']))
    def on_tool_end(self, output, **kwargs): self.tool_ends.append(str(kwargs['run_id']))
    def on_tool_error(self, error, **kwargs): self.tool_errors.append(str(kwargs['run_id']))


@contextmanager
def trace_check(path, metadata):
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    provider = TracerProvider(resource=Resource.create({'service.name': PROJECT, 'openinference.project.name': PROJECT}))
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint='http://127.0.0.1:6006/v1/traces', timeout=5)))
    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=provider)
    try:
        tracer = provider.get_tracer(PROJECT)
        with tracer.start_as_current_span(ROOT_SPAN) as root:
            root.set_attribute('openinference.span.kind', 'AGENT')
            root.set_attribute('metadata', json.dumps(metadata))
            yield tracer
    finally:
        flushed = provider.force_flush(timeout_millis=10000)
        instrumentor.uninstrument()
        path.write_text(json.dumps({'export_flush_completed': flushed,
            'spans': [json.loads(s.to_json()) for s in exporter.get_finished_spans()]}, indent=2))
        provider.shutdown()
        if not flushed: raise RuntimeError('trace_export_flush_incomplete')


def audit(snapshot, path, meter):
    trace = json.loads(path.read_text())
    spans = trace['spans']
    by_id = {s['context']['span_id'].removeprefix('0x'): s for s in spans}
    tools = [e for e in snapshot['events'] if e['type'] == 'tool']
    errors = []
    for event in tools:
        span = by_id.get(event.get('span_id'))
        if not span or not span.get('end_time') or event['status'] == 'STARTED':
            errors.append('missing_or_unclosed_explicit_tool_span')
    if set(meter.tool_starts) != set(meter.tool_ends + meter.tool_errors): errors.append('langchain_tool_callback_gap')
    implicit = [s for s in spans if s.get('attributes', {}).get('openinference.span.kind') == 'TOOL'
                and not s['name'].startswith('reliability.')]
    if len(implicit) != len(meter.tool_starts): errors.append('langchain_tool_span_count_mismatch')
    native = [s for s in spans if s['name'].startswith('reliability.native.')]
    if len(native) != len(snapshot['operations']): errors.append('native_span_count_mismatch')
    if any(e['status'] == 'DISPATCHING' for e in snapshot['operations']): errors.append('unfinished_native_operation')
    if not trace['export_flush_completed']: errors.append('export_flush_incomplete')
    return {'pass': not errors, 'errors': errors, 'explicit_tool_spans': len(tools),
            'native_spans': len(native), 'langchain_tool_callbacks': len(meter.tool_starts), 'total_spans': len(spans)}
