# G1 revision 1 — Stage 0 report for review

Date: **2026-11-13**. **Preparation complete; advancement not authorized.**

The narrowed catalogues register through the unchanged public API, and the new
observer-separation unit tests pass in both mock domains. This resolves the
specific Stage0 design obstruction by **removing unsupported requirements**, not
by extending ROSA. The [original stopped package](../README.md) and its
STOPPED_INTERFACE_INCOMPATIBLE status remain unchanged.

No Stage1 scripted model paths, live requests, full-trial local audits or Phoenix
persisted audits have run. Actual model-turn counts are **not recorded**. They
must be verified structurally before Sol dev. No performance conclusion follows
from Stage0 construction/unit checks.

## The three items requested for Claude's review

| Item | Result |
|---|---|
| Template-group counts | **6 dev; 13 held-out**, with no group crossing splits;6 of the held-out groups are ladder templates |
| Observer-separation proof | **4 test methods,8 domain checks passed**: corrupted reads, dropped acknowledgement/stale cache, mutable-alias isolation, actor-unavailable/observer-available |
| Proposed thresholds | P1>=20% call saving; P2 five-point correctness tolerance; P3>=10-point catalogue error increase; P4 depth contrast equivalent within±10 points; P5 unchanged-API controls/audits all pass. Confidence/sample/ceiling rules below and in the detailed table |

All thresholds are defaults awaiting confirmation. The supplied text does not
actually enumerate P1-P4 numerically; these are explicitly proposed definitions.
The [prediction table](PREDICTIONS_AND_THRESHOLDS.md) gives the precise Support,
Against and Uninformative criteria, per-domain conditions and sample minima.
Ceiling correctness/selection is Uninformative, not evidence of improvement.

## Counts and cases

| Split | Ladder | Movement | Missing pose | Ambiguous | Partial/ineffective write | Unavailable source | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dev | 8 | 4 | 2 | 2 | 0 | 0 | **16** |
| Held-out-designated | 24 | 6 | 2 | 2 | 2 | 2 | **38** |

Held-out:4 depths x2 domains x3 cases=24 ladder;1 write skill x2 domains x3=6;
4 non-depth cases/domain=8. Each case runs in2 execution conditions, so **76
held-out trials/model**,152 across both backends. That is1.9 times M4's40/model,
not38 trials/model. Sol dev adds32 task trials. First-turn catalogue probes are
additional responses without executed task trials.

Each inspection depth has **6 held-out cases/condition/backend**, just3/domain.
Matched-success n can be smaller and must be printed in every depth table. The
held-out ladder uses6 linguistic groups shared across domain/depth cells; the
overall13-group count must not be mistaken for13 independent groups/depth.
Only large effects are visible; group-bootstrap intervals can be unstable.

Ladder fixtures include known true, known false and unavailable-source outcomes.
Negative movement fixtures require missing-pose/no dispatch and an actually
exercised ineffective/partial command. New requests use service/handover contexts
and explicit scope. No exact request duplicates an M4 design string. Semantic
novelty/no-close-paraphrase compliance has **not been independently reviewed**;
the case file must not be called externally validated.

**All54 drafts are Codex/AI-authored.** Zero real teammate-authored cases exist.
The supplied one-third independent-author gate is **unmet**. No teammate,
blindness or independent review was invented. An AI-only study would require
a documented authoring amendment in the advancement confirmation; it cannot be
represented as meeting the original gate. The drafts are not approved test data.

## What now fits the API

Each domain has5 skills:4 source-group inspections of native depth1/2/4/6, and1
single-target movement skill. The combined catalogue has10. Names do not encode
depth; no new plain-language descriptions or prerequisite fields are added.
The underlying tool set stays the same five functions in every condition.

| Nominal path | Primitive model turns, expected | Macro model turns, expected | Native operations |
|---|---:|---:|---:|
| Inspection at any selected depth d | 3 | 2 | d in either condition |
| Healthy initially off-target movement | 5 | 2 | 3 in either condition |

Primitives can already acquire all selected inspection groups in one read_state
call. Macro selection executes the bounded routine and the model then classifies
its evidence. This removes model decision turns; it does not erase native source
work. Expected counts above still require the **Stage1 real-adapter/fake-model
structural check**. If those paths contradict the hypothesis, stop before dev.

Four public constructor checks passed (2 domains x2 conditions), with zero tool
invocations and no source changes. P5 remains pending the full scripted/fault/
trace controls, rather than claiming Support from constructors alone. p3 anchors,
selective acquisition and horizon-dependent reliability are explicitly **G2**.

## Observer and domain engineering

New MockWorld authority, ActorChannel/ActorTransport and read-only
ObserverChannel/ObserverTransport live here. Actor and observer have separate
state objects and record lists; observer truth comes through its own interface,
not the actor cache. Both observe one simulated world. Independence does not
mean independent authorship, a second sensing technology or process isolation.

The observer proof demonstrates true state after a lost acknowledgement, correct
truth despite a corrupted actor read, and no mutable aliases from actor/returned
objects into observer records. **Five additional world/transport unit tests
passed** for map-lease revisions, lost localization, base energy evolution,
different partial effects, and read-only permission enforcement.

Arm coordinates are radians. Base coordinates use metres and heading fractions;
readiness derives from localization confidence, map revisions, battery fraction,
clearance, odometry error and slip. A base partial goto translates without the
requested heading; arm partial actuation affects only one joint-style field.
These are bounded mock semantics, not physical dynamics or navigation performance.
Only the known-pose movement prerequisite is implemented; no hidden multi-source
movement guard was added. Exact mock parameters and test limits are in the
[observer design/proof](OBSERVER_SEPARATION.md) and [world source](worlds.py).

## Budgets, prompt suffix and resources

M4 task limits stay **8 calls,2048 observed output tokens,10 native operations,
16 tool attempts,3 corrections,<=1 dispatch,360 seconds**. Read-only permissions
deny movement identically in both arms. Qwen stays on original A:8192 context,
1024 output/call,temperature0,seed42,think=false,original FA policy,f16 KV.
Fresh task history/state does not disable M4's server prefix-cache reuse.

System/RULES/condition sentences are unchanged. The only domain substitution is:

`Joint tolerance 0.025 radians.`

becomes, for the base in both conditions:

`Position tolerance 0.025 metres; fraction tolerance 0.025.`

The condition-wording confound remains. The exact components are retained in
[prompt-contract.json](prompt-contract.json). The [pre-run clarification](PRE_RUN_CLARIFICATION_01.md)
explicitly distinguishes task evidence/memory from server prefix caching.

| Batch | Ordinary cap | HTTP reserve | Physical ceiling |
|---|---:|---:|---:|
| Sol dev:16x2x8 | 256 | 3 | **259** |
| Sol held-out:38x2x8 | 608 | 3 | **611** |
| Qwen held-out:38x2x8 | 608 | 3 | **611** |
| Stage4b each backend:38x3 | 114 | 3 | **117** |

Stage4b totals228 ordinary/234 maximum across both models. It uses macro wording
only, sizes3/5/10 skills, and no tool execution. Target-plus-two distractors and
the no-target ambiguity sampler are proposed in catalogue-probe-plan.json.
It does not test primitive wording or growth in underlying tool schemas.

Reuse M4's explicit HTTP502/503/504 eligibility/exclusions, at most one retry per
logical call and a separate charged reserve. No task or command replay. Neither
ceilings nor the eight-hour backend bound may be extended after launch.

M4-average **estimates**, not measurements: roughly85 requests for Sol dev,
201 for Sol held-out and274 for Qwen held-out. Qwen's whole-campaign time scales
to **about2.60 hours**; summed task timers scale to2.31h. New mock/case/context
costs can differ. The suggested2.5-3.5h is a planning guess, not a promise. See
[exact arithmetic and estimates](BUDGETS_AND_ESTIMATES.md).

Local encrypted authorization **file presence was confirmed**, with no token
contents read/decrypted, no provider validation/renewal and no login. It does not
prove an active grant. Provider quota is **not recorded/not derivable locally**.
M4's106/323 was a local cap, not217 remaining provider requests. Any future live
batch must use a fail-closed restore-only path and review its preflight first.

## Limits, preservation and next gate

All model outcome predictions are untested. No latency/accuracy from these mocks
was substituted for live model results. All-attempt/matched-success views,
discordant pairs, template-group resampling, separate evidence/goal scores,
batching, ambiguity sensitivity and budget/length endings are required later.
Depth covaries with context/check-set size; only large differences are visible.

AI-only case authorship, explicit acquisition allowlists, fixed numeric goals,
one movement skill/domain, domain-prefixed distractors and a short fixed loop
can favor macros or create ceilings. The study compares two execution conditions
in the shared repaired framework; it does not show superiority over stock ROSA.
Two mock domains/two models establish no broad robot or hardware generality.

The stopped proposal, M4, timing/serving studies, M1-M5 reports and source files
are preserved. Check revision-validation.json and the manifest for exact counts,
hashes and the pre-run-note digest. No commit, push or upload was made.

**Next:** review the13 held-out template groups, observer proof and threshold
table; confirm counts, suffix and ceilings, and resolve the unmet authoring gate.
Only then run Stage1 structural/fault/trace controls. Sol dev, final freeze,
held-out execution and Stage4b each remain separately gated. No background
experiment will start from this preparation.

## Review files

- [Dated amendment](AMENDMENT_2026-11-13.md), [pre-run note](PRE_RUN_NOTE.md),
  [pre-run clarification](PRE_RUN_CLARIFICATION_01.md), [checkpoint](revision-checkpoint.json).
- [Skill/depth table](SKILL_DEPTH_TABLE.md), [cases CSV](cases.csv),
  [full fixtures](cases.json), [template groups](template-groups.json).
- [Observer proof](OBSERVER_SEPARATION.md), [observer results](observer-separation-results.json),
  [world unit results](world-semantics-results.json), [public API construction results](public-api-registration-results.json).
- [Predictions/thresholds](PREDICTIONS_AND_THRESHOLDS.md), [scoring contract](SCORING_CONTRACT.md),
  [budgets/estimates](BUDGETS_AND_ESTIMATES.md), [resource data](resources.json).
- [Proposed catalogue probe](catalogue-probe-plan.json), [pair order](paired-order-proposal.json),
  [actual public catalogue schemas](catalogues.json).
