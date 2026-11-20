# Workflow v1: prospective development milestone

The project vision remains improving ROSA's reliability/efficiency through
backend-neutral software, without training an LLM. Historical Stage 4, Baseline
v1 and all frozen reliability/output-budget campaigns remain unchanged.

## Exact intervention and decision ownership

Candidate: transfer coordination of one authorized, single-node skill's routine
read / conditional write / fresh verify sequence to ROSA. This is an exploratory
system-level orchestration comparison, not a novel routing-algorithm claim.

| Responsibility | Model-managed reference | Program-managed candidate |
| --- | --- | --- |
| Interpret request / select permitted skill | Model | Model |
| Choose when to read prerequisites | Model | Program |
| Validate identifiers, values and write prerequisites | Shared existing safeguards | Identical safeguards |
| Choose when to request the authorized motion | Model | Program, only with known state |
| Choose when to acquire fresh verification | Model | Program |
| Execute native operations and check fresh outcome evidence | Shared transport / verifier | Same transport / verifier |
| Classify outcome and submit truthful observed values | Model | Model |
| Finish after validated accepted report | Program | Program |
| Respond to unexpected conditions | Model / human within limits | Escalate to model / human within same limits |

Automatic reporting is deliberately NOT added to the candidate. The same
accepted-report termination repair is used in both conditions. Single-action
responses are enforced in both conditions before tool dispatch. Rejected reports
remain recoverable. Fresh sessions are required for new tasks.

Both conditions expose identical tool names/schemas, public authorized skill
catalogue and primitives. Selecting a skill triggers automatic coordination only
in the candidate. This deliberate change of select_skill semantics is the
system-level intervention; exposing identical names does not establish identical
tool abstraction. Do not claim a pure tool-selection/filtering effect. A later
comparison against an explicit macro-tool reference is needed to distinguish
orchestration policy from macro-tool packaging.

## Bounds and exclusions

Start with a synchronous opt-in module; legacy ROSA is unchanged. One native
write maximum. Default existing bounds: 8 model requests, 16 tool attempts
(including nested program tool calls and selection), 10 native operations,
3 invalid corrections, 180 seconds. Every routine operation uses the same
ReliableTool, transport and operation ledger as the reference. No automatic
write replay, hidden oracle reads, model-specific argument repair, new OAuth
permissions, streaming, memory or general task planner.

Unknown prerequisite observations cause escalation without motion. A rejected
prerequisite, unknown outcome or ineffective accepted command returns control
with observed evidence; the workflow does not invent an alternative pose.
An exception stops the workflow, especially after uncertain write dispatch.
The module does not establish collision avoidance or physical robot safety.

## Development pilot and next gates

First validate accepted SUCCESS / FAILURE / UNKNOWN termination, rejected report
recovery, mixed-call rejection, tool callback/span closure and resource limits
using actual ROSA with scripted providers. Then exercise fresh mock fixtures
covering movement, already-at-target, dropped motion, unavailable observations,
rejected prerequisites and uncertain write outcomes. These are development
fixtures, not held-out evaluation or evidence of Qwen/Sol improvement.

Record outcomes, native/tool/model counts, invalid attempts, decisions delegated
to program and escalation. A deterministic scripted reference establishes
execution feasibility; scripted generated-token counts have no interpretation
as real inference cost. Preserve pilot code, source hashes and traces separately.

After the pilot, freeze a small live protocol for Qwen and Sol: the same cases,
permissions and resource ceilings per condition; within-backend comparisons;
separate model corrections from program assistance. Keep selection/ambiguity
correctness independently scored, rather than claiming that one permitted skill
tests language understanding. No live model benefit is established by this
development milestone. Hosted tests still require manual OAuth authorization.

Later test the same adapter with the existing Gazebo UR5e skill, then expand
conditions only when the small prototype supports a larger experiment. Full
JTVR stays paused; episodic memory is optional.
