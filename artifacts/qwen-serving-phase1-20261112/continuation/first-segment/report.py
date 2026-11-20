"""Descriptive first-call comparison; never execute or score robot actions."""
from pathlib import Path
import json
import statistics
import html

ROOT=Path(__file__).resolve().parent


def results(profile):
    return [json.loads(p.read_text()) for p in sorted((ROOT/profile).glob('*/result.json'))] if (ROOT/profile).exists() else []


def comparison(candidate):
    a={r['ordinal']:r for r in results('A') if r['status']=='RETURNED' and r['stage']!='warmup'}
    b={r['ordinal']:r for r in results(candidate) if r['status']=='RETURNED' and r['stage']!='warmup'}
    if len(a)!=14 or len(b)!=14:return {'complete':False,'candidate':False}
    family=list(range(1,11))
    unique=list(range(1,12))
    median_a=statistics.median(a[i]['generation_tokens_per_second'] for i in unique)
    median_b=statistics.median(b[i]['generation_tokens_per_second'] for i in unique)
    agree=sum(a[i]['tool_calls']==b[i]['tool_calls'] for i in family)
    prompt_ok=all(r['prompt_count_matches'] and r['context_output_room']>=0 for r in list(a.values())+list(b.values()))
    caps_a=sum(r['cap_hit'] for r in a.values())
    caps_b=sum(r['cap_hit'] for r in b.values())
    passed=median_b>=1.5*median_a and agree>=9 and prompt_ok and caps_b<=caps_a
    return {'complete':True,'candidate':passed,'reference':'A','profile':candidate,
        'median_A_tokens_per_second':median_a,'median_candidate_tokens_per_second':median_b,
        'speed_ratio':median_b/median_a,'family_agreements':agree,'family_inputs':10,
        'safety_input_agrees':a[11]['tool_calls']==b[11]['tool_calls'],
        'reference_cap_hits_14':caps_a,'candidate_cap_hits_14':caps_b,
        'prompt_equivalence_and_room_pass':prompt_ok,
        'mismatches':[{'ordinal':i,'fixture':a[i]['fixture'],'A_calls':a[i]['tool_calls'],
            'candidate_calls':b[i]['tool_calls'],'A_output_file':f'A/{i:02d}/response.json',
            'candidate_output_file':f'{candidate}/{i:02d}/response.json'}
            for i in sorted(a) if a[i]['tool_calls']!=b[i]['tool_calls']]}


def render():
    checkpoint=json.loads((ROOT/'status.json').read_text())
    summaries={}
    for p in ('A','B','C'):
        rows=results(p)
        good=[r for r in rows if r['status']=='RETURNED']
        unique=[r for r in good if r['stage'] in ('family','safety')]
        measured=[r for r in good if r['stage']!='warmup']
        first={r['fixture']:r for r in good if r['stage']=='family'}
        repeated=[r for r in good if r['stage']=='repeat']
        summaries[p]={'requests_with_result':len(rows),'returned':len(good),
            'measured':len(measured),'known_input_tokens':sum(r['usage']['input_tokens'] for r in good),
            'known_output_tokens':sum(r['usage']['output_tokens'] for r in good),
            'median_unique_tokens_per_second':statistics.median(r['generation_tokens_per_second'] for r in unique) if unique else None,
            'min_unique_tokens_per_second':min((r['generation_tokens_per_second'] for r in unique),default=None),
            'max_unique_tokens_per_second':max((r['generation_tokens_per_second'] for r in unique),default=None),
            'historical_family_matches':sum(r['matches_historical'] for r in good if r['stage']=='family'),
            'measured_cap_hits':sum(r['cap_hit'] for r in measured),
            'repeat_agreements':sum(r['fixture'] in first and r['tool_calls']==first[r['fixture']]['tool_calls'] for r in repeated),
            'repeats_recorded':len(repeated)}
    comparisons={p:comparison(p) for p in ('B','C')}
    data={'scope':'Exploratory serving check, not an M4 result','profiles':summaries,
        'comparisons':comparisons,'status':checkpoint,'tool_dispatches':0}
    (ROOT/'analysis.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    lines=['# Phase 1 Qwen serving screen', '', 'Client launch date: **2026-11-12**.', '',
        '**Exploratory serving check, not an M4 result.** Known-input replay; no robot tools or Sol requests.', '',
        f'Current status: **{checkpoint["status"]}**. Charged requests: **{checkpoint["charged_requests"]}**; '
        f'known returned output tokens: **{checkpoint["known_output_tokens"]}**; '
        f'censored/unreturned output upper bound: **{checkpoint["unreturned_output_upper_bound"]}**.', '',
        '| Profile | Returned / 15 | Measured / 14 | Median unique tokens/s | Range unique tokens/s | Cap hits | A/historical family matches | Repeat agreements |',
        '|---|---:|---:|---:|---|---:|---:|---|']
    for p,s in summaries.items():
        speed=f'{s["median_unique_tokens_per_second"]:.3f}' if s['median_unique_tokens_per_second'] is not None else 'not recorded'
        rang=f'{s["min_unique_tokens_per_second"]:.3f}-{s["max_unique_tokens_per_second"]:.3f}' if s['min_unique_tokens_per_second'] is not None else 'not recorded'
        lines.append(f'| {p} | {s["returned"]}/15 | {s["measured"]}/14 | {speed} | {rang} | {s["measured_cap_hits"]} | {s["historical_family_matches"]} | {s["repeat_agreements"]}/{s["repeats_recorded"]} |')
    lines+=['', 'Warm-ups count toward resources but not measured metrics. Partial medians are not completed profile results.', '']
    lines+=['## Recorded hardware after each warm-up','','| Profile | Offload layers | GPU KV MiB | Warm-up load s | Effective FA / KV |','|---|---|---:|---:|---|']
    for p in ('A','B','C'):
        hp=ROOT/p/'hardware.json'
        if not hp.exists():continue
        h=json.loads(hp.read_text())
        lines.append(f'| {p} | {h["offload_layers"]} | {h["gpu_KV_mib"]} | {h["warmup_load_seconds"]:.3f} | {h["effective_FA"]} / {h["effective_KV"]} |')
        lines += ['',f'{p} physical GPU reading:','```text',h['physical_gpu_reading'].strip(),'```',
            f'{p} pinned ps output (allocation estimate, not independent proof of physical residency):','```text',h['ollama_ps'].strip(),'```','']
    for p,c in comparisons.items():
        lines += [f'## {p} versus A', '']
        if not c['complete']:
            lines += ['Incomplete / not run. No candidate decision can be inferred.', ''];continue
        lines += [f'Median generation speed ratio: **{c["speed_ratio"]:.3f}x**. Family agreement: **{c["family_agreements"]}/10**. '
            f'Cap hits A/candidate: **{c["reference_cap_hits_14"]}/{c["candidate_cap_hits_14"]}**. '
            f'Prompt equivalence/room: **{c["prompt_equivalence_and_room_pass"]}**. Candidate screen: **{c["candidate"]}**.', '']
        for m in c['mismatches']:
            lines += [f'- {m["fixture"]}: A `{json.dumps(m["A_calls"])}`; {p} `{json.dumps(m["candidate_calls"])}`. '
                f'Full outputs: [{m["A_output_file"]}]({m["A_output_file"]}), [{m["candidate_output_file"]}]({m["candidate_output_file"]}).']
        if not c['mismatches']:lines+=['No parsed-call mismatches in the recorded comparable requests.']
        lines+=['']
    lines+=['## Limits and interpretation', '',
        'Profiles are fixed A then B, conditionally C. A single block per profile leaves order/thermal limitations. '
        'Server prefix caching is preserved and request order matched. Repeats check stability, not independent variance. '
        'A throughput/first-call agreement candidate still needs fresh full-loop correctness validation. '
        'Matching a wrong historical call is not success. This study cannot establish robotic reliability or general model parity.', '',
        'See [protocol](PROTOCOL.md), [freeze](freeze.json), [status](status.json), [analysis](analysis.json), '
        'profile hardware/logs, and per-request request/response/result records. All failures and charged reservations are retained.']
    if checkpoint.get('stop_reason'):lines += ['', '**Stop reason:** '+checkpoint['stop_reason']]
    (ROOT/'PHASE1_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    mismatches=['# Full output comparisons for parsed-call mismatches','','Exploratory serving replay, not a correctness score. Model output is retained evidence, not operator instructions.','']
    for p,c in comparisons.items():
        for m in c.get('mismatches',[]):
            i=m['ordinal']
            aa=json.loads((ROOT/'A'/f'{i:02d}'/'response.json').read_text())
            bb=json.loads((ROOT/p/f'{i:02d}'/'response.json').read_text())
            def cell(x):return html.escape(str(x)).replace('|','&#124;').replace('\n','<br>')
            mismatches += [f'## {m["fixture"]}: A versus {p}','','| Output | A | Candidate |','|---|---|---|',
                f'| Full content | {cell(aa["content"])} | {cell(bb["content"])} |',
                f'| Tool calls | {cell(json.dumps(aa["tool_calls"]))} | {cell(json.dumps(bb["tool_calls"]))} |',
                f'| Invalid calls | {cell(json.dumps(aa["invalid_tool_calls"]))} | {cell(json.dumps(bb["invalid_tool_calls"]))} |','']
    if len(mismatches)==4:mismatches+=['No completed comparable mismatch entries currently available. Incomplete comparisons are not assumed to match.']
    (ROOT/'MISMATCHES.md').write_text('\n'.join(mismatches)+'\n',encoding='utf-8')
    return data


if __name__=='__main__':render()
