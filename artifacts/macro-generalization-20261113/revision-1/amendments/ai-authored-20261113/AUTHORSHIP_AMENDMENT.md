# G1-r1 amendment: AI-authored-case fallback

Date: **2026-11-13**. Authority: the project owner explicitly selected the
documented AI-authored-case fallback after reviewing the follow-up assessment.

## Adopted change

For **exploratory generalization study G1**, replace the requirement for at least
one third independently teammate-authored cases with an explicitly **AI-authored
case set**. This is a methodological amendment, not satisfaction of the original
independent-authorship requirement.

The current54 draft cases remain unchanged:16 dev,38 held-out-designated. All
are recorded as **Codex (AI)**. There are zero independently teammate-authored
cases. No teammate author, blind review, semantic-novelty review or inter-reviewer
agreement is claimed. The case-level author fields must remain accurate in any
later revision; an additional AI-authored case is not independent authorship.

This resolves the **authoring-policy gate** for proceeding under the fallback,
subject to the other stage gates. Earlier reports saying the original gate was
unmet were correct at their checkpoint and are preserved unchanged. They must
not be retrospectively relabeled as passing the original criterion.

## Required reporting label

Use the following label in every G1 result/report and its exported tables or
figure captions, if and when results exist:

**Exploratory generalization study G1 — AI-authored cases; no independent
teammate authorship or semantic-novelty review.**

Structured study/result metadata must include:

```json
{
  "case_authorship": "AI-authored",
  "independent_teammate_cases": 0,
  "independent_authorship_gate": "replaced_by_owner_approved_fallback",
  "independent_semantic_novelty_review": "not obtained"
}
```

The implemented harness and its case author are not independent. Case choice,
explicit allowlists, fixed numeric targets and template design can favor the
implementation. Template-group splitting and prospective freezing mitigate some
leakage; they do not restore independent authorship or establish broad
generalization. Keep these limitations in conclusions, including negative or
inconclusive outcomes.

## Scope and unchanged gates

This amendment authorizes the authorship fallback only. It does not confirm
thresholds, counts, suffix, resource ceilings, or a model campaign. No Stage1
controls, Sol dev, held-out run or selection probe is launched by it. No cases,
source modules, old reports, budgets or previous scores were changed.

The review also recommends two dev partial-write cases, a stated native-operation
ratio tolerance of±25% per depth, and scorer/observer-metering controls. Those
are separate design updates pending disposition; this amendment does not silently
add them or freeze their thresholds. Adding two dev cases would require updating
the count to18 and the ordinary cap to18x2x8=288, plus the proposed3 reserve=291.
The current16-case proposal remains256+3=259 until that change is adopted.

The optional near-duplicate catalogue is not adopted or run. The current probe
proposal remains3/5/10 skills with macro wording only. No extra request allowance
is created here.

All outputs remain local. No credential contents were accessed, no new login
was started, no model requests were made and no commit, push or upload occurred.

See [current G1 status](../../CURRENT_STATUS.md), the preserved
[revision report](../../README.md) and [threshold proposal](../../PREDICTIONS_AND_THRESHOLDS.md).
