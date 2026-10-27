"""Read the existing WSL runtime and system-package versions without installing."""
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
packages = ('jpl-rosa', 'langchain', 'langchain-core', 'langchain-ollama', 'ollama',
            'pydantic', 'PyJWT', 'openinference-instrumentation-langchain', 'opentelemetry-sdk')
versions = {name: importlib.metadata.version(name) for name in packages}
system = {}
for name in ('ros-jazzy-ur-simulation-gz', 'ros-jazzy-ur-description', 'ros-jazzy-ur-controllers',
             'ros-jazzy-gz-ros2-control', 'ros-jazzy-ros-gz-bridge', 'ros-jazzy-controller-manager',
             'ros-jazzy-joint-trajectory-controller'):
    run = subprocess.run(['dpkg-query', '-W', '-f=${Version}', name], capture_output=True, text=True, timeout=10)
    system[name] = run.stdout.strip() if run.returncode == 0 else 'NOT_INSTALLED_UNDER_THIS_NAME'
uv = shutil.which('uv') or str(Path.home() / '.local/bin/uv')
gz = subprocess.run(['gz', 'sim', '--versions'], capture_output=True, text=True, timeout=10)
result = {'python': sys.version, 'platform': platform.platform(), 'ros_distro': os.environ.get('ROS_DISTRO'),
          'python_packages': versions, 'selected_system_packages': system,
          'uv_version': subprocess.check_output([uv, '--version'], text=True).strip(),
          'gazebo_versions_output': gz.stdout.strip(), 'gazebo_versions_exit_code': gz.returncode,
          'live_model_requests': 0, 'system_changes': False}
(root / 'artifacts/macro-m5-20261027/runtime-environment.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
