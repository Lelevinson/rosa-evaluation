"""Render descriptive report from independently verified evidence; no model calls."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EVIDENCE = BASE / 'evidence'
DATA = EVIDENCE / 'INDEPENDENT_RERUN_ANALYSIS.json'
LABEL = {'llama3.1:8b-instruct-q4_K_M': 'Llama 3.1 8B', 'granite3.3:8b': 'Granite 3.3 8B'}


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|'] +
        ['| ' + ' | '.join(str(c).replace('|', '/') for c in r) + ' |' for r in rows]) + '\n'


def main():
    d = json.loads(DATA.read_text(encoding='utf-8'))
    rows = []
    for model, value in d['models'].items():
        for c, s in value['summary'].items():
            rows.append([LABEL[model], c, f"{s['known_goal_correct']}/36", s['calls'],
                s['input_tokens'], s['output_tokens'], f"{s['mean_seconds']:.2f}",
                f"{s['median_seconds']:.2f}", s['native_operations'], s['invalid_attempts']])
    report = '''# Llama and Granite: integration repair and 80-trial reruns

Date: **2026-11-17** (project/operator timezone). Status: execution and independent archive verification complete.

'''
    report += '## Result at a glance\n\n'
    for m, v in d['models'].items():
        p, k = v['summary']['primitives'], v['summary']['macro']
        saved = (1 - k['calls'] / p['calls']) * 100
        time_saved = (1 - k['total_seconds'] / p['total_seconds']) * 100
        report += (f"- **{LABEL[m]}:** known-goal correctness **{p['known_goal_correct']}/36 primitives, "
            f"{k['known_goal_correct']}/36 macro**, versus 0/36 in each older condition. "
            f"Macro used {p['calls']} → {k['calls']} calls ({saved:.1f}% fewer); "
            f"mean task time {p['mean_seconds']:.2f} → {k['mean_seconds']:.2f} s "
            f"({time_saved:.1f}% less measured task time). Correctness difference: "
            f"{k['known_goal_correct'] - p['known_goal_correct']:+d}/36.\n")
    report += '\nAll **160/160 robot attempts** completed, plus 24/24 live validation attempts; tracing, preserved-source checks and resource-bound checks passed. Completion of the schedule is separate from task success. Eight ambiguous attempts per model remain pending human review.\n\n'
    report += '''
## Scope and interpretation

The owner authorized the opt-in integration profile, fresh complete-loop validation, and immediate **80 Llama + 80 Granite Gazebo trials** after the functional gate. This is a new engineering replication of known M4 cases, not new G1 held-out evidence. The original zero-scoring configurations, diagnostic failures, source freezes and all previous studies remain preserved.

Each model ran ten existing families, four repetitions, and two execution conditions: **40 primitives and 40 macro attempts**. Each condition includes **36 known-goal tasks and four ambiguous requests**. The eight ambiguous attempts per model still require actual human semantic review; their old regex results are diagnostics, never a final task-correctness score.

The proper comparison is a combined system/configuration comparison. Native formatting guidance, persistent schemas and explicitly nonstreaming HTTP were introduced together. This run cannot identify their individual causal effects or establish inherent model superiority. Models still chose their skills and arguments; Python performed bounded execution and evidence validation. No training, task-specific answer routing or stock-ROSA comparison was added.

Within the primitive/macro comparison, the original M4 execution mode and condition instruction sentence remain a package. The condition effect on skill selection cannot be separated from condition wording. Both conditions use the repaired ROSA framework; this is not evidence of superiority to unmodified ROSA or a new selection algorithm.

## Main outcomes and costs

Costs below include **all 40 attempts per condition**, including failures and ambiguity. Fast failure is not successful task efficiency. Known-goal success uses the original goal, independently observed robot outcome, accepted reporting contract, permitted dispatch count and actual fault-exercise checks.

'''
    report += table(['Backend', 'Condition', 'Known-goal correct', 'Calls', 'Input tokens', 'Output tokens',
        'Mean task s', 'Median task s', 'Native ops', 'Invalid attempts'], rows)
    report += '\nTask time is measured inside each task; it excludes simulator startup/reset, separate deterministic controls and post-task persisted trace queries. Campaign elapsed time is reported separately below. Token counts are server/adapter usage totals, not `output limit × maximum calls`.\n'
    report += '\n## Previous integration versus repaired integration\n\n'
    comparison = []
    for model, value in d['models'].items():
        for c in ['primitives', 'macro']:
            old, new = value['old_configuration'][c], value['summary'][c]
            comparison.append([LABEL[model], c, f"{old['known_goal_correct']}/36", f"{new['known_goal_correct']}/36",
                old['calls'], new['calls'], f"{old['mean_seconds']:.2f}", f"{new['mean_seconds']:.2f}"])
    report += table(['Backend', 'Condition', 'Old correct', 'New correct', 'Old calls', 'New calls', 'Old mean s', 'New mean s'], comparison)
    report += '\nOld and new use the same installed weights, hardware, original task catalogue and scoring source. They differ in the declared integration profile and actual HTTP behavior. Earlier constructor `streaming=False` was not proof of nonstreaming HTTP in this pinned adapter; this rerun records and checks the actual request. No retrospective score or source file was changed.\n'
    report += '\n## Per-family outcomes\n\n'
    families = []
    first = next(iter(d['models'].values()))
    for family in first['summary']['primitives']['families']:
        values = [family]
        for model in d['models']:
            for c in ['primitives', 'macro']:
                f = d['models'][model]['summary'][c]['families'][family]
                values.append('PENDING HUMAN' if family == 'ambiguous_goal' else f"{f['correct']}/{f['n']}")
        families.append(values)
    report += table(['Family', 'Llama P', 'Llama M', 'Granite P', 'Granite M'], families)
    report += '\n## Paired correctness and matched-success efficiency\n\n'
    for model, value in d['models'].items():
        p = value['paired']
        report += f"### {LABEL[model]}\n\nThere are {p['known_goal_pairs']} known-goal primitive/macro pairs: **{p['both_correct']} both correct**, {p['primitive_only_correct']} primitive-only correct, {p['macro_only_correct']} macro-only correct, {p['both_wrong']} both wrong.\n\n"
        report += table(['Condition', 'Matched successes', 'Calls', 'Input', 'Output', 'Task s', 'Native ops'],
            [[c, s['trials'], s['calls'], s['input_tokens'], s['output_tokens'], f"{s['seconds']:.2f}", s['native_operations']]
                for c, s in p['matched_success_costs'].items()])
        report += '\nThis subset compares the same cells that both conditions completed. It is selected by outcome and does not replace all-attempt costs or estimate unconditional throughput.\n'
    report += '\n## Selection, reporting, faults and remaining failures\n\n'
    report += table(['Backend', 'Condition', 'Correct skill /36', 'Correct selected outcome /36', 'Dispatches',
        'Accepted SUCCESS for wrong goal', 'Structured unsupported SUCCESS attempts', 'Returned error strings'],
        [[LABEL[m], c, s['correct_skill_known_goal'], s['selected_outcome_correct_known_goal'], s['dispatches'],
            s['known_goal_accepted_wrong_successes'], s['structured_unsupported_success_attempts'], s['returned_error_messages']]
            for m, v in d['models'].items() for c, s in v['summary'].items()])
    report += '\nThe unsupported-success counter covers structured reporting attempts; it is not an exhaustive semantic audit of free text. A truthful report for an incorrectly selected skill can still fail the user goal. Outer exception fields alone also miss errors returned as ordinary answer strings. The independent JSON retains both and every failed/ambiguous answer.\n'
    report += '\nRecorded validation and terminal-error frequencies (counts can exceed failed tasks because a task may make several invalid attempts):\n\n'
    report += table(['Backend', 'Condition', 'Validation codes', 'Returned terminal errors'],
        [[LABEL[m], c, json.dumps(s['validation_codes'], sort_keys=True), json.dumps(s['returned_error_codes'], sort_keys=True)]
            for m, v in d['models'].items() for c, s in v['summary'].items()])
    for m, v in d['models'].items():
        report += '\n' + LABEL[m] + ':\n\n'
        for c, s in v['summary'].items():
            report += f"- **{c}:** {s['faults_actually_exercised']} injected faults exercised; {len(s['skipped_injected_faults'])} skipped or unexercised fault cells. Model/program native operations: {s['native_by_actor']['model']}/{s['native_by_actor']['program']}.\n"
        report += '\n'
        report += table(['Failed known-goal cell', 'Selected skill', 'Accepted report', 'Fault exercised', 'Calls', 'Outer error'],
            [[f"{r['case']} r{r['repetition']} {r['condition']}", r['selected_skill'], r['score']['accepted_report_status'],
                r['score']['injected_fault_exercised'], r['calls'], r['error_type']]
                for r in v['failure_and_ambiguous_details'] if r['case'] != 'ambiguous_goal'])
    report += '\n## Fresh full-loop validation before Gazebo\n\nSeven zero-network tests and twelve deterministic validation controls passed before the live profile tests. Both backends received six fresh scenarios in both execution modes, with two skills offered.\n\n'
    report += table(['Backend', 'Correct /12', 'Functional gate', 'Requests /96', 'Input tokens', 'Output tokens'],
        [[LABEL[m], v['correct'], 'PASS', v['requests'], v['input_tokens'], v['output_tokens']] for m, v in d['validation'].items()])
    robot_requests = sum(v['requests'] for v in d['models'].values())
    validation_requests = sum(v['requests'] for v in d['validation'].values())
    total_input = sum(s['input_tokens'] for v in d['models'].values() for s in v['summary'].values()) + sum(v['input_tokens'] for v in d['validation'].values())
    total_output = sum(s['output_tokens'] for v in d['models'].values() for s in v['summary'].values()) + sum(v['output_tokens'] for v in d['validation'].values())
    report += f'\nNew campaign total: **{robot_requests} robot inference requests + {validation_requests} validation requests = {robot_requests + validation_requests} requests**, **{total_input:,} input tokens** and **{total_output:,} output tokens**. Validation and robot limits remain separate; the combined ceiling was1,478. Unit tests, deterministic controls, metadata queries and explicit unload requests generated no model completions. The earlier48-request diagnostic is a separate completed study, not an uncounted part of this rerun.\n'
    report += '\nThe frozen **functional** gate required at least one healthy complete SUCCESS loop in each execution mode plus all safety, budget and trace checks. It did not require all movement, fault or recovery decisions to succeed. Both passed via healthy inspection; Granite failed both healthy movement validation cells. This gate demonstrated usable integration, not high task reliability. The following table preserves every outcome.\n\n'
    vr = []
    for m, v in d['validation'].items():
        for r in v['cases']:
            vr.append([LABEL[m], r['fixture']['id'], r['condition'], r['correct'], r['world']['writes'],
                r['expired_fault_exercised'], r['inference']['calls']])
    report += table(['Backend', 'Fresh case', 'Mode', 'Correct', 'Writes', 'Expiry exercised', 'Calls'], vr)
    report += '\nValidation limitation: the fresh mock checker tests skill, accepted status, world state and safe writes; it does not require an ineffective-write command actually to be attempted. Llama primitive `write_no_effect` was counted correct with no write, so that cell is **not evidence of detecting a dispatched command failure**. The main Gazebo scorer retains its stronger fault-exercise and expected-dispatch requirements. Stale-evidence cases record whether expiry was actually injected; accepted fresh-evidence reporting remains enforced by the unchanged validator.\n'
    report += '\n## Implementation and configuration\n\n'
    report += '''The new reusable opt-in module is `rosa-research/src/rosa_backends/tool_contract_ollama.py`. It appends model-native calling instructions and the **current bound schemas** as a system message on every request. It does not mutate conversation history, retain obsolete bound schemas, select skills, invent expected outcomes, alias malformed arguments, retry robot writes or weaken reporting. The original backend remains available unchanged. The profile supports the two tested model families and rejects conflicting streaming requests.

`native-schema-v1` explicitly enforces HTTP `stream=false`. Llama receives its documented `name`/`parameters` format; Granite receives its native `<|tool_call|>` list guidance. These are family-specific serialization instructions around a common semantic tool contract. Global Ollama templates were not edited. Existing SDK argument normalization remains assistance from the combined software stack, not raw-model schema competence.

Hardware: lab RTX 4080 SUPER (16,376 MiB VRAM), Ubuntu host, isolated Ubuntu 24.04 container with ROS 2 Jazzy, CPU-rendered Gazebo UR5e, project-local Ollama 0.40.6. Both installed models are 8B Q4_K_M; exact digests, locked dependencies, model templates and original source are in the referenced evidence. Full hardware provenance is retained; these are not the historical laptop trials or a fresh hosted Sol run.

Serving: 8,192-token context, maximum 1,024 output tokens/call, temperature 0, seed 42, one loaded model and serialized simulator access. No additional reasoning mode was enabled. Task bounds: eight model calls, 2,048 observed output tokens, 360 seconds, ten native operations, sixteen tool attempts, three corrections, one movement maximum. Robot batches: 640 ordinary requests plus three narrow HTTP retry-reserve requests/model, eight-hour backend window. Fresh validation: separate 96-request ceiling/model. All extra calls, corrections and returned tokens count. No provider consent or hosted inference was involved.

LangChain response caching was disabled. That does not establish that Ollama prompt-prefix/KV reuse was disabled; a per-request cached-token count was not recorded.

'''
    report += table(['Model tag', 'Frozen installed digest'], [[m, digest] for m, digest in d['model_digests'].items()])
    report += '\nFrozen baseline provenance (runtime imports the archived source, not mutable repository working trees):\n\n'
    report += table(['Repository', 'Recorded baseline revision'], list(d['frozen_baseline_source_commits'].items()))
    report += '\n## Actual transport, parser assistance and timing\n\n'
    timing = []
    for m, v in d['models'].items():
        t = v['timing_and_adapter']; totals = t['recorded_ollama_totals']
        timing.append([LABEL[m], v['requests'], f"{t['generation_tokens_per_second']:.2f}",
            t['max_prompt_tokens'], t['schema_requests_after_tool_results'], len(t['argument_normalizations']),
            len(t['raw_parsed_call_differences']), f"{v['campaign_seconds']:.2f}", json.dumps(t['done_reasons'])])
    report += table(['Backend', 'Robot requests /643', 'Aggregate generated tok/s', 'Max prompt tokens',
        'Schema-bearing calls after tools', 'Argument normalizations', 'Raw/parsed name-count differences', 'Campaign s', 'Done reasons'], timing)
    operator_seconds = d['operator']['finished_unix'] - d['operator']['started_unix']
    report += f'\nThe full detached pipeline took **{operator_seconds / 60:.2f} minutes** through validation, controls, both robot batches and their reports (excluding the initial failed preparation and later offline report/download work).\n\n'
    report += table(['Backend', '80-trial campaign min', 'Sum of timed tasks s', 'Infrastructure retries /3'],
        [[LABEL[m], f"{v['campaign_seconds'] / 60:.2f}", f"{sum(s['total_seconds'] for s in v['summary'].values()):.2f}",
            v['campaign_budget']['infrastructure_retries']] for m, v in d['models'].items()])
    report += '\nThroughput is total generated tokens divided by total recorded Ollama eval duration; it is not complete-task throughput. Every actual HTTP request/response is retained and checked against its trace metadata. The raw API tool calls are already Ollama-parsed native calls, not unparsed model token text. The complete rendered/tokenized prompt after Ollama templating was not captured: schema checks prove actual HTTP system-message presence, not a token-level rendering audit. Argument differences and invalid parsed calls are listed in the independent JSON; do not credit SDK coercion to the LLM. `prompt_eval_cached_count` was not recorded.\n'
    report += '\n## Preservation, amendments and verification\n\n'
    report += f'''The initial deterministic inspection control failed **before any model request** because the new mock returned a float while the existing interface requires a Boolean. Its stopped source, freeze and failed control are preserved in `INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip`. Revision 1 changes only that mock return type, adds its regression check and uses a new output root. No live validation or rerun model result existed when this amendment was made; the profile, task wording, scorer and limits were unchanged. A separate launcher attempt before successful source transfer made no model calls and its log is retained. These were preparation errors, not model failures.

The completed campaign has **160 live robot attempts + 24 live validation attempts**, separate from **20 Gazebo controls + 12 deterministic validation controls**. Every completed attempt retained its local and persisted Phoenix audit. Independent verification matched **{d['new_archive_files']:,} new archive content hashes**, all **75 frozen source/configuration hashes**, model digests, ordered schedules, checkpoint/raw trial fields, physical request journals, actual wire records, token bounds, per-task dispatch limits and cleanup records. The original 69 source files were unchanged. Every pipeline step completed normally. No failed/completed trial was silently repeated.

Raw rerun archive SHA-256: `{d['raw_archive_sha256']}`.

Here, independent verification means a separate read-only reconciliation script checking raw archives rather than trusting the progress summary. It is not an external research replication or a substitute for human semantic review.

The raw archive includes frozen new source, unit/protocol logs, validation, model requests/responses, full traces, persisted audit records, controls, checkpoints and intermediate reports. The original lab archive supplies the unchanged baseline source and old results; both are included in the share package for reproduction. No weights, credentials or full runtime environments are bundled. Historical archives are immutable.

'''
    report += '\n## Contextual model comparison\n\n'
    context = []
    for m, modes in d['context_reference_original_lab'].items():
        for c, s in modes.items():
            context.append([m, 'original lab profile', c, f"{s['known_goal_correct']}/36", s['calls'], f"{s['mean_seconds']:.2f}"])
    for m, v in d['models'].items():
        for c, s in v['summary'].items():
            context.append([m, 'native-schema-v1', c, f"{s['known_goal_correct']}/36", s['calls'], f"{s['mean_seconds']:.2f}"])
    report += table(['Backend', 'Profile', 'Mode', 'Known-goal correct', 'Calls', 'Mean task s'], context)
    report += '\nThese profiles are not uniformly matched. The table is an engineering reference, not an intrinsic model leaderboard. The separately retained Qwen repeat scored 26/36 primitives and 28/36 macro, versus 27/36 and 28/36 in its first lab run. Historical Sol has fewer repetitions and a hosted execution environment; no new Sol trial was run or inferred here.\n'
    report += '\nFor the same known cells that both a rerun backend and the first lab Qwen configuration completed correctly:\n\n'
    qr = []
    for m, v in d['models'].items():
        for c, pair in v['qwen_context_paired'].items():
            for who, cost in pair['matched_success_costs'].items():
                qr.append([LABEL[m], c, pair['both_correct'], who, cost['calls'],
                    f"{cost['seconds']:.2f}", cost['output_tokens'], cost['native_operations']])
    report += table(['Rerun comparison', 'Condition', 'Both correct /36', 'Configuration', 'Calls', 'Task s', 'Output', 'Native'], qr)
    report += '\nThese are outcome-selected descriptive subsets with different integration profiles. They remove failed-task termination from that timing subset, but do not establish a fair isolated model effect or correctness equivalence. Full discordant counts are retained in JSON.\n'
    report += '\n## Conclusions and next decision\n\n'
    report += '''**Llama is now a viable additional experimental backend, with material remaining limitations.** Its macro score improved to28/36 and matched the first lab Qwen macro aggregate, but the two configurations succeeded on only20 shared known-goal cells: each succeeded on8 that the other failed. On those20 shared successes, Llama took28.70 s versus Qwen75.86 s, while using48 versus40 calls and48 versus41 native operations. Those are descriptive, outcome-selected comparisons under different profiles, not model equivalence or universal efficiency superiority.

**For Llama, the macro package has a useful observed trade-off:** seven additional known-goal passes,40.5% fewer calls and54.7% fewer output tokens, but only8.6% less all-attempt task time and more native work (99→112). On its21 matched successes, calls fell88→47 and native work50→44. Four macro SUCCESS reports still served the wrong user goal, and all four partial-command tasks failed. Keep these limitations visible rather than calling the backend reliable in general.

**Granite should not replace the current reference backend on this evidence.** Its macro score is9/36, and primitives5/36. Native tool calling is functional, but repeated schema errors, prohibited multiple-call batches, premature prose and wrong skill/goal selection remain. Native call names/counts survived parsing in the captured requests; no downstream parser loss explains these failures. The macro's lower call count (210→193) comes with more native work (63→119) and12 accepted wrong-goal SUCCESS reports versus9 with primitives. This is poor performance under the tested contract, not proof that Granite is inherently incapable of ROSA tasks.

Do not weaken the one-tool-per-turn rule, automatically substitute skills, or change frozen scoring to make these results look better. Any future contract/selection intervention needs a new prospective evaluation. Keep Qwen as the retained reference, Llama as an opt-in candidate, and Granite as a documented unsuccessful configuration for this workload; no default backend was switched by this study.

'''
    report += '''The previous zeros must remain described as failures of the tested model-plus-adapter configurations, not proof that these model families cannot operate ROSA. The present results quantify what the declared combined integration repair actually achieved, including any remaining decision, execution, feedback or reporting failures.

Choose a backend by verified known-goal completion **and** end-to-end task costs, not call count or rapid termination alone. Macros need an explicit correctness trade-off check; fewer calls do not compensate automatically for missed goals. Any stronger comparison requires fresh cases, matched serving profiles and predeclared decision criteria. Four repetitions of ten familiar families do not establish broad generalization, statistical independence, equivalence or physical-robot safety.

Keep the opt-in profile and frozen evidence available. Do not tune it repeatedly on these failures or overwrite the old study. G1's existing human-review and scorer/instrumentation gates remain unchanged; this authorized replication does not clear them. No new architecture, memory system, full JTVR, physical deployment or additional model study was launched.

Machine-readable details: [independent analysis](INDEPENDENT_RERUN_ANALYSIS.json). Raw data: [rerun archive](NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip). Retained preparation failure: [initial stopped attempt](INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip).
'''
    report += '\n## Complete robot-attempt ledger\n\nAmbiguous rows are marked PENDING even where the legacy regex returned pass or fail.\n\n'
    for m, v in d['models'].items():
        report += f'### {LABEL[m]}\n\n'
        report += table(['Cell', 'Outcome', 'Selected skill', 'Accepted status', 'Fault exercised', 'Calls', 'Input', 'Output', 'Task s', 'Native'],
            [[r['id'], 'PENDING' if r['case'] == 'ambiguous_goal' else ('PASS' if r['correct'] else 'FAIL'),
                r['selected_skill'], r['score']['accepted_report_status'], r['score']['injected_fault_exercised'],
                r['calls'], r['input_tokens'], r['output_tokens'], f"{r['seconds']:.2f}", r['score']['native_operations']]
                for r in v['trial_ledger']])
    (EVIDENCE / 'INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md').write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
