"""Write an explicit Python test exit status without PowerShell stderr remapping."""
import json
from pathlib import Path
import unittest


def main():
    destination = Path(__file__).resolve().parents[2] / 'artifacts/stage4-policy-20261021'
    loader = unittest.defaultTestLoader
    tests = loader.loadTestsFromNames(['tests.test_jtvr_policy', 'tests.test_phase4'])
    with (destination / 'unit-validation-clean.log').open('w') as output:
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(tests)
    status = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'successful': result.wasSuccessful(), 'test_process_exitcode': 0 if result.wasSuccessful() else 1}
    (destination / 'unit-status.json').write_text(json.dumps(status, indent=2))
    print(json.dumps(status))
    raise SystemExit(status['test_process_exitcode'])


if __name__ == '__main__':
    main()
