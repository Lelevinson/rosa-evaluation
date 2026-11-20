# G1 — Stage 0 progress and decision report

Date: **2026-11-13**. Status: **STOPPED_INTERFACE_INCOMPATIBLE**.

**Stage 0 planning is prepared, but its gate is not passed. No experiment has
started.** The exact proposed acquisition study needs capabilities that the
current public module does not expose. The prompt explicitly requires stopping
and reporting that outcome instead of patching the module. That stop was obeyed.

This is a new, separate **exploratory generalization study G1**. It does not
replace or revise M1-M5, M4, the timing probe or Phase1. All outputs are contained
here. Earlier project reports/master files were not edited to insert G1, because
the new instruction restricts all outputs to this directory. Use this README as
the current G1 progress record.

## What was completed

| Stage 0 item | Actual state |
|---|---|
| Requested instructions retained | Original attachment copied byte-for-byte to REQUEST_RECEIVED.txt |
| Source/public-API compatibility assessment | Complete static inspection; required-source-change stop reached |
| Domain/skill proposals | Two distinct mock domain designs, six skill proposals each; no new world instantiated |
| Skill/depth and primitive-call table | Complete; distinguishes intended paths from actual API capabilities |
| Draft case list, authors and split | 96 AI-authored cases:32 dev,64 held-out-designated; template groups separated |
| Budgets/resource ceilings | Computed proposals; not confirmed |
| Predictions/thresholds | Proposed explicit defaults; not confirmed; P1-P4 were absent from the supplied text |
| Pre-run planning note/hash | Recorded as a proposal checkpoint, not a runnable final experiment freeze |
| Preservation | 2112 existing files checked unchanged after preparation |
| New source implementation or live activity | None:0 model requests,0 robot commands, no credential access/login |

## Main finding: the proposed depth comparison is not yet supported

An existing inspection can acquire1,2,4 or6 separately metered sources. But its
primitive `read_state` always acquires **all** the selected source groups in one
call. It does not expose one-source/subset acquisition. Therefore the current
nominal primitive inspection path is **three model calls at every depth**:
select, read, report. Native depth is not model-decision depth.

The state-change macro has a fixed read-target / conditional-write / fresh-check
path. `StateSkill` declares one numeric target node and no prerequisite-source
contract. A p3 guarded write anchor cannot be represented through this unchanged
public API. Hiding three reads inside one transport call would break the intended
metering/comparison rather than solve it.

This is **Against P5 for the exact requested G1 contract**, not evidence that a
mobile-base domain itself cannot reuse the module. A simple numeric mobile pose
and Boolean readiness checks are consistent with the existing API in principle;
no live second-domain performance was measured. See the
[required interface/design decision](REQUIRED_INTERFACE_CHANGE.md) and
[source evidence with line references](source-compatibility.json).

There is another unresolved contract issue: M4's full query hard-codes eight
model calls, ten native operations and joint tolerance in radians. G1 requests
variable limits and mobile units. Exact system/RULES/condition sentences are
retained, but a changed budget/unit suffix has not been approved or applied.

## Proposed cases and their limitations

| Split | Ladder | Write anchors | Missing prerequisite | Ambiguous | Fault | Total |
|---|---:|---:|---:|---:|---:|---:|
| Dev | 16 | 8 | 2 | 2 | 4 | **32** |
| Held-out-designated | 40 | 12 | 4 | 4 | 4 | **64** |

Held-out ladder cells have five cases/domain/depth. Each write anchor has three
held-out cases. Non-depth cases include unsafe/missing prerequisites, partial or
ineffective execution, unavailable outcome sources and ambiguous intent. Each
case records a request, template group, proposed target, private initial values,
fault recipe, expected status/dispatches, and budget. Those recipes are proposed
specifications; they have not been implemented or shown solvable.

**All96 cases are authored by Codex (AI).** Independent teammate authorship and
review were not obtained. The original one-third independent-author criterion
is unmet. No reviewer, teammate contribution or blind validation was invented.
This reduces protection against favorable case selection.

Template groups do not cross the dev/test split: six dev groups and fourteen
held-out groups. The held-out ladder has only **five linguistic template
clusters**, shared across depths/domains. Ten cases per depth are not ten
independent templates; only large effects will be visible. No exact request
matched a string literal in the M4 design file, but semantic template novelty
has not been independently reviewed. These drafts are not an untouched external
test set. No runtime solvability, token-length or outcome claim is made.

Ambiguous cases retain M4's clarification criterion as primary. A separate
inspection-acceptable sensitivity view is proposed; neither enters depth
analysis. Fresh grounded evidence and fulfilling the intended goal remain
separate. A truthful readiness SUCCESS does not establish a movement outcome.

## Budget and ceiling summary

For the intended design, each task gets nominal maximum primitive calls+4,
nominal native depth+4 operations, twice its call limit in tool attempts,
three corrections, at most one dispatch and360 seconds. The same limits apply
to both conditions. Inspection budgets are7/8/10/12 calls for d1/2/4/6;
write-anchor budgets9/11 for p1/3. Ambiguity gets a proposed five-call limit.
Qwen's original A serving profile and2048 observed-output/task gate are retained.

| Batch | Trials | Ordinary logical cap | Separate reserve | Physical ceiling |
|---|---:|---:|---:|---:|
| Sol dev | 64 | 608 | 6 | **614** |
| Sol held-out | 128 | 1196 | 12 | **1208** |
| Qwen held-out | 128 | 1196 | 12 | **1208** |

These are proposed worst-case request envelopes, **not expected consumption or
approved launches**. M4's106/323 Sol count does not reveal remaining account
quota:323 was a local cap. Current Sol quota and current protected authorization
availability are **not recorded/not checked**. No new login was attempted.

M4's HTTP502/503/504 eligibility, exclusions, one retry/logical call and separate
physical reserve are retained in the proposal. No agent, robot command or
complete failed trial is replayed. The optional selection probe would cost195
requests/model with one fixed condition sentence or390/model with both; that
choice is unresolved. See [full formulas and reservations](BUDGETS_AND_CEILINGS.md).

## What was not completed, and why

- The arm mock candidate is the existing isolated
  `experiments.reliability_v2.cases.MockTransport`. Its old mock oracle copies
  the actor object's state; a distinct observer transport/state/record stream
  has not been established. Claiming independent-observer validation would be
  incorrect. A suitable separated harness is described but not implemented.
- The mobile-base runtime/observer is not implemented. Its proposed units,
  sources and fault kinds differ from the arm: metres, localization validity,
  map revisions/leases, battery fraction and translation-versus-heading faults.
- No complete scripted primitive/macro controls, fault-exercise controls,
  local trace audits or persisted Phoenix span-ID audits ran. Those are Stage1
  work, and the Stage0 source/API stop prevents advancement.
- No Sol dev, held-out run, Qwen run or catalogue probe started. No current
  provider quota value or runtime/token estimate was invented.
- No final runnable experiment freeze was made. This package seals the Stage0
  proposal and its negative feasibility finding only. Thresholds, budget suffix,
  ceilings and case limitations remain subject to review.

## Recommendation and next decision

**Prefer a narrower design using the existing module**, rather than adding an
acquisition-policy layer under deadline pressure. Keep second-domain reuse and
catalogue-size sensitivity; measure real batching and native-depth costs, and
accept that increased native inspection depth may not save additional model
calls when primitives already batch fully. Use the existing single-target
three-operation state change rather than an unsupported p3 anchor.

Alternatively approve a separate, versioned engineering extension with a
public prerequisite contract and selective/batched acquisition, followed by its
own validation. That changes the module and catalogue schema and cannot be
silently folded into this protocol. **Neither option was implemented.**

The owner's next decision is whether to revise the study to the present API or
authorize a separate extension. Then review the proposed thresholds, authorship
limitation, budgets and ceilings before Stage1. No approval is inferred from
elapsed time, the draft cases or the old M4 budget.

## Files for review

- [Pre-run note](PRE_RUN_NOTE.md), [checkpoint/hash](STAGE0_CHECKPOINT.json).
- [Skill/depth table](SKILL_DEPTH_TABLE.md), [structured skills](skills-and-depths.json),
  [domain proposals](domains.json).
- [All draft cases as CSV](cases.csv), [full private recipes as JSON](cases.json),
  [split/authorship validation](case-design-validation.json).
- [Predictions, thresholds, scoring and analysis](PREDICTIONS_AND_THRESHOLDS.md).
- [Proposed scoring/observability contract](SCORING_CONTRACT_DRAFT.md).
- [Budget formulas/ceilings](BUDGETS_AND_CEILINGS.md), [machine-readable values](budgets.json).
- [Required interface/design decision](REQUIRED_INTERFACE_CHANGE.md),
  [source evidence](source-compatibility.json), [original prompt components](M4_PROMPT_COMPONENTS.json).
- [Preservation check](preservation-check.json), [preparation source](prepare_stage0.py).

All output remains local. No commit, push or upload was made.
