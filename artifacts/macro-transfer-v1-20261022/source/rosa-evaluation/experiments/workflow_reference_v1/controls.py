"""Deterministic six-joint controls, independently observed, no model calls."""
from copy import deepcopy
import json
import os
from pathlib import Path
from rosa_reliability.reference import ReferenceWorkflowSession, make_reference_tools
from experiments.ur5e_transfer_v1.arm import ArmSimulator, ArmTransport, JOINTS, reset, configure_fault
from .design import catalogue, cases
from .runner import DESTINATION, write


def run_controls(folder, controller, observer):
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    for spec in cases('gazebo'):
        origin = reset(controller, observer)
        configure_fault(controller, spec)
        controller.records.clear()
        session = ReferenceWorkflowSession(controller, catalogue('gazebo'), program_managed=True, tolerance=.025)
        tools = {t.name: t for t in make_reference_tools(session)}
        tools['select_skill'].invoke({'skill_id': spec['skill']})
        observation = session.observations[-1]
        values = observation['observed_values']
        missing = any(v is None for g in values.values() for v in g.values())
        attained = not missing and all(abs(values[n][k] - v) <= .025
            for n, g in session.targets.items() for k, v in g.items())
        status = 'UNKNOWN' if missing else 'SUCCESS' if attained else 'FAILURE'
        report = tools['submit_report'].invoke({'status': status, 'observation_id': observation['observation_id']})
        actual = observer.read('/ur5e', list(JOINTS))
        actual_goal = all(abs(actual[k] - v) <= .025 for k, v in session.targets['/ur5e'].items())
        row = {'case': spec['id'], 'pass': report['report_accepted'] and status == spec['expected'] and
            (actual_goal if status == 'SUCCESS' else not actual_goal),
            'report': report, 'independent_observation': actual, 'observer_record': deepcopy(observer.records[-1]),
            'session': session.snapshot(), 'reset': origin, 'model_calls': 0}
        rows.append(row)
        write(folder / 'result.json', {'pass': all(r['pass'] for r in rows), 'rows': rows})
    if not all(r['pass'] for r in rows):
        raise RuntimeError('deterministic_reference_controls_failed')
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


if __name__ == '__main__': main()
