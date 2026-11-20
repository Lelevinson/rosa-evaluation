# G1 Qwen lab execution report

Date: **2026-11-19**. **Lab hardware; not directly comparable to M4.**

All **76/76** scheduled mock attempts are retained. Outcomes: **{'PASS': 56, 'FAIL': 17, 'PENDING_HUMAN_REVIEW': 3, 'INFRA_CENSORED_PRE_OUTPUT': 0, 'INFRA_CENSORED_POST_ACTION': 0}**. New clarification responses require real blinded human ratings; no previous ratings have been reused.

Requests: **198 inference + 1 auxiliary model load = 199/611 charged**. Reserve retries: 0. Campaign elapsed: 1210.25s. Local and persisted Phoenix audits: **76/76 each**. All frozen hashes reverified.

## Correctness and costs

| Measure | Primitives | Macro |
|---|---:|---:|
| Outcomes | {'PASS': 26, 'FAIL': 11, 'PENDING_HUMAN_REVIEW': 1} | {'PASS': 30, 'FAIL': 6, 'PENDING_HUMAN_REVIEW': 2} |
| All-attempt calls | 123 | 75 |
| Known input tokens | 264961 | 152127 |
| Known output tokens | 25878 | 18791 |
| Native operations | 100 | 106 |
| Total measured task seconds | 322.21557368710637 | 239.85832398664206 |
| Mean task seconds | 8.479357202292272 | 6.312061157543212 |
| Median task seconds | 7.925602282397449 | 5.899545609019697 |
| Invalid attempts | 9 | 2 |
| Length stops | 4 | 3 |
| Budget exhaustion | 0 | 0 |

**25 matched successful pairs** exclude any failed, censored or human-pending pair. These are a conditional efficiency view; all-attempt costs above remain primary operational accounting.

| Matched successful pairs | Primitives | Macro |
|---|---:|---:|
| calls | 87 | 52 |
| known_input_tokens | 194620 | 107787 |
| known_output_tokens | 17800 | 12327 |
| native_operations | 87 | 86 |
| task_seconds | 221.62628123164177 | 159.90291311312467 |

## Returned Ollama timing evidence

- primitives: 123 physical records; decode 89.96031452827731 tokens/s, prompt 11490.183987589216 tokens/s from summed recorded counts/durations. Field presence: {'total_duration': 123, 'load_duration': 123, 'prompt_eval_count': 123, 'prompt_eval_duration': 123, 'eval_count': 123, 'eval_duration': 123}.
- macro: 75 physical records; decode 89.54835244174305 tokens/s, prompt 8566.766799627901 tokens/s from summed recorded counts/durations. Field presence: {'total_duration': 75, 'load_duration': 75, 'prompt_eval_count': 75, 'prompt_eval_duration': 75, 'eval_count': 75, 'eval_duration': 75}.

Missing counters are not zero or estimated. Prompt cache and cold-load effects are retained. This is not a controlled hardware comparison, and hosted Sol time cannot isolate model speed against this local backend.

## Scope, limitations and next action

Frozen G1 AI-authored mock cases, shared tools and matched task budgets were used. This is not new Gazebo work, an unmodified-ROSA comparison, independent case authorship or evidence of general model parity. Condition wording remains part of the manipulated package. The optional catalogue-size probe is not run (P4); P3 was dropped.

All attempts, unsuccessful outcomes and raw traces are preserved. No runtime prompt tuning, failed-trial replacement, new inference for reporting or architecture change occurred. The independent observer establishes the scoped goal outcome separately from accepted report truthfulness.

Return the new blinded review CSV and declaration to complete ambiguous-case adjudication. The frozen final analysis and prediction verdicts remain withheld while required judgments are pending. No new experiment is started by this report.

Detailed per-family outcomes, failure components, timing coverage and raw-result hashes: [completed-report/results.json](operator/completed-report/results.json). Launch evidence: [checklist](operator/LAUNCH_CHECKLIST_ADDENDUM.md).
