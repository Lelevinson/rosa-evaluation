import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import os
import time
from experiments.prompt_live_resume_v1 import runner as r1
from experiments.simulator_home_v1 import HomeSpawnSimulator

ROOT, BASE, original = r1.ROOT, r1.BASE, r1.original
FIRST = r1.DESTINATION
DESTINATION = ROOT / 'artifacts/prompt-contract-v1-live-resume-r2-20261026'
PREFLIGHT = ROOT / 'artifacts/simulator-home-v1-preflight-20261026'
read, sha, jobs, remaining_jobs = r1.read, r1.sha, r1.jobs, r1.remaining_jobs


def verify_setup():
    proof = read(PREFLIGHT / 'result.json')
    if not (proof['pass'] and proof['cold_starts'] == 3 and proof['live_model_requests'] == 0 and
            all(row['controls'] == 6 and row['simulator_cleanup']['returncode'] == 0 for row in proof['rows'])):
        raise RuntimeError('spawn_repair_cold_start_gate_failed')
    for name, expected in read(PREFLIGHT / 'source-digests.json').items():
        if sha(ROOT.parent / name) != expected or sha(PREFLIGHT / 'source' / name) != expected:
            raise RuntimeError('validated_spawn_source_changed:' + name)
    return proof


def verify_original():
    r1.verify_freeze()
    state = read(FIRST / 'gazebo/siwc/checkpoint.json')
    if not (state['status'] == 'STOPPED' and state['total_model_calls'] == 0 and
            not state['trials'] and state.get('current_trial') is None and
            state['error'] == 'independent_home_reset_failed' and
            state['simulator_cleanup']['returncode'] == 0 and
            read(FIRST / 'session-siwc.json')['auth']['session_cleanup'] == 'REVOKED'):
        raise RuntimeError('R2_only_permitted_after_zero_inference_setup_abort_not_service_retry_loop')
    verify_setup()


def verify_freeze():
    verify_original()
    manifest = read(DESTINATION / 'freeze.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT.parent / name) != expected or sha(DESTINATION / 'source' / name) != expected:
            raise RuntimeError('R2_source_changed:' + name)
    for name, expected in manifest['R1_evidence'].items():
        if sha(FIRST / name) != expected:
            raise RuntimeError('R1_evidence_changed:' + name)
    for name, expected in manifest['setup_evidence'].items():
        if sha(PREFLIGHT / name) != expected:
            raise RuntimeError('setup_evidence_changed:' + name)
    return manifest


@contextmanager
def execution_scope(plan):
    from experiments.ur5e_transfer_v1 import arm
    previous = original.DESTINATION, original.jobs, original.verify_freeze, arm.ArmSimulator
    original.DESTINATION = DESTINATION
    original.jobs = lambda phase: deepcopy(plan) if phase == 'gazebo' else []
    original.verify_freeze = verify_freeze
    arm.ArmSimulator = HomeSpawnSimulator
    try:
        yield
    finally:
        original.DESTINATION, original.jobs, original.verify_freeze, arm.ArmSimulator = previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    verify_freeze()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    plan = remaining_jobs(state, jobs('gazebo'))
    if plan != read(DESTINATION / 'schedule.json')['jobs'] or len(plan) != 5:
        raise RuntimeError('R2_schedule_mismatch')
    if (DESTINATION / 'gazebo/siwc').exists():
        raise RuntimeError('R2_already_attempted_no_retry_loop')
    os.environ.update(ROS_DOMAIN_ID='212', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    for key in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from rosa_backends import create_model
    failed_setup = read(FIRST / 'gazebo/siwc/checkpoint.json')
    seconds = lambda record: (datetime.fromisoformat(record['updated_utc']) - datetime.fromisoformat(record['started_utc'])).total_seconds()
    counter = r1.CombinedCounter(state['total_model_calls'], seconds(state) + seconds(failed_setup))
    status, model, transport = {}, None, None
    try:
        with interactive_session(request_budget=40, timeout=1800, status=status, require_renewal=True) as auth:
            transport = SiwcBackend(token_provider=auth.access_token, request_budget=40)
            if 'gpt-6.1-sol' not in {m['slug'] for m in transport.models()}:
                raise RuntimeError('frozen_model_unavailable')
            model = create_model('siwc', model='gpt-6.1-sol', siwc_transport=transport)
            counter.started = time.monotonic()
            with execution_scope(plan), original.gazebo_lock():
                original.run_backend('siwc', model, 'gazebo', counter, transport)
    finally:
        if model is not None:
            original.write(DESTINATION / 'hosted-request-records.json', model.request_records)
            model.close()
        elif transport:
            transport.close()
        original.write(DESTINATION / 'session-siwc.json', {'auth': status, 'additional_request_cap': 40})
        original.write(DESTINATION / 'resource-ledger.json', {'prior_reserved_calls': counter.initial,
            'R1_reserved_calls': 0, 'additional_reserved_calls': counter['calls'] - counter.initial,
            'combined_reserved_calls': counter['calls'], 'additional_cap': 40, 'original_combined_cap': 72})


if __name__ == '__main__':
    main()
