# External-interruption recovery: five unfinished entries

The follow-up supervisor ended and WSL was found stopped after35 results had been
saved (original1 plus34 follow-up trials). Its checkpoint stayed RUNNING, last
updated2026-10-22T03:49:39.893627+00:00, in entry035, repetition1 healthy L512.
The per-trial folder has no final result/evidence/local trace. This is an externally
interrupted, unscorable attempt, NOT a model failure, a success or a completed trial.
The exact shutdown cause/time is unknown. Never alter that original checkpoint.

Preserve the partial attempt and recover any persisted spans without inventing its
unfinished root. Read back all35 saved trace sets before resuming. Restart existing
services; repeat four deterministic controls after the simulator restart. Run the
same eight offline recovery/accounting tests. Freeze a new source/schedule package.

Run ONLY original schedule entries35..39: healthy L512, L256, C256, L1024, R256.
Entry035 is an explicitly labeled replacement attempt, starting from an independently
verified home reset; it does not continue uncertain physical state or replay an
old command. Never rerun the35 completed trials or select based on their scores.
The other four entries had not started. Report41 attempts:40 scored completions
and one external interruption with UNKNOWN outcome. Report the missing attempt
separately rather than silently dropping it or assigning an invented score.

No changes to model, prompt, condition, target, fault, scoring or per-trial limits:
context8192, output allowances256/512/1024, total2048 generated tokens,8 calls,
180seconds,16 tool attempts,10 native operations,one dispatched write. Recovery
remains at most2 extra requests charged within the original limits. The resume
batch adds at most40 inference requests and10240 output tokens; conservatively
reserve8 calls and2048 output tokens for the unscorable attempt. Verify before
freeze that prior known/upper usage plus those reservations still fits the original
320-call/81920-output ceiling. No OAuth required. Resume active-time cap30minutes,
with the original prior active period plus this cap below3hours; exclude external
downtime from active resource time. Record cold-loading/restart effects as limits.

Final report/ZIP must contain all original artifacts, original metadata-accounting
exception, the external interruption receipt and any recovered incomplete trace,
replacement provenance, all40 scored outcomes and independent40-trace readback.
Completion rates over scored trials must be labeled complete-case descriptive
rates; the external interruption does not restore the missing outcome. Preserve
Baseline v1, prior96-trial collection and all published artifact checksums.
