"""Parity Phase B acceptance scorer (transport-level). Read-only, stdlib only, zero model calls.

Implements ACCEPTANCE_CRITERIA.md (frozen). For each arm (primitives, macro) of one model:

  tool_turns      model outputs in trials whose case expects tool use (kind != ambiguous)
  recognized      of those, outputs carrying >= 1 structured tool call (`tool_calls`, Ollama/ChatOllama parsed)
  calls           recognized structured calls in those outputs
  schema_invalid  calls whose name is not a G1 tool, plus harness rejections with a transport code
                  (`schema_validation`), plus ChatOllama `invalid_tool_calls` entries
  parse_crashes   trials whose `error` or `model_errors` is non-empty with a parse-path signature

  PASS (arm)  = recognized/tool_turns >= 0.90 AND (calls-schema_invalid)/calls >= 0.90 AND parse_crashes == 0
  PASS (model)= PASS in both arms

Semantic rejections (wrong skill, unknown observation, wrong classification, ...) are NOT transport
failures and are only reported. Ambiguous-case outputs are excluded from the denominators and reported.

Usage:
  python -I -B tools/parity/acceptance_score.py <trials_dir> <out.json> [--cases <cases.json>]
  <trials_dir> holds one sub-directory per trial with result.json (G1 layout).
  Without --cases, each result.json's embedded `case` decides tool_call_expected (kind != ambiguous).
"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

G1_TOOLS = {'select_skill', 'read_state', 'write_state', 'verify_outcome', 'submit_report'}
TRANSPORT_CODES = {'schema_validation'}
PARSE_SIGNATURE = re.compile(r'pars|json|decode|tool.?call|unmarshal|invalid character|template', re.I)
THRESH_RECOGNIZED, THRESH_VALID = 0.90, 0.90


def tool_messages(r):
    transcript = (r.get('model_inputs') or [[]])[-1]
    if transcript and isinstance(transcript[0], list):
        transcript = transcript[-1]
    for msg in transcript or []:
        if isinstance(msg, dict) and msg.get('type') == 'tool':
            try:
                body = json.loads(msg.get('content'))
            except (TypeError, ValueError):
                body = None
            yield body if isinstance(body, dict) else None, msg.get('content')


def score_trial(r, expects_tool):
    c = Counter()
    for o in r.get('model_outputs') or []:
        calls = o.get('tool_calls') or []
        key = 'tool' if expects_tool else 'ambiguous'
        c[f'{key}_turns'] += 1
        c[f'{key}_recognized'] += bool(calls)
        c[f'{key}_calls'] += len(calls)
        c[f'{key}_unknown_name'] += sum(t.get('name') not in G1_TOOLS for t in calls)
        c[f'{key}_invalid_tool_calls'] += len(o.get('invalid_tool_calls') or [])
        c[f'{key}_length_stops'] += (o.get('response_metadata') or {}).get('done_reason') == 'length'
    for body, raw in tool_messages(r):
        key = 'tool' if expects_tool else 'ambiguous'
        if body and body.get('rejected'):
            code = body.get('code')
            c[f'{key}_rejected_{"transport" if code in TRANSPORT_CODES else "semantic"}'] += 1
        elif isinstance(raw, str) and 'is not a valid tool' in raw:
            c[f'{key}_rejected_transport'] += 1
    errors = [str(e) for e in (r.get('model_errors') or [])] + ([str(r['error'])] if r.get('error') else [])
    c['trials_with_error'] += bool(errors)
    c['parse_crashes'] += any(PARSE_SIGNATURE.search(e) for e in errors)
    return c


def arm_summary(c):
    turns, rec, calls = c['tool_turns'], c['tool_recognized'], c['tool_calls']
    invalid = c['tool_unknown_name'] + c['tool_rejected_transport'] + c['tool_invalid_tool_calls']
    invalid = min(invalid, calls) if calls else invalid
    rec_rate = rec / turns if turns else None
    valid_rate = (calls - invalid) / calls if calls else None
    ok = (rec_rate is not None and rec_rate >= THRESH_RECOGNIZED and valid_rate is not None
          and valid_rate >= THRESH_VALID and c['parse_crashes'] == 0)
    return {'counts': dict(sorted(c.items())), 'tool_turns': turns, 'recognized_turns': rec,
            'recognized_turn_rate': rec_rate, 'calls': calls, 'schema_invalid_calls': invalid,
            'schema_valid_rate': valid_rate, 'parse_crashes': c['parse_crashes'], 'pass': ok}


def main():
    args = sys.argv[1:]
    cases = None
    if '--cases' in args:
        i = args.index('--cases')
        cases = {x['case_id']: x for x in json.loads(Path(args[i + 1]).read_text(encoding='utf-8-sig'))}
        del args[i:i + 2]
    trials_dir, out = Path(args[0]), Path(args[1])
    per_arm = {}
    trials = Counter()
    for path in sorted(glob.glob(str(trials_dir / '*' / 'result.json'))):
        r = json.loads(Path(path).read_text(encoding='utf-8'))
        case = r.get('case') or {}
        if cases is not None:
            if case.get('case_id') not in cases:
                continue
            case = cases[case['case_id']]
        expects = case.get('tool_call_expected', case.get('kind') != 'ambiguous')
        arm = r.get('mode')
        trials[arm] += 1
        per_arm.setdefault(arm, Counter()).update(score_trial(r, expects))
    arms = {a: arm_summary(c) | {'trials': trials[a]} for a, c in sorted(per_arm.items())}
    result = {'criteria': {'recognized_turn_rate_min': THRESH_RECOGNIZED, 'schema_valid_rate_min': THRESH_VALID,
                           'parse_crashes_max': 0, 'arms_required': ['macro', 'primitives']},
              'trials_dir': str(trials_dir), 'arms': arms,
              'model_pass': set(arms) >= {'macro', 'primitives'} and all(a['pass'] for a in arms.values()),
              'model_requests': 0}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    for a, s in arms.items():
        print(a, 'trials', s['trials'], 'rec', s['recognized_turns'], '/', s['tool_turns'],
              'valid', s['calls'] - s['schema_invalid_calls'], '/', s['calls'], 'crash', s['parse_crashes'],
              'PASS' if s['pass'] else 'FAIL')
    print('MODEL', 'PASS' if result['model_pass'] else 'FAIL')


if __name__ == '__main__':
    main()
