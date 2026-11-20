# Llama and Granite: integration repair and 80-trial reruns

Date: **2026-11-17** (project/operator timezone). Status: execution and independent archive verification complete.

## Result at a glance

- **Llama 3.1 8B:** known-goal correctness **21/36 primitives, 28/36 macro**, versus 0/36 in each older condition. Macro used 190 → 113 calls (40.5% fewer); mean task time 2.37 → 2.16 s (8.6% less measured task time). Correctness difference: +7/36.
- **Granite 3.3 8B:** known-goal correctness **5/36 primitives, 9/36 macro**, versus 0/36 in each older condition. Macro used 210 → 193 calls (8.1% fewer); mean task time 6.81 → 5.18 s (24.0% less measured task time). Correctness difference: +4/36.

All **160/160 robot attempts** completed, plus 24/24 live validation attempts; tracing, preserved-source checks and resource-bound checks passed. Completion of the schedule is separate from task success. Eight ambiguous attempts per model remain pending human review.


## Scope and interpretation

The owner authorized the opt-in integration profile, fresh complete-loop validation, and immediate **80 Llama + 80 Granite Gazebo trials** after the functional gate. This is a new engineering replication of known M4 cases, not new G1 held-out evidence. The original zero-scoring configurations, diagnostic failures, source freezes and all previous studies remain preserved.

Each model ran ten existing families, four repetitions, and two execution conditions: **40 primitives and 40 macro attempts**. Each condition includes **36 known-goal tasks and four ambiguous requests**. The eight ambiguous attempts per model still require actual human semantic review; their old regex results are diagnostics, never a final task-correctness score.

The proper comparison is a combined system/configuration comparison. Native formatting guidance, persistent schemas and explicitly nonstreaming HTTP were introduced together. This run cannot identify their individual causal effects or establish inherent model superiority. Models still chose their skills and arguments; Python performed bounded execution and evidence validation. No training, task-specific answer routing or stock-ROSA comparison was added.

Within the primitive/macro comparison, the original M4 execution mode and condition instruction sentence remain a package. The condition effect on skill selection cannot be separated from condition wording. Both conditions use the repaired ROSA framework; this is not evidence of superiority to unmodified ROSA or a new selection algorithm.

## Main outcomes and costs

Costs below include **all 40 attempts per condition**, including failures and ambiguity. Fast failure is not successful task efficiency. Known-goal success uses the original goal, independently observed robot outcome, accepted reporting contract, permitted dispatch count and actual fault-exercise checks.

| Backend | Condition | Known-goal correct | Calls | Input tokens | Output tokens | Mean task s | Median task s | Native ops | Invalid attempts |
|---|---|---|---|---|---|---|---|---|---|
| Llama 3.1 8B | primitives | 21/36 | 190 | 363734 | 6588 | 2.37 | 1.57 | 99 | 31 |
| Llama 3.1 8B | macro | 28/36 | 113 | 207667 | 2982 | 2.16 | 1.44 | 112 | 9 |
| Granite 3.3 8B | primitives | 5/36 | 210 | 463188 | 23139 | 6.81 | 5.66 | 63 | 112 |
| Granite 3.3 8B | macro | 9/36 | 193 | 439916 | 16028 | 5.18 | 3.23 | 119 | 87 |

Task time is measured inside each task; it excludes simulator startup/reset, separate deterministic controls and post-task persisted trace queries. Campaign elapsed time is reported separately below. Token counts are server/adapter usage totals, not `output limit × maximum calls`.

## Previous integration versus repaired integration

| Backend | Condition | Old correct | New correct | Old calls | New calls | Old mean s | New mean s |
|---|---|---|---|---|---|---|---|
| Llama 3.1 8B | primitives | 0/36 | 21/36 | 211 | 190 | 2.16 | 2.37 |
| Llama 3.1 8B | macro | 0/36 | 28/36 | 193 | 113 | 2.84 | 2.16 |
| Granite 3.3 8B | primitives | 0/36 | 5/36 | 40 | 210 | 3.13 | 6.81 |
| Granite 3.3 8B | macro | 0/36 | 9/36 | 40 | 193 | 2.64 | 5.18 |

Old and new use the same installed weights, hardware, original task catalogue and scoring source. They differ in the declared integration profile and actual HTTP behavior. Earlier constructor `streaming=False` was not proof of nonstreaming HTTP in this pinned adapter; this rerun records and checks the actual request. No retrospective score or source file was changed.

## Per-family outcomes

| Family | Llama P | Llama M | Granite P | Granite M |
|---|---|---|---|---|
| already_satisfied | 4/4 | 4/4 | 2/4 | 4/4 |
| ambiguous_goal | PENDING HUMAN | PENDING HUMAN | PENDING HUMAN | PENDING HUMAN |
| ineffective_command | 0/4 | 1/4 | 0/4 | 0/4 |
| inspect_healthy | 4/4 | 4/4 | 3/4 | 3/4 |
| inspect_inactive | 0/4 | 3/4 | 0/4 | 0/4 |
| inspect_missing_controllers | 4/4 | 4/4 | 0/4 | 0/4 |
| inspect_missing_joint | 4/4 | 4/4 | 0/4 | 2/4 |
| missing_prerequisite | 4/4 | 4/4 | 0/4 | 0/4 |
| move_constrained | 1/4 | 4/4 | 0/4 | 0/4 |
| partial_command | 0/4 | 0/4 | 0/4 | 0/4 |

## Paired correctness and matched-success efficiency

### Llama 3.1 8B

There are 36 known-goal primitive/macro pairs: **21 both correct**, 0 primitive-only correct, 7 macro-only correct, 8 both wrong.

| Condition | Matched successes | Calls | Input | Output | Task s | Native ops |
|---|---|---|---|---|---|---|
| primitives | 21 | 88 | 161648 | 2798 | 45.05 | 50 |
| macro | 21 | 47 | 82961 | 1294 | 28.76 | 44 |

This subset compares the same cells that both conditions completed. It is selected by outcome and does not replace all-attempt costs or estimate unconditional throughput.
### Granite 3.3 8B

There are 36 known-goal primitive/macro pairs: **4 both correct**, 1 primitive-only correct, 5 macro-only correct, 26 both wrong.

| Condition | Matched successes | Calls | Input | Output | Task s | Native ops |
|---|---|---|---|---|---|---|
| primitives | 4 | 26 | 59300 | 3147 | 35.57 | 8 |
| macro | 4 | 16 | 35744 | 469 | 7.10 | 10 |

This subset compares the same cells that both conditions completed. It is selected by outcome and does not replace all-attempt costs or estimate unconditional throughput.

## Selection, reporting, faults and remaining failures

| Backend | Condition | Correct skill /36 | Correct selected outcome /36 | Dispatches | Accepted SUCCESS for wrong goal | Structured unsupported SUCCESS attempts | Returned error strings |
|---|---|---|---|---|---|---|---|
| Llama 3.1 8B | primitives | 29 | 25 | 1 | 7 | 0 | 0 |
| Llama 3.1 8B | macro | 32 | 28 | 8 | 4 | 1 | 0 |
| Granite 3.3 8B | primitives | 15 | 5 | 2 | 9 | 1 | 16 |
| Granite 3.3 8B | macro | 21 | 9 | 3 | 12 | 3 | 4 |

The unsupported-success counter covers structured reporting attempts; it is not an exhaustive semantic audit of free text. A truthful report for an incorrectly selected skill can still fail the user goal. Outer exception fields alone also miss errors returned as ordinary answer strings. The independent JSON retains both and every failed/ambiguous answer.

Recorded validation and terminal-error frequencies (counts can exceed failed tasks because a task may make several invalid attempts):

| Backend | Condition | Validation codes | Returned terminal errors |
|---|---|---|---|
| Llama 3.1 8B | primitives | {"known_prerequisite_required": 3, "outcome_classification_mismatch": 5, "schema_validation": 23} | {} |
| Llama 3.1 8B | macro | {"outcome_classification_mismatch": 8, "unsupported_success": 1} | {} |
| Granite 3.3 8B | primitives | {"invalid_node_scope": 17, "known_prerequisite_required": 2, "multiple_tool_calls_rejected": 32, "schema_validation": 40, "skill_selection_required": 18, "stale_observation_reference": 1, "unsupported_success": 1, "write_prerequisite_rejected": 1} | {"truncated_response_no_tool_dispatch_no_automatic_retry": 1, "validation_retry_budget_exhausted": 15} |
| Granite 3.3 8B | macro | {"multiple_tool_calls_rejected": 19, "outcome_classification_mismatch": 2, "registered_target_required": 1, "schema_validation": 40, "skill_selection_required": 19, "unsupported_success": 3, "write_prerequisite_rejected": 3} | {"validation_retry_budget_exhausted": 4} |

Llama 3.1 8B:

- **primitives:** 16 injected faults exercised; 8 skipped or unexercised fault cells. Model/program native operations: 99/0.
- **macro:** 20 injected faults exercised; 4 skipped or unexercised fault cells. Model/program native operations: 28/84.

| Failed known-goal cell | Selected skill | Accepted report | Fault exercised | Calls | Outer error |
|---|---|---|---|---|---|
| ineffective_command r1 primitives | ur5e.park_right | FAILURE | False | 8 | None |
| ineffective_command r1 macro | ur5e.park_right | None | True | 4 | None |
| partial_command r1 macro | ur5e.home | SUCCESS | False | 4 | None |
| partial_command r1 primitives | ur5e.home | SUCCESS | False | 6 | None |
| inspect_inactive r1 primitives | ur5e.inspect_readiness | None | True | 4 | None |
| inspect_inactive r1 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_inactive r2 primitives | ur5e.inspect_readiness | None | True | 4 | None |
| move_constrained r2 primitives | ur5e.home | SUCCESS | None | 6 | None |
| ineffective_command r2 primitives | ur5e.park_right | FAILURE | False | 8 | None |
| partial_command r2 macro | ur5e.home | SUCCESS | False | 4 | None |
| partial_command r2 primitives | ur5e.home | SUCCESS | False | 6 | None |
| move_constrained r3 primitives | ur5e.home | SUCCESS | None | 6 | None |
| ineffective_command r3 primitives | ur5e.park_right | FAILURE | False | 8 | None |
| ineffective_command r3 macro | ur5e.park_right | None | True | 4 | None |
| partial_command r3 macro | ur5e.home | SUCCESS | False | 4 | None |
| partial_command r3 primitives | ur5e.home | SUCCESS | False | 6 | None |
| inspect_inactive r3 primitives | ur5e.inspect_readiness | None | True | 4 | None |
| inspect_inactive r4 primitives | ur5e.inspect_readiness | None | True | 4 | None |
| move_constrained r4 primitives | ur5e.home | SUCCESS | None | 6 | None |
| ineffective_command r4 primitives | ur5e.park_right | FAILURE | False | 8 | None |
| ineffective_command r4 macro | ur5e.park_right | None | True | 4 | None |
| partial_command r4 macro | ur5e.home | SUCCESS | False | 4 | None |
| partial_command r4 primitives | ur5e.home | SUCCESS | False | 6 | None |

Granite 3.3 8B:

- **primitives:** 3 injected faults exercised; 21 skipped or unexercised fault cells. Model/program native operations: 63/0.
- **macro:** 14 injected faults exercised; 10 skipped or unexercised fault cells. Model/program native operations: 42/77.

| Failed known-goal cell | Selected skill | Accepted report | Fault exercised | Calls | Outer error |
|---|---|---|---|---|---|
| move_constrained r1 primitives | ur5e.home | SUCCESS | None | 6 | None |
| move_constrained r1 macro | ur5e.home | SUCCESS | None | 5 | None |
| already_satisfied r1 primitives | None | None | None | 3 | None |
| ineffective_command r1 primitives | ur5e.park_right | None | True | 8 | None |
| ineffective_command r1 macro | ur5e.park_right | None | True | 7 | None |
| partial_command r1 macro | ur5e.home | SUCCESS | False | 5 | None |
| partial_command r1 primitives | ur5e.home | SUCCESS | False | 6 | None |
| missing_prerequisite r1 primitives | ur5e.inspect_readiness | SUCCESS | False | 5 | None |
| missing_prerequisite r1 macro | ur5e.inspect_readiness | SUCCESS | False | 4 | None |
| inspect_healthy r1 macro | None | None | None | 4 | None |
| inspect_inactive r1 primitives | None | None | False | 4 | None |
| inspect_inactive r1 macro | None | None | False | 4 | None |
| inspect_missing_controllers r1 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_missing_controllers r1 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| inspect_missing_joint r1 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| inspect_missing_joint r1 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_inactive r2 primitives | None | None | False | 4 | None |
| inspect_inactive r2 macro | ur5e.inspect_readiness | None | True | 6 | None |
| inspect_missing_controllers r2 macro | ur5e.inspect_readiness | None | True | 6 | None |
| inspect_missing_controllers r2 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| inspect_missing_joint r2 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| move_constrained r2 primitives | ur5e.home | SUCCESS | None | 6 | None |
| move_constrained r2 macro | ur5e.home | SUCCESS | None | 5 | None |
| ineffective_command r2 primitives | None | None | False | 4 | None |
| ineffective_command r2 macro | ur5e.park_right | None | True | 7 | None |
| partial_command r2 macro | ur5e.home | SUCCESS | False | 6 | None |
| partial_command r2 primitives | ur5e.home | None | True | 7 | None |
| missing_prerequisite r2 primitives | ur5e.inspect_readiness | SUCCESS | False | 5 | None |
| missing_prerequisite r2 macro | ur5e.inspect_readiness | SUCCESS | False | 4 | None |
| move_constrained r3 primitives | ur5e.home | SUCCESS | None | 6 | None |
| move_constrained r3 macro | ur5e.home | SUCCESS | None | 5 | None |
| ineffective_command r3 primitives | None | None | False | 4 | None |
| ineffective_command r3 macro | ur5e.park_right | None | True | 7 | None |
| partial_command r3 macro | ur5e.home | SUCCESS | False | 5 | None |
| partial_command r3 primitives | ur5e.home | None | False | 6 | None |
| missing_prerequisite r3 primitives | ur5e.inspect_readiness | SUCCESS | False | 5 | None |
| missing_prerequisite r3 macro | ur5e.inspect_readiness | SUCCESS | False | 3 | None |
| inspect_healthy r3 primitives | ur5e.inspect_readiness | None | None | 5 | None |
| inspect_inactive r3 primitives | None | None | False | 4 | None |
| inspect_inactive r3 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_missing_controllers r3 macro | ur5e.inspect_readiness | None | True | 6 | None |
| inspect_missing_controllers r3 primitives | ur5e.inspect_readiness | None | True | 7 | None |
| inspect_missing_joint r3 primitives | None | None | False | 4 | None |
| inspect_missing_joint r3 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_inactive r4 primitives | None | None | False | 4 | None |
| inspect_inactive r4 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_missing_controllers r4 macro | ur5e.inspect_readiness | None | True | 5 | None |
| inspect_missing_controllers r4 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| inspect_missing_joint r4 primitives | ur5e.inspect_readiness | None | False | 5 | None |
| move_constrained r4 primitives | ur5e.home | SUCCESS | None | 6 | None |
| move_constrained r4 macro | ur5e.home | SUCCESS | None | 5 | None |
| already_satisfied r4 primitives | None | None | None | 3 | None |
| ineffective_command r4 primitives | ur5e.park_right | None | False | 5 | None |
| ineffective_command r4 macro | None | None | False | 4 | None |
| partial_command r4 macro | ur5e.home | SUCCESS | False | 5 | None |
| partial_command r4 primitives | ur5e.home | None | False | 6 | None |
| missing_prerequisite r4 primitives | ur5e.inspect_readiness | SUCCESS | False | 5 | None |
| missing_prerequisite r4 macro | ur5e.inspect_readiness | SUCCESS | False | 3 | None |

## Fresh full-loop validation before Gazebo

Seven zero-network tests and twelve deterministic validation controls passed before the live profile tests. Both backends received six fresh scenarios in both execution modes, with two skills offered.

| Backend | Correct /12 | Functional gate | Requests /96 | Input tokens | Output tokens |
|---|---|---|---|---|---|
| Llama 3.1 8B | 9 | PASS | 51 | 68775 | 1159 |
| Granite 3.3 8B | 6 | PASS | 56 | 98032 | 3663 |

New campaign total: **706 robot inference requests + 107 validation requests = 813 requests**, **1,641,312 input tokens** and **53,559 output tokens**. Validation and robot limits remain separate; the combined ceiling was1,478. Unit tests, deterministic controls, metadata queries and explicit unload requests generated no model completions. The earlier48-request diagnostic is a separate completed study, not an uncounted part of this rerun.

The frozen **functional** gate required at least one healthy complete SUCCESS loop in each execution mode plus all safety, budget and trace checks. It did not require all movement, fault or recovery decisions to succeed. Both passed via healthy inspection; Granite failed both healthy movement validation cells. This gate demonstrated usable integration, not high task reliability. The following table preserves every outcome.

| Backend | Fresh case | Mode | Correct | Writes | Expiry exercised | Calls |
|---|---|---|---|---|---|---|
| Llama 3.1 8B | inspect_ready | primitives | True | 0 | False | 4 |
| Llama 3.1 8B | inspect_ready | macro | True | 0 | False | 3 |
| Llama 3.1 8B | inspect_unready | primitives | False | 0 | False | 4 |
| Llama 3.1 8B | inspect_unready | macro | False | 0 | False | 4 |
| Llama 3.1 8B | set_level | primitives | False | 0 | False | 5 |
| Llama 3.1 8B | set_level | macro | True | 1 | False | 4 |
| Llama 3.1 8B | write_no_effect | primitives | True | 0 | False | 5 |
| Llama 3.1 8B | write_no_effect | macro | True | 1 | False | 4 |
| Llama 3.1 8B | source_unavailable | primitives | True | 0 | False | 3 |
| Llama 3.1 8B | source_unavailable | macro | True | 0 | False | 3 |
| Llama 3.1 8B | expired_observation | primitives | True | 0 | True | 6 |
| Llama 3.1 8B | expired_observation | macro | True | 0 | True | 6 |
| Granite 3.3 8B | inspect_ready | primitives | True | 0 | False | 4 |
| Granite 3.3 8B | inspect_ready | macro | True | 0 | False | 5 |
| Granite 3.3 8B | inspect_unready | primitives | True | 0 | False | 4 |
| Granite 3.3 8B | inspect_unready | macro | False | 0 | False | 4 |
| Granite 3.3 8B | set_level | primitives | False | 0 | False | 2 |
| Granite 3.3 8B | set_level | macro | False | 0 | False | 2 |
| Granite 3.3 8B | write_no_effect | primitives | False | 0 | False | 6 |
| Granite 3.3 8B | write_no_effect | macro | True | 1 | False | 7 |
| Granite 3.3 8B | source_unavailable | primitives | False | 0 | False | 5 |
| Granite 3.3 8B | source_unavailable | macro | False | 0 | False | 5 |
| Granite 3.3 8B | expired_observation | primitives | True | 0 | True | 6 |
| Granite 3.3 8B | expired_observation | macro | True | 0 | True | 6 |

Validation limitation: the fresh mock checker tests skill, accepted status, world state and safe writes; it does not require an ineffective-write command actually to be attempted. Llama primitive `write_no_effect` was counted correct with no write, so that cell is **not evidence of detecting a dispatched command failure**. The main Gazebo scorer retains its stronger fault-exercise and expected-dispatch requirements. Stale-evidence cases record whether expiry was actually injected; accepted fresh-evidence reporting remains enforced by the unchanged validator.

## Implementation and configuration

The new reusable opt-in module is `rosa-research/src/rosa_backends/tool_contract_ollama.py`. It appends model-native calling instructions and the **current bound schemas** as a system message on every request. It does not mutate conversation history, retain obsolete bound schemas, select skills, invent expected outcomes, alias malformed arguments, retry robot writes or weaken reporting. The original backend remains available unchanged. The profile supports the two tested model families and rejects conflicting streaming requests.

`native-schema-v1` explicitly enforces HTTP `stream=false`. Llama receives its documented `name`/`parameters` format; Granite receives its native `<|tool_call|>` list guidance. These are family-specific serialization instructions around a common semantic tool contract. Global Ollama templates were not edited. Existing SDK argument normalization remains assistance from the combined software stack, not raw-model schema competence.

Hardware: lab RTX 4080 SUPER (16,376 MiB VRAM), Ubuntu host, isolated Ubuntu 24.04 container with ROS 2 Jazzy, CPU-rendered Gazebo UR5e, project-local Ollama 0.40.6. Both installed models are 8B Q4_K_M; exact digests, locked dependencies, model templates and original source are in the referenced evidence. Full hardware provenance is retained; these are not the historical laptop trials or a fresh hosted Sol run.

Serving: 8,192-token context, maximum 1,024 output tokens/call, temperature 0, seed 42, one loaded model and serialized simulator access. No additional reasoning mode was enabled. Task bounds: eight model calls, 2,048 observed output tokens, 360 seconds, ten native operations, sixteen tool attempts, three corrections, one movement maximum. Robot batches: 640 ordinary requests plus three narrow HTTP retry-reserve requests/model, eight-hour backend window. Fresh validation: separate 96-request ceiling/model. All extra calls, corrections and returned tokens count. No provider consent or hosted inference was involved.

LangChain response caching was disabled. That does not establish that Ollama prompt-prefix/KV reuse was disabled; a per-request cached-token count was not recorded.

| Model tag | Frozen installed digest |
|---|---|
| llama3.1:8b-instruct-q4_K_M | 46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e |
| granite3.3:8b | fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7 |

Frozen baseline provenance (runtime imports the archived source, not mutable repository working trees):

| Repository | Recorded baseline revision |
|---|---|
| rosa-research | c0c61a05c481669f201cbbb892b0bc9a3a642000 |
| rosa-evaluation | 4412f05210d98d03041b25cf54e41b0ec139580d |

## Actual transport, parser assistance and timing

| Backend | Robot requests /643 | Aggregate generated tok/s | Max prompt tokens | Schema-bearing calls after tools | Argument normalizations | Raw/parsed name-count differences | Campaign s | Done reasons |
|---|---|---|---|---|---|---|---|---|
| Llama 3.1 8B | 303 | 112.63 | 2872 | 223 | 46 | 0 | 1214.32 | {"stop": 303} |
| Granite 3.3 8B | 403 | 98.51 | 3457 | 323 | 0 | 0 | 1510.65 | {"stop": 402, "length": 1} |

The full detached pipeline took **56.70 minutes** through validation, controls, both robot batches and their reports (excluding the initial failed preparation and later offline report/download work).

| Backend | 80-trial campaign min | Sum of timed tasks s | Infrastructure retries /3 |
|---|---|---|---|
| Llama 3.1 8B | 20.24 | 181.17 | 0 |
| Granite 3.3 8B | 25.18 | 479.69 | 0 |

Throughput is total generated tokens divided by total recorded Ollama eval duration; it is not complete-task throughput. Every actual HTTP request/response is retained and checked against its trace metadata. The raw API tool calls are already Ollama-parsed native calls, not unparsed model token text. The complete rendered/tokenized prompt after Ollama templating was not captured: schema checks prove actual HTTP system-message presence, not a token-level rendering audit. Argument differences and invalid parsed calls are listed in the independent JSON; do not credit SDK coercion to the LLM. `prompt_eval_cached_count` was not recorded.

## Preservation, amendments and verification

The initial deterministic inspection control failed **before any model request** because the new mock returned a float while the existing interface requires a Boolean. Its stopped source, freeze and failed control are preserved in `INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip`. Revision 1 changes only that mock return type, adds its regression check and uses a new output root. No live validation or rerun model result existed when this amendment was made; the profile, task wording, scorer and limits were unchanged. A separate launcher attempt before successful source transfer made no model calls and its log is retained. These were preparation errors, not model failures.

The completed campaign has **160 live robot attempts + 24 live validation attempts**, separate from **20 Gazebo controls + 12 deterministic validation controls**. Every completed attempt retained its local and persisted Phoenix audit. Independent verification matched **2,643 new archive content hashes**, all **75 frozen source/configuration hashes**, model digests, ordered schedules, checkpoint/raw trial fields, physical request journals, actual wire records, token bounds, per-task dispatch limits and cleanup records. The original 69 source files were unchanged. Every pipeline step completed normally. No failed/completed trial was silently repeated.

Raw rerun archive SHA-256: `5b98ca99fadab0d2bd6c6a3abb0f9b7baab38bab7e9ce1bdd2e79da97dbdf685`.

Here, independent verification means a separate read-only reconciliation script checking raw archives rather than trusting the progress summary. It is not an external research replication or a substitute for human semantic review.

The raw archive includes frozen new source, unit/protocol logs, validation, model requests/responses, full traces, persisted audit records, controls, checkpoints and intermediate reports. The original lab archive supplies the unchanged baseline source and old results; both are included in the share package for reproduction. No weights, credentials or full runtime environments are bundled. Historical archives are immutable.


## Contextual model comparison

| Backend | Profile | Mode | Known-goal correct | Calls | Mean task s |
|---|---|---|---|---|---|
| qwen3.5:9b | original lab profile | primitives | 27/36 | 188 | 12.39 |
| qwen3.5:9b | original lab profile | macro | 28/36 | 98 | 8.56 |
| ministral-3:8b-instruct-2512-q4_K_M | original lab profile | primitives | 28/36 | 156 | 4.83 |
| ministral-3:8b-instruct-2512-q4_K_M | original lab profile | macro | 28/36 | 82 | 2.31 |
| llama3.1:8b-instruct-q4_K_M | native-schema-v1 | primitives | 21/36 | 190 | 2.37 |
| llama3.1:8b-instruct-q4_K_M | native-schema-v1 | macro | 28/36 | 113 | 2.16 |
| granite3.3:8b | native-schema-v1 | primitives | 5/36 | 210 | 6.81 |
| granite3.3:8b | native-schema-v1 | macro | 9/36 | 193 | 5.18 |

These profiles are not uniformly matched. The table is an engineering reference, not an intrinsic model leaderboard. The separately retained Qwen repeat scored 26/36 primitives and 28/36 macro, versus 27/36 and 28/36 in its first lab run. Historical Sol has fewer repetitions and a hosted execution environment; no new Sol trial was run or inferred here.

For the same known cells that both a rerun backend and the first lab Qwen configuration completed correctly:

| Rerun comparison | Condition | Both correct /36 | Configuration | Calls | Task s | Output | Native |
|---|---|---|---|---|---|---|---|
| Llama 3.1 8B | primitives | 16 | qwen_original_lab_profile | 62 | 118.38 | 9492 | 33 |
| Llama 3.1 8B | primitives | 16 | rerun_native_schema_v1 | 61 | 26.25 | 1920 | 36 |
| Llama 3.1 8B | macro | 20 | qwen_original_lab_profile | 40 | 75.86 | 5377 | 41 |
| Llama 3.1 8B | macro | 20 | rerun_native_schema_v1 | 48 | 28.70 | 1349 | 48 |
| Granite 3.3 8B | primitives | 5 | qwen_original_lab_profile | 24 | 43.15 | 3443 | 11 |
| Granite 3.3 8B | primitives | 5 | rerun_native_schema_v1 | 32 | 47.61 | 4281 | 10 |
| Granite 3.3 8B | macro | 9 | qwen_original_lab_profile | 18 | 26.55 | 1850 | 18 |
| Granite 3.3 8B | macro | 9 | rerun_native_schema_v1 | 41 | 31.67 | 2502 | 22 |

These are outcome-selected descriptive subsets with different integration profiles. They remove failed-task termination from that timing subset, but do not establish a fair isolated model effect or correctness equivalence. Full discordant counts are retained in JSON.

## Conclusions and next decision

**Llama is now a viable additional experimental backend, with material remaining limitations.** Its macro score improved to28/36 and matched the first lab Qwen macro aggregate, but the two configurations succeeded on only20 shared known-goal cells: each succeeded on8 that the other failed. On those20 shared successes, Llama took28.70 s versus Qwen75.86 s, while using48 versus40 calls and48 versus41 native operations. Those are descriptive, outcome-selected comparisons under different profiles, not model equivalence or universal efficiency superiority.

**For Llama, the macro package has a useful observed trade-off:** seven additional known-goal passes,40.5% fewer calls and54.7% fewer output tokens, but only8.6% less all-attempt task time and more native work (99→112). On its21 matched successes, calls fell88→47 and native work50→44. Four macro SUCCESS reports still served the wrong user goal, and all four partial-command tasks failed. Keep these limitations visible rather than calling the backend reliable in general.

**Granite should not replace the current reference backend on this evidence.** Its macro score is9/36, and primitives5/36. Native tool calling is functional, but repeated schema errors, prohibited multiple-call batches, premature prose and wrong skill/goal selection remain. Native call names/counts survived parsing in the captured requests; no downstream parser loss explains these failures. The macro's lower call count (210→193) comes with more native work (63→119) and12 accepted wrong-goal SUCCESS reports versus9 with primitives. This is poor performance under the tested contract, not proof that Granite is inherently incapable of ROSA tasks.

Do not weaken the one-tool-per-turn rule, automatically substitute skills, or change frozen scoring to make these results look better. Any future contract/selection intervention needs a new prospective evaluation. Keep Qwen as the retained reference, Llama as an opt-in candidate, and Granite as a documented unsuccessful configuration for this workload; no default backend was switched by this study.

The previous zeros must remain described as failures of the tested model-plus-adapter configurations, not proof that these model families cannot operate ROSA. The present results quantify what the declared combined integration repair actually achieved, including any remaining decision, execution, feedback or reporting failures.

Choose a backend by verified known-goal completion **and** end-to-end task costs, not call count or rapid termination alone. Macros need an explicit correctness trade-off check; fewer calls do not compensate automatically for missed goals. Any stronger comparison requires fresh cases, matched serving profiles and predeclared decision criteria. Four repetitions of ten familiar families do not establish broad generalization, statistical independence, equivalence or physical-robot safety.

Keep the opt-in profile and frozen evidence available. Do not tune it repeatedly on these failures or overwrite the old study. G1's existing human-review and scorer/instrumentation gates remain unchanged; this authorized replication does not clear them. No new architecture, memory system, full JTVR, physical deployment or additional model study was launched.

Machine-readable details: [independent analysis](INDEPENDENT_RERUN_ANALYSIS.json). Raw data: [rerun archive](NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip). Retained preparation failure: [initial stopped attempt](INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip).

## Complete robot-attempt ledger

Ambiguous rows are marked PENDING even where the legacy regex returned pass or fail.

### Llama 3.1 8B

| Cell | Outcome | Selected skill | Accepted status | Fault exercised | Calls | Input | Output | Task s | Native |
|---|---|---|---|---|---|---|---|---|---|
| 01-move_constrained-r1-primitives | PASS | ur5e.stage_left | SUCCESS | None | 6 | 12328 | 204 | 9.29 | 4 |
| 02-move_constrained-r1-macro | PASS | ur5e.stage_left | SUCCESS | None | 3 | 5831 | 77 | 5.51 | 4 |
| 03-already_satisfied-r1-macro | PASS | ur5e.stage_left | SUCCESS | None | 2 | 3775 | 56 | 1.13 | 2 |
| 04-already_satisfied-r1-primitives | PASS | ur5e.stage_left | SUCCESS | None | 6 | 12353 | 209 | 2.74 | 3 |
| 05-ineffective_command-r1-primitives | FAIL | ur5e.park_right | FAILURE | False | 8 | 17788 | 435 | 5.30 | 3 |
| 06-ineffective_command-r1-macro | FAIL | ur5e.park_right | None | True | 4 | 8059 | 106 | 5.77 | 4 |
| 07-partial_command-r1-macro | FAIL | ur5e.home | SUCCESS | False | 4 | 8103 | 89 | 1.62 | 4 |
| 08-partial_command-r1-primitives | FAIL | ur5e.home | SUCCESS | False | 6 | 12404 | 207 | 2.97 | 3 |
| 09-missing_prerequisite-r1-primitives | PASS | ur5e.stage_left | UNKNOWN | True | 6 | 11951 | 198 | 2.65 | 3 |
| 10-missing_prerequisite-r1-macro | PASS | ur5e.stage_left | UNKNOWN | True | 3 | 5713 | 82 | 1.42 | 2 |
| 11-inspect_healthy-r1-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 2 | 3253 | 54 | 0.87 | 2 |
| 12-inspect_healthy-r1-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 4660 | 79 | 1.08 | 2 |
| 13-inspect_inactive-r1-primitives | FAIL | ur5e.inspect_readiness | None | True | 4 | 6376 | 86 | 1.33 | 2 |
| 14-inspect_inactive-r1-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 8989 | 121 | 1.68 | 4 |
| 15-inspect_missing_controllers-r1-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3271 | 57 | 0.93 | 2 |
| 16-inspect_missing_controllers-r1-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4651 | 80 | 1.09 | 2 |
| 17-inspect_missing_joint-r1-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4661 | 80 | 1.11 | 2 |
| 18-inspect_missing_joint-r1-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3280 | 58 | 1.98 | 2 |
| 19-ambiguous_goal-r1-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 2 | 3227 | 56 | 0.85 | 2 |
| 20-ambiguous_goal-r1-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 3 | 4620 | 81 | 1.12 | 2 |
| 21-inspect_healthy-r2-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 2 | 3255 | 56 | 0.87 | 2 |
| 22-inspect_healthy-r2-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 4661 | 80 | 1.14 | 2 |
| 23-inspect_inactive-r2-primitives | FAIL | ur5e.inspect_readiness | None | True | 4 | 6379 | 87 | 1.22 | 2 |
| 24-inspect_inactive-r2-macro | PASS | ur5e.inspect_readiness | FAILURE | True | 4 | 6931 | 108 | 1.53 | 4 |
| 25-inspect_missing_controllers-r2-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3272 | 58 | 1.03 | 2 |
| 26-inspect_missing_controllers-r2-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4653 | 82 | 1.13 | 2 |
| 27-inspect_missing_joint-r2-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4665 | 84 | 1.14 | 2 |
| 28-inspect_missing_joint-r2-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3279 | 57 | 0.92 | 2 |
| 29-ambiguous_goal-r2-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 2 | 3229 | 58 | 0.91 | 2 |
| 30-ambiguous_goal-r2-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 3 | 4621 | 82 | 1.39 | 2 |
| 31-move_constrained-r2-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 12433 | 210 | 2.66 | 3 |
| 32-move_constrained-r2-macro | PASS | ur5e.stage_left | SUCCESS | None | 3 | 5831 | 77 | 5.48 | 4 |
| 33-already_satisfied-r2-macro | PASS | ur5e.stage_left | SUCCESS | None | 2 | 3778 | 59 | 1.17 | 2 |
| 34-already_satisfied-r2-primitives | PASS | ur5e.stage_left | SUCCESS | None | 6 | 12346 | 208 | 2.70 | 3 |
| 35-ineffective_command-r2-primitives | FAIL | ur5e.park_right | FAILURE | False | 8 | 17801 | 435 | 4.95 | 3 |
| 36-ineffective_command-r2-macro | PASS | ur5e.park_right | FAILURE | True | 4 | 7913 | 112 | 5.84 | 4 |
| 37-partial_command-r2-macro | FAIL | ur5e.home | SUCCESS | False | 4 | 8115 | 90 | 1.75 | 4 |
| 38-partial_command-r2-primitives | FAIL | ur5e.home | SUCCESS | False | 6 | 12404 | 208 | 2.80 | 3 |
| 39-missing_prerequisite-r2-primitives | PASS | ur5e.stage_left | UNKNOWN | True | 6 | 11965 | 200 | 2.58 | 3 |
| 40-missing_prerequisite-r2-macro | PASS | ur5e.stage_left | UNKNOWN | True | 3 | 5695 | 75 | 1.38 | 2 |
| 41-move_constrained-r3-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 12421 | 208 | 2.85 | 3 |
| 42-move_constrained-r3-macro | PASS | ur5e.stage_left | SUCCESS | None | 3 | 5828 | 76 | 5.52 | 4 |
| 43-already_satisfied-r3-macro | PASS | ur5e.stage_left | SUCCESS | None | 2 | 3774 | 56 | 1.14 | 2 |
| 44-already_satisfied-r3-primitives | PASS | ur5e.stage_left | SUCCESS | None | 6 | 12360 | 210 | 3.23 | 3 |
| 45-ineffective_command-r3-primitives | FAIL | ur5e.park_right | FAILURE | False | 8 | 17776 | 356 | 4.27 | 3 |
| 46-ineffective_command-r3-macro | FAIL | ur5e.park_right | None | True | 4 | 8052 | 104 | 5.82 | 4 |
| 47-partial_command-r3-macro | FAIL | ur5e.home | SUCCESS | False | 4 | 8112 | 90 | 1.70 | 4 |
| 48-partial_command-r3-primitives | FAIL | ur5e.home | SUCCESS | False | 6 | 12414 | 208 | 2.76 | 3 |
| 49-missing_prerequisite-r3-primitives | PASS | ur5e.stage_left | UNKNOWN | True | 3 | 5504 | 75 | 1.27 | 1 |
| 50-missing_prerequisite-r3-macro | PASS | ur5e.stage_left | UNKNOWN | True | 3 | 5701 | 78 | 1.40 | 2 |
| 51-inspect_healthy-r3-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 2 | 3256 | 57 | 0.92 | 2 |
| 52-inspect_healthy-r3-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 4661 | 80 | 1.17 | 2 |
| 53-inspect_inactive-r3-primitives | FAIL | ur5e.inspect_readiness | None | True | 4 | 6379 | 87 | 1.30 | 2 |
| 54-inspect_inactive-r3-macro | PASS | ur5e.inspect_readiness | FAILURE | True | 4 | 6943 | 112 | 2.10 | 4 |
| 55-inspect_missing_controllers-r3-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3269 | 55 | 1.47 | 2 |
| 56-inspect_missing_controllers-r3-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4652 | 81 | 1.18 | 2 |
| 57-inspect_missing_joint-r3-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4662 | 81 | 1.21 | 2 |
| 58-inspect_missing_joint-r3-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3279 | 57 | 0.91 | 2 |
| 59-ambiguous_goal-r3-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 2 | 3228 | 57 | 0.90 | 2 |
| 60-ambiguous_goal-r3-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 3 | 4619 | 80 | 1.13 | 2 |
| 61-inspect_healthy-r4-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 2 | 3255 | 56 | 0.91 | 2 |
| 62-inspect_healthy-r4-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 4663 | 82 | 1.16 | 2 |
| 63-inspect_inactive-r4-primitives | FAIL | ur5e.inspect_readiness | None | True | 4 | 6379 | 87 | 1.76 | 2 |
| 64-inspect_inactive-r4-macro | PASS | ur5e.inspect_readiness | FAILURE | True | 4 | 6943 | 112 | 1.65 | 4 |
| 65-inspect_missing_controllers-r4-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3270 | 56 | 0.95 | 2 |
| 66-inspect_missing_controllers-r4-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4651 | 80 | 1.14 | 2 |
| 67-inspect_missing_joint-r4-primitives | PASS | ur5e.inspect_readiness | UNKNOWN | True | 3 | 4663 | 82 | 1.15 | 2 |
| 68-inspect_missing_joint-r4-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 2 | 3280 | 58 | 0.93 | 2 |
| 69-ambiguous_goal-r4-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 2 | 3228 | 57 | 0.93 | 2 |
| 70-ambiguous_goal-r4-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 3 | 4619 | 80 | 1.21 | 2 |
| 71-move_constrained-r4-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 12432 | 208 | 2.72 | 3 |
| 72-move_constrained-r4-macro | PASS | ur5e.stage_left | SUCCESS | None | 3 | 5834 | 78 | 5.52 | 4 |
| 73-already_satisfied-r4-macro | PASS | ur5e.stage_left | SUCCESS | None | 2 | 3774 | 55 | 1.47 | 2 |
| 74-already_satisfied-r4-primitives | PASS | ur5e.stage_left | SUCCESS | None | 7 | 14966 | 322 | 3.90 | 3 |
| 75-ineffective_command-r4-primitives | FAIL | ur5e.park_right | FAILURE | False | 8 | 17807 | 435 | 5.02 | 3 |
| 76-ineffective_command-r4-macro | FAIL | ur5e.park_right | None | True | 4 | 8045 | 98 | 5.80 | 4 |
| 77-partial_command-r4-macro | FAIL | ur5e.home | SUCCESS | False | 4 | 8096 | 87 | 2.37 | 4 |
| 78-partial_command-r4-primitives | FAIL | ur5e.home | SUCCESS | False | 6 | 12414 | 210 | 2.86 | 3 |
| 79-missing_prerequisite-r4-primitives | PASS | ur5e.stage_left | UNKNOWN | True | 6 | 11972 | 201 | 3.02 | 3 |
| 80-missing_prerequisite-r4-macro | PASS | ur5e.stage_left | UNKNOWN | True | 3 | 5701 | 77 | 1.45 | 2 |
### Granite 3.3 8B

| Cell | Outcome | Selected skill | Accepted status | Fault exercised | Calls | Input | Output | Task s | Native |
|---|---|---|---|---|---|---|---|---|---|
| 01-move_constrained-r1-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 14741 | 156 | 4.12 | 2 |
| 02-move_constrained-r1-macro | FAIL | ur5e.home | SUCCESS | None | 5 | 12511 | 477 | 5.88 | 3 |
| 03-already_satisfied-r1-macro | PASS | ur5e.stage_left | SUCCESS | None | 5 | 12099 | 134 | 2.17 | 3 |
| 04-already_satisfied-r1-primitives | FAIL | None | None | None | 3 | 6415 | 387 | 4.68 | 0 |
| 05-ineffective_command-r1-primitives | FAIL | ur5e.park_right | None | True | 8 | 21234 | 360 | 8.46 | 3 |
| 06-ineffective_command-r1-macro | FAIL | ur5e.park_right | None | True | 7 | 18631 | 551 | 10.80 | 5 |
| 07-partial_command-r1-macro | FAIL | ur5e.home | SUCCESS | False | 5 | 12802 | 128 | 2.22 | 4 |
| 08-partial_command-r1-primitives | FAIL | ur5e.home | SUCCESS | False | 6 | 14765 | 152 | 2.45 | 2 |
| 09-missing_prerequisite-r1-primitives | FAIL | ur5e.inspect_readiness | SUCCESS | False | 5 | 12049 | 136 | 2.39 | 4 |
| 10-missing_prerequisite-r1-macro | FAIL | ur5e.inspect_readiness | SUCCESS | False | 4 | 9159 | 120 | 1.89 | 2 |
| 11-inspect_healthy-r1-macro | FAIL | None | None | None | 4 | 7456 | 769 | 8.07 | 0 |
| 12-inspect_healthy-r1-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 6 | 12071 | 1134 | 12.05 | 2 |
| 13-inspect_inactive-r1-primitives | FAIL | None | None | False | 4 | 7436 | 824 | 8.62 | 0 |
| 14-inspect_inactive-r1-macro | FAIL | None | None | False | 4 | 7460 | 882 | 9.23 | 0 |
| 15-inspect_missing_controllers-r1-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9752 | 821 | 9.53 | 2 |
| 16-inspect_missing_controllers-r1-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9527 | 532 | 5.73 | 0 |
| 17-inspect_missing_joint-r1-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9548 | 524 | 5.63 | 0 |
| 18-inspect_missing_joint-r1-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9765 | 644 | 6.96 | 2 |
| 19-ambiguous_goal-r1-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 4 | 8237 | 124 | 1.67 | 4 |
| 20-ambiguous_goal-r1-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 5 | 10285 | 140 | 1.90 | 4 |
| 21-inspect_healthy-r2-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 5771 | 99 | 1.30 | 2 |
| 22-inspect_healthy-r2-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 6 | 12071 | 1134 | 12.03 | 2 |
| 23-inspect_inactive-r2-primitives | FAIL | None | None | False | 4 | 7436 | 824 | 8.64 | 0 |
| 24-inspect_inactive-r2-macro | FAIL | ur5e.inspect_readiness | None | True | 6 | 12740 | 985 | 10.61 | 4 |
| 25-inspect_missing_controllers-r2-macro | FAIL | ur5e.inspect_readiness | None | True | 6 | 14142 | 227 | 2.98 | 6 |
| 26-inspect_missing_controllers-r2-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9527 | 499 | 5.69 | 0 |
| 27-inspect_missing_joint-r2-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9560 | 510 | 5.54 | 0 |
| 28-inspect_missing_joint-r2-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 5 | 9766 | 603 | 6.54 | 2 |
| 29-ambiguous_goal-r2-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 4 | 8231 | 122 | 1.64 | 4 |
| 30-ambiguous_goal-r2-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 5 | 10285 | 140 | 1.90 | 4 |
| 31-move_constrained-r2-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 14778 | 156 | 2.25 | 2 |
| 32-move_constrained-r2-macro | FAIL | ur5e.home | SUCCESS | None | 5 | 12511 | 805 | 9.50 | 3 |
| 33-already_satisfied-r2-macro | PASS | ur5e.stage_left | SUCCESS | None | 5 | 12097 | 134 | 1.96 | 3 |
| 34-already_satisfied-r2-primitives | PASS | ur5e.stage_left | SUCCESS | None | 7 | 17582 | 439 | 5.54 | 2 |
| 35-ineffective_command-r2-primitives | FAIL | None | None | False | 4 | 8609 | 1184 | 12.65 | 0 |
| 36-ineffective_command-r2-macro | FAIL | ur5e.park_right | None | True | 7 | 19371 | 360 | 8.69 | 5 |
| 37-partial_command-r2-macro | FAIL | ur5e.home | SUCCESS | False | 6 | 16091 | 620 | 7.57 | 4 |
| 38-partial_command-r2-primitives | FAIL | ur5e.home | None | True | 7 | 17623 | 1511 | 20.89 | 2 |
| 39-missing_prerequisite-r2-primitives | FAIL | ur5e.inspect_readiness | SUCCESS | False | 5 | 12043 | 134 | 2.29 | 4 |
| 40-missing_prerequisite-r2-macro | FAIL | ur5e.inspect_readiness | SUCCESS | False | 4 | 9161 | 122 | 2.89 | 2 |
| 41-move_constrained-r3-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 14784 | 156 | 2.30 | 2 |
| 42-move_constrained-r3-macro | FAIL | ur5e.home | SUCCESS | None | 5 | 12813 | 128 | 2.28 | 4 |
| 43-already_satisfied-r3-macro | PASS | ur5e.stage_left | SUCCESS | None | 5 | 12104 | 136 | 2.29 | 3 |
| 44-already_satisfied-r3-primitives | PASS | ur5e.stage_left | SUCCESS | None | 7 | 17573 | 437 | 5.55 | 2 |
| 45-ineffective_command-r3-primitives | FAIL | None | None | False | 4 | 8609 | 1148 | 12.47 | 0 |
| 46-ineffective_command-r3-macro | FAIL | ur5e.park_right | None | True | 7 | 19358 | 368 | 8.69 | 5 |
| 47-partial_command-r3-macro | FAIL | ur5e.home | SUCCESS | False | 5 | 12818 | 129 | 2.22 | 4 |
| 48-partial_command-r3-primitives | FAIL | ur5e.home | None | False | 6 | 14490 | 1062 | 11.79 | 1 |
| 49-missing_prerequisite-r3-primitives | FAIL | ur5e.inspect_readiness | SUCCESS | False | 5 | 12043 | 134 | 2.21 | 4 |
| 50-missing_prerequisite-r3-macro | FAIL | ur5e.inspect_readiness | SUCCESS | False | 3 | 6784 | 97 | 1.69 | 2 |
| 51-inspect_healthy-r3-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 5 | 9827 | 562 | 6.16 | 2 |
| 52-inspect_healthy-r3-primitives | FAIL | ur5e.inspect_readiness | None | None | 5 | 9654 | 1206 | 12.68 | 0 |
| 53-inspect_inactive-r3-primitives | FAIL | None | None | False | 4 | 7436 | 824 | 8.66 | 0 |
| 54-inspect_inactive-r3-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9859 | 776 | 8.98 | 2 |
| 55-inspect_missing_controllers-r3-macro | FAIL | ur5e.inspect_readiness | None | True | 6 | 14122 | 213 | 3.37 | 6 |
| 56-inspect_missing_controllers-r3-primitives | FAIL | ur5e.inspect_readiness | None | True | 7 | 15006 | 252 | 3.51 | 4 |
| 57-inspect_missing_joint-r3-primitives | FAIL | None | None | False | 4 | 7456 | 806 | 9.10 | 0 |
| 58-inspect_missing_joint-r3-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9765 | 649 | 7.05 | 2 |
| 59-ambiguous_goal-r3-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 4 | 8231 | 122 | 2.36 | 4 |
| 60-ambiguous_goal-r3-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 5 | 10282 | 140 | 1.96 | 4 |
| 61-inspect_healthy-r4-macro | PASS | ur5e.inspect_readiness | SUCCESS | None | 3 | 5772 | 100 | 1.56 | 2 |
| 62-inspect_healthy-r4-primitives | PASS | ur5e.inspect_readiness | SUCCESS | None | 6 | 12074 | 1137 | 12.44 | 2 |
| 63-inspect_inactive-r4-primitives | FAIL | None | None | False | 4 | 7436 | 824 | 8.65 | 0 |
| 64-inspect_inactive-r4-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9863 | 1063 | 11.99 | 2 |
| 65-inspect_missing_controllers-r4-macro | FAIL | ur5e.inspect_readiness | None | True | 5 | 9752 | 821 | 8.83 | 2 |
| 66-inspect_missing_controllers-r4-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9527 | 532 | 5.80 | 0 |
| 67-inspect_missing_joint-r4-primitives | FAIL | ur5e.inspect_readiness | None | False | 5 | 9548 | 524 | 5.71 | 0 |
| 68-inspect_missing_joint-r4-macro | PASS | ur5e.inspect_readiness | UNKNOWN | True | 5 | 9765 | 602 | 6.61 | 2 |
| 69-ambiguous_goal-r4-macro | PENDING | ur5e.inspect_readiness | SUCCESS | None | 4 | 8237 | 124 | 1.72 | 4 |
| 70-ambiguous_goal-r4-primitives | PENDING | ur5e.inspect_readiness | SUCCESS | None | 5 | 10276 | 138 | 1.95 | 4 |
| 71-move_constrained-r4-primitives | FAIL | ur5e.home | SUCCESS | None | 6 | 14783 | 157 | 2.36 | 2 |
| 72-move_constrained-r4-macro | FAIL | ur5e.home | SUCCESS | None | 5 | 12813 | 129 | 2.39 | 4 |
| 73-already_satisfied-r4-macro | PASS | ur5e.stage_left | SUCCESS | None | 5 | 12094 | 132 | 3.10 | 3 |
| 74-already_satisfied-r4-primitives | FAIL | None | None | None | 3 | 6415 | 417 | 4.73 | 0 |
| 75-ineffective_command-r4-primitives | FAIL | ur5e.park_right | None | False | 5 | 11676 | 1200 | 12.96 | 0 |
| 76-ineffective_command-r4-macro | FAIL | None | None | False | 4 | 8605 | 925 | 10.02 | 0 |
| 77-partial_command-r4-macro | FAIL | ur5e.home | SUCCESS | False | 5 | 12797 | 128 | 2.09 | 4 |
| 78-partial_command-r4-primitives | FAIL | ur5e.home | None | False | 6 | 14486 | 1033 | 11.92 | 1 |
| 79-missing_prerequisite-r4-primitives | FAIL | ur5e.inspect_readiness | SUCCESS | False | 5 | 12049 | 136 | 2.31 | 4 |
| 80-missing_prerequisite-r4-macro | FAIL | ur5e.inspect_readiness | SUCCESS | False | 3 | 6784 | 97 | 1.70 | 2 |
