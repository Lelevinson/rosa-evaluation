# Stage 2 detailed execution checks

Date: **2026-11-14**.

This supplements [the combined report](COMBINED_STAGE2_REPORT.md). All figures combine the sealed original segment and its continuation. The original failed provider attempt is retained. This is dev validation, not a held-out test or a P1-P4 verdict.

## Actual model turns

1 attempt(s) differed from the scripted turn comparator. The comparator was not forced on the live model.

| Trial | Actual calls | Expected calls | Recorded error |
|---|---:|---:|---|
| G1r1-dev-012-primitives | 1 | 3 | {'type': 'SafeError', 'code': 'error'} |

## Cost views

| View | Calls saved | Known input tokens saved | Known output tokens saved | Task time saved | Native attempts saved |
|---|---:|---:|---:|---:|---:|
| all_attempt_costs | 43.33% | 44.10% | 37.86% | 42.87% | -15.00% |
| matched_success_costs | 45.76% | 47.77% | 41.05% | 45.53% | 0.00% |

Known token sums omit unknown usage on the interrupted call. The matched-success view excludes that entire pair. A negative saving means more work. Timing includes local agent instrumentation and evaluator reads, and excludes subsequent persisted-trace audits. The long pause and fresh server/session segment limit causal timing interpretations.

## Native-acquisition band

The predefined band is **0.75-1.25** macro/primitive attempts per domain/depth. The failed Base depth-6 primitive attempt has no completed acquisition path; its ratio is undefined and cannot be treated as a measured band violation.

| Domain | Depth | Primitive native | Macro native | Ratio | In band |
|---|---:|---:|---:|---:|---|
| arm | 1 | 1 | 1 | 1.00 | True |
| arm | 2 | 2 | 2 | 1.00 | True |
| arm | 4 | 4 | 4 | 1.00 | True |
| arm | 6 | 6 | 6 | 1.00 | True |
| base | 1 | 1 | 1 | 1.00 | True |
| base | 2 | 2 | 2 | 1.00 | True |
| base | 4 | 4 | 4 | 1.00 | True |
| base | 6 | 0 | 6 | undefined | None |

## Fault coverage and reporting

| Trial | Injected fault | Exercised | Dispatches | Accepted status | Correct |
|---|---|---|---:|---|---|
| G1r1-dev-007-macro | missing_pose | True | 0 | UNKNOWN | True |
| G1r1-dev-007-primitives | missing_pose | True | 0 | UNKNOWN | True |
| G1r1-dev-partial-arm-macro | partial | True | 1 | FAILURE | True |
| G1r1-dev-partial-arm-primitives | partial | True | 1 | FAILURE | True |
| G1r1-dev-015-macro | missing_pose | True | 0 | UNKNOWN | True |
| G1r1-dev-015-primitives | missing_pose | True | 0 | UNKNOWN | True |
| G1r1-dev-partial-base-macro | partial | True | 1 | FAILURE | True |
| G1r1-dev-partial-base-primitives | partial | True | 1 | FAILURE | True |

Diagnostics: dispatch_violation=0, unsupported_accepted_success=0, accepted_success_wrong_goal=0, budget_exhaustion=0, length_stop=0, clarification_review_required=4.

Correctness includes appropriate failure/unknown reporting and preliminary clarification; it does not mean every request caused a successful movement. Clarification transcripts still lack independent semantic human adjudication. Fault-exercised status follows the frozen scorer and must not be inferred merely from an expected FAILURE label.

## Interpretation and next gate

The dev run checks execution paths, accounting, scorers and observability. No prompts, guards, conditions or cases were tuned from these results. The one permitted scorer amendment was consumed before live inference. No additional amendment was used.

The provider interruption cannot establish an architecture correctness advantage. The condition-sentence confound and AI-only authorship remain. Stronger claims require the separately gated held-out study. Do not launch it, a distractor probe or Qwen here. For later stages P2 remains restricted to Against or Uninformative; Qwen also needs its reviewed GPU-idle gate.

The owner authorized completion of this continuation and future evidence-preserving recovery from external interruptions. See [the standing instruction](STANDING_INTERRUPTION_POLICY_2026-11-14.md). Normal remembered-credential cleanup retains encrypted sign-in and clears in-memory credentials. No new consent was automated.
