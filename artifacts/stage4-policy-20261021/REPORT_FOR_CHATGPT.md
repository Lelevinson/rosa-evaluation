# Stage 4 three-algorithm comparison: results and recap

Date: 2026-10-21. This report completes the frozen policy-only comparison and
the small real ROS validation. It does not complete the separate V2 live
reliability work or establish end-to-end manifest quality. Baseline v1 is unchanged.

## Verdict

The predefined criterion for full JTVR model integration was not met. Do not build the full custom Runnable or launch the larger model JTVR study on these results alone.

JTVR versus batching: 0 lower-cost, 96 cost-tied, 0 higher-cost paired fixtures out of 96. Identical acquisition sequences: 74/96.

On the 30-fixture predefined opportunity subset, complete modeled-cost reduction versus batching was 0.00%; the 95% template-cluster descriptive interval was [0.00%, 0.00%]. The required threshold was at least 10% with a positive lower bound.

These are operation-cost simulations using fixed development timing weights,
not measured end-to-end ROS/model speed. Selector CPU and parser time are
reported separately and cannot turn equal acquisition work into a benefit.

## What ran

- 1152 persisted policy episodes; 1152 passed the separate read-back audit.
- 288 primary episodes: 96 fixtures each for greedy, amortized batching and JTVR.
- 576 sensitivity episodes: unit-cost and prior-service-type profiles.
- 96 depth-one JTVR episodes and 192 role-separated-with-shared-reuse episodes.
- 15 real ROS episodes across five templates and all three policies; 15 contract passes and 15 separate server-value audit passes.
- Zero model requests. No OAuth sign-in or tokens used. No robot motion or Gazebo arm.
- 39 validation tests passed: 22 new policy/evidence/audit tests plus 17 existing Phase 4 tests.

The full protocol, bounds and stop rule were frozen before the evaluation run:
[protocol](../../docs/STAGE4_POLICY_PROTOCOL_2026-10-21.md), [freeze](freeze.json),
[fixtures](fixtures.json), [machine-readable analysis](analysis.json).

## Primary results

| Policy | Contract passes | Complete modeled cost | Acquisition cost | Acquisition executions | All CLI commands | Modeled parameter RPCs | Selector CPU ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| greedy | 96/96 | 523.5915 | 296.9516 | 272 | 468 | 320 | 22.838 |
| batching | 96/96 | 482.7105 | 256.0706 | 256 | 452 | 244 | 42.702 |
| jtvr | 96/96 | 482.7105 | 256.0706 | 256 | 452 | 244 | 417.455 |

Complete costs include common bootstrap, charged metadata warm-up, controlled
writes and all acquisition attempts. Acquisition costs exclude those common
setup/write phases. Simulated RPC counts are modeled from the captured
contracts; real server-counted RPCs appear in the real-validation table.

JTVR complete modeled-cost reduction versus greedy: 7.81%. This alone does not establish a contribution beyond batching.

Against greedy, JTVR won 37, tied 44 and lost 15 fixtures. The 15 losses are 10 wrong-type and five partial-output cases: exploration can waste work when its nominal output assumptions fail. All eventually resolved their requirements; these are cost losses rather than unreported task failures.

### Results by task template

| Template, 12 fixtures each | Greedy mean complete cost | Batching mean | JTVR mean | J/B cost ties |
| --- | ---: | ---: | ---: | ---: |
| one_parameter | 2.5658 | 2.5658 | 2.5658 | 12/12 |
| three_cold | 4.4709 | 3.9625 | 3.9625 | 12/12 |
| three_warm | 3.9625 | 3.9625 | 3.9625 | 12/12 |
| write_report_verify | 7.8699 | 7.3616 | 7.3616 | 12/12 |
| mixed_roles | 7.8699 | 7.3616 | 7.3616 | 12/12 |
| node_summary_and_parameters | 4.4238 | 4.0675 | 4.0675 | 12/12 |
| two_node_scope | 7.5743 | 6.5575 | 6.5575 | 12/12 |
| parameters_and_topic_qos | 4.8953 | 4.3869 | 4.3869 | 12/12 |

## Sensitivity and ablations

| Profile | J/B lower / tied / higher cost | Identical sequences | J/B total cost reduction |
| --- | ---: | ---: | ---: |
| calibrated | 0 / 96 / 0 | 74/96 | 0.00% |
| unit_cost | 0 / 96 / 0 | 78/96 | 0.00% |
| prior_type_allowed | 0 / 94 / 2 | 76/96 | -0.55% |

| Ablation | Contract passes | Cost ties with own primary arm | Ablation / primary total cost |
| --- | ---: | ---: | ---: |
| jtvr_depth_one | 96/96 | 96/96 | 482.7105 / 482.7105 |
| batching_role_separated | 96/96 | 87/96 | 491.6610 / 482.7105 |
| jtvr_role_separated | 96/96 | 87/96 | 491.6610 / 482.7105 |

The role-separated arms keep the same evidence ledger. Reuse is not removed
to manufacture an advantage for joint obligations. A depth-one prefix still
has a greedy completion estimate; a tie with depth two is plausible.

The two J/B losses under prior-type access are the wrong-type node-summary
cases. J retains an equal-estimated-cost greedy plan that attempts bulk first;
B reads the already-required node summary first, discovers the actual wrong
type, and avoids that failed bulk attempt. J wastes one bulk invocation in
each case. This is a concrete limit of nominal-cost selection and the tie
rule, not a reason to retune against these frozen cases.

Joint versus role-separated acquisition saves work in nine cases for BOTH
B and J. The mixed-role request can batch verification-only fields alongside
the task field before the phase boundary. The same shared cache is retained
in the separated arm; this is a scheduling/batching benefit available to B,
not evidence of an exclusive JTVR lookahead contribution.

## Was the selection problem genuinely difficult?

The tested catalogue provides genuine cold discovery, full versus partial bulk
reads, shared node-summary/type acquisition, per-node scope, changing cost
estimates and mixed parameter/topic obligations. Targeted tests also change
the requirements and require replanning. Node information is never credited
with parameter values or topic QoS. Thus this is broader than triplet queries.

It is nevertheless a small, mostly separable catalogue: compatible parameter
batches are per node, there are only two discovery providers, and topic details
have a separate provider. The amortized baseline explicitly credits every
such overlap and setup cost. There is no demonstrated hard cross-group
selection problem here. This is the central limitation of the current
research opportunity, not evidence that more artificial tools should be added.

The two seeds vary values and partial-output shape, not task semantics.
Several warm conditions repeat an already-warm state; ambiguous-write faults
are inert on read-only tasks. Treat eight templates, not 96 independent
families, as the diversity unit. The suite is not independently authored or
blinded. No global theorem about every ROSA request follows from these runs.

## Real ROS validation

These episodes used the existing ROSA wrapper implementations with a common
bounded argv subprocess helper on isolated ROS Jazzy nodes. Real parameter
callbacks recorded values separately from CLI parsing. Server counts exclude
DDS discovery. One episode per template/policy is a smoke check; wall times
include startup/scheduling noise and do not support a model speed claim.

| Policy | Passes | Wrapper / CLI executions | Server RPCs | Actual summed CLI wall time, s |
| --- | ---: | ---: | ---: | ---: |
| greedy | 5/5 | 23 / 23 | 17 | 22.483 |
| batching | 5/5 | 19 / 19 | 9 | 17.779 |
| jtvr | 5/5 | 19 / 19 | 9 | 13.492 |

See [real raw episodes](ros-comparison/episodes.jsonl),
[real native commands and RPC values](ros-comparison/native-commands.json),
[real audit](real-audit.json), and [cleanup status](ros-comparison/status.json).

B and J performed the same amount of native work. The observed difference
in wall time across single repetitions is not a demonstrated JTVR selection
speedup; scheduling, CLI discovery and warm-up can dominate such samples.

Development calibration used two samples per tool. Its probe was developed
before the evaluation freeze; callback value logging was added for the later
real comparison. The retained development captures are the frozen cost input.
They are too small to characterize latency distributions or transfer to a
different graph, host load or robot. Real injected-fault campaigns have not run.

## Manifest and model dependency

All policies received the same annotated required fields, roles, targets and
phases. They did not receive hidden current values, failure labels or optimal
actions. Strict validation tests reject omitted fields/roles, altered targets
and expanded scope. This validates a supported structured contract, not
general natural-language interpretation. Neither Qwen nor the hosted model
generated manifests in this experiment. Their end-to-end omission rates and
fallback behavior remain unknown. Zero inference savings are claimed.

## Original JTVR implementation scope

Implemented in this isolated experiment: joint deduplicated obligations,
provenance/epoch/phase-qualified evidence, conservative write barriers,
scoped CLI parsers, shared actual-result-checked two-read fragments,
greedy/reference cost completion, strong per-node amortized grouping, and
bounded JTVR prefix-plus-residual selection with a switching margin.

Not implemented: model root approval, same-inference manifest extraction,
production custom Runnable/formatter, native history integration, dynamic
ROSA tool menus, automatic writes or recovery, and asynchronous continuations.
The real check drives unchanged wrappers directly, not AgentExecutor.

## Reliability, Baseline v1 and remaining stages

Baseline v1 still contains 540 scripted controls plus 120 live trials.
Original hosted/local baseline handling scores remain 30/36 and 24/36.
Additional retrospective strict scores remain 30/36 and 12/36. The local
drop exposed report-argument and prerequisite-attempt problems; it is not
a new model run or a changed 18/18 achievable-goal result.

The prior V2 hosted batch stopped before consent with zero model requests.
Its failed-supervisor status was an intentional scope-change cancellation.
V2 live reliability interventions have not now been run. This policy study
does not replace that comparison or establish safer model behavior.

| Stage | Status after this study |
| --- | --- |
| 1, shared ROSA backends | Previously demonstrated in mock tools. |
| 2, contract/scoring | Working foundation; new scoped evidence contracts tested. |
| 3, baselines/reliability | V1 preserved; prospective isolated interventions pending. |
| 4, acquisition/caching | Policy tier and real smoke complete; full integration decision recorded above; separate reliability work incomplete. |
| 5, verified episodic memory | Not started; requires history-dependent cases and matched controls. |
| 6, Gazebo arm/hardware | Base simulator installed; arm, controllers, skills and platform contract pending. |

The user requested a final results commit on `member/martin` after the newly
tested Stage 4 is complete. That full-stage condition is not met. No final
Stage 4 completion commit is claimed by this report. Evidence for this tier
already resides inside the experiments repository for explicit later staging.

## Recommended next decision

Use amortized batching as the current selection reference and pause full JTVR integration in this catalogue. Finish the separately controlled reliability/manifest questions before spending on a large end-to-end study. Revisit lookahead only if an actual supported workflow introduces a grounded decision that B cannot already handle as efficiently.

For ChatGPT review: assess whether the registered real catalogue contains a
missing legitimate overlap or prerequisite pattern, whether the strong B
definition is fair, and whether the negative/tied outcome warrants simplifying
the project. Do not infer value merely from the sophistication of the design.

## Reproduction and evidence integrity

From the prepared WSL research environment in the evaluation checkout:

```bash
python -B -m experiments.jtvr_policy.campaign verify
python -B -m experiments.jtvr_policy.report
```

The original prepare/run actions refuse overwrite. A modified protocol needs
a separately named campaign rather than overwriting this evidence. The
source snapshot and input hashes are in `freeze.json` and `source/`.
The analysis module was added after freezing selection code; it performs
read-only analysis and is recorded in the final evidence manifest.

One Windows launch misclassified unittest stderr as a native-command error
despite 39 tests reporting OK. Its original log is preserved. A clean
Python test runner repeated the same 39 tests with explicit exit code zero;
both logs remain. No failed model trials are hidden in this correction.

The original Baseline v1 archive hash and every previously frozen V2 source
file were checked unchanged in [preservation-check.json](preservation-check.json).
The detailed pre-policy history remains in
[the earlier checkpoint](../../docs/RECAP_FOR_CHATGPT_2026-10-21.md).

Local-only report links may not work in a bare ChatGPT attachment. Supply
this Markdown with the evidence archive if raw inspection is needed.
