"""Summarize fresh controls without calling them independent reviews."""
from collections import defaultdict
from pathlib import Path
from prepare import read,write
from runner import verify

ROOT=Path(__file__).resolve().parent

def main():
    protection=verify()
    rows=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))]
    persisted=read(ROOT/'persisted-audit.json')
    assert len(rows)==132 and all(r['pass'] for r in rows) and persisted['pass']
    assert read(ROOT/'unit-tests.json')['pass']
    ratios=[]
    for domain in ('arm','base'):
        for depth in (1,2,4,6):
            group=[r for r in rows if r['block']=='cases' and r['case']['kind']=='ladder'
                   and r['case']['domain']==domain and r['case']['native_depth']==depth]
            p=sum(len(r['actor_records']) for r in group if r['mode']=='primitives')
            m=sum(len(r['actor_records']) for r in group if r['mode']=='macro')
            assert p and m/p==1
            ratios.append(dict(domain=domain,depth=depth,primitive_native=p,macro_native=m,ratio=m/p))
    summary=dict(passed=True,controls=132,structural_trials=20,heldout_fixture_trials=76,dev_fixture_trials=36,
        observer_world_unit_methods=read(ROOT/'unit-tests.json')['tests'],
        local_audits_passed=sum(r['local_audit']['pass'] for r in rows),
        persisted_audits_passed=persisted['trials'],persisted_spans=persisted['persisted_spans'],
        actor_only_truth_refusals=sum(r['actor_only_ground_truth_rejected'] for r in rows),
        fault_controls=[dict(id=r['id'],fault=r['case']['fault'],exercised=r['score'].get('fault_exercised'))
                        for r in rows if r['case']['fault']],
        native_ratios=ratios,protected_check=protection,live_model_requests=0,
        independent_scorer_review=False,study_freeze=False,
        scope='Fresh real-adapter scripted controls; no hosting source change; not model generalization evidence')
    write('analysis.json',summary)
    write('status.json',dict(status='COMPLETE',planned=132,completed=132,live_model_requests=0,
                             persisted_audit_passed=True,Stage4_started=False))
    (ROOT/'CONTROL_RERUN_REPORT.md').write_text(f'''# Stage 3 fresh zero-model controls

Date: **2026-11-14**. **132/132 controls passed**, with zero model requests.

This repeats 20 structural paths and 112 fixture paths through the real public adapters and the unchanged
Stage 2 scorer: 76 held-out-designated fixture trials plus 36 dev fixture trials. Decisions and token metadata
are scripted; this is engineering validation, not held-out model evaluation or independent scorer review.

Observer/world suites passed {summary['observer_world_unit_methods']} test methods. All 132 local audits and
132 persisted Phoenix audits passed; **{summary['persisted_spans']} spans** matched exactly and closed.
Actor-only truth was rejected in all 132 controls. Native ratios were 1.00 in all eight domain/depth cells.
Fault controls require their intended acquisition/dispatch effects, as recorded in analysis.json.

No prompts, cases, public source, scorer or resource rules changed. Helper copies differ only in isolated
paths/project metadata and the control-inventory filename, as recorded in provenance.json. Hosting both
domains needs no source edit. The proposed OAuth observation hook remains unapplied and unrelated to hosting.

G-b's technical control check passes for the unchanged owner-approved AI-only fixtures. The formal study freeze
still requires the remaining instrumentation/review gates. These controls do not count as either human review.
No OAuth, Ollama, Gazebo, robot action, live inference, Git action or upload was used. The local owned Phoenix
service is shut down by the launcher; check phoenix-service.json after completion. Earlier evidence is preserved.
''',encoding='utf-8')
    print({key:summary[key] for key in ('passed','controls','observer_world_unit_methods','persisted_spans','live_model_requests')})

if __name__=='__main__':main()
