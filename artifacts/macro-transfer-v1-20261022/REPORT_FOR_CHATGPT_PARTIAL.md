# ROSA macro comparison: audited partial checkpoint

Status: INCOMPLETE. User-local date: 2026-10-23 (Asia/Taipei). The historical campaign name retains its 2026-10-22 UTC freeze date. The hosted service stopped at 00:19:53 Taipei time with subscription_sharing_usage_limit_exceeded. This was a quota stop, not a laptop shutdown or loss of the saved experiment.

Qwen completed18/18 planned trials. Sol completed14 scoreable trials, all correct; one further trial was quota-interrupted before any tool/native operation, and three were never started. All33 saved attempt records passed local/persisted-span audits and their saved primary scores were recomputed exactly. No frozen score was changed.

## Outcomes and costs

| Backend | Condition | Correct / scoreable | Scoreable calls | All attempted calls | Native | Invalid | Known input tokens | Known output tokens | Censored | Trial seconds (scoreable) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ollama | model | 4/6 | 39 | 39 | 25 | 4 | 122340 | 5088 | 0 | 724.84 |
| ollama | macro | 5/6 | 22 | 22 | 19 | 5 | 61179 | 3615 | 0 | 502.43 |
| ollama | workflow | 5/6 | 21 | 21 | 19 | 4 | 57269 | 3436 | 0 | 483.86 |
| siwc | model | 5/5 | 23 | 23 | 13 | 0 | 48067 | 747 | 0 | 98.63 |
| siwc | macro | 5/5 | 11 | 11 | 13 | 0 | 21353 | 309 | 0 | 48.88 |
| siwc | workflow | 4/4 | 8 | 9 | 11 | 0 | 15348 | 229 | 1 | 38.31 |

Each condition originally planned six trials. Sol denominators differ; do not compare its unequal condition totals as a completed paired benchmark. Token totals are known lower bounds where censored: the quota-interrupted request returned no usage and is not assumed zero-cost. All125 inference attempts count against the resource ledger (82 Qwen,43 hosted). Native operations include failed observations.

## Complete-case paired comparison

```json
{
  "ollama": {
    "complete_three_condition_cases": [
      "positive_wrist",
      "constrained_pose",
      "already_home",
      "ineffective_motion",
      "missing_prerequisite",
      "transient_after_motion"
    ],
    "cells": {
      "model": {
        "correct": 4,
        "calls": 39,
        "native": 25
      },
      "macro": {
        "correct": 5,
        "calls": 22,
        "native": 19
      },
      "workflow": {
        "correct": 5,
        "calls": 21,
        "native": 19
      }
    }
  },
  "siwc": {
    "complete_three_condition_cases": [
      "positive_wrist",
      "constrained_pose",
      "already_home",
      "ineffective_motion"
    ],
    "cells": {
      "model": {
        "correct": 4,
        "calls": 19,
        "native": 11
      },
      "macro": {
        "correct": 4,
        "calls": 8,
        "native": 11
      },
      "workflow": {
        "correct": 4,
        "calls": 8,
        "native": 11
      }
    }
  }
}
```

For Sol, only the first four cases form complete three-condition pairs. All four passed in every condition:19 primitive-tool calls versus8 macro and8 workflow calls. The missing-prerequisite case has model/macro outcomes but no scoreable workflow outcome. No Sol transient-after-motion trial started. There is no full Sol retention result.

## Per-case status

| Backend | Case | Primitive tools | Macro | Workflow |
| --- | --- | --- | --- | --- |
| ollama | positive_wrist | PASS / 7 calls | PASS / 3 calls | PASS / 3 calls |
| ollama | constrained_pose | PASS / 7 calls | PASS / 3 calls | PASS / 3 calls |
| ollama | already_home | FAIL / 1 calls | FAIL / 1 calls | FAIL / 1 calls |
| ollama | ineffective_motion | PASS / 8 calls | PASS / 7 calls | PASS / 6 calls |
| ollama | missing_prerequisite | FAIL / 8 calls | PASS / 4 calls | PASS / 4 calls |
| ollama | transient_after_motion | PASS / 8 calls | PASS / 4 calls | PASS / 4 calls |
| siwc | positive_wrist | PASS / 5 calls | PASS / 2 calls | PASS / 2 calls |
| siwc | constrained_pose | PASS / 5 calls | PASS / 2 calls | PASS / 2 calls |
| siwc | already_home | PASS / 4 calls | PASS / 2 calls | PASS / 2 calls |
| siwc | ineffective_motion | PASS / 5 calls | PASS / 2 calls | PASS / 2 calls |
| siwc | missing_prerequisite | PASS / 4 calls | PASS / 3 calls | QUOTA INTERRUPTED |
| siwc | transient_after_motion | NOT STARTED | NOT STARTED | NOT STARTED |

## Interpretation and decision

The simple macro and workflow have the same acquisition policy. Qwen had the same 5/6 correctness in each; macro used22 calls versus21 for workflow, with19 native operations each. The strict predeclared Qwen macro screen therefore fails its no-additional-calls requirement (21 versus20 calls on five matched-correct pairs). Do not rename that screen as a pass. A one-call difference in this tiny study is not proof of an algorithmic workflow advantage. Sol showed observed parity on four complete pairs, but its full screen remains incomplete.

Both bundles are promising relative to primitive tools in the recorded Qwen cases, particularly avoiding the persistent-observation loop. They did not fix Qwen ending the already-home task without using tools. No architectural novelty, general reliability, statistical equivalence or physical-robot readiness is established.

A shared prompt/tool inconsistency was discovered: default system prompts mandate unavailable discovery tools before action while the bounded contract mandates selection first. It is a real interface defect, but its causal effect is untested. Passing trace/schema/resource audits does not mean that the instruction contract was consistent. Preserve this experiment and resolve the mismatch prospectively before a larger study; do not silently tune or rerun frozen cases.

## Safety, cleanup and audit scope

All33 saved attempts matched actual persisted Phoenix span IDs and closed trees. All saved primary scores were reproduced from raw evidence. No accepted unsupported selected-goal SUCCESS or dispatch violation appeared. Fault coverage is recorded separately; the quota attempt had no fault exercise. Both simulators exited with returncode0, both supervisors released sleep holds, Qwen was unloaded, and the hosted session was revoked. No credential persistence or consent bypass was introduced.

Pre-live validation:40 test methods,18 scripted ROSA/Phoenix trials and six initial deterministic UR5e controls passed. Six deterministic controls also passed before each live backend. The initial Phoenix-unavailable attempt is retained. All189 frozen sources, including both dependency lockfiles, are verified and included.

Per trial:8 requests,180 seconds,16 tool attempts,10 native operations,one trajectory, three corrections. Per backend:144 inference attempts and4500 active batch seconds. Qwen retained the frozen Q4_K_M model digest, Ollama0.40.6, ctx8192, temp0,seed42, reasoning off, per-call allowance1024 reduced against2048 cumulative generated tokens. Sol retained the OAuth adapter and observed2048 stopping threshold; an equivalent hard generation cap is not available. Cross-model hard-token-budget equality is not claimed. Latencies exclude startup/reset/control/audit/serialization overhead.

Session receipt:

```json
{
  "auth": {
    "validated_sign_in": "PASS",
    "token_refreshes": 0,
    "session_cleanup": "REVOKED"
  },
  "request_cap": 144
}
```

The session supports authorized memory renewal, but token_refreshes0 means this batch did not exercise actual renewal. The observed error was quota exhaustion, which refresh-token renewal cannot legitimately bypass.

## Remaining work

Four hosted cells remain: repeat the quota-interrupted missing-prerequisite workflow cell as a new attempt, then the three transient-after-motion conditions. They require quota availability and fresh manual consent because cleanup revoked the session. Use a separate continuation protocol/output folder and preserve the original quota record. A continuation capped at32 requests keeps combined hosted attempts at most75, below the original144 ceiling. No continuation has been launched and no reset time is assumed. Do not rerun completed Qwen or hosted cells.

Next research priority after this interrupted campaign is accounted for: uniformly repair the composed prompt/tool contract, validate separately, and compare the smallest bundled skill with primitive tools using fresh repeated cases. Keep JTVR, memory, general planning and physical deployment out of this experiment.

## Detailed review notes

# Interpretation notes: exploratory review, not protocol amendments

These notes supplement the frozen protocol and raw evidence. They do not change
scores, treatments, stopping rules or cases, and no live trial is replaced.

## Qwen's already-home failures

The workflow, primitive-tool and macro trials each returned a clarification
request without selecting a skill, acquiring an observation or submitting a
validated report. All finished with `stop`, not output truncation, at158/168/158
generated tokens respectively. The first recorded LLM span contains the actual
explicit home goal in the user message; it was not omitted by the runner.

The independent observer found the arm at home, because the evaluator reset it
there. This is distinct from completing the required observation/reporting
task. All three primary outcomes correctly remain failures. A false
`truthful_report` flag in these rows means **no accepted truthful report**, not
that the model submitted a dishonest report. These answers did not claim task
success. Lower call counts from such early exits are not efficiency gains.

The bundle is invoked only after model selection. It cannot assist a model
that ends the conversation without invoking it. This finding concerns these
tested prompts and serving settings; it is not proof that Qwen cannot handle
already-satisfied goals. ROSA's shared system prompt includes generic robot
instructions in addition to the bounded task contract. Possible prompt
interaction is a future hypothesis, not an established cause or a license to
tune this campaign.

## Corrections and fault coverage

In Qwen's workflow ineffective-motion trial, the model attempted read_state
twice before selection. Both were rejected under the shared select-first
contract, used the correction budget and performed no native read. The model
then selected the authorized skill, the bundle attempted the exact command
once, the injected no-effect fault was exercised, and a supported FAILURE
report was accepted. Six model calls and two invalid attempts are retained.
This is completion after shared feedback, not error-free model performance.

The primary scoring of this campaign requires the correct command to be
attempted for the ineffective-motion case. A truthful FAILURE without that
attempt does not pass. Earlier campaign scores remain unchanged.

Qwen's primitive-tool missing-prerequisite trial selected the correct skill,
then alternated seven read_state/verify_outcome observations until all eight
model calls were exhausted. It dispatched no movement but never submitted an
UNKNOWN report. All eight generations ended with stop, not length, and usage
was complete. This is failure to stop observation acquisition and report within
the fixed budget, not insufficient output allowance or unsafe execution.

The paired macro accepted UNKNOWN in four model calls, but also made three
missing observations (one bundled read and two model-requested reads). The
prompt's 'one additional read' guidance is not a separately enforced per-fault
retry ceiling or a scored primary condition. Global model/native/tool/write
ceilings are enforced. Report excess observation acquisition as a diagnostic;
do not describe primary correctness as proof of compliance with every prose
instruction. `invalid_attempts` counts validator/schema errors, not every
behavioral deviation. No retrospective primary-score change is made.

## Shared prompt-contract audit exception

Inspection of the frozen `rosa-research/src/rosa/prompts.py` (especially the
action-request workflow near line94) confirms instructions requiring
rosnode_list and rostopic_list before action. These tools are not available in
this bounded experiment. The prompt also recommends retries and calculation
tools absent from this catalog. `ROSA._get_prompts` in `rosa.py` near line303
prepends all default system prompts before the supplied robot-specific prompt;
load_default_tools=False does not remove those defaults. The user task then
requires select_skill before any other tool. The recorded LLM inputs contain
both the default instructions and the task contract.

This is a real shared interface inconsistency, not a proven causal explanation
for any particular Qwen failure. All three conditions and both backends receive
it, so the comparison remains descriptive for that shared configuration.
However, passing schema/trace/resource tests does not establish a fully
consistent instruction contract. Do not present this campaign as clean
validation that all interface problems were resolved or as an isolated measure
of intrinsic model capability. The generic instructions are not edited during
this frozen run. Resolve this model-independent prompt/tool mismatch and
validate it prospectively before a larger study; retain these results.

## What is being compared

The primitive-tool reference is controlled ROSA with the same reporting repair,
permissions, limits and feedback as the bundled conditions. It is not a rerun
of Baseline v1 or unrestricted stock ROSA. All conditions inherit the same
select-first guard, including any interaction with the default system prompt.

The macro and workflow use the same acquisition policy and identical model
prompts/tool schemas. Their common validator/guards are shared; the macro
replaces the execution method, not the complete safety implementation. These
data cannot establish a new scheduling/tool-selection algorithm, nor a large
code-complexity reduction. Different observation-reference IDs and live model
execution mean identical policies need not produce identical token streams.

The deterministic controller receives a resolved task target. It establishes
skill/controller/verifier feasibility, not natural-language goal understanding.
Four authorized poses are variants of one movement primitive, not four
heterogeneous robot capabilities. User constraints concern final poses; no
collision avoidance or path-constraint claim is supported.

`unsupported_success_attempts` counts structured submit_report attempts checked
against private observation/goal truth. It is not a general natural-language
claim classifier. Free-text answers without an accepted report fail the primary
task contract and remain available in raw evidence for review.

The earlier scorer's truthfulness diagnostic assumes persistent missing data
only in the designated missing-prerequisite case. A model accepting an UNKNOWN
report immediately after the transient read failure could be truthful about
its available observation while still failing this campaign's required
recover-and-verify objective. If such a row occurs, inspect its raw observation
and report rather than reading that diagnostic as proof of dishonesty. Do not
retroactively change the frozen primary score.


## Evidence

The frozen analyzer analysis.json/REPORT_FOR_CHATGPT.md remains unchanged and includes the raw failed quota row. Use PARTIAL_AUDIT.json and this partial report for the explicit infrastructure/scoreable distinction. Complete campaign finalization correctly refused to publish a complete ZIP. This separate archive is explicitly partial.

Archive: `ROSA_MACRO_TRANSFER_V1_PARTIAL_EVIDENCE_2026-10-23.zip`. All raw attempts, controls, checkpoints, source snapshots, actual Phoenix spans, cleanup receipts and partial classification are included.
