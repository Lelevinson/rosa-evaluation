# ROSA research recap for independent review

As of 2026-10-21. **Checkpoint report, not the final revised Stage 4 report.**

The shared model interface and an initial mock benchmark work. Baseline v1 is
preserved. Reliability problems have been identified, and corrected scoring and
scripted controls have been tested. The original JTVR specification has now been
compared with the code. Its central selector and continuation mechanism have not
been implemented or evaluated. Stage 4 remains incomplete.

This document records measured results, their limits, the design correction, and
the proposed next experiment. A separate detailed final recap is required after
the revised testing or its predeclared stopping decision. Nothing below should be
read as results from that future experiment.

## 1. Project objective and working constraints

Compare local Qwen3.5 9B with a hosted model accessed through the existing OAuth
adapter, using the same ROSA interface. The two backends are alternatives to test
independently; neither is presumed the permanent primary model. Then evaluate
whether original JTVR evidence acquisition, and eventually verified episodic
memory, improve the combined agent system over strong simpler alternatives.

The user wants candid conclusions, including negative findings, rather than
optimistic claims about research novelty or eventual robot reliability.

The current priorities are:

1. Preserve Baseline v1 and distinguish retrospective checks from new experiments.
2. Define the task contract and score each task from independent state evidence.
3. Separate instruction changes, bounded recovery and enforced verification.
   Attribute repaired behavior to the model plus orchestration, not the model alone.
4. Separate local inference performance diagnosis from behavior changes.
5. Freeze genuinely different evaluation mechanisms before tuning.
6. Test the original JTVR contribution against capable caching, greedy selection
   and amortized batching with identical continuation capabilities.

Mock tests are useful for controlled failure and evidence-validity experiments.
They do not establish manipulation, perception or physics competence. A small
real ROS parameter-service check can validate the retrieval mechanism without
first building a Gazebo arm. Arm integration is a separate engineering milestone.

## 2. Repositories, environment and reproducibility

| Item | Recorded state |
| --- | --- |
| Experiments repository | `Lelevinson/rosa-evaluation`, current branch `member/martin` |
| Research repository | `Lelevinson/rosa-research`, current branch `member/martin` |
| Evaluation base commit | `b3b1d45422331f41416bba55a6f569bf78bb60ab` |
| Research base commit | `18a5f2f962133a0bc490a2f2e79873ab6dca9b1d` |
| Source identity caveat | Both checkouts contain uncommitted work; base commits alone do not reproduce current behavior. Frozen source copies and manifests are necessary. |
| Host / Linux | Windows with WSL Ubuntu 24.04; Python 3.12.3; uv 0.13.3 |
| Research environment | `/home/martin/.local/share/rosa-envs/research`, exposed through the research checkout's `.venv` |
| Inspected agent stack | LangChain 0.3.30, langchain-core 0.3.86, langchain-ollama 0.3.10 |
| Local runtime | Ollama 0.40.6; `qwen3.5:9b`, Q4_K_M |
| Model digest | `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90` |
| Hardware | RTX 4050 Laptop GPU, 6 GB VRAM; 16 GB system RAM |
| Hosted comparator in Baseline v1 | `gpt-6.1-sol`, through the existing OAuth adapter |
| Tracing | Phoenix 20.23.0, client 3.5.0, separate environment and persistent SQLite storage |
| Simulator | Gazebo 8.15.0 and ROS Jazzy foundation installed; arm model/controllers/skills not configured |

The local behavior profile uses an 8192 context, 256 output-token limit,
temperature zero, seed 42 and `use_mmap=True`. These settings do not imply that
local and hosted models have equivalent resource budgets. Mmap was important to
local runtime stability. Historical logs show partial GPU offload, 17/33 layers.

The experiment code uses actual ROSA with isolated mock tools, rather than only
calling the model directly. Native tool-call and shared-interface readiness tests
passed. This demonstrates interface operation, not general robot competence.

## 3. Preserved Baseline v1: what was actually measured

The clean campaign contains **540 scripted controls and 120 live model trials**.
Each backend ran 36 baseline trials and 24 cache trials. Baseline fixtures cover
12 scenario types; repeated instances and cache subsets are not 120 independent
task families.

Primary evidence:

- [Original clean campaign report](../../reports/clean-stage1-4-20261021-r1/REVIEW_REPORT.md).
- [Original evidence archive](../../reports/ROSA_STAGE1_TO_4_CLEAN_RERUN_2026-10-21.zip).

The archive is 9,048,767 bytes. Its preserved SHA-256 is
`721d5960d82f49ea4b0c6f6470ad2c2b02e4e4379720f4b6936a67f13cd3fcad`.
The campaign audit checked 660 trial records and 2,346 hashed files. Earlier
campaigns remain separate and are not pooled into these fresh results.

### Live baseline results under the original scorer

| Measure | Hosted | Local Qwen |
| --- | ---: | ---: |
| Baseline trials | 36 | 36 |
| Original task-handling passes | 30/36, 83.3% | 24/36, 66.7% |
| Achievable cases reaching an independently verified goal | 18/18 | 18/18 |
| Baseline model requests | 211 | 306 |
| Median baseline trial time | 18.95 s | 102.60 s |
| Baseline trial p95 | 35.12 s | 133.61 s |
| All 60 live-trial model requests, including cache arms | 367 | 457 |
| All 60 live-trial reported tokens | 591,714 | 1,077,999 |

Task handling includes correct failure/unknown/refusal behavior when appropriate;
it is not synonymous with physical goal achievement. Both models reached all 18
achievable baseline goals, while differing on other contract requirements.

Hosted had six missing-sensor coverage failures. Local had six accepted-failure
iteration-exhaustion cases and six missing-sensor handling failures. Independent
world/trace audits passed for all live trials; a passing audit means the records
and state reconstruction were consistent, not that the agent passed every task.

The hosted session was revoked after the run. No hosted transport timeout was
recorded in that baseline batch. One local conservative-cache trial timed out
after 240 seconds before action.

### Cache controls

The scripted controls ran 60 fixtures x three policies x three repetitions:

| Scripted policy | Eligible reads | Mandatory checks | Cache hits | Stale uses |
| --- | ---: | ---: | ---: | ---: |
| No cache | 600 | 420 | 0 | 0 |
| TTL | 360 | 480 | 300 | 120 |
| Conservative invalidation | 450 | 420 | 150 | 0 |

Conservative caching reduced eligible reads by 25% here without observed stale
uses. TTL made more stale uses and induced additional mandatory checks. These
are scripted mechanism results; they do not demonstrate saved model inference.

In live cache subsets, hosted TTL and conservative caching each passed 12/12 and
reduced matched eligible reads from 24 to 18, without saving model requests.
Local TTL passed 12/12; conservative passed 11/12. Apparent local savings of five
model requests and four mandatory checks were contaminated by the timed-out
trial. Early termination is not an efficiency improvement.

These results support a limited claim about read reuse in the tested mock world.
They do not establish original JTVR, generalization, or a reliable robotics policy.

## 4. Scoring and reliability issues found after Baseline v1

Baseline v1 remains unchanged. Additional checks were calculated separately from
its preserved records in [retrospective.json](../../reports/phase4-v2/retrospective.json).

The most consequential finding was report compliance. The contract required
`battery_percent=-1` for these non-reading tasks. Local produced an incorrect
battery argument in 18 baseline trials, including 12 otherwise passing trials.
It also attempted 12 picks after the pose observation was UNKNOWN. The mock
controller rejected those attempts. That protection belongs to the controller;
the attempted action still reveals an agent-policy failure.

| Additional retrospective measure | Hosted | Local |
| --- | ---: | ---: |
| Strict contract completion | 30/36 | 12/36 |
| Trials with invalid report arguments | 0 | 18 |
| Trials without a compliant completed report | 6 | 24 |
| Critical prerequisite violations | 0 | 12 |

The 12/36 local result is an additional stricter calculation, not a fresh run and
not a claim that physical goal success fell from 18/18. V1 records do not permit
full reconstruction of raw native argument types before coercion; retrospective
checks cannot invent missing evidence.

V2 engineering now checks raw argument types before coercion, report arguments,
exactly one report, verification at the claim, calls after reporting, known
missing prerequisites, inappropriate retries after a verified failed pick, and
unnecessary action when the goal already holds. Independent audit reconstructs
state and distinguishes model, context-manager and orchestrator actions.

**41 evaluation tests passed**: 17 new Phase 4 tests plus 24 existing tests.
This validates the tested infrastructure cases, not prospective model reliability.
Instruction clarification, bounded recovery and enforced verification need
separate live arms before claiming that any intervention improved behavior.

## 5. V2 preflight: completed controls, no completed live batch

V2 introduced 60 fixtures spanning 12 mechanisms, with six development and six
evaluation mechanisms. Examples include permission revocation after locating an
object, target closure after picking, gripper slip, verification outages and an
already-satisfied goal. These are more varied state transitions, but still share
a simple transfer-task structure.

Final scripted batch: `3088be87-0447-4807-8548-024e05f268c8`.
All **264 scripted trials** passed independent audit: 24 earlier-fixture
reliability controls plus 60 new fixtures under four policies.

| V2 scripted policy, 60 new fixtures each | Strict passes | Eligible reads | Mandatory checks | Hits | Stale uses |
| --- | ---: | ---: | ---: | ---: | ---: |
| No cache | 60/60 | 320 | 220 | 0 | 0 |
| Conservative cache | 60/60 | 300 | 220 | 20 | 0 |
| Eager context acquisition | 60/60 | 405 | 211 | 0 | 0 |
| Fixed dependency bundle, legacy code label `jtvr` | 60/60 | 304 | 214 | 20 | 0 |

The fixed bundle used fewer eligible reads than eager acquisition but slightly
more than conservative caching. Differences in mandatory-check counts include
avoided rejected controller checks; accepted-action checks were audited. There
is no demonstrated model-call or latency improvement from scripted controls.

Two interrupted scripted-only preflight candidates are preserved under
`reports/phase4-v2/preflight-history/`; they were not used as live model results.
The final source freeze is timestamped `2026-10-21T10:17:29.308225+00:00`.
The specification review did not change its frozen model/world/scorer/policy code.

### Local inference diagnostic

Nine short native requests tested three runtime profiles. All produced the
expected `observe_robot` call. Recorded generation rates, in tokens/second:

| Profile | Three observed rates |
| --- | --- |
| 8192 context, automatic offload | 10.45, 10.55, 9.28 |
| 4096 context, automatic offload | 9.60, 9.49, 8.82 |
| 8192 context, forced 24 GPU layers | 14.47, 15.04, 14.44 |

See [local-diagnostics.json](../../reports/phase4-v2/local-diagnostics.json).
The samples include cold/warm differences and uncontrolled competing host work.
They do not establish sustained task throughput, behavioral improvement, or
stability of the forced-offload setting. The behavioral primary profile was not
changed. Models were unloaded after diagnostics.

### Why the prospective live run stopped

The superseded hosted batch was `00879ccd-8e51-4b84-9ce5-50163da5bc55`.
It was interrupted while waiting for consent, after the original specification
changed the required experiment. It made **zero model requests and zero trials**.
Cleanup recorded `NO_TOKEN_SESSION`; the local successor never started.

The supervisor's failed-child status records this deliberate interruption, not
a measured model failure. The monitor and temporary sleep hold were released.
The old sign-in prompt is retired. See [DISPOSITION.md](../../reports/phase4-v2/DISPOSITION.md).
No revised live batch is currently running, and there are no prospective V2
reliability or original-JTVR model results to report.

## 6. Original JTVR: correction to the research question

The authoritative supplied design is preserved byte-for-byte at
[JTVR_Final_Technical_Specification_ID(1).md](<specifications/JTVR_Final_Technical_Specification_ID(1).md>).
SHA-256: `cd18df7ec554b5ca845c4bfbf9ff1971738801a9aa13b0da5a7b3e24abadc2df`.
It is a proposed design, not proof of implementation or experimentally established
novelty. Its literature claims have not all been independently verified here.

Original JTVR contains five central ideas:

1. Joint, deduplicated task-report and verification evidence obligations, qualified
   by entity, field, scope, phase and epoch.
2. Cost-aware read selection using bounded lookahead and estimated remaining
   acquisition cost, including discovery that enables a later bulk read.
3. Conservative evidence validity and invalidation on write dispatch, including
   uncertain acknowledgments and post-write observation barriers.
4. Guarded read-only continuations through the ordinary agent executor, possibly
   avoiding a second model inference for a safe child read.
5. Comparison with strong amortized batching that receives the same reuse,
   discovery, batching and continuation capabilities.

The existing `phase4/client.py` implementation named `jtvr` is a fixed dependency
bundle behind `acquire_context`. It lacks the central joint-obligation and
residual-cost selection mechanism. Treating its results as a test of original
JTVR would be scientifically misleading. This was an overly narrow earlier
interpretation and is corrected explicitly in the roadmap.

| Component | Current state |
| --- | --- |
| Shared model factory, ROSA tool execution and tracing | Implemented foundation |
| Stateful mock world and independent evaluator | Implemented; contract corrections tested |
| Conservative cache and invalidation controls | Implemented for existing mock semantics |
| Fixed dependency acquisition bundle | Implemented auxiliary control, not original JTVR |
| Joint obligation manifest and provenance-rich evidence ledger | Missing |
| Tool-instance contracts, cost calibration and scoped parsers | Missing for original-spec experiment |
| Depth-two prefix selection plus greedy remaining-cost estimate | Missing |
| Write-dispatch invalidation and phase-qualified evidence | Current post-response cache clearing is insufficient |
| Ordinary executor read-only child without additional inference | Missing |
| Strong amortized batching with matched continuation | Missing |
| Original-spec policy and live comparison | Not run |

### Architecture constraints that must be resolved

ROSA currently constructs the standard tool-calling agent inside `_get_agent`;
there is no configurable custom agent factory. The installed LangChain tool
agent accepts a formatter hook, but ROSA does not expose it. Its default formatter
retains actual observations for native `ToolAgentAction` steps; for an ordinary
`AgentAction`, it retains only the action log. A deterministic child therefore
needs explicit observation formatting and provenance. Fake native call IDs are
not an acceptable substitute.

The hosted adapter retains native history privately and rejects orphan tool
messages or unsupported binding options. A custom continuation must be tested
against both backends' real history rules. This is an integration requirement,
not evidence that the approach is fundamentally incompatible.

Existing ROS tools provide individual parameter get/set, service listing/type
inspection and generic service calls. A registered, scoped call to ROS standard
`GetParameters` can provide bulk access without inventing a special JTVR API.
Generic services are not automatically read-only. Current CLI wrappers lack a
general timeout, and their returned text needs conservative parsing. A successful
write acknowledgment does not establish the final parameter value.

The current mock task requires a dedicated `verify_goal` call. A parameter study
needs a separately frozen, equally applied contract allowing a post-write value
observation to satisfy both reporting and verification. Do not silently change
the old movement-task scoring to create that overlap.

## 7. Proposed minimum experiment, not yet implemented

The full component audit and protocol proposal are in
[JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md](JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md).

Four matched model arms are proposed:

| Arm | Definition |
| --- | --- |
| C | Capable prompted ROSA with conservative evidence reuse; retains access to batching and the common continuation mechanism |
| G | Greedy marginal eligible coverage per cost, with reuse |
| B | Amortized batching with reuse, setup/discovery costs, remaining direct-read costs and the same continuations |
| J | Joint obligations, bounded depth-two prefix selection plus greedy remaining-cost estimate, switching margin and greedy reference |

All arms receive the same tool contracts, costs, validity rules, raw outputs,
parsers and continuation capabilities. No custom aggregate API is reserved for J.
Native multiple independent tool calls remain available equally. A fixed direct
read control may help diagnose caching, but must not replace capable C or B.

Eight task templates cover one parameter; three cold parameters; three with
cached discovery; set/report/verify overlapping values; distinct task/verification
fields; node-scoped endpoint plus parameter evidence; two-node scope; and mixed
parameter/topic information. The last cases must use actual tool capabilities,
not assumed parameter or QoS coverage from node information.

Three direct reads versus discovery plus one bulk read is not sufficient evidence
of JTVR's unique value. If discovery plus bulk costs two units, strong B and J
can both choose it. With one field both can choose direct access; with valid
cached type evidence both can choose bulk. Those ties are expected controls.

Proposed sequence and ceilings:

1. Capture real Jazzy outputs on isolated parameter nodes; validate parsers,
   action history, write barriers, failure handling and cost estimates. Freeze
   development calibration separately from evaluation data.
2. Run policy-only G/B/J on 8 templates x 6 predetermined conditions x 2 seeds:
   96 fixtures per policy, 288 episodes. An optional weak cache control brings
   the maximum to 384. Annotated manifests are shared equally in this tier.
3. If B and J select equivalent sequences with equivalent costs throughout the
   grounded scope, report that finding and stop before expensive integration.
4. Only if justified, run 8 preselected fixtures x 4 arms x 2 backends x 2 repeats:
   128 model episodes, at most 768 model requests per backend.
5. Continuation on/off: 4 preselected cases x B/J x 2 backends, one repeat:
   16 additional episodes, at most 96 requests per backend. Joint-versus-separated
   obligations must share the same reuse cache; depth-one/two comparisons must
   share candidates and cost accounting.
6. Run a small real ROS parameter read/write/readback smoke check. No arm needed.

The six policy conditions are nominal, cached discovery, high setup cost,
missing/wrong-type bulk provider, partial/malformed bulk output, and ambiguous
write acknowledgment. The last is an explicitly inert control for read-only
tasks. Faults attach to entity/tool-instance events, not overall call number.

Separate reliability follow-up is proposed as six development fixtures x four
independent intervention configurations x two repeats: 48 episodes per backend,
at most 672 requests. If every proposed tier runs, reliability plus model JTVR
and continuation arms total 120 episodes and at most 1,536 requests per backend.
These are proposed caps, not active authorization prompts or completed runs.
Calibration and integration checks need their own declared accounting.

Measure goal/verification correctness, unsupported success, unresolved fields,
scope and argument violations, actual tool/CLI/ROS request work, model requests
and reported tokens, total wall time, selector/parser/binder overhead, fallbacks,
and B/J sequence identity. Include writes, automatic reads and final responses.
Do not equate an iteration cap with a model-request cap once automatic children
exist. Distinguish policy tests with annotated manifests from end-to-end manifest
extraction using the ordinary inference budget.

A suggested criterion, to finalize before collection, is preserved observed
verification correctness plus at least 10% paired cost/time benefit over B on a
predeclared opportunity subset, with a positive lower descriptive uncertainty
bound and acceptable negative-control overhead. Small experiments cannot prove
safety or reliability noninferiority. Failures remain in outcome denominators;
failed early exits do not earn speed credit. Ties and negative findings are valid
outcomes and must not trigger baseline weakening or invented favorable tools.

## 8. Six-stage roadmap and actual completion status

The full roadmap is [PROJECT_ROADMAP_SIX_STAGES.md](PROJECT_ROADMAP_SIX_STAGES.md).
These work packages do not retroactively rename the historical master-plan gates.

| Stage | Status and next exit requirement |
| --- | --- |
| 1. Shared local/hosted ROSA interface | Demonstrated with mock tools. Preserve backend parity and validate custom history changes before using continuations. |
| 2. Stateful contract and independent scoring | Working foundation; corrections tested. Original-JTVR evidence/phase contracts and ROS parsers remain. |
| 3. Baselines and reliability | V1 pilot complete. Prospective isolated reliability interventions are pending. |
| 4. Caching and original JTVR | Cache controls complete; original selector unimplemented. Split into 4A reliability, 4B policy comparison, 4C real ROS parameter validation. |
| 5. Verified episodic memory | Not started. Requires history-dependent tasks and matched retrieval/example/token controls. |
| 6. Gazebo arm and eventual hardware | Simulator foundation installed; arm integration not started. Robot model, controllers, skills and task/safety contract remain unspecified. |

Stage 6 preparation can begin before Stage 5 if scope is defined. Episodic memory
is not a prerequisite for connecting an arm simulator. Neither stage should be
used to hide unresolved scoring or claim untested JTVR benefits.

## 9. Commit and final-report requirements

The user requested committing results/files to the experiments repository on
their branch **after the newly tested Stage 4 is finished**. That condition has
not been met, so the final results commit has not been made. Current destination
is `Lelevinson/rosa-evaluation`, branch `member/martin`.

Root `reports/` artifacts sit outside that repository, and generated results may
be ignored. The eventual commit needs an explicitly curated evidence package
inside the repository, without tokens or private session state. A commit to the
evaluation repository does not automatically preserve sibling research changes;
record the exact research revision and any required reviewed patch/source copy.
Preserve existing unrelated work and stage explicit paths.

The final recap must include:

- Frozen protocol, task contracts, hypotheses, success/stop criteria, source and
  fixture hashes, dependency versions, model identity/settings and hardware.
- Every attempted/completed/interrupted trial, arm, request/tool budget, retry,
  failure and exclusion, with durable evidence references.
- Original v1 scores and separately labeled retrospective calculations.
- Independent scoring/trace audits, actual controller protection, and attribution
  of orchestration repairs.
- Paired outcome and cost tables, all-attempt denominators, descriptive uncertainty,
  B/J ties, failed trials and overheads; no speed credit for early failure.
- Separate reliability, inference-diagnostic, policy-only, model and real ROS tiers.
- Deviations from the freeze, canceled runs, cleanup and limitations.
- Exact committed branch and commit SHA, artifact checksums and reproduction
  instructions. Unrun tiers must remain labeled unrun.

## 10. Questions for ChatGPT's review

1. Does the proposed mixed-obligation scope offer a grounded distinction between
   bounded residual-cost selection and a correctly implemented amortized baseline?
   Which cases should be expected to tie?
2. Are evidence resolution, goal truth, post-write phase barriers and failure
   reporting sufficiently separated to avoid rewarding known-wrong values or
   repeated useless acquisition?
3. Are the matched batching/continuation capabilities strong enough to isolate
   selection from ordinary reuse and inference amortization?
4. Is the proposed stopping rule appropriate before investing in the custom ROSA
   runnable, especially if policy-only B/J results are identical?
5. Which reliability interventions and manifest-extraction checks are necessary
   before interpreting any end-to-end advantage?
6. Should the first real ROS check stay with parameter nodes, and what specific
   robot/task would justify the later Gazebo integration effort?

The current evidence supports a functioning experimental foundation and limited
cache results. It also exposes material local contract failures and a mismatch
between the earlier bundle and original JTVR. It does not yet support a claim
that original JTVR works, fails universally, or constitutes a novel contribution.
