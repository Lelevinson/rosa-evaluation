"""Full-arm simulator lifecycle and frozen transfer cases, after mock completion."""
from copy import deepcopy
import json
import os
from pathlib import Path
import signal
import subprocess
from rosa_reliability.ros_arm import ArmTransport, HOME_POSE, JOINTS


def arm_cases():
    first, second = deepcopy(HOME_POSE), deepcopy(HOME_POSE)
    first.update(shoulder_pan_joint=.18, wrist_3_joint=.16)
    second.update(shoulder_pan_joint=-.16, elbow_joint=1.70, wrist_3_joint=-.18)
    return [dict(id=name, targets={'/ur5e': deepcopy(target)}, fault=fault,
            expected_status=expected, achievable=achievable) for name,target,fault,expected,achievable in (
        ('ur5e_coordinated_move', first, None, 'SUCCESS', True),
        ('ur5e_suppressed_command', second, 'drop', 'FAILURE', False),
        ('ur5e_partial_trajectory', first, 'partial', 'FAILURE', False),
        ('ur5e_missing_sensor', second, 'missing', 'UNKNOWN', False))]


def gazebo_jobs():
    return [dict(phase='gazebo', arm=arm, spec=spec) for i,spec in enumerate(arm_cases())
            for arm in (('A','D') if i % 2 == 0 else ('D','A'))]


class ArmSimulator:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.child = self.log = None
    def start(self):
        os.environ['GZ_PARTITION'] = 'rosa-ur5e-v2-' + str(os.getpid())
        self.log = (self.folder / 'launch.log').open('w')
        self.child = subprocess.Popen(['ros2','launch','ur_simulation_gz','ur_sim_control.launch.py',
            'ur_type:=ur5e','launch_rviz:=false','gazebo_gui:=false',
            'initial_joint_controller:=joint_trajectory_controller'],
            stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        # JointState publication can precede trajectory-controller activation.
        # This is an outside-trial startup prerequisite, never a free agent read.
        import time
        from controller_manager_msgs.srv import ListControllers
        probe=ArmTransport(read_only=True)
        queries=[]
        try:
            client=probe.node.create_client(ListControllers,'/controller_manager/list_controllers')
            deadline=time.monotonic()+120
            while time.monotonic()<deadline:
                if not client.wait_for_service(timeout_sec=2):
                    continue
                future=client.call_async(ListControllers.Request())
                while not future.done() and time.monotonic()<deadline:
                    probe.executor.spin_once(timeout_sec=.05)
                if future.done() and future.result():
                    states={c.name:c.state for c in future.result().controller}
                    queries.append({'at':time.monotonic(),'states':states})
                    if states.get('joint_state_broadcaster')=='active' and states.get('joint_trajectory_controller')=='active':
                        observed=probe.read('/ur5e',list(JOINTS))
                        (self.folder/'readiness.json').write_text(json.dumps({'pass':True,'outside_trial':True,
                            'queries':queries,'observed_values':observed,'sensor_record':probe.records[-1]},indent=2))
                        return
            raise RuntimeError('active_controllers_not_ready_within_120_seconds')
        finally:
            probe.close()
    def close(self):
        if self.child and self.child.poll() is None:
            os.killpg(self.child.pid, signal.SIGINT)
            try:
                self.child.wait(20)
            except subprocess.TimeoutExpired:
                os.killpg(self.child.pid, signal.SIGKILL)
                self.child.wait(5)
        if self.log:
            self.log.close()
        return {'pid': self.child.pid if self.child else None,
                'returncode': self.child.returncode if self.child else None}


def reset(controller, observer):
    controller.suppress_commands = controller.partial_commands = controller.missing_observations = False
    controller.read('/ur5e', list(JOINTS))
    controller.write('/ur5e', HOME_POSE)
    actual = observer.read('/ur5e', list(JOINTS))
    if any(abs(actual[n]-HOME_POSE[n]) > .025 for n in JOINTS):
        raise RuntimeError('independent_home_reset_failed')
    return {'values': actual, 'sensor_record': deepcopy(observer.records[-1])}


def configure_fault(controller, spec):
    controller.suppress_commands = spec['fault'] == 'drop'
    controller.partial_commands = spec['fault'] == 'partial'
    controller.missing_observations = spec['fault'] == 'missing'


def deterministic(folder):
    from .runner import write
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    simulator = ArmSimulator(folder / 'simulator')
    controller = observer = None
    rows = []
    try:
        simulator.start()
        controller, observer = ArmTransport(), ArmTransport(read_only=True)
        # Model startup is bounded by launch/controller readiness, not ROS discovery assumptions.
        import time
        deadline = time.monotonic() + 120
        while True:
            try:
                controller.read('/ur5e', list(JOINTS))
                break
            except TimeoutError:
                if time.monotonic() > deadline:
                    raise
        for spec in arm_cases():
            origin = reset(controller, observer)
            configure_fault(controller, spec)
            offset = len(controller.records)
            started = time.monotonic()
            observed = None
            try:
                observed = controller.read('/ur5e', list(JOINTS))
                controller.write('/ur5e', spec['targets']['/ur5e'])
                observed = controller.read('/ur5e', list(JOINTS))
                outcome = 'SUCCESS' if all(abs(observed[n]-spec['targets']['/ur5e'][n]) <= .025 for n in JOINTS) else 'FAILURE'
            except TimeoutError:
                outcome = 'UNKNOWN'
            actual = observer.read('/ur5e', list(JOINTS))
            rows.append({'case': spec['id'], 'outcome': outcome, 'expected': spec['expected_status'],
                'pass': outcome == spec['expected_status'], 'reset': origin, 'model_calls': 0,
                'wall_seconds': time.monotonic()-started, 'reported_values': observed,
                'independent_observation': actual, 'observer_record': deepcopy(observer.records[-1]),
                'records': deepcopy(controller.records[offset:])})
            write(folder / 'result.json', {'status': 'RUNNING', 'rows': rows})
    finally:
        for item in (controller, observer):
            if item:
                item.close()
        result = {'status': 'COMPLETE' if len(rows)==4 and all(r['pass'] for r in rows) else 'FAILED',
                  'rows': rows, 'simulator_cleanup': simulator.close()}
        write(folder / 'result.json', result)
    if result['status'] != 'COMPLETE':
        raise RuntimeError('full_arm_deterministic_controls_failed')
    return result
