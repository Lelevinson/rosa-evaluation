"""Export actual explicit and LangChain spans locally and to Phoenix."""
from contextlib import contextmanager
import json


@contextmanager
def trace_trial(metadata, output, *, phoenix=True):
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.resources import Resource
    provider = TracerProvider(resource=Resource.create({
        'service.name': 'rosa-reliability-v1', 'openinference.project.name': 'rosa-reliability-v1-20261022'}))
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    if phoenix:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint='http://127.0.0.1:6006/v1/traces', timeout=5)))
    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=provider)
    tracer = provider.get_tracer('rosa.reliability.v1')
    try:
        with tracer.start_as_current_span('rosa.reliability.trial') as span:
            span.set_attribute('openinference.span.kind', 'AGENT')
            span.set_attribute('metadata', json.dumps(metadata))
            yield tracer, span
    finally:
        flushed = provider.force_flush(timeout_millis=10000)
        instrumentor.uninstrument()
        spans = [json.loads(s.to_json()) for s in exporter.get_finished_spans()]
        output.write_text(json.dumps({'export_flush_completed': flushed, 'spans': spans}, indent=2))
        provider.shutdown()
        if not flushed:
            raise RuntimeError('trace_export_flush_incomplete')


def audit(snapshot, trace_path, meter):
    trace = json.loads(trace_path.read_text())
    spans = trace['spans']
    by_id = {s['context']['span_id'].removeprefix('0x'): s for s in spans}
    tool_events = [e for e in snapshot['events'] if e['type'] == 'tool']
    errors = []
    for event in tool_events:
        span = by_id.get(event.get('span_id'))
        if not span or not span['end_time'] or event['status'] == 'STARTED':
            errors.append('missing_or_unclosed_explicit_tool_span')
    callbacks_complete = set(meter.tool_starts) == set(meter.tool_ends + meter.tool_errors)
    if not callbacks_complete:
        errors.append('langchain_tool_callback_gap')
    implicit = [s for s in spans if s.get('attributes', {}).get('openinference.span.kind') == 'TOOL'
                and not s['name'].startswith('reliability.')]
    if len(implicit) != len(meter.tool_starts):
        errors.append('langchain_tool_span_count_mismatch')
    native = [s for s in spans if s['name'].startswith('reliability.native.')]
    if len(native) != len(snapshot['operations']):
        errors.append('native_span_count_mismatch')
    if any(e['status'] == 'DISPATCHING' for e in snapshot['operations']):
        errors.append('unfinished_native_operation')
    if not trace['export_flush_completed']:
        errors.append('export_flush_incomplete')
    return {'pass': not errors, 'errors': errors, 'explicit_tool_spans': len(tool_events),
            'langchain_tool_callbacks': len(meter.tool_starts), 'langchain_tool_spans': len(implicit),
            'native_spans': len(native), 'total_spans': len(spans)}
