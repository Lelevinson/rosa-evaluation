"""Run bounded offline checks, retaining each development pass/failure log."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
destination = root / 'rosa-evaluation/artifacts/macro-module-v1-20261027'
index = len(list(destination.glob('offline-*'))) + 1
folder = destination / f'offline-{index:02d}'
folder.mkdir()
rows = []
groups = [('research', root / 'rosa-research', ['test_bounded_macro.py', 'test_macro_agent.py'])]
if '--regression' in sys.argv:
    groups = [('research', root / 'rosa-research', ['test_*.py']),
        ('evaluation', root / 'rosa-evaluation', ['test_reference_report.py', 'test_macro_transfer_v1.py',
         'test_macro_focus_v2.py', 'test_prompt_contract_v1.py', 'test_output_completion.py',
         'test_output_timeout.py', 'test_workflow_live_v1.py', 'test_reliability_integration.py',
         'test_reliability_v2.py', 'test_simulator_home_v1.py', 'test_ur5e_readiness.py'])]
for name, cwd, patterns in groups:
    for pattern in patterns:
        run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
            '-p', pattern, '-v'], cwd=cwd, capture_output=True, text=True, timeout=180)
        log = folder / (name + '-' + pattern.replace('*', 'all') + '.log')
        log.write_text(run.stdout + run.stderr)
        rows.append({'suite': name + '/' + pattern, 'returncode': run.returncode, 'log': str(log)})
        print(name, pattern, 'PASS' if run.returncode == 0 else 'FAIL', flush=True)
        if run.returncode:
            print((run.stdout + run.stderr)[-7000:], flush=True)
            (folder / 'result.json').write_text(json.dumps({'pass': False, 'rows': rows}, indent=2))
            raise SystemExit(run.returncode)
(folder / 'result.json').write_text(json.dumps({'pass': True, 'live_model_requests': 0, 'rows': rows}, indent=2))
