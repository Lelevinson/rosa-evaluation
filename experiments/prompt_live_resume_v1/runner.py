import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import time
from rosa_reliability import ControlledStop
from experiments.prompt_live_v1 import runner as original
from experiments.prompt_live_v1.design import jobs
from experiments.macro_resume_v1.runner import verify_freeze as verify_history

ROOT = original.ROOT
BASE = original.DESTINATION
DESTINATION = ROOT / 'artifacts/prompt-contract-v1-live-resume-r1-20261026'
ADDITIONAL_CAP = 40


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remaining_jobs(state, schedule):
    if (state['status'] != 'STOPPED' or state.get('current_trial') is not None or
            not state.get('authorization_or_service_unavailable') or
            state.get('simulator_cleanup', {}).get('returncode') != 0):
        raise RuntimeError('original_interruption_not_cleanly_bounded')
    attempts = state['trials']
    if len(attempts) > len(schedule):
        raise RuntimeError('unexpected_attempt_count')
    selected = []
    censored = 0
    for index, job in enumerate(schedule):
        row = attempts[index] if index < len(attempts) else None
        if row and (row['case'], row['condition']) != (job['case']['id'], job['condition']):
            raise RuntimeError('original_schedule_mismatch')
        if row and row['inference']['usage_complete']:
            continue  # Preserve genuine model failures as well as successes.
        if row:
            # A new dialogue after interruption is permitted only for the last
            # read-only attempt. Never reset/replay an uncertain movement.
            if (index != len(attempts) - 1 or not row['answer'].startswith('An error occurred:') or
                    row['score']['accepted_report_status'] is not None or
                    row['score']['dispatch_count'] != 0 or row['score']['dispatch_violations'] or
                    sum(e['status'] == 'UNRETURNED' for e in row['inference']['events']) != 1 or
                    any(e['status'] not in ('RETURNED', 'UNRETURNED') for e in row['inference']['events'])):
                raise RuntimeError('uncertain_or_scoreable_attempt_must_not_be_replayed')
            evidence = read(BASE / 'gazebo/siwc' / row['run_id'] / 'evidence.json')
            if any(r['kind'] in ('write', 'trajectory_request') for r in evidence['transport_records']):
                raise RuntimeError('prior_command_dispatch_do_not_replay')
            censored += 1
        selected.append({'original_schedule_index': index,
            'prior_run_id': row['run_id'] if row else None,
            'reason': 'censored_service_interruption_read_only' if row else 'not_started', **deepcopy(job)})
    if censored != 1:
        raise RuntimeError('expected_exactly_one_read_only_censored_attempt')
    return selected


def verify_original():
    verify_history()
    manifest = read(BASE / 'freeze.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT.parent / name) != expected or sha(BASE / 'source' / name) != expected:
            raise RuntimeError('original_validation_source_changed:' + name)
    return manifest


def verify_freeze():
    verify_original()
    manifest = read(DESTINATION / 'freeze.json')
    for name, expected in manifest['files'].items():
        if sha(ROOT.parent / name) != expected or sha(DESTINATION / 'source' / name) != expected:
            raise RuntimeError('continuation_source_changed:' + name)
    for name, expected in manifest['original_evidence'].items():
        if sha(BASE / name) != expected:
            raise RuntimeError('original_evidence_changed:' + name)
    return manifest


@contextmanager
def execution_scope(plan):
    previous = original.DESTINATION, original.jobs, original.verify_freeze
    original.DESTINATION = DESTINATION
    original.jobs = lambda phase: deepcopy(plan) if phase == 'gazebo' else []
    original.verify_freeze = verify_freeze
    try:
        yield
    finally:
        original.DESTINATION, original.jobs, original.verify_freeze = previous


class CombinedCounter(dict):
    def __init__(self, used, prior_seconds):
        super().__init__(calls=used)
        self.initial, self.prior_seconds, self.started = used, prior_seconds, time.monotonic()

    def __setitem__(self, key, value):
        if key == 'calls' and (value - self.initial > ADDITIONAL_CAP or value > 72 or
                self.prior_seconds + time.monotonic() - self.started >= 4500):
            raise ControlledStop('combined_validation_resource_limit_before_dispatch')
        super().__setitem__(key, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    verify_freeze()
    state = read(BASE / 'gazebo/siwc/checkpoint.json')
    plan = remaining_jobs(state, jobs('gazebo'))
    if plan != read(DESTINATION / 'schedule.json')['jobs'] or len(plan) != 5:
        raise RuntimeError('unexpected_continuation_plan')
    if (DESTINATION / 'gazebo/siwc').exists():
        raise RuntimeError('single_continuation_already_attempted_no_retry_loop')
    if read(BASE / 'session-siwc.json')['auth']['session_cleanup'] != 'REVOKED':
        raise RuntimeError('original_session_cleanup_unverified')
    os.environ.update(ROS_DOMAIN_ID='212', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST')
    for key in ('LANGCHAIN_TRACING', 'LANGCHAIN_TRACING_V2', 'LANGSMITH_TRACING'):
        os.environ[key] = 'false'
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    from rosa_auth.session import interactive_session
    from rosa_auth.responses import SiwcBackend
    from rosa_backends import create_model
    prior_seconds = (datetime.fromisoformat(state['updated_utc']) - datetime.fromisoformat(state['started_utc'])).total_seconds()
    counter = CombinedCounter(state['total_model_calls'], prior_seconds)
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
            'additional_reserved_calls': counter['calls'] - counter.initial, 'combined_reserved_calls': counter['calls'],
            'additional_cap': 40, 'original_combined_cap': 72})


if __name__ == '__main__':
    main()
