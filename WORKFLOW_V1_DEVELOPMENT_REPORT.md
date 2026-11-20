# ROSA workflow v1: terminal repair and initial prototype

Date: 2026-10-22. Status: initial offline engineering milestone complete;
live Qwen/Sol and Gazebo evaluation of this new module NOT started.

## Vision and exact scope

The objective remains improving ROSA reliability and efficiency through modular
software around existing LLMs, with the same rules for Qwen and Sol. No model
training, larger-model substitution, full JTVR, episodic memory or general task
planner is introduced. Historical Stage 4 and all frozen experiment results
remain unchanged. This is a separate prospective engineering milestone.

The user's two ideas map to this implementation as follows:

- Divide responsibilities: the model selects a permitted skill and reports the
  observed result; software coordinates that skill's routine execution.
- Program-selected routine tools: after selection, the candidate executes the
  existing read, conditional write and fresh verification tools in order.

This is a system-level orchestration candidate, not evidence for a new routing
algorithm. Selecting a skill has deliberately different execution semantics
between conditions even though tool names and schemas match. A later explicit
macro-tool reference is needed before claiming benefits beyond skill packaging.

## Implemented prerequisite repair

`rosa-research/src/rosa_reliability/terminal.py` adds an opt-in synchronous ROSA
adapter. It terminates after submit_report returns acceptance AND the bound
session ledger confirms matching accepted status and observed values. A textual
success claim or a forged acceptance response without a ledger entry cannot
trigger this termination. The returned acknowledgement is deterministic JSON,
not an additional model response.

Rejected semantic or schema reports remain correctable. An accepted report on
the eighth allowed iteration finishes without a ninth inference. Multi-tool
responses are rejected before any of their calls dispatch, count against the
shared validation budget and can receive ordinary bounded corrective feedback.
The same policy is used in both comparison conditions. This policy is a new,
explicit common constraint, not a retrospective change to previous trials.

The base ROSA implementation and previous completion tools remain unchanged.
Default prototype model-iteration limit is eight. Accepted sessions cannot be
invoked again as new tasks. Streaming is explicitly unsupported in this version.

## Workflow implementation and decision ownership

`rosa-research/src/rosa_reliability/workflow.py` adds a fresh-session public
authorized skill catalogue, select_skill tool, state transitions and bounded
execution. It currently supports one selected single-node numeric skill per
session, including a multi-coordinate arm pose. A test selects a second distinct
pose to check that dispatch is not fixed to the demonstration target.

The ownership table is in `docs/WORKFLOW_V1_DEVELOPMENT_2026-10-22.md`. Both
conditions share primitives, transport validation, evidence contract, controller,
verification criteria, native/tool budgets and terminal handling. In both,
the MODEL retains final outcome classification and reporting. The program does
not silently repair model arguments, invent observations or generate a report
on the model's behalf.

Program condition:

1. Validate skill selection against the public authorized catalogue.
2. Read fresh prerequisite state through read_state.
3. If evidence is missing, escalate without motion.
4. If known state is off target, request the selected bounded movement once.
5. Acquire fresh verification through verify_outcome, including when already
   at the target. Command acceptance is never goal attainment.
6. Return confirmed evidence for model reporting, or return an explicit
   NEEDS_DECISION result if prerequisites/outcome are unresolved.
7. Stop on an execution exception without automatic command replay.

The model-managed reference selects the same skill and requests the routine
primitives itself. The candidate still exposes the same primitives for bounded
handling after escalation. Model-requested versus program-requested operations,
evidence and verification are recorded separately. Automatically executed steps
are credited to the combined system, never to the LLM's underlying ability.

## Validation results

Five recorded suites pass (35 test methods total):

| Suite | Tests |
| --- | ---: |
| New terminal/workflow integration checks | 16 |
| Existing output completion checks | 6 |
| Existing output timeout accounting checks | 2 |
| Existing reliability/operation/tracing checks | 8 |
| Existing evidence freshness checks | 3 |

Receipts and complete logs:
`artifacts/workflow-v1-validation-20261022/validation.json` and adjacent logs.
The new tests execute actual ROSA and LangChain with scripted providers. They
include terminal SUCCESS/FAILURE/UNKNOWN, rejected-report correction, forged
acceptance rejection, final-iteration completion, mixed-call rejection with
closed callbacks/spans, shared native/tool/validation/time bounds, no command
replay, alternate catalogue selection and attribution of program evidence.

The separate persisted development pilot has seven fixtures in two conditions:

| Fixture | Expected behavior | Scripted model calls: reference / program | Native operations: each |
| --- | --- | ---: | ---: |
| Movement | Verified SUCCESS | 5 / 2 | 3 |
| Already at target | Verified SUCCESS, no write | 4 / 2 | 2 |
| Accepted command with no effect | Observed FAILURE, no replay | 5 / 2 | 3 |
| Missing prerequisite observation | UNKNOWN, no write | 4 / 3 | 2 |
| Missing post-write observation | UNKNOWN, no replay | 5 / 2 | 3 |
| Controller prerequisite rejection | Observed FAILURE, no automatic retry | 5 / 3 | 2 |
| Write exception after partial effect | Controlled stop, no accepted report | 3 / 1 | 2 |

All 14 saved scenarios pass their intended behavior and local trace audit. That
means 12 truthful accepted reports and two expected controlled error stops;
it does NOT mean 14 successful robot movements. Two fixture families produce
SUCCESS, two FAILURE, two UNKNOWN and one controlled stop.

Total scripted invocations are 31 reference versus 15 program; native operations
are 17 in each condition. This invocation reduction follows from the prescribed
scripts and workflow ownership. It demonstrates that the execution paths work,
not an empirically established Qwen/Sol efficiency gain. Generated token usage
and inference latency are not measured; the pilot uses no live model.

The 16-test suite includes these fixtures, so the saved pilot is not another
14 statistically independent observations. Cases are development cases, not a
held-out benchmark. There is no inference about generalization or significance.

## Development failures preserved

`artifacts/workflow-v1-development-a0-20261022` preserves the first 14-case
attempt, its source snapshots, results and traces. Thirteen cases failed the
trace audit because workflow/terminal bookkeeping spans were classified TOOL
and counted as extra tool executions. Their behavioral checks passed. One
reference error-stop case passed its trace audit.

The correction classifies bookkeeping as CHAIN. A later targeted test also
identified that executor-local callbacks did not propagate to LangChain's
internal parser-error tool. Invocation-level callbacks corrected this gap.
The existing auditor was not weakened or edited. The corrected independent
14-case run is `artifacts/workflow-v1-development-r1-20261022`.

No failing attempt was deleted, relabeled as a pass or substituted into an old
campaign. Old output-budget scores and known retrospective terminal cases are
unchanged; this repair needs prospective live validation.

## Limits and next gate

- No live Qwen, Sol, OAuth authorization, model token generation or Gazebo
  execution occurred in this milestone. No credentials were read or persisted.
- Traces are actual local OpenInference/OpenTelemetry spans. Phoenix export
  and server-side matching were NOT exercised by this offline pilot.
- The prototype assumes serialized synchronous invocation and fresh sessions;
  it is not validated for concurrent sessions sharing state or streaming.
- The operation ledger rejects expired native dispatches. A live runner must
  also bound in-flight model/native calls with external deadlines and retain
  cumulative token accounting. Existing hard live caps must not be replaced
  by max_iterations alone.
- This is an authorized bounded movement procedure, not collision avoidance,
  perception, grasping or a physical-robot safety certification.
- The scripted pilot has one permitted skill per fixture. It does not measure
  language interpretation, ambiguous-goal resolution or adaptive planning.

Next: freeze a small live feasibility protocol, using this same common repair
and the same public permissions/limits in both conditions; test each backend
against its own model-managed reference. Include independently scored skill
selection and uncertainty/escalation behavior. Keep development and held-out
cases separate. Only expand the study if the live pilot shows a plausible
benefit. Hosted trials retain manual OAuth consent and existing session cleanup.

After that, adapt the same workflow to the existing Gazebo UR5e transport and
validate deterministic controls before model-driven trials. No reinstall or
new robot integration is required merely to resume the existing movement skill.

## Preservation checks

Previously sealed archive hashes were checked and remain:

- Output-budget complete evidence:
  `ae202ca1f6aa0bf43fdeea189c6f489b0b1cb0b632ce160e905303b3accea19a`
- Output-budget complete review:
  `da713dc6b59670d83eb17e4a7edc1d1a7f8dfc67a36846f541c963c7a4ba6cf0`
- Reliability v2 + UR5e complete evidence:
  `63188649d0c21bd7f0b9a8a70bce01de88b5d2df45845486aafa884d68cadae6`

The new implementation is in the research repo; development protocols, tests,
raw data, traces and this report are in the evaluation repo. No historical
source snapshot, protocol, score or evidence archive was edited.
