"""One archived-input model request, no ROSA executor or tool dispatch."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import time
from urllib.request import urlopen

from langchain_core.messages import HumanMessage, SystemMessage
from rosa_backends.chat_ollama import ConfiguredChatOllama

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / sys.argv[2]
assert FOLDER.parent == ROOT and FOLDER.name.startswith('hardware-')
DIGEST = '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'


def save(name, obj):
    (FOLDER / name).write_text(json.dumps(obj, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')


def get(endpoint, path):
    with urlopen(endpoint + path, timeout=10) as r:
        return json.load(r)


def main():
    endpoint = sys.argv[1]
    version = get(endpoint, '/api/version')
    assert version['version'] == '0.40.6', 'pinned_server_version_mismatch'
    models = get(endpoint, '/api/tags')['models']
    matching = [m for m in models if m['name'] == 'qwen3.5:9b']
    assert len(matching) == 1 and matching[0]['digest'] == DIGEST, 'pinned_digest_mismatch'
    fixtures = json.loads((ROOT / 'replay-inputs.json').read_text(encoding='utf-8'))
    fixture = next(f for f in fixtures if f['id'] == '02-move_constrained-r1-macro-call-1')
    classes = {'SystemMessage': SystemMessage, 'HumanMessage': HumanMessage}
    messages = []
    for m in fixture['messages_serialized']:
        assert set(m['kwargs']) == {'content', 'type'}
        messages.append(classes[m['id'][-1]](content=m['kwargs']['content']))
    model = ConfiguredChatOllama(model='qwen3.5:9b', base_url=endpoint,
        num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
        streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
    tools = fixture['invocation_parameters']['tools']
    # _chat_params only constructs the same adapter payload. It does not send it.
    params = model._chat_params(messages, tools=tools)
    # The pinned adapter assembles an internally streamed Ollama response even
    # with LangChain streaming=False. Preserve M4's actual wire behavior.
    assert params['think'] is False and params['stream'] is True
    assert params['options']['num_ctx'] == 8192
    assert params['options']['num_predict'] == 1024
    payload = json.dumps(params, sort_keys=True, ensure_ascii=True)
    note = ROOT / 'PRE_RUN_NOTE.md'
    receipt = json.loads((ROOT / 'pre-run-note.sha256.json').read_text())
    assert hashlib.sha256(note.read_bytes()).hexdigest() == receipt['sha256']
    amendment = ROOT / 'PRE_RUN_AMENDMENT_01.md'
    amendment_receipt = json.loads((ROOT / 'pre-run-amendment-01.sha256.json').read_text())
    assert hashlib.sha256(amendment.read_bytes()).hexdigest() == amendment_receipt['sha256']
    save('request.json', params)
    save('pre-dispatch.json', {'fixture': fixture['id'], 'version': version,
        'model': matching[0], 'expected_historical_input_tokens': fixture['recorded_input_tokens'],
        'historical_tool_calls': fixture['historical_tool_calls'],
        'pre_run_note_sha256': receipt['sha256'],
        'pre_run_amendment_sha256': amendment_receipt['sha256'],
        'payload_sha256': hashlib.sha256(payload.encode()).hexdigest(),
        'hardware_call_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inference_limit': 1, 'output_limit': 1024, 'tool_dispatch_enabled': False})
    # Exclusive durable reservation prevents accidental replay after interruption.
    with (ROOT / 'hardware-dispatch-reservation.json').open('x', encoding='utf-8') as f:
        json.dump({'requests_reserved': 1, 'at_utc': datetime.now(timezone.utc).isoformat(),
                   'attempt': FOLDER.name, 'status': 'RESERVED_BEFORE_DISPATCH', 'automatic_retries': 0}, f, indent=2)
    save('dispatch-reservation.json', {'requests_reserved': 1, 'global_reservation': '../hardware-dispatch-reservation.json'})
    started = time.monotonic()
    try:
        message = model.bind_tools(tools).invoke(messages)
        md = message.response_metadata
        usage = message.usage_metadata
        output = message.model_dump(mode='json')
        save('response.json', output)
        current_calls = [{'name': c['name'], 'args': c['args']} for c in message.tool_calls]
        result = {'status': 'RETURNED', 'requests_reserved': 1, 'requests_returned': 1,
            'client_monotonic_seconds': time.monotonic()-started, 'usage': usage,
            'metadata': md, 'tool_calls': current_calls, 'tools_dispatched': 0,
            'first_call_matches_historical': current_calls == fixture['historical_tool_calls'],
            'input_count_matches_historical': md.get('prompt_eval_count') == fixture['recorded_input_tokens'],
            'output_hit_cap': (md.get('eval_count') or 0) >= 1024,
            'generation_tokens_per_second': (md['eval_count'] / (md['eval_duration']/1e9))
                if md.get('eval_duration', 0) > 0 else None,
            'interpretation': 'Single cold-load request. Current serving observation, not an M4 trial or steady-state speed comparison.'}
        save('result.json', result)
        print(json.dumps({'status': result['status'], 'usage': usage,
                          'generation_tokens_per_second': result['generation_tokens_per_second'],
                          'first_call_matches_historical': result['first_call_matches_historical']}))
    except BaseException as exc:
        save('result.json', {'status': 'FAILED_OR_CENSORED_NO_RETRY', 'requests_reserved': 1,
            'requests_returned': 0, 'error_type': type(exc).__name__,
            'client_monotonic_seconds': time.monotonic()-started, 'tools_dispatched': 0,
            'output_tokens': None, 'output_upper_bound': 1024})
        raise


if __name__ == '__main__':
    main()
