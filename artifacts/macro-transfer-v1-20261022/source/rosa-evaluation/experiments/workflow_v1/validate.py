"""Persist focused offline checks and relevant unchanged-behavior regressions."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    evaluation = Path(__file__).resolve().parents[2]
    research = evaluation.parent / 'rosa-research'
    suites = [(evaluation, 'test_workflow_v1.py'), (evaluation, 'test_output_completion.py'),
              (evaluation, 'test_output_timeout.py'), (research, 'test_reliability.py'),
              (research, 'test_evidence.py')]
    results = []
    for root, pattern in suites:
        command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v']
        run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
        log = run.stdout + run.stderr
        (args.output / (pattern + '.log')).write_text(log)
        results.append({'suite': pattern, 'cwd': str(root), 'command': command,
                        'exit_code': run.returncode, 'pass': run.returncode == 0})
    result = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'all_pass': all(r['pass'] for r in results), 'suites': results}
    (args.output / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if not result['all_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
