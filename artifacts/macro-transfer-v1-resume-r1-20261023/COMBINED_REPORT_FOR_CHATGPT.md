# ROSA macro comparison: combined original and four-cell continuation

**Measurement matrix: COMPLETE (36 cells).** The original quota interruption is retained separately. This report joins the original scoreable outcomes with only authorized remaining cells; no completed pass or failure was replaced.

| Backend | Condition | Correct / scoreable | Scoreable calls | All attempts | Known input tokens | Known output tokens | Native | Invalid | Seconds (scoreable) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ollama | model | 4/6 | 39 | 39 | 122340 | 5088 | 25 | 4 | 724.84 |
| ollama | macro | 5/6 | 22 | 22 | 61179 | 3615 | 19 | 5 | 502.43 |
| ollama | workflow | 5/6 | 21 | 21 | 57269 | 3436 | 19 | 4 | 483.86 |
| siwc | model | 6/6 | 29 | 29 | 61315 | 946 | 17 | 0 | 122.38 |
| siwc | macro | 6/6 | 14 | 14 | 27449 | 381 | 17 | 0 | 61.68 |
| siwc | workflow | 6/6 | 14 | 15 | 27439 | 379 | 17 | 0 | 59.31 |

Known tokens exclude unknown usage from service-interrupted generations. Those requests count in all-attempt costs and are never assumed zero-cost. No outcome was imputed.

## Per-case matrix

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
| siwc | missing_prerequisite | PASS / 4 calls | PASS / 3 calls | PASS / 3 calls |
| siwc | transient_after_motion | PASS / 6 calls | PASS / 3 calls | PASS / 3 calls |

## Continuation provenance and limits

The continuation was frozen separately before inference on2026-10-23 Asia/Taipei. It reused the exact original runner, agent, model slug, prompts, schemas, budgets, controllers, faults and independent scorer. Only the remaining schedule, output path and freeze checks were supplied by a temporary coordinator. Six resume tests passed; six fresh deterministic controls preceded the continuation. Original preflight had40 tests,18 scripted ROSA/Phoenix cases and six initial deterministic controls, plus six controls before each original backend. Control/reset/startup/audit costs remain separate from in-trial seconds. Four pose variants remain one movement primitive.

Requests and session receipt:

```json
{
  "prior_hosted_calls": 43,
  "additional_hosted_calls": 15,
  "combined_hosted_calls": 58,
  "additional_cap": 32,
  "original_cap": 144,
  "original_freeze_sha256": "3d0bfa5ad24a7b195f7c0c74d043bd3e61cfa9326705edbb71101fc3838b4b88"
}
```

```json
{
  "auth": {
    "validated_sign_in": "PASS",
    "token_refreshes": 0,
    "session_cleanup": "REVOKED"
  },
  "request_cap": 32
}
```

Per trial limits remain8 requests,180 seconds,16 tool attempts,10 native operations,one write and3 corrections. Quota-interrupted attempts are retained. The continuation has a hard32-request adapter cap and preserves the original144 combined hosted ceiling and4500 active seconds. Tokens stay in memory, consent is manual and cleanup revokes the session. Refresh support does not bypass quota; token_refreshes indicates whether actual renewal occurred. The hosted2048-token limit is an observed stopping threshold, not a requested hard generation cap. Qwen was not rerun; its frozen1024-per-call/2048 cumulative allowance,8192 context,Q4_K_M digest,temp0,seed42 and reasoning-off settings remain in the original freeze. Hidden hosted server version identity is not guaranteed by the unchanged model slug. No cross-backend hard-token equality is claimed.

## Predeclared macro screen

```json
[
  {
    "backend": "ollama",
    "status": "EVALUATED",
    "paired_primary_losses": [],
    "matched_correct_pairs": 5,
    "macro_calls": 21,
    "workflow_calls": 20,
    "macro_native": 19,
    "workflow_native": 19,
    "numerical_screen_pass": false,
    "larger_study_readiness": "BLOCKED_BY_SHARED_PROMPT_CONTRACT_EXCEPTION"
  },
  {
    "backend": "siwc",
    "status": "EVALUATED",
    "paired_primary_losses": [],
    "matched_correct_pairs": 6,
    "macro_calls": 14,
    "workflow_calls": 14,
    "macro_native": 17,
    "workflow_native": 17,
    "numerical_screen_pass": true,
    "larger_study_readiness": "BLOCKED_BY_SHARED_PROMPT_CONTRACT_EXCEPTION"
  }
]
```

These are the original numerical screen rules, not significance or equivalence tests. A failed screen remains a failure even if only one model call differs. Macro and workflow have the same acquisition policy; small live differences do not establish an algorithmic workflow advantage. The full system includes shared feedback, guards and report validation.

## Audit exception and conclusions

The shared default ROSA system prompts require unavailable discovery tools before action while the task requires selection first. This real instruction-contract inconsistency was intentionally preserved in the continuation for treatment comparability. Its causal contribution to failures is untested. Passing schema,trace and resource audits does not make the instruction contract consistent. Do not call this a clean validation of all interface fixes or a measurement of intrinsic model intelligence.

Treat the simplest bounded macro as the main candidate to investigate, subject to the actual per-backend retention result above. There is no demonstrated new tool-selection algorithm in the state-tracked workflow. Preserve negative outcomes and resolve the shared prompt/tool mismatch prospectively. Validate that separate repair before using fresh repeated and independently designed tasks for a larger comparison. Do not add JTVR,memory,general planning or physical deployment to explain this pilot.

One run per cell in a single pose family cannot establish statistical equivalence or general reliability. Both model decisions and program assistance are credited to the combined system. Fault exercise, reporting honesty and verified task completion remain distinct. No accepted unsupported selected-goal SUCCESS or dispatch violation appeared in these saved attempts; structured-claim metrics do not classify all free prose.

## Detailed preserved interpretation notes

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


## Missing cells

```json
[]
```

Every saved primary score was recomputed from raw evidence; actual Phoenix span IDs and closed trees matched every saved attempt. All original and continuation frozen source copies are included in the archive and verified against its bytes. The original partial archive and old checkpoints remain unchanged. Original STOPPED statuses describe the historical batch; this combined report is the authoritative joined-matrix status.
