"""Supplementary zero-inference checks; immutable runtime is not changed."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import ROOT,read,verify
from local_model import configured_model,LocalObservation
from rosa_backends.chat_ollama import ConfiguredChatOllama
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from catalogue import registry
from worlds import create_world
from ollama import ChatResponse,ResponseError
from ollama._types import ChatRequest
from types import SimpleNamespace
from httpx import ReadTimeout,ConnectError
from recovery import transient
def main():
    before=verify(require_seal=True)
    results=[]
    mapping={'human':HumanMessage,'ai':AIMessage,'system':SystemMessage,'tool':ToolMessage}
    rows=sorted((ROOT/'zero-model-validation-attempt02/trials').glob('*/result.json'))
    for path in rows:
        row=read(path)
        world,actor,observer=create_world(row['case']['domain'],**row['case']['world_configuration'])
        inv=registry(row['case']['domain']).open({'state':actor,'inspection':actor},mode=row['mode'])
        tools=[convert_to_openai_tool(t) for t in inv.tools]
        for index,batches in enumerate(row['model_inputs']):
            messages=[mapping[d['type']](**d) for d in batches[0]]
            for allowance in [1024,512]:
                opts={'num_ctx':8192,'num_predict':allowance,'temperature':0,'seed':42,'use_mmap':True}
                observed=configured_model('http://127.0.0.1:11439',LocalObservation())
                golden=ConfiguredChatOllama(model='ministral-3:8b-instruct-2512-q4_K_M',base_url='http://127.0.0.1:11439',
                    num_ctx=8192,num_predict=1024,temperature=0,seed=42,use_mmap=True,
                    streaming=False,reasoning=False,cache=False,client_kwargs={'timeout':180})
                a=observed._chat_params(messages,tools=tools,options=opts)
                b=golden._chat_params(messages,tools=tools,options=opts)
                wire_a=ChatRequest(**a).model_dump_json(exclude_none=True).encode()
                wire_b=ChatRequest(**b).model_dump_json(exclude_none=True).encode()
                assert wire_a==wire_b
                results.append({'id':row['id'],'call':index+1,'allowance':allowance,'bytes':len(wire_a),
                    'sha256':hashlib.sha256(wire_a).hexdigest(),'byte_identical':True})
    obs=LocalObservation(); model=configured_model('http://127.0.0.1:11439',obs)
    durations={'total_duration':100,'load_duration':10,'prompt_eval_count':3,'prompt_eval_duration':20,'eval_count':2,'eval_duration':30}
    response=ChatResponse(model='ministral-3:8b-instruct-2512-q4_K_M',done=True,done_reason='stop',message={'role':'assistant','content':'fixture'},**durations)
    model._client=SimpleNamespace(chat=lambda **kwargs:iter([response]))
    model._generate([HumanMessage(content='zero-network fixture')])
    info=model.request_records[-1]['generation_info']
    assert all(info.get(k)==v for k,v in durations.items()),info
    failures=[]
    for error in [ResponseError('CANARY_NOT_FOR_RECORD CUDA out of memory',status_code=500),
                  ReadTimeout('CANARY_NOT_FOR_RECORD'),ConnectError('CANARY_NOT_FOR_RECORD')]:
        m=configured_model('http://127.0.0.1:11439',obs)
        def fake(**kwargs): raise error
        m._client=SimpleNamespace(chat=fake)
        try:m._generate([HumanMessage(content='zero-network fixture')])
        except type(error):pass
        assert not transient(error)
        failures.append({'type':type(error).__name__,'record':m.request_records[-1],
                         'observation':obs.error_metadata_records[-1]})
    assert 'CANARY_NOT_FOR_RECORD' not in json.dumps(failures)
    assert verify(require_seal=True)==before
    out={'pass':True,'zero_model_requests':True,'executed_on':'lab Jazzy container',
         'body_comparisons':results,'comparison_count':len(results),
         'golden':'unchanged frozen ConfiguredChatOllama, identical messages/tools/options; actual ChatRequest serialization',
         'timing_fields_preserved':list(durations),'cached_count':'not supplied by fixture; record only if present in provider generation_info',
         'injected_failures':failures,'all_ineligible_for_retry':True,
         'local_failure_limit':'HTTP 500 records status and exception type, not raw CUDA text; external GPU/container telemetry supplements diagnosis. Unknown parser errors are not automatically censored.',
         'frozen_inputs_verified':before}
    (ROOT/'operator/FINAL_ZERO_INFERENCE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'pass':True,'byte_identical_bodies':len(results),'timing_fields':len(durations),'model_requests':0}))
if __name__=='__main__':main()
