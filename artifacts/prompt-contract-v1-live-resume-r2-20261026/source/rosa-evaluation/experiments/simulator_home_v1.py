"""Simulator-only initial-position correction. No model or trial-policy change.

The installed UR macro already exposes initial_positions; pass HOME explicitly
through one new attribute in a generated copy of the original top-level Xacro.
Do not alter geometry, controllers, path tolerances or installed ROS packages.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from experiments.ur5e_transfer_v1.arm import ArmSimulator, ArmTransport, JOINTS
from rosa_reliability.ros_arm import HOME_POSE

INSTALLED = Path('/opt/ros/jazzy/share/ur_simulation_gz/urdf/ur_gz.urdf.xacro')
MARKER = 'transmission_hw_interface="$(arg transmission_hw_interface)"'


def home_description(original):
    if original.count(MARKER) != 1:
        raise RuntimeError('unsupported_installed_urdf_template')
    expression = '${dict(' + ','.join(k + '=' + repr(v) for k, v in HOME_POSE.items()) + ')}'
    return original.replace(MARKER, MARKER + '\n    initial_positions="' + expression + '"')


def verify_home(observed, tolerance=.025):
    if set(observed) != set(HOME_POSE) or any(abs(observed[k] - v) > tolerance
                                               for k, v in HOME_POSE.items()):
        raise RuntimeError('spawned_initial_state_is_not_documented_home')


class HomeSpawnSimulator(ArmSimulator):
    def start(self):
        original = INSTALLED.read_text()
        generated = home_description(original)
        description = self.folder / 'ur_gz_home.urdf.xacro'
        description.write_text(generated)
        (self.folder / 'ur_gz_original.urdf.xacro').write_text(original)
        (self.folder / 'description-change.json').write_text(json.dumps({
            'installed_path': str(INSTALLED), 'original_sha256': hashlib.sha256(original.encode()).hexdigest(),
            'generated_sha256': hashlib.sha256(generated.encode()).hexdigest(),
            'only_change': 'explicit_initial_positions_attribute', 'initial_positions': HOME_POSE}, indent=2))
        os.environ['GZ_PARTITION'] = 'rosa-home-spawn-v1-' + str(os.getpid())
        self.log = (self.folder / 'launch.log').open('w')
        self.child = subprocess.Popen(['ros2', 'launch', 'ur_simulation_gz', 'ur_sim_control.launch.py',
            'ur_type:=ur5e', 'launch_rviz:=false', 'gazebo_gui:=false',
            'initial_joint_controller:=joint_trajectory_controller', 'description_file:=' + str(description)],
            stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        from controller_manager_msgs.srv import ListControllers
        probe, queries = ArmTransport(read_only=True), []
        try:
            client = probe.node.create_client(ListControllers, '/controller_manager/list_controllers')
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                if not client.wait_for_service(timeout_sec=2):
                    continue
                future = client.call_async(ListControllers.Request())
                while not future.done() and time.monotonic() < deadline:
                    probe.executor.spin_once(timeout_sec=.05)
                if future.done() and future.result():
                    states = {c.name: c.state for c in future.result().controller}
                    queries.append({'at': time.monotonic(), 'states': states})
                    if states.get('joint_state_broadcaster') == 'active' and states.get('joint_trajectory_controller') == 'active':
                        observed = probe.read('/ur5e', list(JOINTS))
                        verify_home(observed)
                        (self.folder / 'readiness.json').write_text(json.dumps({'pass': True,
                            'outside_trial': True, 'queries': queries, 'observed_values': observed,
                            'sensor_record': probe.records[-1], 'spawn_home_verified': True}, indent=2))
                        return
                time.sleep(.05)  # startup polling only, no retries of commands
            raise RuntimeError('active_controllers_not_ready_within_120_seconds')
        finally:
            probe.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cold-starts', type=int, default=3)
    args = parser.parse_args()
    if args.cold_starts != 3:
        raise RuntimeError('this_diagnostic_is_fixed_at_three_cold_starts')
    from experiments.prompt_live_v1.runner import ROOT, write
    from experiments.macro_transfer_v1.controls import run_controls
    from experiments.macro_resume_v1.runner import verify_freeze as verify_history
    verify_history()
    os.environ.update(ROS_DOMAIN_ID='213', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    destination = ROOT / 'artifacts/simulator-home-v1-preflight-20261026'
    destination.mkdir(parents=True, exist_ok=False)
    check = subprocess.run([__import__('sys').executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
        '-p', 'test_simulator_home_v1.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    (destination / 'preflight.log').write_text(check.stdout + check.stderr)
    if check.returncode:
        raise RuntimeError('spawn_description_unit_checks_failed')
    paths = [Path(__file__), ROOT / 'tests/test_simulator_home_v1.py']
    for path in paths:
        target = destination / 'source' / path.relative_to(ROOT.parent)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    write(destination / 'source-digests.json', {p.relative_to(ROOT.parent).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    results = []
    for index in range(3):
        folder = destination / str(index + 1)
        simulator = HomeSpawnSimulator(folder / 'simulator')
        controller = observer = None
        row = {'cold_start': index + 1, 'live_model_requests': 0, 'pass': False}
        try:
            simulator.start()
            controller, observer = ArmTransport(), ArmTransport(read_only=True)
            controls = run_controls(folder / 'controls', controller, observer)
            row.update(pass_=all(r['pass'] for r in controls), controls=len(controls))
            row['pass'] = row.pop('pass_')
        except BaseException as error:
            row.update(error_type=type(error).__name__, error=str(error))
            raise
        finally:
            for item in (controller, observer):
                if item:
                    item.close()
            row['simulator_cleanup'] = simulator.close()
            results.append(row)
            write(destination / 'result.json', {'pass': len(results) == 3 and all(r['pass'] for r in results),
                'cold_starts': len(results), 'live_model_requests': 0, 'rows': deepcopy(results)})
        print('cold_start', index + 1, 'controls', row['controls'], 'pass', row['pass'], flush=True)
    verify_history()


if __name__ == '__main__':
    main()
