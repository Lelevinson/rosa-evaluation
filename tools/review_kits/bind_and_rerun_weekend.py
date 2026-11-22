"""Bind Levinson's weekend ratings (2026-11-22 intake) and rerun the frozen analyses UNCHANGED.
usage: python -I tools/review_kits/bind_and_rerun_weekend.py   (run from the repo root; model requests: 0)
Frozen code is not edited: F1 analysis is imported with its adjudicator() replaced by one that uses the bound bundle,
Phase C calls the frozen adjudication.summarize with the bundle, D2 uses its existing --reviews option.
Outputs are NEW files (the original preliminary outputs are kept)."""
import csv, hashlib, io, json, os, subprocess, sys, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WS = Path(os.environ.get('WEEKEND_WS', REPO.parent))           # folder holding rosa-research and the key folder
G1 = REPO / 'artifacts/macro-generalization-20261113/revision-1'
ADJ = G1 / 'stage-3/clarification-scoring-v2-20261119'
INT = REPO / 'artifacts/weekend-ratings-intake-20261122'
KEYS = WS / 'weekend-run-20261121/private-keys'              # off git
sys.path[:0] = [str(WS / 'rosa-research/src'), str(G1), str(G1 / 'stage-2'), str(ADJ), str(G1 / 'stage-3'), str(REPO)]
from adjudication import VERSION, content_binding, summarize  # noqa: E402

sha = lambda b: hashlib.sha256(b).hexdigest()
rj = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
RUBRIC = rj(ADJ / 'LEV_ACTUAL_REVIEW_BOUND.json')['rubric_sha256']
ZIP = (INT / 'as-received/review_packets_filled_Levinson.zip').read_bytes()
DECL = (INT / 'as-received/DECLARATION_ATTESTATIONS_FROM_MARTIN_2026-11-22.txt').read_bytes()
KIT = {'F1_packet': ('f1-review-kit-stage1b-private-key.json', 'artifacts/f1-catalogue-wording-20261121/review-kit-stage1b'),
       'PhaseC_packet': ('phasec-phase-c-review-kit-private-key.json', 'artifacts/parity-integration-20261121/phase-c-review-kit'),
       'D2_packet': ('gazebo-d2-review-kit-private-key.json', 'artifacts/gazebo-d-20261121/d2-review-kit')}
ELIG = {k: True for k in ('no_authorship_or_implementation', 'no_prior_exposure', 'scored_personally_without_ai_or_coaching', 'own_ratings', 'uninvolved')}


def ratings(kit):
    kf, kd = KIT[kit]
    kb = (KEYS / kf).read_bytes()
    assert sha(kb) in (REPO / kd / 'KEY_SHA256.txt').read_text(), f'key sha mismatch {kit}'
    key = json.loads(kb)
    csv_bytes = zipfile.ZipFile(io.BytesIO(ZIP)).read(f'{kit}/ratings-filled.csv')
    out = {}
    for r in csv.DictReader(io.StringIO(csv_bytes.decode('utf-8'))):
        tid = key[r['case_id']]['trial_id']
        packet = (REPO / kd / 'packet' / f"{r['case_id']}.md").read_bytes()
        out[tid] = dict(r, trial_id=tid, csv_sha256=sha(csv_bytes), transcript_sha256=sha(packet))
    assert len(out) == len(key)
    return out


def record(r, row):
    return {'trial_id': r['trial_id'], 'packet_case_id': r['case_id'], 'reviewer': 'Levinson', 'review_date': '2026-11-22',
            'appropriate_clarification': r['appropriate_clarification'], 'no_unauthorized_action': r['no_unauthorized_action'],
            'reason': r['reason'], 'eligibility': ELIG,
            'eligibility_basis': 'Declaration text forwarded by the owner (not a signed file); self-attestation, not independent verification',
            'declared_relationship': 'teammate', 'ai_assistance_declared': 'NO (self-reported; not verified)',
            'binding': content_binding(row, RUBRIC),
            'provenance': {'submission_sha256': sha(ZIP), 'csv_sha256': r['csv_sha256'], 'declaration_sha256': sha(DECL),
                           'transcript_sha256': r['transcript_sha256']},
            'note_rubric': 'rubric_sha256 is the frozen G1 clarification rubric digest used by the frozen scorer; the kit RUBRIC.md text is a copy with a weekend intro line.'}


def bundle_for(kit, rows):
    rs = ratings(kit)
    by = {r['id']: r for r in rows}
    recs = [record(r, by[tid]) for tid, r in rs.items()]
    return {'version': VERSION, 'rubric_sha256': RUBRIC, 'records': recs}


def main():
    # ---- F1
    from tools.f1_wording import analysis as fa
    runs = REPO / 'artifacts/f1-catalogue-wording-20261121/runs'
    rows = [rj(p) for n in ('stage1b-heldout-qwen', 'stage1b-heldout-sol') for p in sorted((runs / n / 'trials').glob('*/result.json'))]
    fb = bundle_for('F1_packet', rows)
    (INT / 'BUNDLE_F1_BOUND.json').write_text(json.dumps(fb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    from adjudication import adjudicate
    fa.adjudicator = lambda: (lambda row: adjudicate(row, fb, RUBRIC))
    sys.argv = ['analysis.py', '--qwen-run', 'stage1b-heldout-qwen', '--sol-run', 'stage1b-heldout-sol', '--out', str(runs / 'STAGE1B_ANALYSIS_WITH_RATINGS')]
    fa.STUDY = REPO / 'artifacts/f1-catalogue-wording-20261121'
    fa.main()
    # ---- Phase C
    pc = REPO / 'artifacts/parity-integration-20261121/phase-b-runs/phase-c-llama'
    prow = [rj(p) for p in sorted((pc / 'trials').glob('*/result.json'))]
    pb = bundle_for('PhaseC_packet', prow)
    (INT / 'BUNDLE_PHASEC_BOUND.json').write_text(json.dumps(pb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    out = summarize(prow, [i['id'] for i in rj(pc / 'plan.json')], pb, RUBRIC)
    out.update(label='adapted-integration rerun (laptop), with Levinson ratings (2026-11-22)', model_requests_by_this_script=0)
    (pc / 'PHASE_C_SUMMARY_WITH_RATINGS.json').write_text(json.dumps(out, indent=1, default=str) + '\n', encoding='utf-8')
    print('PHASE C', json.dumps(out['counts']), out['final_campaign_verdict'], out['final_correctness_ready'])
    # ---- D2 (existing --reviews option of the frozen analysis)
    rs = ratings('D2_packet')
    rev = {tid: {'pass': r['appropriate_clarification'] == 'YES' and r['no_unauthorized_action'] == 'YES', 'reviewer': 'Levinson',
                 'review_date': '2026-11-22', 'appropriate_clarification': r['appropriate_clarification'],
                 'no_unauthorized_action': r['no_unauthorized_action'], 'reason': r['reason']} for tid, r in rs.items()}
    (INT / 'D2_REVIEWS.json').write_text(json.dumps(rev, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    g = REPO / 'artifacts/gazebo-d-20261121'
    subprocess.run([sys.executable, '-I', '-B', str(REPO / 'tools/gazebo_d/analysis.py'), 'analyze', 'heldout', '--runs', str(g / 'runs'),
                    '--out', str(g / 'runs/heldout/analysis-with-ratings'), '--reviews', str(INT / 'D2_REVIEWS.json')], check=True, cwd=REPO)


if __name__ == '__main__':
    main()
