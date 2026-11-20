from pathlib import Path
from urllib.request import urlopen
import json
import platform
import subprocess
from importlib.metadata import version
from dotenv import dotenv_values

root = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation')
endpoint = dotenv_values(root/'.env')['OLLAMA_BASE_URL']
record = {'python': platform.python_version(), 'system': platform.system(),
          'kernel': platform.release(), 'packages': {}, 'ollama_loaded': None}
for name in ('langchain', 'langchain-core', 'langchain-ollama', 'pydantic', 'opentelemetry-sdk'):
    record['packages'][name] = version(name)
try:
    record['ollama_loaded'] = json.load(urlopen(endpoint + '/api/ps', timeout=10))
except Exception as error:
    record['ollama_probe_error'] = type(error).__name__
for name, argv in [('gazebo', ['gz', 'sim', '--versions']),
                   ('bridge', ['dpkg-query', '-W', 'ros-jazzy-ros-gz-bridge']),
                   ('gpu', ['/usr/lib/wsl/lib/nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.used', '--format=csv,noheader'])]:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        record[name] = {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as error:
        record[name] = {'error_type': type(error).__name__}
(root/'artifacts/reliability-v1-20261022/runtime-metadata.json').write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))
