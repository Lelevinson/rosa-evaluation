# Qwen output/interaction diagnostic v1 — prospective protocol

This is an authorized, separate exploratory engineering study. Preserve the prior
96-trial collection and every original score/source snapshot. No larger model,
OAuth renewal, JTVR, memory, controller changes, sensor rounding, automatic report
repair or verification-contract revision is part of this experiment.

## Questions and five configurations

Use the same Qwen3.5:9b Q4_K_M digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90.
Context8192, temperature0, seed42, reasoningFalse, mmapTrue. The user's correction
specifies 1024, not 2024 tokens.

|Condition|Maximum generated tokens/call|Instructions|Length recovery|
|---|---:|---|---|
|L256|256|Original|Off: preserve reference end handling|
|L512|512|Original|Off|
|L1024|1024|Original|Off|
|C256|256|Original plus concise/tool-first style only|Off|
|R256|256|Original|On: at most2 fresh-next-step requests/trial|

All conditions use repaired reference A: identical unstructured error facts,
no automatic post-write verification, identical four schemas and EvidenceSession
gates. The same opt-in inference gateway meters every condition. Existing global
model factory and ROSA implementation remain unchanged. No hosted trials planned;
earlier Sol results are contextual, not a fresh matched comparison.

## Cases, ordering, budgets

Same four UR5e cases, targets and fault injections as ur5e-transfer-v1: healthy
coordinated movement; suppressed command; partial trajectory; missing agent sensor.
Two repetitions of every condition/case:40 trials, eight/condition, only two healthy
movements/condition. This is a diagnostic, not a powered generalization claim.
Seed20261022 selects reproducible case/condition ordering; each case/repetition is
a block containing all five conditions. Rotate order and reverse the second pass.
Archive schedule.json and hashes before any live inference. Full-precision live
sensor values and timestamps remain visible, so generation can differ despite seed.

Every trial: at most8 model requests,2048 total generated tokens,180 seconds,
16 tool attempts,10 native operations,3 invalid corrections,one dispatched write.
All recovery requests count toward these same limits. Dynamically request at most
min(condition allowance, remaining total output allowance); do not allow a larger
condition an automatic8192-token trial budget. Input token counts are measured,
not capped as if different tokenizers/representations represented equal work.
Batch at most320 requests,81920 generated tokens,3 hours before next trial.
180-second per-trial alarm also bounds native/provider waiting. Outside-trial
startup120s and home reset use deterministic controls and are archived separately.
No selective reruns/tuning; unexpected engineering or trace failures stop the batch.
Incomplete interrupted trial remains unknown and must be reported.
If inference is interrupted before usage metadata returns, preserve its partial
evidence and stop the batch: do not invent usage or continue under an unmeasurable
remaining token budget. This is an engineering stop, not a selective trial rerun.

## Safe recovery

Inspect provider done_reason/finish_reason before the existing ROSA tool parser.
On length termination, withhold ALL tool calls from that response, even parseable
ones; never execute partial arguments or concatenate argument fragments. Retain
prose as explicitly incomplete context and send a fixed feedback message requesting
a fresh complete next step. Previously executed tool results remain in the original
prompt. Do not automatically replay previously accepted/uncertain commands.
The one-write guard, read prerequisites and fresh-evidence report gate remain in
force. If recovery/call/token/time limits are exhausted, terminate incomplete.
Recovery does not turn prose into a report or credit an unverified goal.
Do not retry a provider/network failure as a command replay.

## Validation and scoring

Before freeze/live inference: offline actual-ROSA tests exercise discarded tool
calls, post-write truncation without replay, closed spans, request/token/time and
continuation bounds, unchanged disabled behavior and balanced schedule. Repeat
all four deterministic Gazebo controls with independent state observations.

Independent observer and per-report call-time oracle use the existing scoring.
Correct combined outcomes distinguish achieved healthy moves, known injected
failures and UNKNOWN sensor cases. Count raw invalid/unsupported attempts even
after guard-assisted recovery; never label blocked unsafe attempts error-free.
Every trial archives raw model messages/metadata, requested token allowance,
usage, length stops, discarded calls, recovery events, transport ledger, reset,
independent observations and full local/Phoenix traces. Persist after every trial.
Independent Phoenix readback must exactly match span IDs and closed trees.

Primary comparisons: paired correct outcomes L512/L1024 versus L256 (serving),
C256 versus L256 (style), R256 versus L256 (combined framework assistance).
Report per-case/repetition pairs and healthy completion separately. Report actual
tokens/calls/latency, truncations, accepted writes/reports, invalid calls and raw
unsupported success attempts. Quantify visible prose characters separately from
structured tool argument characters; character counts are descriptive, not token
attribution. Report output/input token usage including all recovery calls.
Do not interpret a lower total from early failure as higher efficiency.

No formal significance or universal-model claim. A useful candidate requires both
healthy repetitions correct, no deterioration of paired fault outcomes or increase
in unsupported claims relative to the fresh reference; cost must be reported.
Two repetitions do not prove superiority. No post-hoc mechanism combination.
If larger output succeeds, credit serving resources; if concise succeeds, credit
prompting; if recovery succeeds, credit the combined framework, not the LLM alone.
