# ROSA research: six-stage roadmap and evidence map

Updated 2026-10-21 after the final simplified Stage 4 campaign. This maps all six
work packages; it does not claim that all six are complete or every acceptance
check passed. The earlier [policy checkpoint roadmap](PROJECT_ROADMAP_POLICY_CHECKPOINT_2026-10-21.md)
is preserved separately.

The [final report](../artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md)
contains the methods, every failed trial, counts, limitations and recommendations.
The [evidence guide](STAGE4_EVIDENCE_GUIDE.md) gives offline verification commands.

## Current verdict

The planned live screen is finished: 160 attempts, 80 per backend. Automatic
batching did not meet either backend's retention screen. Hosted completed all
parameter tasks with either policy and used the same native/model work. Qwen
completed none of the parameter-report contracts, so successful-task cost/time
benefit is not estimable. Fix the interface before treating that as a comparison
of useful completed Qwen workflows.

Original bounded-lookahead JTVR remains paused: it did not beat strong amortized
batching in the original-spec policy study. Do not rename batching as JTVR.

There is an audit exception: the frozen auditor passed 152/160 trials and found
eight missing recovery-stop tool spans. All state checks passed. A separate,
explicit post-run reconciliation accounts for those eight using raw requests,
callback counts, world records and attributed reports. The original supervisor
still says FAILED; complete tool-span coverage and the original full-audit
acceptance check remain false. No trial was rerun, rescored or silently repaired.

## Goal and numbering

Evaluate local Qwen3.5 9B and the hosted OAuth comparator through one ROSA tool
interface. Measure whether conservative reuse and selection improve successful,
verified task execution beyond strong simpler controls. Investigate memory only
when tasks require history, and validate a specified simulated robot separately.

These are research work packages. The historical Gate 1-4 rerun ended at simple
caching; it is not retroactively renamed as an original-JTVR evaluation.

| Stage | Work package | Current status | Boundary / next requirement |
| --- | --- | --- | --- |
| 1 | Shared local and hosted backends | Demonstrated through actual ROSA | Interface compatibility is established; reliable use of every tool schema is not. |
| 2 | Stateful contract and independent scoring | Working prototype; state records audited | Eight trace gaps remain explicit. Reporting/schema and extra-claim behavior need a new prospective contract. |
| 3 | Baseline and reliability interventions | V1 preserved; the agreed small live follow-up is finished | Broad held-out movement generalization is untested. Neither local prompting nor guards solved the whole contract. |
| 4 | Caching and evidence selection | Planned simplified screen and analysis closed with a documented audit exception | Neither live retention screen met; full JTVR paused. This is not an all-gates-passed readiness result. |
| 5 | Verified episodic memory | Not started | Requires history-dependent tasks and matched retrieval/examples/token controls. |
| 6 | Gazebo arm, then hardware | Simulator foundation installed; arm interface not configured | Select the robot and bounded skill contract before installing an arm stack. |

## Stage 1: interchangeable backends

Both candidates run the actual modified ROSA AgentExecutor with the same tools,
prompt structure and fresh trial sessions. Hosted sessions use memory-only OAuth
credentials and revoke on exit. The final hosted campaign used account-catalog
`gpt-6.1-sol`; local used `qwen3.5:9b`, 8192 context, 256 output, temperature 0,
seed 42, reasoning disabled, mmap and automatic offload.

Those are different serving profiles, not equal model/token/compute budgets.
The loaded Qwen digest, quantization, runtime and sampled host memory are archived.
The final campaign used 429 hosted and 576 local model requests, below each 1,056
request cap. No inference tuning was silently applied during behavioral testing.

## Stage 2: contract, world and evaluator

The stateful movement world runs separately from the agent. An evaluator checks
state, reports, prerequisites, verification timing and raw argument types rather
than trusting model prose. Real ROS parameter tasks additionally record native
commands, instrumented server callbacks and independent evaluator reads.

Independence is from model claims, not independent authorship: trusted fixture
code and some scoring functions are shared. The mock is not a physics simulator
or adversarial operating-system sandbox. No robot moved in this campaign.

Keep these outcomes separate:

1. Goal state and accurate SUCCESS/FAILURE/UNKNOWN classification.
2. Tool/report schema and exact entity-identifier compliance.
3. Invalid attempts rejected by a controller versus accepted execution.
4. Model behavior versus orchestrator verification/reporting.
5. Operational completion versus iteration limits and validation aborts.
6. Record consistency versus full instrumentation coverage.

The battery=-1 sentinel remains an artificial API convention for comparability.
Required structured fields are scored; arbitrary additional claims and final
prose are not exhaustively evaluated. Future contracts should remove irrelevant
fields, specify extra-claim behavior and use consistent helper/report shapes.
Do not rewrite frozen historical scores when making those changes.

The recovery stop uses BaseException and bypasses LangChain's normal tool-error
callback. Correct that control-flow/tracing boundary before wider use; the
post-run reconciliation does not manufacture the eight absent spans.

## Stage 3: baseline and reliability attribution

Baseline v1 remains unchanged: 540 scripted controls and 120 live trials.
Original hosted/local baseline handling was 30/36 and 24/36; retrospective stricter
contract scores were 30/36 and 12/36. Both verified all 18 achievable baseline
goals. Those different definitions remain separately labeled.

The new screen used six existing development fixtures, four independent arms and
two repetitions: 48 trials per backend, 12 per arm.

| Intervention | Hosted strict / combined passes | Qwen strict / combined passes |
| --- | ---: | ---: |
| Original instructions | 8/12 | 0/12 |
| Clarification only | 12/12 | 4/12 |
| Bounded recovery only | 10/12 | 4/12 |
| Enforced verification only | 12/12 | 0/12 |

All four achievable mock transfer goals per arm were reached by both candidates.
Many local report failures therefore differ from motion failures. Local also
made invalid UNKNOWN-pose attempts and repeated failed actions; those remain
material behavior defects even when the controller rejected execution.

Hosted's six failed reliability trials classified UNKNOWN accurately and had no
critical action violations, but omitted the required final verifier step. Its
bounded guard activated zero times, so its two-pass difference from control is
not demonstrated benefit from recovery. Enforced verification added three checks.

Qwen's guard activated eight times; four resulting trials passed the full contract.
It cannot erase an earlier invalid attempt. Local enforced verification activated
zero times and did not solve local reporting/retry problems. Ten local reliability
trials exited at the iteration limit. Read the family breakdown in the final report.

These are small within-profile screens, not a general model ranking or confirmed
intervention effect. The 12-trial mix differs from the original 36-trial baseline.
The earlier expanded movement suite has 264 scripted controls; its proposed live
generalization schedule was not run. Nine inference diagnostics remain separate.

## Stage 4: selection evidence and decision

### Historical simple caching

Baseline v1 conservative caching saved 25% of eligible scripted sensor reads.
It did not demonstrate live model-call savings. A local timeout contaminated an
apparent latency/call advantage; that is preserved as a failure, not an improvement.

### Original-spec policy study

The [specification review](JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md) distinguishes
joint obligations, conservative validity, cost-aware lookahead and guarded read
continuations from earlier fixed bundles. The separate
[policy report](../artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md) records
1,152 audited policy episodes and 15 audited real ROS smoke cases, with no LLM calls.

On 96 primary paired fixtures, greedy cost was 523.5915 and batching/JTVR each
482.7105. Both reduced modeled cost 7.81% against greedy; JTVR improved 0% against
batching and tied all 96 primary cases. Depth two did not beat depth one, and
joint role handling benefited batching too. Sensitivity included two JTVR losses.
This did not justify a full custom JTVR Runnable in the registered catalogue.

### Prospective live batching screen

Actual ROSA, isolated Jazzy parameter nodes and model-generated requirements were
tested under the [frozen protocol](STAGE4_BATCHING_COMPLETION_PROTOCOL.md). Each
backend attempted eight nominal templates, two arms and two repetitions: 32 trials.

Both arms share the same convenience executor, conservative ledger, native tools
and continuation capabilities. Reference honors model-selected plans; candidate
selects amortized plans. This isolates selection above a shared batching helper.
An untouched primitive-only ROSA arm was not run, so no general helper/continuation
speedup over upstream ROSA is established.

| Result | Hosted | Qwen |
| --- | --- | --- |
| Strict completion, reference / candidate | 16/16 / 16/16 | 0/16 / 0/16 |
| Native CLI commands, reference / candidate | 48 / 48 | 66 / 54 |
| Instrumented parameter RPCs, reference / candidate | 30 / 30 | 58 / 38 |
| Model requests, reference / candidate | 67 / 67 | 60 / 60 |
| Successful matched pairs | 16 | 0 |
| Retention screen | Not met | Not met; completed-task benefit unestimable |

Hosted candidate/reference summed wall times were 352.605/318.282 seconds.
That observed 10.78% increase is not proof of causal selector overhead; serving,
native discovery and generation vary. Median ordering differs from total ordering.

Qwen's lower recorded candidate native work occurred in failed attempts. Do not
promote it to a useful end-to-end speedup. Both arms had 14 flat-report validation
aborts and two reports with node keys missing their leading slash. Provided helper
manifests were valid (14/14 per arm); only 12/16 trials per arm had a complete
manifest union, with four primitive-tool bypasses. Reporting and requirement
communication are different outcomes.

The nominal two-node case uses identical initial values on both nodes. It checks
separate acquisition and exact identities, not discrimination of differing node
values. Eight nominal templates and two repeats do not establish generalization,
fault tolerance, simulator performance or safety.

### Closure and remaining engineering

The agreed screen and analysis are closed with negative/inconclusive outcomes and
the eight-span audit exception. The frozen full-audit criterion was not fully met.
All 160 state records agree; the original failed audit and separate reconciliation
are retained. Keep the simpler selection reference and batching optional.

A separate BoundedGateway fixes a discovered write-count budget gap and has two
focused tests. It was not used in this study. Neither backend exceeded 24 native
commands. Broader use requires that guard plus a corrected tracing stop path.
Preserve failures; do not revive JTVR merely because the local report interface failed.

## Stage 5: verified episodic memory

Not started. Use tasks where prior verified experience can change a decision.
Compare no memory, matched fixed examples, unverified memory and outcome-verified
memory under matched example/token budgets. Store provenance, scope, conditions,
freshness and SUCCESS/FAILURE/UNKNOWN separately. Test stale and misleading episodes.

Mutable state requires current evidence. Memory cannot authorize motion or replace
verification. Implementing a database is not a measured memory contribution.

## Stage 6: specified Gazebo arm, then hardware

ROS 2 Jazzy/Gazebo foundation is installed; the last inspected simulator responded
as Gazebo 8.15.0. A specific arm model, controllers, MoveIt/skill interface and
robot scene are not configured. Earlier GUI rendering used llvmpipe; current GUI
performance is unverified. Hardware remains unspecified.

Choose the robot and a bounded task first. Start with read-only state and a
deterministic joint/pose skill under ordinary ROS control. Then expose the same
bounded skills to both models from matching reset states and verify fresh joints
independently. Use a deterministic planner/skill control. Add grasp/place and
perception after basic motion works; coordinated dual-arm behavior follows that.

Stage 6 can precede Stage 5. Gazebo is the more useful next integration target
after a small interface/tracing repair check; neither JTVR nor memory is a
prerequisite. Mock percentages do not transfer numerically to physics or hardware.

## Publication and immediate next work

Destination: `Lelevinson/rosa-evaluation`, branch `member/martin`. The results
commit contains code, curated raw records, reports and checksummed archives.
The exact modified research dependency is snapshotted; the evaluation commit
does not publish a separate research-repository commit. Credentials, environments
and local databases are excluded.

Next: separately freeze a small interface variant with consistent report shapes,
canonical node identifiers, bounded validation feedback and explicit stop tracing.
Do not silently fill missing model information or replace these results. Then
select the actual arm and configure one Gazebo skill before expanding into memory.
