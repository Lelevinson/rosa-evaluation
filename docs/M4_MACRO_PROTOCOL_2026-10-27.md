# M4: focused paired evaluation of bounded ROSA capabilities

Date: 2026-10-27. Status: prospective; freeze before any live inference.

## Question and boundaries

Does the existing simple bounded macro reduce the cost of completing fresh tasks
without an observed correctness loss against model-managed primitives, within
each tested backend? The tested module supports named-pose arm movement and
read-only controller/joint-sample readiness inspection. It does not implement
multi-step multi-actuator autonomy, perception, a new planner, JTVR or memory.

The primitive reference uses the same current ROSA integration, repaired common
prompt contract, registered tools, permissions, feedback, evidence-reference
reporting, terminal handling and guards. It is not untouched upstream ROSA.
Only ownership of routine operations changes: select_skill returns targets for
the primitive condition; the macro performs bounded reads/conditional write/fresh
verification. The model still chooses the skill and classifies its outcome.

No product policy, model-specific fix or new truncation recovery is introduced.
The shared behavioral rules are reused from M3; condition semantics and new time
limits are explicitly disclosed. Different fresh case wording is not independent
external task design: these are prospective cases authored by the same project,
frozen before inference and not tuned after observing model outcomes.

## Design, schedule and controls

Ten task families x two repetitions x two execution conditions x two backends =
80 live trials, 40 per backend, 20 per condition/backend. This size supports
coverage of both capabilities and repeated paired execution, not a precise
population-level noninferiority claim.

Five movement families: constraint-based selection among home/stage_left/park_right;
an already-satisfied stage_left goal requiring zero commands; suppressed ineffective
publication; actual partial wrist execution; missing prerequisite joint observation.
Four inspection families: healthy readiness; actually deactivated trajectory
controller; injected missing controller observation; injected missing joint sample.
One ambiguous request requires clarification with no skill, report or native action.

Home/stage_left/park_right remain one movement capability. Stage_left has pan=-0.14
and final wrist=0.20; park_right has pan=0.16 and final wrist=-0.12; other joints
retain home. Every target remains within the existing 0.4-rad transport boundary.
One command maximum per task remains unchanged. Inspection/ambiguous tasks expose
only read-only inspection permission; movement tasks expose both capability types.
This public application permission is shared across conditions, not hidden scoring
information or evidence that the LLM infers authorization independently.

Each case/repetition is an adjacent pair with condition order counterbalanced:
each condition is first in ten of twenty pairs per backend. The second repetition
rotates case order. The backend schedule reverses condition order. Sol runs first,
then Qwen; Gazebo access is serialized. Backends are analyzed separately; this
order does not permit a causal cross-backend speed comparison.

Before live inference, run 20 zero-model Gazebo controls (ten cases x two conditions)
with the actual skill/report tools and independent checkers. The reference receives
resolved goals and explicitly scripted clarification; it is not an LLM competitor.
Every control and its local/exact Phoenix audit must pass, with clean teardown.
Offline tests cover task scoring, permission boundaries, schedule completeness,
budgets and the recovery reserve. Preflight failures stay recorded. Any runtime
change after freezing requires an explicitly new version; no silent tuning.

Each trial resets to its frozen starting pose using an outside-task command and
independent observation. Actual controller deactivation/reactivation is outside-task
management. Actor sensor failures are explicit injected unavailability; an independent
healthy observer does not supply missing evidence to the agent. Ineffective movement
records a dispatch attempt but suppresses actual publication; partial movement
publishes with the final wrist left at home. Required fault exercise is scored.

## Measures and scoring

Primary: correct full task completion under the frozen contract, with no credited
infrastructure recovery. Report final completion including eligible recovery
separately. Scoring retains these components rather than conflating them:

- User-goal alignment: selected exact skill satisfies the frozen request, or an
  ambiguous request receives clarification before any selection/acquisition.
- Grounded selected-skill outcome and independently checked physical state or
  readiness. A truthful report about the wrong goal still fails the full task.
- Required command count and fault exercise. Truthful failure without attempting
  an ineffective/partial command does not pass the fault-handling fixture.
- Invalid attempts, unsupported success attempts, accepted success for the wrong
  goal, dispatch violations, actual versus suppressed publication, and no replay.
- Physical model requests including failures; charged decision calls; known input
  and generated tokens; missing/censored usage; native operations by actor; task
  wall time; campaign wall time and outside-task setup/observer/audit costs.

SUCCESS means observed selected goal within 0.025 rad, or all readiness facts true;
FAILURE means known off-target/unready; UNKNOWN means required actor evidence is
unavailable. Independent read-only transport instances check final joints and
controller readiness, but share the same simulator/APIs. No collision-safety or
hardware guarantee follows from this verification.

The clarification screen requires a clarification marker and zero skill selection,
accepted reports and native operations. Save and review all eight live clarification
transcripts against that fixed intent rubric; retain automated and review decisions
separately. Do not change the rubric based on model identity or favorable outcomes.

Report all scheduled cells, attempted/completed/censored/unstarted cells, and paired
outcomes. Missing cells are neither passes nor silently invented model failures.
All-attempt cost tables accompany matched-success costs, so cheap failures cannot
manufacture efficiency. Primary comparisons are within-backend. Repetitions of
the same family are clustered, not twenty independent task families.

Engineering screen, fixed before results: require the complete paired schedule,
all quality audits, no dispatch violations, no greater number of primary failed
tasks than primitives, at least 25% fewer model calls on pairs where both conditions
pass, and no more than 25% extra native operations on those pairs. Report paired
wins/losses and exact descriptive counts. This screen is a development decision,
not proof of equivalence or statistical noninferiority. With only ten families,
generalization uncertainty remains substantial. If both conditions perform alike,
or the macro trades correctness for call savings, report that without redesign.

## Limits and infrastructure reserve

Each condition uses the same limits: eight charged decision calls per task,
2048 observed generated tokens, ten native operations, sixteen tool attempts,
three corrections, 360 seconds, one movement at most. This new time allowance
is prospective, shared and deliberately longer than M3's 180 seconds. It is not
a retroactive change to old results or a Qwen-only serving intervention.

Qwen remains qwen3.5:9b Q4_K_M, digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90,
pinned Ollama server 0.40.6; num_ctx=8192, num_predict up to1024 per call within
remaining observed allowance, temperature=0, seed=42, mmap=true, no streaming,
reasoning or cache. HTTP client timeout remains180 seconds. Sol remains
gpt-6.1-sol via ChatSiwc. The hosted adapter has an observed-output gate, not an
identical provider-side generation cap. Usage missing from failed requests is
censored, not free compute. An observed-token threshold is not a guarantee about
unknown actual provider-side tokens.

Each backend has 320 ordinary request slots plus three infrastructure reserve
slots: 323 total; combined hosted+local ceiling646. At most one retry per logical
call, one-second backoff, only explicit HTTP502/503/504 without auth/scope/quota
error categories. No automatic retry for transport timeouts, truncated generation,
invalid tool output, HTTP429, revoked grants or quota exhaustion. Other errors
stop the affected task/backend as specified by existing transport availability.

A qualifying failed request stays recorded as an external failure and consumes
the shared reserve before a retry. A returned retry completion consumes a normal
decision slot. Only the unconsumed model request/prompt is retried inside the
pre-parser gate; a whole trial or any robot command is never replayed. Previous
tool results are preserved. Unknown provider usage remains explicitly censored.
Primary uninterrupted completion and recovered completion stay separate.

The backend wall ceiling is eight hours, inclusive of setup/audit/recovery, chosen
to accommodate forty full 360-second task allowances plus bounded overhead rather
than prematurely censor later cells. It is a ceiling, not a runtime forecast.
An external task alarm takes the smaller of360 seconds and remaining campaign
time; setup has its own120-second alarm and native I/O remains bounded. All attempts
reserve/checkpoint before inference and journal inference/session state afterward.
No repeated attempt replaces an unsuccessful trial. If interrupted, preserve the
current attempt and require an explicit documented continuation, not an automatic
restart of completed cells. Authorization loss preserves progress and stops hosted
requests; Qwen remains independently runnable.

## Observability, reproducibility and stopping

Freeze cases, prompts, scoring, schedule, limits, source bytes and dependency locks
before controls/live inference. Verify immutable M2/M3 evidence against its original
382-entry manifest. Current OAuth hotfix sources are prospective and explicitly
included; do not weaken old historical hash gates to rerun frozen studies.

Use the existing local audit and exact persisted-Phoenix span/closed-tree auditor,
unchanged. Agent traces use the existing capability project/root span, with explicit
stage=M4, case, condition, repetition and backend metadata. Every physical model
request must have a matching LLM span, including failed/retried requests. Stop on
quality audit failure; retain unsuccessful audit evidence. Normal task failures
remain recorded and do not trigger replacement or tuning.

Use the user's opt-in protected remembered authorization, preserving scopes,
identity checks and serialized rotation. No automatic approval of new consent.
Tokens stay outside traces/Git; successful opt-in exit clears memory while retaining
the encrypted refresh credential. Explicit sign-out remains available. No paid-key
fallback, package/model download or hardware deployment is introduced.

When finished or stopped, independently aggregate checkpoint/trial records, review
clarification transcripts, report both conditions and both backends honestly,
retain all failures and prepare a checksummed evidence archive. Do not claim M4
complete if scheduled cells remain unstarted. No M5 implementation or new research
mechanism is automatically authorized by a positive result.
