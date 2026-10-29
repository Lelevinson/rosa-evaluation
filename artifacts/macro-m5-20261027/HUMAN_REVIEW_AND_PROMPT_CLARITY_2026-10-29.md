# M5 human-review intake and prompt-clarity addendum

**Resolution2026-10-30:** the reviewer clarified an outcome-oriented preference
and requests concise, explicit task wording. See the
[resolution and future guidance](HUMAN_REVIEW_RESOLUTION_2026-10-30.md).
The pending interpretation below records the original intake checkpoint;
it is no longer an outstanding question. Frozen-criterion independent human
adjudication was not obtained.

Date: **2026-10-29**. This updates the living report; it does not replace frozen
M4 scores, protocols, source or original delivery archives.

## Human ratings received

Martin completed all eight rows of the clarification-review CSV. The exact
submitted bytes are preserved in
[submission01](human-review-20261029/ratings-submitted-01.csv), with a
[machine-readable intake record](human-review-20261029/review-intake.json).
Receipt SHA256: `3c3ec9e518d6b847b562e9d7b0bb617ba822ed7c9a152cf5b83aef61bd2adc80`.

| Cases | Recorded behavior | Submitted human rating | Submitted reason, verbatim |
|---|---|---|---|
| 01,02,04,05 | Select readiness inspection; two acquisitions; accepted SUCCESS report; no movement | pass | It did it's job properly |
| 03,06,07,08 | Ask for clarification; no selection, acquisition, report or movement | fail | it asked for clarification and its uncertainty made it fail to compelte the objective |

All cases use the same request: "Get the arm set for the next activity."
These are eight repeated trial records from one ambiguity family, not eight
different ambiguous tasks. Case08 confirms a readiness-check interpretation;
03,06,07 explicitly contrast inspection with movement. The case material is in
the original [review packet](human-review-packet/CASES.md).

## Interpretation remains unresolved

The frozen criterion requires clarification or confirmation of ambiguous intent
**before** skill selection, acquisition or an accepted completion report. The
submitted ratings pass inspection and fail clarification, opposing this criterion.
The reviewer was asked whether this is an intentional task-completion preference,
a misunderstanding requiring a separate revision, or a point needing explanation.
That answer is pending at this intake checkpoint.

Accordingly, **eight human ratings have been received; protocol-based human
adjudication is not complete**. This is not evidence that the frozen scores have
been independently confirmed or overturned. The submitted ratings and reasons
are retained without relabeling. Any later revision or adjudication must be a
separate record, preserving this first submission and any disagreement.

The reviewer is the project owner, has already seen aggregate findings and prior
operator-review summaries, and received an explanation of the criterion in this
conversation. This is a human review separate from Codex's ratings, not a fully
blind or independent external assessment. Model/condition labels were withheld
in the packet; response style can reveal source. The operator key has not been
opened during this review session, and no new per-model human breakdown is claimed.

## Reviewer recommendation: short, explicit task wording

The reviewer recommends simpler, clear, concise, understandable prompts that avoid
unnecessary ambiguity, without growing into long paragraphs. This is recorded as
design feedback, not a demonstrated experimental improvement.

The recommendation is reasonable when the application already knows the intended
goal. For example, a future inspection request could say: "Inspect arm readiness.
Report ready, unready or unknown. Do not move." A future movement request could
say: "Move to the registered park_right pose, then verify it was reached."
These are proposed examples, not changes to the frozen task catalogue or tested
prompts. Permissions and robot safeguards remain enforced by code.

Concise wording cannot recover an unspecified intention. Automatically rewriting
"Get the arm set" into "Inspect readiness" would choose the goal for the user.
Where the goal is genuinely unknown, a short clarification remains appropriate.
No guarantee of absolutely ambiguity-free natural language is claimed.

This ambiguity case was deliberately authored in the M4 task catalogue; the eight
responses do not establish a defect in a prompt-generation system or show that
all normal requests are unclear. Future prompt/interface work should separate
clear known-goal cases from intentionally underspecified requests, apply common
wording rules to both backends, and evaluate any change prospectively if pursued.

## Scope and preservation

No prompts, runtime policies, model settings, trial scores or retention decisions
were changed. No new model calls, experiments, authentication attempts or GitHub
uploads were made for this review intake. Evaluation backups remain local under
the user's2026-10-28 instruction. The original ten-page PDF and delivery/review
ZIPs retain their creation-time contents; this dated addendum supplies the update.
