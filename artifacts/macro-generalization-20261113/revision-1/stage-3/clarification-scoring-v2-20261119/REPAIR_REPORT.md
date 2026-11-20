# G1 clarification-scoring repair completed

Date: **2026-11-19**. **First repair: COMPLETE for the reviewed v2 layer.**
No live trial, new OAuth authorization, robot operation or Git publication.

## What changed and why

The original clarification scorer uses a loose keyword/question regex. The old
separate review demonstrated six reachable semantic mistakes; four good dev
examples could not resolve that defect. The owner's instruction to handle the
first repair authorized the prospective amendment documented in
[AMENDMENT.md](AMENDMENT.md), implementation, zero-model validation and renewed
separate-model review. The second metadata amendment remains unapproved.

The new [analysis layer](adjudication.py) makes actual eligible human judgments
authoritative for ambiguous-request semantics, retaining the regex only as a
diagnostic. Without judgments, semantics are **PENDING_HUMAN_REVIEW**, never an
automatic pass, false score or infrastructure failure. NO fails, CANNOT_JUDGE
remains pending, and both YES require independent no-action and original runner
checks. Human approval cannot override skill selection/activity, native or tool
operations, reports, writes/dispatches, failed audits, errors, timeouts or the
original recovered-infrastructure rule. Invalid required evidence stops analysis.

The layer rejects duplicate, orphan, wrong-rubric, mismatched-content, incomplete
or ineligible supplied ratings. Ratings are bound to the exact full row, request,
response, activity and rubric. The existing four actual ratings were checked
against the exact issued transcript rendering and original submission bytes.
All reasons and original files are preserved. Synthetic labels in software tests
are explicitly named test fixtures and never counted as human evidence.

All scheduled work/costs stay visible. Pending semantics or unstarted results
withhold final campaign conclusions. The explicit bridge to old Boolean analysis
refuses unresolved semantics. Future orchestration must also check the authoritative
schedule with `summarize` before using projected rows; the bridge alone does not
check schedule completeness. Existing censoring, predictions and uncertainty
rules remain applicable. See [usage and trust boundary](USAGE.md).

## Validation

**Implementer checks: 15 test methods PASS**, including the six original regex
mismatches as regressions, malformed/missing evidence, both human rating columns,
wrong bindings, positive-rating action overrides, original runner gates, censoring,
cost retention, incomplete campaigns and real-review compatibility. See the
[log](development-validation/implementer-tests.log) and
[receipt](development-validation/VALIDATION_RECEIPT.json).

**Renewed independent review: PASS for the exact effective layer within its
documented trusted-input boundary.** The separate reviewer was configured as
GPT-6 Astra/high, with no inherited history. Runtime identity was not separately
attested. This is an actual separate AI review, not another human adjudication.

- First run: 65 newly authored cases, 63 expectations matched and 2 mismatches.
- Both mismatches were reviewer shared-reference construction errors: a later
  forbidden-repeat request mutated the earlier authorized-repeat test input before
  serialization. The scorer correctly rejected those serialized requests.
- The original inputs, expectations and failures are retained unchanged. Two
  separately copied corrected repeat constructions both matched (2/2).
- No substantive scorer defect was found. Do not call this 65/65 or 67/67 matched.
- All 66 recorded review inputs remained byte-identical. No operator case edits
  or source repairs were made during the review.

Read the [independent report](independent-review/REVIEW_REPORT.md) and
[clearance](independent-review/CLEARANCE.json) for coverage, original discrepancies
and exact source hashes. This clearance does not relabel the old regex review
as passed and is not proof of complete scorer correctness.

## Development results and preservation

The separately labeled [retrospective overlay](development-validation/RETROSPECTIVE_DEV_OVERLAY.json)
contains 36 retained dev attempts: 35 evaluable passes, 1 pre-output infrastructure-
censored attempt, no pending human judgments. The four real reviewed examples
already passed the original dev scoring; their outcomes are not newly improved.
All 32 nonambiguous records retain their scores. V2/V3 prediction point metrics
match the prior development inputs; no prediction is adjudicated from these data.

| All retained attempts | Primitives | Macro |
|---|---:|---:|
| Trials |18|18|
| Physical model requests |60|34|
| Known recorded input tokens |90,425|50,552|
| Known recorded output tokens |1,783|1,108|
| Incomplete-usage records |1|0|
| Native operations |40|46|
| Measured task seconds, sum |194.910188|111.350612|

These costs are unchanged. The older 40-versus-40 native comparison uses matched
pairs, a different denominator. Missing usage is not estimated. No new claims
about model reliability or framework efficiency follow from this scoring repair.

Before final living-document maintenance, **all 3,726 snapshotted prior files were
unchanged**. Old experiments, raw outputs, human submissions, previous reviews,
protected source, prompts, cases, model settings, budgets and retry rules remain.
The old protection guard's existing master-README mismatch is retained as FAIL;
authorized mutable-document updates are not falsely described as a clean old
guard pass. A later freeze must explicitly disposition its documentation scope.

## Limits and remaining work

The generic review validator trusts documented organizer input. It does not
authenticate a human identity, prove lack of prior exposure or fetch original
bytes behind supplied hashes. Current actual intake verifies retained bytes;
future submissions need equivalent real intake and a new blinded review. Models
must never supply organizer review bundles. Program-owned evidence remains
trusted under the unchanged public-interface boundary; synthetic forged-record
limitations are retained in the independent report. No runtime replay of those
forged states is claimed.

**G-e: PASS for this reviewed v2 layer; historical legacy clearance remains FAIL.**
**G-f: PASS on Levinson's submitted ratings and eligibility self-declaration.**
**G-c: still BLOCKED.** The owner must choose between accepting/test-validating
reduced error metadata with protected code unchanged, or approving the minimal
protected hook to capture the original required fields. This repair selects
neither. G-g/G-h still require upstream clearance, documentation protection-scope
disposition, a valid freeze and fresh preflight, followed by separate held-out
launch authorization. No held-out result is present or implied.
