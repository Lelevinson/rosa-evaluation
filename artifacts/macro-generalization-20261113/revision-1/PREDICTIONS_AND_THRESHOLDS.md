# G1-r1 proposed predictions and thresholds

Date: **2026-11-13**. **Defaults for confirmation, not approved thresholds.**
The supplied revision does not enumerate P1-P4 or numerical decision thresholds;
the definitions below are proposals. Old Stage0 predictions remain unchanged
in the stopped package. The revised study tests a fixed decision-turn abstraction,
not an acquisition-policy algorithm or horizon-dependent reliability.

For each applicable backend report **Support, Against or Uninformative**. Require
all stated domain/endpoint conditions for Support; do not select the favorable
stratum after results. A ceiling/floor in the performance metric relevant to the
prediction is Uninformative. Perfect primary correctness does not establish a
reliability improvement, although differing model-call costs can still be measured.

| ID | Proposed prediction and metric | Support | Against | Uninformative |
|---|---|---|---|---|
| P1 | Macros remove model turns in read-only tasks in both domains. Call saving=1-sum(macro physical requests)/sum(primitive physical requests). | Point saving>=20% and lower95% cluster-bootstrap bound>0 in each domain; matched-primary-success and all-attempt estimates both satisfy the rule | In either domain upper95% bound<=0 with at least4 matched-success pairs | Otherwise, including fewer than4 matched-success pairs in a required domain |
| P2 | Full-contract correctness is preserved within a five-percentage-point loss. Delta=macro pass fraction minus primitive pass fraction. | Lower95% bound>=-0.05 in each domain and non-ceiling outcomes exist; zero dispatch violations | Upper95% bound<-0.05 in either domain, or any macro dispatch violation | Otherwise; both conditions perfect is Uninformative about reliability, not Support |
| P3 | A larger catalogue makes first-turn selection harder under macro wording. Delta=error fraction at10 minus at3, paired by case. | Delta>=0.10 and lower95% bound>0 | Upper95% bound<=0 and there is non-ceiling/floor outcome variation | Otherwise, including perfect selection at all sizes; report size5 as well |
| P4 | The call-saving fraction does not increase materially just because native inspection depth increases. Contrast=saving(d6)-saving(d1). | Entire95% interval lies within[-0.10,+0.10] in each domain, with at least2 matched-success pairs per required domain-depth cell | Entire95% interval lies above+0.10 or below-0.10 in either domain | Otherwise; intervals too wide or endpoint sample too small |
| P5 | Both narrowed domains use the unchanged public API and preserve safety/observability | All requested Stage1 scripted paths, fault controls, observer tests and local/persisted audits pass without changing protected source or hiding I/O | A required source change, hidden operation or failed mandatory control demonstrates the claim false | Constructor checks alone, an unrun control suite, or unresolved test defect |

The20% call threshold, five-point correctness tolerance, ten-point selection
effect/equivalence band and sample minima are explicit proposed engineering
criteria. They have not been selected from G1 model results. A single measured
dispatch violation is a retention failure, not a population-risk estimate.
If a prerequisite metric/sample is missing, use Uninformative; never estimate
unrecorded values to fill the gap.

P1 nominal expectation for an error-free inspection is33.3% fewer model turns
(3 to2), independent of native depth. That arithmetic alone is not live evidence.
P4 can fail if deeper requests/context trigger enough extra model turns, retries
or failed completions. A positive depth trend would contradict the constant-turn
picture, even if macros still help overall. A negative trend can show overhead
or failures eroding savings. A wide interval supports neither equivalence nor
a trend. The shared-native-work table is an accounting check, not a separate
claim that batching makes native operations disappear.

## Analysis defaults

- Report per model, domain and depth, then backend summaries. Retain both-pass,
  primitive-only, macro-only and neither counts for paired cases. No pooled
  p-values. Report known-failure/UNKNOWN handling as correct when the full
  corresponding case contract is satisfied; physical goal attainment is separate.
- Exactly6 held-out ladder cases/depth/condition/backend:3/domain. That is small;
  only large effects are visible. Matched-success n can be below6; print its
  actual value for every depth/contrast and per-domain cell. Never use the planned
  denominator for a missing or interrupted result.
- Resample **whole template groups**, including all their domains, cases and
  paired condition rows. Proposed10000 bootstrap draws, seed20261113, percentile
  95% intervals. Retain empty/degenerate draws and their counts. Do not pretend
  individual paraphrases are independent. The draft has13 held-out groups overall
  and6 ladder groups; per-domain/depth cells contain just3 cases/groups. These
  exploratory intervals can be unstable or degenerate.
- Compare all-attempt and matched-primary-success costs side by side: logical
  decisions, physical requests including reserve attempts, known input/output
  tokens, unavailable usage, elapsed task time, native operations and invalid
  attempts. Failed/censored usage is not zero. Matched-success conditioning can
  favor a condition and cannot replace all-attempt outcomes.
- Report native attempts per selected source and per-call logical nodes plus
  physical groups. Inspection depth d is d native attempts behind one subject-node
  read, in either arm. Show tool names/arguments and source records. Rejected
  calls, repeated observations and program-owned nested tools remain charged.
- Depth covaries with requested fields, source identities and context length.
  This is not an isolated causal effect of horizon. Native/source work and model
  decision turns are distinct axes; true horizon-dependent reliability is G2.
- Budget exhaustion (calls/output/native/tools/corrections/deadline) and explicit
  provider length stops are separate flags, allowed to overlap. Do not group
  all errors as wrong choices or false SUCCESS. Provider finish reason absent
  means not recorded, not an inferred length stop.
- Ambiguity primary scoring preserves M4 clarification behavior and transcript
  review flags. The alternative inspection-acceptable view is sensitivity analysis,
  not a revised primary score. Neither enters depth analysis. Evidence truth,
  selected-goal attainment and requested-goal correctness remain separate.
- Stage4b uses the macro condition sentence only; it does not test primitive
  wording. Size3 includes the correct target plus two prespecified distractors;
  ambiguous cases use a frozen no-target sampler. Record the sampler and catalogue
  order before launch. Domain prefixes make cross-domain distractors relatively
  easy; a catalogue-size ceiling is not broad selection robustness.

## Current status and bias disclosure

**No G1 model data exist. P1-P4 are Uninformative.** Public registration/open checks
passed and observer unit tests passed, but Stage1 fake-model paths and Phoenix
audits have not run. P5 remains Uninformative pending the full controls.
There is no observed contradiction of3-versus2 model turns yet because actual
turn counts have not been measured; the structural gate must test that first.

All54 drafts are AI-authored, with no independent teammate input. This violates
the supplied independent-authorship criterion and reduces protection against
implementation-driven case selection. Exact numeric movement goals, explicit
inspection allowlists, fixed source sets, one write capability/domain and a
fixed short-horizon loop can favor macros or produce ceilings. False/unavailable
observations were included in ladder cells to avoid an exclusively healthy screen;
this still is not independent validation. No prompt may be tuned on held-out data.

The condition-wording confound carries over unchanged. Native-turn equivalence
in scripted paths is a structural control, not proof that execution packaging
alone caused a model's different skill choice. Two mocks and two backends do not
establish generality across robots, hardware, models or real navigation.
