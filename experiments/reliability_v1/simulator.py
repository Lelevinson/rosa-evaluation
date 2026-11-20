"""Own isolated simulator/bridge child processes; never kill unrelated sessions."""
import os
from pathlib import Path
import signal
import subprocess


class Simulator:
    def __init__(self, destination):
        self.destination = Path(destination)
        self.destination.mkdir(parents=True, exist_ok=True)
        self.children, self.logs = [], []

    def start(self):
        import rosa_reliability
        assets = Path(rosa_reliability.__file__).parent / 'sim'
        os.environ['GZ_PARTITION'] = 'rosa-reliability-v1-' + str(os.getpid())
        for name, argv in (
            ('gazebo', ['gz', 'sim', '-s', '-r', str(assets / 'arm.sdf')]),
            ('bridge', ['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', '--ros-args',
                        '-p', 'config_file:=' + str(assets / 'bridge.yaml')]),
        ):
            log = (self.destination / (name + '.log')).open('w')
            self.logs.append(log)
            self.children.append(subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, start_new_session=True))

    def close(self):
        result = []
        for child in reversed(self.children):
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGINT)
                try:
                    child.wait(8)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(3)
            result.append({'pid': child.pid, 'returncode': child.returncode})
        for log in self.logs:
            log.close()
        return result


def main():
    import json
    import sys
    from rosa_reliability.ros_joint import JointTransport
    destination = Path(sys.argv[1])
    os.environ['ROS_DOMAIN_ID'] = '183'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    simulator = Simulator(destination)
    agent = observer = None
    rows = []
    try:
        simulator.start()
        agent, observer = JointTransport(), JointTransport(read_only=True)
        print('initial', observer.read('/rosa_arm', ['shoulder']), flush=True)
        for target in (0.25, -0.35, 0.0):
            receipt = agent.write('/rosa_arm', {'shoulder': target})
            actual = observer.read('/rosa_arm', ['shoulder'])
            passed = abs(actual['shoulder'] - target) < 0.015
            rows.append({'target': target, 'receipt': receipt, 'independent_observation': actual, 'pass': passed})
            print(rows[-1], flush=True)
        agent.suppress_commands = True
        receipt = agent.write('/rosa_arm', {'shoulder': 0.3})
        actual = observer.read('/rosa_arm', ['shoulder'])
        rows.append({'fault': 'accepted_request_command_publication_suppressed', 'target': 0.3,
                     'receipt': receipt, 'independent_observation': actual,
                     'pass': abs(actual['shoulder'] - 0.3) > 0.1})
        assert all(row['pass'] for row in rows), rows
    finally:
        for transport in (agent, observer):
            if transport:
                transport.close()
        cleanup = simulator.close()
        (destination / 'deterministic.json').write_text(json.dumps({'rows': rows, 'cleanup': cleanup}, indent=2))


if __name__ == '__main__':
    main()
