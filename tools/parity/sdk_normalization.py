"""Count tool-call arguments the ChatOllama SDK changed (langchain-ollama 0.3.10
_parse_arguments_from_tool_call: shallow json.loads / ast.literal_eval of string values, e.g. a list
sent as the string '["a","b"]'). Reported as ASSISTANCE, separately from the model's own schema
compliance. Read-only. Usage: sdk_normalization.py <run_dir>  -> <run_dir>/SDK_NORMALIZATION.json"""
import ast
import json
import sys
from pathlib import Path


def decodes(value):
    if not isinstance(value, str):
        return None
    for fn in (json.loads, ast.literal_eval):
        try:
            v = fn(value)
            return type(v).__name__ if isinstance(v, (list, dict)) else None
        except Exception:
            pass
    return None


def main():
    run = Path(sys.argv[1])
    calls = normalized = whole_string_args = 0
    examples = []
    for f in sorted((run / 'wire').glob('*.json')):
        row = json.loads(f.read_text(encoding='utf-8'))
        for chunk in row.get('response') or []:
            for tc in (chunk.get('message') or {}).get('tool_calls') or []:
                calls += 1
                args = (tc.get('function') or {}).get('arguments')
                if isinstance(args, str):
                    whole_string_args += 1
                    continue
                hit = {k: decodes(v) for k, v in (args or {}).items() if decodes(v)}
                if hit:
                    normalized += 1
                    if len(examples) < 10:
                        examples.append({'wire_file': f.name, 'tool': tc['function'].get('name'), 'fields': hit})
    out = {'raw_tool_calls': calls, 'calls_with_string_encoded_list_or_object': normalized,
           'calls_with_whole_arguments_as_string': whole_string_args,
           'model_own_compliance_note': 'schema validity counted by acceptance_score.py is AFTER SDK normalization; '
                                        'calls listed here would not be schema-valid as the model emitted them',
           'examples': examples}
    (run / 'SDK_NORMALIZATION.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'examples'}))


if __name__ == '__main__':
    main()
