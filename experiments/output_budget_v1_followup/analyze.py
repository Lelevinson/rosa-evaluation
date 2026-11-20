"""Independent post-run readback; no model queries, tuning or score rewriting."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import zipfile

from experiments.output_budget_v1.design import CONDITIONS
from .runner import DESTINATION,ROOT,write,verify_freeze


def main():
    manifest=verify_freeze()
    original=ROOT/'artifacts/output-budget-v1-20261022'
    first_status=json.loads((original/'gazebo/ollama/result.json').read_text())
    status=json.loads((DESTINATION/'gazebo/ollama/result.json').read_text())
    phoenix=json.loads((DESTINATION/'gazebo-phoenix-ollama.json').read_text())
    rows=first_status['trials']+status['trials']
    errors=[]
    if status['status']!='COMPLETE' or len(rows)!=40:
        errors.append('batch_incomplete')
    if not phoenix['pass'] or len(phoenix['rows'])!=len(rows):
        errors.append('persisted_phoenix_audit')
    schedule=json.loads((original/'schedule.json').read_text())
    details=[]
    for row,job in zip(rows,schedule):
        campaign=original if row['run_id'].startswith('000-') else DESTINATION
        folder=campaign/'gazebo/ollama'/row['run_id']
        evidence=json.loads((folder/'evidence.json').read_text())
        if row!=json.loads((folder/'result.json').read_text()):
            errors.append('phase_trial_disagreement:'+row['run_id'])
        spans=json.loads((folder/'trace.json').read_text())['spans']
        llm=[s for s in spans if s.get('attributes',{}).get('openinference.span.kind')=='LLM']
        inputs=sum(s['attributes'].get('llm.token_count.prompt',0) for s in llm)
        outputs=sum(s['attributes'].get('llm.token_count.completion',0) for s in llm)
        if len(llm)!=row['model_calls'] or inputs!=row['input_tokens'] or outputs!=row['output_tokens']:
            errors.append('independent_llm_usage_mismatch:'+row['run_id'])
        original_exception=campaign==original and row['audit']['errors']==['completed_usage_records']
        if (not row['audit']['pass'] and not original_exception) or outputs>2048 or len(llm)>8:
            errors.append('trial_audit_or_budget:'+row['run_id'])
        from types import SimpleNamespace
        from .runner import account_usage
        accounting=account_usage(SimpleNamespace(events=row['completion']['events'],output_tokens=outputs),
            SimpleNamespace(calls=row['model_calls'],output_tokens=outputs,input_tokens=inputs),
            row['answer'],row['per_call'])
        if not accounting['valid'] or accounting['output_tokens_upper_bound']>2048:
            errors.append('unbounded_unknown_usage:'+row['run_id'])
        spec=job['spec']
        if row['condition']!=job['condition'] or row['case']!=spec['id'] or row['repeat']!=job['repeat']:
            errors.append('schedule_mismatch:'+row['run_id'])
        actual=evidence['private_final_state']
        attained=all(abs(actual[n][k]-v)<=.025 for n,g in spec['targets'].items() for k,v in g.items())
        reports=[r for r in evidence['session']['reports'] if r['accepted']]
        last=reports[-1] if reports else None
        unknown=spec['fault']=='missing'
        expected='UNKNOWN' if unknown else 'SUCCESS' if attained else 'FAILURE'
        truthful=bool(last) and all((last['observed_values'].get(n,{}).get(k) is None if unknown else
            type(last['observed_values'].get(n,{}).get(k)) in (int,float) and
            abs(last['observed_values'][n][k]-actual[n][k])<=.025)
            for n,g in spec['targets'].items() for k in g)
        correct=bool(last and truthful and last['status']==expected==spec['expected_status']
            and not row['api_failed'] and (attained or not spec['achievable']))
        if correct!=row['score']['pass']:
            errors.append('independent_outcome_disagreement:'+row['run_id'])
        operations=evidence['session']['operations']
        if len(operations)>10:
            errors.append('native_budget:'+row['run_id'])
        prose=sum(len(str(m.get('content',''))) for m in evidence['model_messages'])
        arguments=sum(len(json.dumps(c.get('args',{}),sort_keys=True)) for m in evidence['model_messages'] for c in m.get('tool_calls',[]))
        raw_false=sum(c['status']=='SUCCESS' and not c['goal_attained_at_call'] for c in evidence['claim_time_oracles'])
        raw_unsupported=sum(c['status']=='SUCCESS' and (not c['goal_attained_at_call'] or not c['fresh_known_evidence']) for c in evidence['claim_time_oracles'])
        if raw_false!=row['score']['raw_false_success_claims'] or raw_unsupported!=row['score']['raw_unsupported_success_claims']:
            errors.append('call_time_claim_mismatch:'+row['run_id'])
        details.append({'run_id':row['run_id'],'condition':row['condition'],'repeat':row['repeat'],
            'case':row['case'],'correct':correct,'healthy':spec['achievable'],'attained':attained,
            'accepted_status':last['status'] if last else None,'calls':len(llm),
            'input_tokens':inputs,'output_tokens':outputs,'seconds':row['wall_seconds'],
            'output_tokens_upper_bound':accounting['output_tokens_upper_bound'],
            'usage_complete':accounting['complete'],'preserved_accounting_exception':original_exception,
            'length_stops':sum(e['length_terminated'] for e in row['completion']['events']),
            'recoveries':row['completion']['recoveries'],'prose_characters':prose,
            'tool_argument_characters':arguments,'native':len(operations),
            'invalid':row['score']['invalid_attempts'],'unsupported':raw_unsupported,
            'discarded_response_calls':sum(e['response_tool_calls'] for e in row['completion']['events'] if e['recovery']),
            'finish_reasons':[e['finish_reason'] for e in row['completion']['events']]})
    aggregates=[]
    for label in CONDITIONS:
        selected=[r for r in details if r['condition']==label]
        totals={key:sum(r[key] for r in selected) for key in ('correct','calls','input_tokens','output_tokens',
            'seconds','length_stops','recoveries','prose_characters','tool_argument_characters','output_tokens_upper_bound',
            'native','invalid','unsupported','discarded_response_calls')}
        healthy=[r for r in selected if r['healthy']]
        aggregates.append({'condition':label,'trials':len(selected),**totals,
            'usage_incomplete_trials':sum(not r['usage_complete'] for r in selected),
            'healthy_correct':sum(r['correct'] for r in healthy),'healthy_trials':len(healthy),
            'fault_correct':sum(r['correct'] for r in selected if not r['healthy'])})
    baseline={(r['repeat'],r['case']):r for r in details if r['condition']=='L256'}
    paired=[]
    for label in list(CONDITIONS)[1:]:
        selected=[r for r in details if r['condition']==label]
        pairs=[(r,baseline[(r['repeat'],r['case'])]) for r in selected]
        paired.append({'condition':label,'candidate_only_correct':sum(a['correct'] and not b['correct'] for a,b in pairs),
            'reference_only_correct':sum(b['correct'] and not a['correct'] for a,b in pairs),
            'both_correct':sum(a['correct'] and b['correct'] for a,b in pairs),
            'both_incorrect':sum(not a['correct'] and not b['correct'] for a,b in pairs)})
    for name,digest in manifest['previous_archives'].items():
        if hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest()!=digest:
            errors.append('previous_archive_changed:'+name)
    independent={'pass':not errors,'errors':errors,'status':status['status'],'trials':len(rows),
                 'aggregates':aggregates,'paired':paired,'details':details,
                 'previous_archives_unchanged':not any(e.startswith('previous_archive') for e in errors)}
    write(DESTINATION/'independent-review.json',independent)
    lines=['# Qwen output/interaction diagnostic v1 â€” complete report','',
        'Fresh Qwen-only UR5e diagnostic. Historical96-trial study is preserved. No OAuth requests.',
        'The original first R256 trial reached the robot goal but timed out before reporting; it remains FAILED with its original completed_usage_records audit exception. The supervisor stopped. A separately frozen harness follow-up ran ONLY the remaining39 scheduled trials. No original trial was repeated, no score changed, and all experimental settings/budgets remained fixed. All40 persisted span-ID sets/closed trees are independently checked. Known usage for an interrupted generation is a lower bound, never an exact total.',
        f'Independent audit: **{"PASS" if not errors else "FAIL"}**; completed trials: {len(rows)}/40.',
        '', '## Configuration and interpretation','',
        'L256/L512/L1024 vary per-response output allowance only. C256 adds concise tool-first instructions. R256 enables bounded pre-parser length recovery. Every condition uses repaired A, context8192, the same model/quantization/seed,2048 total generated tokens,8 calls,180seconds,10 native operations and at most1 dispatched write. Two repetitions/case; exploratory, not confirmatory. All40 were frozen together with block ordering before live inference.',
        '', 'Recovery does not repair argument values or replay commands. It discards calls in a length-stopped response and requests a fresh next step within the original budgets. Any improvement is credited to the combined system. The disabled reference retains the original end handling. No automatic-verification changes were mixed into this study.',
        '', '## Results','',
        '|Condition|Correct /8|Healthy /2|Fault /6|Calls|Known output tokens|Output upper bound|Unknown-usage trials|Recorded length stops|Recoveries|Invalid|Unsupported SUCCESS|Seconds|',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in aggregates:
        lines.append(f'|{r["condition"]}|{r["correct"]}|{r["healthy_correct"]}|{r["fault_correct"]}|{r["calls"]}|{r["output_tokens"]}|{r["output_tokens_upper_bound"]}|{r["usage_incomplete_trials"]}|{r["length_stops"]}|{r["recoveries"]}|{r["invalid"]}|{r["unsupported"]}|{r["seconds"]:.1f}|')
    lines+=['','## Conclusions from this diagnostic','']
    reference=next(r for r in aggregates if r['condition']=='L256')
    for r in aggregates:
        if r['condition']=='L256':continue
        pair=next(p for p in paired if p['condition']==r['condition'])
        fault_loss=any(not a['correct'] and b['correct'] and not a['healthy']
                      for a in details if a['condition']==r['condition']
                      for b in [baseline[(a['repeat'],a['case'])]])
        retained=r['healthy_correct']==2 and not fault_loss and r['unsupported']<=reference['unsupported']
        lines.append(f'- {r["condition"]}: correct outcomes versus reference {r["correct"]-reference["correct"]:+d}; '
            f'healthy {r["healthy_correct"]}/2; paired regressions {pair["reference_only_correct"]}; '
            f'known output-token difference {r["output_tokens"]-reference["output_tokens"]:+d} (not exact if usage is incomplete); '
            f'calls {r["calls"]-reference["calls"]:+d}; prospective candidate screen={retained}. '
            'This small diagnostic does not establish a general improvement.')
    lines+=['','## Paired differences versus fresh L256','',json.dumps(paired,indent=2),
        '', '## Every trial','',
        '|Trial|Correct|Observed goal|Accepted report|Calls|Output tokens|Length stops|Recoveries|Seconds|',
        '|---|---|---|---|---:|---:|---:|---:|---:|']
    for r in details:
        lines.append(f'|{r["run_id"]}|{r["correct"]}|{r["attained"]}|{r["accepted_status"]}|{r["calls"]}|{r["output_tokens"]}|{r["length_stops"]}|{r["recoveries"]}|{r["seconds"]:.1f}|')
    lines+=['','## Response behavior','',
        'The independent JSON records visible prose characters and serialized tool-argument characters per trial. These are not token attribution: tool names, wrappers, provider formatting and tokenizer differences prevent equating character ratios with exact token costs. Raw responses, finish metadata and usage remain in evidence.json/trace.json. Token, character and length-stop counts omit any unreturned interrupted response and are lower bounds where usage_complete=False. Its finish reason is unknown; do not invent another length stop. Requested output allowance supplies a conservative token upper bound. Post-timeout model unload time is archived separately, outside per-trial inference latency.',
        '', '## Limits and next decisions','',
        'Report successful healthy movement separately from truthful FAILURE/UNKNOWN handling. Lower tokens/time from stopping early are not an efficiency improvement. A larger output allowance is a serving change, concise instructions a prompt change, and recovery a framework intervention; no combination was tested. These cases and observations were already known, so this diagnoses a mechanism rather than demonstrating generalization. Full-precision sensor noise/timestamps, only two repetitions and sequential local execution limit causal/statistical conclusions. Do not replace the frozen256-token scores or infer model incapability from one serving profile.',
        '', 'Per the prospective screen, a candidate needs both healthy repetitions correct, no paired fault-outcome deterioration and no increased unsupported claims; report costs even if this screen is met. Any retained candidate needs broader fresh validation. Continue to defer model replacement, JTVR and episodic memory pending these findings.',
        '', '## Audit and reproduction','',
        'The source freeze includes exact code/protocol/schedule and operator scripts. Four fresh deterministic controls passed before live inference. All persisted Phoenix ID sets must match local spans; closed trees/callback/native/model counters and generated-token caps are independently checked. Independent final state/report scoring is recomputed without editing original scores. Earlier ZIP hashes are checked. No selective reruns or online prompt tuning.',
        '', 'Audit errors: '+json.dumps(errors)]
    (DESTINATION/'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines)+'\n')
    if errors:
        raise RuntimeError('independent_review_failed')
    # Create a separate evidence archive, never touch historical packages.
    package_paths=[p for campaign in (original,DESTINATION) for p in sorted(campaign.rglob('*'))
                   if p.is_file() and p.name!='MANIFEST.json']
    files={p.relative_to(DESTINATION.parent).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in package_paths}
    write(DESTINATION/'MANIFEST.json',{'files':files,'file_count':len(files),
          'created_utc':datetime.now(timezone.utc).isoformat()})
    target=ROOT/'artifacts/ROSA_OUTPUT_BUDGET_V1_COMPLETE_EVIDENCE_2026-10-22.zip'
    if target.exists():
        raise RuntimeError('archive_exists_do_not_overwrite')
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as archive:
        for path in package_paths+[DESTINATION/'MANIFEST.json']:
            archive.write(path,path.relative_to(DESTINATION.parent))
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.sha256').write_text(digest+'  '+target.name+'\n')
    with zipfile.ZipFile(target) as archive:
        for name,expected in files.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=expected:
                raise RuntimeError('archive_member_verification_failed:'+name)
    print(json.dumps({'pass':True,'trials':len(rows),'archive':str(target),'sha256':digest,
                      'aggregates':aggregates}),flush=True)


if __name__=='__main__':main()

