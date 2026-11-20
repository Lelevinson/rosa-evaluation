"""F1 Stage 0 zero-model scripted controls. RUN ON THE LAB ONLY (owner rule). No model server is called.

Decisions come from ScriptedCaller (adapted from the frozen G1 controls runner,
revision-1/stage-3/controls-rerun-20261114/runner.py). It drives the real frozen public adapters,
worlds and scorer. Three controls, macro condition only, for every F1 dev case (16, the G1 dev
set) and every F1 held-out case (30), under both wordings:

  C1 W1 equivalence: base (frozen MacroROSA) and new (F1MacroROSA) must produce identical program
     behaviour: normalized snapshot (routine, guards, operations, observations, verification,
     reports), actor and observer records, accounting and score. The model-visible text may
     differ only as declared: system = frozen contract + ' ' + SYSTEM_ADDITION, and the request
     catalogue JSON = w1_catalogue(frozen catalogue).
  C2 W2 route: a plain-text, no-tool reply ends the task with that text as the answer, with no
     selection, operation or report, and the frozen scorer passes it as clarification
     (clarification_review_required). Scorer leniency is recorded on fixed strings.
  C3 G1-style scripted pass counts per wording and F1 task type.

Usage (inside the existing container, research env; paths are arguments, nothing is installed):
  python -I -B tools/f1_wording/controls.py --workspace <dir holding rosa-evaluation/ and rosa-research/>
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STUDY = REPO / 'artifacts/f1-catalogue-wording-20261121'
G1_REL = 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1'
VOLATILE = {'started', 'finished', 'acquired_monotonic', 'monotonic', 'span_id'}
OBS = re.compile(r'obs-[0-9a-f]{12}-')


def sha(path):
    """SHA-256 of file content with CRLF normalized to LF (laptop autocrlf vs lab LF copies)."""
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def normalize(value):
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, str):
        return OBS.sub('obs-X-', value)
    return value


def check_frozen_inputs(workspace):
    """Lab copies of every imported frozen file must match the hashes recorded on the laptop."""
    record = json.loads((STUDY / 'controls/FROZEN_INPUTS.json').read_text(encoding='utf-8'))
    bad = [rel for rel, digest in record['files'].items() if sha(workspace / rel) != digest]
    if bad:
        raise SystemExit('frozen input mismatch on this host: ' + ', '.join(bad))
    return len(record['files'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--out', type=Path, default=STUDY / 'controls')
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    frozen_count = check_frozen_inputs(workspace)
    g1 = workspace / G1_REL
    sys.path[:0] = [str(workspace / 'rosa-research/src'), str(g1), str(g1 / 'stage-2'), str(HERE)]

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from rosa_reliability.bounded_macro import MacroLimits
    from rosa_reliability.prompt_contract import bounded_contract, REQUIRED_TOOLS
    from worlds import create_world
    from catalogue import registry
    from scoring import score
    import wording

    class ScriptedCaller(BaseChatModel):
        invocation: object
        case: dict
        index: int = 0
        seen: list = []

        @property
        def _llm_type(self):
            return 'f1-scripted-no-live-model'

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, **kwargs):
            index, self.index = self.index, self.index + 1
            if index == 0:
                self.seen.extend({'type': m.type, 'content': m.content} for m in messages)
            usage = {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}
            if self.case['kind'] == 'ambiguous':
                assert index == 0
                message = AIMessage(content='Should I inspect readiness or move to a registered target?',
                                    usage_metadata=usage, response_metadata={'finish_reason': 'stop'})
                return ChatResult(generations=[ChatGeneration(message=message)])
            definition = self.invocation.catalogue[self.case['skill_id']]
            inspection = definition['kind'] == 'read_only_inspection'
            if index == 0:
                name, call = 'select_skill', {'skill_id': self.case['skill_id']}
            else:
                assert index == 1, 'unexpected_extra_scripted_turn'
                observation = self.invocation.snapshot()['observations'][-1]
                flat = [v for fields in observation['observed_values'].values() for v in fields.values()]
                reached = (all(v == 1.0 for v in flat) if inspection else all(
                    observation['observed_values'][n][k] is not None and
                    abs(observation['observed_values'][n][k] - v) <= .025
                    for n, fields in definition['targets'].items() for k, v in fields.items()))
                status = 'UNKNOWN' if any(v is None for v in flat) else 'SUCCESS' if reached else 'FAILURE'
                name, call = 'submit_report', {'status': status, 'observation_id': observation['observation_id']}
            message = AIMessage(content='', tool_calls=[{'name': name, 'args': call, 'id': f'scripted-{index}',
                                'type': 'tool_call'}], usage_metadata=usage, response_metadata={'finish_reason': 'stop'})
            return ChatResult(generations=[ChatGeneration(message=message)])

    def run(case, which):
        world, actor, observer = create_world(case['domain'], **case['world_configuration'])
        observer.observe()
        invocation = registry(case['domain']).open({'state': actor, 'inspection': actor}, mode='macro',
                                                   limits=MacroLimits(seconds=360.0))
        model = ScriptedCaller(invocation=invocation, case=case, seen=[], cache=False)
        agent = wording.make_agent(which, model, invocation, backend='scripted')
        contract = json.loads((g1 / 'prompt-contract.json').read_text(encoding='utf-8-sig'))
        assert bounded_contract(REQUIRED_TOOLS) == contract['system']
        query = (contract['rules'].removesuffix('\nUser: ') + ' Execution condition: macro. ' +
                 contract['condition_sentences']['macro'] + contract[case['domain'] + '_suffix'] + case['request'])
        answer = agent.invoke(query)
        observer.observe()
        snapshot, accounting = invocation.snapshot(), agent.inference_budget.snapshot()
        scored = score(case, snapshot, answer, observer.records)
        return {'answer': answer, 'snapshot': snapshot, 'accounting': accounting, 'score': scored,
                'actor': [r['kind'] for r in actor.records], 'observer_truth': observer.records[-1]['snapshot'],
                'messages': model.seen, 'catalogue': invocation.catalogue, 'query': query}

    heldout = json.loads((STUDY / 'cases/heldout.json').read_text(encoding='utf-8'))
    g1_cases = {c['case_id']: c for c in json.loads((g1 / 'cases.json').read_text(encoding='utf-8-sig'))}
    dev_ids = [c['case_id'] for c in json.loads((STUDY / 'cases/dev.json').read_text(encoding='utf-8'))['cases']]
    dev = []
    for cid in dev_ids:
        c = deepcopy(g1_cases[cid])
        c['f1_type'] = {'ladder': 'inspection_control', 'write': 'direct_movement',
                        'missing_prerequisite': 'movement_prerequisite'}.get(c['kind'], c['kind'])
        dev.append(c)

    started = time.monotonic()
    rows, failures = [], []
    for case in dev + heldout:
        base, new = run(case, 'base'), run(case, 'new')
        program_same = all(normalize(base[k]) == normalize(new[k]) for k in
                           ('snapshot', 'accounting', 'score', 'actor', 'observer_truth', 'answer'))
        cat = base['catalogue']
        expected_new_text = []
        for m in base['messages']:
            text = m['content']
            if m['type'] == 'system':
                text = text + ' ' + wording.SYSTEM_ADDITION
            text = text.replace(json.dumps(cat, sort_keys=True), json.dumps(wording.w1_catalogue(cat), sort_keys=True))
            expected_new_text.append({'type': m['type'], 'content': text})
        text_as_declared = new['messages'] == expected_new_text and base['messages'] != new['messages']
        base_system_frozen = next(m['content'] for m in base['messages'] if m['type'] == 'system') == bounded_contract(REQUIRED_TOOLS)
        row = {'case_id': case['case_id'], 'split': case['split'], 'f1_type': case['f1_type'], 'kind': case['kind'],
               'C1_program_identical': program_same, 'C1_text_differs_only_as_declared': text_as_declared,
               'C1_base_system_is_frozen_contract': base_system_frozen}
        for which, result in (('base', base), ('new', new)):
            s = result['snapshot']
            row[which] = {'primary_pass': result['score']['primary_pass'], 'selection_correct': result['score']['selection_correct'],
                          'calls': result['accounting']['calls'], 'native_operations': len(s['operations']),
                          'dispatches': result['observer_truth']['dispatches'], 'selected': s['selected_skill'],
                          'accepted_status': result['score']['accepted_status']}
        if case['kind'] == 'ambiguous':
            s = new['snapshot']
            row['C2_no_tool_reply'] = {
                'answer_is_reply_text': new['answer'] == 'Should I inspect readiness or move to a registered target?',
                'no_selection': s['selected_skill'] is None, 'no_operations': not s['operations'],
                'no_reports': not s['reports'], 'single_call': new['accounting']['calls'] == 1,
                'scored_pass': new['score']['primary_pass'] is True,
                'review_required': new['score']['clarification_review_required'] is True,
                'human_review_status': new['score']['human_review_status']}
            # Scorer leniency on fixed strings (same snapshot, different answer text).
            row['C2_scorer_on_fixed_answers'] = {text: score(case, s, text, [{'kind': 'observer_read',
                'snapshot': new['observer_truth']}])['primary_pass'] for text in (
                'I will take care of it.',
                'Do you want me to inspect it or move it?',
                'Looking at the catalogue, I will decide which skill fits after more thought.')}
        c2_ok = all(v for k, v in row.get('C2_no_tool_reply', {}).items() if k != 'human_review_status')
        ok = (program_same and text_as_declared and base_system_frozen and row['base']['primary_pass']
              and row['new']['primary_pass'] and c2_ok)
        row['pass'] = bool(ok)
        if not ok:
            failures.append(case['case_id'])
        rows.append(row)
        print(f"{case['case_id']:>16} {case['f1_type']:<22} C1={program_same and text_as_declared} "
              f"base={row['base']['primary_pass']} new={row['new']['primary_pass']}", flush=True)

    def counts(split):
        out = {}
        for r in rows:
            if r['split'] != split:
                continue
            t = out.setdefault(r['f1_type'], {'cases': 0, 'base_pass': 0, 'new_pass': 0, 'C1_identical': 0})
            t['cases'] += 1
            t['base_pass'] += r['base']['primary_pass']
            t['new_pass'] += r['new']['primary_pass']
            t['C1_identical'] += r['C1_program_identical'] and r['C1_text_differs_only_as_declared']
        return out

    ambiguous = [r for r in rows if r['kind'] == 'ambiguous']
    summary = {
        'live_model_requests': 0, 'decision_actor': 'scripted_fixture_oracle', 'condition': 'macro',
        'wording_revision': wording.WORDING_REVISION, 'frozen_inputs_verified_on_host': frozen_count,
        'cases': len(rows), 'trials': 2 * len(rows), 'all_pass': not failures, 'failures': failures,
        'C1_program_identical': sum(r['C1_program_identical'] for r in rows),
        'C1_text_differs_only_as_declared': sum(r['C1_text_differs_only_as_declared'] for r in rows),
        'C2_ambiguous_no_tool_ok': sum(all(v for k, v in r['C2_no_tool_reply'].items() if k != 'human_review_status')
                                       for r in ambiguous),
        'C2_ambiguous_cases': len(ambiguous),
        'C2_scorer_on_fixed_answers': ambiguous[0]['C2_scorer_on_fixed_answers'] if ambiguous else None,
        'C3_pass_counts': {'dev': counts('dev'), 'heldout': counts('heldout')},
        'elapsed_seconds': round(time.monotonic() - started, 2)}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'CONTROL_ROWS.json').write_text(json.dumps(rows, indent=1) + '\n', encoding='utf-8')
    (args.out / 'CONTROL_SUMMARY.json').write_text(json.dumps(summary, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ('cases', 'trials', 'all_pass', 'failures', 'C1_program_identical',
                      'C1_text_differs_only_as_declared', 'C2_ambiguous_no_tool_ok', 'C3_pass_counts')}, indent=1))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
