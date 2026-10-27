"""Isolated Gazebo camera recording and bounded delivery demos, never M4 trials."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027'
REQUEST = 'Move the arm to the registered ur5e.offset pose and report the verified outcome.'


class Camera:
    def __init__(self, folder):
        import rclpy
        from rclpy.node import Node
        from rclpy.executors import SingleThreadedExecutor
        from rclpy.qos import qos_profile_sensor_data
        from sensor_msgs.msg import Image
        self.folder = folder
        self.folder.mkdir()
        self.frames = []
        self.started = time.monotonic()
        self.context = rclpy.Context()
        rclpy.init(context=self.context)
        self.node = Node('rosa_m5_recording_camera', context=self.context)
        self.subscription = self.node.create_subscription(Image, '/m5/camera', self.image, qos_profile_sensor_data)
        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)
        self.finished = threading.Event()
        self.thread = threading.Thread(target=self.spin, daemon=True)
        self.thread.start()

    def image(self, message):
        from PIL import Image
        if message.encoding not in ('rgb8', 'bgr8', 'rgba8', 'bgra8'):
            return
        mode = 'RGBA' if 'a' in message.encoding else 'RGB'
        raw = message.encoding.upper().replace('8', '')
        frame = Image.frombytes(mode, (message.width, message.height), bytes(message.data), 'raw', raw, message.step)
        name = f'{len(self.frames):05d}.png'
        frame.convert('RGB').save(self.folder / name)
        self.frames.append({'file': name, 'seconds': time.monotonic() - self.started,
                            'sim_stamp': [message.header.stamp.sec, message.header.stamp.nanosec]})

    def spin(self):
        while not self.finished.is_set():
            self.executor.spin_once(timeout_sec=.1)

    def wait(self, seconds):
        until = time.monotonic() + seconds
        while time.monotonic() < until:
            time.sleep(.1)

    def close(self):
        self.finished.set()
        self.thread.join(5)
        self.executor.shutdown()
        self.node.destroy_node()
        self.context.shutdown()
        (self.folder.parent / 'frames.json').write_text(json.dumps(self.frames, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=('preflight', 'ollama', 'siwc'), required=True)
    parser.add_argument('--endpoint')
    args = parser.parse_args()
    folder = OUT / ('demo-' + args.backend)
    folder.mkdir(parents=True, exist_ok=False)
    # Visual-only isolated world. Existing robot description/controller/guards are unchanged.
    resource = str(Path(__file__).parent / 'media_world')
    os.environ['GZ_SIM_RESOURCE_PATH'] = resource + os.pathsep + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    os.environ.update(ROS_DOMAIN_ID='219', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',
                      GZ_PARTITION='rosa-macro-module-v1-' + str(os.getpid()))
    from rosa_reliability.gazebo_demo import GazeboDemo
    from rosa_reliability.ros_arm import ArmTransport, JOINTS
    from rosa_reliability.ros_readiness import ArmReadinessTransport
    from rosa_reliability.capability_demo import registry
    from rosa_reliability.macro_agent import MacroROSA
    simulator = GazeboDemo(folder / 'simulator')
    camera = bridge = movement = inspection = observer = model = None
    result = {'backend': args.backend, 'kind': 'Delivery demonstration, not a new research trial',
        'request': REQUEST, 'live_model_requests': 0, 'pass': False,
        'visual_world_change': 'isolated static camera/rendering world only; original runtime source unchanged',
        'limits': {'calls': 8, 'observed_output_tokens': 2048, 'local_output_per_call': 1024,
                   'native_operations': 10, 'tool_attempts': 16, 'corrections': 3,
                   'invocation_seconds': 180, 'external_seconds': 300, 'writes': 1}}
    def expired(signum, frame):
        raise TimeoutError('m5_demo_external_deadline')
    old_alarm = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, 300 if args.backend != 'preflight' else 170)
    try:
        simulator.start()
        camera = Camera(folder / 'frames')
        bridge_log = (folder / 'camera-bridge.log').open('w')
        bridge = subprocess.Popen(['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
            '/m5/camera@sensor_msgs/msg/Image[gz.msgs.Image'], stdout=bridge_log, stderr=subprocess.STDOUT,
            start_new_session=True)
        camera.wait(12)
        if len(camera.frames) < 2:
            raise RuntimeError('gazebo_camera_frames_unavailable')
        if args.backend == 'preflight':
            result.update(pass_=True, camera_frames=len(camera.frames))
            result['pass'] = result.pop('pass_')
            return
        movement, inspection, observer = ArmTransport(), ArmReadinessTransport(), ArmTransport(read_only=True)
        invocation = registry().open({'state': movement, 'inspection': inspection})
        result['model_started_seconds'] = time.monotonic() - camera.started
        if args.backend == 'ollama':
            from rosa_backends.chat_ollama import ConfiguredChatOllama
            model = ConfiguredChatOllama(model='qwen3.5:9b', base_url=args.endpoint, num_ctx=8192,
                num_predict=1024, temperature=0, seed=42, use_mmap=True, reasoning=False,
                streaming=False, cache=False, client_kwargs={'timeout': 180})
            agent = MacroROSA(model, invocation, backend='ollama')
            answer = agent.invoke(REQUEST)
        else:
            from rosa_auth.remembered import remembered_session
            from rosa_auth.protected_store import WindowsCredentialStore
            from rosa_auth.responses import SiwcBackend
            from rosa_backends.chat_siwc import ChatSiwc
            status = {}
            with WindowsCredentialStore('research') as store:
                if store.load() is None:
                    raise RuntimeError('manual_consent_required_demo_not_started')
                with remembered_session(store=store, request_budget=8, status=status) as auth:
                    transport = SiwcBackend(request_budget=8, token_provider=auth.access_token)
                    model = ChatSiwc(model='gpt-6.1-sol', backend=transport)
                    agent = MacroROSA(model, invocation, backend='siwc')
                    try:
                        answer = agent.invoke(REQUEST)
                        transport.raise_if_unavailable()
                    finally:
                        model.close()
            result['authorization'] = status
        result['model_finished_seconds'] = time.monotonic() - camera.started
        snapshot = invocation.snapshot()
        actual = observer.read('/ur5e', list(JOINTS))
        target = registry().catalogue()['ur5e.offset']['targets']['/ur5e']
        goal = all(abs(actual[j] - target[j]) <= .025 for j in JOINTS)
        accepted = bool(invocation.session.reports and invocation.session.reports[-1].get('accepted')
                        and invocation.session.reports[-1]['status'] == 'SUCCESS')
        result.update(answer=answer, snapshot=snapshot, inference=agent.inference_budget.snapshot(),
                      live_model_requests=agent.inference_budget.calls, independent_final_joints=actual,
                      independent_goal_reached=goal, accepted_report=accepted,
                      pass_=bool(goal and accepted and snapshot['selected_skill'] == 'ur5e.offset'))
        result['pass'] = result.pop('pass_')
        camera.wait(5)
    except BaseException as error:
        result.update(error_type=type(error).__name__, error=str(error)
                      if isinstance(error, (RuntimeError, TimeoutError)) else type(error).__name__)
        if 'agent' in locals():
            result.update(inference=agent.inference_budget.snapshot(), live_model_requests=agent.inference_budget.calls,
                          snapshot=invocation.snapshot())
        raise
    finally:
        if camera:
            camera.close()
            result['camera_frames'] = len(camera.frames)
        if bridge:
            if bridge.poll() is None:
                os.killpg(bridge.pid, signal.SIGINT)
                try: bridge.wait(10)
                except subprocess.TimeoutExpired:
                    os.killpg(bridge.pid, signal.SIGKILL)
                    bridge.wait(5)
            bridge_log.close()
        for item in (movement, inspection, observer):
            if item: item.close()
        result['simulator_cleanup'] = simulator.close()
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_alarm)
        (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: result.get(k) for k in ('backend', 'pass', 'camera_frames', 'live_model_requests', 'error_type', 'simulator_cleanup')}))


if __name__ == '__main__':
    main()
