"""A0 Gazebo smoke check, zero model: launch the M4 UR5e world headless via the unchanged
rosa_reliability.gazebo_demo.GazeboDemo, confirm controllers active and the documented home pose,
then shut down cleanly. Usage: gazebo_smoke.py <new output folder>"""
import json, os, sys, time, subprocess
os.environ.update(ROS_DOMAIN_ID='231', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
sys.path.insert(0, '/mnt/c/Proj/robotics/introtorobotics/rosa-research/src')
from rosa_reliability.gazebo_demo import GazeboDemo
out = sys.argv[1]
started = time.monotonic(); result = {'ros_domain_id': 231, 'model_requests': 0}
demo = GazeboDemo(out)
try:
    demo.start()
    result['ready_seconds'] = round(time.monotonic() - started, 1)
    result['readiness'] = json.load(open(os.path.join(out, 'readiness.json')))['pass']
finally:
    result['close'] = demo.close()
    time.sleep(3)
    left = subprocess.run(['pgrep', '-af', 'gz sim|ruby.*gz|ros2_control_node|robot_state_publisher'],
                          capture_output=True, text=True).stdout.strip()
    result['leftover_processes'] = left.splitlines() if left else []
    result['total_seconds'] = round(time.monotonic() - started, 1)
    open(os.path.join(os.path.dirname(out.rstrip('/')), 'GAZEBO_SMOKE_RESULT.json'), 'w').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
