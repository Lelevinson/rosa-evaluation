"""Lab-only zero-model controls for the Qwen backend port, never live evidence."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import sys

import common
from common import ROOT, REV, read
import trial as runtime
import runtime_support as support
from local_model import configured_model, LocalObservation
from recovery import Campaign, transient
from adjudication import adjudicate
from censoring import censor_class
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from ollama import ResponseError
from rosa_backends.chat_ollama import ConfiguredChatOllama


def main():
    common.verify()
    label = sys.argv[1] if len(sys.argv) > 1 else 'zero-model-validation'
    assert Path(label).name == label
    out = ROOT / label
    out.mkdir(exist_ok=False)
    observation = LocalObservation()
    model = configured_model('http://127.0.0.1:11439', observation)
    params = model._chat_params([HumanMessage(content='Development-only transport fixture')],
        options={'num_predict': 512, 'num_ctx': 8192, 'temperature': 0, 'seed': 42, 'use_mmap': True})
    assert params['model'] == 'ministral-3:8b-instruct-2512-q4_K_M' and params['think'] is False
    golden = ConfiguredChatOllama(model='ministral-3:8b-instruct-2512-q4_K_M', base_url='http://127.0.0.1:11439',
        num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
        streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
    expected = golden._chat_params([HumanMessage(content='Development-only transport fixture')],
        options={'num_predict': 512, 'num_ctx': 8192, 'temperature': 0, 'seed': 42, 'use_mmap': True})
    assert params == expected and params['options']['num_predict'] == 512
    assert params['options']['num_ctx'] == 8192 and not model.request_records
    assert transient(ResponseError('fixture', status_code=503))
    assert not transient(ResponseError('fixture', status_code=429))
    assert not transient(TimeoutError())
    # Reuse the exact frozen scripted fixture, never model outputs or test answers.
    source = REV / 'stage-1/runner.py'
    tree = ast.parse(source.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ScriptedCaller')
    namespace = dict(BaseChatModel=BaseChatModel, AIMessage=AIMessage,
        ChatGeneration=ChatGeneration, ChatResult=ChatResult)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
    class Caller(namespace['ScriptedCaller']):
        @property
        def request_records(self):
            return []
    plan = read(ROOT / 'plan.json')
    specifications = [('arm', 'ladder', 'none'), ('arm', 'ladder', 'source_timeout'),
                      ('base', 'write', 'none'), ('base', 'write_fault', None)]
    selected = []
    for domain, kind, fault in specifications:
        candidates = [p for p in plan if p['case']['domain'] == domain and p['case']['kind'] == kind
                      and (fault is None or p['case']['fault'] == fault)]
        if not candidates and fault == 'none':
            candidates = [p for p in plan if p['case']['domain'] == domain and p['case']['kind'] == kind
                          and p['case']['nominal_healthy_world']]
        assert candidates, (domain, kind, fault)
        case_id = candidates[0]['case']['case_id']
        selected.extend(p for p in plan if p['case']['case_id'] == case_id)
    original = runtime.MacroROSA
    def bind_oracle(llm, invocation, **kwargs):
        llm.invocation = invocation
        return original(llm, invocation, **kwargs)
    runtime.MacroROSA = bind_oracle
    common.ROOT = support.ROOT = runtime.ROOT = out
    shutil.copyfile(ROOT / 'persisted_audit.py', out / 'persisted_audit.py')
    results = []
    try:
        for item in selected:
            caller = Caller(invocation=None, case=item['case'])
            campaign = Campaign(lambda _: None)
            row = runtime.trial(item, caller, LocalObservation(), campaign,
                decision_actor='scripted_fixture_oracle')
            row['token_usage_kind'] = 'SYNTHETIC_FIXTURE_METADATA'
            row['live_model_requests'] = 0
            (out / 'trials' / item['id'] / 'result.json').write_text(json.dumps(row, indent=2) + '\n')
            verdict = support.evaluate_progress(row)
            assert verdict['primary_status'] == 'PASS'
            assert row['actual_turns'] == item['expected_turns']
            assert len(row['actor_records']) == item['expected_native']
            results.append({'id': item['id'], 'pass': True, 'scripted_calls': row['actual_turns'],
                'native': len(row['actor_records']), 'local_audit': row['local_audit']['pass'],
                'persisted_audit': row['phoenix_audit']['pass'], 'live_model_requests': 0})
        # Once recorded, pre-failure activity cannot be overwritten by later reads.
        folder = out / 'failure-binding-fixture'
        obs = LocalObservation()
        obs.error_metadata_records = [{'failure_surface': 'HTTP', 'http_status': 503}]
        meter, actor = SimpleNamespace(tool_inputs=[]), SimpleNamespace(records=[])
        inv = SimpleNamespace(snapshot=lambda: {})
        support.journal_progress(folder, {}, inv, meter, actor, obs, 0, {})
        meter.tool_inputs.append({})
        actor.records.append({})
        support.journal_progress(folder, {}, inv, meter, actor, obs, 0, {})
        event = read(folder / 'failure-observations.json')[0]['analysis_failure_observation']
        assert censor_class({'analysis_failure_observation': event}) == 'INFRA_CENSORED_PRE_OUTPUT'
        assert event['tool_executions_before_failure'] == 0
    finally:
        common.ROOT = support.ROOT = runtime.ROOT = ROOT
        runtime.MacroROSA = original
    report = {'pass': True, 'controls': results, 'control_count': len(results),
        'fixture_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'effective_wire_settings': {k: params[k] for k in ['model', 'think', 'stream', 'options']},
        'wire_matches_unchanged_configured_adapter': True,
        'streaming_note': 'Pinned adapter has streaming=False at the LangChain level but stream=True in Ollama wire parameters; behavior retained and explicitly reported.',
        'failure_activity_preserved': True, 'retry_eligibility_503_only_tested_with_429_and_timeout': True,
        'model_requests': 0, 'live_results_claimed': False, 'frozen_inputs': common.verify()}
    (out / 'VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'zero_model_validation': 'PASS', 'controls': len(results), 'model_requests': 0}))


if __name__ == '__main__':
    main()
