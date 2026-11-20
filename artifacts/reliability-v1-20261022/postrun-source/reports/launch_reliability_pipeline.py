"""Detach the explicitly authorized bounded batch; logs contain no tokens."""
from pathlib import Path
import json
import subprocess

root = Path('/mnt/c/Proj/robotics/introtorobotics')
destination = root / 'rosa-evaluation/artifacts/reliability-v1-20261022'
with (destination / 'pipeline.log').open('x') as log:
    child = subprocess.Popen(['bash', str(root / 'reports/reliability_pipeline.sh')],
                             stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             start_new_session=True)
(destination / 'supervisor.json').write_text(json.dumps({'pid': child.pid, 'launch_script': 'reports/reliability_pipeline.sh'}))
print('Detached bounded validation supervisor PID', child.pid)
