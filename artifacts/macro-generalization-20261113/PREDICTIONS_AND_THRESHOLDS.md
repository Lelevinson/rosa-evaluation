# G1 proposed predictions and decision rules

Date: **2026-11-13**. **Draft defaults; no user confirmation or experimental
freeze.** The supplied prompt refers to thresholds but does not enumerate them.
These definitions are proposed here, not recovered from an earlier agreement.

All performance outcomes below are currently **Uninformative: no G1 data**.
The static architectural finding for P5 is separately recorded. Never classify
a correctness ceiling as evidence of a reliability improvement.

| ID | Precisely proposed prediction | Support | Against | Uninformative |
|---|---|---|---|---|
| P1 | Macro fractional model-call savings grow with native inspection depth | Per model, reduction at d6 minus d1 >=15 percentage points, with cluster-bootstrap lower95% bound >0 | Upper95% bound <=0 | Otherwise; missing paired data; effective model decision depth does not vary |
| P2 | The macro's call-saving benefit transfers to both mock domains | In each domain, point reduction >=20% and lower95% bound >0, reported separately per model; no claim from pooling | In either domain, upper95% bound <=0 | Otherwise, or insufficient observations |
| P3 | Larger catalogues hurt first-turn selection on this task set | Selection error rate at12 minus3 >=10 percentage points, lower95% bound >0, separately per model and fixed condition wording | Upper95% bound <=0 and a non-ceiling outcome exists | Otherwise; all catalogues perfect; ambiguity sampling or wording factor unresolved |
| P4 | Macro preserves primary correctness to within a five-percentage-point loss | Macro-minus-primitive primary pass lower95% bound >=-0.05, with non-ceiling outcomes and no dispatch violation | Upper95% bound <-0.05, or any macro dispatch violation | Otherwise; both arms perfect is Uninformative about reliability improvement, not Support |
| P5 | The exact proposed G1 acquisition contract fits the unchanged public API | Both domains implement all proposed skills and pass controls without source changes, selective handicaps or hidden operations | A required skill/acquisition contract needs module/schema changes | Controls or specification unresolved; live transfer untested |

**Observed before any live run:** static source inspection places the exact
requested p3 write anchor Against P5. The native inspection ladder exists, but
the API forces full source-group acquisition into one primitive call. Native
depth alone does not increase nominal model decision count. This contradicts
any assumption that the requested d+2 model-call ladder already exists in ROSA;
it is not an observed model-performance result.

The five-point noninferiority margin is a proposed engineering tolerance, not
a clinically/statistically established standard. If the user wants no loss at
all, change it before confirmation. Sample size is unlikely to establish a tight
five-point bound: a wide interval means Uninformative, not equivalence. A zero
dispatch-violation requirement is a safety retention gate, separate from uncertain
performance estimates. P2 cost support does not convert P4 ceilings into support.

## Frozen analysis would require

- Report per model/domain/depth before any overall summary. For each case retain
  adjacent paired condition outcomes, both-pass / primitive-only / macro-only /
  neither counts. Do not turn two domains/models into a generality claim.
- Report all-attempt costs and matched-primary-success-pair costs side by side:
  logical and physical model requests, known input/output tokens, censored usage,
  monotonic task latency, provider timing when recorded, native operations and
  invalid attempts. Do not treat unavailable usage as zero. No estimates for
  missing values. Matched-success conditioning can favor a method by excluding
  failures, so it never replaces all-attempt outcomes.
- Define call saving as1-(sum macro calls)/(sum primitive calls), on a declared
  subset. P1 contrasts d6 with d1; do not fit a causal depth slope. Depth is
  confounded with nominal horizon/context, source set, and possibly task semantics.
- Bootstrap paired case records **by complete template group**, retaining all
  cases/conditions in a selected group. Proposed10,000 draws, fixed seed20261113,
  percentile95% intervals. Report degenerate draws and actual group counts.
  Never resample individual cases as independent observations. No pooled p-values.
- The draft held-out ladder has five template groups shared across all domain/
  depth cells, not ten independent templates per depth. Although there are ten
  cases/depth, these are few independent clusters. Only large effects are visible;
  bootstrap intervals are exploratory and can be unstable or degenerate.
- Separate selection correct, executed path correct, task-local truthful report,
  goal satisfaction, fresh outcome evidence and primary pass. A grounded readiness
  SUCCESS for a movement request is not goal completion. Recognizing failure
  without exercising a mandated fault is not a successful fault-control result.
- Keep logical-call exhaustion, native/tool/correction/deadline exhaustion and
  response-length endings as separate flags. An overlapping failure may carry
  multiple flags; do not rename it as a simple skill-selection error.
- For primitive runs show requested nodes, physical sources acquired, reads per
  read_state call, and actual subset/full-batch fractions. Current inspections
  acquire d sources behind one subject-node request: report both counts so that
  one logical subject is not mistaken for one physical acquisition.
- Show independent prerequisite reads separately from genuinely dependent-read
  acquisitions. There are no proposed dependent-read cases yet. Write/verification
  dependency is not itself a dependent-read acquisition case.
- Ambiguity uses frozen M4 primary clarification: no selection, report, operation
  or movement and a valid clarifying question, with transcript review. Alternative
  view may accept authorized truthful read-only inspection with no movement, or
  clarification; it is stakeholder sensitivity analysis. Neither enters depth
  tests; never choose the favorable rubric after seeing results.
- Apply one user-confirmed primary rule per prediction. Do not search for a
  favorable domain, catalogue size, metric, model or threshold after results.

## Anticipated favorable-result biases

All cases are authored by the implementing assistant, without the requested
independent teammate contribution. Read-only depth cells are healthy nominal
paths, exact observation allowlists make targets easy to identify, fixed numeric
goals align closely with catalogue targets, and most reads are independent.
These choices can favor a straightforward bundling result and create ceilings.
Primitive execution must retain full batching; forcing one call per source would
handicap the reference. Per-case budgets derived from the correct target can also
leak workload/depth through the displayed limits. No such bias is fixed by having
64 cases. Report these limitations and consider a common maximum budget per domain
as a separately confirmed amendment; do not change budgets silently.

The original condition-wording confound remains. Selection differences cannot
be attributed solely to execution architecture. Stage5 may cross wording as a
factor, but that needs a new explicit decision and the larger ceiling.
