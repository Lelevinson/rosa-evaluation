"""No live inference: validate composed loop and actual Phoenix persistence."""
import json
from pathlib import Path
import subprocess
import sys

from rosa_reliability.workflow import WorkflowSession, make_workflow_tools
from experiments.workflow_v1.pilot import Scripted, call
from .design import CASES, SKILLS, PilotTransport, query
from .inference import InferenceGate, LiveROSA
from .runner import DESTINATION, ROOT, Meter, phoenix_audit, score, write
from .tracing import audit, trace_trial


def message(name, args):
    return call(name, args).model_copy(update={'usage_metadata': {
        'input_tokens': 100, 'output_tokens': 10, 'total_tokens': 110}})


def main():
    folder = DESTINATION / 'preflight'
    folder.mkdir(parents=True, exist_ok=False)
    run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_workflow_live_v1.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (folder / 'tests.log').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('offline_live_runner_checks_failed')
    results = []
    for spec in (CASES[0], CASES[1], CASES[3]):
        for program in (False, True):
            trial = folder / f'{spec["id"]}-{"program" if program else "model"}'
            trial.mkdir()
            targets = SKILLS[spec['skill']]
            missing = spec['fault'] == 'missing'
            observed = {n: {k: None for k in g} for n, g in targets.items()} if missing else targets
            planned = [message('select_skill', {'skill_id': spec['skill']})]
            if not program:
                planned.append(message('read_state', {'nodes': ['/bench_arm']}))
                if not missing:
                    planned.append(message('write_state', {'node_name': '/bench_arm', 'values': targets['/bench_arm']}))
                planned.append(message('verify_outcome', {}))
            planned.append(message('submit_report', {'status': spec['expected'], 'observed_values': observed}))
            model, meter = Scripted(responses=planned), Meter()
            gate = InferenceGate('ollama', lambda: None)
            transport = PilotTransport(spec)
            with trace_trial({'provider': 'scripted-preflight', 'case': spec['id'], 'program': program}, trial / 'trace.json') as (tracer, root):
                session = WorkflowSession(transport, SKILLS, program_managed=program, tracer=tracer)
                answer = LiveROSA(2, model, completion_gate=gate, terminal_session=session,
                    tools=make_workflow_tools(session), load_default_tools=False,
                    execution_callbacks=[meter]).invoke(query(spec, program))
            local = audit(session.snapshot(), trial / 'trace.json', meter)
            persisted = phoenix_audit(trial)
            result = {'case': spec['id'], 'program': program, 'score': score(session, spec, transport, answer, []),
                'local_audit': local, 'persisted_audit': persisted}
            result['pass'] = result['score']['pass'] and local['pass'] and persisted['pass']
            write(trial / 'result.json', result)
            results.append(result)
    result = {'pass': len(results) == 6 and all(r['pass'] for r in results), 'scripted_trials': results,
              'no_live_model_requests': True, 'unit_tests_passed': True}
    write(folder / 'result.json', result)
    print(json.dumps({'pass': result['pass'], 'persisted_scripted_traces': len(results)}))
    if not result['pass']:
        raise SystemExit(1)


if __name__ == '__main__': main()
