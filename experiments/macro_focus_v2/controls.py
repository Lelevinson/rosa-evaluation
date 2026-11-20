"""Resolved-goal deterministic reference, not natural-language understanding."""
from copy import deepcopy
from rosa_reliability.macro import MacroSession
from rosa_reliability.reference import make_reference_tools
from rosa_reliability.ros_arm import JOINTS
from experiments.prompt_live_v1.runner import write
from .design import cases, catalogue, FaultTransport, initialize
from .scoring import score


def run_controls(folder, controller, observer):
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    for spec in cases():
        origin = initialize(controller, observer, spec)
        transport = FaultTransport(controller, spec)
        session = MacroSession(transport, catalogue(), program_managed=True, tolerance=.025)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        if spec['fault'] == 'transient_before':
            tools['read_state'].invoke({'nodes': ['/ur5e']})
            tools['write_state'].invoke({'node_name': '/ur5e', 'values': catalogue()[spec['skill']]['/ur5e']})
            tools['verify_outcome'].invoke({})
        elif spec['fault'] == 'missing_after':
            tools['verify_outcome'].invoke({})
        observation = session.observations[-1]
        values = observation['observed_values']
        missing = any(v is None for group in values.values() for v in group.values())
        reached = not missing and all(abs(values[n][k] - v) <= .025
            for n, group in session.targets.items() for k, v in group.items())
        report = tools['submit_report'].invoke({'status': 'UNKNOWN' if missing else 'SUCCESS' if reached else 'FAILURE',
            'observation_id': observation['observation_id']})
        session.events.append({'type': 'terminal', 'actor': 'deterministic_control'})
        actual = {'/ur5e': observer.read('/ur5e', list(JOINTS))}
        scored = score(session, spec, transport, '{}', [], catalogue(), .025, actual)
        rows.append({'case': spec['id'], 'pass': scored['pass'], 'score': scored,
            'report': report, 'session': session.snapshot(), 'reset': origin, 'model_calls': 0,
            'independent_observation': actual, 'observer_record': deepcopy(observer.records[-1]),
            'transport_records': deepcopy(transport.records)})
        write(folder / 'result.json', {'pass': all(r['pass'] for r in rows), 'rows': rows})
    if not all(r['pass'] for r in rows):
        raise RuntimeError('fresh_deterministic_controls_failed')
    return rows
