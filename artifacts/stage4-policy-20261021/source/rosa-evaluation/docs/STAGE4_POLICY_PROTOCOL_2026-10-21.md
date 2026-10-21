# Stage 4: frozen policy comparison protocol

Protocol date: 2026-10-21. Scope authorized by the user's request to proceed with
the three-algorithm comparison after the independent checkpoint review.

This is a new experiment, separate from Baseline v1, the canceled V2 live batch,
and the fixed dependency bundle previously labeled `jtvr`. No original-JTVR
custom ROSA Runnable or new live-model batch is included in this protocol.

## Question and permitted conclusions

Does bounded prefix-plus-greedy-residual selection improve acquisition cost over
strong amortized batching on actual ROSA-supported read patterns, after giving
both the same evidence reuse, setup/discovery information and continuation runner?

Algorithm behavior uses annotated task manifests. Model ability to communicate
those requirements is a separate unmeasured dependency. A validator is tested
for missing fields/roles, wrong predicates and expanded scope. That does not
establish natural-language extraction quality for either model.

The experiment must demonstrate a plausible selection opportunity before
claiming a lookahead benefit. No specialized aggregate tool or artificial broad
coverage provider may be added to create one. Negative or tied results can
justify stopping full integration in this scope, but cannot disprove the method
for every future catalogue.

## Shared catalogue, contracts and acquisition runner

Existing tool names/schemas/raw shapes: `ros2_param_get`, `ros2_param_set`,
`ros2_service_list`, `ros2_service_info`, `ros2_service_call`, `ros2_node_info`,
`ros2_topic_info`. The real ROSA wrappers are unchanged. Parameter-service reads
use standard `rcl_interfaces/srv/GetParameters`; unknown services are excluded.

Two isolated nodes `/jtvr_alpha` and `/jtvr_beta` declare integer parameters
`alpha`, `beta`, `gamma` and publish a string status topic. These are ordinary
test-node fields, not invented tools. Node information may provide service
endpoint/type metadata, never parameter values or topic QoS. Topic QoS evidence
comes only from verbose topic information.

All methods use the same canonical entity/field/phase keys, run-isolated ledger,
per-field epochs, raw-result references, parsers, validity ages and failed-provider
records. Task and verification roles are deduplicated for all primary methods.
Numeric goals are evaluated separately from observation resolution.

Writes are a fixed authorized fixture phase, not decisions made by any selector.
Dispatch invalidates pre-write evidence before execution; ambiguous acknowledgment
does not supply final values. A read must start after the completed-write barrier
and match the current local epoch. Delayed, partial and invalid observations have
targeted tests. Local epochs cannot detect arbitrary external writers; nominal
experiments assume no unobserved concurrent writer. The external-writer limitation
is explicitly tested and disclosed, not presented as a solved guarantee.

All selectors can schedule at most two read executions per fragment. A child is
rechecked against actual root results, matching type, remaining names, epochs,
scope and budget. Root failure/ambiguous parsing cancels it. Each action remains
an individual transport execution. This is a policy-only runner, not an
AgentExecutor integration. Policy decisions are not counted as model requests.

Limits: 24 acquisition executions and 24 decisions per episode; greedy simulation
32 steps; JTVR depth two, at most 16 retained roots and 128 evaluated prefixes per
decision. Keep the greedy reference first action. Switch only for an estimated
improvement exceeding 1% of the smallest common tool cost plus 0.0001 cost units.
This is an execution-cost objective; it does not model hypothetical LLM latency.
The greedy reference remains available if search is capped or unprofitable.

## Three algorithms

- **G, greedy:** eligible marginal required-field coverage per estimated cost.
  A currently callable bulk read is an ordinary provider. Acquire a supported
  prerequisite only if no useful provider is eligible.
- **B, amortized batching:** enumerate compatible per-node direct/bulk strategies,
  include setup through either service type inspection or node information, credit
  required node-summary overlap, include leftover direct reads and required topic
  information, and select the cheapest full group completion. Replan from actual
  results. It receives the same read continuations as J.
- **J, original-spec policy minimum:** compare bounded feasible read prefixes plus
  greedy estimated remaining acquisition cost against the retained greedy
  reference. Only hypothetical coverage/structural sets enter simulation; imagined
  values never enter the actual evidence ledger. Replan after actual results.

This implements the specified selection core for the declared catalogue, not the
full original JTVR system. No manifest-generating LLM, root approval, custom
scratchpad formatter, or production Runnable is claimed implemented.

## Development calibration and real validation

Before freezing this policy run, capture actual ROSA wrapper outputs on isolated
Jazzy nodes in ROS domain 173 with localhost discovery. Bounded argv transport
replaces only the wrappers' subprocess helper. Server callbacks independently
count parameter RPCs; DDS discovery is not an RPC count. Two sequential development
samples per read tool give median cost estimates. These small measurements are
operational estimates, not stable latency guarantees or evaluation outcomes.

Calibration is stored separately under `ros-calibration/`. A list-valued two-node
wrapper probe confirms its multiple native commands. Bootstrap service-list and
cache warm-up acquisition costs are charged in every policy episode. Writes are
also charged. Report acquisition-only and complete-episode costs separately.

After the policy run, execute five nominal templates on real transport under all
three policies, one repeat each (15 episodes): one parameter, three cold, node
summary plus parameters, two-node scope, and write/report/verify. Fixed shuffled
order seed 20261021. Record actual wrappers, CLI commands, server RPCs, raw outputs,
observations, source references and elapsed time. Compare parsed values against
separate server callback values. This is a smoke check, not a powered speed study.

## Fixed fixture matrix and sensitivity analyses

Eight templates:

1. One parameter, expected no discovery/lookahead benefit.
2. Three cold parameters, expected discovery/bulk opportunity.
3. Three parameters with warm type metadata, bulk already eligible for G.
4. Set three values; report and verify those same post-write fields.
5. Report one post-write field and verify it plus two other fields.
6. Node-scoped summary plus parameter values, giving genuine metadata overlap.
7. Two nodes, preserving separate scopes and compatible batches.
8. Parameter values plus topic QoS, which node information cannot supply.

Each uses six declared conditions and two value seeds: nominal, cached discovery,
fourfold setup-cost stress, wrong bulk type, partial bulk response, ambiguous write
acknowledgment. Seed zero partial output has a shortened positional list and is
rejected; seed one retains list alignment with one unset entry, allowing only the
other numeric entries. Failures are tied to provider/node events. Ambiguous-write
faults are inert on read-only templates. Seeds and overlapping warm conditions
are repeated controls, not independent task families.

Primary: 96 fixtures x G/B/J = **288 episodes**, using calibrated nominal tool
costs and explicit discovery. Costs are fixed for all methods; faults/hidden
values are unavailable to selectors.

Two sensitivity profiles repeat the same 288 each:

- Unit native-command costs, with the same fourfold setup stress.
- Prior standard-service type knowledge permitted equally, making bulk callable
  without a new discovery observation. Wrong actual type still fails execution.

Ablations on all 96 fixtures: J depth one (96), and B/J role-separated rollout
with the SAME shared ledger (192). **Total policy-only ceiling: 1,152 episodes.**
Maximum model requests: **zero**. No OAuth consent is needed for this tier.

Role separation acquires task fields first, then verification-only fields; shared
evidence can satisfy both phases. It must not intentionally clear the cache to
manufacture a joint-policy advantage. The post-write phase and epochs remain
unchanged. Depth one may already anticipate discovery through its greedy tail;
there is no assumption that depth two must outperform it.

## Evidence, audit and decision

Freeze fixtures, protocol, source, supplied original specification and development
captures before the full run; refuse overwrite and refuse changed frozen sources.
Retain full per-episode traces, all failed attempts, parser outputs, evidence and
decisions. Audit persisted records separately from the selector/parser execution.
The mock oracle and its producer share implementation authorship; this is not a
blinded independent replication.

Primary opportunity subset, fixed here: templates 2, 4, 5, 6, 7 under nominal,
cached-discovery and high-setup conditions (30 paired fixtures). Expected simple
controls and faults must still be reported. Compare verified outcome rates and
all-attempt costs. Paired successful cost summaries cannot hide failed episodes.

Report G/B/J costs, actual policy CPU/parse time, simulated native work, complete
versus acquisition-only costs, B/J sequence identity, depth and role ablations,
and 8-template-cluster descriptive bootstrap intervals (seed 20261021, 2,000
resamples). These intervals describe this small chosen suite, not a population
safety guarantee. Simulated calibrated costs are not measured ROS end-to-end time.

Criterion to justify full model integration: preserve observed verification
correctness and demonstrate at least 10% paired complete modeled-cost improvement
over B on the opportunity subset, with a positive lower descriptive uncertainty
bound, plus explainable manageable policy overhead. Report stronger-baseline ties
and negative controls. If the criterion fails, do not build the full Runnable or
start the large hosted/local JTVR study on the strength of beating G alone.

Do not stop solely on simple triplet ties. Examine mixed obligations, node-info
overlap, scope separation, partial results, cached facts, cost stress and targeted
requirement-change tests first. Assess catalogue difficulty explicitly: this
registered subset has per-node compatible groups, few alternative providers and
little cross-group overlap. If B solves it just as efficiently, that is a limit
of the currently grounded opportunity, not permission to invent harder tools.

V2 live reliability remains a separate unfinished work package. Even a successful
policy tier would not establish model manifest quality, model reliability or
robotics performance. The final Stage 4 completion and results commit remain
conditional on the appropriate remaining work or an explicitly documented scope
decision; do not mark all of Stage 4 done after these policy tests.
