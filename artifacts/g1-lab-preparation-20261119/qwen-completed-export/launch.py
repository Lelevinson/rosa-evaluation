"""Explicitly acknowledged Qwen lab campaign; no consent or hidden task replay."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import time
from common import ROOT, REV, read, write, verify
from local_model import MeasuredOllama, LocalObservation
from recovery import Campaign
from runtime_support import evaluate_progress
from adjudication import summarize
from runtime_support import empty_bundle
import trial as runtime

ENDPOINT = 'http://127.0.0.1:11439'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--resume-unstarted', action='store_true')
    args = parser.parse_args()
    verify(require_seal=True)
    ack = read(ROOT / 'owner-launch-acknowledgment.json')
    assert ack['launch_allowed'] and ack['trials'] == 76 and ack['physical_request_cap'] == 611
    assert ack['freeze_sha256'] == hashlib.sha256((ROOT / 'freeze.json').read_bytes()).hexdigest()
    assert args.execute, 'Explicit execution flag required'
    if not args.resume_unstarted:
        assert not (ROOT / 'RUN_ONCE').exists()
        (ROOT / 'RUN_ONCE').write_text('No replacement of completed or censored trials.\n')
        status = {'status': 'STARTING', 'planned': 76, 'completed': 0, 'live_model_requests': 0,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'current_trial': None,
            'execution_host': 'Lab SSH / existing Jazzy container', 'backend': 'ollama',
            'auxiliary_load_requests': read(ROOT / 'MODEL_LOAD_PREFLIGHT.json')['physical_load_requests']}
    else:
        status = read(ROOT / 'status.json')
        assert status['status'] == 'STOPPED'
    def checkpoint(budget):
        status['campaign'] = budget
        status['charged_total_requests'] = budget['reserved_requests']
        status['live_model_requests'] = budget['reserved_requests'] - status['auxiliary_load_requests']
        write('status.json', status)
    campaign = Campaign(checkpoint)
    campaign.requests = status['auxiliary_load_requests']
    if args.resume_unstarted:
        campaign.requests = status['campaign']['reserved_requests']
        campaign.retries = status['campaign']['infrastructure_retries']
        campaign.events = status['campaign']['events']
        origin = datetime.fromisoformat(status['started_utc'])
        campaign.started = time.monotonic() - (datetime.now(timezone.utc) - origin).total_seconds()
    prior_hashes = {}
    retained = set()
    for path in (ROOT / 'trials').glob('*/result.json'):
        row = read(path)
        assert row['local_audit']['pass'] and read(path.parent / 'phoenix-audit.json')['pass']
        retained.add(row['id'])
        for p in path.parent.glob('*.json'):
            prior_hashes[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    phase = ROOT / 'operator' / f"phase-{len(list((ROOT / 'operator').glob('phase-*'))) + 1:02d}"
    phase.mkdir(parents=True, exist_ok=False)
    (phase / 'ENTRY_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
    (phase / 'PRIOR_TRIAL_HASHES.json').write_text(json.dumps(prior_hashes, indent=2) + '\n')
    journal_name = phase.relative_to(ROOT) / 'physical-call-journal.json'
    status['completed'] = len(retained)
    model = MeasuredOllama(model='qwen3.5:9b', base_url=ENDPOINT,
        num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
        streaming=False, reasoning=False, cache=False, client_kwargs={'timeout': 180})
    observation = LocalObservation()
    model.observe_with(observation)
    try:
        status['status'] = 'RUNNING'
        for item in read(ROOT / 'plan.json'):
            if item['id'] in retained:
                continue
            status['current_trial'] = item['id']
            checkpoint(campaign.snapshot())
            before = len(observation.error_metadata_records)
            row = runtime.trial(item, model, observation, campaign)
            retained.add(item['id'])
            status['completed'] = len(retained)
            status['current_trial'] = None
            checkpoint(campaign.snapshot())
            print(json.dumps({'completed': len(retained), 'planned': 76, 'trial_id': item['id'],
                'effective_status': evaluate_progress(row)['primary_status'],
                'calls': row['inference']['calls'], 'charged_total': campaign.requests}), flush=True)
            write(journal_name, model.request_records)
            if len(observation.error_metadata_records) > before:
                raise RuntimeError('Local_transport_failure_preserved_inspect_before_unstarted_resume')
        status['status'] = 'COMPLETE'
        verify(require_seal=True)
    except BaseException as error:
        status.update(status='STOPPED', error_type=type(error).__name__)
        raise
    finally:
        status['completed_utc'] = datetime.now(timezone.utc).isoformat()
        checkpoint(campaign.snapshot())
        write(journal_name, model.request_records)
        bundle = empty_bundle()
        rows = [read(p) for p in sorted((ROOT / 'trials').glob('*/result.json'))]
        write('analysis/current.json', summarize(rows, [r['id'] for r in read(ROOT / 'plan.json')],
            bundle, bundle['rubric_sha256']))
        assert all(hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == d for n, d in prior_hashes.items())


if __name__ == '__main__':
    main()
