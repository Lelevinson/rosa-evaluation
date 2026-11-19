# Assessment of the post-M5 ChatGPT/Claude discussion

Date: **2026-10-30**. Scope: read the complete supplied discussion, check its
factual claims against existing records, and assess proposed directions. Quoted
requests to commence phases are discussion material, not execution authorization.
No implementation, live inference, new experiment or publication was started.

**Verdict.** The final cautious agreement is reasonable: preserve M1–M5, make
the evidence available for outside inspection, and keep any M6 conditional.
However, several intermediate explanations overstate what the traces show.
The strongest observation concerns an existing commitment restriction, not proof
that a confirmation call improves goal selection.

The [complete received discussion](M5_POST_CLOSEOUT_DISCUSSION_RECEIVED_2026-10-30.txt)
is preserved unchanged. Exact decoded first-turn material is available as
[readable excerpts](../artifacts/macro-m5-20261027/external-discussion-20261030/RAW_FOUR_TRIAL_EXCERPTS.md)
and [structured data](../artifacts/macro-m5-20261027/external-discussion-20261030/raw-four-trial-excerpts.json).
All four source trace SHA256 hashes match the M5 extraction. The export includes
the shared system prompt and tool schemas, both condition messages, the first
two visible assistant outputs, the actual first tool response supplied in the
next input, and later rejection strings. These are decoded stored messages,
not newly reconstructed prompts or privileged access to model reasoning.

## 1. The main factual correction

The primitive runs did not select inspection and then switch skills. Both first
attempted `read_state` on `/ur5e_readiness` before selecting any skill. Their
**first visible assistant content already identifies `ur5e.park_right` as the
correct target**, before the rejection. The rejection is:

```json
{"code":"skill_selection_required","corrections_remaining":2,"details":{"available_skills":["ur5e.home","ur5e.inspect_readiness","ur5e.park_right","ur5e.stage_left"]},"rejected":true}
```

This enforces protocol order and repeats the already public catalogue. It does
not tell the model that inspection is the wrong user goal or supply a new answer.
On call two, both primitive runs select park_right. A later premature write is
also rejected pending a fresh prerequisite read; they eventually exercise the
injected partial movement and correctly report FAILURE. Their passing scores
mean correct handling of the fault, not physical attainment of the target.

Both macro runs instead select inspect_readiness first, acquire two read-only
sources, and **request park_right on their second model call**. That request is
rejected with `skill_already_selected`; the details say "Do not replay a workflow;
use observed feedback or stop." One run later reports accepted readiness SUCCESS;
the other ends on response length. Neither exercises the requested movement.

Consequently:

- "The same selection error occurred in both conditions" is inaccurate. A
  premature read is different from committing to a wrong capability.
- The primitive output does not show newly discovering the correct goal after
  feedback; its visible first response already names it.
- Both conditions share the one-selection rule. Macro execution is not uniquely
  subject to commitment; the observed paths reach that boundary differently.
- The generic rejection still contains procedural information. Calling its
  effect purely content-free resampling is also an untested explanation.

The system prompt and five tool schemas are identical, but the user-message
execution-condition sentence differs. Within each condition, repeated first
inputs and first visible content/tool name/arguments match under fixed serving
settings. Before any tool runs, wording is the strongest observed explanation
for the first-action difference. M4 compares mode plus its explanatory wording;
the condition effect on selection cannot be separated from condition wording.
Four records are two repetitions of one known case, not four independent task
formulations. The precise wording mechanism and generality are not isolated.
See the [follow-up clarification](M5_CONDITION_WORDING_CLARIFICATION_2026-10-30.md).

## 2. What this changes about possible recovery work

A blanket confirmation call is not the only candidate. In these records the
model already emits the corrective selection on its existing next call.
An optional future policy could examine allowing one requested change after
read-only work and before any write, rather than forcing another confirmation
turn on every task. That is a concrete candidate for economical correction.

This would change the single-skill invocation contract. It is not an implemented
fix or a demonstrated benefit. It would need shared permission checks, cumulative
budgets that never reset, task/evidence scoping after a goal change, rejection
after any dispatched or uncertain write, and preserved no-replay guarantees.
It might recover some cases and break others; it would not help a wrong selection
that is followed directly by an accepted report with no attempted correction.
Extra native work and fresh verification must be counted.

The macro sequence is compatible with inspection being used as a preparatory
step before movement, but its first response contains no explanatory prose.
Later model explanations cannot establish its original internal intention.
Do not convert that possibility into a causal claim.

This candidate is narrower than a general planner and more directly grounded in
the observed rejected requests than an unconditional confirmation layer. It is
still only a possible extension, requiring its own decision and fresh protocol.

## 3. Cost arithmetic is correct, but illustrative

Holding all other behavior fixed and adding calls to every 20-task condition:

| Added macro calls per task | Sol call reduction versus primitives | Qwen call reduction versus primitives |
|---|---:|---:|
| 0 | 44.1% | 41.8% |
| 0.5 on average | 29.4% | 30.8% |
| 1 | 14.7% | 19.8% |

These are arithmetic scenarios, not measured recovery performance. A changed
policy can add or remove later retries, tokens, latency and robot operations.
A 0.5-call allowance is a proposed engineering target, not an empirical law.
Any future rule should specify correctness preservation/recovery and acceptable
overhead before observing results, without choosing thresholds to fit M4.

Known input tokens fell 48.9% for Sol and 49.1% for Qwen. Reduced context accumulation
is a plausible contributor, but the totals alone do not isolate that cause.
No dollar, energy or pure generation-speed saving was measured.

## 4. Separate explicit-task failures from ambiguity

Seven of Qwen's eleven failed trials concern explicit movement-related requests;
four concern the deliberately ambiguous family. Of the five accepted wrong-goal
readiness SUCCESS reports, four are ambiguous cases and one is an explicit
movement-related case. The other six failures terminate in errors. Neither
"eleven false successes" nor "all eleven are disputed ambiguity" is supported.

The explicit category includes four missing-prerequisite trials. Correct behavior
there was to withhold movement and report UNKNOWN about the requested movement
task. A fix must not improve a movement count by commanding an arm under unknown
prerequisites. Outcome scoring must retain the intended conservative behavior.

The suggested sensitivity table can be computed without rerunning anything:

| Scoring view | Sol primitives | Sol macro | Qwen primitives | Qwen macro |
|---|---:|---:|---:|---:|
| Frozen criterion | 20/20 | 20/20 | 15/20 | 14/20 |
| Exclude ambiguity family | 18/18 | 18/18 | 15/18 | 14/18 |
| Apply owner's submitted labels only to ambiguity | 18/20 | 18/20 | 17/20 | 16/20 |

The last row also fails the clarification responses, rather than only giving
Qwen extra passes. It is an explicitly post-hoc label scenario using Martin's
actual submissions. It does not prove that inspection fulfilled the unspecified
intent, change frozen scores, establish a fair new model ranking, or demonstrate
statistical reliability loss. The observed macro-minus-primitive gap remains
one task for Qwen; that is not causal proof that macros generally harm Qwen.
The [calculation record](../artifacts/macro-m5-20261027/external-discussion-20261030/retrospective-label-sensitivity.json)
retains its method and source hashes.

## 5. Claims, trusted goals and controls

Keep "improve ROSA" as the project objective. The demonstrated result is reduced
LLM orchestration overhead relative to a repaired primitive ROSA reference, with
mixed correctness. A stock-ROSA comparison is needed for a broader upstream
superiority claim, not to make the current scoped comparison valid. That caveat
already appears in the report; it is not a newly discovered missing experiment.

Trusted application goals are not automatically cheating or outside this
framework-focused project. Goals naturally supplied by users or application
interfaces can support legitimate deterministic constraints, supplied equally to
comparison arms. Feeding the runtime hidden scorer labels or the expected skill
is a different matter and would invalidate a claimed natural-language selection
improvement. Application contracts also do not demonstrate improved underlying
LLM understanding. There is no reason to implement another goal layer now.

If a future study claims the causal value of informative feedback, it needs a
control capable of distinguishing message content from another decision turn.
If it only tests whether a bounded policy is a useful system configuration,
that narrower engineering claim may not require a full mechanism study. Choose
the question before adding experimental arms. A text-only replay probe would
still be a new, post-hoc diagnostic on known cases, not a passive trace review
or evidence that a change generalizes to new robot tasks.

## 6. What is already done and what remains optional

M5 already contains the forensic review. The new value here is making its raw
material directly readable and correcting external interpretations, not claiming
to discover the same mechanism again or rewriting a post-hoc note as preregistration.
The demo contains two presentation runs, one per backend; it is functional
demonstration evidence, not a repeated comparative reliability experiment.

An uninvolved teammate could still rate the eight cases under the frozen rule,
with labels withheld and prior exposure disclosed. Do not coach ratings toward
agreement. Martin's different preference remains preserved even if another
reviewer agrees with the original criterion.

The current local backups are restore-verified through evaluation be32a23 and
research b13df0f. The later recap commit ec42ee7 and this new assessment are not
implicitly included in that pinned snapshot. Off-machine protection remains
deferred by user choice; proposals for a drive/cloud copy do not override that.
No transfer or external communication occurred during this assessment.

The proposed Nov 6–8 decision, Nov 8–16 optional pilot and Nov 20 report freeze are
planning suggestions based on a late-November deadline assumed in the discussion.
They are not an approved schedule or automatic experiment launch. Actual course
requirements and deadline should govern any later choice.

**Recommended decision now:** preserve M1–M5; let reviewers inspect the exact
excerpts; retain the corrected claims and retrospective sensitivity illustration.
Keep M6 proposed and unauthorized. If later approved, it should test one clearly
specified policy on fresh, frozen cases in every comparison condition, including
correct inspections, correct movements, missing prerequisites and ambiguity.
It must have a clear correctness/cost decision rule and leave the existing final
deliverable independently usable. Additional development is optional, not
unfinished M5 work.
