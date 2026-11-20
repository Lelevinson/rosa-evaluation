"""Audit completed evidence, then make a source-complete review package."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / 'rosa-evaluation/artifacts/macro-transfer-v1-20261022'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(ROOT / 'rosa-evaluation'))
    from experiments.macro_transfer_v1.design import catalogue, cases
    from experiments.macro_transfer_v1.scoring import score
    specs = {s['id']: s for s in cases()}
    analysis = read(CAMPAIGN / 'analysis.json')
    if not analysis['complete']:
        raise RuntimeError('campaign_not_complete_do_not_publish_partial_as_complete')
    freeze = read(CAMPAIGN / 'freeze.json')
    checks, all_rows = [], []
    for backend in ('ollama', 'siwc'):
        folder = CAMPAIGN / 'gazebo' / backend
        state = read(folder / 'checkpoint.json')
        assert state['status'] == 'COMPLETE' and len(state['trials']) == 18
        assert state['total_model_calls'] <= 144
        assert state['simulator_cleanup']['returncode'] == 0
        assert read(folder / 'fresh-controls/result.json')['pass']
        assert read(CAMPAIGN / 'operator' / (backend + '-supervisor.json'))['status'] == 'COMPLETE'
        assert read(CAMPAIGN / 'operator' / (backend + '-power-release.json'))['released']
        for row in state['trials']:
            trial = folder / row['run_id']
            raw = read(trial / 'evidence.json')
            saved = read(trial / 'result.json')
            assert row == saved
            assert row['audit']['pass'] and read(trial / 'phoenix-audit.json')['pass']
            local = read(trial / 'trace.json')['spans']
            persisted = read(trial / 'phoenix-trace.json')
            ids = lambda spans: {s['context']['span_id'].removeprefix('0x') for s in spans}
            assert ids(local) == ids(persisted)
            assert row['inference']['calls'] <= 8 and row['native_operations'] <= 10
            assert not row['score']['accepted_unsupported_selected_goal_success']
            assert not row['score']['dispatch_violations']
            assert row['score']['pass'] == bool(row['score']['legacy_outcome_contract_pass'] and row['score']['coverage_pass'])
            assert len(raw['session']['operations']) == row['native_operations']
            selected = raw['session']['selected_skill']
            reconstructed = SimpleNamespace(snapshot=lambda: raw['session'],
                selected_skill=selected, targets=catalogue('gazebo')[selected or 'pose_amber'])
            rescored = score(reconstructed, specs[row['case']],
                SimpleNamespace(records=raw['transport_records']), row['answer'],
                raw['claim_time_oracles'], catalogue('gazebo'), .025, raw['private_final_state'])
            assert rescored == row['score'], 'saved_score_recomputation_mismatch:' + row['run_id']
            all_rows.append(row)
            checks.append({'backend': backend, 'run_id': row['run_id'], 'outcome_correct': row['score']['pass'],
                           'exact_persisted_spans': True, 'resource_audit': True})
    assert read(CAMPAIGN / 'preflight/result.json')['pass']
    assert read(CAMPAIGN / 'deterministic-preflight/result.json')['pass']
    assert read(CAMPAIGN / 'deterministic-preflight/cleanup.json')['returncode'] == 0
    assert read(CAMPAIGN / 'session-siwc.json')['auth']['session_cleanup'] == 'REVOKED'
    assert read(CAMPAIGN / 'local-model-unload.json')['done_reason'] == 'unload'
    source_names = {}
    for name, value in freeze['files'].items():
        path = CAMPAIGN / 'source' / name
        assert sha(path) == value, name
        assert sha(ROOT / name) == value, 'runtime source drift:' + name
        source_names[path.relative_to(ROOT).as_posix()] = value
    retention = []
    for backend in ('ollama', 'siwc'):
        pairs = [p for p in analysis['paired_cases'] if p['backend'] == backend]
        losses = [p['case'] for p in pairs if p['conditions']['workflow']['correct'] and not p['conditions']['macro']['correct']]
        matched = [p for p in pairs if p['conditions']['workflow']['correct'] and p['conditions']['macro']['correct']]
        macro_calls = sum(p['conditions']['macro']['calls'] for p in matched)
        workflow_calls = sum(p['conditions']['workflow']['calls'] for p in matched)
        macro_native = sum(p['conditions']['macro']['native'] for p in matched)
        workflow_native = sum(p['conditions']['workflow']['native'] for p in matched)
        retention.append({'backend': backend, 'paired_primary_losses': losses,
            'matched_correct_pairs': len(matched), 'macro_calls': macro_calls, 'workflow_calls': workflow_calls,
            'macro_native': macro_native, 'workflow_native': workflow_native,
            'provisional_screen_pass': not losses and macro_calls <= workflow_calls and macro_native <= workflow_native})
    failures = [{k: r[k] for k in ('backend', 'case', 'condition', 'answer', 'score', 'inference', 'wall_seconds')}
                for r in all_rows if not r['score']['pass']]
    review = {'evidence_audit_pass': True, 'checks': checks, 'retention_screen': retention,
              'failed_outcomes': failures, 'all_frozen_sources_present': len(source_names)}
    (CAMPAIGN / 'independent-review.json').write_text(json.dumps(review, indent=2) + '\n')
    lines = [(CAMPAIGN / 'REPORT_FOR_CHATGPT.md').read_text(), '\n## Independent audit and limitations\n',
        f'All {len(checks)} live trials passed local/persisted trace and resource audits. '
        f'All {len(source_names)} frozen source copies match their digests. '
        'Both simulators exited cleanly, sleep holds were released, Qwen was unloaded and hosted tokens revoked.\n',
        'The initial scripted trace attempt failed because Phoenix was unavailable; it is retained under '
        'preflight-attempt-1-phoenix-unavailable. After starting the existing local service, the complete '
        'scripted preflight passed. No live trial was replaced or retuned.\n',
        '## Predeclared simple-macro retention screen\n', '```json', json.dumps(retention, indent=2), '```\n',
        '## Task failures and full resource records\n', '```json', json.dumps(failures, indent=2), '```\n',
        '## Interpretation and next decision\n',
        'The existing workflow and the strong macro share the same read/conditional-write/verify policy. '
        'There is no evidence of a new tool-selection algorithm in this contrast. Use the per-backend '
        'retention screen to describe observed tradeoffs; do not reinterpret a failed screen as success. '
        'Even when the macro matches or beats the workflow, this small pilot does not establish '
        'statistical non-inferiority or generalization. The practical candidate is the smallest reusable '
        'bounded skill wrapper with trusted outcome reporting and explicit model handoff.\n',
        'A further study should use independently designed tasks and repeated paired trials to test that '
        'simple wrapper against primitive tools. Preserve observation freshness, actual fault exercise, '
        'full token/native/latency accounting and identical permissions. Do not add JTVR, episodic memory '
        'or a general planner to explain these results. No physical-robot readiness follows.\n',
        '## Reproducibility\n',
        'Sources, both dependency lockfiles, task schedule, protocol, all raw records, independent observations, '
        'actual Phoenix span sets, control/reset costs and cleanup receipts are archived. The original prior '
        'ZIP remains unchanged; its uv.lock omission was corrected in a separately named complete archive. '
        'This archive verifies inclusion of every frozen source, not only hashes of listed members.\n']
    (CAMPAIGN / 'DETAILED_REVIEW_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    files = [p for p in CAMPAIGN.rglob('*') if p.is_file() and p.suffix != '.tmp' and p.name != 'gazebo.lock']
    files.append(Path(__file__))
    manifest = {p.relative_to(ROOT).as_posix(): sha(p) for p in files}
    assert all(manifest.get(name) == value for name, value in source_names.items())
    destination = CAMPAIGN.parent / 'ROSA_MACRO_TRANSFER_V1_EVIDENCE_2026-10-22.zip'
    with ZipFile(destination, 'x', compression=ZIP_DEFLATED) as archive:
        for name in manifest:
            archive.write(ROOT / name, name)
        archive.writestr('evidence-manifest.json', json.dumps(manifest, indent=2) + '\n')
    with ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(n)).hexdigest() == d for n, d in manifest.items())
        assert all(hashlib.sha256(archive.read(n)).hexdigest() == d for n, d in source_names.items())
    destination.with_suffix('.sha256').write_text(sha(destination) + '  ' + destination.name + '\n')
    print(json.dumps({'complete': True, 'files': len(files), 'frozen_sources_in_zip': len(source_names),
                      'archive': str(destination), 'sha256': sha(destination)}))


if __name__ == '__main__':
    main()
