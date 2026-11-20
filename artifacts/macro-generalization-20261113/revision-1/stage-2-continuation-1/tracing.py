"""Local/OTLP live G1 dev traces; observer I/O belongs to the evaluator."""
from contextlib import contextmanager
import json

from experiments.macro_capabilities_v2.observability import Meter as OriginalMeter, audit as original_audit

PROJECT='rosa-g1-sol-dev-20261114'
ROOT_SPAN='g1.sol.dev'


class Meter(OriginalMeter):
    raise_error=True
    def __init__(self,observer,tracer):
        super().__init__()
        self.observer,self.tracer=observer,tracer
        self.model_outputs,self.observer_tags,self.tool_inputs=[],[],[]
        self.model_inputs,self.model_errors=[],[]
        self.execution_errors=[]
    def on_chain_error(self,error,**kwargs):
        from rosa_reliability.execution import ControlledStop
        if isinstance(error,ControlledStop):self.execution_errors.append(str(error))
    def on_chat_model_start(self,serialized,messages,**kwargs):
        self.model_inputs.append([[m.model_dump(mode='json') for m in batch] for batch in messages])
    def on_llm_error(self,error,**kwargs):
        value={'type':type(error).__name__}
        if hasattr(error,'code'):value['code']=error.code
        self.model_errors.append(value)
    def observe(self,tag):
        with self.tracer.start_as_current_span('g1.evaluator.observer_read') as span:
            span.set_attribute('openinference.span.kind','CHAIN')
            span.set_attribute('g1.owner','evaluator')
            span.set_attribute('g1.observer_read_index',len(self.observer.records)+1)
            value=self.observer.observe()
        self.observer_tags.append({'index':len(self.observer.records),'tag':tag})
        return value
    def on_tool_start(self,serialized,input_str,**kwargs):
        super().on_tool_start(serialized,input_str,**kwargs)
        self.tool_inputs.append({'run_id':str(kwargs['run_id']),'tool':(serialized or {}).get('name'),
                                 'input':input_str})
    def on_tool_end(self,output,**kwargs):
        super().on_tool_end(output,**kwargs)
        self.observe('tool_end:'+str(kwargs['run_id']))
    def on_tool_error(self,error,**kwargs):
        super().on_tool_error(error,**kwargs)
        self.observe('tool_error:'+str(kwargs['run_id']))
    def on_llm_end(self,response,**kwargs):
        for batch in response.generations:
            for generation in batch:
                self.model_outputs.append(generation.message.model_dump(mode='json'))


@contextmanager
def trace_check(path,metadata):
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor,BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    provider=TracerProvider(resource=Resource.create({'service.name':PROJECT,'openinference.project.name':PROJECT}))
    exporter=InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint='http://127.0.0.1:6006/v1/traces',timeout=5)))
    instrumentor=LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=provider)
    try:
        tracer=provider.get_tracer(PROJECT)
        with tracer.start_as_current_span(ROOT_SPAN) as root:
            root.set_attribute('openinference.span.kind','AGENT')
            root.set_attribute('metadata',json.dumps(metadata))
            yield tracer
    finally:
        flushed=provider.force_flush(timeout_millis=10000)
        instrumentor.uninstrument()
        path.write_text(json.dumps({'export_flush_completed':flushed,
            'spans':[json.loads(s.to_json()) for s in exporter.get_finished_spans()]},indent=2)+'\n')
        provider.shutdown()
        if not flushed:raise RuntimeError('trace_export_flush_incomplete')


def audit(snapshot,path,meter,inference,actor_records):
    result=original_audit(snapshot,path,meter)
    spans=json.loads(path.read_text())['spans']
    llm=[s for s in spans if s.get('attributes',{}).get('openinference.span.kind')=='LLM']
    evaluator=[s for s in spans if s['name']=='g1.evaluator.observer_read']
    native=[s for s in spans if s['name'].startswith('reliability.native.')]
    errors=list(result['errors'])
    if (len(llm)!=inference['calls'] or len(meter.model_outputs)+len(meter.model_errors)!=inference['calls'] or
        len(meter.model_inputs)!=inference['calls']):
        errors.append('physical_request_callback_span_count_mismatch')
    if len(evaluator)!=len(meter.observer.records):errors.append('observer_span_count_mismatch')
    if len(native)!=len(actor_records):errors.append('actor_IO_native_ledger_mismatch')
    if len(snapshot['operations'])!=len(actor_records):errors.append('observer_or_hidden_IO_charged_as_agent_native')
    if any(s['attributes'].get('g1.owner')!='evaluator' or 'reliability.operation_id' in s['attributes'] for s in evaluator):
        errors.append('observer_metering_owner_invalid')
    result.update(pass_=not errors,errors=errors,physical_LLM_spans=len(llm),observer_spans=len(evaluator),
                  actor_IO_attempts=len(actor_records),observer_excluded_from_agent_native=not errors)
    result['pass']=not errors
    result.pop('pass_',None)
    return result
