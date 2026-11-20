# G1 Stage 2 Sol dev report

Date: **2026-11-14**.

**Execution: stopped/incomplete; 26/36 trial records retained.**

This is an AI-authored exploratory engineering/dev run, without independent teammate authorship or semantic-novelty review. It checks the scorer, budget and live execution paths. **P1-P4 are not adjudicated.** No Qwen or later stage was launched.

The restore-only authorization preflight passed after actual provider renewal, unchanged-scope validation and an authenticated Sol catalogue check, using zero inference requests. Provider inference quota remained unknown. The batch rechecked the existing grant at launch; no consent/login fallback was available.

| Condition | Primary correct | Physical model attempts | Known input tokens | Known output tokens | Native attempts | Task time total (s) | Mean / median (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| primitives | 12/13 | 41 | 60528 | 1207 | 30 | 130.05 | 10.00 / 9.80 |
| macro | 13/13 | 25 | 37405 | 841 | 36 | 80.29 | 6.18 / 6.07 |

Primary correctness excludes infrastructure-recovered trials; completion including recovery is separately retained in analysis.json. Token totals are known usage only; incomplete usage is explicitly counted, never assumed zero. Task times include agent construction, local instrumentation and evaluator reads, and exclude subsequent server-side audit work. Campaign elapsed time includes between-trial audit/setup overhead.

Charged requests: **66/291**; infrastructure reserve used: **0/3**. The corrected planning estimate was ~95, not a required target.

Local audits passed: **26/26**. Persisted Phoenix audits passed: **26/26**; **1040 spans** matched. Any retained failed/unstarted work remains visible in status.json.

Actual physical-turn deviations from scripted expectations: **1**. Scripted expectations (inspection 3 primitive vs 2 macro; healthy movement 5 vs 2) are comparators, not requirements imposed on model behavior.

| Trial | Correct | Physical calls | Scripted calls | Native attempts | Accepted status | Budget / length stop |
|---|---:|---:|---:|---:|---|---|
| G1r1-dev-001-macro | True | 2 | 2 | 1 | SUCCESS | False / False |
| G1r1-dev-001-primitives | True | 3 | 3 | 1 | SUCCESS | False / False |
| G1r1-dev-002-macro | True | 2 | 2 | 2 | SUCCESS | False / False |
| G1r1-dev-002-primitives | True | 3 | 3 | 2 | SUCCESS | False / False |
| G1r1-dev-003-macro | True | 2 | 2 | 4 | SUCCESS | False / False |
| G1r1-dev-003-primitives | True | 3 | 3 | 4 | SUCCESS | False / False |
| G1r1-dev-004-macro | True | 2 | 2 | 6 | SUCCESS | False / False |
| G1r1-dev-004-primitives | True | 3 | 3 | 6 | SUCCESS | False / False |
| G1r1-dev-005-macro | True | 2 | 2 | 3 | SUCCESS | False / False |
| G1r1-dev-005-primitives | True | 5 | 5 | 3 | SUCCESS | False / False |
| G1r1-dev-006-macro | True | 2 | 2 | 3 | SUCCESS | False / False |
| G1r1-dev-006-primitives | True | 5 | 5 | 3 | SUCCESS | False / False |
| G1r1-dev-007-macro | True | 2 | 2 | 1 | UNKNOWN | False / False |
| G1r1-dev-007-primitives | True | 3 | 3 | 1 | UNKNOWN | False / False |
| G1r1-dev-008-macro | True | 1 | 1 | 0 | None | False / False |
| G1r1-dev-008-primitives | True | 1 | 1 | 0 | None | False / False |
| G1r1-dev-009-macro | True | 2 | 2 | 1 | SUCCESS | False / False |
| G1r1-dev-009-primitives | True | 3 | 3 | 1 | SUCCESS | False / False |
| G1r1-dev-010-macro | True | 2 | 2 | 2 | SUCCESS | False / False |
| G1r1-dev-010-primitives | True | 3 | 3 | 2 | SUCCESS | False / False |
| G1r1-dev-011-macro | True | 2 | 2 | 4 | SUCCESS | False / False |
| G1r1-dev-011-primitives | True | 3 | 3 | 4 | SUCCESS | False / False |
| G1r1-dev-012-macro | True | 2 | 2 | 6 | SUCCESS | False / False |
| G1r1-dev-012-primitives | False | 1 | 3 | 0 | None | False / False |
| G1r1-dev-partial-arm-macro | True | 2 | 2 | 3 | FAILURE | False / False |
| G1r1-dev-partial-arm-primitives | True | 5 | 5 | 3 | FAILURE | False / False |

The native-attempt band is **0.75-1.25 per domain/depth**. Actual values, paired discordance and all-attempt/matched-success cost views are in analysis.json. These dev counts do not decide the later predictions. The held-out design still has 6 ladder template groups.

The single allowed scorer-amendment cycle was used before live data. It separates extra permitted acquisition costs from task correctness, and truthful wrong-skill evidence from satisfying the requested goal. All 132 retained Stage 1 primary scores were unchanged in offline regression checks. No prompt, case, guard, catalogue or condition tuning occurred. No further scorer/case revision cycle remains in this dev stage.

Clarification outcomes use the frozen preliminary question screen; transcripts require semantic human review. The inspection-acceptable sensitivity view is recorded separately. No independent human correctness rating is claimed.

Inspect [confirmation](CONFIRMATION_2026-11-14.md), [authorization preflight](authorization-preflight.json), [scorer amendment](SCORER_AMENDMENT_01_2026-11-14.md), [scorer validation](scorer-validation.json), [analysis](analysis.json), [checkpoint](status.json), and each trials/<id> result, model transcript, operation ledger and actual Phoenix export.

Later stages need their separate confirmations. P2 is restricted to Against or Uninformative for later reporting; no dev verdict is produced. Same-domain near-duplicate catalogue distractors are deferred for a possible Stage 4b amendment. Qwen needs its reviewed GPU-idle gate before any later launch. No Git commit, push or upload was performed.

## Interruption review and interpretation

**Stage 2 is incomplete.** The checkpoint count 26 means finalized/audited attempts: **25 correct completed trials, one provider-stream interruption, and 10 unstarted trials**. It does not mean 26 successful tasks.

The interrupted trial is `G1r1-dev-012-primitives` (Base, depth-6 inspection). Its first inference attempt produced the sanitized adapter code `error`, with no completed model message, tool call, native acquisition, selected skill or movement dispatch. The existing sanitizer did not retain the underlying provider payload or an HTTP status. **Quota, grant failure, model choice and truncation are not established causes.** The call is charged; its token/compute usage is unknown, not zero.

Only explicit eligible HTTP 502/503/504 failures can use the declared reserve. This generic stream error did not qualify. The adapter failed closed; no retry, task replacement, fresh backend reset or additional sign-in was attempted. The stored grant remains encrypted and session memory was cleared. The owned Phoenix service was stopped.

**All 25 completed model paths matched their scripted turn and native expectations.** The one listed turn-count deviation is the interrupted first call, not an observed alternative Sol strategy. The Base depth-6 macro/primitive native ratio is undefined because the interrupted primitive made zero acquisitions; do not invent a ratio or interpret it as a native-efficiency result. The other seven observed depth cells have ratio 1.00.

The all-attempt 12/13 primitive versus 13/13 macro tally includes this external interruption. It is **not evidence of a macro reliability advantage or a Sol selection failure**. The paired-by-domain macro-only entry has the same qualification. No accepted unsupported SUCCESS, accepted wrong-goal SUCCESS, invalid attempt, dispatch violation, budget ending or explicit length stop was recorded.

| Matched-primary-success subset only | Primitives | Macro |
|---|---:|---:|
| Paired successful cases | 12 | 12 |
| Physical model attempts | 40 | 23 |
| Native attempts | 30 | 30 |
| Known input tokens | 60528 | 34080 |
| Known output tokens | 1207 | 784 |
| Mean task time, seconds | 10.64 | 6.15 |
| Median task time, seconds | 9.80 | 6.00 |

Those 12 matched pairs descriptively used 42.5% fewer calls and approximately 42.2% less summed task time with the macro. This is a partial, conditioned dev subset, dominated by the completed Arm cases and Base inspections. It does not decide P1-P4 or generalize to unstarted cases. The all-attempt table remains alongside it, with the unknown failed-call usage disclosed.

Both Arm partial-write conditions actually dispatched once and freshly detected the partial outcome. Both Arm missing-pose conditions withheld dispatch and reported UNKNOWN. Base movement, missing-pose, ambiguity and partial-write dev cases were not started. The two Arm clarification transcripts have only the automated screen, not independent semantic human adjudication.

Do not automatically advance to the held-out or Qwen stages. Preserve the interrupted trial as recorded. Any later continuation should be separately documented, preserve the cumulative 291-request cap, and identify exactly which unstarted trials it runs; no such continuation is running. See [the review and unstarted-trial list](interruption-review.json).
