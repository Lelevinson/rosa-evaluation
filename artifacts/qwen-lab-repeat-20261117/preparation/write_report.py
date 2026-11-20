"""Write a transparent current lab reference report from verified aggregates."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EVIDENCE = BASE / 'evidence'


def main():
    data = json.loads((EVIDENCE / 'INDEPENDENT_REPEAT_ANALYSIS.json').read_text())
    summary = data['summary']
    rows = []
    for run in ['lab_run_1', 'lab_run_2']:
        for condition, s in summary[run].items():
            rows.append(f'| {run} | {condition} | {s["known_goal_correct"]}/{s["known_goal_n"]} | '
                f'{s["calls"]} | {s["input_tokens"]:,} | {s["output_tokens"]:,} | '
                f'{s["mean_seconds"]:.2f} | {s["median_seconds"]:.2f} | {s["native_operations"]} | {s["invalid_attempts"]} |')
    changes = []
    for condition, s in data['same_lab_paired_comparison'].items():
        changes.append(f'| {condition} | {s["both_correct"]} | {s["first_only_correct"]} | '
            f'{s["repeat_only_correct"]} | {s["both_wrong"]} |')
    families = []
    for family in summary['lab_run_1']['primitives']['families']:
        if family == 'ambiguous_goal':
            continue
        values = []
        for run in ['lab_run_1', 'lab_run_2']:
            for condition in ['primitives', 'macro']:
                f = summary[run][condition]['families'][family]
                values.append(f'{f["correct"]}/{f["n"]}')
        families.append('| ' + family + ' | ' + ' | '.join(values) + ' |')
    costs = []
    for condition, s in data['same_lab_paired_comparison'].items():
        a, b = s['matched_success_costs']['first'], s['matched_success_costs']['repeat']
        costs.append(f'| {condition} | {s["both_correct"]} | {a["calls"]} / {b["calls"]} | '
            f'{a["seconds"]:.2f} / {b["seconds"]:.2f} | {a["native_operations"]} / {b["native_operations"]} |')
    a = data['audits']
    t = data['timing']
    report = '# Qwen lab evaluation and repeatability report\n\nDate: **2026-11-17**.\n\n'
    report += ('The lab Qwen configuration is the current reference for the lab local-model comparison. '
        'Both completed lab runs are reported; the second is a replication rather than a replacement selected for a better result. '
        'This report does not revise historical M4 or its matched hosted-Sol comparison.\n\n')
    report += ('## What ran\n\nTwo lab runs of **80 Qwen trials each**, with ten known M4 families, four repetitions '
        'and two conditions: model-managed primitives and a bounded macro. Each run has 40 attempts per condition. '
        'Four ambiguous attempts per condition remain **pending human semantic review**. Known-goal correctness therefore '
        'uses **36 per condition**, while cost totals and means include all 40 attempts. '
        'Correctness includes appropriate FAILURE or UNKNOWN handling when required, not only successful physical movement. '
        'The underlying legacy ambiguity regex remains diagnostic and is not treated as human adjudication.\n\n')
    report += f'Hardware: **{data["hardware"]["gpu"]}**. Model: `qwen3.5:9b`, Q4_K_M, digest `{data["model"]["digest"]}`. '
    report += ('The existing identical model was reused; no duplicate model was downloaded. The original 62-file M4 execution snapshot '
        'and frozen lab adapter were imported unchanged. The second run uses a new 74-file source/config freeze and separate Phoenix project/output paths.\n\n'
        'Serving settings: Ollama 0.40.6, context 8,192, maximum output 1,024 per call, observed output allowance 2,048 per task, '
        'temperature 0, seed 42, thinking off, streaming off, application response cache off. The existing server uses one parallel request '
        'and one loaded model. Application caching off does not establish absence of internal prefix/KV reuse; cached-token counts are not recorded.\n\n'
        'Bounds remain eight model calls, ten native operations, sixteen tool attempts, three corrections, 360 seconds and at most one '
        'movement dispatch per task. The repeat ceiling is 640 ordinary requests plus three narrow HTTP retry reserve and an eight-hour backend window. '
        'Only HTTP 502/503/504 can receive the existing one retry per logical call; generic errors and response-length failures cannot. '
        'There were no hosted requests and no changes to model prompts, schema acceptance, scoring, retry eligibility or robot guards.\n\n')
    report += '## Observed results\n\n'
    report += '| Run | Condition | Known-goal correct | Calls | Input tokens | Output tokens | Mean task s | Median task s | Native ops | Invalid attempts |\n'
    report += '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n' + '\n'.join(rows) + '\n\n'
    report += ('Task times are measured trial wall time, including framework and native work, rather than generation throughput alone. '
        'Simulator startup, intertrial preparation, deterministic controls and installation are excluded from those means. '
        'Lower calls or time do not establish useful efficiency if a requested task was not correctly completed.\n\n')
    report += '| Condition | Correct in both runs | First only correct | Repeat only correct | Incorrect in both |\n|---|---:|---:|---:|---:|\n' + '\n'.join(changes) + '\n\n'
    report += 'Each paired cell has the same family, repetition and condition. This records behavioral repeatability, without assuming exact repeatability from a fixed seed.\n\n'
    report += 'The verified changed-cell records are:\n\n'
    for item in data['changed_cell_evidence']:
        first, second = item['first'], item['repeat']
        report += (f'- `{item["case"]}`, repetition {item["repetition"]}, {item["condition"]}: '
            f'correct {first["primary_pass"]} -> {second["primary_pass"]}; '
            f'selected skill `{first["selected_skill"]}` -> `{second["selected_skill"]}`; '
            f'accepted report {first["accepted_report_status"]} -> {second["accepted_report_status"]}; '
            f'calls {first["calls"]} -> {second["calls"]}.\n')
    report += ('\nIn these three cells the selected movement skill remained `ur5e.park_right`, and the injected fault '
        'was actually exercised. The differences concerned completing a valid outcome report. '
        'The repeat partial-command r1 case exhausted eight calls without an accepted report; '
        'ineffective-command r4 stopped on response truncation without an accepted report; '
        'partial-command r4 obtained an accepted, evidence-grounded FAILURE in the repeat. '
        'These are not evidence of three new initial skill-selection mistakes. Full answers and validation errors '
        'are retained in `changed_cell_evidence` in the independent analysis.\n\n')
    report += '| Known-goal family | First primitives | First macro | Repeat primitives | Repeat macro |\n|---|---:|---:|---:|---:|\n' + '\n'.join(families) + '\n\n'
    report += '## Costs on identical successful cells\n\n'
    report += '| Condition | Cells correct in both runs | Calls first / repeat | Seconds first / repeat | Native ops first / repeat |\n|---|---:|---:|---:|---:|\n' + '\n'.join(costs) + '\n\n'
    report += 'Within the second run, costs for cells successfully completed in both architectures are:\n\n'
    for c, s in data['within_repeat_matched_success'].items():
        report += f'- {c}: {s["trials"]} tasks, {s["calls"]} calls, {s["seconds"]:.2f} seconds, {s["native_operations"]} native operations.\n'
    report += ('\nThe complete machine-readable analysis includes tokens, correctness transitions and family counts. '
        'The earlier multi-model report remains authoritative for Ministral, Llama and Granite; they were not rerun here.\n\n')
    report += '## Audits, limits and actual inference timing\n\n'
    report += (f'The repeat completed **80/80 live trial audits** and **20/20 deterministic controls**, with '
        f'**{a["live_persisted_spans"]:,} persisted live spans**. All {a["source_hashes"]} frozen source/config hashes matched; '
        'the original 69-file freeze remains intact. Raw trial files match checkpoints, persisted Phoenix records match local audits, '
        'and downloaded ZIP integrity and every manifest hash passed independent verification. '
        f'The repeat used **{data["requests"]} physical requests**, matching traced model calls and the request journal. '
        'Token usage was complete; every checked task stayed inside call/output/native/dispatch/time bounds. '
        'Simulator cleanup completed successfully and no dispatch violation was recorded.\n\n')
    report += (f'Final audited LLM spans retain actual Ollama durations: aggregate generation throughput '
        f'**{t["generation_tokens_per_second"]:.2f} tokens/s**; largest prompt **{t["max_prompt_tokens"]:,} tokens**; '
        f'completion reasons `{json.dumps(t["done_reasons"], sort_keys=True)}`. '
        f'Total backend campaign elapsed time was **{t["campaign_seconds"] / 60:.2f} minutes**. '
        'This is separate from mean task time. Early `_generate` journal metadata may be empty because LangChain merges generation metadata later; '
        'the analysis reads the final spans rather than substituting zero durations.\n\n')
    report += ('A zero outer-exception count does not mean there were no errors: ROSA can return an error as answer text. '
        'Structured unsupported-success counters also do not audit every free-text claim. Both limitations are retained in the original study and '
        'in the machine-readable repeat aggregates. Fault handling should be interpreted alongside whether the injected command was actually attempted.\n\n')
    if 'historical_laptop_m4' in summary:
        report += '## Relationship to historical laptop M4\n\n'
        report += ('The historical laptop configuration used an RTX 4050 Laptop GPU with 6 GB VRAM and partial CPU offload, '
            'rather than the lab RTX 4080 SUPER with 16 GB. Historical M4 had two repetitions and 40 Qwen trials total; '
            'each lab run has four repetitions and 80. Its published 15/20 primitives and 14/20 macro legacy totals remain unchanged. '
            'Those totals include ambiguity cases; they are not directly interchangeable with the lab report\'s known-goal denominator.\n\n')
        for c, s in summary['historical_laptop_m4'].items():
            report += f'- Historical {c}, known-goal subset: {s["known_goal_correct"]}/{s["known_goal_n"]}; all-attempt mean {s["mean_seconds"]:.2f} seconds, {s["calls"]} calls over {s["attempts"]} attempts.\n'
        report += '\nRestricting the repeat to the historical case/repetition/condition cells gives:\n\n'
        report += '| Condition | Shared known-goal cells | Historical correct | Repeat correct | Both correct | Historical only correct | Repeat only correct |\n|---|---:|---:|---:|---:|---:|---:|\n'
        for c, s in data['historical_paired_comparison'].items():
            report += f'| {c} | {s["common_known_goal_cells"]} | {s["historical_correct"]} | {s["repeat_correct"]} | {s["both_correct"]} | {s["historical_only_correct"]} | {s["repeat_only_correct"]} |\n'
        report += ('\nThe new lab observations can establish how this lab setup performed, but do not isolate a causal hardware effect. '
            'Serving environment, system state, execution timing and repetition count differ. No fresh Sol run was made, '
            'so this cannot replace the earlier paired Sol/Qwen comparison with a purported same-environment comparison.\n\n')
    report += ('## Interpretation and next steps\n\n'
        'These are repetitions of ten already-seen families, not 160 independent new task designs or held-out generalization evidence. '
        'Temperature zero and a fixed seed do not remove all inference or simulator nondeterminism. The evidence can show where '
        'correctness, calls and timing were stable or changed, but does not establish broad model parity, statistical equivalence, '
        'or physical-robot safety. Both conditions use the same previously repaired ROSA framework, not a stock-ROSA comparator. '
        'Execution mode and the condition instruction sentence remain bundled, so a selection difference cannot be attributed to execution code alone. '
        'The lab Qwen setup remains the current reference; retain both runs and the family-specific limitations '
        'rather than replacing failures or selecting a favorable repetition.\n\n'
        'Use the verified aggregates to decide whether a specific error deserves a separately authorized prospective intervention. '
        'No prompt repair, automatic report repair, new model study or G1 held-out launch is authorized by this repeat. '
        'G1 human/scorer/observability gates remain unresolved.\n\n'
        '## Files and cleanup\n\n'
        'The raw repeat ZIP, independent analysis and verification accompany this report. The original full lab evidence ZIP '
        'is also required to reproduce the imported frozen runtime; the share bundle includes it. Earlier reports and archives are unchanged. '
        f'Repeat raw ZIP SHA-256: `{data["raw_archive_sha256"]}`.\n\n'
        'The old misplaced `/media/naeem/marvel proj` and `/media/naeem/d/marvel proj` paths were already absent. '
        'A targeted inventory found no project-named leftovers in `/tmp`, `/var/tmp` or `/home/naeem`. '
        'Useful Ollama identity/cache files, SSH/VPN configuration, installed models, shared tools and Docker runtime dependencies were preserved. '
        'No unrelated project directories were deleted. The project itself and all repeat outputs are under `/media/naeem/d1/marvel proj/`.\n')
    (EVIDENCE / 'QWEN_LAB_REPEAT_COMPARISON_REPORT.md').write_text(report, encoding='utf-8')
    print('Report written')


if __name__ == '__main__':
    main()
