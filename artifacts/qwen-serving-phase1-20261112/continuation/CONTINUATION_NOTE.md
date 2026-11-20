# Phase 1 bounded continuation after an audit false negative

Date: **2026-11-13**. This note is written before any measured B request.

The first segment completed all 15 A requests and B's discarded warm-up. The
controller then stopped because its audit required the literal line "Flash
Attention enabled". Actual B log shows `llama_context: flash_attn = enabled`,
`--flash-attn on`, and K/V q8_0. The runtime was correctly configured; the audit
predicate had a false negative. This is retained as an infrastructure exception,
not a Qwen failure or a completed negative B comparison.

Original frozen source, freeze, status, reports and server logs remain intact in
the first-segment preservation record. The continuation uses copied coordinator/
worker source, with its own freeze and explicit diff. The corrected predicate
requires the main LLM context to be enabled, or auto plus its resolved enabled
line. A vision-only warm-up line or environment flag is not sufficient. Tests use
actual auto-enabled, explicitly enabled and disabled logs, including the negative
Phase 0 case. This changes no model input, scoring or speed/agreement threshold.

A is not rerun. No measured case is replayed. Restarting the stopped B server
requires one new discarded B warm-up to restore the matched warmed/cache state.
The earlier valid warm-up is retained and excluded from metrics, not overwritten.
Then only B's 14 previously unstarted measured/repeat requests run.

Resource accounting is explicit: the first segment charged 16 requests; this
continuation can charge at most 15 more. Completed A/B would therefore total
**31 requests including three warm-ups**, an infrastructure deviation from the
original 30-request A/B schedule. This consumes one slot of the already authorized
**45-request / 46080-output-token overall ceiling**, which is not increased. Each
call still has a 1024-token maximum and no inference retry. The generation is a
declared infrastructure warm-up, not retrying an unsuccessful measured outcome.

If B passes, C needs 15 requests but only 14 slots would remain; do not run an
incomplete C block or enlarge the ceiling. Record C deferred for insufficient
remaining budget. If B fails its gates, do not run C. No D, Gazebo, Sol or tools.

The original 9000-second campaign envelope includes the interruption and repair;
do not reset it. Same idle gate, profile configuration, cache policy, input order,
timeouts and acceptance gates. Preserve the interruption as an order/thermal
limitation and report both segment counts. The first warm-up's live ps/VRAM was
not captured before the audit stop; the recovery captures fresh B hardware.

Continuation decisions are fixed before collecting measured B outputs. The A/B
study remains an exploratory serving screen; it does not establish robotic
correctness or generalized speed improvement. Source/runtime exceptions must
appear in the final report and living tracker.
