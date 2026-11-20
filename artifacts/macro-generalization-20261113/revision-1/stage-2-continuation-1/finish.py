"""Combined descriptive report; old files and original failed score stay intact."""
from statistics import mean,median
from collections import defaultdict
from common import ROOT,ORIGINAL,read,write,verify

def cost(rows):
    times=[r['task_seconds'] for r in rows if 'task_seconds' in r]
    return {'trials':len(rows),'primary_correct':sum(r.get('primary_pass',False) for r in rows),
        'requests':sum(r.get('inference',{}).get('calls',0) for r in rows),
        'known_input_tokens':sum(r.get('inference',{}).get('known_input_tokens',0) for r in rows),
        'known_output_tokens':sum(r.get('inference',{}).get('known_output_tokens',0) for r in rows),
        'usage_incomplete_trials':sum(not r.get('inference',{}).get('usage_complete',False) for r in rows),
        'native_attempts':sum(len(r.get('actor_records',[])) for r in rows),
        'invalid_attempts':sum(r.get('snapshot',{}).get('validation_errors',0) for r in rows),
        'task_seconds_sum':sum(times),'task_seconds_mean':mean(times) if times else None,
        'task_seconds_median':median(times) if times else None}

def main():
    state=read(ROOT/'status.json')
    old=[read(p) for p in sorted((ORIGINAL/'trials').glob('*/result.json'))]
    new=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))] if (ROOT/'trials').exists() else []
    rows=old+new;assert len({r['id'] for r in rows})==len(rows)
    pairs=defaultdict(dict)
    for r in rows:pairs[r['case']['case_id']][r['mode']]=r
    both={name for name,p in pairs.items() if len(p)==2 and all(r.get('primary_pass') for r in p.values())}
    all_cost={m:cost([r for r in rows if r['mode']==m]) for m in ('primitives','macro')}
    matched={m:cost([r for r in rows if r['mode']==m and r['case']['case_id'] in both]) for m in all_cost}
    plan=read(ORIGINAL/'plan.json');ids={r['id'] for r in rows}
    unstarted=[r['id'] for r in plan if r['id'] not in ids]
    summary={'attempt_schedule_complete':len(rows)==36,'continuation_status':state['status'],
        'original_attempts':len(old),'new_attempts':len(new),'all_attempts':len(rows),'unstarted':unstarted,
        'all_attempt_costs':all_cost,'matched_success_costs':matched,'matched_success_pairs':len(both),
        'cumulative_requests':state['live_model_requests'],'new_requests':state['new_model_requests'],
        'request_cap':291,'original_interrupted_trial_preserved':any(r['id']=='G1r1-dev-012-primitives' and
            not r['primary_pass'] for r in old),'original_error_cause':'UNRESOLVED; failed-call usage unknown',
        'local_audits_passed':sum(r.get('local_audit',{}).get('pass',False) for r in rows),
        'persisted_audits_passed':sum(r.get('phoenix_audit',{}).get('pass',False) for r in rows),
        'persisted_spans':sum(r.get('phoenix_audit',{}).get('persisted_spans',0) for r in rows),
        'P1_P4':'NOT_ADJUDICATED_DEV_ONLY','case_scorer_revision_cycles_total':1,'new_scorer_cycles':0,
        'later_stages_started':False,'protected_check':verify()}
    assert sum(c['requests'] for c in all_cost.values())==state['live_model_requests']
    write('combined-analysis.json',summary)
    lines=['# G1 Stage 2 combined continuation report','','Date: **2026-11-14**.',
        '', f'Finalized attempts: **{len(rows)}/36** ({len(old)} original + {len(new)} continuation). '
        f'Correct completed trials: **{sum(r.get("primary_pass",False) for r in rows)}**. '
        f'Unstarted trials: **{len(unstarted)}**.',
        '', 'The original provider-interrupted trial remains recorded as failed/censored execution. '
        'It was not rerun or replaced, and it does not establish a wrong Sol decision. This is '
        'AI-authored exploratory dev, without independent teammate authorship or semantic-novelty '
        'review. P1-P4 are not adjudicated.',
        '', f'Cumulative inference attempts: **{state["live_model_requests"]}/291**, including '
        f'**66 original + {state["new_model_requests"]} new**. No new case/scorer amendment cycle was used.',
        '', '| Condition, all attempts | Correct | Physical calls | Known input / output tokens | Native attempts | Mean / median task seconds |',
        '|---|---:|---:|---:|---:|---:|']
    for mode,c in all_cost.items():
        t=f'{c["task_seconds_mean"]:.2f} / {c["task_seconds_median"]:.2f}' if c['task_seconds_mean'] is not None else 'not recorded'
        lines.append(f'| {mode} | {c["primary_correct"]}/{c["trials"]} | {c["requests"]} | {c["known_input_tokens"]} / {c["known_output_tokens"]} | {c["native_attempts"]} | {t} |')
    lines += ['',f'Matched-primary-success subset: **{len(both)} paired cases**. Full cost views are in '
        '[combined-analysis.json](combined-analysis.json). Failed-call usage is unknown, not zero; '
        'known token sums are incomplete for those calls. Do not interpret the provider interruption '
        'as an architectural reliability advantage. Task timings are monotonic and exclude subsequent '
        'server-side audit work; cross-segment timing/state differences limit causal interpretation.',
        '',f'Local audits passed: **{summary["local_audits_passed"]}/{len(rows)}**. Persisted audits passed: '
        f'**{summary["persisted_audits_passed"]}/{len(rows)}**, with **{summary["persisted_spans"]}** matched spans.',
        '', 'The original eight-hour wall-clock window had expired before this continuation. '
        'A separate explicit owner approval was required for the bounded new 30-minute window; '
        'the old request count and cumulative active-execution allowance were carried forward. '
        'The original deadline was not silently reset. See [the continuation plan](CONTINUATION_PLAN_2026-11-14.md) '
        'and window-approval.json. Fresh restore-only authorization was reviewed and rechecked at launch. '
        'Provider quota remained unknown. No new OAuth consent or scope expansion was permitted.',
        '', '| Trial | Primary correct | Calls | Native attempts | Error |',
        '|---|---:|---:|---:|---|']
    for r in rows:
        lines.append(f'| {r["id"]} | {r.get("primary_pass",False)} | {r.get("inference",{}).get("calls","not recorded")} | {len(r.get("actor_records",[]))} | {(r.get("error") or {}).get("code","")} |')
    lines += ['', 'The frozen original request, condition wording, public tools, limits, scorer and '
        'native-operation accounting rules were retained. The original condition-wording confound '
        'remains. Clarification results still require semantic human review; an automated question '
        'screen is not independent adjudication. The original Base depth-6 primitive interruption '
        'leaves that native-cost pair incomplete; do not invent its missing acquisitions.',
        '', 'No later stage or Qwen run was launched. No Git commit, push or upload was performed. '
        'The original reports/manifests remain unchanged; this combined report is a separate artifact.']
    (ROOT/'COMBINED_STAGE2_REPORT.md').write_text('\n'.join(lines)+'\n')
    (ROOT/'README.md').write_text('# Stage 2 continuation current progress\n\nUpdated: **2026-11-14**.\n\n'
        f'Status: **{state["status"]}**; {len(rows)}/36 cumulative finalized attempts; '
        f'{state["live_model_requests"]}/291 cumulative requests.\n\n'
        'See [combined report](COMBINED_STAGE2_REPORT.md) and [analysis](combined-analysis.json). '
        'The original provider-interrupted attempt was retained; P1-P4 remain unadjudicated.\n')
    print({k:summary[k] for k in ('attempt_schedule_complete','all_attempts','new_attempts','cumulative_requests','new_requests')})

if __name__=='__main__':main()
