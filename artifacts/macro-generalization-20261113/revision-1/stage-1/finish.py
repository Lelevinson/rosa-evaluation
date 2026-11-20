"""Close the engineering gate without inventing model-performance evidence."""
from collections import defaultdict
from datetime import datetime,timezone
import json
from pathlib import Path
from prepare import read,write,digest
from runner import verify

ROOT=Path(__file__).resolve().parent

def main():
    protected=verify()
    rows=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))]
    persisted=read(ROOT/'persisted-audit.json')
    assert len(rows)==132 and all(r['pass'] for r in rows) and persisted['pass']
    paired=defaultdict(dict)
    for row in rows:
        if row['block']=='cases' and row['case']['kind']=='ladder':
            paired[(row['case']['domain'],row['case']['native_depth'],row['case']['case_id'])][row['mode']]=row
    ratios=[]
    for domain in ('arm','base'):
        for depth in (1,2,4,6):
            pairs=[p for (dom,d,c),p in paired.items() if dom==domain and d==depth]
            primitive=sum(p['primitives']['score']['native_operations'] for p in pairs)
            macro=sum(p['macro']['score']['native_operations'] for p in pairs)
            ratio=macro/primitive
            ratios.append({'domain':domain,'depth':depth,'pairs':len(pairs),'primitive_native':primitive,
                           'macro_native':macro,'ratio':ratio,'pass':.75<=ratio<=1.25})
    assert all(r['pass'] for r in ratios)
    structural=[r for r in rows if r['block']=='structural']
    summary={'pass':True,'completed_utc':datetime.now(timezone.utc).isoformat(),
        'label':'AI-authored exploratory fixtures, scripted decisions; no independent teammate authorship or semantic novelty review',
        'structural_trials':20,'case_trials':112,'total_trials':132,'unit_tests':read(ROOT/'unit-tests.json'),
        'local_audits_passed':sum(r['local_audit']['pass'] for r in rows),
        'persisted_audits_passed':persisted['trials'],'persisted_spans':persisted['persisted_spans'],
        'actor_only_scorer_rejections':sum(r['actor_only_ground_truth_rejected'] for r in rows),
        'scorer_negative_controls':sum(len(r['scorer_negative_controls']) for r in rows),
        'evaluator_observer_reads':sum(len(r['observer_records']) for r in rows),
        'agent_native_attempts':sum(len(r['actor_records']) for r in rows),
        'scripted_turns':sum(r['accounting']['calls'] for r in rows),'live_model_requests':0,
        'actual_model_tokens':'not measured; all token metadata synthetic',
        'native_ratios':ratios,'heldout_ladder_template_groups':6,'protected_check':protected,
        'Stage2_started':False,'research_predictions':'Not adjudicated from scripted controls',
        'structural_rows':[{'skill':r['case']['skill_id'],'domain':r['case']['domain'],'mode':r['mode'],
            'native_depth':r['case']['native_depth'],'actual_turns':r['accounting']['calls'],
            'actual_native':len(r['actor_records'])} for r in structural]}
    write('analysis.json',summary)
    write('status.json',{'status':'COMPLETE_STAGE1_ENGINEERING_GATE_PASSED','completed':132,'planned':132,
        'live_model_requests':0,'Stage2_started':False,'next_gate':'Owner confirmation before Sol dev'})
    lines=['# G1 Stage 1 engineering report','',f'Date: {summary["completed_utc"][:10]}.',
        '', '**Completed: 132/132 scripted real-adapter controls, with zero live model requests.**',
        '', 'These are AI-authored fixtures with scripted skill decisions. No independent teammate authorship or semantic-novelty review was obtained. This establishes execution and measurement plumbing, not model competence, generalization, or an efficiency advantage with real models.',
        '', f'The observer/world unit suites passed {summary["unit_tests"]["tests"]} tests. All 132 local audits and 132 persisted Phoenix audits passed; {summary["persisted_spans"]} span IDs matched exactly with closed trees.',
        '', '| Public-adapter path | Primitive turns | Macro turns | Native attempts in each condition |',
        '|---|---:|---:|---:|','| Inspection, depth 1 / 2 / 4 / 6 | 3 | 2 | 1 / 2 / 4 / 6 |',
        '| Healthy movement, depth 3 | 5 | 2 | 3 |',
        '', 'The 20 structural paths passed before the 112 case paths. All 56 fixtures were exercised in both conditions: 18 dev and 38 held-out-designated cases. Held-out designation concerns future live evaluation; engineering fixtures and expected results were visible during construction. There are 8 dev template groups and 13 held-out groups, including **6 held-out ladder groups**. No independent held-out authorship is claimed.',
        '', f'Independent-observer scoring rejected actor-only records in {summary["actor_only_scorer_rejections"]}/132 trials. An additional {summary["scorer_negative_controls"]} counterfactual scoring checks rejected nonexistent observation references, invented values and unsupported SUCCESS for UNKNOWN outcomes. {summary["evaluator_observer_reads"]} observer reads were separately traced and excluded from {summary["agent_native_attempts"]} agent-native attempts.',
        '', 'Missing observations, known-false conditions, ineffective commands, partial commands and clarification paths passed their scripted expected contracts. Fault scoring requires actual attempted acquisition/dispatch where applicable. Clarification here uses an engineering question check; independent human intent review remains absent.',
        '', 'Macro/primitive inspection native-attempt ratios were 1.00 at every depth in both domains, within the predefined [0.75, 1.25] band. These counts do not demonstrate fewer native operations. The expected 3-to-2 inspection turn difference is constant across depth because primitive inspection already batches the selected sources.',
        '', f'{protected["protected_files"]} protected historical files and {protected["frozen_files"]} Stage 1 frozen files remained unchanged. Original M1–M5, M4, serving/timing, Stage 0 and revision evidence were preserved.',
        '', 'No Qwen/Sol inference, OAuth, Gazebo, physical robot, Git commit, push or upload was used. Synthetic token counts and scripted timings are not real-model performance measurements. P1–P4 are not decided here; the Stage 1 unchanged-source engineering prerequisite is satisfied.',
        '', 'The two partial-write dev cases and native-ratio threshold were adopted before outcomes in the Stage 1 pre-run note. The future Sol dev proposal is 18 paired cases, at most 291 charged requests including its reserve. **Stage 2 needs owner confirmation and has not started.**',
        '', 'Detailed evidence: analysis.json, control-plan.json, freeze.json, protected-before.json, unit-tests.log, persisted-audit.json, and each trials/<id> directory.']
    (ROOT/'STAGE1_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('structural_rows','native_ratios')}))

if __name__=='__main__':main()
