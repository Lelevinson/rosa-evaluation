# Live prompt-validation continuation R1

Prospective amendment after a generic hosted stream error. No model, prompt,
schema, controller, scoring, permissions or trial limit changes. Keep the
initial attempt/checkpoints and all earlier experiments intact.

Initial Qwen:9/9 completed correct,34 requests, all nine audits and controls
passed, normal shutdown/unload. Initial hosted:four scoreable completed trials,
all correct; one service-censored attempt during cell4; four cells unstarted.
Thirteen hosted requests were reserved, twelve returned usage, one has unknown
cost. Error code was `error`, with no HTTP status; this does not establish quota
exhaustion or a model capability failure. Both simulators closed normally and
the initial hosted token session was revoked.

R1 runs ONLY original schedule indices4..8: the censored missing-prerequisite
primitive case and the four unstarted cells. Completed passes AND genuine
completed failures are never selected. The interrupted case had selection and
one unavailable read, zero dispatched trajectories and no accepted report.
The continuation starts a new dialogue after an independently verified reset;
it does not replay an uncertain movement or pretend the interrupted dialogue
completed. Any prior command, report, unmatched schedule, non-clean shutdown or
uncertain extra attempt rejects the plan. A single bounded continuation is
allowed; a further service failure stops for review, with no retry loop.

Maximum40 additional inference requests (5x8), at most53 combined given the
initial13; an independent counter also retains the original72-request ceiling
and4500 cumulative active seconds. Each trial retains all existing limits.
Consent waiting is excluded from active time. Six fresh deterministic controls
precede the continuation; same independent observer, no oracle access by policy,
same actual-input checks and exact local/Phoenix span audit. Freeze sources,
schedule and original evidence hashes before new inference.

Initial manual consent and validated scopes are mandatory. Use the existing
memory-only renewable session and normal revocation. Initial tokens were already
revoked; the user must manually authorize the new session. No OAuth implementation
or permissions changes, persisted credentials or automatic approval.

Report all attempted costs, including the original censored call and read.
Keep its raw `pass=false` untouched, classify it separately from completed
capability outcomes, and label the combined analysis with continuation lineage.
Readiness requires all nine scoreable hosted cells plus Qwen's nine to satisfy
their original contract and every attempt (including the censored one) to pass
instrumentation/bounds audits. Do not infer success for the remaining cells.
