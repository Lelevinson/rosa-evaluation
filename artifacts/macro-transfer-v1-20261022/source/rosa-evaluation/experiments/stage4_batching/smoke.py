"""Non-paid native-message ROSA/real-ROS/Phoenix acceptance before live models."""
import argparse
import json
from pathlib import Path
import subprocess
from uuid import uuid4

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from rosa_backends import create_mock_agent
from rosa.prompts import RobotSystemPrompts

from ..config import ROOT, phoenix_project, phoenix_url
from ..tracing import trace_run
from .environment import RealEnvironment
from .gateway import Gateway, make_tools
from .tasks import tasks, INSTRUCTIONS
from .runner import CAMPAIGN, PROJECT
from .trace_accounting import counts


class ScriptedModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='trace-smoke')
    args = parser.parse_args()
    if '/' in args.name or '\\' in args.name or args.name in ('.', '..'):
        raise ValueError('expected_single_identifier')
    folder = CAMPAIGN / args.name
    folder.mkdir(exist_ok=False)
    spec = next(s for s in tasks() if s['template'] == 'one_parameter')
    costs = json.loads((ROOT / 'artifacts/stage4-policy-20261021/ros-calibration/calibration.json').read_text())['cost_seconds']
    environment = RealEnvironment(folder / 'ros', 177)
    run_id = str(uuid4())
    (folder / 'metadata.json').write_text(json.dumps({'run_id': run_id, 'live_model_requests': 0}))
    try:
        environment.start()
        environment.reset(spec)
        gateway = Gateway(spec, 'amortized_batching', environment.invoke, costs)
        messages = [AIMessage(content='', tool_calls=[{'name': 'read_parameter_evidence',
            'args': {'node_name': '/jtvr_alpha', 'names': ['alpha'], 'report_names': ['alpha'],
                     'expected_values': {}, 'strategy': 'direct'}, 'id': 'read-one'}]),
            AIMessage(content='', tool_calls=[{'name': 'submit_parameter_report',
                'args': {'outcome': 'success', 'observed_values': {'/jtvr_alpha': {'alpha': 1}},
                         'acknowledged_details': []}, 'id': 'report-one'}]), AIMessage(content='Done.')]
        llm = ScriptedModel(responses=messages)
        with trace_run(True, project=PROJECT, metadata={'run_id': run_id, 'stage': 'nonpaid_batching_trace_smoke'}) as span:
            agent = create_mock_agent(llm, make_tools(gateway.call), max_iterations=5,
                prompts=RobotSystemPrompts(critical_instructions=INSTRUCTIONS))
            answer = agent.invoke(spec['query'])
        evidence = gateway.score(environment.oracle(spec), [])
    finally:
        environment.close()
    phoenix_python = str(Path.home() / '.local/share/rosa-envs/phoenix/bin/python')
    exported = folder / 'trace.json'
    subprocess.run([phoenix_python, '-B', '-m', __package__ + '.trace_export',
                    '--run-id', run_id, '--output', str(exported)], check=True, stdout=subprocess.DEVNULL)
    trace = json.loads(exported.read_text())
    spans, summary = trace['spans'], trace['summary']
    accounting = counts(spans)
    passed = (evidence['strict_contract_pass'] and answer == 'Done.' and summary['trace_complete']
              and summary['llm_calls'] == 3 and accounting['model_tool_spans'] == 2
              and accounting['native_tool_spans'] == len(environment.commands))
    (folder / 'result.json').write_text(json.dumps({'passed': passed, 'run_id': run_id,
        'evidence': evidence, 'trace_summary': summary, 'actor_accounting': accounting,
        'spans': spans, 'live_model_requests': 0}, indent=2))
    print(json.dumps({'passed': passed, 'trace_summary': summary}))
    if not passed:
        raise RuntimeError('controlled_trace_acceptance_failed')


if __name__ == '__main__':
    main()
