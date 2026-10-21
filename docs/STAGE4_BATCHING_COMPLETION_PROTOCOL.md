# Final Stage 4 protocol: reliability and end-to-end batching

Date: 2026-10-21. Authorized scope: complete Stage 4 using amortized batching,
preserve the negative original-JTVR result, commit the files/data/results on the
user's experiments branch, and produce a detailed report for independent review.

This is a new frozen protocol. Baseline v1, frozen V2 preflight and the 1,152
policy-only / 15 real-ROS JTVR comparisons remain unchanged. No JTVR lookahead
extension or production custom agent Runnable is planned.

## Track A: reliability, separately identifiable interventions

Both Qwen3.5 9B and hosted gpt-6.1-sol run six existing development fixtures:
transfer, accepted failure, missing sensor, variants zero/one. Compare original
instructions, clarification only, bounded recovery only, report-time enforced
verification only. Two repetitions, balanced cyclic arm order: **48 trials per
backend**. Every trial uses a fresh agent, world and cache. No episodic memory.

Use the corrected V2 contract and independent state reconstruction. Preserve
original instructions in the control and do not combine interventions. Count
orchestrator verification/report/stop separately. Controller-rejected unsafe
attempts still count as agent prerequisite violations. Report physical goals,
strict contract compliance, operational failures and system repairs separately.

## Track B: batching in the real ROSA model loop

Eight fixed nominal tasks (two repeats, two arms): one parameter, three cold,
three with charged warm type metadata, set/report/verify three, mixed task versus
verification fields, node summary plus parameters, two nodes, parameters plus
topic details. **32 trials per backend**, 16 paired arm comparisons. Scoped test
nodes in ROS Jazzy domains 174/175, no robot motion or arbitrary services.

The actual existing ROSA AgentExecutor and existing local/hosted backend factory
are used. No change to the research agent core is necessary. Existing primitive
ROSA tools retain their names/schemas and are wrapped for exact scope enforcement,
dispatch-time invalidation, conservative parsing and native-operation records.

### Fair shared orchestration interface

Both arms receive identical tools, prompts, cost guidance, cached evidence and
the same read-only convenience executor, `read_parameter_evidence`. It accepts
model-generated node/names/report_names/expected_values and a preferred direct,
bulk or node_bulk strategy. Existing primitives, including generic registered
GetParameters calls, remain available. Strong prompting explicitly teaches the
discovery/bulk cost tradeoff and node-summary/type overlap to both arms.

- Reference: **strong prompted ROSA, model-selected plan**, with the matched helper
  and primitive reads. It honors the model's preferred plan.
- Candidate: **the same ROSA plus amortized plan selection**, using calibrated
  costs and the model's validated declared requirements. It can replace an
  inefficient preferred plan with the amortized minimum.

This reference is augmented with the same convenience executor rather than an
untouched upstream ROSA baseline. It is deliberately capable of selecting the
same bulk plan and executing its read continuation in one model tool call. No
capability or continuation is reserved to the candidate. Automatic helper reads
are nested native operations, not extra native assistant tool-call messages.
No inference savings are credited to a continuation facility denied to reference.

This is an engineering evaluation of adding deterministic plan selection to the
matched interface. It does not claim to reproduce untouched upstream ROSA or test
the full original-JTVR architecture. Extra tool schemas/tokens are shared costs.

### Manifest quality and conservative execution

The native helper arguments are the model's structured requirement manifest,
produced during an ordinary inference; no hidden extraction inference is made.
Record first manifest validity, all manifest attempts, node/field coverage,
bypassing the helper, incomplete roles/targets and phase errors. The validator
checks a supported task template against the public request's fields/targets;
it does not supply omitted fields to the selector. Invalid manifests execute no
hidden reads and return a bounded error so the model may correct or use primitives.

Read-only tasks cannot write. Writes are restricted to exact requested values.
Invalidate at dispatch, before acknowledgment. Final numeric evidence must be
acquired after all requested writes on that node complete. Acknowledgments are
not values. Read-start epochs, source raw data and post-write phase are recorded.
External writers are excluded by scope assumption; no atomic snapshot guarantee.
No automatic write/recovery is introduced by batching.

One report must accurately contain requested reporting values, acknowledge
required metadata, and have current evidence for all verification predicates.
Known incorrect targets are failure; missing evidence is unknown. Nominal tasks
are achievable, so failure/unknown remain task failures. Any calls after report,
unauthorized attempt, raw argument-type violation, or unsupported report fail the
strict contract. Independent evaluator parameter queries occur outside trial
metrics and are recorded separately from agent work and environment resets.

Both arms keep the same conservative evidence ledger. Metadata warm-up is charged.
Native operations inside helpers receive individual actor-tagged Phoenix TOOL spans
and raw records. The installed LangChain instrumentor may parent explicit spans
to the run rather than the automatic helper span; audits use explicit provenance
to distinguish them. Ordinary model tool dispatches are counted separately. One
wrapper is not silently counted as one ROS request. Actual server callback counts
exclude DDS discovery. Record model calls/tokens/truncation, wall time, CLI work,
server requests, selector/parsing overhead, reports and all failures. The common
parameter CLI transport allows five seconds for node discovery and 35 seconds
per subprocess, records canceled executions, and cleans up child process groups.
Infrastructure graph readiness/reset is recorded outside trial acquisition work.

## Bounds, order and model settings

80 trials/backend = 48 reliability + 32 batching. Reliability max 14 model
requests/trial; batching max 12. **Hard cap 1,056 requests/backend**, 240 seconds
per trial, six hours/backend. Native acquisition/write budget 24 per parameter
trial. The common helper is bounded by that budget; it can execute a direct
list or a discovery-plus-bulk plan in either arm. No custom AgentAction child or
separate continuation ablation is needed for this matched helper implementation.

Within each backend, run reliability then batching. Counterbalance arm order
across repetitions; do not pool the two models. Run hosted then local sequentially.
Local profile unchanged: context8192, output256, temperature0, seed42,
reasoningfalse, mmaptrue, automatic offload. Hosted uses exact account catalog
slug gpt-6.1-sol with account sampling defaults. Provider KV state cannot be reset
or equated; record that limitation. No model upgrades or tuning after evaluation.

Hosted consent is fresh, tokens remain in memory and are revoked on exit.
Interrupted/failed attempts are preserved rather than silently overwritten.
No unplanned evaluation repeats to improve results.

## Preflight, freeze, audit and decision criteria

Before live inference: run relevant tests including actual ROSA synthetic native
calls, then all eight tasks under both plans with real ROS and scripted public
requirements. Freeze source, fixtures, protocol, calibration, dependency/runtime
identities and preflight artifacts. Verify the previous evidence remains intact.
The experiment is not independently authored/blinded; tests share task templates.

Audit every persisted trial against independent state evidence, raw arguments,
server callback values and Phoenix traces. A passing audit is not a passing task.
Report every operational/contract failure and all planned denominators. Use
paired fixture/repetition tables and template-cluster descriptive uncertainty;
this small screen cannot establish a safety guarantee or model noninferiority.

Retain batching as a default in this tested interface only if it has no observed
strict-completion loss against the matched model-selected reference and gives
at least 10% paired end-to-end time or native-work reduction on successful
matched episodes, with consistent direction across repeats. Include all-attempt
costs and failures separately; no speed credit for early failure. Differences in
host/local outcomes must be reported, not pooled to manufacture the criterion.
If benefits are absent, keep the simpler configuration and retain batching as
optional experimental code. No requirement to meet a success threshold to
finish Stage 4: an audited simplify/stop decision is a valid completion.

End deliverables: detailed results/conclusions/limitations/next steps report,
machine-readable per-trial evidence and trace exports, source identity and
reproduction instructions, preserved original-JTVR negative result, and explicit
commit on member/martin in Lelevinson/rosa-evaluation. Include a reproducible
snapshot/patch of required sibling research changes; an evaluation commit alone
cannot reproduce uncommitted research source. Exclude credentials/local databases.
Recommend a specified Gazebo robot/task next if results justify it; episodic
memory remains a separate history-dependent research question.
