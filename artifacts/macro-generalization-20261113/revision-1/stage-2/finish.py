"""Descriptive dev closeout, including stopped attempts. Never decides P1-P4."""
from collections import defaultdict
from statistics import mean,median
from common import ROOT,read,write,verify

def costs(rows):
    times=[r['task_seconds'] for r in rows if 'task_seconds' in r]
    return {'trials':len(rows),'primary_passes':sum(r.get('primary_pass',False) for r in rows),
        'completion_including_recovery':sum(r.get('completion_including_recovery',False) for r in rows),
        'physical_requests':sum(r.get('inference',{}).get('calls',0) for r in rows),
        'logical_decisions':sum(r.get('inference',{}).get('decision_calls',0) for r in rows),
        'known_input_tokens':sum(r.get('inference',{}).get('known_input_tokens',0) for r in rows),
        'known_output_tokens':sum(r.get('inference',{}).get('known_output_tokens',0) for r in rows),
        'usage_incomplete_trials':sum(not r.get('inference',{}).get('usage_complete',False) for r in rows),
        'native_attempts':sum(len(r.get('actor_records',[])) for r in rows),
        'tool_attempts':sum(r.get('snapshot',{}).get('tool_calls',0) for r in rows),
        'invalid_attempts':sum(r.get('snapshot',{}).get('validation_errors',0) for r in rows),
        'task_seconds_sum':sum(times),'task_seconds_mean':mean(times) if times else None,
        'task_seconds_median':median(times) if times else None,'task_time_unrecorded':len(rows)-len(times),
        'budget_endings':sum(r.get('score',{}).get('budget_exhaustion',False) for r in rows),
        'length_endings':sum(r.get('score',{}).get('length_stop',False) for r in rows)}

def main():
    state=read(ROOT/'status.json')
    rows=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))] if (ROOT/'trials').exists() else []
    pairs=defaultdict(dict)
    for row in rows:pairs[row['case']['case_id']][row['mode']]=row
    both={name for name,pair in pairs.items() if len(pair)==2 and all(r.get('primary_pass',False) for r in pair.values())}
    by_mode={mode:costs([r for r in rows if r['mode']==mode]) for mode in ('primitives','macro')}
    matched={mode:costs([r for r in rows if r['mode']==mode and r['case']['case_id'] in both])
             for mode in ('primitives','macro')}
    discordant={}
    for domain in ('arm','base'):
        values={'both_pass':0,'primitive_only':0,'macro_only':0,'neither':0,'incomplete_pairs':0}
        for pair in pairs.values():
            if next(iter(pair.values()))['case']['domain']!=domain:continue
            if len(pair)!=2:values['incomplete_pairs']+=1;continue
            p=pair['primitives'].get('primary_pass',False);m=pair['macro'].get('primary_pass',False)
            values['both_pass' if p and m else 'primitive_only' if p else 'macro_only' if m else 'neither']+=1
        discordant[domain]=values
    ratios=[]
    for domain in ('arm','base'):
        for depth in (1,2,4,6):
            group=[r for r in rows if r['case']['kind']=='ladder' and r['case']['domain']==domain and r['case']['native_depth']==depth]
            primitives=sum(len(r['actor_records']) for r in group if r['mode']=='primitives')
            macros=sum(len(r['actor_records']) for r in group if r['mode']=='macro')
            ratio=macros/primitives if primitives else None
            ratios.append({'domain':domain,'depth':depth,'primitive_native':primitives,'macro_native':macros,
                'ratio':ratio,'in_band':.75<=ratio<=1.25 if ratio is not None else None})
    persisted=[r.get('phoenix_audit',{}) for r in rows]
    complete=state['status']=='COMPLETE' and len(rows)==36
    summary={'stage':'G1 Sol dev','execution_complete':complete,'planned_trials':36,'retained_trials':len(rows),
        'checkpoint_completed':state['completed'],'all_attempts':by_mode,'matched_primary_success':matched,
        'paired_by_domain':discordant,'native_ratios':ratios,'campaign':state.get('campaign',{}),
        'local_audits_passed':sum(r.get('local_audit',{}).get('pass',False) for r in rows),
        'persisted_audits_passed':sum(r.get('pass',False) for r in persisted),
        'persisted_spans':sum(r.get('persisted_spans',0) for r in persisted),
        'turn_expectation_deviations':[{'id':r['id'],'actual':r.get('actual_turns'),'expected':r['expected_scripted_turns']}
            for r in rows if not r.get('turns_match_scripted_expectation',False)],
        'scorer_cycles_used':1,'P1_P4_verdict':'NOT_ADJUDICATED_DEV_ONLY','later_stages_started':False,
        'independent_teammate_authorship':False,'clarification_human_review':'NOT_OBTAINED',
        'scope':'AI-authored exploratory dev; no inferential model-performance claims',
        'protected_check':verify()}
    write('analysis.json',summary)
    lines=['# G1 Stage 2 Sol dev report','','Date: **2026-11-14**.',
        '',f'**Execution: {"complete" if complete else "stopped/incomplete"}; {len(rows)}/36 trial records retained.**',
        '', 'This is an AI-authored exploratory engineering/dev run, without independent teammate authorship or semantic-novelty review. It checks the scorer, budget and live execution paths. **P1-P4 are not adjudicated.** No Qwen or later stage was launched.',
        '', 'The restore-only authorization preflight passed after actual provider renewal, unchanged-scope validation and an authenticated Sol catalogue check, using zero inference requests. Provider inference quota remained unknown. The batch rechecked the existing grant at launch; no consent/login fallback was available.',
        '', '| Condition | Primary correct | Physical model attempts | Known input tokens | Known output tokens | Native attempts | Task time total (s) | Mean / median (s) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode,c in by_mode.items():
        average=f'{c["task_seconds_mean"]:.2f} / {c["task_seconds_median"]:.2f}' if c['task_seconds_mean'] is not None else 'not recorded'
        lines.append(f'| {mode} | {c["primary_passes"]}/{c["trials"]} | {c["physical_requests"]} | {c["known_input_tokens"]} | {c["known_output_tokens"]} | {c["native_attempts"]} | {c["task_seconds_sum"]:.2f} | {average} |')
    lines += ['', 'Primary correctness excludes infrastructure-recovered trials; completion including recovery is separately retained in analysis.json. Token totals are known usage only; incomplete usage is explicitly counted, never assumed zero. Task times include agent construction, local instrumentation and evaluator reads, and exclude subsequent server-side audit work. Campaign elapsed time includes between-trial audit/setup overhead.',
        '',f'Charged requests: **{state.get("live_model_requests",0)}/291**; infrastructure reserve used: **{state.get("campaign",{}).get("infrastructure_retries",0)}/3**. The corrected planning estimate was ~95, not a required target.',
        '',f'Local audits passed: **{summary["local_audits_passed"]}/{len(rows)}**. Persisted Phoenix audits passed: **{summary["persisted_audits_passed"]}/{len(rows)}**; **{summary["persisted_spans"]} spans** matched. Any retained failed/unstarted work remains visible in status.json.',
        '', f'Actual physical-turn deviations from scripted expectations: **{len(summary["turn_expectation_deviations"])}**. Scripted expectations (inspection 3 primitive vs 2 macro; healthy movement 5 vs 2) are comparators, not requirements imposed on model behavior.',
        '', '| Trial | Correct | Physical calls | Scripted calls | Native attempts | Accepted status | Budget / length stop |',
        '|---|---:|---:|---:|---:|---|---|']
    for row in rows:
        scored=row.get('score',{})
        lines.append(f'| {row["id"]} | {row.get("primary_pass",False)} | {row.get("inference",{}).get("calls","not recorded")} | {row["expected_scripted_turns"]} | {len(row.get("actor_records",[]))} | {scored.get("accepted_status")} | {scored.get("budget_exhaustion")} / {scored.get("length_stop")} |')
    lines += ['', 'The native-attempt band is **0.75-1.25 per domain/depth**. Actual values, paired discordance and all-attempt/matched-success cost views are in analysis.json. These dev counts do not decide the later predictions. The held-out design still has 6 ladder template groups.',
        '', 'The single allowed scorer-amendment cycle was used before live data. It separates extra permitted acquisition costs from task correctness, and truthful wrong-skill evidence from satisfying the requested goal. All 132 retained Stage 1 primary scores were unchanged in offline regression checks. No prompt, case, guard, catalogue or condition tuning occurred. No further scorer/case revision cycle remains in this dev stage.',
        '', 'Clarification outcomes use the frozen preliminary question screen; transcripts require semantic human review. The inspection-acceptable sensitivity view is recorded separately. No independent human correctness rating is claimed.',
        '', 'Inspect [confirmation](CONFIRMATION_2026-11-14.md), [authorization preflight](authorization-preflight.json), [scorer amendment](SCORER_AMENDMENT_01_2026-11-14.md), [scorer validation](scorer-validation.json), [analysis](analysis.json), [checkpoint](status.json), and each trials/<id> result, model transcript, operation ledger and actual Phoenix export.',
        '', 'Later stages need their separate confirmations. P2 is restricted to Against or Uninformative for later reporting; no dev verdict is produced. Same-domain near-duplicate catalogue distractors are deferred for a possible Stage 4b amendment. Qwen needs its reviewed GPU-idle gate before any later launch. No Git commit, push or upload was performed.']
    (ROOT/'STAGE2_REPORT.md').write_text('\n'.join(lines)+'\n')
    (ROOT/'README.md').write_text('# G1 Stage 2 current progress\n\nUpdated: **2026-11-14**.\n\n'+
        f'Status: **{state["status"]}**, {state["completed"]}/36 checkpointed trials; '+
        f'{state.get("live_model_requests",0)}/291 charged requests.\n\n'+
        'Read [the report](STAGE2_REPORT.md) and [analysis](analysis.json). This is AI-authored exploratory Sol dev, not a P1-P4 evaluation. Later stages have not started.\n')
    print({'execution_complete':complete,'retained_trials':len(rows),'charged_requests':state.get('live_model_requests',0),
           'primary_by_mode':{m:c['primary_passes'] for m,c in by_mode.items()}})

if __name__=='__main__':main()
