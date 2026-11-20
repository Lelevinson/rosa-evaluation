# G1-r1 counts, budgets, ceilings and planning estimates

Date: **2026-11-13**. All numbers are proposed for confirmation. Live requests:0.

## Exact counts

| Case family | Per domain held-out | Two-domain held-out |
|---|---:|---:|
| Four inspection depths x3 cases | 12 | 24 |
| One movement skill x3 cases | 3 | 6 |
| Missing prerequisite, ambiguous, partial/ineffective, unavailable source | 4 | 8 |
| Total | **19** | **38** |

Each case runs once in each execution condition:38x2=**76 trials/model**.
Sol+Qwen therefore means152 held-out task trials, compared with M4's80 total
and40/model: **1.9 times M4**, not38 trials/model. Dev has16 cases x2=32 Sol
trials. The first-turn probe adds responses, not executed robotic task trials.

No adjustment from the proposed16/38 counts was made. Dev has8 ladder,4 movement,
2 missing-prerequisite and2 ambiguous cases. The Stage1 control suite must also
cover the held-out fault fixtures; this tests the harness, not model performance.

## Fixed M4 limits

8 logical model decisions/task;2048 observed output tokens;10 native operations;
16 tool attempts including nested program steps;3 corrections;<=1 dispatch;
360 seconds. Read-only/ambiguous application permissions allow0 dispatches.
Keep the existing8-hour backend deadline as the proposed unchanged campaign
ceiling. Limit failures stop progress; they do not authorize extra attempts.

Qwen A:8192 context,1024 generated tokens/call,temperature0,seed42,think=false,
original unset/auto effective-enabled Flash Attention andf16 KV. Client response
cache stays off; server prefix-cache reuse follows M4. Fresh world/agent history
per task is separate from server prefix caching. Loaded runtime/digest must be
reviewed at the later inference preflight; no model was loaded in Stage0.

## Proposed request caps

| Batch | Ordinary arithmetic | Ordinary logical cap | Separate reserve | Total physical cap |
|---|---|---:|---:|---:|
| Sol dev | 16 cases x2 arms x8 | 256 | 3 | **259** |
| Sol held-out | 38 x2 x8 | 608 | 3 | **611** |
| Qwen held-out | 38 x2 x8 | 608 | 3 | **611** |
| Stage4b, each backend | 38 x3 catalogue sizes x1 response | 114 | 3 | **117** |
| Stage4b, both backends | 38 x3 x2 backends | 228 | 6 | **234** |

The proposed reserve of3/batch matches M4's fixed reserve. Reuse its explicit
HTTP502/503/504 eligibility, one retry/logical call, one-second backoff, and
quota/auth/scope/token/grant/client exclusions. Count every physical attempt and
retain failed HTTP records. A reserve attempt does not refund physical usage or
authorize a repeated task/robot command. No ordinary timeout, truncated output,
invalid tool call or task failure qualifies. Unknown provider compute/usage on a
failed response is **not recorded**, not zero.

Stage4b uses only macro wording and3/5/10 **skills**, with the same five underlying
tool types. It does not test primitive wording or a changing number of tool schemas.
For nonambiguous3-skill views, include the target and two deterministic distractors;
for ambiguity use a deterministic sample without a designated target. Freeze the
exact catalogues before inference. Domain prefixes make10-skill distractors easier
to reject and limit generalization to a real heterogeneous ROS tool catalogue.

## M4-based expected-consumption estimates

These are **planning estimates from recorded M4 averages**, not observations or
new-task guarantees. M4 Sol used3.4 calls/primitive task and1.9/macro task;
Qwen used4.55 and2.65. All40 attempts/backend are included, not just successes.

| Batch | Request estimate | Summed task-time projection | Entire-campaign projection |
|---|---:|---:|---:|
| Sol dev,32 trials | 84.8 (~85) | 418.356s (~7.0min) | 848.624s (~14.1min) |
| Sol held-out,76 trials | 201.4 (~201) | 993.595s (~16.6min) | 2015.481s (~33.6min) |
| Qwen held-out,76 trials | 273.6 (~274) | 8309.379s (~2.31h) | 9344.573s (~2.60h) |

For example: Qwen requests=38(91/20+53/20)=273.6. Task-time projection=
(76/40)x(2669.723862264+1703.633427467). Whole-campaign projection=
(76/40)x4918.196232745. These distinct clock/cost views are not added together.
Campaign projection proportionally scales setup/idle/overhead as well, so it can
misrepresent fixed costs. Mock source operations, new task mix, five-skill prompts,
depth6 requests and termination behavior differ from M4. The supplied2.5-3.5-hour
Qwen planning guess is consistent with the whole-campaign scale projection, but
it is not a completion-time promise. Actual time is not recorded yet.

Stage4b expects exactly114 first-turn responses/backend before eligible failures.
Its token/latency demand is not inferred from whole-task averages; **not recorded**.
The machine resource file also retains labelled historical token projections,
with their scale factors and limitations. No missing historical value was filled.

## Authorization and quota

The protected research authorization **file is present**, checked locally on
2026-11-13. No credential contents were read or decrypted, no refresh/provider
validation was attempted and no login started. Presence can reflect an expired
or revoked grant and is not readiness for a hosted run. See authorization-presence.json.

Current provider quota is **not recorded/not knowable from these local records**.
M4's106/323 was106 charged requests against a local323 cap; the unused217 slots
are not a transferable allowance. Stage0 does not verify that611 new requests fit
the account. Before a future approved batch use a restore-only existing-grant
path, never the generic helper's absent-credential login fallback; review the
preflight before inference. Stop/checkpoint on auth/quota failure without new consent.
