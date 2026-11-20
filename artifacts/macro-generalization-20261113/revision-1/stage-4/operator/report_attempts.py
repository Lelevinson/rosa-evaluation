"""Create a clearly provisional evidence report from approved adjudication only."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from statistics import mean,median
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from common import read,WORKSPACE
from runtime_support import empty_bundle
from adjudication import summarize

def main():
    state=read(ROOT/'status.json')
    manager=read(HERE/'recovery-manager/status.json') if (HERE/'recovery-manager/status.json').exists() else {}
    if state['status']=='RUNNING' or manager.get('status')=='CONTINUING_UNSTARTED':
        raise SystemExit('Wait for a terminal checkpoint before packaging a report')
    output=HERE/'reports'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output.mkdir(parents=True,exist_ok=False)
    paths=sorted((ROOT/'trials').glob('*/result.json'))
    rows=[read(p) for p in paths]
    schedule=read(ROOT/'plan.json')
    bundle=empty_bundle()
    result=summarize(rows,[x['id'] for x in schedule],bundle,bundle['rubric_sha256'])
    result['report_scope']='Provisional actual attempts; no invented human judgments or unstarted outcomes'
    outcomes={x['trial_id']:x for x in result['outcomes']}
    local=sum(read(p)['local_audit']['pass'] for p in paths)
    persisted=sum(read(p.parent/'phoenix-audit.json')['pass'] for p in paths)
    bymode={}
    for mode in ('primitives','macro'):
        subset=[r for r in rows if r['mode']==mode]
        known=[r for r in subset if r['case']['kind']!='ambiguous' and outcomes[r['id']]['censor_class']=='EVALUABLE']
        durations=[r['task_seconds'] for r in subset]
        bymode[mode]={'scheduled':38,'retained':len(subset),'known_goal_correct':sum(outcomes[r['id']]['primary_correct'] is True for r in known),
            'known_goal_evaluable':len(known),'pending_semantics':sum(outcomes[r['id']]['semantic_correct']=='PENDING_HUMAN_REVIEW' for r in subset),
            'censored':sum(outcomes[r['id']]['censor_class']!='EVALUABLE' for r in subset),
            **result['all_attempt_costs'][mode],
            'mean_task_seconds':mean(durations) if durations else None,'median_task_seconds':median(durations) if durations else None}
    pairs=defaultdict(dict)
    for row in rows:pairs[row['case']['case_id']][row['mode']]=row
    matched=[p for p in pairs.values() if set(p)=={'primitives','macro'} and all(outcomes[r['id']]['primary_status']=='PASS' for r in p.values())]
    matched_cost={m:dict(calls=sum(p[m]['inference']['calls'] for p in matched),
        native_operations=sum(len(p[m]['actor_records']) for p in matched),
        task_seconds=sum(p[m]['task_seconds'] for p in matched)) for m in ('primitives','macro')}
    freeze=read(ROOT/'freeze.json')
    mismatch=[n for n,d in freeze['files_sha256'].items() if hashlib.sha256((WORKSPACE/n).read_bytes()).hexdigest()!=d]
    assert not mismatch
    result.update(by_mode=bymode,matched_success_pairs=len(matched),matched_success_costs=matched_cost,
        local_audits_passed=local,persisted_audits_passed=persisted,source_mismatches=mismatch,
        manager_status=manager,backend_operationally_compromised=sum(outcomes[r['id']]['censor_class']!='EVALUABLE' for r in rows)>=8)
    (output/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines=['# G1 Sol held-out actual-attempt report','', 'Date: **2026-11-19**. **Provisional; pending human review and/or unstarted trials.**','',
        f"Retained **{len(rows)}/76** scheduled trials; **{state['live_model_requests']}/611** charged requests. No task was replayed or replaced.",
        f"Effective states: {json.dumps(result['counts'])}. Unstarted: **{result['unstarted']}**.",'',
        f"Local audits **{local}/{len(rows)}**; persisted Phoenix audits **{persisted}/{len(rows)}**. Frozen source mismatches: **0**.",'',
        '| Metric | Primitives | Macro |','|---|---:|---:|']
    specs=[('Retained / scheduled','retained'),('Known-goal evaluable correct','known_goal_correct'),('Known-goal evaluable denominator','known_goal_evaluable'),
        ('Pending semantic judgments','pending_semantics'),('Infrastructure censored','censored'),('Physical model calls','calls'),
        ('Known input tokens','input_tokens'),('Known output tokens','output_tokens'),('Incomplete-usage records','usage_incomplete'),
        ('Native operations','native_operations'),('Task seconds, sum','task_seconds'),('Task seconds, mean','mean_task_seconds'),('Task seconds, median','median_task_seconds')]
    for label,key in specs:
        values=[bymode[m][key] for m in ('primitives','macro')]
        rendered=[f'{v:.3f}' if isinstance(v,float) else str(v) for v in values]
        lines.append(f'| {label} | {rendered[0]} | {rendered[1]} |')
    lines+=['',f"Matched-success pairs: **{len(matched)}**. Costs: `{json.dumps(matched_cost)}`.",'',
        'All-attempt costs include failed/censored work. Partial or unbalanced arms are not a fair complete-arm efficiency comparison. Unknown usage is not estimated. Task latency excludes interruption pauses and campaign setup; the cumulative deadline includes pauses. Call count alone is not whole-system efficiency.','',
        'Original in-stream errors have no recorded original provider code/type. Their cause is unknown. They are not called quota exhaustion or model selection failures. Their affected pairs are excluded from matched-success costs; sensitivity counting censored attempts as failures remains required in final analysis.','',
        'All cases are AI-authored. This is the original fixed G1 catalogue and condition wording; no independence/generalization or original-ROSA superiority claim is made. Qwen/catalogue stages are unstarted. New ambiguous outcomes require their own blinded human review; old dev ratings are not reused.','',
        'If the frozen eight-censored threshold is reached, this backend is operationally compromised and prediction conclusions are Uninformative. Remaining unstarted outcomes are unknown. Full final conclusions remain withheld while required human judgments are absent.','',
        '| Trial | Mode | Domain | Kind | Effective status | Calls | Native |','|---|---|---|---|---|---:|---:|']
    for r in rows:
        lines.append(f"| {r['id']} | {r['mode']} | {r['case']['domain']} | {r['case']['kind']} | {outcomes[r['id']]['primary_status']} | {r['inference']['calls']} | {len(r['actor_records'])} |")
    (output/'G1_SOL_ACTUAL_ATTEMPT_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(output/'G1_SOL_ACTUAL_ATTEMPT_REPORT.md'),'retained':len(rows),'requests':state['live_model_requests'],'counts':result['counts'],'source_mismatches':0}))

if __name__=='__main__':main()
