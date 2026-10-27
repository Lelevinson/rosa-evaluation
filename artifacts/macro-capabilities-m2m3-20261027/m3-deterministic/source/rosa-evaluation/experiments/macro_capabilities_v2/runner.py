"""M2 independent capability engineering gate; no model/consent is used."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from rosa_reliability.capability_demo import registry, deterministic_report
from rosa_reliability.gazebo_demo import GazeboDemo, require_home
from rosa_reliability.ros_arm import ArmTransport, HOME_POSE, JOINTS
from rosa_reliability.ros_readiness import ArmReadinessTransport
from .observability import Meter, audit, trace_check

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'artifacts/macro-capabilities-m2m3-20261027'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def verify_history():
    count = 0
    for campaign, filename, key in [('macro-focus-v2-20261026', 'freeze.json', 'files'),
                                  ('macro-module-v1-20261027', 'source-manifest.json', 'source_files')]:
        folder = ROOT / 'artifacts' / campaign
        manifest = json.loads((folder / filename).read_text())
        for name, expected in manifest[key].items():
            if hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('historical_source_changed:' + name)
            if hashlib.sha256((folder / 'source' / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('historical_snapshot_changed:' + name)
            count += 1
    archive = ROOT / 'artifacts/ROSA_MACRO_MODULE_V1_M1_ENGINEERING_2026-10-27.zip'
    expected = archive.with_suffix('.sha256').read_text().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected: raise RuntimeError('m1_archive_changed')
    return {'pass': True, 'source_assertions': count, 'm1_archive_sha256': expected}


def persisted(folder):
    run = subprocess.run(['/home/martin/.local/share/rosa-envs/phoenix/bin/python', '-B', '-m',
        'experiments.macro_capabilities_v2.persisted', '--folder', str(folder)], cwd=ROOT,
        capture_output=True, text=True, timeout=60)
    (folder / 'phoenix-audit.log').write_text(run.stdout + run.stderr)
    if run.returncode: raise RuntimeError('persisted_phoenix_audit_failed')
    return json.loads((folder / 'phoenix-audit.json').read_text())


def switch_trajectory(inspection, active):
    """Outside-task simulated fault setup, never a public skill/tool."""
    from controller_manager_msgs.srv import SwitchController
    observer = inspection.observer
    client = observer.node.create_client(SwitchController, '/controller_manager/switch_controller')
    if not client.wait_for_service(timeout_sec=2): raise TimeoutError('switch_controller_setup_unavailable')
    request = SwitchController.Request()
    request.activate_controllers = ['joint_trajectory_controller'] if active else []
    request.deactivate_controllers = [] if active else ['joint_trajectory_controller']
    request.strictness = SwitchController.Request.STRICT
    request.activate_asap = True
    request.timeout.sec = 5
    future = client.call_async(request)
    deadline = time.monotonic() + 8
    try:
        while not future.done() and time.monotonic() < deadline:
            observer.executor.spin_once(timeout_sec=0.05)
        if not future.done() or future.result() is None or not future.result().ok:
            raise RuntimeError('simulated_controller_switch_failed')
        return {'outside_task': True, 'activate_trajectory_controller': active, 'response_ok': True}
    finally:
        observer.node.destroy_client(client)


class MissingSource:
    def __init__(self, inner, source): self.inner, self.source, self.injected_calls = inner, source, 0
    def read_group(self, source, names):
        if source == self.source:
            self.injected_calls += 1
            raise TimeoutError('engineering_injected_source_unavailable')
        return self.inner.read_group(source, names)


def run_m2(folder):
    simulator = GazeboDemo(folder / 'simulator')
    movement = inspection = oracle = readiness_oracle = None
    inactive = False
    rows, setup = [], []
    result = {'pass': False, 'live_model_requests': 0, 'stage': 'M2', 'rows': rows, 'outside_task_setup': setup}
    meter = Meter()
    try:
        simulator.start()
        movement, inspection = ArmTransport(), ArmReadinessTransport()
        oracle, readiness_oracle = ArmTransport(read_only=True), ArmReadinessTransport()
        result['inspection_has_no_publisher'] = inspection.observer.publisher is None
        cases = [
            ('move_offset', 'ur5e.offset', None, 'SUCCESS', 1),
            ('already_offset', 'ur5e.offset', None, 'SUCCESS', 0),
            ('ineffective_home', 'ur5e.home', 'ineffective', 'FAILURE', 1),
            ('missing_movement_prerequisite', 'ur5e.home', 'missing', 'UNKNOWN', 0),
            ('return_home', 'ur5e.home', None, 'SUCCESS', 1),
            ('partial_offset', 'ur5e.offset', 'partial', 'FAILURE', 1),
            ('inspect_ready', 'ur5e.inspect_readiness', None, 'SUCCESS', 0),
            ('inspect_actual_inactive_controller', 'ur5e.inspect_readiness', 'inactive', 'FAILURE', 0),
            ('inspect_missing_controllers', 'ur5e.inspect_readiness', 'controllers', 'UNKNOWN', 0),
            ('inspect_missing_joint_sample', 'ur5e.inspect_readiness', 'joint_state', 'UNKNOWN', 0),
        ]
        for name, selected, fault, expected, writes in cases:
            movement.suppress_commands = fault == 'ineffective'
            movement.partial_commands = fault == 'partial'
            movement.missing_observations = fault == 'missing'
            if fault == 'inactive':
                setup.append(switch_trajectory(inspection, False))
                inactive = True
            reader = MissingSource(inspection, fault) if fault in ('controllers', 'joint_state') else inspection
            offset = len(movement.records)
            trial = folder / name
            trial.mkdir()
            with trace_check(trial / 'trace.json', {'stage': 'M2', 'case': name,
                'decision_actor': 'deterministic_reference', 'live_model_requests': 0}) as tracer:
                invocation = registry().open({'state': movement, 'inspection': reader}, tracer=tracer)
                config = {'callbacks': [meter]}
                bundle = invocation.execute(selected, config=config)
                evidence = invocation.session.observations[-1]
                values, targets = evidence['observed_values'], invocation.session.targets
                status = 'UNKNOWN' if any(v is None for g in values.values() for v in g.values()) else (
                    'SUCCESS' if all(abs(values[n][k] - v) <= invocation.limits.tolerance
                        for n, group in targets.items() for k, v in group.items()) else 'FAILURE')
                rejected_write = None
                if selected == 'ur5e.inspect_readiness' and fault is None:
                    rejected_write = next(t for t in invocation.tools if t.name == 'write_state').invoke(
                        {'node_name': '/ur5e', 'values': HOME_POSE}, config=config)
                report = invocation.submit_report(status, evidence['observation_id'], config=config)
                snapshot = invocation.snapshot()
            # Each trace has its own callback lists for exact local auditing.
            actual = oracle.read('/ur5e', list(JOINTS))
            if selected == 'ur5e.inspect_readiness':
                independent = {**readiness_oracle.read_group('controllers',
                    ['trajectory_controller_active', 'joint_state_broadcaster_active']),
                    **readiness_oracle.read_group('joint_state', ['joint_sample_fresh'])}
                agreement = (status == 'UNKNOWN' if fault in ('controllers', 'joint_state') else
                             status == ('SUCCESS' if all(independent.values()) else 'FAILURE'))
                if rejected_write is not None:
                    agreement = agreement and 'read_only_skill_forbids_write' in rejected_write
            else:
                target = invocation.session.targets['/ur5e']
                reached = all(abs(actual[k] - v) <= invocation.limits.tolerance for k, v in target.items())
                independent = {'goal_reached': reached}
                agreement = status == 'UNKNOWN' if fault == 'missing' else reached == (status == 'SUCCESS')
            records = deepcopy(movement.records[offset:])
            count = sum(r['kind'] == 'trajectory_request' for r in records)
            local = audit(snapshot, trial / 'trace.json', meter)
            row = {'case': name, 'pass': report['report_accepted'] and status == expected and agreement
                and count == writes and local['pass'], 'selected_skill': selected, 'expected_status': expected,
                'report': report, 'bundle': bundle, 'snapshot': snapshot, 'local_audit': local,
                'independent_observation': actual, 'independent_checks': independent,
                'dispatches': count, 'required_dispatches': writes, 'movement_records': records,
                'injected_source_calls': getattr(reader, 'injected_calls', 0), 'rejected_write': rejected_write}
            write(trial / 'result.json', row)
            write(trial / 'audit.json', local)
            row['phoenix_audit'] = persisted(trial)
            rows.append(row)
            write(folder / 'result.json', result)
            print(name, 'PASS' if row['pass'] else 'FAIL', flush=True)
            if not row['pass']: raise RuntimeError('m2_case_failed:' + name)
            if inactive:
                setup.append(switch_trajectory(inspection, True))
                inactive = False
            meter = Meter()
        movement.suppress_commands = movement.partial_commands = movement.missing_observations = False
        movement.read('/ur5e', list(JOINTS))
        movement.write('/ur5e', HOME_POSE)
        final_home = oracle.read('/ur5e', list(JOINTS))
        require_home(final_home)
        result['outside_task_reset'] = {'dispatches': 1, 'independent_observation': final_home}
        result['pass'] = len(rows) == 10 and all(r['pass'] for r in rows)
    except BaseException as error:
        result.update(error_type=type(error).__name__, error=str(error))
        raise
    finally:
        if inactive and inspection:
            try: setup.append(switch_trajectory(inspection, True))
            except BaseException as error: result.update(pass_=False, controller_restore_error=type(error).__name__)
        cleanup_errors = []
        for item in (movement, inspection, oracle, readiness_oracle):
            if item:
                try: item.close()
                except BaseException as error: cleanup_errors.append(type(error).__name__)
        result['simulator_cleanup'] = simulator.close()
        result['cleanup_errors'] = cleanup_errors
        if cleanup_errors or result['simulator_cleanup']['returncode'] != 0 or 'pass_' in result:
            result['pass'] = False
        write(folder / 'result.json', result)
    return result


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    folder = DESTINATION / f'm2-{len(list(DESTINATION.glob("m2-*"))) + 1:02d}'
    folder.mkdir()
    write(folder / 'history-before.json', verify_history())
    check = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        cwd=ROOT.parent / 'rosa-research', capture_output=True, text=True, timeout=120)
    (folder / 'research-tests.log').write_text(check.stdout + check.stderr)
    if check.returncode: raise RuntimeError('research_regression_failed_before_gazebo')
    os.environ.update(ROS_DOMAIN_ID='216', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    def expired(signum, frame): raise TimeoutError('m2_external_deadline_300_seconds')
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, 300)
    try:
        result = run_m2(folder)
        write(folder / 'history-after.json', verify_history())
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    print(json.dumps({'stage': 'M2', 'pass': result['pass'], 'cases': len(result['rows']), 'live_model_requests': 0}))
    if not result['pass']: raise SystemExit(1)


if __name__ == '__main__': main()
