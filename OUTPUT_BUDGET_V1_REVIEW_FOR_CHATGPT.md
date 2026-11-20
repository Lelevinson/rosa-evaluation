# Qwen output-budget and completion study: review and interpretation

Date: 2026-10-22. This review supplements the sealed raw evidence report. It does
not change any frozen score, protocol, source snapshot or historical study.

## What finished

There are **40 scored Gazebo UR5e trials plus one externally interrupted,
unscorable attempt**. The scored trials made188 model calls. No hosted/OAuth
requests were made. All40 scored-trial Phoenix span-ID sets match the local
exports and have closed trees. Eight offline test cases passed, and four fresh
deterministic controls passed after the external shutdown (in addition to the
four controls before the initial session).

The independent verifier checked395 archived files, source request options,
identical tool schemas, original scores/checkpoints and prior archive hashes.
The model was unloaded, temporary sleep hold released, and no model-runner or
Gazebo simulation process remained in the final process check.

## Design

Same Qwen3.5:9b Q4_K_M model digest, Ollama0.40.6, context8192, seed42,
temperature0, thinking disabled and mmap enabled. Use repaired reference A:
plain actionable feedback, no automatic post-write check, the same four tools,
strict evidence/report gates and independent observer. This is not untouched
upstream ROSA and not a new comparison with Sol.

Each of five configurations runs the same four cases twice: healthy coordinated
movement, suppressed command, partial trajectory, missing agent observations.
Every trial shares8 model calls,2048 total generated tokens,180seconds,
16 tool attempts,10 native operations,3 invalid corrections and at most1
dispatched write. Per-call allowance is clamped to the remaining total budget.
Ordering was frozen in case/repetition blocks before live inference; rotate and
reverse condition order. Two repetitions do not fully balance all five positions.

|Condition|Per-call output allowance|Change|
|---|---:|---|
|L256|256|Fresh reference|
|L512|512|Output allowance only|
|L1024|1024|Output allowance only|
|C256|256|Add concise/tool-first instructions|
|R256|256|Enable bounded pre-parser length recovery|

R256 inspects the provider's length finish reason before the tool parser. It
withholds all calls in that incomplete response and requests a fresh complete
next step, at most twice, within the original budgets. It never stitches argument
fragments or automatically replays a robot command. The normal ROSA and model
factory defaults were not changed. This opt-in prototype was tested in synchronous
local inference; other providers/streaming require separate validation.

## Frozen primary results

The primary metric requires correct independently observed outcomes, a truthful
accepted report **and normal agent finalization within the execution limits**.
Fault-case passes include correct FAILURE/UNKNOWN handling, not successful motion.

|Configuration|Correct /8|Healthy task /2|Fault handling /6|Model calls|Recorded output-token interval|Aggregate trial seconds|
|---|---:|---:|---:|---:|---:|---:|
|L256|2|0|2|24|3466 exactly|474.6|
|L512|3|0|3|42|7589–8101|1095.7|
|L1024|5|1|4|48|8425–10473|1255.0|
|C256|1|0|1|25|3520 exactly|497.9|
|R256|2|0|2|49|7791–8303|1083.8|

The intervals cover **scored trials only**. Five scored trials hit the wall
deadline before their last generation returned usage. Known outputs are lower
bounds; the requested remaining allowance supplies a conservative upper bound.
Their missing finish reasons are unknown. Additionally reserve up to8 calls and
2048 output tokens for the externally interrupted unscorable attempt. The resource
reservation stayed within the original320-call/81920-output/3-active-hour ceilings.
External downtime is not active experiment time.

The primary prospective candidate screen required both healthy repetitions correct,
no paired fault deterioration and no increased unsupported structured success.
**No configuration met that screen.** That does not erase the exploratory benefit
of the larger output allowance. L1024 gained four paired correct outcomes versus
L256 and lost one; net+3/8. With two repetitions, known cases, live numeric/timestamp
variation, restart and order effects, this is not a statistically established or
generalizable improvement.

## What the output limit actually affected

The first L512 healthy trial reached the physical goal and obtained fresh state,
but hit512 generated tokens while composing its final report. Raising the ceiling
can move the cutoff to a later workflow step rather than remove it entirely.

L1024 completed one healthy trial with a truthful accepted SUCCESS report and
normal final response: **6 calls,1173 generated tokens,164.17seconds**. It corrected
one rejected request for failing to include all six required joints. This credits
the combined model/feedback/controller system, not an error-free model trajectory.
Its other healthy trial reached the goal but timed out before an accepted report.

The 256-token configuration therefore constrained useful behavior. Qwen has now
demonstrated that it can finish this complete arm workflow under the larger
allowance. The data do not justify calling Qwen incapable of arm control. They also
do not establish reliable or efficient local operation: the successful example took
nearly the entire180second budget, and task targets were explicitly supplied joint
dictionaries that a deterministic controller can already execute.

Compared with the fresh L256 reference over the same eight scored cases, L1024
made twice as many calls and generated at least2.43times as many output tokens.
Its aggregate wall time was about2.64times larger. Those timing totals mix fast
early failures with longer successful workflows; they are descriptive costs,
not a matched-success latency comparison or a causal speed measurement.

## Prose and recovery findings

The concise instruction was present in the actual raw prompts. Qwen continued to
narrate full-precision joint states and hit length limits. C256 had7541 visible
prose characters versus7974 for L256, with6 recorded length stops in both and a
lower primary correctness count. This particular prompt did not establish benefit.
Character counts are not exact token attribution.

R256 issued12 bounded recovery requests and had16 recorded length stops. Its two
primary passes were missing-sensor cases with **zero recovery activations**.
None of its six recovery-activated trials passed the strict end-to-end metric.
R256 made49 calls versus24 for L256 and generated at least7791 output tokens
versus3466. A primary reliability/efficiency improvement was not demonstrated.

No live length-stopped response contained a returned tool call, so the live
discarded-call count is0. Withholding parseable proposed calls and avoiding replay
after a prior write were exercised by the offline actual-ROSA tests. Do not claim
that a live partial-tool-call hazard was observed and prevented in these40 cases.

## Important post-run contract finding: two terminal reports were already accepted

This is a **retrospective descriptive check**, not rescoring or another experiment.

|Trial|Frozen result|What had already completed|What failed afterward|
|---|---|---|---|
|028, missing sensor, L512|Fail|Truthful UNKNOWN report accepted|Agent hit8 iterations before a final natural-language acknowledgement|
|039, healthy movement, R256|Fail|Goal independently reached; truthful SUCCESS report accepted|An additional natural-language response hit180seconds|

Both frozen scores remain failures. A separately reported, retrospective
"goal/fault outcome plus accepted truthful terminal report" check, ignoring
normal finalization, would count L5124/8 and R2563/8; the other configurations stay
unchanged. These are secondary counts under a different criterion, **not corrected
primary results**. This distinction is directly visible in the raw score/report
fields and post-run receipt.

Consequently, do not claim that R256 never achieved an accepted healthy report,
or that the second L512 missing-sensor failure proves it could not classify UNKNOWN.
Those particular failures occurred after accepted terminal reports. Other
uncertainty-handling failures and blocked unsafe attempts remain in the data.

A useful next engineering hypothesis is to end execution immediately after a
validated terminal report, without spending another LLM call on an acknowledgement.
Rejected/invalid reports must remain recoverable; simply making every report tool
return terminally could break that behavior. Any deterministic finalization must
be explicitly attributed to the framework and tested prospectively on both backends,
including invalid reports, limits, traces and uncertain command outcomes.

## Reliability and safety attribution

There were30 validation/prerequisite rejections across scored trials:

- 21 attempted writes with unavailable state, blocked before native dispatch.
- 8 requests missing the required full set of six joints, rejected before dispatch.
- 1 outcome-classification mismatch.

Unsupported structured submit_report SUCCESS attempts counted0. This counter does
not semantically grade every sentence of free-form prose. Guard-blocked attempts
remain model errors even if the final task passes. The simulator is not hardware
or a safety certification; the independent observer is another read-only ROS node
using the trusted simulator's joint-state source, not separate physical sensing.

## Interruptions and integrity

The original first R256 trial reached the goal but timed out; its strict accounting
audit failed because the last generation had no returned usage. Its original
failure and metadata exception are preserved. The separately frozen accounting
follow-up saved34 more results, then its supervisor ended and WSL was found stopped
during entry035. The shutdown cause/time is unknown. All35 saved span sets survived;
15 partial spans from the unscorable attempt were recovered without inventing a root.

A separately frozen recovery session repeated deterministic controls and the eight
offline tests, verified unchanged Python package versions, and ran only the five
unfinished entries. Entry035 is explicitly a replacement for the interrupted
attempt; four had not started. No completed trial or score was rerun/rewritten.
L512 therefore has9 attempts,8 scored and1 unknown. The complete-case rates do not
restore that missing outcome. Cold loading and the session restart limit causal
interpretation, especially of latency.

The original metadata exception is distinct from missing trace spans: all40 scored
local span sets match Phoenix. The interrupted partial trace is archived separately
and is not represented as complete. Baseline v1, Stage4, reliability v1 and the
prior96-trial evidence archives remain unchanged.

## Recommended next steps

1. Keep Qwen3.5:9b; do not infer a larger model is necessary from the old256 profile.
   Treat1024 as the most promising diagnostic allowance tested, with measured cost,
   rather than a proven production default or framework research contribution.
2. Prospectively define task outcome and agent finalization as separate metrics;
   test accepted-report terminal completion under the same resource envelope.
3. Investigate compact, consistent model-facing observations/provenance while
   retaining raw readings and independent validation. Keep this separate from
   prompt-only changes and avoid tuning on these known cases then claiming holdout gain.
4. Retain safe length detection as an opt-in engineering mechanism. Do not claim
   bounded retry improves reliability from this primary result; its overhead and
   the accepted-report/finalization distinction both matter.
5. If capability remains the question, a separately frozen common-deadline study
   can isolate180seconds from a longer allowance; this study does not measure
   unconstrained maximum capability. Additional compute is a serving resource,
   not evidence of a new framework algorithm. No new experiments were launched.

Keep JTVR and episodic memory paused. The next practical issue is reliable,
economical task termination and observation handling, not architectural expansion.

## Evidence locations

- Sealed report: `artifacts/output-budget-v1-resume-20261022/REPORT_FOR_CHATGPT.md`.
- Independent review: `artifacts/output-budget-v1-resume-20261022/independent-review.json`.
- Interruption and reservations: resume package `INTERRUPTION.json` and `budget-reservation.json`.
- Final verification: workspace `reports/OUTPUT_BUDGET_V1_FINAL_VERIFICATION.json`.
- Retrospective terminal check: workspace `reports/OUTPUT_BUDGET_V1_TERMINAL_REPORT_REVIEW.json`.
- Raw evidence ZIP: `artifacts/ROSA_OUTPUT_BUDGET_V1_COMPLETE_EVIDENCE_2026-10-22.zip`.

Raw ZIP:4782967bytes;395 manifest members; SHA256:
`ae202ca1f6aa0bf43fdeea189c6f489b0b1cb0b632ce160e905303b3accea19a`.
This review is an explicit post-run addendum outside that sealed ZIP, so its
interpretations and retrospective check cannot be mistaken for the frozen protocol.
