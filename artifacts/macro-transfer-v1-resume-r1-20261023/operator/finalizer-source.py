"""Join continuation cells without replacing any completed original outcome."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'rosa-evaluation/artifacts/macro-transfer-v1-20261022'
RESUME = ROOT / 'rosa-evaluation/artifacts/macro-transfer-v1-resume-r1-20261023'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(ROOT / 'rosa-evaluation'))
    from experiments.macro_resume_v1.runner import verify_freeze, QUOTA
    from experiments.macro_transfer_v1.design import cases, catalogue
    from experiments.macro_transfer_v1.scoring import score
    verify_freeze()
    specs = {s['id']: s for s in cases()}
    permitted = {(j['case']['id'], j['condition']) for j in read(RESUME / 'schedule.json')['jobs']}
    matrix, attempts, service_interruptions, audited = {}, [], [], []
    scopes = [(BASE, b) for b in ('ollama', 'siwc')] + [(RESUME, 'siwc')]
    for campaign, backend in scopes:
        folder = campaign / 'gazebo' / backend
        checkpoint = folder / 'checkpoint.json'
        if not checkpoint.exists():
            continue
        state = read(checkpoint)
        assert state['status'] in ('COMPLETE', 'STOPPED')
        assert state['simulator_cleanup']['returncode'] == 0
        assert read(folder / 'fresh-controls/result.json')['pass']
        for row in state['trials']:
            trial = folder / row['run_id']
            raw = read(trial / 'evidence.json')
            assert read(trial / 'result.json') == row
            assert row['audit']['pass'] and read(trial / 'phoenix-audit.json')['pass']
            local, persisted = read(trial / 'trace.json')['spans'], read(trial / 'phoenix-trace.json')
            ids = lambda spans: {s['context']['span_id'].removeprefix('0x') for s in spans}
            assert ids(local) == ids(persisted)
            assert all(s.get('end_time') and (not s.get('parent_id') or
                s['parent_id'].removeprefix('0x') in ids(persisted)) for s in persisted)
            selected = raw['session']['selected_skill']
            reconstructed = SimpleNamespace(snapshot=lambda: raw['session'], selected_skill=selected,
                targets=catalogue('gazebo')[selected or 'pose_amber'])
            assert score(reconstructed, specs[row['case']], SimpleNamespace(records=raw['transport_records']),
                row['answer'], raw['claim_time_oracles'], catalogue('gazebo'), .025,
                raw['private_final_state']) == row['score']
            assert row['inference']['calls'] <= 8 and row['native_operations'] <= 10
            assert not row['score']['accepted_unsupported_selected_goal_success']
            assert not row['score']['dispatch_violations']
            quota = QUOTA in row['answer'] and not row['inference']['usage_complete']
            recorded = {**row, 'campaign': campaign.name,
                'evidence_folder': trial.relative_to(ROOT).as_posix(), 'service_interrupted': quota}
            attempts.append(recorded)
            audited.append({'folder': trial.relative_to(ROOT).as_posix(),
                'saved_score_recomputed': True, 'exact_persisted_spans': True})
            if quota:
                service_interruptions.append(recorded)
                continue
            key = (backend, row['case'], row['condition'])
            if campaign == RESUME:
                assert (row['case'], row['condition']) in permitted
            assert key not in matrix, 'completed_original_outcome_would_be_replaced'
            matrix[key] = recorded
    ledger = read(RESUME / 'resource-ledger.json')
    assert ledger['additional_hosted_calls'] <= 32 and ledger['combined_hosted_calls'] <= 75
    assert sum(r['inference']['calls'] for r in attempts if r['backend'] == 'siwc') == ledger['combined_hosted_calls']
    auth = read(RESUME / 'session-siwc.json')
    assert auth['auth']['session_cleanup'] in ('REVOKED', 'NO_TOKEN_SESSION')
    assert read(RESUME / 'operator/power-release.json')['released']
    for backend in ('ollama', 'siwc'):
        assert read(BASE / 'operator' / (backend + '-power-release.json'))['released']
    complete = len(matrix) == 36
    summaries, retention = [], []
    for backend in ('ollama', 'siwc'):
        for condition in ('model', 'macro', 'workflow'):
            cells = [r for key, r in matrix.items() if key[0] == backend and key[2] == condition]
            all_attempts = [r for r in attempts if r['backend'] == backend and r['condition'] == condition]
            summaries.append({'backend': backend, 'condition': condition, 'scoreable': len(cells),
                'correct': sum(r['score']['pass'] for r in cells),
                'scoreable_calls': sum(r['inference']['calls'] for r in cells),
                'all_request_attempts': sum(r['inference']['calls'] for r in all_attempts),
                'known_input_tokens': sum(r['inference']['known_input_tokens'] for r in all_attempts),
                'known_output_tokens': sum(r['inference']['known_output_tokens'] for r in all_attempts),
                'censored_attempts': sum(not r['inference']['usage_complete'] for r in all_attempts),
                'native': sum(r['native_operations'] for r in all_attempts),
                'invalid': sum(r['score']['invalid_attempts'] for r in all_attempts),
                'scoreable_seconds': sum(r['wall_seconds'] for r in cells)})
        pairs = [(matrix.get((backend, s['id'], 'macro')), matrix.get((backend, s['id'], 'workflow')))
                 for s in cases()]
        if not all(a and b for a, b in pairs):
            retention.append({'backend': backend, 'status': 'INCOMPLETE'})
            continue
        losses = [a['case'] for a, b in pairs if b['score']['pass'] and not a['score']['pass']]
        matched = [(a, b) for a, b in pairs if a['score']['pass'] and b['score']['pass']]
        calls = [sum(pair[i]['inference']['calls'] for pair in matched) for i in (0, 1)]
        native = [sum(pair[i]['native_operations'] for pair in matched) for i in (0, 1)]
        retention.append({'backend': backend, 'status': 'EVALUATED', 'paired_primary_losses': losses,
            'matched_correct_pairs': len(matched), 'macro_calls': calls[0], 'workflow_calls': calls[1],
            'macro_native': native[0], 'workflow_native': native[1],
            'numerical_screen_pass': not losses and calls[0] <= calls[1] and native[0] <= native[1],
            'larger_study_readiness': 'BLOCKED_BY_SHARED_PROMPT_CONTRACT_EXCEPTION'})
    missing = [{'backend': b, 'case': s['id'], 'condition': c} for b in ('ollama', 'siwc')
               for s in cases() for c in ('model', 'macro', 'workflow') if (b, s['id'], c) not in matrix]
    result = {'measurement_matrix_complete': complete, 'scoreable_cells': len(matrix),
        'attempt_records': len(attempts), 'service_interruptions': len(service_interruptions),
        'summaries': summaries, 'retention': retention, 'missing_cells': missing, 'resource_ledger': ledger,
        'audits': audited, 'original_scores_and_artifacts_unchanged': True,
        'prompt_contract_exception_preserved': True}
    (RESUME / 'combined-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# ROSA macro comparison: combined original and four-cell continuation', '',
        '**Measurement matrix: ' + ('COMPLETE (36 cells).' if complete else 'INCOMPLETE.') + '** '
        'The original quota interruption is retained separately. This report joins the original '
        'scoreable outcomes with only authorized remaining cells; no completed pass or failure was replaced.', '',
        '| Backend | Condition | Correct / scoreable | Scoreable calls | All attempts | Known input tokens | Known output tokens | Native | Invalid | Seconds (scoreable) |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in summaries:
        lines.append(f'| {r["backend"]} | {r["condition"]} | {r["correct"]}/{r["scoreable"]} | '
            f'{r["scoreable_calls"]} | {r["all_request_attempts"]} | {r["known_input_tokens"]} | '
            f'{r["known_output_tokens"]} | {r["native"]} | {r["invalid"]} | {r["scoreable_seconds"]:.2f} |')
    lines += ['', 'Known tokens exclude unknown usage from service-interrupted generations. Those '
        'requests count in all-attempt costs and are never assumed zero-cost. No outcome was imputed.', '',
        '## Per-case matrix', '', '| Backend | Case | Primitive tools | Macro | Workflow |',
        '| --- | --- | --- | --- | --- |']
    for backend in ('ollama', 'siwc'):
        for spec in cases():
            cells = []
            for condition in ('model', 'macro', 'workflow'):
                row = matrix.get((backend, spec['id'], condition))
                cells.append('UNFILLED' if row is None else
                    f'{"PASS" if row["score"]["pass"] else "FAIL"} / {row["inference"]["calls"]} calls')
            lines.append(f'| {backend} | {spec["id"]} | ' + ' | '.join(cells) + ' |')
    lines += ['', '## Continuation provenance and limits', '',
        'The continuation was frozen separately before inference on2026-10-23 Asia/Taipei. '
        'It reused the exact original runner, agent, model slug, prompts, schemas, budgets, '
        'controllers, faults and independent scorer. Only the remaining schedule, output path '
        'and freeze checks were supplied by a temporary coordinator. Six resume tests passed; '
        'six fresh deterministic controls preceded the continuation. Original preflight had40 '
        'tests,18 scripted ROSA/Phoenix cases and six initial deterministic controls, plus six '
        'controls before each original backend. Control/reset/startup/audit costs remain separate '
        'from in-trial seconds. Four pose variants remain one movement primitive.', '',
        'Requests and session receipt:', '', '```json', json.dumps(ledger, indent=2), '```', '',
        '```json', json.dumps(auth, indent=2), '```', '',
        'Per trial limits remain8 requests,180 seconds,16 tool attempts,10 native operations,one '
        'write and3 corrections. Quota-interrupted attempts are retained. The continuation has '
        'a hard32-request adapter cap and preserves the original144 combined hosted ceiling '
        'and4500 active seconds. Tokens stay in memory, consent is manual and cleanup revokes '
        'the session. Refresh support does not bypass quota; token_refreshes indicates whether '
        'actual renewal occurred. The hosted2048-token limit is an observed stopping threshold, '
        'not a requested hard generation cap. Qwen was not rerun; its frozen1024-per-call/2048 '
        'cumulative allowance,8192 context,Q4_K_M digest,temp0,seed42 and reasoning-off settings '
        'remain in the original freeze. Hidden hosted server version identity is not guaranteed '
        'by the unchanged model slug. No cross-backend hard-token equality is claimed.', '',
        '## Predeclared macro screen', '', '```json', json.dumps(retention, indent=2), '```', '',
        'These are the original numerical screen rules, not significance or equivalence tests. '
        'A failed screen remains a failure even if only one model call differs. Macro and workflow '
        'have the same acquisition policy; small live differences do not establish an algorithmic '
        'workflow advantage. The full system includes shared feedback, guards and report validation.', '',
        '## Audit exception and conclusions', '',
        'The shared default ROSA system prompts require unavailable discovery tools before action '
        'while the task requires selection first. This real instruction-contract inconsistency '
        'was intentionally preserved in the continuation for treatment comparability. Its causal '
        'contribution to failures is untested. Passing schema,trace and resource audits does not '
        'make the instruction contract consistent. Do not call this a clean validation of all '
        'interface fixes or a measurement of intrinsic model intelligence.', '',
        'Treat the simplest bounded macro as the main candidate to investigate, subject to the '
        'actual per-backend retention result above. There is no demonstrated new tool-selection '
        'algorithm in the state-tracked workflow. Preserve negative outcomes and resolve the '
        'shared prompt/tool mismatch prospectively. Validate that separate repair before using '
        'fresh repeated and independently designed tasks for a larger comparison. Do not add '
        'JTVR,memory,general planning or physical deployment to explain this pilot.', '',
        'One run per cell in a single pose family cannot establish statistical equivalence or '
        'general reliability. Both model decisions and program assistance are credited to the '
        'combined system. Fault exercise, reporting honesty and verified task completion remain '
        'distinct. No accepted unsupported selected-goal SUCCESS or dispatch violation appeared '
        'in these saved attempts; structured-claim metrics do not classify all free prose.', '',
        '## Detailed preserved interpretation notes', '', (BASE / 'INTERPRETATION_NOTES.md').read_text(), '',
        '## Missing cells', '', '```json', json.dumps(missing, indent=2), '```', '',
        'Every saved primary score was recomputed from raw evidence; actual Phoenix span IDs '
        'and closed trees matched every saved attempt. All original and continuation frozen '
        'source copies are included in the archive and verified against its bytes. The original '
        'partial archive and old checkpoints remain unchanged. Original STOPPED statuses describe '
        'the historical batch; this combined report is the authoritative joined-matrix status.']
    (RESUME / 'COMBINED_REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines) + '\n')
    paths = [p for campaign in (BASE, RESUME) for p in campaign.rglob('*')
             if p.is_file() and p.suffix != '.tmp' and p.name != 'gazebo.lock']
    paths.append(Path(__file__))
    manifest = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    sources = {}
    for campaign in (BASE, RESUME):
        for name, value in read(campaign / 'freeze.json')['files'].items():
            member = (campaign / 'source' / name).relative_to(ROOT).as_posix()
            assert manifest[member] == value
            sources[member] = value
    label = 'COMPLETE' if complete else 'INCOMPLETE'
    archive_path = RESUME.parent / ('ROSA_MACRO_TRANSFER_V1_' + label + '_WITH_CONTINUATION_2026-10-23.zip')
    with ZipFile(archive_path, 'x', compression=ZIP_DEFLATED) as archive:
        for name in manifest:
            archive.write(ROOT / name, name)
        archive.writestr('evidence-manifest.json', json.dumps(manifest, indent=2) + '\n')
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(n)).hexdigest() == value for n, value in manifest.items())
        assert all(hashlib.sha256(archive.read(n)).hexdigest() == value for n, value in sources.items())
    archive_path.with_suffix('.sha256').write_text(sha(archive_path) + '  ' + archive_path.name + '\n')
    receipt = {'status': 'COMPLETE' if complete else 'INCOMPLETE', 'measurement_matrix_complete': complete,
        'scoreable_cells': len(matrix), 'attempt_records_audited': len(attempts),
        'source_copies_in_archive': len(sources), 'manifest_entries': len(manifest),
        'archive': archive_path.name, 'sha256': sha(archive_path)}
    (RESUME / 'operator/finalization-status.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
