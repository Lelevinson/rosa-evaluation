"""A1: independently recompute retained Stage 2 evidence; no live requests."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REV = ROOT.parent
OLD = REV / 'stage-2'
CONT = REV / 'stage-2-continuation-1'
WORKSPACE = REV.parents[3]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)

def main():
    sealed = {}
    for folder, name in ((OLD, 'stage2-manifest.json'), (CONT, 'continuation-manifest.json')):
        manifest = read(folder / name)
        receipt = read(folder / 'manifest-verification.json')
        assert receipt['pass'] and digest(folder/name) == receipt['manifest_sha256']
        for relative, expected in manifest['files'].items():
            assert digest(folder/relative) == expected, 'Sealed evidence changed: '+relative
        sealed[folder.name] = dict(files_verified=len(manifest['files']), manifest_sha256=digest(folder/name))
    rows = [read(p) for folder in (OLD, CONT) for p in sorted((folder/'trials').glob('*/result.json'))]
    assert len(rows) == 36 and len({r['id'] for r in rows}) == 36
    pairs = {}
    for row in rows:
        pairs.setdefault(row['case']['case_id'], {})[row['mode']] = row
    matched_ids = {key for key, pair in pairs.items()
                   if len(pair) == 2 and all(r['primary_pass'] for r in pair.values())}
    def costs(subset):
        result = {}
        for mode in ('primitives', 'macro'):
            group = [r for r in subset if r['mode'] == mode]
            calls = sum(r['inference']['calls'] for r in group)
            seconds = sum(r['task_seconds'] for r in group)
            result[mode] = dict(trials=len(group), primary_correct=sum(r['primary_pass'] for r in group),
                calls=calls, known_input_tokens=sum(r['inference']['known_input_tokens'] for r in group),
                known_output_tokens=sum(r['inference']['known_output_tokens'] for r in group),
                native_attempts=sum(len(r['actor_records']) for r in group), task_seconds=seconds,
                task_seconds_divided_by_calls=seconds/calls)
        return result
    all_costs = costs(rows)
    matched = costs([r for r in rows if r['case']['case_id'] in matched_ids])
    assert [all_costs[m]['calls'] for m in all_costs] == [60, 34]
    assert [matched[m]['calls'] for m in matched] == [59, 32]
    assert [all_costs[m]['known_input_tokens'] for m in all_costs] == [90425, 50552]
    assert [all_costs[m]['known_output_tokens'] for m in all_costs] == [1783, 1108]
    assert [matched[m]['native_attempts'] for m in matched] == [40, 40]
    assert [round(all_costs[m]['task_seconds'], 2) for m in all_costs] == [194.91, 111.35]
    failed = next(r for r in rows if r['id'] == 'G1r1-dev-012-primitives')
    failure_fields = {key: failed['score'][key] for key in ('selection_correct', 'execution_correct', 'goal_correct')}
    assert all(value is False for value in failure_fields.values())
    assert failed['inference']['infrastructure_failures'] == 0
    trace = read(OLD/'trials/G1r1-dev-012-primitives/phoenix-trace.json')
    stack_found = any('responses.py", line 44, in completed_response' in value for value in strings(trace))
    assert stack_found
    response_source = WORKSPACE/'rosa-research/src/rosa_auth/responses.py'
    assert digest(response_source) == read(OLD/'protected-before.json')['rosa-research/src/rosa_auth/responses.py']
    source_lines = response_source.read_text().splitlines()
    assert "if kind in ('error', 'response.failed', 'response.incomplete'):" in source_lines[40]
    assert 'raise SafeError(error_code(code, kind.replace' in source_lines[43]
    identical = {}
    for name in ('scoring.py', 'tracing.py', 'recovery.py', 'persisted_audit.py', 'authorization.py'):
        assert (OLD/name).read_bytes() == (CONT/name).read_bytes()
        identical[name] = digest(OLD/name)
    original_trial = (OLD/'runner.py').read_text().split('\ndef main():', 1)[0].rstrip()
    changed = original_trial.replace('remaining=28800-(time.monotonic()-campaign.started)',
                                     'remaining=campaign.remaining_seconds()')
    assert changed != original_trial
    assert changed == (CONT/'runtime_trial.py').read_text().rstrip()
    call_saving = 1-all_costs['macro']['calls']/all_costs['primitives']['calls']
    time_saving = 1-all_costs['macro']['task_seconds']/all_costs['primitives']['task_seconds']
    result = dict(date='2026-11-14', scope='Retrospective Stage 2 A1 addendum; no experiment changes',
        analyst='Codex', owner='Martin', independent_human_review='NOT_OBTAINED',
        retained_trials=36, matched_pairs=len(matched_ids), all_attempt_costs=all_costs,
        matched_success_costs=matched, failed_trial_score_fields=failure_fields,
        failed_trial_infrastructure_failures=failed['inference']['infrastructure_failures'],
        failure_surface='IN_STREAM_TERMINAL_ERROR_BRANCH; exact event type and original provider code NOT_RECORDED',
        failure_trace_location='rosa_auth/responses.py:44 completed_response; invoked at responses.py:145',
        http_status='NOT_RECORDED; retained exception is from stream parsing, not HTTP status handling',
        scorer_false_fields_interpretation='Recorded primary endpoint failures, not evidence of a wrong model decision',
        call_saving_percent=100*call_saving, task_time_saving_percent=100*time_saving,
        saving_difference_percentage_points=100*(call_saving-time_saving),
        helper_files_byte_identical=identical,
        sole_trial_executor_change='remaining=28800-(time.monotonic()-campaign.started) -> remaining=campaign.remaining_seconds()',
        executor_scope='Extracted trial executor only; separate campaign orchestration also differs and is retained.',
        original_integrity=sealed, new_model_requests=0, stage3_launched=False)
    (ROOT/'STAGE2_AUDIT_ADDENDUM.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    text = f'''# Stage 2 audit addendum (A1)

Date: **2026-11-14**. Analyst: **Codex**. Owner: **Martin**. Independent human review: **not obtained**.

This is a retrospective read-only audit, recomputed directly from all 36 retained `result.json` files.
No original file, score, retry criterion or frozen input was changed. No model requests were made.

## Reproduced results

| Measure | Primitives | Macro |
|---|---:|---:|
| All-attempt inference attempts | 60 | 34 |
| Inference attempts across 17 matched-success pairs | 59 | 32 |
| All-attempt known input tokens | 90,425 | 50,552 |
| All-attempt known output tokens | 1,783 | 1,108 |
| Matched-success native attempts | 40 | 40 |
| All-attempt measured task seconds | 194.91 | 111.35 |

Unknown usage on the failed call remains unknown, not zero. Both original manifests were verified:
192 original-segment files and 98 continuation files matched their hashes.

## More precise failure characterization

The persisted traceback for **G1r1-dev-012-primitives** reaches `completed_response()` at
`rosa_auth/responses.py:44`, called by `respond()` at line 145 while consuming parsed stream events.
The protected source hash still matches the original snapshot. This line raises from the branch
handling `error`, `response.failed` or `response.incomplete`. Thus the retained failure surfaced
inside stream processing, rather than as an HTTP-status exception. The exact event type, original
provider code and underlying cause were not preserved. No quota diagnosis follows from this.

The scorer recorded **selection_correct=False, execution_correct=False and goal_correct=False**.
Those recorded endpoint flags remain unchanged. Since no completed model output or native operation
preceded the interruption, they do not demonstrate a wrong model choice. The ledger also records
**infrastructure_failures=0**: that counter does not establish that no external failure occurred;
it is not a complete taxonomy of all possible stream failures. No reserve retry was used.

## Time and calls: close, not equal

Summed task seconds divided by charged calls are **{all_costs['primitives']['task_seconds_divided_by_calls']:.4f}**
for primitives and **{all_costs['macro']['task_seconds_divided_by_calls']:.4f}** for macros.
These are task-time/call ratios, including local overhead, rather than independently measured
provider serving latency. Call saving is **{100*call_saving:.4f}%** and task-time saving is
**{100*time_saving:.4f}%**, differing by **{100*(call_saving-time_saving):.4f} percentage points**.
The similar ratios are consistent with fewer calls explaining much of the observed time difference;
the savings are not exactly equal, and this arithmetic does not isolate a causal mechanism.

## Executor and helper consistency

The extracted per-trial executor differs in exactly one statement:

```text
remaining=28800-(time.monotonic()-campaign.started)
    -> remaining=campaign.remaining_seconds()
```

`scoring.py`, `tracing.py`, `recovery.py`, `persisted_audit.py` and `authorization.py` are byte-identical
across segments. This comparison concerns the trial executor and named helpers; the continuation
also has its separately retained campaign orchestration, launch and reporting files. It would be
incorrect to say the whole continuation implementation differed by just one line.

## Scope and current preparation status

This addendum sharpens the historical account without rescoring or changing the existing ZIP.
Stage 3 has **not launched**. Only A1 and a truncated beginning of A2 have been received from the
new prompt. Error-observability requirements and the remainder of the new launch gates are pending
the full text. The owner's run authorization is recorded; unperformed reviews are not attributed
to the owner as completed reviews.

See [machine-readable audit](STAGE2_AUDIT_ADDENDUM.json) and
[the combined results/problems report](../STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md).
'''
    (ROOT/'STAGE2_AUDIT_ADDENDUM.md').write_text(text, encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('retained_trials', 'matched_pairs', 'call_saving_percent',
        'task_time_saving_percent', 'saving_difference_percentage_points', 'failure_surface',
        'new_model_requests', 'stage3_launched')}, indent=2))

if __name__ == '__main__':
    main()
