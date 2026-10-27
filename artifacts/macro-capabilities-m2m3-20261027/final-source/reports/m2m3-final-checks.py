import json
import os
from pathlib import Path
import subprocess
import sys

root = Path('/mnt/c/Proj/robotics/introtorobotics')
folder = root / 'rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027'
environment = dict(os.environ, ROSA_TEST_WINDOWS_STORAGE='1')
results = []
for repository, arguments, filename in [
    ('rosa-research', ['discover', '-s', 'tests', '-v'], 'research-final-tests.log'),
    ('rosa-evaluation', ['discover', '-s', 'tests', '-p', 'test_m2_m3_bounds.py', '-v'], 'evaluation-final-tests.log'),
]:
    command = [sys.executable, '-B', '-m', 'unittest', *arguments]
    run = subprocess.run(command, cwd=root / repository, env=environment, capture_output=True, text=True, timeout=120)
    (folder / filename).write_text(run.stdout + run.stderr)
    results.append({'repository': repository, 'returncode': run.returncode, 'log': filename})
(folder / 'final-test-status.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results))
raise SystemExit(int(any(r['returncode'] for r in results)))
