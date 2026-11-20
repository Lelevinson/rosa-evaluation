"""Read-only final checks, inventory and regression summary for M1 reporting."""
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
destination = root / 'rosa-evaluation/artifacts/macro-module-v1-20261027'
checks = []
for pattern in ('test_bounded_macro.py', 'test_macro_agent.py', 'test_macro_gazebo.py', 'test_remembered_auth.py'):
    run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v'],
        cwd=root / 'rosa-research', capture_output=True, text=True, timeout=90)
    log = destination / ('final-' + pattern + '.log')
    if log.exists(): raise RuntimeError('refuse_to_overwrite_final_log')
    log.write_text(run.stdout + run.stderr)
    count = re.search(r'Ran (\d+) tests?', run.stderr)
    checks.append({'suite': pattern, 'pass': run.returncode == 0, 'methods': int(count[1]) if count else None})
    print(pattern, 'PASS' if run.returncode == 0 else 'FAIL', flush=True)
    if run.returncode: raise RuntimeError('final_offline_check_failed:' + pattern)
packages = subprocess.check_output(['ros2', 'pkg', 'list'], text=True).splitlines()
description = Path('/opt/ros/jazzy/share/ur_simulation_gz/urdf/ur_gz.urdf.xacro').read_text()
readiness = json.loads((destination / 'gazebo-01/demo/simulator/readiness.json').read_text())
inventory = {'active_controllers_observed': readiness['queries'][-1]['states'],
    'installed_related_packages': [p for p in packages if any(s in p for s in
        ('gripper', 'robotiq', 'camera', 'moveit', 'ur_description', 'ur_simulation', 'joint_trajectory'))],
    'top_level_model_mentions_gripper': 'gripper' in description.lower(),
    'interpretation': 'Installed controller software alone does not demonstrate a configured gripper/sensor. '
                      'Only the six-joint arm interface was exercised. A read-only joint-state inspection skill '
                      'is the smallest currently grounded M2 candidate; it is not another actuator or grasping skill.'}
(destination / 'simulator-inventory.json').write_text(json.dumps(inventory, indent=2))
summaries = []
for folder in sorted(destination.glob('offline-*')):
    result = json.loads((folder / 'result.json').read_text())
    methods = 0
    for log in folder.glob('*.log'):
        match = re.search(r'Ran (\d+) tests?', log.read_text())
        if match: methods += int(match[1])
    summaries.append({'attempt': folder.name, 'pass': result['pass'], 'methods_executed': methods})
storage = subprocess.run([sys.executable, '-B', '-m', 'rosa_auth.remembered', 'storage-self-test'],
                         capture_output=True, text=True, timeout=60)
(destination / 'protected-storage-self-test.log').write_text(storage.stdout + storage.stderr)
if storage.returncode: raise RuntimeError('protected_storage_self_test_failed')
(destination / 'final-checks.json').write_text(json.dumps({'pass': True, 'live_model_requests': 0,
    'focused_suites': checks, 'retained_offline_attempts': summaries,
    'protected_storage': json.loads(storage.stdout)}, indent=2))
print(json.dumps({'pass': True, 'checks': checks, 'prior_offline_attempts': summaries, 'inventory': inventory}, indent=2))
