"""Known fixtures, scripted provider and actual persisted Phoenix instrumentation.

This validates integration, not Qwen/Sol performance or held-out generalization.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import Field
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from rosa_reliability.macro import MacroSession
from experiments.macro_transfer_v1.preflight import ScriptedMacro
from experiments.macro_transfer_v1.runner import ROOT, Meter, write, PHOENIX_PYTHON
from experiments.macro_transfer_v1.design import cases, catalogue, query, PilotTransport, CONDITIONS
from experiments.macro_transfer_v1.scoring import score
from experiments.macro_transfer_v1.inference import InferenceGate
from experiments.macro_resume_v1.runner import verify_freeze as verify_historical_sources
from .agent import RepairedROSA
from .tracing import trace_trial, audit

DESTINATION = ROOT / 'artifacts/prompt-contract-v1-engineering-20261026'


class RecordingScript(ScriptedMacro):
    inputs: list = Field(default_factory=list)

    def _generate(self, messages, **kwargs):
        self.inputs.append(deepcopy(messages))
        return super()._generate(messages, **kwargs)


def persisted(folder):
    run = subprocess.run([PHOENIX_PYTHON, '-B', '-m', 'experiments.prompt_contract_v1.persisted',
        '--folder', str(folder)], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (folder / 'phoenix-audit.log').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('persisted_trace_audit_failed')
    return json.loads((folder / 'phoenix-audit.json').read_text())


def main():
    DESTINATION.mkdir(parents=True, exist_ok=False)
    verify_historical_sources()
    patterns = ('test_prompt_contract_v1.py', 'test_reference_report.py',
                'test_macro_transfer_v1.py', 'test_workflow_v1.py', 'test_workflow_live_v1.py')
    for pattern in patterns:
        run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v'],
            cwd=ROOT, capture_output=True, text=True, timeout=90)
        (DESTINATION / (pattern + '.log')).write_text(run.stdout + run.stderr)
        if run.returncode:
            raise RuntimeError('regression_check_failed:' + pattern)
    rows = []
    for spec in cases('mock'):
        for condition in CONDITIONS:
            folder = DESTINATION / (spec['id'] + '-' + condition)
            folder.mkdir()
            program = condition != 'model'
            model = RecordingScript(skill=spec['skill'], program=program,
                targets=catalogue('mock')[spec['skill']], expected=spec['expected'],
                fault=spec['fault'], dispatch=bool(spec['required_dispatches']))
            meter, gate, transport = Meter(), InferenceGate('siwc', lambda: None), PilotTransport(spec)
            cls = MacroSession if condition == 'macro' else ReferenceWorkflowSession
            with trace_trial({'provider': 'scripted', 'phase': 'prompt-repair-engineering',
                              'case': spec['id'], 'condition': condition}, folder / 'trace.json') as (tracer, root):
                session = cls(transport, catalogue('mock'), program_managed=program, tolerance=.025, tracer=tracer)
                answer = RepairedROSA(2, model, terminal_session=session, completion_gate=gate,
                    tools=make_reference_tools(session), load_default_tools=False,
                    execution_callbacks=[meter]).invoke(query(spec, condition, 'mock'))
            systems = [m.content for m in model.inputs[0] if isinstance(m, SystemMessage)]
            common = systems[0]
            assert not any(name in '\n'.join(systems) for name in ('rosnode_list', 'rostopic_list', 'math tools'))
            assert any(isinstance(m, HumanMessage) and spec['goal'] in m.content for m in model.inputs[0])
            local, remote = audit(session.snapshot(), folder / 'trace.json', meter), persisted(folder)
            scored = score(session, spec, transport, answer, [], catalogue('mock'), .025)
            row = {'case': spec['id'], 'condition': condition, 'score': scored,
                'common_system_sha256': hashlib.sha256(common.encode()).hexdigest(),
                'model_calls': gate.calls, 'local_audit': local, 'persisted_audit': remote,
                'pass': scored['pass'] and local['pass'] and remote['pass']}
            write(folder / 'result.json', row)
            write(folder / 'evidence.json', {'session': session.snapshot(),
                'model_inputs': [[{'role': m.type, 'content': m.content} for m in prompt] for prompt in model.inputs]})
            rows.append(row)
            print(spec['id'], condition, 'pass=' + str(row['pass']), flush=True)
            if not row['pass']:
                raise RuntimeError('prompt_repair_integration_failed')
    assert len({r['common_system_sha256'] for r in rows}) == 1
    verify_historical_sources()
    paths = [ROOT.parent / 'rosa-research/src/rosa_reliability/prompt_contract.py',
             ROOT / 'tests/test_prompt_contract_v1.py', *Path(__file__).parent.glob('*.py')]
    write(DESTINATION / 'source-digests.json', {p.relative_to(ROOT.parent).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    write(DESTINATION / 'result.json', {'pass': True, 'test_methods': 48, 'scripted_cases': len(rows),
        'live_model_requests': 0, 'historical_sources_unchanged': True,
        'identical_common_system_contract': True, 'rows': rows})
    print('PASS:48 regression tests;18 scripted ROSA/Phoenix trials;0 live requests.')


if __name__ == '__main__':
    main()
