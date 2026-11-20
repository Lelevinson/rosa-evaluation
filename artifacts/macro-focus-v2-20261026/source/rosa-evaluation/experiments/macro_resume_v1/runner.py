"""Reuse the frozen execution loop; change only output path and selected jobs."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

from rosa_reliability import ControlledStop
from experiments.macro_transfer_v1 import runner as original
from experiments.macro_transfer_v1.design import jobs as full_jobs

ROOT = original.ROOT
BASE = ROOT / 'artifacts/macro-transfer-v1-20261022'
DESTINATION = ROOT / 'artifacts/macro-transfer-v1-resume-r1-20261023'
QUOTA = 'subscription_sharing_usage_limit_exceeded'
ADDITIONAL_REQUEST_CAP = 32


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remaining_jobs(state, schedule):
    """Never select a completed outcome, including genuine model failures."""
    if state['status'] != 'STOPPED' or state.get('current_trial') is not None:
        raise RuntimeError('original_batch_not_cleanly_stopped')
    if state.get('simulator_cleanup', {}).get('returncode') != 0:
        raise RuntimeError('original_simulator_cleanup_not_verified')
    attempted = {(r['case'], r['condition']): r for r in state['trials']}
    if len(attempted) != len(state['trials']):
        raise RuntimeError('duplicate_original_cell')
    selected = []
    for index, job in enumerate(schedule):
        key = job['case']['id'], job['condition']
        row = attempted.get(key)
        if row is not None:
            if row['inference']['usage_complete']:
                continue  # Passing and failing model outcomes are both final.
            if (QUOTA not in row['answer'] or row['native_operations'] != 0
                    or row['tool_attempts'] != 0):
                raise RuntimeError('uncertain_prior_attempt_do_not_replay:' + row['run_id'])
        selected.append({'original_schedule_index': index,
            'prior_run_id': row['run_id'] if row else None,
            'reason': 'quota_interrupted_no_tools' if row else 'not_started',
            **deepcopy(job)})
    return selected


def verify_original():
    manifest = read(BASE / 'freeze.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT.parent / name) != expected or sha(BASE / 'source' / name) != expected:
            raise RuntimeError('original_frozen_source_changed:' + name)
    return manifest


def verify_freeze():
    verify_original()
    manifest = read(DESTINATION / 'freeze.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT.parent / name) != expected or sha(DESTINATION / 'source' / name) != expected:
            raise RuntimeError('continuation_frozen_source_changed:' + name)
    for name, expected in manifest['original_artifacts'].items():
        if sha(BASE / name) != expected:
            raise RuntimeError('original_evidence_changed:' + name)
    return manifest


@contextmanager
def execution_scope(plan):
    """Temporary orchestration settings; the agent/controller/scorer stay frozen."""
    previous = original.DESTINATION, original.jobs, original.verify_freeze
    original.DESTINATION = DESTINATION
    original.jobs = lambda phase: [deepcopy(j) for j in plan] if phase == 'gazebo' else []
    original.verify_freeze = verify_freeze
    try:
        yield
    finally:
        original.DESTINATION, original.jobs, original.verify_freeze = previous


class CombinedCounter(dict):
    def __init__(self, used, previous_active_seconds):
        super().__init__(calls=used)
        self.initial, self.started, self.previous_seconds = used, time.monotonic(), previous_active_seconds

    def __setitem__(self, key, value):
        if key == 'calls' and (value - self.initial > ADDITIONAL_REQUEST_CAP or value > 144 or
                self.previous_seconds + time.monotonic() - self.started >= 4500):
            raise ControlledStop('combined_continuation_resource_limit_before_dispatch')
        super().__setitem__(key, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    manifest = verify_freeze()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    if read(BASE / 'session-siwc.json')['auth']['session_cleanup'] != 'REVOKED':
        raise RuntimeError('original_session_cleanup_not_verified')
    plan = remaining_jobs(state, full_jobs('gazebo'))
    if plan != read(DESTINATION / 'schedule.json')['jobs'] or len(plan) != 4:
        raise RuntimeError('continuation_schedule_mismatch')
    if (DESTINATION / 'gazebo/siwc').exists():
        raise RuntimeError('continuation_already_attempted_no_automatic_rerun')
    os.environ['ROS_DOMAIN_ID'] = '212'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    for key in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from rosa_backends import create_model
    auth_status = {}
    model = transport = None
    used = state['total_model_calls']
    previous_seconds = (datetime.fromisoformat(state['updated_utc']) - datetime.fromisoformat(state['started_utc'])).total_seconds()
    counter = CombinedCounter(used, previous_seconds)
    try:
        with interactive_session(request_budget=32, timeout=1800, status=auth_status, require_renewal=True) as auth:
            transport = SiwcBackend(token_provider=auth.access_token, request_budget=32)
            if 'gpt-6.1-sol' not in {m['slug'] for m in transport.models()}:
                raise RuntimeError('original_model_not_in_account_catalog')
            model = create_model('siwc', model='gpt-6.1-sol', siwc_transport=transport)
            # Consent waiting is not active experiment time.
            counter.started = time.monotonic()
            with execution_scope(plan), original.gazebo_lock():
                original.run_backend('siwc', model, 'gazebo', counter, transport)
    finally:
        if model is not None:
            original.write(DESTINATION / 'hosted-request-records.json', model.request_records)
            model.close()
        elif transport:
            transport.close()
        original.write(DESTINATION / 'session-siwc.json', {'auth': auth_status, 'request_cap': 32})
        original.write(DESTINATION / 'resource-ledger.json', {'prior_hosted_calls': used,
            'additional_hosted_calls': counter['calls'] - used, 'combined_hosted_calls': counter['calls'],
            'additional_cap': 32, 'original_cap': 144, 'original_freeze_sha256': manifest['original_freeze_sha256']})


if __name__ == '__main__':
    main()
