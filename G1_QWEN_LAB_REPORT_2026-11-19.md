# G1 Qwen lab results and handoff

Date: **2026-11-19**. Status: **execution complete; human adjudication incomplete**.
**Lab hardware; not directly comparable to M4.** These are AI-authored G1 mock cases.

All **76/76 scheduled attempts** finished in one uninterrupted batch. There were **56 PASS, 17 FAIL, 3 PENDING_HUMAN_REVIEW and no infrastructure-censored trials**. Local and persisted Phoenix audits passed for all 76 attempts. The original 3,796 frozen inputs and the 81-file Qwen backend assembly remained unchanged.

The macro condition used fewer model calls and less measured task time. Its preliminary known-goal correctness was higher in this batch, but Qwen still failed substantial parts of the catalogue. This does not demonstrate parity with Sol or a general reliability improvement.

## What was run

The owner's reviewed launch authorization covered the same 38 frozen G1 cases in two conditions: model-managed primitives and the simple bounded macro. Each condition has 38 attempts. Both domains, arm and base, used their frozen mock adapters and independent observer. This was not Gazebo or physical-robot execution.

Execution ran through SSH on the lab's existing Jazzy container. No Sol rerun, optional first-turn replay, catalogue-size probe, new model download, prompt tuning or runtime repair was added. The completed Sol batch retains its original hosted-model and laptop-orchestration provenance.

The batch started at **19:45:22 Taipei time** and ended at **20:05:33**, lasting **1,210.25 seconds (20 minutes 10 seconds)**. It spent **198 inference requests plus one earlier auxiliary model-load request = 199/611 charged requests**. No infrastructure retry or failed-trial replacement occurred.

Original bounds remained: eight-hour backend window, eight decision calls/task, 1,024 output tokens/call, 2,048 observed output tokens/task, 360 seconds/task, ten native operations, sixteen tool attempts, three corrections and at most one dispatch. Only the existing narrow HTTP 502/503/504 rule could use the three-request reserve; it was not used.

## Correctness: keep the denominators separate

| View | Primitives | Macro |
|---|---:|---:|
| Scheduled attempts | 38 | 38 |
| PASS | 26 | 30 |
| FAIL | 11 | 6 |
| Outcome pending human review | 1 | 2 |
| Infrastructure-censored | 0 | 0 |
| Known-goal tasks only | 26/36 (72.2%) | 30/36 (83.3%) |
| Arm known-goal tasks | 13/18 | 15/18 |
| Base known-goal tasks | 13/18 | 15/18 |

Known-goal figures exclude the two ambiguous cases in each condition. Across the 36 known-goal pairs, both conditions passed 25; macro alone passed five; primitives alone passed one; neither passed five. This is a small, grouped sample, not proof of a population-level reliability advantage.

There are **four new clarification transcripts to review**, although only three primary outcomes are undecided. One primitive ambiguous trial already fails structural/runtime requirements; its missing semantic rating does not erase that failure. The frozen final-analysis bridge still requires actual semantic judgments for all four. No Sol or development ratings were reused.

### Per-family outcomes

Entries show **PASS / FAIL / pending**. There is one run per case and condition.

| Domain / task kind / native depth | Primitives | Macro |
|---|---:|---:|
| Arm inspection, depth 1 | 2 / 1 / 0 | 3 / 0 / 0 |
| Arm inspection, depth 2 | 3 / 0 / 0 | 3 / 0 / 0 |
| Arm inspection, depth 4 | 3 / 0 / 0 | 3 / 0 / 0 |
| Arm inspection, depth 6 | 3 / 0 / 0 | 3 / 0 / 0 |
| Arm missing prerequisite | 0 / 1 / 0 | 0 / 1 / 0 |
| Arm unavailable source | 1 / 0 / 0 | 1 / 0 / 0 |
| Arm write | 1 / 2 / 0 | 2 / 1 / 0 |
| Arm partial-write fault | 0 / 1 / 0 | 0 / 1 / 0 |
| Arm ambiguous request | 0 / 1 / 0 | 0 / 0 / 1 |
| Base inspection, depth 1 | 1 / 2 / 0 | 1 / 2 / 0 |
| Base inspection, depth 2 | 3 / 0 / 0 | 3 / 0 / 0 |
| Base inspection, depth 4 | 3 / 0 / 0 | 3 / 0 / 0 |
| Base inspection, depth 6 | 3 / 0 / 0 | 3 / 0 / 0 |
| Base missing prerequisite | 1 / 0 / 0 | 0 / 1 / 0 |
| Base unavailable source | 1 / 0 / 0 | 1 / 0 / 0 |
| Base write | 1 / 2 / 0 | 3 / 0 / 0 |
| Base partial-write fault | 0 / 1 / 0 | 1 / 0 / 0 |
| Base ambiguous request | 0 / 0 / 1 | 0 / 0 / 1 |

## Efficiency and speed

### All scheduled attempts

| Measure | Primitives | Macro | Macro difference |
|---|---:|---:|---:|
| Model calls | 123 | 75 | 39.0% fewer |
| Input tokens | 264,961 | 152,127 | 42.6% fewer |
| Output tokens | 25,878 | 18,791 | 27.4% fewer |
| Native operations | 100 | 106 | 6.0% more |
| Summed measured task time | 322.22 s | 239.86 s | 25.6% less |
| Mean task time | 8.48 s | 6.31 s | |
| Median task time | 7.93 s | 5.90 s | |
| Invalid attempts | 9 | 2 | |
| Trials with length stop | 4 | 3 | |
| Trials with budget exhaustion | 0 | 0 | |

All 198 inference calls have returned usage and the six Ollama timing fields. The auxiliary load's omitted internal usage remains **NOT_RECORDED**, not zero or estimated.

### Only the 25 pairs where both conditions passed

This conditional view excludes eleven known-goal pairs with a failed arm and both ambiguous pairs. It complements the all-attempt view; it does not replace it.

| Measure | Primitives | Macro | Macro difference |
|---|---:|---:|---:|
| Model calls | 87 | 52 | 40.2% fewer |
| Input tokens | 194,620 | 107,787 | 44.6% fewer |
| Output tokens | 17,800 | 12,327 | 30.7% fewer |
| Native operations | 87 | 86 | 1.1% fewer |
| Summed measured task time | 221.63 s | 159.90 s | 27.9% less |
| Mean task time | 8.87 s | 6.40 s | |

Fewer LLM interactions do not imply less robot work. The macro performed more native operations over all attempts. Conditional successful-pair native costs were almost equal.

Campaign time includes persisted-trace auditing, bookkeeping and gaps outside the measured task interval. Summed task time was 562.07 s; the remaining 648.18 s is not a measured breakdown of those activities and must not all be attributed to Phoenix or inference. The separate earlier model-load check took about 6.59 s.

## Failure and verification findings

The 17 failed trials comprise:

- **Seven length-stop trials:** four primitives, three macro. The common completion gate withheld tool dispatch from the truncated response and stopped without automatic replay. Earlier activity in the same trial is retained; this is not evidence that the whole trial had no actions.
- **Five other failures with incorrect selection** under the frozen component scorer.
- **Five other failures with correct selection but failed execution/reporting or goal completion.**

These are descriptive post-run buckets, not a causal diagnosis or new frozen hypotheses. They show why the failures should not all be described as wrong initial skill choices or false-success reports.

There were **zero recorded dispatch violations and zero unsupported accepted SUCCESS flags**, but **one accepted SUCCESS for the wrong requested goal in each condition**, both on case G1r1-heldout-036. Evidence can support the selected skill's report while that skill fails the user's goal. The independent goal score correctly retains these failures.

The frozen fault-exercise flag was True on 19 attempts, False on three and not applicable on sixteen **in each condition**. The flag has condition-specific definitions: some concern unavailable/false evidence and others require an actual partial-write dispatch. It is not a count of 19 robot commands or proof that every injected fault was exercised. Raw observer/activity records and per-case scores remain available.

## Hardware and observability

- RTX 4080 SUPER, 16 GB; original model digest, Q4_K_M quantization, Ollama 0.40.6, 8K context, temperature 0, seed 42, reasoning off.
- The earlier load check recorded 33/33 GPU layers, Flash Attention enabled and f16 KV. Driver 570.195.03; nvidia-smi CUDA compatibility 12.8. Installed toolkit version is not established by that display.
- Container image digest, restart policy, dependencies and source identities are retained in the launch records. No automatic container restart was configured.
- Fresh idle GPU gate passed. Detached execution and a scoped sleep/idle inhibitor were used. The inhibitor ended after the run; no permanent power policy changed.
- Telemetry captured 122 samples: GPU utilization 0–100%, SM clocks 210–1,500 MHz and temperature 32–71 C. The sampled compute list contained Ollama and the existing GNOME remote-desktop process. No fixed CUDA/OOM/reset/runner-termination signatures were counted.
- One model-inventory sample preceded loading; the following 121 samples showed the model present. Sampling does not prove absence of a reload between samples or of brief competing work.
- All six fields were recorded on all 198 inference calls: total_duration, load_duration, prompt_eval_count, prompt_eval_duration, eval_count and eval_duration. Aggregate decode rates were **89.96 tokens/s primitives and 89.55 tokens/s macro**.
- No prompt_eval_cached_count was returned. Prompt-count/duration ratios are cache-influenced effective rates, not a cold-prefill benchmark. Client cache=False does not disable server prompt caching. Actual API streaming remains True despite the LangChain streaming=False setting, as documented before launch.

These measurements do not isolate a laptop-versus-lab hardware effect. Sol remains hosted and has different orchestration provenance. No general speed parity claim follows from comparing backend task averages.

## Checks, repairs and evidence integrity

Before launch, eight scripted controls passed local and persisted audits with zero inference. A supplementary check matched 48 serialized request bodies against the unchanged configured adapter and verified timing-field preservation with a fake response. Its first import failure was retained and corrected in the helper only.

The completion report initially referenced an operator packet helper absent from the isolated snapshot. Before report generation, the unchanged helper was copied into this batch's operator folder and the report path corrected. Its earlier reporting source and repair receipt are retained. This changed no frozen runtime, prompt, task, scorer, retry rule or model setting.

The completed export contains 663 files, including a manifest for 662 entries. All 662 manifest entries verified locally after transfer; all 81 sealed backend files remained unchanged. The post-run telemetry/descriptive addendum is separate. A manually transcribed addendum hash initially duplicated a digit; verification stopped before extraction, the lab hash was rechecked, and matching bytes were then imported. That check did not alter evidence or launch inference.

The new descriptive report helpers do not replace or modify the frozen formal analysis script. Formal prediction adjudication remains withheld pending human review. **P3 is dropped; the separate P4 catalogue-size probe was not run.** AI authorship, grouped cases, condition wording and limited task coverage remain important limitations.

## Conclusion and next action

The macro remains a useful efficiency candidate within this tested repaired ROSA arrangement. On these known-goal cases it also had four more correct outcomes, but six macro failures remained and the ambiguous-case review is incomplete. A reliability advantage, model parity, broad generalization or superiority to unmodified ROSA has not been established.

The next step is to obtain actual ratings for the four new blinded transcripts, bind them to the preserved evidence, and run the unchanged final analysis. Do not tune the experiment, replace failures, start the optional replay or launch a new study as part of that closeout.

Send the reviewer **only the neutral review ZIP** below, without this report, model names, mappings or prior ratings. Ask them to read READ_FIRST.md and RUBRIC.md, complete ratings-empty.csv with their own ratings/reasons, and complete REVIEWER_DECLARATION.md honestly. Return the completed CSV and declaration. No reviewer input is prefilled.

## Files

- [Detailed raw-metric report and source-linked records](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/QWEN_EXECUTION_REPORT.md).
- [Full per-trial, per-family, timing and outcome JSON](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/operator/completed-report/results.json).
- [Post-run descriptive accounting](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/operator/POSTRUN_DESCRIPTIVE_FINDINGS.json).
- [Post-run telemetry summary](artifacts/macro-generalization-20261113/revision-1/stage-4-qwen-lab-20261119/operator/POSTRUN_TELEMETRY_SUMMARY.json).
- [Verified completed evidence ZIP](artifacts/g1-lab-preparation-20261119/G1_QWEN_LAB_COMPLETED_20261119.zip).
- [Separate post-run addendum ZIP](artifacts/g1-lab-preparation-20261119/QWEN_POSTRUN_ADDENDUM_20261119.zip).
- [Neutral four-transcript reviewer ZIP](artifacts/reviewer-delivery-20261119/G1_HELDOUT_REVIEW_BATCH_B_2026-11-19.zip).
- [Completed adjudicated Sol report](G1_SOL_ADJUDICATED_REPORT_2026-11-19.md).
- [Living project master](PROJECT_MASTER_README.md).

Evidence ZIP SHA256: e61457a77a881d187834404433e6b176ffe31d942b9b65b0b927bf284a441d64.
Review ZIP SHA256: 5e6020394c348f5cf3b90adf76b07745bb68ef3c3f01fb6512ad8e3b7047c1d8.

