# G1 proposed budgets and request ceilings

Date: **2026-11-13**. **Unconfirmed proposals; no launch authorized.**

The formula below applies to the intended G1 acquisition design. Some paths are
not expressible by the current module. It is a resource proposal, not evidence
those paths exist or that they will finish within360 seconds.

## Per-task formulas, identical for primitives and macro

One complete tool call per model response, including selection and final report:

- Inspection depth d: nominal minimum primitive calls3 (select, batched read,
  report); intended maximum d+2 (one-source reads). Budget **d+6** calls,
  **d+4** native operations, **2(d+6)** tool attempts.
- State anchor with p independent prerequisites: nominal minimum5 (select,
  batched prereads, write, fresh verify, report); intended maximum **p+4**.
  Budget **p+8** calls, **p+6** native operations, **2(p+8)** tool attempts.
- Ambiguous task has no execution path: proposed nominal one classification/
  clarification call+4, hence **5 calls, 4 native operations, 10 attempts**.
  Primary correctness still requires no selection/acquisition/dispatch. Budget
  slack does not authorize them. This resolves an otherwise undefined budget
  formula for ambiguous cases, subject to confirmation.
- Missing-prerequisite/fault cases inherit the relevant p3 anchor's **11 calls,
  9 native operations and22 attempts**, despite early-stop expected paths.
- All tasks:3 corrections, <=1 motion dispatch,360 seconds,2048 observed output
  tokens/task. Local generation cap1024/call, context8192, temperature0, seed42,
  thinking off; original A FA/f16 policy. Retry/timeout overhead counts against
  task elapsed time; no blind command or agent-invocation replay.

The current public inspection API actually batches all declared sources into
one call, so its nominal min=max3, not d+2. The larger intended maxima above are
conservative proposed caps, not an instruction to force unbatched calls.
Actual budgets may need revision if the study is narrowed to the current API.

## Ceiling arithmetic

Each case runs once in each condition. Sum per-case caps, then add a **separate
physical infrastructure reserve**. No repeated model outcomes are scheduled.

| Batch | Cases | Trials | Logical request ceiling | Infrastructure reserve | Total physical ceiling |
|---|---:|---:|---:|---:|---:|
| Sol dev | 32 | 64 | 608 | 6 | **614** |
| Sol held-out | 64 | 128 | 1196 | 12 | **1208** |
| Qwen held-out | 64 | 128 | 1196 | 12 | **1208** |

Dev arithmetic per condition: ladder148 + anchors80 + non-depth76 =304;
two conditions=608. Held-out per condition: ladder370 + anchors120 + non-depth108
=598; two conditions=1196. These are hard envelope proposals, not forecasts.

Reserve defaults6 and12 are newly proposed small fixed allowances, not carried
balances or user-approved values. Reuse M4 eligibility unchanged: explicit HTTP
**502/503/504 only**, excluding quota/auth/scope/token/grant/client failures;
at most one retry per logical call, one-second backoff, each physical attempt
charged, and aggregate reserve enforced. No retry for length, wrong calls,
ordinary timeouts or model/robot failures. The reserve cannot be spent rerunning
failed trials or extending ordinary model decisions. Failed HTTP compute/usage
may be censored; record it as not recorded, never zero. This proposal applies
eligible HTTP recovery consistently to both backends, not just Sol.

The maximum sum of the proposed per-trial wall envelopes is23040 seconds/dev
and46080 seconds/held-out/backend, excluding between-trial setup. These are sums
of360-second task limits, **not runtime estimates or confirmed campaign
deadlines**. Batch-wide elapsed limits still need explicit confirmation; do not
copy M4's eight-hour coordinator timeout into a potentially larger batch without
review. No Qwen runtime estimate is substituted for unmeasured deeper cases.

## Separate catalogue-size probe: unresolved factor

64 held-out cases x3 catalogue sizes =192 first-turn calls/model if one fixed
condition sentence is used. Proposed reserve3 gives **195/model**. Crossing both
original condition sentences gives384/model; reserve6 gives **390/model**.
Two backends double those figures. No tools execute. Clarification cases lack
a unique target; define their3-skill sampling policy before any launch.
Do not choose between these designs after seeing results. No numerical ceiling
for this probe is approved yet. Qwen-on-lab hardware would be a different
configuration and must be recorded, not silently mixed with laptop measurements.

## Sol allowance and authorization

The archive records M4's **106 physical requests against a local cap323**.
The arithmetic difference217 is unused room in that old harness cap. It is not
an OpenAI account quota, remaining weekly usage balance or authorization for G1.
Current provider remaining quota: **not recorded**. Stage0 performs no remote
quota check and makes no inference or token-renewal request.

Existing remembered-sign-in status: **not checked**. A generic helper can open
manual login when its store is empty; G1 must use a fail-closed restore-only path
and must never invoke that fallback. Before a future confirmed batch, review
sanitized authorization availability, correct scopes/model digest and its durable
reserve ledger before the first model request. Stop and preserve progress on
unavailable credentials or quota; do not raise any limit or start new consent.
