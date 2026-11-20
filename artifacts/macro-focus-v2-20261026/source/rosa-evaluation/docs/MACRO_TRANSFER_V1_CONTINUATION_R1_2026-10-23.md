# Four-cell continuation, authorized 2026-10-23 Asia/Taipei

Continue only the four remaining hosted cells from macro-transfer-v1-20261022.
Do not restart Qwen or any completed hosted result, including genuine model
failures. The prior hosted batch used43 requests:42 returned generations and
one quota-interrupted attempt before any tool/native activity. Preserve that
attempt, its unknown token usage, all primary scores and the sealed partial ZIP.

Order: missing_prerequisite/workflow (new attempt after quota), then
transient_after_motion/model, /workflow and /macro. Retain original scheduled
order and case definitions. Outputs go to a separate
macro-transfer-v1-resume-r1-20261023 directory. A schedule maps original cell
indices and prior attempt IDs. The original execution loop is reused through
temporary output-directory, job-list and freeze-verifier settings restored
after execution. No agent, tool, prompt, model parameter or scorer is changed.

This intentionally retains the documented shared default-prompt/tool mismatch;
fixing it now would alter the treatment. That defect remains a caveat and must
be repaired in a separate prospective milestone before larger research claims.

Budgets: at most32 new hosted inference requests; at most75 combined hosted
requests including the43 prior attempts, below the original144 ceiling. The
OAuth backend independently enforces32 requests. The shared counter preserves
the original4500 active batch-second limit including previous active time.
Manual consent waiting is excluded. Original per-trial limits stay8 requests,
180seconds,16 tool attempts,10 native operations,one dispatched trajectory and
three correction opportunities. The observed2048 generated-token stopping
threshold remains; it is not an equivalent hosted hard generation cap.

Fresh Gazebo startup, six deterministic controls and independent home reset
before each selected trial are required. All native attempts, invalid attempts,
known/censored usage, latency, goal truth and fault exercise remain recorded.
Actual local/Phoenix exact-span and closed-tree audits run for every attempt.
Do not execute incomplete arguments or replay a command after uncertain outcome.

Initial consent remains manual. Existing granted-scope validation, optional
authorized memory renewal and revocation on exit are unchanged. No token is
persisted. If quota or authorization remains unavailable, save evidence and
stop without automatically retrying, obtaining further consent or changing an
account/model. Quota renewal is not bypassed through refresh or sign-in.

Before consent: validate original source digests, original artifact digests,
selection/refusal/restoration/resource-cap tests and freeze the continuation
sources/schedule. No model calls occur during preparation. No automatic rerun
of a populated continuation directory is permitted.

Analysis joins cells by backend/case/condition. Use a continuation result only
for a previously quota-interrupted/unstarted cell; never replace a completed
scoreable result. Keep every infrastructure request in the cost ledger. If
all four complete with full returned usage, the combined matrix has36 scoreable
trials plus the preserved original quota attempt. Failures of the robotic
task remain outcomes and are not grounds for another attempt. If quota stops
again, mark the combined matrix incomplete, classify only explicit service
interruptions separately, and list unfilled cells without imputing success.

Report the session/time separation and the possible variability of a hosted
model under the same catalogue slug. Freeze/settings identity is not proof of
identical hidden server weights or exact repeatability. Prior limitations,
strict retention screen, one-repetition sample size and prompt audit exception
remain visible. No physical-robot, algorithmic novelty or broad reliability
claim follows from finishing these four cells.
