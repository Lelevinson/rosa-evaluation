"""Lab-only, zero-inference Qwen G1 closeout: bind Batch B ratings, run the unchanged frozen engine.

Modelled on stage-4-multimodel-20261119/operator/adjudicate_extension_20261120.py.
Reads retained trials and the preserved submission; writes only to a new directory
adjudicated-closeout-20261120/ (fails if it exists). No model, network or ROS calls.
"""
from pathlib import Path
import csv, io, json, hashlib, importlib.util, sys, zipfile
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]          # stage-4-qwen-lab-20261119
REV = ROOT.parent
INTAKE = ROOT/'operator/human-review-intake-20261120'
REVIEW = ROOT/'operator/heldout-human-review'
OUT = ROOT/'adjudicated-closeout-20261120'
STAGE3 = REV/'stage-3'
EXPECTED_PACKET = '5e6020394c348f5cf3b90adf76b07745bb68ef3c3f01fb6512ad8e3b7047c1d8'
EXPECTED_SUBMISSION = 'f8afa83fc6f813f7501cd7a5ca7fc43e334ca6492968f7316ccb833b1b1c354e'
sys.path[:0] = [str(STAGE3), str(STAGE3/'clarification-scoring-v2-20261119')]
from adjudication import VERSION, ELIGIBILITY, content_binding, summarize, validate_bundle, project_complete_rows

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, v): p.write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def main():
    assert sys.platform == 'linux', 'Formal analysis must execute on the lab.'
    verifier = load('qwen_protection', ROOT/'common.py')
    before = verifier.verify(require_seal=True); assert before['pass']
    paths = sorted((ROOT/'trials').glob('*/result.json'))
    all_evidence = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT/'trials').rglob('*') if p.is_file()}
    rows = [read(p) for p in paths]; assert len(rows) == 76
    assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
    controls = read(ROOT/'zero-model-validation-attempt02/VALIDATION.json')
    assert controls['pass'] is True and len(controls['controls']) == 8 and all(c['pass'] for c in controls['controls'])

    # Submission and declaration, exactly as preserved.
    zip_path = INTAKE/"lev's rating4.zip"; assert sha(zip_path) == EXPECTED_SUBMISSION
    with zipfile.ZipFile(zip_path) as z:
        assert sorted(z.namelist()) == ['REVIEWER_DECLARATION.md', 'ratings-filled-batch2.csv'] and z.testzip() is None
        csv_bytes, decl_bytes = z.read('ratings-filled-batch2.csv'), z.read('REVIEWER_DECLARATION.md')
    declaration = decl_bytes.decode('utf-8')
    assert 'Reviewer name: Levinson' in declaration and '2026/11/20' in declaration
    assert declaration.count(': YES') == 4 and '\nTeammate\n' in declaration
    assert 'I can provide YES uninvolved review under those conditions: __________' in declaration
    supplement = INTAKE/'SUPPLEMENTAL_DECLARATION_2026-11-20.md'
    supp = supplement.read_text(encoding='utf-8')
    assert 'he provided an uninvolved review' in supp and '**YES**' in supp
    ratings = list(csv.DictReader(io.StringIO(csv_bytes.decode('utf-8-sig'))))
    assert len(ratings) == 4 and len({r['case_id'] for r in ratings}) == 4

    mapping = read(REVIEW/'PRIVATE_MAPPING_DO_NOT_SEND.json')
    assert {r['case_id'] for r in ratings} == set(mapping)
    packet = REVIEW/'G1_NEW_HELDOUT_HUMAN_REVIEW_2026-11-19.zip'
    assert sha(packet) == read(REVIEW/'PACKET_RECEIPT.json')['sha256'] == EXPECTED_PACKET
    by_id = {r['id']: r for r in rows}; records = []
    with zipfile.ZipFile(packet) as z:
        rubric = hashlib.sha256(z.read('RUBRIC.md')).hexdigest()
        for rating in ratings:
            key = mapping[rating['case_id']]
            source = ROOT/'trials'/key['trial_id']/'result.json'
            assert sha(source) == key['row_sha256']
            row = by_id[key['trial_id']]; assert row['case']['kind'] == 'ambiguous' and row['mode'] == key['mode']
            assert rating['reviewer_name'] == 'Levinson' and rating['reason'].strip()
            assert all(rating[k] in ('YES', 'NO', 'CANNOT_JUDGE') for k in ('appropriate_clarification', 'no_unauthorized_action'))
            transcript = z.read(rating['case_id']+'.md')
            snapshot = row['snapshot']
            activity = dict(selected_capability_kind=snapshot['catalogue'].get(snapshot['selected_skill'], {}).get('kind', 'NONE'),
                            recorded_tool_executions=len(row['tool_inputs']), native_attempts=len(row['actor_records']),
                            accepted_reports=sum(x.get('accepted') is True for x in snapshot['reports']),
                            observed_dispatches=row['observer_records'][-1]['snapshot']['dispatches'])
            rendered = '# '+rating['case_id']+'\n\nUser request:\n\n'+row['case']['request']+'\n\nAssistant response:\n\n'+row['answer']+'\n\nRecorded activity:\n\n'+json.dumps(activity, indent=2)+'\n'
            assert transcript.decode('utf-8').replace('\r\n', '\n') == rendered, 'transcript mismatch '+rating['case_id']
            records.append(dict(trial_id=row['id'], packet_case_id=rating['case_id'], reviewer='Levinson', review_date='2026-11-20',
                appropriate_clarification=rating['appropriate_clarification'], no_unauthorized_action=rating['no_unauthorized_action'], reason=rating['reason'],
                eligibility={k: True for k in ELIGIBILITY},
                eligibility_basis='Four YES answers in the returned declaration; item 5 (uninvolved) relayed as YES by the owner after a form-entry error; self-attestation, not independently verified',
                declared_relationship='Teammate; prior reviews of separate cohorts are known; no-exposure answer is self-declared',
                binding=content_binding(row, rubric),
                provenance=dict(submission_sha256=sha(zip_path), csv_sha256=hashlib.sha256(csv_bytes).hexdigest(),
                                declaration_sha256=hashlib.sha256(decl_bytes).hexdigest(), supplement_sha256=sha(supplement),
                                transcript_sha256=hashlib.sha256(transcript).hexdigest()),
                declaration_delivery='Declaration in submission ZIP; item 5 answer from a separate owner-relayed statement'))
    assert len(records) == 4
    bundle = dict(version=VERSION, rubric_sha256=rubric, records=records,
                  scope='Qwen G1 held-out Batch B only; no cross-cohort transfer',
                  original_packet_sha256=sha(packet), identity_basis='Owner-supplied ZIP and owner-relayed item-5 answer; no cryptographic identity proof')
    validate_bundle(bundle, rubric)
    schedule = read(ROOT/'plan.json')
    summary = summarize(rows, [r['id'] for r in schedule], bundle, rubric)
    assert summary['final_correctness_ready'] and not summary['semantic_judgments_pending']
    projected = project_complete_rows(rows, bundle, rubric)
    OUT.mkdir(exist_ok=False)
    write(OUT/'human-review-bound.json', bundle)
    write(OUT/'ADJUDICATED_SUMMARY.json', summary)
    engine_source = STAGE3/'predictions-amendment-20261114/run_analysis.py'
    engine = load('unchanged_frozen_analysis', engine_source)
    result = engine.analyze(projected, schedule, {r['id']: p.parent for r, p in zip(rows, paths)}, OUT,
                            scope='heldout', hosting_source_changes=(), fresh_controls_passed=True)
    write(OUT/'FROZEN_ENGINE_RESULTS.json', result)
    write(OUT/'ANALYSIS_SCOPE.json', dict(label='Qwen G1 held-out, lab hardware; not directly comparable to M4',
        P1_prime='Sol-specific original prediction; Qwen engine output is diagnostic only',
        P2='Unchanged native-operation ratio rule', P3='DROPPED',
        P4='NOT RUN; engine fallback is not evidence from a catalogue-size probe',
        P5='Unchanged source-hosting engineering controls, not a reliability claim',
        H_write='Not tested on Qwen: the rule was derived from this batch post hoc; counts reported descriptively only',
        engine_sha256=sha(engine_source), review_date_verbatim='2026/11/20', review_date_normalized='2026-11-20'))
    groups = {kind: {mode: sum(r['primary_pass'] for r in projected if r['mode'] == mode and r['case']['kind'] != 'ambiguous'
                               and (r['case']['kind'] in ('write', 'write_fault')) == (kind == 'write')) for mode in ('primitives', 'macro')}
              for kind in ('write', 'other')}
    pairs = {}
    for r in projected: pairs.setdefault(r['case']['case_id'], {})[r['mode']] = r['primary_pass']
    discordant = Counter('both_correct' if p['primitives'] and p['macro'] else 'primitive_only' if p['primitives'] else 'macro_only' if p['macro'] else 'neither' for p in pairs.values())
    write(OUT/'CLOSEOUT.json', dict(model='qwen3.5:9b', counts=summary['counts'], operational_views=result['operational_views'],
        matched_success_pairs=result['matched_success_pairs'], discordant_pairs=dict(discordant),
        write_bearing_counts_descriptive=groups, raw_engine_statuses=result['official_verdicts'],
        all_attempt_costs=summary['all_attempt_costs'],
        primary_outcomes_by_arm={m: dict(Counter(o['primary_status'] for o in summary['outcomes'] if by_id[o['trial_id']]['mode'] == m)) for m in ('primitives', 'macro')},
        new_model_requests=0))
    after = verifier.verify(require_seal=True); assert after['pass']
    assert all(sha(ROOT/n) == v for n, v in all_evidence.items())
    write(OUT/'INTEGRITY.json', dict(pass_=True, frozen_inputs_and_backend_seal='PASS', raw_evidence_files_unchanged=len(all_evidence),
                                     local_and_persisted_audits=76, model_requests=0))
    print(json.dumps(dict(counts=summary['counts'], discordant_pairs=dict(discordant), raw_engine_statuses=result['official_verdicts'])), flush=True)

if __name__ == '__main__': main()
