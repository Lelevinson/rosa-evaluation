# Original JTVR specification: implementation audit and proposed minimum experiment

Historical review before policy implementation. The subsequently authorized
[frozen policy experiment](STAGE4_POLICY_PROTOCOL_2026-10-21.md) and
[results](../artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md) now supersede
the implementation-status statements below. The original review is preserved:
the policy core was tested, while full model/Runnable integration remains unbuilt.

Date: 2026-10-21. Status: review and proposal only; no original-JTVR implementation
or new JTVR experiment is claimed complete by this document.

## Verdict

The Phase 4 roadmap needs revision before further JTVR code changes. The original
proposal is a bounded evidence-acquisition policy inside the ROSA agent loop.
The current `phase4/client.py` policy named `jtvr` is a fixed dependency bundle
around a custom `acquire_context` tool. It is not the specified algorithm and
cannot establish its usefulness or uselessness.

I previously reduced the research question too far. The existing mock tests are
useful for reliability and cache behavior, but they do not reproduce discovery
that enables bulk access, shared task/verification obligations, or residual-cost
selection. The correction is to preserve those results under their actual scope,
not to rename a fixed bundle as the original JTVR.

The original proposal is more precise and testable. Its central risk remains
that amortized batching with reuse and the same continuation runner makes the
same choices. On homogeneous parameter tasks that is a likely equivalence, not
a flaw that should be hidden by weakening the baseline.

## Authoritative design and current evidence

The original file is copied byte-for-byte into
[specifications/JTVR_Final_Technical_Specification_ID(1).md](<specifications/JTVR_Final_Technical_Specification_ID(1).md>).
Its SHA-256 is `cd18df7ec554b5ca845c4bfbf9ff1971738801a9aa13b0da5a7b3e24abadc2df`.
The copy does not change the original root document. That document is a proposed
design, not evidence that the algorithm or its claimed literature comparisons
have already been reproduced.

Relevant local implementation:

- [ROSA agent/executor factory](../../rosa-research/src/rosa/rosa.py): `_get_agent`, `_get_executor`.
- [Backend factory](../../rosa-research/src/rosa_backends/__init__.py) and
  [hosted history adapter](../../rosa-research/src/rosa_backends/chat_siwc.py).
- [Existing ROS 2 tools](../../rosa-research/src/rosa/tools/ros2.py): single parameter
  reads, writes, node/service information and generic service calls.
- [Current observation gateway](../experiments/phase4/client.py),
  [contract checks](../experiments/phase4/contract.py),
  [experiment runner](../experiments/phase4/runner.py), and
  [read-back audit](../experiments/phase4/audit.py).

The inspected installed stack is LangChain 0.3.30, langchain-core 0.3.86 and
langchain-ollama 0.3.10. The original design audited earlier dependency versions;
compatibility must be established on the installed stack, not inferred from the
old audit alone.

Baseline v1 remains: 120 live trials across 12 scenarios and 540 scripted controls.
Its original 24/36 local and 30/36 hosted handling scores are unchanged.
Additional retrospective contract checks produce 12/36 local and 30/36 hosted
strict completed handling; these are additional calculations, not new model runs.

The current v2 preflight has 41 passing tests and 264 passing, audited scripted
trials. Nine local native diagnostic requests completed. The prospective hosted
batch `00879ccd-8e51-4b84-9ce5-50163da5bc55` was intentionally interrupted while
awaiting consent: zero model requests, zero trials, `NO_TOKEN_SESSION` cleanup.
The dependent local batch did not start. The temporary monitor/sleep request was
released. An `INTERRUPTED` batch and failed orchestration step are preserved;
they must not be called completed trials or unexplained model failures.

## Component-by-component comparison

| Original requirement | Current status | What is actually present / missing |
| --- | --- | --- |
| Same actual ROSA executor for both models | Implemented foundation | Both adapters run through modified ROSA and its standard AgentExecutor. |
| Native typed tool calls and bounded requests | Implemented foundation | Tool registries, callbacks and per-trial limits exist. This is not a JTVR selector. |
| Task and verification evidence obligations | Missing | Tasks are encoded in mock queries/scorer predicates, not an explicit acquisition manifest. |
| Joint deduplication by entity/field/scope/phase/epoch | Missing | Cache keys are tool name plus serialized arguments. No merged obligation roles or predicate ledger. |
| Observation resolved versus goal predicate satisfied | Partial foundation | World scoring distinguishes goal truth/UNKNOWN/claims; the acquisition layer has no corresponding evidence objects. |
| Typed, provenance-bearing evidence ledger | Partial foundation | Ordered calls/raw observations exist, but no parser-versioned canonical evidence ledger. |
| Conservative validity | Partial, mock-specific | Five logical ticks, public invalidations and bypass under unreliable notification flags. These are not ROS freshness guarantees. |
| Invalidate on write attempt before execution | Missing | Current cache clearing happens after the command response; it is insufficient for ambiguous ROS writes or transport failures. |
| Per-field mutation epochs and read-start phase barriers | Missing | Synthetic world revisions are not dispatch epochs for actual parameter fields. |
| Supported ROS tool/service contracts and parsers | Missing from experiments | Actual ROSA functions exist; the mock experiment instead uses pick/place tools and structured mock returns. |
| Exact instance enforcement for generic ROS calls | Missing | Mock world guards and post-hoc argument checks do not enforce a grounded ROS endpoint/type/request before execution. |
| Cost-aware eligible providers | Missing | `DEPENDENCIES` is a fixed pick/place-to-read mapping, not a ranked candidate-instance registry. |
| Bounded prefix plus residual greedy completion | Missing | No `G(Q,S)`, prefix enumeration, shadow structural state, switching margin or reference fallback. |
| Zero-immediate-coverage discovery enabling bulk read | Missing | No discovery/bulk provider pattern in the movement mock. |
| Root approval followed by actual-result-bound child | Missing | `acquire_context` performs internal reads within one custom tool; it does not return a child AgentAction through AgentExecutor. |
| At most one guarded read continuation at depth two | Missing in required form | Existing internal bundling may perform several reads and notification refreshes; it is not the specified bound. |
| Automatic writes excluded | Implemented for information manager | Current bundles only read. Reliability guards can verify/report; those interventions must remain outside JTVR. |
| Strong greedy comparator | Missing | A deterministic task planner exists, not an evidence-coverage/cost greedy policy. |
| Amortized batching + reuse + equal continuation capability | Missing | The eager read-all bundle is not this comparator. It does not optimize discovery/setup plus compatible group costs. |
| Strong prompted model with identical metadata | Not tested for original scope | Both models have been tested on other tasks; no original-contract comparison exists. |
| Separate LLM/tool/native-operation costs | Partial | LLM calls/tokens, IPC observation counts and elapsed time exist; actual CLI/RPC accounting and policy search cost do not. |
| Same-inference requirement manifest | Missing | Native text is retained by the model adapter, but ordinary agent parsing does not validate a manifest. |
| Oracle-independent execution scoring and trace audits | Implemented foundation | Reusable test infrastructure, with the documented shared simulator/scorer trust boundary. |

The legacy policy string `jtvr` must be described as **fixed dependency bundling**
in any paper or report. Keep its frozen code and provenance; do not silently
rewrite its identity or interpret its thresholds as a verdict on original JTVR.

## Architecture: feasible extensions and current incompatibilities

There is no demonstrated fundamental incompatibility with ROSA. There are
specific missing extension points and protocol conflicts to resolve first.

| Issue | Verified current behavior | Minimum acceptance check / change |
| --- | --- | --- |
| Agent construction | `ROSA._get_agent()` always calls `create_tool_calling_agent`. | Add an optional agent factory while preserving the default; retain the same AgentExecutor. |
| Intermediate steps | The executor maintains tool actions and results; public `invoke` returns the final answer. | Consume actual intermediate steps/dispatch records; do not reconstruct evidence from final prose. |
| Deterministic action history | Installed `format_to_tool_messages` emits only `AIMessage(action.log)` for an ordinary AgentAction, omitting its observation. | A custom formatter must include actual policy observations with explicit provenance. Test that the next model turn actually receives them. |
| Hosted tool-call identity | `ChatSiwc._history` rejects orphan ToolMessages and fabricated/unrecoverable assistant tool calls. | Preserve genuine native calls/IDs. Never invent provider IDs for deterministic continuations; test an explicit policy-observation representation on both backends. |
| Tool binding | The default agent binds one tool menu. The hosted adapter supports `bind_tools` without arbitrary binding options. | Cache bounded menus and enforce exact instances in wrappers; do not assume a `tool_choice` option is supported. |
| Tool effects | Generic `ros2_service_call` can mutate state. | Delegate only a registered, validated GetParameters request; all unknown services and writes remain model-controlled. |
| Arguments and shell execution | Existing ROS tools build CLI commands; the generic execution helper has no general subprocess timeout. | Common exact-instance/scope checks, controlled request serialization and timeout/child-process cleanup for all arms. |
| Evidence validity | Current cache is not field/phase/epoch keyed and clears after response. | Invalidate affected evidence at dispatch, record read-start epochs, reconcile ambiguous acknowledgments without inventing final values. |
| Iteration limits | AgentExecutor iterations and model calls currently tend to move together. | With deterministic continuations they differ. Bound and record executor steps, model requests and native operations independently. |
| Tracing | Current aggregate-tool internals are oracle records, not individual normal AgentExecutor tool dispatches. | Each root and child should appear as its own ordinary tool execution, with a shared fragment ID and actor provenance. |
| Mandatory verification contract | Movement tests require a dedicated `verify_goal` tool. | In parameter experiments, verification is equality evaluated on valid post-write evidence. One read may serve reporting and verification; this is a new shared contract for all methods, not a retrospective movement-score change. |
| Async execution | Existing backend compatibility does not establish a new policy's async semantics. | MVP is synchronous. Do not claim `astream` continuation support until separately tested. |

Important parser constraint: `ros2_param_get` returns CLI text inside a dictionary;
`ros2_service_call` returns response text. These require conservative parsers,
not assumptions that dictionaries already contain usable values. GetParameters
specifies value correspondence by request order. Do not zip a shortened or
ambiguous response onto names and silently claim valid evidence. Unset values,
wrong types and parse failures do not establish a successful numeric goal.

The official [GetParameters interface](https://raw.githubusercontent.com/ros2/rcl_interfaces/jazzy/rcl_interfaces/srv/GetParameters.srv)
supports a list of names and corresponding values. It does not supply an atomic
snapshot or an external-writer consistency guarantee. Shared local epochs cannot
detect arbitrary external writes. Nominal claims require declared writer/freshness
assumptions; concurrent-writer stress must report their limits.

## Minimal scientifically useful experiment: proposal, not implementation

### Research question

Does depth-two prefix-plus-residual evidence selection improve verified acquisition
cost over strong amortized batching when all methods have the same evidence,
capabilities, validity rules and read continuations?

The question is not whether JTVR repairs Qwen's reasoning or performs robot motion.
Reliability interventions and movement experiments remain a separate track.

### Shared substrate

Use the existing ROSA tool names, argument schemas and raw-result shapes for:
`ros2_param_get`, `ros2_param_set`, `ros2_service_list`, `ros2_service_info`,
`ros2_service_call`, `ros2_node_info`, and `ros2_topic_info` where required.
Mock their environment/transport, not a new privileged aggregate API.

Only registered GetParameters calls are eligible automatic service reads. Keep
names, node scope, phase barriers, parsers, cost metadata, validity rules, request
budgets and continuation capability identical in matched arms. Count native
operations inside list-valued wrappers; one wrapper is not necessarily one CLI
command or ROS request.

First isolate policy behavior with annotated user requirements supplied equally
to every arm. These contain required fields/predicates, not hidden values or
optimal actions. Test manifest extraction later on the same ordinary model turn;
do not add a hidden planner inference. Record invalid manifests and fallbacks.

### Four primary arms

| Arm | Decision rule | Fairness requirement |
| --- | --- | --- |
| C: strong prompted ROSA + conservative evidence reuse | Model chooses reads using the full shared capabilities/metadata. | It may select direct or bulk calls and approve the same continuation; no forced redundant reads. |
| G: greedy coverage/cost + shared reuse | Choose currently eligible marginal coverage per estimated cost; acquire supported prerequisites when no useful provider is eligible. | Recognizes already callable batches; same runner and validity rules. |
| B: amortized batching + shared reuse | Compare compatible per-node batch/direct groups, including discovery/setup, cached facts and remaining direct reads. | Same context, all relevant discovery providers, and identical continuations; an exact tie with JTVR is permitted. |
| J: original JTVR minimum | Shared obligations, depth-two read prefixes, prefix cost plus greedy residual, reference retention and switching margin. | Same cost estimates/runner. Predicted bindings remain shadow state until actual results arrive. |

C is the practical cache/model reference; its purely deterministic policy-only
counterpart uses a declared fixed direct-read preference and is only a weak
mechanism control. It must not replace the strong prompted C arm in model tests.
G, B and J are the primary causal selection comparison. B must not be quietly
implemented as eager read-all or as batching that ignores setup costs.

### Tasks and scope

Use eight fixed templates, not a large invented menu:

1. One current parameter: expected no-lookahead-benefit control.
2. Three current parameters with cold discovery.
3. Three parameters with valid cached endpoint/type evidence.
4. Set three parameters, then report and verify those same post-write values.
5. Post-write task reporting for one field plus verification of additional fields:
   expose a genuinely different joint-obligation versus separate-phase decision.
6. Node-scoped endpoint/type summary plus parameter values: test real scope overlap.
7. Two nodes with different required fields: batching must respect node boundaries.
8. Parameter values plus topic endpoint/QoS details: node information must not be
   substituted for a field it does not observe.

The three-color example alone is insufficient. With equal costs, three direct
gets cost 3 units and type discovery plus bulk costs 2; amortized B and J both
choose 2. With one field both choose a direct get; with cached type both can
choose bulk. These ties must appear in the report rather than be manufactured
into an algorithmic advantage.

### Bounded study and staged stop rules

1. **Calibration and integration acceptance.** Capture a few real Jazzy tool
   outputs on isolated test parameter nodes; document parser grammars and measured
   native work. Freeze cost estimates from development tasks. Test policy-action
   history, write barriers, partial parsing, epoch changes and bounds without a
   paid inference. No robot or Gazebo is needed.
2. **Policy isolation.** Eight templates x six predetermined conditions x two
   seeds = 96 fixtures per deterministic policy (G/B/J); also run the weak cache
   mechanism control if useful, for at most 384 policy episodes total. Conditions:
   nominal, cached discovery, high setup cost, unavailable/wrong-type bulk provider,
   partial/format-invalid bulk output, and ambiguous write acknowledgment. For
   read-only templates, the last condition is explicitly an inert negative control.
   Faults attach to entity/tool-instance events, not the nth overall agent call.
3. **Decision before more integration.** If every relevant B/J selection and
   realized cost ties, report no incremental selection benefit in this scope.
   Investigate a grounded mixed-obligation case before building more machinery;
   do not create custom tools or handicap B to manufacture separation.
4. **Small model comparison, only if justified.** Preselect eight representative
   fixtures before policy outcomes are inspected. Four arms x two backends x two
   repetitions x eight fixtures = 128 model episodes. Proposed limit: 12 model
   requests/episode, 768 requests/backend, with a separate bounded tool-execution
   cap. Allow provider-native multiple independent calls equally. This is a screen,
   not a reliability guarantee.
5. **Matched ablations.** On four preselected cases, compare continuation on/off
   for B/J on both backends: 16 additional episodes at one repetition. In policy
   isolation compare joint obligations against role-separated rollout with the
   SAME shared evidence cache. This prevents calling ordinary reuse a joint-policy
   benefit. Depth one versus two uses identical candidates and cost accounting.
6. **Real ROS smoke check.** Repeat a few fixed read/write/readback cases against
   isolated parameter nodes (turtlesim is optional). No manipulator is required.
   Scope to the test nodes; do not expose arbitrary ROS services or live actuators.

This is a proposed upper budget, not an instruction to run it now. Finish shared
contracts and the policy-only decision before spending the model budget. If a
predeclared negative-result stop rule fires, record that outcome as the stage's
decision; do not mark unexecuted later tiers as completed experiments.

### What must be measured

Report task success from post-write observations, accurate failure/UNKNOWN,
false/unsupported success, scope/phase/argument violations, and unresolved fields.
Then report actual wrapper executions, CLI/process work, instrumented logical ROS
requests, LLM calls, input/output tokens, complete wall time, selector CPU time,
parsing/binding time, rejected suggestions, fallback frequency, and B/J sequence
identity. Include bootstrap, writes, failures, automatic reads and final responses.

Calibrate costs on development data only; all matched policies get the same
estimates. If only operation weights are supported, claim operation-cost results,
not predicted latency optimization. Do not double-count measured model latency
and token-derived latency. Ordinary binding is not an inference request.

Keep failures in outcome denominators. Report performance on paired successful
episodes separately, with exclusions and all-attempt cost distributions. A method
that fails early does not earn an efficiency improvement. Use template-clustered
descriptive uncertainty; a small run cannot establish safety/noninferiority.

Suggested keep criterion, to finalize before data collection: preserved observed
verification correctness and at least 10% lower end-to-end or declared acquisition
cost than B on the preregistered opportunity subset, with a positive lower paired
descriptive uncertainty bound and acceptable overhead on simple negative controls.
Model-call savings alone cannot establish a selection contribution if B receives
the same savings from continuation. Report negative and tied results explicitly.

## Recommended Phase 4 revision and commit disposition

Split Stage 4 into 4A (contract/reliability), 4B (original-JTVR policy comparison)
and 4C (small real ROS parameter-service validation). Retain the fixed-bundle work
as an auxiliary engineering control, not the central JTVR arm. Preserve the old
frozen plan and source snapshot; write a new protocol/configuration before new
data, rather than modifying the old freeze in place.

The six-stage roadmap is [PROJECT_ROADMAP_SIX_STAGES.md](PROJECT_ROADMAP_SIX_STAGES.md).
The conditional commit request is recorded for `Lelevinson/rosa-evaluation`, branch
`member/martin`, verified locally. Stage 4 is not yet complete, so the requested
final results commit has not been made. The eventual commit must contain the
audited results, exact protocol/source identity and limitations, not a claim that
an unrun algorithm passed. Use an explicit file list; preserve unrelated work and
exclude credentials, local configuration, environments and raw database files.

Research-repository changes needed for the agent factory are a separate repository
dependency. An evaluation-only commit must reference their reproducible revision
or include an exact reviewed patch; it cannot pretend to contain those changes.

## Scope of this review

All sections of the supplied specification and the pasted response were read.
Local code and installed formatter/factory source were inspected. The official
GetParameters interface was checked. This turn does not independently authenticate
every cited paper, reproduce parent algorithms or establish novelty. Those remain
separate literature/reproduction tasks; the proposed controlled comparison does
not depend on accepting the supplied document's novelty/readiness verdict.
