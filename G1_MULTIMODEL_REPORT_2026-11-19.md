# G1 exploratory multi-model extension — results and comparison

Date: **2026-11-19**. **Exploratory backends, added after Sol and Qwen results.**

**228/228 scheduled mock attempts completed.** 701 inference +6 preparation +3 cleanup = **710/1,833 total charged requests**, with separate611-request and eight-hour limits per model. No infrastructure retries, failed-trial replacement, hosted requests, new downloads or Git publication occurred. All228 local and228 persisted Phoenix audits pass.

**Execution is complete; human adjudication and formal analysis are not.** Twelve new semantic ratings are required, including structurally failed responses. Seven primary outcomes remain pending. Qwen Batch B has four separate outstanding ratings. No ratings were generated or reused.

## Main comparison

Known-goal rows exclude the two ambiguous cases per condition. Calls and latency use all38 attempts per arm, including failures. Counts are correct/evaluable. Do not pool backend pass rates.

| Backend | Primitives known-goal | Macro known-goal | Calls P → M | Mean task seconds P → M |
|---|---:|---:|---:|---:|
| Retained Sol | 33/33 | 36/36 | 126 → 74 | 13.27 → 8.36 |
| Retained Qwen3.5 9B | 26/36 | 30/36 | 123 → 75 | 8.48 → 6.31 |
| ministral | 28/36 | 33/36 | 154 → 83 | 5.32 → 3.18 |
| granite | 0/36 | 0/36 | 38 → 38 | 3.55 → 3.15 |
| llama | 0/36 | 1/36 | 203 → 185 | 1.96 → 2.11 |

Sol has three censored primitive attempts and retains its original hosted/laptop-WSL provenance. Qwen retains its old lab container; the extension uses another disclosed installed Jazzy image. These times are contextual per-backend measurements, not a controlled model-speed ranking. Ministral33/36 versus Sol36/36 does not establish parity.

## New-model details

P/M means primitives/macro. Native operations count attempted acquisitions/actions, not only accepted calls. Unknown usage is not zero.

### ministral

{'primitives': {'PASS': 28, 'FAIL': 9, 'PENDING_HUMAN_REVIEW': 1}, 'macro': {'PASS': 33, 'FAIL': 3, 'PENDING_HUMAN_REVIEW': 2}}

Requests: **237 inference +2 preparation +1 cleanup = 240/611**. Full backend elapsed: 16.08min, including auditing/bookkeeping outside measured task time. Paired outcomes over38 pairs: {'both_pass': 27, 'neither': 2, 'macro_only': 6, 'pending_human': 2, 'primitive_only': 1}.

| Metric | Primitives | Macro |
|---|---:|---:|
| calls | 154 | 83 |
| input_tokens | 289754 | 149219 |
| output_tokens | 17691 | 9814 |
| native_operations | 102 | 127 |
| task_seconds | 202.130 | 120.756 |
| mean_seconds | 5.319 | 3.178 |
| median_seconds | 5.397 | 3.025 |
| invalid_attempts | 40 | 5 |
| length_stops | 0 | 0 |
| budget_endings | 4 | 1 |
| incomplete_usage | 0 | 0 |

Recognized native calls: 234. Parser-level invalid-tool-call records: 0 (separate from schema/argument validation errors). Native call names: {'select_skill': 77, 'submit_report': 97, 'read_state': 24, 'write_state': 7, 'verify_outcome': 29}.

Aggregate recorded decode rate P/M: 99.78/100.16tokens/s, in each model's tokenizer units. All six timing-field coverage counts and sums are in the corrected JSON. Cached-token counts were not returned; none are estimated.

Goal/report flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}. These are structured accepted-report flags, not a certification of every prose statement or physical safety.

### granite

{'primitives': {'FAIL': 36, 'PENDING_HUMAN_REVIEW': 2}, 'macro': {'FAIL': 36, 'PENDING_HUMAN_REVIEW': 2}}

Requests: **76 inference +2 preparation +1 cleanup = 79/611**. Full backend elapsed: 14.90min, including auditing/bookkeeping outside measured task time. Paired outcomes over38 pairs: {'neither': 36, 'pending_human': 2}.

| Metric | Primitives | Macro |
|---|---:|---:|
| calls | 38 | 38 |
| input_tokens | 60371 | 60333 |
| output_tokens | 12567 | 10856 |
| native_operations | 0 | 0 |
| task_seconds | 134.768 | 119.719 |
| mean_seconds | 3.547 | 3.150 |
| median_seconds | 3.445 | 2.974 |
| invalid_attempts | 0 | 0 |
| length_stops | 1 | 0 |
| budget_endings | 0 | 0 |
| incomplete_usage | 0 | 0 |

Recognized native calls: 0. Parser-level invalid-tool-call records: 0 (separate from schema/argument validation errors). Native call names: {}.

Aggregate recorded decode rate P/M: 99.83/99.93tokens/s, in each model's tokenizer units. All six timing-field coverage counts and sums are in the corrected JSON. Cached-token counts were not returned; none are estimated.

Goal/report flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}. These are structured accepted-report flags, not a certification of every prose statement or physical safety.

### llama

{'primitives': {'FAIL': 38}, 'macro': {'FAIL': 37, 'PASS': 1}}

Requests: **388 inference +2 preparation +1 cleanup = 391/611**. Full backend elapsed: 13.38min, including auditing/bookkeeping outside measured task time. Paired outcomes over38 pairs: {'neither': 37, 'macro_only': 1}.

| Metric | Primitives | Macro |
|---|---:|---:|
| calls | 203 | 185 |
| input_tokens | 287906 | 295800 |
| output_tokens | 5374 | 5419 |
| native_operations | 42 | 122 |
| task_seconds | 74.570 | 80.134 |
| mean_seconds | 1.962 | 2.109 |
| median_seconds | 1.923 | 2.061 |
| invalid_attempts | 150 | 135 |
| length_stops | 0 | 0 |
| budget_endings | 37 | 31 |
| incomplete_usage | 0 | 0 |

Recognized native calls: 383. Parser-level invalid-tool-call records: 0 (separate from schema/argument validation errors). Native call names: {'select_skill': 76, 'submit_report': 149, 'read_state': 132, 'verify_outcome': 21, 'write_state': 5}.

Aggregate recorded decode rate P/M: 115.79/114.50tokens/s, in each model's tokenizer units. All six timing-field coverage counts and sums are in the corrected JSON. Cached-token counts were not returned; none are estimated.

Goal/report flags: {'dispatch_violation': 0, 'unsupported_accepted_success': 0, 'accepted_success_wrong_goal': 0}. These are structured accepted-report flags, not a certification of every prose statement or physical safety.

## Conditional successful-pair efficiency

Ministral has27 pairs where both conditions passed: calls110 →58 (47.3% fewer), input207,603 →103,276, output12,455 →7,310, native85 →87, task time142.54 →90.47s (36.5% less). Those conditional costs exclude failed/pending pairs and do not replace all-attempt accounting. Its all-attempt call saving is46.1%, while native work rises102 →127. The evidence supports lower LLM orchestration overhead here, not universally lower robot work.

Granite and Llama have zero matched successful pairs. A successful-pair efficiency comparison is undefined; shorter failed-task times are not useful task efficiency.

## Predefined write-bearing contrast — counts only

Six healthy writes plus two frozen write_fault cases form the predefined8-case group; the other known-goal group has28. These are not eight healthy writes.

| Backend | Write P /8 | Write M /8 | Other P /28 | Other M /28 |
|---|---:|---:|---:|---:|
| Qwen, retrospective origin | 2 | 6 | 24 | 24 |
| ministral | 4 | 8 | 24 | 25 |
| granite | 0 | 0 | 0 | 0 |
| llama | 0 | 1 | 0 | 0 |

The observed write-arm floors/ceilings are important: Ministral macro8/8, Granite0/8, Llama primitive0/8. The predefined rule gives those boundaries precedence over a favorable difference. Do not label the positive Ministral pattern H-write Support while ignoring that rule. Formal H-write computation remains withheld under T6 until actual review.

## Integration and environment

Granite produced76 text responses and zero recognized native calls; no native
operations executed. An inspected response rendered tool-shaped JSON in a code
fence and prose. One primitive response hit its output limit. Tool-capability
metadata and full GPU loading did not demonstrate functional tool calling. These
results characterize a failed tested integration, not intrinsic task incapacity.

Llama produced383 recognized native calls, but schema/argument adherence and
recovery failed repeatedly:150/135 invalid attempts and37/31 budget endings P/M.
An inspected read call used incompatible node/fields arguments. One macro
known-goal task passed; the remaining known-goal tasks failed. Native-call parsing
and successful end-to-end task execution are different requirements.

Ministral is the strongest of the three new local configurations on these cases:
known-goal correctness28/36 →33/36, with six macro-only and one primitive-only
correct pair. The point difference is exploratory; small, grouped cases do not
establish a general reliability advantage. Its primitive40 versus macro5 invalid
attempts and native102 versus127 operations should accompany the call savings.

Every sampled loaded-model observation was fully GPU-resident at8K context:
Ministral96/96, Granite89/89, Llama80/80. Sampling observed the Ollama runner and
the existing GNOME remote-desktop compute process. Samples do not prove continuous
absence of competing work. Raw utilization, clocks, temperatures and residency are
retained; no causal thermal or hardware comparison is inferred.

Common serving: context8192, maximum1024 output/call, observed task-output gate2048,
temperature0, seed42, use_mmap true, client cache false, think=false and actual API
streaming true. The server cache stayed as-is. None of these three advertised
thinking capability. Per task:8 decisions,360s,10 native operations,16 tool attempts,
3 corrections and at most1 dispatch. Each backend kept its own611-request cap and
eight-hour clock. Models ran sequentially on the lab via SSH.

The extension image is
`sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2`,
different from Qwen's earlier image. Pinned dependencies matched and all24 scripted
preparation controls passed. Driver570.195.03 and reported CUDA compatibility12.8
are recorded; compatibility is not an installed-toolkit assertion. These are mock
arm/base operations inside a ROS2 Jazzy/ROSA environment, not new Gazebo,
controller or physical-robot tests.

## Preserved errors and corrections

1. Three metadata values were transcribed incorrectly into the acknowledged
   preflight prose: Ministral disk bytes and digest, and Llama loaded size. Actual
   sealed configurations and live digest checks were correct and unchanged. The
   original acknowledged record remains intact. The dated preflight correction
   supplies exact authoritative values.
2. The automatic report worker initially invoked a host Docker verifier inside
   the container, where the Docker CLI was absent. It stopped after all trials
   completed. A reporting-only continuation ran the stdlib consolidator on the
   host. No trials or inference were repeated. Failed source, status and logs are
   retained.
3. The first descriptive helper used nonexistent kind `partial_write`, omitting
   the two actual `write_fault` cases and displaying6/30. The corrected helper uses
   frozen kinds `write` and `write_fault`, asserting8/28 per arm. Original source,
   derived outputs and the completed raw archive remain unchanged. **Use
   DESCRIPTIVE_EXTENSION_RESULTS_CORRECTED01.json and this report for subgroup
   counts.** Scorer, frozen analyzer, hypotheses, thresholds and raw results did
   not change.

The original3,796 frozen inputs,1,159 retained Sol/Qwen hashes and three backend
seals reverified. All228 raw trial hashes and2,019 entries of the initial completed
archive verified locally. Its derived subgroup table is superseded, so the share
package supplies the corrected report/JSON separately and marks them authoritative.
This package is not a live Phoenix database backup. Original runtime prerequisites
and model weights retain their separately recorded hashes/provenance; no model
weights are uploaded or newly downloaded.

## Claims, limitations and next action

These results support reduced LLM orchestration overhead for Ministral in this
environment, with a favorable known-goal point difference. They do not establish
a new selection algorithm, broad reliability improvement, superiority to stock
ROSA, parity with Sol, or a replacement for original Qwen/M4 results. Equal token
limits do not mean equal semantic output across tokenizers. Granite/Llama failure
times cannot support useful-task efficiency claims.

All cases are AI-authored and reused across models; backends were added after
Sol/Qwen results were seen. Condition wording remains confounded with execution
mode, the catalogue is bounded, and samples are small and grouped. Interpretation
must preserve model/integration/environment differences and all failures. There
was no per-model prompt, schema, parser or template repair.

Send only the neutral12-transcript extension review ZIP to Levinson. Obtain his
actual CSV and honest eligibility declaration. Keep Qwen's four-transcript Batch B
separate. Then bind ratings and run the unchanged frozen analyzer separately for
each backend with its original endpoint scopes. T6 remains BLOCKED until then;
no final human-adjudicated campaign verdict or H-write closeout is claimed. P3 is
dropped horizon reliability; P4's catalogue probe was not run; P1′ remains formally
Sol-specific. No further model run, architecture change or Git publication starts
from this report.

