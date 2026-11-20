"""Independent archive aggregation; never rewrites raw trials or frozen scoring."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import sys
import zipfile

MODELS = ['qwen3.5:9b', 'llama3.1:8b-instruct-q4_K_M', 'granite3.3:8b',
          'ministral-3:8b-instruct-2512-q4_K_M']
LABELS = dict(zip(MODELS, ['Qwen3.5 9B', 'Llama 3.1 8B', 'Granite 3.3 8B', 'Ministral 3 8B']))


def key(model):
    return model.replace(':', '_')


def reduction(reference, candidate):
    return None if not reference else 100 * (reference - candidate) / reference


def number(value, digits=2):
    return 'NOT_RECORDED' if value is None else f'{value:,.{digits}f}'


def main(folder):
    archive = folder / 'ROSA_LAB_MULTIMODEL_2026-11-17.zip'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        manifest = json.loads(z.read('ARCHIVE_MANIFEST.json'))
        for name, expected in manifest['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
        def read(name):
            return json.loads(z.read(name))
        freeze = read('study/freeze.json')
        for name, expected in freeze['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
        state = read('results/operator-status.json')
        control = read('results/deterministic/controls/checkpoint.json')
        assert len(control['trials']) == 20 and control['primary_correct'] == 20
        assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in control['trials'])
        summaries = {}
        families = {}
        matrix = {}
        all_rows = []
        audits = 0
        persisted_spans = 0
        for model in MODELS:
            path = f'results/{key(model)}/ollama/'
            if path + 'checkpoint.json' not in z.namelist():
                summaries[model] = {'status': 'UNSTARTED', 'recorded': 0}
                continue
            checkpoint = read(path + 'checkpoint.json')
            rows = checkpoint['trials']
            assert len({r['job']['id'] for r in rows}) == len(rows)
            traced_call_metadata = []
            for row in rows:
                raw = read(path + row['job']['id'] + '/result.json')
                for name in ('case', 'condition', 'repetition', 'inference', 'score', 'primary_pass', 'wall_seconds'):
                    assert raw[name] == row[name], (model, row['job']['id'], name)
                pa = read(path + row['job']['id'] + '/phoenix-audit.json')
                assert pa == row['phoenix_audit'] and pa['pass'] and row['local_audit']['pass']
                audits += 1
                persisted_spans += pa['persisted_spans']
                trace = read(path + row['job']['id'] + '/trace.json')
                spans = sorted((s for s in trace['spans'] if
                    s.get('attributes', {}).get('openinference.span.kind') == 'LLM'),
                    key=lambda s: s['start_time'])
                assert len(spans) == row['inference']['calls']
                for span in spans:
                    output = span.get('attributes', {}).get('output.value')
                    generation_info = {}
                    if output:
                        payload = json.loads(output)
                        generations = payload.get('generations') or []
                        if generations:
                            generation = generations[0]
                            if isinstance(generation, list):
                                generation = generation[0]
                            generation_info = generation.get('generation_info') or {}
                    traced_call_metadata.append(generation_info)
            calls = read(f'results/{key(model)}/physical-model-calls.json')
            assert len(calls) == checkpoint['live_model_requests'], model
            assert len(calls) == sum(r['inference']['calls'] for r in rows), model
            assert len(traced_call_metadata) == len(calls)
            # BaseChatModel merges generation_info into message metadata after
            # _generate returns. The journal's early metadata can be empty;
            # finalized, audited LLM spans retain the actual Ollama fields.
            returned = [{'response_metadata': meta} for meta in traced_call_metadata if meta]
            def recorded_sum(field):
                values = [c['response_metadata'][field] for c in returned
                    if type(c['response_metadata'].get(field)) in (int,float)]
                return sum(values) if values else None
            total_eval = recorded_sum('eval_count')
            eval_ns = recorded_sum('eval_duration')
            load_ns = recorded_sum('load_duration')
            prompt_ns = recorded_sum('prompt_eval_duration')
            total_ns = recorded_sum('total_duration')
            model_summary = {'status': checkpoint['status'], 'recorded': len(rows), 'planned': 80,
                'campaign_seconds': checkpoint.get('total_elapsed_seconds'),
                'physical_requests': len(calls), 'physical_call_records_match': True,
                'server_metadata_source': 'finalized audited LLM span output.value generation_info',
                'calls_with_returned_server_metadata': len(returned),
                'request_cap': checkpoint['campaign']['request_cap'],
                'reserve_used': checkpoint['campaign']['infrastructure_retries'],
                'cleanup': checkpoint['simulator_cleanup'], 'cleanup_errors': checkpoint['cleanup_errors'],
                'output_length_stops': sum(e.get('finish_reason') == 'length' for r in rows for e in r['inference']['events']),
                'max_returned_prompt_tokens': max((c['response_metadata']['prompt_eval_count'] for c in returned
                    if type(c['response_metadata'].get('prompt_eval_count')) is int), default=None),
                'prompt_eval_cached_count': [c['response_metadata']['prompt_eval_cached_count'] for c in returned
                    if 'prompt_eval_cached_count' in c.get('response_metadata', {})] or 'NOT_RECORDED',
                'server_load_seconds': load_ns / 1e9 if load_ns is not None else None,
                'server_prompt_seconds': prompt_ns / 1e9 if prompt_ns is not None else None,
                'server_generation_seconds': eval_ns / 1e9 if eval_ns is not None else None,
                'server_total_seconds': total_ns / 1e9 if total_ns is not None else None,
                'generation_tokens_per_second': total_eval / (eval_ns / 1e9) if eval_ns and total_eval is not None else None,
                'conditions': {}}
            pairs = {}
            for row in rows:
                pairs.setdefault((row['case'], row['repetition']), {})[row['condition']] = row
                matrix[(model, row['case'], row['repetition'], row['condition'])] = row
                all_rows.append((model, row))
                families.setdefault(row['case'], {})[(model, row['condition'])] = None
            for condition in ['primitives', 'macro']:
                selected = [r for r in rows if r['condition'] == condition]
                known = [r for r in selected if r['case'] != 'ambiguous_goal']
                ambiguous = [r for r in selected if r['case'] == 'ambiguous_goal']
                matching = [p for (case, rep), p in pairs.items() if case != 'ambiguous_goal' and
                    len(p) == 2 and all(r['primary_pass'] for r in p.values())]
                values = {'recorded': len(selected), 'known_correct': sum(r['primary_pass'] for r in known),
                    'known_recorded': len(known), 'known_planned': 36,
                    'known_selection_correct': sum(r['score']['goal_correct'] for r in known),
                    'known_selected_outcome_correct': sum(r['score']['selected_outcome_correct'] for r in known),
                    'known_passes_after_validation_errors': sum(r['primary_pass'] and r['score']['invalid_attempts'] > 0 for r in known),
                    'known_passes_without_validation_errors': sum(r['primary_pass'] and r['score']['invalid_attempts'] == 0 for r in known),
                    'known_agent_error_text': sum(str(r['answer']).startswith('An error occurred:') for r in known),
                    'known_error_text_codes': dict(Counter(str(r['answer']).split(': ',1)[1]
                        for r in known if str(r['answer']).startswith('An error occurred:'))),
                    'known_validation_codes': dict(Counter(e['code'] for r in known for e in r['snapshot']['events']
                        if e['type'] == 'validation')),
                    'known_schema_details': dict(Counter(d['field']+':'+d['reason']
                        for r in known for e in r['snapshot']['events'] if e['type'] == 'validation'
                        and e['code'] == 'schema_validation' for d in e.get('details',[]))),
                    'ambiguous_recorded': len(ambiguous), 'human_status': 'PENDING',
                    'ambiguous_no_action': sum(r['snapshot']['selected_skill'] is None and
                        not r['snapshot']['operations'] and not any(q.get('accepted') for q in r['snapshot']['reports'])
                        and r['score']['dispatches'] == 0 for r in ambiguous),
                    'legacy_ambiguous_passes': sum(r['primary_pass'] for r in ambiguous),
                    'calls': sum(r['inference']['calls'] for r in selected),
                    'input_tokens': sum(r['inference']['known_input_tokens'] for r in selected),
                    'output_tokens': sum(r['inference']['known_output_tokens'] for r in selected),
                    'unknown_usage_trials': sum(not r['inference']['usage_complete'] for r in selected),
                    'native': sum(r['score']['native_operations'] for r in selected),
                    'model_native': sum(r['score']['model_native_operations'] for r in selected),
                    'program_native': sum(r['score']['program_native_operations'] for r in selected),
                    'seconds': sum(r['wall_seconds'] for r in selected),
                    'mean_seconds': statistics.mean(r['wall_seconds'] for r in selected) if selected else None,
                    'median_seconds': statistics.median(r['wall_seconds'] for r in selected) if selected else None,
                    'max_seconds': max((r['wall_seconds'] for r in selected), default=None),
                    'invalid': sum(r['score']['invalid_attempts'] for r in selected),
                    'unsupported_success': sum(r['score']['unsupported_success_attempts'] for r in selected),
                    'wrong_goal_success': sum(r['score']['accepted_success_wrong_user_goal'] for r in known),
                    'legacy_wrong_goal_success_all_trials': sum(r['score']['accepted_success_wrong_user_goal'] for r in selected),
                    'dispatch_violations': sum(bool(r['score']['dispatch_violations']) for r in selected),
                    'fault_exercised': sum(r['score']['injected_fault_exercised'] is True for r in selected),
                    'fault_required': sum(r['score']['injected_fault_exercised'] is not None for r in selected),
                    'errors': dict(Counter(r['error_type'] for r in selected if r.get('error_type'))),
                    'matched_success_pairs': len(matching),
                    'matched_calls': sum(p[condition]['inference']['calls'] for p in matching),
                    'matched_native': sum(p[condition]['score']['native_operations'] for p in matching),
                    'matched_seconds': sum(p[condition]['wall_seconds'] for p in matching)}
                model_summary['conditions'][condition] = values
                for case in families:
                    relevant = [r for r in selected if r['case'] == case]
                    if relevant:
                        families[case][(model, condition)] = (sum(r['primary_pass'] for r in relevant), len(relevant))
            known_pairs = [p for (case, rep), p in pairs.items() if case != 'ambiguous_goal' and len(p) == 2]
            model_summary['paired_macro_vs_primitives'] = {
                'pairs': len(known_pairs),
                'macro_only_correct': sum(p['macro']['primary_pass'] and not p['primitives']['primary_pass'] for p in known_pairs),
                'primitive_only_correct': sum(p['primitives']['primary_pass'] and not p['macro']['primary_pass'] for p in known_pairs)}
            summaries[model] = model_summary
        paired_vs_qwen = {}
        for model in MODELS[1:]:
            paired_vs_qwen[model] = {}
            for condition in ['primitives', 'macro']:
                compared = [(r, matrix[(MODELS[0], r['case'], r['repetition'], condition)])
                    for m, r in all_rows if m == model and r['condition'] == condition and r['case'] != 'ambiguous_goal'
                    and (MODELS[0], r['case'], r['repetition'], condition) in matrix]
                matched = [(a,q) for a,q in compared if a['primary_pass'] and q['primary_pass']]
                paired_vs_qwen[model][condition] = {'pairs': len(compared),
                    'candidate_only_correct': sum(a['primary_pass'] and not q['primary_pass'] for a,q in compared),
                    'qwen_only_correct': sum(q['primary_pass'] and not a['primary_pass'] for a,q in compared),
                    'matched_success_pairs': len(matched),
                    'matched_candidate_calls': sum(a['inference']['calls'] for a,q in matched),
                    'matched_qwen_calls': sum(q['inference']['calls'] for a,q in matched),
                    'matched_candidate_seconds': sum(a['wall_seconds'] for a,q in matched),
                    'matched_qwen_seconds': sum(q['wall_seconds'] for a,q in matched),
                    'matched_candidate_native': sum(a['score']['native_operations'] for a,q in matched),
                    'matched_qwen_native': sum(q['score']['native_operations'] for a,q in matched)}
        result = {'operator': state, 'models': summaries, 'paired_vs_qwen': paired_vs_qwen,
            'verified_live_audits': audits, 'persisted_live_spans': persisted_spans,
            'verified_archive_files': len(manifest['files']), 'verified_frozen_files': len(freeze['files']),
            'same_qwen_digest_as_m4': freeze['same_qwen_digest_as_m4'],
            'ambiguity_semantic_verdict': 'PENDING_HUMAN_REVIEW',
            'historical_sol_not_rerun': True}
        (folder / 'INDEPENDENT_ANALYSIS.json').write_text(json.dumps(result, indent=2) + '\n')
        lines = ['# ROSA lab local-model comparison', '', 'Date: **2026-11-17**.', '',
            'A new M4-based replication on the lab RTX 4080 SUPER. Original M4 results remain unchanged. '
            'The owner requested **80 trials per model**, so this schedules **320 total** across four model families. '
            'Original M4 had **80 total**, 40 each for Sol and Qwen.', '',
            '**Semantic correctness covers 72 known-goal trials/model (36 per condition).** '
            'Eight ambiguous trials/model remain separately pending human semantic review; legacy regex passes are not a final judgment. '
            'Calls, tokens, native operations and timing below include **all attempted trials**, including failures and ambiguous cases.', '',
            '| Model | Condition | Known-goal correct | Recorded trials | Calls | Input tokens | Output tokens | Mean task s | Median task s | Native ops |',
            '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for model in MODELS:
            for c, v in summaries[model].get('conditions', {}).items():
                lines.append(f'| {LABELS[model]} | {c} | {v["known_correct"]}/{v["known_recorded"]} | {v["recorded"]}/40 | {v["calls"]} | {v["input_tokens"]:,} | {v["output_tokens"]:,} | {number(v["mean_seconds"])} | {number(v["median_seconds"])} | {v["native"]} |')
        lines += ['', '## Macro versus primitives: cost and correctness together', '',
            'Matched-success costs use only known-goal pairs where **both** conditions passed. This selected subset cannot erase failures in the full schedule.', '',
            '| Model | Known-goal macro minus primitive passes | Macro-only / primitive-only correct pairs | Matched-success pairs | Matched calls P / M | Calls saved | Matched native P / M | Matched time P / M (s) |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
        for model, s in summaries.items():
            if 'conditions' not in s:
                continue
            p, m = s['conditions']['primitives'], s['conditions']['macro']
            pair = s['paired_macro_vs_primitives']
            saved = reduction(p['matched_calls'], m['matched_calls'])
            saved_text = number(saved)+'%' if saved is not None else 'N/A (no successful pairs)'
            lines.append(f'| {LABELS[model]} | {m["known_correct"]-p["known_correct"]:+d} | {pair["macro_only_correct"]} / {pair["primitive_only_correct"]} | {p["matched_success_pairs"]} | {p["matched_calls"]} / {m["matched_calls"]} | {saved_text} | {p["matched_native"]} / {m["matched_native"]} | {number(p["matched_seconds"])} / {number(m["matched_seconds"])} |')
        lines += ['', '## Direct paired comparison against fresh lab Qwen', '',
            'Each candidate is aligned with Qwen on case, repetition and execution condition. Repeated cases are not independent task families.', '',
            '| Candidate | Condition | Known-goal pairs | Candidate-only correct | Qwen-only correct |',
            '|---|---|---:|---:|---:|']
        for model, compared in paired_vs_qwen.items():
            for c,v in compared.items():
                lines.append(f'| {LABELS[model]} | {c} | {v["pairs"]} | {v["candidate_only_correct"]} | {v["qwen_only_correct"]} |')
        lines += ['', 'Across-model matched-success costs below use only identical case/repetition/condition cells that both the candidate and Qwen passed. They accompany, rather than replace, the all-attempt and discordant-outcome views.', '',
            '| Candidate | Condition | Both-correct cells | Calls candidate / Qwen | Task seconds candidate / Qwen | Native candidate / Qwen |',
            '|---|---|---:|---:|---:|---:|']
        for model, compared in paired_vs_qwen.items():
            for c,v in compared.items():
                lines.append(f'| {LABELS[model]} | {c} | {v["matched_success_pairs"]} | {v["matched_candidate_calls"]} / {v["matched_qwen_calls"]} | {number(v["matched_candidate_seconds"])} / {number(v["matched_qwen_seconds"])} | {v["matched_candidate_native"]} / {v["matched_qwen_native"]} |')
        lines += ['', '## Family outcomes', '',
            'Each known-goal cell is passes/recorded for that family and condition. **Pending** is not a failure. The ambiguous family is excluded from semantic pass totals.', '',
            '| Family | Qwen P | Qwen M | Llama P | Llama M | Granite P | Granite M | Ministral P | Ministral M |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for case, data in families.items():
            cells=[]
            for model in MODELS:
                for c in ['primitives','macro']:
                    value=data.get((model,c))
                    cells.append('PENDING' if case=='ambiguous_goal' else (f'{value[0]}/{value[1]}' if value else 'UNSTARTED'))
            lines.append('| '+case+' | '+' | '.join(cells)+' |')
        lines += ['', '## Errors, claims and fault exercise', '',
            '| Model | Condition | Invalid attempts | Unsupported SUCCESS attempts | Accepted wrong-goal SUCCESS (known goals) | Fault exercised / required | Dispatch violations | Error types |',
            '|---|---|---:|---:|---:|---:|---:|---|']
        for model,s in summaries.items():
            for c,v in s.get('conditions',{}).items():
                lines.append(f'| {LABELS[model]} | {c} | {v["invalid"]} | {v["unsupported_success"]} | {v["wrong_goal_success"]} | {v["fault_exercised"]}/{v["fault_required"]} | {v["dispatch_violations"]} | {v["errors"]} |')
        lines += ['', '**Metric boundary:** unsupported-SUCCESS attempts count validation events at the structured reporting tool. This is not a semantic audit of every free-text claim. A model can describe invented tool execution without invoking a tool, fail the task, and still have zero structured unsupported-SUCCESS events. Accepted wrong-goal SUCCESS in this table covers known-goal tasks; raw legacy flags across all trials remain separately available in JSON.']
        lines += ['', '## Selection, reporting and feedback are different outcomes', '',
            'These rows concern the 36 known-goal tasks in each condition. Correct skill selection does not imply successful execution or an accepted report. A pass after validation errors credits the combined model/feedback/framework system, not an unaided first-pass model improvement.', '',
            '| Model | Condition | Correct selection | Correct selected outcome | Full-task pass | Pass after validation errors | Agent returned an error message |',
            '|---|---|---:|---:|---:|---:|---:|']
        for model,s in summaries.items():
            for c,v in s.get('conditions',{}).items():
                lines.append(f'| {LABELS[model]} | {c} | {v["known_selection_correct"]}/36 | {v["known_selected_outcome_correct"]}/36 | {v["known_correct"]}/36 | {v["known_passes_after_validation_errors"]} | {v["known_agent_error_text"]} |')
        lines += ['', 'The legacy outer `error_type` can be empty while ROSA returns a controlled error as answer text. It does not mean that generation truncation or validation exhaustion never occurred. Structured validation codes, schema details and these returned-error codes are preserved in INDEPENDENT_ANALYSIS.json.']
        lines += ['', '## Speed, inference and resource accounting', '',
            'Task time includes the agent loop and its native operations. Campaign time additionally includes simulator startup, resets, independent observations, logging and trace audits. The inference throughput below is returned eval tokens divided by returned eval duration, not wall-clock task throughput. Cold-load time is shown rather than silently removed.', '',
            '| Model | Campaign s | Physical calls | Returned length stops | Max returned prompt tokens | Load s | Prompt evaluation s | Generation s | Generated tokens/s |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for model,s in summaries.items():
            if 'physical_requests' not in s:
                continue
            lines.append(f'| {LABELS[model]} | {number(s["campaign_seconds"])} | {s["physical_requests"]} | {s["output_length_stops"]} | {s["max_returned_prompt_tokens"]} | {number(s["server_load_seconds"])} | {number(s["server_prompt_seconds"])} | {number(s["server_generation_seconds"])} | {number(s["generation_tokens_per_second"])} |')
        lines += ['', 'Unknown usage and whether `prompt_eval_cached_count` exists are retained explicitly in INDEPENDENT_ANALYSIS.json. LangChain response cache is disabled; that does not prove the Ollama server reused no prompt prefix/KV state. Token counts use each model\'s tokenizer and do not represent equal semantic work.', '',
            '## Reproducibility and limits', '',
            f'- Operator phase: **{state["phase"]}**. Verify completed per-model schedules before calling the study finished.',
            f'- Archive CRC and **{len(manifest["files"])} content hashes** matched; **{len(freeze["files"])} frozen source/config hashes** matched.',
            f'- **{audits} live local/persisted audit pairs** checked, totaling **{persisted_spans:,} persisted live spans**. Twenty deterministic controls passed separately.',
            f'- Qwen digest identical to retained original M4: **{freeze["same_qwen_digest_as_m4"]}**.',
            '- Four models use Q4_K_M, the same requested 8K context, 1024 output tokens/call, 2048 observed output tokens/task, temp0, seed42, non-thinking policy, and unchanged tools/guards. Architecture, tokenizer, templates, stop tokens and other native defaults differ.',
            '- Limits: eight decisions, 360 seconds, ten native operations, sixteen tool attempts, three corrections and at most one permitted movement/task. Each model has 640 ordinary plus three narrowly eligible reserve request slots and an eight-hour campaign window. Failed/unknown usage is not free compute.',
            '- Lab host is Ubuntu 25.04; the owned ROS 2 Jazzy container uses Ubuntu 24.04. Locked Python environments and exact container package inventory are archived. Actual simulator package versions can differ from the historical laptop.',
            '- Seeded model order is Ministral, Granite, Qwen, Llama. GPU is checked at each launch, not continuously proven idle throughout. Model timing is observed combined-system performance on a shared host.',
            '- All conditions share the repaired framework. This does not compare against untouched upstream ROSA. Execution mode and condition wording remain packaged together.',
            '- These are known M4 cases repeated four times, not 80 independent tasks/model or unseen generalization. There are only nine known-goal families plus one ambiguity family; no population-level equivalence or general reliability claim follows.',
            '- Human clarification judgments remain pending. Structural no-action counts and raw legacy regex diagnostics are available; no names or judgments were fabricated.',
            '- Frozen historical M4/G1/M1–M5 artifacts were not rewritten. G1 held-out remains paused. No new Sol requests, OAuth grant or physical robot action was involved.', '',
            '## Historical comparison context', '',
            'Original M4 used **20 trials/condition/backend**, including two ambiguous trials per condition. Its reported whole-task outcomes were Sol **20/20 → 20/20** and Qwen **15/20 → 14/20**. Calls were **68 → 38** and **91 → 53**; mean task time was **16.42 → 9.73 s** and **133.49 → 85.18 s**, respectively. These original totals are preserved, not rescored.', '',
            'The new schedule doubles repetitions and reports clarification separately because of the known regex defect. Historical Sol is not a fresh lab control. A laptop-to-lab Qwen speed difference combines GPU/offload, environment, schedule and time effects; it is not an intrinsic model or framework improvement.', '',
            '## Interpretation and next step', '',
            'Use known-goal correctness and paired disagreements first, then compare all-attempt and matched-success costs. A model that stops cheaply on the wrong skill is not more effective. An evidence-grounded readiness SUCCESS can still fail a movement goal. Native-operation savings, inference savings and task-time savings are different claims.', '',
            'Treat any ranking here as a ranking of these model/configuration/framework combinations on this small known catalogue. Retain a cheaper macro only where its correctness trade-off is acceptable; do not enlarge limits or tune prompts after observing these outcomes and present that as the same experiment. Obtain actual clarification review before an 80-case semantic verdict, and resolve the existing G1 gates before any G1 held-out launch.', '',
            'Official model references: [Qwen3.5](https://ollama.com/library/qwen3.5), [Llama 3.1](https://ollama.com/library/llama3.1), [Granite 3.3](https://ollama.com/library/granite3.3), [Ministral 3](https://ollama.com/library/ministral-3). Exact downloaded identities and licenses are in preparation/model-*.json and study/freeze.json.', '']
        (folder / 'DETAILED_COMPARISON_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
        (folder / 'INDEPENDENT_VERIFICATION.json').write_text(json.dumps({
            'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'archive_files_verified':len(manifest['files']),'frozen_files_verified':len(freeze['files']),
            'all_trial_records_match_checkpoints':True,'physical_request_counts_match':True,
            'live_audits_passed':audits,'persisted_live_spans':persisted_spans,
            'operator_phase':state['phase']},indent=2)+'\n')
        print(json.dumps({'phase':state['phase'],'models':{m:{'status':s['status'],'recorded':s['recorded']} for m,s in summaries.items()},'audits':audits}))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
