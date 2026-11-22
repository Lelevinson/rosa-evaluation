"""Phase A re-diagnosis of G1 multi-model tool-call behaviour from frozen trial records.

Read-only. Zero model calls, zero network. Reads result.json of every G1 held-out trial for
Qwen (stage-4-qwen-lab-20261119) and Ministral/Granite/Llama (stage-4-multimodel-20261119),
and writes per-model counts plus quoted examples.

Usage: python -I tools/parity/rediagnose.py <repo_root> <out.json>
"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

REV = 'artifacts/macro-generalization-20261113/revision-1'
SOURCES = {
    'qwen': f'{REV}/stage-4-qwen-lab-20261119/trials',
    'ministral': f'{REV}/stage-4-multimodel-20261119/backends/ministral/trials',
    'granite': f'{REV}/stage-4-multimodel-20261119/backends/granite/trials',
    'llama': f'{REV}/stage-4-multimodel-20261119/backends/llama/trials',
}
FENCE = re.compile(r'```')
JSON_NAME = re.compile(r'"name"\s*:')
JSON_FUNCTION = re.compile(r'"function"\s*:')
JSON_PARAMETERS = re.compile(r'"parameters"\s*:')
GRANITE_TOKEN = '<|tool_call|>'


def rejected(content):
    try:
        body = json.loads(content)
    except (TypeError, ValueError):
        return None
    return body if isinstance(body, dict) and body.get('rejected') else None


def analyse(model, root):
    files = sorted(glob.glob(str(root / SOURCES[model] / '*' / 'result.json')))
    c = Counter()
    rejection_codes = Counter()
    rejection_fields = Counter()
    rejections_by_turn = Counter()
    prompt_shrinks = 0
    prompt_pairs = 0
    examples = {'text_no_call': [], 'rejection': []}
    for path in files:
        r = json.loads(Path(path).read_text(encoding='utf-8'))
        c['trials'] += 1
        outputs = r.get('model_outputs') or []
        sizes = [((o.get('usage_metadata') or {}).get('input_tokens')) for o in outputs]
        for a, b in zip(sizes, sizes[1:]):
            if isinstance(a, int) and isinstance(b, int):
                prompt_pairs += 1
                prompt_shrinks += b < a
        for i, o in enumerate(outputs):
            c['outputs'] += 1
            calls = o.get('tool_calls') or []
            c['recognized_calls'] += len(calls)
            c['invalid_tool_calls'] += len(o.get('invalid_tool_calls') or [])
            text = o.get('content') or ''
            if not calls:
                c['outputs_without_call'] += 1
                c['no_call_with_fence'] += bool(FENCE.search(text))
                c['no_call_with_granite_token'] += GRANITE_TOKEN in text
                c['no_call_with_json_name_key'] += bool(JSON_NAME.search(text))
                c['no_call_with_json_function_key'] += bool(JSON_FUNCTION.search(text))
                c['no_call_with_json_parameters_key'] += bool(JSON_PARAMETERS.search(text))
                if text and len(examples['text_no_call']) < 3:
                    examples['text_no_call'].append({'trial': r.get('id'), 'turn': i + 1, 'content': text[:700]})
            if (o.get('response_metadata') or {}).get('done_reason') == 'length':
                c['length_stops'] += 1
        # tool responses that rejected a call, located in the last model_inputs transcript
        transcript = (r.get('model_inputs') or [[]])[-1]
        if transcript and isinstance(transcript[0], list):
            transcript = transcript[-1]
        ai_turn = 0
        last_call = None
        for msg in transcript:
            if not isinstance(msg, dict):
                continue
            if msg.get('type') == 'ai':
                ai_turn += 1
                last_call = (msg.get('tool_calls') or [None])[0]
            elif msg.get('type') == 'tool':
                body = rejected(msg.get('content'))
                if body:
                    c['rejections'] += 1
                    rejection_codes[body.get('code')] += 1
                    rejections_by_turn['turn_1' if ai_turn == 1 else 'turn_2_plus'] += 1
                    details = body.get('details') or []
                    for d in details if isinstance(details, list) else [details]:
                        key = f"{d.get('field')}:{d.get('reason')}" if isinstance(d, dict) else str(d)[:60]
                        rejection_fields[key] += 1
                    if len(examples['rejection']) < 4:
                        examples['rejection'].append({'trial': r.get('id'), 'turn': ai_turn,
                                                      'call': last_call, 'tool_response': body})
    return {'files': len(files), 'counts': dict(c), 'rejection_codes': dict(rejection_codes),
            'rejection_fields_top': dict(rejection_fields.most_common(12)),
            'rejections_by_turn': dict(rejections_by_turn),
            'prompt_token_pairs': prompt_pairs, 'prompt_shrank_next_turn': prompt_shrinks,
            'examples': examples}


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    result = {m: analyse(m, root) for m in SOURCES}
    result['_meta'] = {'model_requests': 0, 'network_access': False,
                       'note': 'rejections counted from tool messages in the final model_inputs transcript'}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    for m in SOURCES:
        x = result[m]
        print(m, x['files'], x['counts'], x['rejection_codes'], x['rejections_by_turn'],
              'shrink', x['prompt_shrank_next_turn'], '/', x['prompt_token_pairs'])


if __name__ == '__main__':
    main()
