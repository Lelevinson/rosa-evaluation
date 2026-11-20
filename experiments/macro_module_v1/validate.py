"""M1 engineering checks: scripted ROSA, persisted traces, deterministic Gazebo.

No OAuth or actual model service. Every invocation creates a new evidence folder.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from rosa_reliability.macro_agent import MacroROSA
from rosa_reliability.macro_demo import MemoryTransport, demo_registry
from .tracing import Meter, audit, trace_check

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'artifacts/macro-module-v1-20261027'


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


class ScriptedCaller(BaseChatModel):
    """Fixture-selected answers prove execution plumbing, not model decisions."""
    invocation: object
    fault: str
    index: int = 0

    @property
    def _llm_type(self): return 'm1-scripted-not-a-live-model'
    def bind_tools(self, tools, **kwargs): return self

    def _generate(self, messages, **kwargs):
        index, self.index = self.index, self.index + 1
        steps = [('select_skill', {'skill_id': 'station.right'})]
        if self.invocation.mode == 'primitives':
            steps.append(('read_state', {'nodes': ['/demo_arm']}))
            if self.fault not in ('already', 'missing_before'):
                steps.append(('write_state', {'node_name': '/demo_arm', 'values': {'yaw': 0.2, 'pitch': 0.1}}))
            steps.append(('verify_outcome', {}))
        if index < len(steps):
            name, args = steps[index]
        else:
            if index != len(steps): raise AssertionError('unexpected_model_acknowledgment')
            evidence = self.invocation.session.observations[-1]
            values = evidence['observed_values']['/demo_arm']
            target = self.invocation.catalogue['station.right']['/demo_arm']
            status = 'UNKNOWN' if any(v is None for v in values.values()) else 'SUCCESS' if all(
                abs(values[k] - v) <= self.invocation.limits.tolerance for k, v in target.items()) else 'FAILURE'
            name, args = 'submit_report', {'status': status, 'observation_id': evidence['observation_id']}
        response = AIMessage(content='', tool_calls=[{'name': name, 'args': args,
            'id': 'scripted-' + str(index), 'type': 'tool_call'}],
            usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15},
            response_metadata={'finish_reason': 'stop'})
        return ChatResult(generations=[ChatGeneration(message=response)])


def persisted(folder):
    run = subprocess.run(['/home/martin/.local/share/rosa-envs/phoenix/bin/python', '-B', '-m',
        'experiments.macro_module_v1.persisted', '--folder', str(folder)], cwd=ROOT,
        capture_output=True, text=True, timeout=60)
    (folder / 'phoenix-audit.log').write_text(run.stdout + run.stderr)
    if run.returncode: raise RuntimeError('persisted_trace_audit_failed')
    return json.loads((folder / 'phoenix-audit.json').read_text())


def scripted(folder):
    rows = []
    for mode in ('primitives', 'macro'):
        for fault in ('none', 'already', 'ineffective', 'partial', 'missing_before', 'missing_after'):
            trial = folder / (mode + '-' + fault)
            trial.mkdir()
            initial = {'yaw': 0.2, 'pitch': 0.1} if fault == 'already' else None
            transport = MemoryTransport(initial, fault=fault)
            meter = Meter()
            with trace_check(trial / 'trace.json', {'mode': mode, 'case': fault, 'decision_actor': 'scripted_fixture'}) as tracer:
                invocation = demo_registry().open(transport, mode=mode, tracer=tracer)
                model = ScriptedCaller(invocation=invocation, fault=fault)
                agent = MacroROSA(model, invocation, backend='scripted', callbacks=[meter])
                answer = agent.invoke('Choose the station.right skill.')
                report = json.loads(answer)
                snapshot = invocation.snapshot()
            local = audit(snapshot, trial / 'trace.json', meter)
            write(trial / 'audit.json', local)
            expected = 'UNKNOWN' if fault.startswith('missing') else 'FAILURE' if fault in ('ineffective', 'partial') else 'SUCCESS'
            row = {'mode': mode, 'fault': fault, 'report': report, 'snapshot': snapshot,
                   'accounting': agent.inference_budget.snapshot(), 'local_audit': local,
                   'private_final_values': deepcopy(transport.values), 'writes': transport.writes,
                   'pass': report['report_accepted'] and report['status'] == expected and local['pass']}
            write(trial / 'result.json', row)
            row['phoenix_audit'] = persisted(trial)
            if not row['pass']: raise RuntimeError('scripted_contract_failed')
            rows.append(row)
            print(mode, fault, 'PASS', flush=True)
    return {'pass': len(rows) == 12 and all(r['pass'] for r in rows), 'live_model_requests': 0, 'rows': rows}


def gazebo(folder):
    from rosa_reliability.ur5e_macro_demo import run_checks
    meter = Meter()
    with trace_check(folder / 'trace.json', {'environment': 'gazebo', 'decision_actor': 'deterministic_demo'}) as tracer:
        result = run_checks(folder / 'demo', tracer=tracer, callbacks=[meter])
    combined = {key: [item for row in result['rows'] for item in row['snapshot'][key]]
                for key in ('events', 'operations')}
    local = audit(combined, folder / 'trace.json', meter)
    write(folder / 'audit.json', local)
    result['local_audit'] = local
    result['phoenix_audit'] = persisted(folder)
    result['pass'] = result['pass'] and local['pass'] and result['phoenix_audit']['pass']
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('scripted', 'gazebo'))
    args = parser.parse_args()
    os.environ.update(ROS_DOMAIN_ID='214', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    folder = DESTINATION / f'{args.stage}-{len(list(DESTINATION.glob(args.stage + "-*"))) + 1:02d}'
    folder.mkdir()
    def expired(signum, frame): raise TimeoutError('m1_external_timeout_300_seconds')
    prior = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, 300)
    result = {'pass': False, 'live_model_requests': 0}
    try:
        # Read-only verification, including all original source/evidence hashes.
        from experiments.macro_focus_v2.runner import verify_freeze
        verify_freeze()
        result = scripted(folder) if args.stage == 'scripted' else gazebo(folder)
        verify_freeze()
    except BaseException as error:
        result.update(error_type=type(error).__name__, error=str(error))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prior)
        write(folder / 'result.json', result)
    print(json.dumps({'stage': args.stage, 'pass': result['pass'], 'cases': len(result['rows']), 'live_model_requests': 0}))
    if not result['pass']: raise SystemExit(1)


if __name__ == '__main__': main()
