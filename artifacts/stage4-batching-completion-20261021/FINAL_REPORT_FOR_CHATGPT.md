# Stage 4 completion: results, conclusions and next steps

This is the final report for the simplified Stage 4 authorized after the
negative original-JTVR policy comparison. Both backend schedules and their
state/Phoenix records have been reviewed, with eight explicitly documented
missing recovery-stop tool spans. The frozen auditor/supervisor failure is
preserved alongside a separate reconciliation. An unfavorable outcome is a valid stage
completion; it is not a claim that batching or either model is robot-ready.

## Decisions

- **gpt-6.1-sol**: the predefined batching retention screen was not met; keep model-selected planning as the reference and batching optional.
- **qwen3.5:9b**: the predefined batching retention screen was not met; keep model-selected planning as the reference and batching optional.
  No pair completed successfully under both arms, so a successful-task cost/time benefit is not estimable. This is an unsuccessful integration screen, not proof that the selector is intrinsically ineffective for this model.

Original bounded-lookahead JTVR remains paused. It tied strong amortized
batching in all 96 primary policy fixtures; it offered zero additional
modeled cost benefit and used more recorded selector time. Do not relabel batching
as JTVR or infer that a full custom Runnable was implemented.

## Scope and project history

The shared Qwen/hosted ROSA interface, Phoenix tracing and stateful mock
benchmark predate this campaign. Baseline v1 has 540 scripted and 120 live
trials. Original hosted/local baseline handling scores remain 30/36 and
24/36; retrospective stricter contract checks remain 30/36 and 12/36.
Both originally verified all 18 achievable baseline goals. Wrong report
arguments and attempted picks with UNKNOWN pose were material local issues;
controller rejection is a protection, not credit for model policy.

The canceled V2 hosted batch made zero model requests while awaiting
consent. The fixed dependency bundle once named jtvr was never the original
algorithm. Its 264 scripted controls and nine local diagnostics remain
separate. The subsequent original-spec policy tier has 1,152 episodes plus
15 real ROS smoke cases, with no model requests. The present campaign is
the prospective live follow-up; none of those historical samples are pooled.

The superseded 120-trial V2 live schedule, including the 60 expanded movement
fixtures, was not resumed. This authorized simplified completion uses six
development reliability fixtures and eight real-parameter templates. The
expanded movement suite remains scripted-only; no held-out live movement
generalization result is claimed.

## Frozen methods and limits

Freeze time UTC: `2026-10-21T12:49:16.325052+00:00`. SHA-256: `36912701feba9d7159eaae5c54b4c63196930636098f4d465b7ff4f87664f484`.
80 trials per backend: 48 independent reliability-intervention trials and
32 end-to-end parameter-task trials. Two repeats, fresh agent/world/cache
per trial, balanced arm order. Reliability has six development fixtures;
batching has eight nominal templates. Repetitions are not new task families.

The real ROSA AgentExecutor and existing backend factory run every live
trial. Default ROSA tools are disabled for isolation: the parameter track
registers six supported native schemas plus the shared helper/report tools.
This is not a full-catalogue tool-confusion benchmark. Local Qwen uses the unchanged 8192/256, temperature0, seed42, mmaptrue
profile. Hosted uses exact account-catalog model gpt-6.1-sol with account
defaults. Provider sampling, context and hidden KV behavior are unequal.
No model upgrades, episodic memory or unreported evaluation reruns.

Per backend: hard cap 1,056 model requests, 240 seconds/trial and six hours.
Reliability caps 14 model calls/trial; batching caps 12. The native parameter
budget target is 24 operations/trial; the write-dispatch enforcement gap
is disclosed below with observed counts. OAuth credentials stay in memory and are
revoked; request records exclude transport-only private continuation data.

The loaded local model identity and actual context were checked using read-only
Ollama metadata during execution. The observation, quantization/digest and
GPU snapshot are included in the package; they do not alter inference settings.
Ten-second host memory samples are provided separately from per-trial timings.
They are sampled host free memory, not process memory peaks or proof of a
specific performance bottleneck. See analysis.json for exact runtime fields.

### Completed run ledger

| Backend | Start UTC | Finish UTC | Model requests / cap | Reported total tokens | Cleanup |
| --- | --- | --- | ---: | ---: | --- |
| siwc | 2026-10-21T12:49:50.879835+00:00 | 2026-10-21T13:21:43.540563+00:00 | 429 / 1056 | 788604 | REVOKED |
| ollama | 2026-10-21T13:22:20.543608+00:00 | 2026-10-21T15:08:56.949892+00:00 | 576 / 1056 | 1496711 | No OAuth session for local backend |

The hosted refresh count is 0.
Audit time and setup are outside per-trial agent timings. Total token
metadata is retained as reported by each backend; the tokenizers and
provider accounting differ, so totals are not directly comparable costs.

| Backend | Turns with prompt metadata | Maximum reported prompt tokens | Maximum reported completion tokens | Output-limit turns |
| --- | ---: | ---: | ---: | ---: |
| siwc | 429 | 2680 | 78 | 0 |
| ollama | 576 | 3494 | 256 | 6 |

These are reported token observations, not an inspection of hidden context
truncation or KV state. Output-limit events differ from iteration-limit exits;
a bounded final narrative can be truncated even after a valid structured
report. Diagnose performance and interface behavior separately before tuning.

## Reliability results

Each intervention arm has 12 trials: transfer, accepted failure and missing
sensor, two variants and two repetitions. Controls use original instructions;
clarification, bounded recovery and enforced verification are separate.

| Backend | Intervention | Strict passes | Combined passes | Operational failures | Mock goal states reached | Critical prerequisite violations | Noncompliant / missing reports | Model calls | Auto verifications / guard recoveries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| siwc | original | 8/12 | 8/12 | 0 | 4 | 0 | 0 | 72 | 0 / 0 |
| siwc | clarified | 12/12 | 12/12 | 0 | 4 | 0 | 0 | 76 | 0 / 0 |
| siwc | bounded_recovery | 10/12 | 10/12 | 0 | 4 | 0 | 0 | 74 | 0 / 0 |
| siwc | enforce_verification | 12/12 | 12/12 | 0 | 4 | 0 | 0 | 73 | 3 / 0 |
| ollama | original | 0/12 | 0/12 | 4 | 4 | 14 | 12 | 136 | 0 / 0 |
| ollama | clarified | 4/12 | 4/12 | 2 | 4 | 0 | 6 | 104 | 0 / 0 |
| ollama | bounded_recovery | 4/12 | 4/12 | 0 | 4 | 4 | 4 | 80 | 2 / 8 |
| ollama | enforce_verification | 0/12 | 0/12 | 4 | 4 | 14 | 12 | 136 | 0 / 0 |

These goal states belong to the mock world; no robot moved. Goal achievement
is expected only on achievable transfer cases. Correct
failure/unknown handling is still required on the other cases. Strict
compliance and operational completion are reported separately. Repairs
belong to the combined system. No single intervention is silently credited
with another intervention or with a controller rejecting unsafe attempts.
The bounded guard can stop repetition but cannot erase an invalid action
attempt that happened before activation; such trials retain their critical
contract violations even when the orchestrator subsequently reports correctly.
Compare prospective arms with each other; their 12-trial fixture mix differs
from the original 36-trial baseline, so those percentages are not a direct
before/after improvement estimate.
The battery=-1 sentinel is a deliberately strict API convention, not a
physical robotics requirement. Reporting the observed battery instead can
fail this contract even when the goal was reached. That differs materially
from an attempted action with UNKNOWN pose. Keep error severity separate;
a future task-specific report schema can remove irrelevant fields, tested
prospectively without rewriting these scores.

siwc: bounded recovery had 0 actual guard recoveries; enforced verification added 3 automatic checks.
The bounded-arm pass difference occurred without a guard recovery, so it is not demonstrated benefit from the repair mechanism; sampling/behavior variability remains an explanation.
Clarification alone produced 12/12 combined passes versus 8/12 with original instructions. This is a small within-profile screen, not a general model ranking or independently confirmed intervention effect.
6 failures across the reliability arms had accurate outcome classification and compliant report arguments, with the missing required verifier step as their recorded contract defect. In UNKNOWN sensor cases, this final verifier invocation is a task-contract requirement; omitting it is not equivalent to an unsafe action or a false claim of success.

ollama: bounded recovery had 8 actual guard recoveries; enforced verification added 0 automatic checks.
Clarification alone produced 4/12 combined passes versus 0/12 with original instructions. This is a small within-profile screen, not a general model ranking or independently confirmed intervention effect.
0 failures across the reliability arms had accurate outcome classification and compliant report arguments, with the missing required verifier step as their recorded contract defect. In UNKNOWN sensor cases, this final verifier invocation is a task-contract requirement; omitting it is not equivalent to an unsafe action or a false claim of success.

### Descriptive failure breakdown by fixture family

Four attempts per family/arm. These are descriptive diagnostics, not extra
retention tests. Critical counts are violating action indices, while rejected
attempts count controller rejections. Missing reports differ from reports
with bad arguments; the aggregate noncompliance column above includes both.

| Backend | Family | Arm | Combined passes | Iteration-limit exits | Rejected actions | Critical violations | Bad report-argument trials | Raw argument-error trials | False / unsupported success claims | Missing verification at report |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| siwc | accepted_failure | original | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | accepted_failure | clarified | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | accepted_failure | bounded_recovery | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | accepted_failure | enforce_verification | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | missing_sensor | original | 0/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 4 |
| siwc | missing_sensor | clarified | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | missing_sensor | bounded_recovery | 2/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 2 |
| siwc | missing_sensor | enforce_verification | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | transfer | original | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | transfer | clarified | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | transfer | bounded_recovery | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| siwc | transfer | enforce_verification | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| ollama | accepted_failure | original | 0/4 | 2 | 0 | 0 | 2 | 0 | 0 / 0 | 0 |
| ollama | accepted_failure | clarified | 0/4 | 2 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| ollama | accepted_failure | bounded_recovery | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| ollama | accepted_failure | enforce_verification | 0/4 | 2 | 0 | 0 | 2 | 0 | 0 / 0 | 0 |
| ollama | missing_sensor | original | 0/4 | 2 | 14 | 14 | 2 | 0 | 0 / 0 | 0 |
| ollama | missing_sensor | clarified | 0/4 | 0 | 0 | 0 | 4 | 0 | 0 / 0 | 4 |
| ollama | missing_sensor | bounded_recovery | 0/4 | 0 | 4 | 4 | 0 | 0 | 0 / 0 | 0 |
| ollama | missing_sensor | enforce_verification | 0/4 | 2 | 14 | 14 | 2 | 0 | 0 / 0 | 0 |
| ollama | transfer | original | 0/4 | 0 | 0 | 0 | 4 | 0 | 0 / 0 | 0 |
| ollama | transfer | clarified | 4/4 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 |
| ollama | transfer | bounded_recovery | 0/4 | 0 | 0 | 0 | 4 | 0 | 0 / 0 | 0 |
| ollama | transfer | enforce_verification | 0/4 | 0 | 0 | 0 | 4 | 0 | 0 / 0 | 0 |

## End-to-end batching: what was actually compared

Both arms have the same primitive ROSA tools, strong cost guidance, evidence
ledger and read_parameter_evidence convenience executor. Native helper
arguments are the model-generated requirement manifest; no annotated manifest
is supplied to the optimizer. Missing report/verification fields or targets
produce a recorded error and no hidden reads. Primitive-tool fallback remains
available. Invalid manifests are not silently filled by the evaluator.

Reference honors the model-preferred direct/bulk/node_bulk plan. Candidate
uses amortized selection over the same declared needs and capabilities.
Both can execute discovery plus bulk in one model tool call. This is a
matched orchestration baseline, stronger than withholding bulk from reference,
and is not untouched upstream ROSA. Extra helper schemas are shared costs.

Selector costs reuse the small development calibration from the earlier
policy study (two samples per tool). Its separately frozen hash is verified
again in this analysis; no test-outcome recalibration is performed. These
weights guide selection but are not a latency guarantee on live tasks.

The comparison isolates automatic plan selection on top of a shared batching
executor. A primitive-only untouched-ROSA arm was not run. Consequently,
this study cannot establish the helper/continuation speedup over upstream
ROSA, or conclude that batching in general is unnecessary. Model-selected
planning here still retains access to the tested batching executor.

Eight templates: single, three cold, three warm, write/report/verify, mixed
report/verification roles, node-summary overlap, two-node scope, and parameters
plus topic details. Real scoped ROS parameter nodes are used; no robot motion.
Resets and independent evaluator queries are logged outside agent work.
Charged type warm-up, writes, failed attempts and automatic reads are included.

The nominal two-node case initializes both nodes to the same numeric values.
Its ledger checks separate acquisition and exact entity identifiers; it does
not demonstrate discrimination of differing values across nodes. Independently
varying node values is required in a broader scope/generalization campaign.

Agent wall time includes agent construction, charged warm-up, model calls,
tool work and generation of the final answer. It excludes outside-trial
reset/evaluator operations, trace flush/export and artifact writes. Reported
server RPC counts are the instrumented parameter-service callbacks, not all
DDS traffic. Free-form final prose is preserved but not semantically graded;
correctness uses the structured report and independent state/evidence.

| Backend | Arm | Combined passes | Strict passes | Operational failures | Model calls | Input / output tokens | CLI commands | Server RPCs | Total / median trial s | Selector / parser elapsed s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| siwc | model_selected | 16/16 | 16/16 | 0 | 67 | 150687 / 3150 | 48 | 30 | 318.282 / 17.600 | 0.000 / 0.007 |
| siwc | amortized_batching | 16/16 | 16/16 | 0 | 67 | 150679 / 3152 | 48 | 30 | 352.605 / 16.775 | 0.007 / 0.006 |
| ollama | model_selected | 0/16 | 0/16 | 14 | 60 | 174534 / 6255 | 66 | 58 | 856.112 / 47.931 | 0.000 / 0.002 |
| ollama | amortized_batching | 0/16 | 0/16 | 14 | 60 | 174502 / 6163 | 54 | 38 | 811.343 / 45.381 | 0.007 / 0.006 |

### Matched successful pairs and retention screen

Native work means actual CLI commands, fixed in the analysis clarification
before any batching outcomes. RPC counts are secondary. No speed credit is
given for early failed termination. All-attempt totals appear above.

Relative reduction uses one minus the candidate/reference ratio of summed
matched wall times or work, not the difference of medians. The median can
move in a different direction when a few longer trials dominate the total.

| Backend | Both successful pairs | Excluded pairs | Candidate-only / reference-only success | Time reduction | CLI reduction | Time interval | CLI interval | Retain screen |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| siwc | 16/16 | 0 | 0 / 0 | -10.78% | 0.00% | -28.80%, 1.33% | 0.00%, 0.00% | False |
| ollama | 0/16 | 16 | 0 / 0 | not estimable | not estimable | not estimable, not estimable | not estimable, not estimable | False |

Screen: no observed total completion loss plus >=10% matched successful
time or CLI reduction, with nonnegative direction in both repetitions.
Bootstrap intervals cluster by available task templates (at most eight), 2,000 resamples, seed
20261021. They are descriptive, not proof of safety/noninferiority. The
machine-readable analysis includes each repetition and every paired outcome.

As an exploratory mechanism check, inspect whether paired primitive-tool
count vectors differ. A timing-only screen result with identical native work
does not by itself establish that deterministic selection caused a speedup;
model serving and action-generation variability remain explanations.

siwc: 14/16 paired trials had identical primitive-tool count vectors.
ollama: 8/16 paired trials had identical primitive-tool count vectors.

## Model communication of requirements

| Backend | Arm | Raw helper calls | Raw well-typed calls | Recorded / post-schema valid requests | First-valid trials | Complete parameter-node union | Bypassed trials | Phase errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| siwc | model_selected | 18 | 18 | 18 / 18 | 16/16 | 16/16 | 0 | 0 |
| siwc | amortized_batching | 18 | 18 | 18 / 18 | 16/16 | 16/16 | 0 | 0 |
| ollama | model_selected | 14 | 14 | 14 / 14 | 12/16 | 12/16 | 4 | 0 |
| ollama | amortized_batching | 14 | 14 | 14 / 14 | 12/16 | 12/16 | 4 | 0 |

A passing task can bypass the helper using primitive reads; that is not a
successful manifest extraction. A complete per-node union differs from a
valid first request on only one node. Preferred strategy distributions,
manifest contents, corrections and evidence are retained per trial. This
tests a supported structured tool interface, not general language understanding.
Queries explicitly name parameters. Union coverage refers to parameter-node
requirements; graph/topic needs are checked separately in task compliance.
Post-schema validity can differ from raw typing; strict scoring checks raw
arguments too, and calls rejected before entering the helper remain visible
in the raw-call denominator. No general manifest-extraction claim is made.

### Report-interface failures

The helper returns node_name plus a flat observed_values object for that
node; the report tool requires observed_values nested by node. The model
must perform that conversion. ROSA currently returns an error and aborts
the trial on an unhandled tool-schema validation error, so this study does
not measure whether a model could correct that error with bounded feedback.
A valid read manifest followed by a malformed report is a combined-system
failure, not evidence that the model could not identify its read requirements.

| Backend | Arm | Schema-validation abort trials | Trials with flat raw report values | Report keys missing node leading slash |
| --- | --- | ---: | ---: | ---: |
| siwc | model_selected | 0 | 0 | 0 |
| siwc | amortized_batching | 0 | 0 | 0 |
| ollama | model_selected | 14 | 14 | 2 |
| ollama | amortized_batching | 14 | 14 | 2 |

Required structured fields and details are graded. Arbitrary additional
claims and final prose are not exhaustively semantically evaluated. A future
report contract should define and test extra-field/extra-claim behavior.

The leading-slash diagnostic describes a raw identifier mismatch; it does
not canonically rewrite identifiers or award retrospective passes. A correctly
observed number can still be unsupported under an incorrectly scoped report key.

## Every failed trial

### siwc: 6 failures out of 80 attempts

- `44497371-80f3-4971-9d04-2bc50ab728b5` — reliability / s040 / repeat 0 / original / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/44497371-80f3-4971-9d04-2bc50ab728b5/evidence.json).
- `1d858924-ece7-4b84-8ed5-0bb52fafda91` — reliability / s040 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/1d858924-ece7-4b84-8ed5-0bb52fafda91/evidence.json).
- `8044f452-56d4-4e10-8d1b-3851d790d79f` — reliability / s041 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/8044f452-56d4-4e10-8d1b-3851d790d79f/evidence.json).
- `ddf0703f-3439-48ae-a433-924d965cca46` — reliability / s041 / repeat 0 / original / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/ddf0703f-3439-48ae-a433-924d965cca46/evidence.json).
- `030d2d1c-8501-4b10-b2d5-073962d90cf4` — reliability / s040 / repeat 1 / original / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/030d2d1c-8501-4b10-b2d5-073962d90cf4/evidence.json).
- `833f3ede-1e99-423f-908d-a9f1d7d3ddc2` — reliability / s041 / repeat 1 / original / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](siwc/trials/833f3ede-1e99-423f-908d-a9f1d7d3ddc2/evidence.json).

### ollama: 72 failures out of 80 attempts

- `2cf69379-a821-45c7-86e7-6245429def75` — reliability / s010 / repeat 0 / original / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/2cf69379-a821-45c7-86e7-6245429def75/evidence.json).
- `55628532-5624-43c4-8103-c4016e116596` — reliability / s010 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/55628532-5624-43c4-8103-c4016e116596/evidence.json).
- `f6b87dd1-e60e-430a-a064-61ca1a1e68b7` — reliability / s010 / repeat 0 / enforce_verification / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/f6b87dd1-e60e-430a-a064-61ca1a1e68b7/evidence.json).
- `f0a76205-0ad2-4df4-a2af-ebf921e2b8b7` — reliability / s011 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/f0a76205-0ad2-4df4-a2af-ebf921e2b8b7/evidence.json).
- `f645472d-1453-41a0-b765-49672153845c` — reliability / s011 / repeat 0 / enforce_verification / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/f645472d-1453-41a0-b765-49672153845c/evidence.json).
- `27ecdbee-f4dc-4f67-9b5e-9957873cb2ee` — reliability / s011 / repeat 0 / original / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/27ecdbee-f4dc-4f67-9b5e-9957873cb2ee/evidence.json).
- `3ab69381-bd81-46d2-9c4f-f68c6072050b` — reliability / s020 / repeat 0 / enforce_verification / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[{"index":12,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[{"index":5,"reason":"retry_after_verified_failed_pick"},{"index":9,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/3ab69381-bd81-46d2-9c4f-f68c6072050b/evidence.json).
- `b1365d47-b845-43bb-b2d6-ea9f0e41cf0c` — reliability / s020 / repeat 0 / original / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[{"index":12,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[{"index":5,"reason":"retry_after_verified_failed_pick"},{"index":9,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/b1365d47-b845-43bb-b2d6-ea9f0e41cf0c/evidence.json).
- `e44001d0-fc86-4e29-a1fe-aa686d7bc565` — reliability / s020 / repeat 0 / clarified / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/e44001d0-fc86-4e29-a1fe-aa686d7bc565/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `48a4d995-29ba-4c93-b822-15aa3fa91923` — reliability / s021 / repeat 0 / enforce_verification / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/48a4d995-29ba-4c93-b822-15aa3fa91923/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `4a678958-4178-4419-b09d-5903b020dc99` — reliability / s021 / repeat 0 / original / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/4a678958-4178-4419-b09d-5903b020dc99/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `8ac405a6-9539-4230-8687-53fa585b2d74` — reliability / s021 / repeat 0 / clarified / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/8ac405a6-9539-4230-8687-53fa585b2d74/evidence.json).
- `3980c50c-5447-4860-ba58-69ab54ae9a56` — reliability / s040 / repeat 0 / original / none; operational failure=False, exception=None, calls=10. Reasons: `{"report_argument_errors":[{"index":8,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":2,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/3980c50c-5447-4860-ba58-69ab54ae9a56/evidence.json).
- `3b38b297-7fc1-4772-8a7f-b061acc2a6db` — reliability / s040 / repeat 0 / clarified / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[{"index":2,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/3b38b297-7fc1-4772-8a7f-b061acc2a6db/evidence.json).
- `a5770df5-a7cd-43b6-8887-627d21e264ce` — reliability / s040 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=6. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":1,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/a5770df5-a7cd-43b6-8887-627d21e264ce/evidence.json).
- `65fe8400-632b-44fe-9776-470d746a4abe` — reliability / s040 / repeat 0 / enforce_verification / none; operational failure=False, exception=None, calls=10. Reasons: `{"report_argument_errors":[{"index":8,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":2,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/65fe8400-632b-44fe-9776-470d746a4abe/evidence.json).
- `678c20d0-41a7-4604-9fe6-0ba1a2a8e568` — reliability / s041 / repeat 0 / clarified / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[{"index":2,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/678c20d0-41a7-4604-9fe6-0ba1a2a8e568/evidence.json).
- `6cc04329-bb91-46f3-b195-f4e4e9811e14` — reliability / s041 / repeat 0 / bounded_recovery / none; operational failure=False, exception=None, calls=5. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":1,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/6cc04329-bb91-46f3-b195-f4e4e9811e14/evidence.json).
- `784d9675-41d1-49e9-8abb-68675425051a` — reliability / s041 / repeat 0 / enforce_verification / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":5,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/784d9675-41d1-49e9-8abb-68675425051a/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `0731cc2e-6f7d-42ef-b1d2-667170da1fe6` — reliability / s041 / repeat 0 / original / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":5,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/0731cc2e-6f7d-42ef-b1d2-667170da1fe6/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `a0eb028c-55e6-40ec-bfb3-dd4995f5c5b3` — reliability / s010 / repeat 1 / bounded_recovery / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/a0eb028c-55e6-40ec-bfb3-dd4995f5c5b3/evidence.json).
- `fb69e25e-8fa4-48e9-b4bc-6af5f75e923d` — reliability / s010 / repeat 1 / enforce_verification / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/fb69e25e-8fa4-48e9-b4bc-6af5f75e923d/evidence.json).
- `6e0a8e50-a9b3-44ac-9057-15bc285a5af8` — reliability / s010 / repeat 1 / original / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/6e0a8e50-a9b3-44ac-9057-15bc285a5af8/evidence.json).
- `cc212329-9260-4b43-b2e0-42a4d24f8cbc` — reliability / s011 / repeat 1 / bounded_recovery / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/cc212329-9260-4b43-b2e0-42a4d24f8cbc/evidence.json).
- `aec795cc-f7b6-44b0-953a-a99294a70487` — reliability / s011 / repeat 1 / enforce_verification / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/aec795cc-f7b6-44b0-953a-a99294a70487/evidence.json).
- `b22df5c6-347e-493e-bded-07e29441b733` — reliability / s011 / repeat 1 / original / none; operational failure=False, exception=None, calls=8. Reasons: `{"report_argument_errors":[{"index":6,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/b22df5c6-347e-493e-bded-07e29441b733/evidence.json).
- `fca8a19b-e13a-45af-bc20-301b1051699b` — reliability / s020 / repeat 1 / enforce_verification / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[{"index":12,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[{"index":5,"reason":"retry_after_verified_failed_pick"},{"index":9,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/fca8a19b-e13a-45af-bc20-301b1051699b/evidence.json).
- `456c7918-c614-49f9-9e32-c1621ff751bd` — reliability / s020 / repeat 1 / original / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[{"index":12,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[{"index":5,"reason":"retry_after_verified_failed_pick"},{"index":9,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/456c7918-c614-49f9-9e32-c1621ff751bd/evidence.json).
- `2a53b07e-4f29-4fb2-b4c0-8a2b79f35802` — reliability / s020 / repeat 1 / clarified / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/2a53b07e-4f29-4fb2-b4c0-8a2b79f35802/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `c3458011-fe11-4d22-ae5f-f4440b60137d` — reliability / s021 / repeat 1 / original / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/c3458011-fe11-4d22-ae5f-f4440b60137d/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `03363384-2f2b-4256-b283-5bdd9e579dea` — reliability / s021 / repeat 1 / clarified / none; operational failure=False, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/03363384-2f2b-4256-b283-5bdd9e579dea/evidence.json).
- `d39d473a-04d7-4902-a786-d12f28aa03bb` — reliability / s021 / repeat 1 / enforce_verification / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[{"index":6,"reason":"retry_after_verified_failed_pick"},{"index":10,"reason":"retry_after_verified_failed_pick"}],"critical_prerequisite_violations":0,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/d39d473a-04d7-4902-a786-d12f28aa03bb/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `f8172788-1e3c-4349-890f-1e4888d7412e` — reliability / s040 / repeat 1 / clarified / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[{"index":2,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/f8172788-1e3c-4349-890f-1e4888d7412e/evidence.json).
- `5c4ba5b2-9660-4f5d-b820-e2aac4f7bcaa` — reliability / s040 / repeat 1 / bounded_recovery / none; operational failure=False, exception=None, calls=6. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":1,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/5c4ba5b2-9660-4f5d-b820-e2aac4f7bcaa/evidence.json).
- `cbf262f5-2e95-4efe-9330-8b0ff4648ed6` — reliability / s040 / repeat 1 / enforce_verification / none; operational failure=False, exception=None, calls=10. Reasons: `{"report_argument_errors":[{"index":8,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":2,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/cbf262f5-2e95-4efe-9330-8b0ff4648ed6/evidence.json).
- `0be129a7-c854-4730-96d8-9787ce18dcca` — reliability / s040 / repeat 1 / original / none; operational failure=False, exception=None, calls=10. Reasons: `{"report_argument_errors":[{"index":8,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":2,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/0be129a7-c854-4730-96d8-9787ce18dcca/evidence.json).
- `c6169904-b9e2-44ed-b86b-7d744955f07d` — reliability / s041 / repeat 1 / bounded_recovery / none; operational failure=False, exception=None, calls=5. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":1,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/c6169904-b9e2-44ed-b86b-7d744955f07d/evidence.json).
- `1f12da56-1c08-43ae-a07e-ab30c311155f` — reliability / s041 / repeat 1 / enforce_verification / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":5,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/1f12da56-1c08-43ae-a07e-ab30c311155f/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `36dcb2e7-351e-45e7-bd5a-1f870b8279b8` — reliability / s041 / repeat 1 / original / none; operational failure=True, exception=None, calls=14. Reasons: `{"report_argument_errors":[],"instruction_sequence_violations":[],"critical_prerequisite_violations":5,"verification_missing_at_report":0,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/36dcb2e7-351e-45e7-bd5a-1f870b8279b8/evidence.json).
  Operational output: "Agent stopped due to max iterations.".
- `46d89e42-0e88-4db4-9d59-41b28abd0f69` — reliability / s041 / repeat 1 / clarified / none; operational failure=False, exception=None, calls=4. Reasons: `{"report_argument_errors":[{"index":2,"reasons":["nonreading_battery_must_equal_minus_one"]}],"instruction_sequence_violations":[],"critical_prerequisite_violations":0,"verification_missing_at_report":1,"false_success_at_report":0,"unsupported_success_at_report":0,"strict_contract_pass":false}`. [Raw evidence](ollama/trials/46d89e42-0e88-4db4-9d59-41b28abd0f69/evidence.json).
- `212c2fb6-b823-4413-9c63-f3f81e31c79b` — batching / one_parameter__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/212c2fb6-b823-4413-9c63-f3f81e31c79b/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `dda9178a-1ab6-43f0-88cd-441d5b799b80` — batching / one_parameter__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/dda9178a-1ab6-43f0-88cd-441d5b799b80/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `0c19cfd4-b07f-4523-8037-b4414303bc22` — batching / three_cold__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/0c19cfd4-b07f-4523-8037-b4414303bc22/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `3539ff97-f68b-4da3-87cd-60e90033c2e4` — batching / three_cold__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/3539ff97-f68b-4da3-87cd-60e90033c2e4/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `5a420ecb-8f10-42b1-8335-f3e5e4385e8d` — batching / three_warm__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/5a420ecb-8f10-42b1-8335-f3e5e4385e8d/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `1e99fccb-ae0f-48a0-b720-ce19bcfb8823` — batching / three_warm__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/1e99fccb-ae0f-48a0-b720-ce19bcfb8823/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `9caee1b9-b9d7-4532-87c1-c6b57a77c37c` — batching / write_report_verify__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/9caee1b9-b9d7-4532-87c1-c6b57a77c37c/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value='20', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value='40', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value='60', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `61b469ff-a802-48ac-b0b5-cda3febc0966` — batching / write_report_verify__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/61b469ff-a802-48ac-b0b5-cda3febc0966/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value='20', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value='40', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value='60', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `93396620-a110-4e85-abac-27c181ddb44e` — batching / mixed_roles__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/93396620-a110-4e85-abac-27c181ddb44e/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `e964ae5d-6491-4322-9180-4ed6cd53932e` — batching / mixed_roles__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/e964ae5d-6491-4322-9180-4ed6cd53932e/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `bba941aa-bfdb-491a-94be-43797f5e893c` — batching / node_summary_and_parameters__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/bba941aa-bfdb-491a-94be-43797f5e893c/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `227ce6d4-3895-47fa-9655-c575d014ae57` — batching / node_summary_and_parameters__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/227ce6d4-3895-47fa-9655-c575d014ae57/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `e0f2175f-a736-4306-a1a6-e8b5cec7cc5b` — batching / two_node_scope__nominal__0 / repeat 0 / none / model_selected; operational failure=False, exception=None, calls=4. Reasons: `["incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value"]`. [Raw evidence](ollama/trials/e0f2175f-a736-4306-a1a6-e8b5cec7cc5b/evidence.json).
- `d903ee79-fdc9-4caf-ba9d-c3bd7dbdcbe9` — batching / two_node_scope__nominal__0 / repeat 0 / none / amortized_batching; operational failure=False, exception=None, calls=4. Reasons: `["incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value"]`. [Raw evidence](ollama/trials/d903ee79-fdc9-4caf-ba9d-c3bd7dbdcbe9/evidence.json).
- `77f8e56b-2bdf-4d5d-807c-bb609b57c961` — batching / parameters_and_topic_qos__nominal__0 / repeat 0 / none / amortized_batching; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/77f8e56b-2bdf-4d5d-807c-bb609b57c961/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `1ad03673-bb4e-465c-a613-c118369ebc14` — batching / parameters_and_topic_qos__nominal__0 / repeat 0 / none / model_selected; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/1ad03673-bb4e-465c-a613-c118369ebc14/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `043068fd-6549-46c5-9833-c35e601719e2` — batching / one_parameter__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/043068fd-6549-46c5-9833-c35e601719e2/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `1b7471bc-08e9-4c53-a547-bb3ba739864d` — batching / one_parameter__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/1b7471bc-08e9-4c53-a547-bb3ba739864d/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `4f0ad684-afe1-4845-9326-c1a6c6b4d3d4` — batching / three_cold__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/4f0ad684-afe1-4845-9326-c1a6c6b4d3d4/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `976da744-3e32-4ee4-b7f7-64828a49719d` — batching / three_cold__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/976da744-3e32-4ee4-b7f7-64828a49719d/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `eb62e12b-1f73-4ee6-998f-33d227a40f54` — batching / three_warm__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/eb62e12b-1f73-4ee6-998f-33d227a40f54/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `0ada9ff9-b120-46c2-be83-6e5e5cbc9b14` — batching / three_warm__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=2. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/0ada9ff9-b120-46c2-be83-6e5e5cbc9b14/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `db3781b2-2ab2-44f1-8655-1c0c287e88c9` — batching / write_report_verify__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/db3781b2-2ab2-44f1-8655-1c0c287e88c9/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=40, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=60, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `465247d0-b8f2-4662-bcc1-d2df47dd2324` — batching / write_report_verify__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/465247d0-b8f2-4662-bcc1-d2df47dd2324/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=40, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=60, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `7c5e5a0c-b159-4531-86af-424b60ff7228` — batching / mixed_roles__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/7c5e5a0c-b159-4531-86af-424b60ff7228/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `24c62284-963d-43bb-a044-c5128f1ca886` — batching / mixed_roles__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=7. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/24c62284-963d-43bb-a044-c5128f1ca886/evidence.json).
  Operational output: "An error occurred: 1 validation error for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=20, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `cfe9b549-b73a-4ce1-8e12-47cf3850f026` — batching / node_summary_and_parameters__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/cfe9b549-b73a-4ce1-8e12-47cf3850f026/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `6bff62dc-323e-47ee-b41f-75f6c1c502fe` — batching / node_summary_and_parameters__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/6bff62dc-323e-47ee-b41f-75f6c1c502fe/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `2f10aae2-365e-445d-9e22-b8485d9b1303` — batching / two_node_scope__nominal__0 / repeat 1 / none / amortized_batching; operational failure=False, exception=None, calls=4. Reasons: `["incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value"]`. [Raw evidence](ollama/trials/2f10aae2-365e-445d-9e22-b8485d9b1303/evidence.json).
- `e6fe5504-95d3-4684-a61c-3a8956eeefe9` — batching / two_node_scope__nominal__0 / repeat 1 / none / model_selected; operational failure=False, exception=None, calls=4. Reasons: `["incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value","incorrect_or_missing_report_value","unsupported_report_value"]`. [Raw evidence](ollama/trials/e6fe5504-95d3-4684-a61c-3a8956eeefe9/evidence.json).
- `763efde8-ad3d-4d19-8c9d-f956c7f3f1a5` — batching / parameters_and_topic_qos__nominal__0 / repeat 1 / none / model_selected; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/763efde8-ad3d-4d19-8c9d-f956c7f3f1a5/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".
- `2dc9ad4e-ae5e-46c7-8d7a-7957852ab054` — batching / parameters_and_topic_qos__nominal__0 / repeat 1 / none / amortized_batching; operational failure=True, exception=None, calls=3. Reasons: `["expected_exactly_one_report"]`. [Raw evidence](ollama/trials/2dc9ad4e-ae5e-46c7-8d7a-7957852ab054/evidence.json).
  Operational output: "An error occurred: 3 validation errors for submit_parameter_report\nobserved_values.alpha\n  Input should be a valid dictionary [type=dict_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.beta\n  Input should be a valid dictionary [type=dict_type, input_value=2, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type\nobserved_values.gamma\n  Input should be a valid dictionary [type=dict_type, input_value=3, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.14/v/dict_type".

## Audits, preflight corrections and preservation

All 160 live trials have separate state/raw-result and Phoenix records. Passing
an audit means records agree; it does not mean the task passed. Evaluators
are independent of model claims, but share trusted fixture code and some
scoring functions; they are not independently authored or blinded. Native values
were compared with separately recorded ROS server callbacks and independent
final evaluator queries. Every actual native operation has an explicit actor
span. Installed instrumentation parents these spans to the run, so actor
provenance rather than assumed nesting distinguishes them from model dispatches.

**Audit exception:** the frozen hosted audit passed 80/80; the frozen local
audit passed 72/80 and failed eight bounded-recovery trials. Their state
checks and model-call counts agree, but each lacks the final stopped tool
span. InterventionStop derives from BaseException; the installed LangChain
tool handler catches Exception/KeyboardInterrupt, so this signal bypasses
its normal error/finish callback. The original supervisor remains FAILED.
No missing span was fabricated and no task result was rerun or rescored.

The originally specified full audit acceptance check was therefore not
fully met. Stage completion here means closure of the planned experiment
and its analysis with that exception, not a claim that every gate passed.

The separate audit-reconciliation.json accounts for all 160 records using
strict cross-checks: saved raw tool calls, the final LLM tool-call ID/arguments,
callback dispatch count, exact world-call prefix, reconstructed guard predicate
and attributed orchestrator report. All eight exceptions match that one
pattern. Complete tool-span coverage is still false. Five focused checks
cover the supported case and reject extra loss, tampering, absent reports
and nonintervention trials. This is a post-run observability reconciliation,
not an independently authored evaluator or a repair to the frozen auditor.

Before live requests: 72 discovery tests passed, then the focused 11-test
integration suite passed after two added fault/type tests (74 distinct tests
across these runs). Sixteen actual-ROS scripted acceptance cases passed and
a scripted native-message ROSA/Phoenix trace passed. These are controls, not
paid model episodes. Preflight fixes addressed namespace test discovery,
private ROS executor context, CLI graph readiness/timeout, separate Phoenix
client environment, bounded local trace reads and explicit span provenance.
Each failed preflight directory and disposition remains. No model outcome
was discarded to fix these infrastructure errors.

Historical reports and JTVR policy evidence remain frozen. Exact baseline
archive and source identities are preserved rather than retrospectively
rewritten. The new live freeze contains 137 source/input files, including
the sibling research dependency snapshot. The evaluation commit therefore
does not rely only on an uncommitted research checkout being available.

## Practical limits and conclusions

These small nominal parameter tasks test real tool interfaces, not robot
physics, perception, manipulation or arbitrary ROS services. Local epochs
cannot detect arbitrary external writers; no atomic snapshot is guaranteed.
Only exact registered read services and authorized writes are allowed.
A source audit found that the 24-operation guard blocks further native reads
after 24 recorded events, while exact authorized writes lack an independent
dispatch-count guard. Model/time caps still bound them. The observed maxima
and any over-limit trials are reported below; the frozen code is preserved
rather than silently repaired during evaluation. A global dispatch guard is
required before any wider or actuator-facing use. The separate BoundedGateway
class closes that gap and has two focused unit tests; it was not used by the
frozen live study and is not credited with its results.
siwc: maximum 5 native commands, 0 trials above 24; ollama: maximum 6 native commands, 0 trials above 24.
Failure handling is investigated separately in the movement mock track;
real parameter fault/generalization campaigns have not been completed.

The catalogue is small and mainly per-node separable. Strong model planning
can already select the amortized optimum. Equal end-to-end results are a
reason to simplify, not to invent harder tools or revive lookahead without
a grounded need. Repairs and plan substitutions are combined-system effects.
Shared helper execution deliberately removes unequal continuation savings.

Both repetitions share fixtures, dependencies and host. User workloads,
partial GPU offload, warm-up, provider routing and unresettable KV state can
affect latency. Fixed local settings do not make models or token budgets
equivalent. Low error counts do not prove robot safety. Reported tokens
are provider metadata, not a financial cost estimate.

## Recommended next steps and six-stage status

1. Keep the simpler configuration unless this screen supports a scoped
   batching benefit. Keep original-JTVR negative results visible.
2. Choose a specific robot and a bounded Gazebo task: identify its ROS
   distribution, URDF/controllers, planning/skill interface, scene and
   success/verification contract before installing an arbitrary arm stack.
3. Start with read-only state and deterministic arm skills, then test
   high-level model requests under limits and independent verification.
   First test a consistent task-specific report schema and bounded schema-
   validation feedback as a separate prospective interface intervention.
   Do not silently fill missing model fields. Evaluate finishing directly on
   a validated final report to avoid an unnecessary narrative-generation
   turn. These are future variants, not measured benefits of this study.
   Keep a deterministic skill/planner control for fixed tasks. The LLM
   should be evaluated on goal interpretation and flexible task choice,
   not credited with deterministic checks already implemented in tools.
4. Broaden real failure/generalization tasks before making reliability
   claims. Revisit lookahead only if actual catalogue overlap defeats the
   current amortized groups.
5. Defer episodic memory until tasks require history and matched retrieval,
   examples, token budgets, freshness and verification controls are defined.

| Stage | Status |
| --- | --- |
| 1, shared backends | Demonstrated through actual ROSA; both used in this live campaign. |
| 2, contract/scoring | State audits complete; eight tool-span gaps documented and reconciled separately. |
| 3, baseline/reliability | V1 preserved; independent prospective interventions now evaluated. |
| 4, caching/selection | Planned simplified screen and analysis closed with the documented audit exception; neither retention screen met. Full JTVR paused. |
| 5, episodic memory | Not started; no prerequisite to simulator integration. |
| 6, Gazebo/hardware | Simulator foundation installed; specific arm, skills and hardware remain unconfigured. |

## Evidence, reproduction and repository publication

- [Machine-readable analysis](analysis.json), [all 160 trial rows](all-trials.csv).
- [Hosted audit](siwc/audit.json), [local audit](ollama/audit.json).
- [Post-run audit reconciliation](audit-reconciliation.json).
- [Frozen source/input hashes](freeze.json), [jobs](jobs.json).
- [Frozen protocol](../../docs/STAGE4_BATCHING_COMPLETION_PROTOCOL.md).
- [Offline review and reproduction guide](../../docs/STAGE4_EVIDENCE_GUIDE.md).
- [Earlier JTVR report](../stage4-policy-20261021/REPORT_FOR_CHATGPT.md).

Restore the byte-exact frozen evaluation AND research sources from the
snapshot before hash verification; Git line-ending conversion can otherwise
change working-file bytes. Reconstruct the research checkout, install its
locked uv environment and ROS Jazzy dependencies, start the separate Phoenix
service, and verify source hashes. Live commands are the runner/audit modules
recorded in supervisor logs; hosted reruns need fresh consent and a separately
named campaign. Never overwrite this campaign or silently rerun failed data.

This analysis module was added after the execution freeze and performs only
post-run analysis. Its exact source is archived under analysis-source. The
analysis metric clarification was recorded before Track B outcomes.

Publication target: Lelevinson/rosa-evaluation, member/martin. The final
results commit includes code, curated evidence and this report. Its SHA is
provided in the handoff/commit history, avoiding a circular self-hash in the
report. Credentials, environments and raw local databases are excluded.

For ChatGPT review: examine matched-baseline fairness, manifest omissions,
whether interventions help independently, failure attribution and whether
the retention decisions justify the next simulator experiment. The full
evidence package is more informative than headline pass rates alone.
