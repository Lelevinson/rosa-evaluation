# Post-Stage 4 engineering milestone: reliable tool execution

Planning update: 2026-10-22. The user subsequently authorized completing this
sequence. Implementation and prospective validation are now in progress under
the separate [Reliability v1 protocol](RELIABILITY_V1_PROTOCOL_2026-10-22.md).
See `artifacts/reliability-v1-20261022/` for the source freeze and live records.

## Direction and evidence boundary

The objective is a practical, reproducible improvement to ROSA's reliability
and/or tool-calling efficiency, using modular software compatible with local
Qwen and the hosted OAuth backend. Training a model, implementing full JTVR and
building episodic memory are not required deliverables.

This sequence takes priority over future work in the
[historical six-stage roadmap](PROJECT_ROADMAP_SIX_STAGES.md). That roadmap is
part of the checksummed Stage 4 evidence and remains unchanged. Keep its stage
numbers as historical work-package labels; this is a separate prospective
engineering milestone, not a reopened Stage 4 campaign or a newly passed gate.

The [closed Stage 4 report](../artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md)
remains authoritative for those experiments. Baseline v1 and every frozen score,
protocol and source snapshot remain intact. Original full-audit acceptance was
not met: 152/160 frozen trace audits passed, with eight documented missing tool
spans reconciled separately. Reconciliation did not repair the absent spans.

The live comparison isolated automatic selection above a shared batching helper,
not batching versus untouched ROSA. Hosted arms used the same native/model work;
Qwen had no successful parameter-report pairs. Do not reinterpret those findings
as either useful batching gains or a universal rejection of batching.

## 1. Specify a model-independent contract before changing runtime code

Use the same node-keyed observation structure in retrieval and reporting, with
canonical, fully qualified node identifiers. Separate requested information,
observed values, provenance/freshness and claimed outcome. A possible shared
value structure is:

```json
{
  "observed_values": {
    "/node_a": {"alpha": 1},
    "/node_b": {"alpha": 9}
  }
}
```

This illustrates structure, not a frozen schema. Define missing values, invalid
identifiers, types, stale observations and additional claims before validation.
The evaluator must check reported identifiers and values against actual
observations and required task scope. It must not trust agreement with prose.

Do not silently add missing model requirements, rewrite entity identifiers or
substitute observed values into a model report and then call it model success.
If normalization or automatic report construction is deliberately supported,
record the original request and transformation and score that path as system
assistance. Apply identical rules to both backends.

Keep command acceptance, verified outcome and accurate reporting as separate
events. An accepted write is not evidence that a requested state was reached.

## 2. Repair execution boundaries and instrumentation

Implement reusable runtime mechanisms in `rosa-research`; put independent
evaluation and experiment-specific fixtures in `rosa-evaluation`.

- Return structured, actionable feedback for recoverable validation errors.
  Bound retries explicitly and retain the original invalid attempt. Distinguish
  model correction after feedback from deterministic orchestration repairs.
- Make recovery-stop control flow close and export its real tool span. Cover
  success, validation rejection, execution error, controlled stop and
  cancellation; do not manufacture terminal callbacks or success outcomes.
- Enforce the native-operation budget before every read or authorized write
  dispatch, including composite tools, retry paths and automatic verification.
  Define how attempted, dispatched, rejected and evaluator-only operations are
  counted. A retry must not reset or evade the shared agent budget.
- Keep execution/state records and Phoenix spans attributable using stable
  trial, tool-call and operation IDs. Distinguish an attempted call with no
  native dispatch from an executed native operation.

An earlier separately tested write-budget wrapper is a starting point, not
proof that all new runtime paths enforce the limit. Runtime integration needs
its own checks. Historical frozen traces and audits stay unchanged.

## 3. Validate with focused prospective evidence

First exercise deterministic and injected-fault cases without model calls:

- Different values on different nodes, wrong or missing node IDs, missing
  required fields and invalid types.
- Read-after-write freshness, stale evidence, rejected writes, accepted commands
  that do not achieve the goal, and accurate FAILURE/UNKNOWN reports.
- Exhausted operation budgets across reads, writes, composite execution,
  automatic verification and recovery.
- Trace closure and raw-record reconciliation for normal completion, errors,
  controlled stops and cancellation. Unexpected gaps fail acceptance.

Then freeze a small live validation protocol before running either backend.
Freeze the task contract, new cases, software versions, serving profiles,
trial order, sample size, retries, request/time/operation limits and decision
criteria. Cases used while developing the repair are development cases; reserve
fresh validation cases before further tuning. Repeated familiar templates do
not establish generalization.

### Proposed research question and controlled comparison

Under fixed resource limits, do structured validation feedback and automatic
fresh outcome verification improve verified task completion and reduce
unsupported success claims beyond a consistent interface, clear instructions
and ordinary bounded retries?

This is the immediate candidate study, not a frozen protocol. The prerequisite
repairs supply a trustworthy common platform; they are not themselves evidence
that these interventions outperform a competent reference.

| Configuration | Structured validation feedback | Automatic fresh outcome verification |
| --- | --- | --- |
| A: strong reference | No; ordinary actionable errors remain available | No |
| B: feedback only | Yes | No |
| C: verification only | No; ordinary actionable errors remain available | Yes |
| D: combined system | Yes | Yes |

All configurations share the corrected tool/report contract, clear task
instructions, safety/prerequisite checks, available observation tools, retry
opportunities and resource caps. Baseline validation errors must be recoverable,
not fatal by design. No arm receives extra retry entitlement or privileged
ground-truth access. Freeze error-message content and detail so that a claim
about structure is not accidentally a comparison of different information.

The independent evaluator always observes the outcome, without leaking its
private records into agent context. Turning automatic verification off must not
forbid the model from requesting a check through the shared tools. Turning it
on changes when ROSA initiates fresh checks and returns their evidence. Define
the triggering policy, evidence freshness and decision rules before execution.
Charge automatic checks and recovery to the same agent operation/time budgets;
record their additional model and token costs. Evaluator-only reads are tracked
separately and cannot supply free evidence to the agent.

Compare B with A for feedback, C with A for automatic verification, and D with
B and C for incremental benefit. Do not claim synergy merely because D beats
A: an interaction needs its own predefined analysis and adequate evidence.
Do not change prompts, schemas or serving settings between these arms.

Keep any existing common retry controller fixed. New guarded-recovery policies
are deferred as an additional independent intervention rather than bundled into
D. Keep raw model success claims visible even if a system gate rejects or
changes the final report; report both model and combined-system outcomes.

The specific hypotheses, sample size, uncertainty analysis and minimum useful
effect remain to be set prospectively. Do not equate identical maximum budgets
with identical actual cost or draw a general small-model conclusion from one
local and one hosted configuration.

For both backends report:

1. Initial model contract compliance, invalid attempts and unsupported claims.
2. Corrections generated by the model after feedback, with retry cost.
3. Orchestrator repairs/checks and final combined-system outcomes separately.
4. Independently verified goal attainment and report accuracy.
5. Model calls, native operations, wall time, limit exits and complete trace
   coverage, including failures.

Predefine the benefit and acceptable reliability/efficiency tradeoff before
seeing live results. Engineering acceptance requires the specified deterministic
contract, budget and tracing checks to pass; a general reliability claim also
requires the planned comparison to support it. A small positive screen is not
proof of safety or research novelty. No live sample count, effect threshold or
experiment result is being retrospectively declared here.

## 4. Move to one deterministic Gazebo skill

After initial repairs and validation, select one supported robot and bounded
task. Establish ROS 2 state communication, reset behavior, deterministic
movement limits and independently observed final state before model control.
Validate the verifier with deliberately unsuccessful as well as successful
motions. Do not infer physical goal completion from command acceptance alone.

Then give both backends the same ROSA skills, resets, observation/report
contract and execution limits, with a deterministic controller reference.
Keep simulation behavior separate from mock percentages and hardware claims.

## Deferred work and publication

Full JTVR remains paused; batching remains an optional capability, not the
mandatory research contribution. Stage 5 verified episodic memory is deferred.
Stage 6 Gazebo can precede it. Expand scope only when the evidence and project
capacity justify it.

Publish runtime changes to the member's `rosa-research` branch and evaluation
protocols/data/reports to the corresponding `rosa-evaluation` branch, with exact
cross-referenced commits. Preserve existing local runtime changes and snapshots;
this planning update does not publish them or start a new experiment.
