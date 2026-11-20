# Stage 2 audit addendum (A1)

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

Summed task seconds divided by charged calls are **3.2485**
for primitives and **3.2750** for macros.
These are task-time/call ratios, including local overhead, rather than independently measured
provider serving latency. Call saving is **43.3333%** and task-time saving is
**42.8708%**, differing by **0.4625 percentage points**.
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
