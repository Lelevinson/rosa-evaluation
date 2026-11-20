"""Matched controller reference on the same two Gazebo targets and faults."""
import json
import os
import time
from .cases import GAZEBO_CASES
from .runner import DESTINATION
from .simulator import Simulator


def main():
    from rosa_reliability.ros_joint import JointTransport
    os.environ['ROS_DOMAIN_ID'] = '188'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    destination = DESTINATION / 'deterministic-reference'
    destination.mkdir(exist_ok=False)
    simulator = Simulator(destination / 'simulator')
    controller = observer = None
    rows = []
    try:
        simulator.start()
        controller, observer = JointTransport(), JointTransport(read_only=True)
        for spec in GAZEBO_CASES:
            controller.suppress_commands = False
            controller.read('/rosa_arm', ['shoulder'])
            controller.write('/rosa_arm', {'shoulder': 0.0})
            reset = observer.read('/rosa_arm', ['shoulder'])
            if abs(reset['shoulder']) > 0.015:
                raise RuntimeError('deterministic_reset_failed')
            controller.suppress_commands = spec['fault'] == 'drop'
            start = time.monotonic()
            offset = len(controller.records)
            initial = controller.read('/rosa_arm', ['shoulder'])
            receipt = controller.write('/rosa_arm', spec['targets']['/rosa_arm'])
            verified = controller.read('/rosa_arm', ['shoulder'])
            wall = time.monotonic() - start
            actual = observer.read('/rosa_arm', ['shoulder'])
            target = spec['targets']['/rosa_arm']['shoulder']
            observed_status = 'SUCCESS' if abs(verified['shoulder'] - target) <= 0.015 else 'FAILURE'
            oracle_status = 'SUCCESS' if abs(actual['shoulder'] - target) <= 0.015 else 'FAILURE'
            rows.append({'case': spec['id'], 'target': target, 'initial': initial, 'receipt': receipt,
                'verified': verified, 'separate_observer': actual, 'reset_observation': reset,
                'status': observed_status, 'expected_status': spec['expected_status'],
                'pass': observed_status == oracle_status == spec['expected_status'],
                'native_skill_operations': 3, 'outside_trial_oracle_reads': 1, 'model_calls': 0,
                'wall_seconds': wall, 'transport_records': controller.records[offset:]})
            print('Matched deterministic reference:', spec['id'], rows[-1]['pass'], flush=True)
    finally:
        for item in (controller, observer):
            if item:
                item.close()
        result = {'actor': 'deterministic_controller_not_an_llm', 'rows': rows, 'cleanup': simulator.close(),
                  'ordering': 'after_live_backends', 'same_low_level_skill_and_observer': True}
        (destination / 'result.json').write_text(json.dumps(result, indent=2))
    if len(rows) != 2 or not all(r['pass'] for r in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
