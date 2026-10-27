import json
from pathlib import Path
import subprocess
import sys

root = Path('/mnt/c/Proj/robotics/introtorobotics')
destination = root / 'reports/m4-development'
destination.mkdir(exist_ok=True)
attempt = len(list(destination.glob('tests-*.json'))) + 1
results = []
for repo, arguments, name in [
    ('rosa-evaluation', ['discover', '-s', 'tests', '-p', 'test_macro_m4.py', '-v'], 'm4'),
    ('rosa-research', ['discover', '-s', 'tests', '-v'], 'research'),
]:
    run = subprocess.run([sys.executable, '-B', '-m', 'unittest', *arguments], cwd=root / repo,
        capture_output=True, text=True, timeout=120)
    path = destination / f'tests-{attempt}-{name}.log'
    path.write_text(run.stdout + run.stderr)
    results.append({'repository': repo, 'returncode': run.returncode, 'log': path.name})
(destination / f'tests-{attempt}.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results))
raise SystemExit(int(any(result['returncode'] for result in results)))
