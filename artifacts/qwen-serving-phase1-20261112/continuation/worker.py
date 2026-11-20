"""Persistent model-only WSL worker; commands come from the bounded controller."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from rosa_backends.chat_ollama import ConfiguredChatOllama

CODE=Path(__file__).resolve().parent
ROOT=CODE.parent
CLASSES={c.__name__:c for c in (AIMessage,HumanMessage,SystemMessage,ToolMessage)}


def save(path, obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')


def build(fixture, endpoint, context):
    messages=[CLASSES[m['id'][-1]](**m['kwargs']) for m in fixture['messages_serialized']]
    model=ConfiguredChatOllama(model='qwen3.5:9b',base_url=endpoint,num_ctx=context,
        num_predict=1024,temperature=0,seed=42,use_mmap=True,reasoning=False,
        streaming=False,cache=False,client_kwargs={'timeout':180})
    tools=fixture['invocation_parameters']['tools']
    params=model._chat_params(messages,tools=tools)
    assert params['think'] is False and params['stream'] is True
    assert params['options']['num_ctx']==context and params['options']['num_predict']==1024
    return model,messages,tools,params


def verify():
    recovery=json.loads((CODE/'freeze.json').read_text())
    for name,digest in recovery['files'].items():
        assert hashlib.sha256((CODE/name).read_bytes()).hexdigest()==digest,'continuation_source_changed:'+name
    frozen=json.loads((ROOT/'freeze.json').read_text())
    for name,digest in frozen['probe_files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'frozen_probe_file_changed:'+name


def main():
    config=json.loads((ROOT/'protocol.json').read_text())
    fixtures={x['id']:x for x in json.loads((ROOT/'inputs.json').read_text())}
    if sys.argv[1]=='--validate':
        checks=[]
        for ident in config['unique_inputs']:
            _,messages,_,params=build(fixtures[ident],'http://127.0.0.1:1',8192)
            checks.append({'fixture':ident,'message_count':len(messages),
                'wire_message_count':len(params['messages']),
                'wire_payload_sha256':hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()})
        save(ROOT/'offline-validation.json',{'network_calls':0,'inputs_checked':checks,
            'versions':{p:importlib.metadata.version(p) for p in ('langchain-ollama','langchain-core','ollama','pydantic')}})
        print(json.dumps({'offline_inputs_validated':len(checks),'model_calls':0}));return
    profile,endpoint=sys.argv[1:3]
    context=config['profiles'][profile]['num_ctx']
    verify()
    print(json.dumps({'event':'ready','profile':profile}),flush=True)
    for line in sys.stdin:
        command=json.loads(line)
        ordinal=command['ordinal']
        job=config['schedule'][ordinal]
        assert command['profile']==profile
        assert profile=='B'
        folder=ROOT/profile/('recovery-warmup' if ordinal==0 else f'{ordinal:02d}')
        folder.mkdir(exist_ok=False)
        verify()
        fixture=fixtures[job['fixture']]
        model,messages,tools,params=build(fixture,endpoint,context)
        save(folder/'request.json',params)
        global_index=31 if ordinal==0 else 16+ordinal
        assert global_index<=45 and ordinal<15
        with (ROOT/'reservations'/f'{global_index:02d}.json').open('x',encoding='utf-8') as f:
            json.dump({'profile':profile,'ordinal':ordinal,'request_number':global_index,
                'fixture':fixture['id'],'output_upper_bound':1024,'stage':job['stage']},f,indent=2)
        started=time.monotonic()
        try:
            msg=model.bind_tools(tools).invoke(messages)
            md=msg.response_metadata
            usage=msg.usage_metadata
            save(folder/'response.json',msg.model_dump(mode='json'))
            required=('total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration')
            assert all(type(md.get(k)) is int and md[k]>=0 for k in required), 'missing_or_invalid_timing_fields'
            assert md['eval_duration']>0 and md['eval_count']<=1024
            assert usage['input_tokens']==md['prompt_eval_count'] and usage['output_tokens']==md['eval_count']
            calls=[{'name':c['name'],'args':c['args']} for c in msg.tool_calls]
            result={'status':'RETURNED','profile':profile,'ordinal':ordinal,'fixture':fixture['id'],
                'stage':job['stage'],'client_seconds':time.monotonic()-started,'metadata':md,'usage':usage,
                'tool_calls':calls,'invalid_tool_calls':msg.invalid_tool_calls,
                'historical_tool_calls':fixture['historical_tool_calls'],
                'matches_historical':calls==fixture['historical_tool_calls'],
                'prompt_count_matches':md['prompt_eval_count']==fixture['recorded_input_tokens'],
                'expected_input_tokens':fixture['recorded_input_tokens'],
                'context_output_room':context-md['prompt_eval_count']-1024,
                'cap_hit':md['eval_count']>=1024 or md.get('done_reason')=='length',
                'generation_tokens_per_second':md['eval_count']/(md['eval_duration']/1e9),
                'tools_dispatched':0}
            save(folder/'result.json',result)
            print(json.dumps({'event':'returned','profile':profile,'ordinal':ordinal,
                'prompt_count_matches':result['prompt_count_matches']}),flush=True)
            if not result['prompt_count_matches']:return
        except BaseException as exc:
            save(folder/'result.json',{'status':'FAILED_OR_CENSORED_NO_RETRY','profile':profile,
                'ordinal':ordinal,'fixture':fixture['id'],'stage':job['stage'],
                'error_type':type(exc).__name__,'client_seconds':time.monotonic()-started,
                'output_upper_bound':1024,'tools_dispatched':0})
            print(json.dumps({'event':'failed','error_type':type(exc).__name__}),flush=True)
            return


if __name__=='__main__':main()
