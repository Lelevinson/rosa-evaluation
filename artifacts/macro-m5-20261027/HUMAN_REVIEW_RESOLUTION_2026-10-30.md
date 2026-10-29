# M5 human-review resolution and future task wording

Date: **2026-10-30**.

## Reviewer interpretation

After submitting eight ratings, Martin clarified: "i feel like in the end th result
matters more" and "i want concise but clear". The reviewer objects to the clarity
of the request and prefers practical completion over clarification overhead.

The eight submitted labels and reasons are preserved exactly in
[submission01](human-review-20261029/ratings-submitted-01.csv). Four inspection
responses were rated pass and four clarification responses fail. The
[2026-10-29 intake](HUMAN_REVIEW_AND_PROMPT_CLARITY_2026-10-29.md) records the initial
criterion discrepancy; this resolution supersedes its pending-clarification status.

This closes the owner's feedback review as **outcome-oriented stakeholder
feedback**. It does not supply an independent human adjudication applying the
frozen clarification criterion. No revised human ratings were supplied or invented.
The original operator ratings, M4 scores and retention decisions are unchanged.
Protocol-based independent human adjudication remains not obtained; no further
reviewer or revised submission is currently scheduled.

The inspected task actually said "Get the arm set for the next activity."
The catalogue intentionally made this an ambiguous-intent case. Readiness
observations establish controller/joint-data readiness; they do not establish an
unspecified intended final pose or task. The owner's preference therefore does
not prove that an inspection completed the original intended goal. Conversely,
asking for clarification does not execute a movement; under this case's frozen
contract, clarification was the expected correct response.

The reviewer is the project owner and had prior aggregate-result exposure.
This is not a blind external validation or evidence of inter-reviewer agreement.
The disagreement in judging criteria is retained rather than converted into a
new success score. No new per-model human-performance claim is made.

## Future task-writing guidance

Use short, concrete requests when the application knows the goal:

- **Inspection:** "Check arm readiness. Report ready, unready or unknown. Do not move."
- **Movement:** "Move the UR5e to registered pose park_right, then verify it was reached."

Name the action and target; include only constraints that affect execution.
Keep wording common to both backends. Permissions, resource bounds and robot
safeguards remain enforced by the application rather than relying on prose.
These examples are proposed future wording, not tested interventions.

If the goal or target is missing, do not guess it. Ask one concise question such
as "Which registered pose should the arm move to?" Clearer wording can remove
avoidable ambiguity; it cannot recover information the user has not provided.

For future evaluation design, known-goal execution and intentionally ambiguous
requests should have separately reported outcomes and predefined criteria.
Outcome measures should distinguish verified execution from goal satisfaction
and from appropriate clarification. Do not remove ambiguity cases or redefine
their scores after seeing results. This review does not establish that clearer
wording improves Qwen; that would require a separate prospective comparison if
later authorized.

## Scope

The current user feedback establishes a direction for future task wording.
No prompt generator was rebuilt, no runtime or frozen prompts were changed,
and no new model calls or experiments were started. The original ZIPs and
ten-page PDF remain unchanged. Current Markdown reports link this dated update.
Evaluation backups remain local by the user's2026-10-28 instruction; GitHub
authentication or publication is a separate step.
