"""Durable post-processing so evidence/report completion survives agent interruptions."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import time
from urllib.request import Request, urlopen
from dotenv import dotenv_values

workspace = Path('/mnt/c/Proj/robotics/introtorobotics')
evaluation = workspace / 'rosa-evaluation'
campaign = evaluation / 'artifacts/reliability-v1-20261022'
python = '/home/martin/.local/share/rosa-envs/research/bin/python'
deadline = time.monotonic() + 7 * 3600
while time.monotonic() < deadline and not (campaign / 'pipeline-completion.json').exists():
    time.sleep(10)
if not (campaign / 'pipeline-completion.json').exists():
    raise RuntimeError('pipeline_completion_timeout')
completion = json.loads((campaign / 'pipeline-completion.json').read_text())
try:
    endpoint = dotenv_values(evaluation / '.env')['OLLAMA_BASE_URL']
    request = Request(endpoint + '/api/generate', data=json.dumps({'model': 'qwen3.5:9b', 'keep_alive': 0}).encode(),
                      headers={'Content-Type': 'application/json'})
    response = json.load(urlopen(request, timeout=30))
    (campaign / 'local-model-cleanup.json').write_text(json.dumps({'model': response.get('model'),
        'done': response.get('done'), 'done_reason': response.get('done_reason')}, indent=2))
except Exception as error:
    (campaign / 'local-model-cleanup.json').write_text(json.dumps({'error_type': type(error).__name__}))
reference = subprocess.run(['bash', str(workspace / 'reports/reliability_reference.sh')], cwd=evaluation)
review = subprocess.run([python, '-B', '-m', 'experiments.reliability_v1.review'], cwd=evaluation)
(campaign / 'monitor.stop').touch()
for _ in range(30):
    if (campaign / 'power-release.json').exists():
        break
    time.sleep(1)
package = None
if reference.returncode == 0 and review.returncode == 0 and all(completion[k] == 0 for k in completion):
    package = subprocess.run([python, '-B', '-m', 'experiments.reliability_v1.package'], cwd=evaluation).returncode
receipt = {'finished_utc': datetime.now(timezone.utc).isoformat(), 'pipeline': completion,
           'reference_and_demo_exit': reference.returncode, 'review_exit': review.returncode, 'package_exit': package}
(workspace / 'reports/RELIABILITY_V1_POSTPROCESS_RECEIPT.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt), flush=True)
