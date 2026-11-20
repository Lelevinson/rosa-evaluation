"""Six deterministic macro controls and an independent ROS observer, no LLM."""
from copy import deepcopy
import os
from rosa_reliability.macro import MacroSession
from rosa_reliability.reference import make_reference_tools
from experiments.ur5e_transfer_v1.arm import ArmSimulator, ArmTransport, JOINTS, reset, configure_fault
from .design import catalogue, cases, FaultTransport
from .runner import DESTINATION, write
from .scoring import score


def run_controls(folder, controller, observer):
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    for spec in cases('gazebo'):
        origin = reset(controller, observer)
        configure_fault(controller, spec)
        controller.records.clear()
        transport = FaultTransport(controller, spec)
        session = MacroSession(transport, catalogue('gazebo'), program_managed=True, tolerance=.025)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        if spec['fault'] == 'transient_after':
            tools['verify_outcome'].invoke({})
        observation = session.observations[-1]
        values = observation['observed_values']
        missing = any(v is None for group in values.values() for v in group.values())
        reached = not missing and all(abs(values[n][k] - v) <= .025
            for n, group in session.targets.items() for k, v in group.items())
        classification = 'UNKNOWN' if missing else 'SUCCESS' if reached else 'FAILURE'
        report = tools['submit_report'].invoke({'status': classification,
            'observation_id': observation['observation_id']})
        # Simulate only the trusted terminal marker for the no-model reference.
        session.events.append({'type': 'terminal', 'actor': 'deterministic_control'})
        actual = {'/ur5e': observer.read('/ur5e', list(JOINTS))}
        scored = score(session, spec, transport, '{}', [], catalogue('gazebo'), .025, actual)
        row = {'case': spec['id'], 'pass': scored['pass'], 'score': scored, 'report': report,
            'independent_observation': actual, 'observer_record': deepcopy(observer.records[-1]),
            'session': session.snapshot(), 'reset': origin, 'model_calls': 0,
            'transport_records': deepcopy(transport.records)}
        rows.append(row)
        write(folder / 'result.json', {'pass': all(r['pass'] for r in rows), 'rows': rows})
    if not all(r['pass'] for r in rows):
        raise RuntimeError('deterministic_macro_controls_failed')
    return rows


def main():
    os.environ['ROS_DOMAIN_ID'] = '213'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    folder = DESTINATION / 'deterministic-preflight'
    folder.mkdir(parents=True, exist_ok=False)
    simulator = ArmSimulator(folder / 'simulator')
    controller = observer = None
    try:
        simulator.start()
        controller, observer = ArmTransport(), ArmTransport(read_only=True)
        rows = run_controls(folder / 'controls', controller, observer)
        write(folder / 'result.json', {'pass': all(r['pass'] for r in rows), 'cases': len(rows)})
    finally:
        for item in (controller, observer):
            if item:
                item.close()
        write(folder / 'cleanup.json', simulator.close())


if __name__ == '__main__':
    main()
