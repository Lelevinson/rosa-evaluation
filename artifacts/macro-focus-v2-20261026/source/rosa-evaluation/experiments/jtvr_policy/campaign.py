"""Freeze, run and audit the small original-spec policy comparison.

Run prepare after validation and calibration, then run exactly once. Artifacts
are repository-owned and contain no authentication state. Never overwrite runs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil

from .audit import check
from .experiment import execute
from .fixtures import suite

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'artifacts/stage4-policy-20261021'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def sources():
    own = list((ROOT / 'experiments/jtvr_policy').glob('*.py'))
    own += [ROOT / 'tests/test_jtvr_policy.py', ROOT / 'scripts/jtvr-wsl.sh',
            ROOT / 'docs/STAGE4_POLICY_PROTOCOL_2026-10-21.md']
    own += [ROOT.parent / 'rosa-research/src/rosa/tools/ros2.py',
            ROOT.parent / 'JTVR_Final_Technical_Specification_ID(1).md']
    own += list((DEFAULT / 'ros-calibration').glob('*'))
    own += [p for p in DEFAULT.glob('unit-*') if p.is_file()]
    return sorted(p for p in own if p.is_file())


def prepare(destination):
    target = destination / 'freeze.json'
    if target.exists():
        raise RuntimeError('freeze_exists_create_a_new_explicit_protocol_if_revision_needed')
    fixtures = suite()
    hashes = {}
    for source in sources():
        relative = source.relative_to(ROOT.parent)
        hashes[str(relative)] = digest(source)
        copy = destination / 'source' / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, copy)
    json_write(destination / 'fixtures.json', fixtures)
    json_write(target, {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'platform': platform.platform(),
        'source_sha256': hashes, 'fixtures_sha256': digest(destination / 'fixtures.json'),
        'primary_episodes': 288, 'sensitivity_episodes': 576,
        'depth_ablation_episodes': 96, 'role_ablation_episodes': 192,
        'total_policy_episodes': 1152, 'model_requests': 0,
        'real_smoke_episodes': 15, 'independent_authorship_or_blinding': False,
        'annotations': 'shared user-required fields and predicates, never hidden values or faults'})
    print(json.dumps({'freeze': str(target), 'fixtures': len(fixtures), 'policy_episodes': 1152}))


def assert_frozen(destination):
    frozen = json.loads((destination / 'freeze.json').read_text())
    for relative, wanted in frozen['source_sha256'].items():
        if digest(ROOT.parent / relative) != wanted:
            raise RuntimeError('source_changed_since_freeze:' + relative)
    if digest(destination / 'fixtures.json') != frozen['fixtures_sha256']:
        raise RuntimeError('fixture_manifest_changed')
    return frozen


def run(destination):
    frozen = assert_frozen(destination)
    target = destination / 'policy-episodes.jsonl'
    if target.exists():
        raise RuntimeError('policy_run_already_exists_no_silent_overwrite')
    calibration = destination / 'ros-calibration'
    costs = json.loads((calibration / 'calibration.json').read_text())['cost_seconds']
    captures = [json.loads(line) for line in (calibration / 'captures.jsonl').read_text().splitlines()]
    fixtures = json.loads((destination / 'fixtures.json').read_text())
    outcomes, audits = [], []
    json_write(destination / 'policy-status.json', {'status': 'RUNNING', 'episodes': 0})
    for profile in ('calibrated', 'unit_cost', 'prior_type_allowed'):
        for spec in fixtures:
            for policy in ('greedy', 'batching', 'jtvr'):
                row = execute(spec, policy, costs, captures, profile=profile)
                audit = check(row, spec)
                with target.open('a') as output:
                    output.write(json.dumps(row) + '\n')
                outcomes.append(row)
                audits.append(audit)
    for spec in fixtures:
        for policy, depth, separated in (('jtvr', 1, False),
                                         ('batching', 2, True), ('jtvr', 2, True)):
            row = execute(spec, policy, costs, captures, depth=depth, role_separated=separated)
            audit = check(row, spec)
            with target.open('a') as output:
                output.write(json.dumps(row) + '\n')
            outcomes.append(row)
            audits.append(audit)
    json_write(destination / 'policy-audit.json', {'episodes': len(audits),
        'passed': sum(a['passed'] for a in audits), 'records': audits})
    correct = len(outcomes) == frozen['total_policy_episodes'] and all(a['passed'] for a in audits)
    json_write(destination / 'policy-status.json', {'status': 'COMPLETE' if correct else 'AUDIT_FAILED',
        'episodes': len(outcomes), 'audit_passed': sum(a['passed'] for a in audits),
        'verified_contract_passed': sum(r['verified_contract_pass'] for r in outcomes),
        'finished_utc': datetime.now(timezone.utc).isoformat()})
    assert_frozen(destination)
    print(json.dumps({'episodes': len(outcomes), 'audit_passed': sum(a['passed'] for a in audits),
                      'contract_passed': sum(r['verified_contract_pass'] for r in outcomes)}))
    if not correct:
        raise RuntimeError('audit_failed_preserve_attempt_and_inspect')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'run', 'verify'))
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.output)
    elif args.action == 'run':
        run(args.output)
    else:
        assert_frozen(args.output)
        print('Frozen sources and fixture manifest match.')


if __name__ == '__main__':
    main()
