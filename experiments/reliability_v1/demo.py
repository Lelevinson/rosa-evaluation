"""Interactive one-skill demonstration, separate from frozen validation cases."""
import argparse
from contextlib import nullcontext
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('deterministic', 'ollama', 'siwc'), default='deterministic')
    parser.add_argument('--configuration', choices=('A', 'B', 'C', 'D'), default='A')
    parser.add_argument('--target', type=float, default=0.2)
    args = parser.parse_args()
    if not -0.6 <= args.target <= 0.6:
        parser.error('target must be within [-0.6, 0.6] radians')
    from dotenv import load_dotenv
    from rosa.prompts import RobotSystemPrompts
    from rosa_backends import create_model, create_mock_agent
    from rosa_reliability import ExecutionSession, ControlledStop, make_tools
    from rosa_reliability.ros_joint import JointTransport
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from langchain_core.callbacks import BaseCallbackHandler
    from .cases import ARMS, INSTRUCTIONS
    from .simulator import Simulator
    from .tracing import trace_trial
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / '.env')
    os.environ['ROS_DOMAIN_ID'] = '187'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    run_id = 'demo-' + datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = root / 'artifacts/reliability-demos' / run_id
    folder.mkdir(parents=True, exist_ok=False)
    simulator = Simulator(folder / 'simulator')
    transport = observer = llm = None
    class Cap(BaseCallbackHandler):
        raise_error = True
        calls = 0
        def on_chat_model_start(self, serialized, messages, **kw):
            if self.calls >= 8:
                raise ControlledStop('demo_request_cap_reached')
            self.calls += 1
    cap = Cap()
    result = None
    try:
        scope = interactive_session(request_budget=8) if args.backend == 'siwc' else nullcontext(None)
        with scope as auth:
            if auth:
                llm = create_model('siwc', model='gpt-6.1-sol',
                                   siwc_transport=SiwcBackend(request_budget=8, token_provider=auth.access_token))
            elif args.backend == 'ollama':
                llm = create_model('ollama', base_url=os.getenv('OLLAMA_BASE_URL'), num_ctx=8192, use_mmap=True)
            simulator.start()
            transport, observer = JointTransport(), JointTransport(read_only=True)
            observer.read('/rosa_arm', ['shoulder'])
            target = {'/rosa_arm': {'shoulder': args.target}}
            with trace_trial({'run_id': run_id, 'backend': args.backend}, folder / 'trace.json') as (tracer, span):
                session = ExecutionSession(transport, target, structured_feedback=ARMS[args.configuration][0],
                    automatic_verification=ARMS[args.configuration][1], tolerance=0.015, write_limit=1, tracer=tracer)
                tools = make_tools(session)
                if llm:
                    llm.callbacks = [cap]
                    agent = create_mock_agent(llm, tools, max_iterations=8,
                        prompts=RobotSystemPrompts(critical_instructions=INSTRUCTIONS))
                    def expired(signum, frame):
                        raise ControlledStop('demo_wall_limit_180_seconds')
                    signal.signal(signal.SIGALRM, expired)
                    signal.setitimer(signal.ITIMER_REAL, 180)
                    try:
                        answer = agent.invoke('Requested target values: ' + json.dumps(target) + '. Read, move only if needed, verify, and submit_report.')
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                else:
                    registry = {t.name: t for t in tools}
                    initial = registry['read_state'].invoke({'nodes': ['/rosa_arm']})
                    if abs(initial['observed_values']['/rosa_arm']['shoulder'] - args.target) > 0.015:
                        registry['write_state'].invoke({'node_name': '/rosa_arm', 'values': target['/rosa_arm']})
                    evidence = registry['verify_outcome'].invoke({})
                    registry['submit_report'].invoke({'status': 'SUCCESS' if evidence['goal_reached'] else 'FAILURE',
                                                       'observed_values': evidence['observed_values']})
                    answer = 'Deterministic reference completed.'
            actual = observer.read('/rosa_arm', ['shoulder'])
            result = {'backend': args.backend, 'target': args.target, 'independent_observation': actual,
                      'goal_attained': abs(actual['shoulder'] - args.target) <= 0.015, 'answer': answer,
                      'model_calls': cap.calls, 'session': session.snapshot()}
            result['report_accepted'] = bool(session.reports and session.reports[-1]['accepted'])
            result['completed_verified_task'] = result['goal_attained'] and result['report_accepted']
            result['report_source'] = 'model_generated_tool_call' if llm else 'deterministic_reference'
            if not llm:
                result['ledger_actor_note'] = 'Library model labels denote the tool-facing API path; this demo generated those calls deterministically, with zero LLM requests.'
            (folder / 'result.json').write_text(json.dumps(result, indent=2))
            print(json.dumps({k: v for k, v in result.items() if k not in ('session', 'ledger_actor_note')}, indent=2))
            print('Evidence:', folder)
    finally:
        for item in (transport, observer):
            if item:
                item.close()
        cleanup = simulator.close()
        (folder / 'cleanup.json').write_text(json.dumps(cleanup))
        if llm is not None and args.backend == 'siwc':
            llm.close()
    if result is not None and not result['completed_verified_task']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
