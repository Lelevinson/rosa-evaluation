# Live prompt-contract validation

Known development cases, one run per case/condition; not a causal efficacy study.

## ollama

Status: COMPLETE; 9/9 correct; 34 reserved inference requests.

Scoreable completed trials: 9; censored attempts: 0; unstarted cells: 0. A service-censored raw score is not an established model failure.

| Condition | Correct | Calls | Input tokens | Output tokens | Native operations | Invalid attempts | Corrected trials | Trial seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| workflow | 3/3 | 9 | 20087 | 1980 | 9 | 0 | 0 | 299.06 |
| model | 3/3 | 16 | 39986 | 3210 | 9 | 1 | 1 | 449.30 |
| macro | 3/3 | 9 | 19971 | 1696 | 9 | 0 | 0 | 230.59 |

Engineering gate: True. Progression gate: True.

## siwc

Status: STOPPED; 4/5 correct; 13 reserved inference requests.

Scoreable completed trials: 4; censored attempts: 1; unstarted cells: 4. A service-censored raw score is not an established model failure.

| Condition | Correct | Calls | Input tokens | Output tokens | Native operations | Invalid attempts | Corrected trials | Trial seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| workflow | 1/1 | 2 | 2903 | 55 | 2 | 0 | 0 | 12.13 |
| model | 1/2 | 6 | 7233 | 126 | 2 | 0 | 0 | 54.48 |
| macro | 2/2 | 5 | 7537 | 137 | 4 | 0 | 0 | 29.45 |

Failed frozen contract: 04-missing_prerequisite-model. Score: `{"accepted_report_status": null, "accepted_unsupported_selected_goal_success": false, "accepted_wrong_user_goal_success": false, "correct_skill": true, "corrected_after_feedback": false, "coverage_pass": true, "dispatch_count": 0, "dispatch_violations": [], "escalations": [], "expected_status": "UNKNOWN", "injected_fault_exercised": true, "invalid_attempts": 0, "legacy_outcome_contract_pass": false, "normal_terminal": false, "pass": false, "pass_with_required_coverage": false, "program_native_operations": 0, "requested_goal_attained": false, "requested_goal_command_attempted": false, "required_dispatches": 0, "transient_observation_failure_seen": false, "truthful_report": false, "unsupported_success_attempts": 0}`

Engineering gate: False. Progression gate: False.

## Interpretation

The opt-in repair changes the common system-prefix instructions only. Historical results remain intact. Known cases and tiny sample size prohibit a general reliability or causal prompt-effect claim. Task outcomes, engineering conformance and readiness to progress are reported separately. A correct outcome after rejected attempts is a combined-system result; it does not erase the model error. Program-managed native operations are explicitly attributed to ROSA. This validation retains the preceding scorer: one-additional-read wording is guidance and is not independently enforced as a hard retry ceiling. Exceedances must be disclosed as behavior, not silently rescored. The fresh pilot proposes explicit prospective retry-policy scoring.

Overall engineering gate: False. Overall progression gate: False.

No fresh held-out pilot may start automatically while its readiness gate is false. Do not repair/tune prompts on these outcomes and relabel a repeat as this frozen validation.
