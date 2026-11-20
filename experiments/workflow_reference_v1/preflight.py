"""Scripted public-tool-history provider and Phoenix round-trip checks."""
import json
import subprocess
import sys
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from .design import cases, catalogue, PilotTransport, query
from .inference import InferenceGate, LiveROSA
from .runner import DESTINATION, ROOT, Meter, phoenix_audit, score, write
from .tracing import audit, trace_trial


class ScriptedReference(BaseChatModel):
    skill: str
    program: bool
    targets: dict
    expected: str
    index: int = 0
    @property
    def _llm_type(self): return 'scripted-reference-preflight-not-live'
    def bind_tools(self, tools, **kwargs): return self
    def _generate(self, messages, **kwargs):
        node = next(iter(self.targets))
        plan = [('select_skill', {'skill_id': self.skill})]
        if not self.program:
            plan.append(('read_state', {'nodes': [node]}))
            if self.expected != 'UNKNOWN':
                plan.append(('write_state', {'node_name': node, 'values': self.targets[node]}))
            plan.append(('verify_outcome', {}))
        if self.index < len(plan):
            name, arguments = plan[self.index]
        else:
            def find(value):
                if isinstance(value, dict):
                    if 'observation_id' in value: return value['observation_id']
                    for child in value.values():
                        result = find(child)
                        if result: return result
            identifier = next((found for m in reversed(messages) if isinstance(m, ToolMessage)
                               and (found := find(json.loads(m.content)))), None)
            if identifier is None: raise RuntimeError('no_public_observation_reference')
            name, arguments = 'submit_report', {'status': self.expected, 'observation_id': identifier}
        self.index += 1
        message = AIMessage(content='', tool_calls=[{'name': name, 'args': arguments,
            'id': 'script-' + str(self.index), 'type': 'tool_call'}],
            usage_metadata={'input_tokens': 100, 'output_tokens': 10, 'total_tokens': 110})
        return ChatResult(generations=[ChatGeneration(message=message)])


def main():
    folder = DESTINATION / 'preflight'
    folder.mkdir(parents=True, exist_ok=False)
    for pattern in ('test_reference_report.py', 'test_workflow_v1.py', 'test_workflow_live_v1.py'):
        run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v'],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        (folder / (pattern + '.log')).write_text(run.stdout + run.stderr)
        if run.returncode: raise RuntimeError('offline_test_failed:' + pattern)
    rows = []
    for spec in cases('mock'):
        for program in (False, True):
            trial = folder / (spec['id'] + ('-program' if program else '-model'))
            trial.mkdir()
            model = ScriptedReference(skill=spec['skill'], program=program,
                targets=catalogue('mock')[spec['skill']], expected=spec['expected'])
            meter, gate, transport = Meter(), InferenceGate('ollama', lambda: None), PilotTransport(spec)
            with trace_trial({'provider': 'scripted', 'case': spec['id'], 'program': program}, trial / 'trace.json') as (tracer, root):
                session = ReferenceWorkflowSession(transport, catalogue('mock'), program_managed=program, tracer=tracer)
                answer = LiveROSA(2, model, terminal_session=session, completion_gate=gate,
                    tools=make_reference_tools(session), load_default_tools=False, execution_callbacks=[meter]).invoke(query(spec, program, 'mock'))
            local, persisted = audit(session.snapshot(), trial / 'trace.json', meter), phoenix_audit(trial)
            scored = score(session, spec, transport, answer, [], catalogue('mock'), .01)
            row = {'score': scored, 'local_audit': local, 'persisted_audit': persisted,
                   'pass': scored['pass'] and local['pass'] and persisted['pass']}
            write(trial / 'result.json', row)
            rows.append(row)
    write(folder / 'result.json', {'pass': all(r['pass'] for r in rows), 'scripted_trials': len(rows), 'rows': rows})
    if not all(r['pass'] for r in rows): raise RuntimeError('reference_preflight_failed')
    print('PASS: 8 reference + 16 workflow + 9 inference/design tests; 8 persisted scripted traces')


if __name__ == '__main__': main()
