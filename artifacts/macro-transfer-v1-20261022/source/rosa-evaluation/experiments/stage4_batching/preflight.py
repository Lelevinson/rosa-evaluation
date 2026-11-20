"""Infrastructure and actual-tool validation before the live experiment freeze."""
import argparse
import json
from pathlib import Path
import shutil
import unittest

from ..config import ROOT
from .environment import RealEnvironment
from .gateway import Gateway
from .tasks import tasks
from .runner import CAMPAIGN


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='preflight')
    parser.add_argument('--reuse-passed-tests', help='Reuse the already passed test record; run fresh actual ROS acceptance')
    args = parser.parse_args()
    if '/' in args.name or '\\' in args.name or args.name in ('.', '..'):
        raise ValueError('expected_single_output_identifier')
    destination = CAMPAIGN / args.name
    destination.mkdir(parents=True, exist_ok=False)
    if args.reuse_passed_tests:
        if '/' in args.reuse_passed_tests or '\\' in args.reuse_passed_tests or args.reuse_passed_tests in ('.', '..'):
            raise ValueError('invalid_test_record_directory')
        source = CAMPAIGN / args.reuse_passed_tests
        test_summary = json.loads((source / 'tests.json').read_text())
        test_summary['reused_from'] = args.reuse_passed_tests
        shutil.copy2(source / 'tests.txt', destination / 'tests.txt')
    else:
        with (destination / 'tests.txt').open('w') as stream:
            tests = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
        test_summary = {'count': result.testsRun, 'errors': len(result.errors),
                        'failures': len(result.failures), 'passed': result.wasSuccessful()}
    (destination / 'tests.json').write_text(json.dumps(test_summary, indent=2))
    if not test_summary['passed']:
        raise RuntimeError('unit_validation_failed')
    costs = json.loads((ROOT / 'artifacts/stage4-policy-20261021/ros-calibration/calibration.json').read_text())['cost_seconds']
    environment = RealEnvironment(destination / 'ros', 176)
    rows = []
    try:
        environment.start()
        for spec in tasks():
            for policy in ('model_selected', 'amortized_batching'):
                environment.reset(spec)
                gateway = Gateway(spec, policy, environment.invoke, costs)
                for node, group in spec['groups'].items():
                    for name, value in group['expected_values'].items():
                        gateway.call('ros2_param_set', node_name=node, param_name=name, param_value=str(value))
                    strategy = 'node_bulk' if node + ':node_summary' in spec['extras'] else 'direct' if len(group['names']) == 1 else 'bulk'
                    gateway.call('read_parameter_evidence', node_name=node, **group, strategy=strategy)
                for extra in spec['extras']:
                    if extra.endswith(':topic_details'):
                        gateway.call('ros2_topic_info', topics=[extra.rsplit(':', 1)[0]])
                values = {node: {name: gateway.ledger.valid(__import__('experiments.jtvr_policy.core', fromlist=['Key']).Key(node, 'param:' + name)).value
                                for name in group['report_names']} for node, group in spec['groups'].items()}
                gateway.call('submit_parameter_report', outcome='success', observed_values=values,
                             acknowledged_details=spec['extras'])
                evidence = gateway.score(environment.oracle(spec), [])
                rows.append({'fixture_id': spec['id'], 'policy': policy, 'evidence': evidence})
                with (destination / 'real-scripted.jsonl').open('a') as output:
                    output.write(json.dumps(rows[-1]) + '\n')
                if not evidence['strict_contract_pass']:
                    raise RuntimeError('real_scripted_contract_failed:' + spec['id'])
    finally:
        environment.close()
    (destination / 'status.json').write_text(json.dumps({'status': 'COMPLETE',
        'tests': test_summary['count'], 'real_scripted_episodes': len(rows),
        'all_contract_passed': all(r['evidence']['strict_contract_pass'] for r in rows)}, indent=2))
    print(f"Preflight complete: {test_summary['count']} tests, {len(rows)} actual-ROS scripted cases.")


if __name__ == '__main__':
    main()
