#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
task_root=/mnt/c/Proj/robotics/introtorobotics
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
mkdir -p "$task_root/rosa-evaluation/artifacts/reliability-v1-development"
cd "$task_root/rosa-research"
"$task_python" -B -m unittest discover -s tests -p test_reliability.py -v 2>&1 | tee "$task_root/rosa-evaluation/artifacts/reliability-v1-development/unit-tests.log"
cd "$task_root/rosa-evaluation"
"$task_python" -B -m unittest discover -s tests -p test_reliability_integration.py -v 2>&1 | tee artifacts/reliability-v1-development/integration-tests.log
"$task_python" - <<'PY'
from dotenv import dotenv_values
from urllib.request import urlopen
import json
endpoint = dotenv_values('.env')['OLLAMA_BASE_URL']
version = json.load(urlopen(endpoint + '/api/version', timeout=10))
tags = json.load(urlopen(endpoint + '/api/tags', timeout=10))
print('Ollama', version)
print('Qwen present', any(m['name'] == 'qwen3.5:9b' for m in tags['models']))
assert any(m['name'] == 'qwen3.5:9b' for m in tags['models'])
from pathlib import Path
Path('artifacts/reliability-v1-development/model-inventory.json').write_text(json.dumps({'version': version, 'tags': tags}, indent=2))
PY
