# UR5e transfer follow-up v1

Preserve the complete reliability-v2 attempt, including80 live validation/mock
trials and its failed first deterministic arm reset. Both mock backends completed
32/32 correct outcomes; all64 mock Phoenix trace-ID sets matched. The16 earlier
validation traces also matched. No model-driven arm trial ran in that attempt.

The failed reset is a setup failure, not a model failure or an interrupted chat.
Joint-state publication preceded confirmed trajectory-controller readiness.
The new simulator startup waits up to120seconds for BOTH joint_state_broadcaster
and joint_trajectory_controller to be active, then requires fresh six-axis state.
These readiness service queries occur outside trials, are archived separately,
and never provide free observations to the model. The subsequent controller,
three-second trajectory, four-second settling,0.025rad tolerance and skill are
unchanged. Four deterministic controls passed with the readiness correction.

This is a separate prospective arm follow-up, not an alteration of old sources,
scores, protocols, failed gates or cleanup records. Freeze all new source and
this document before either backend runs. Preserve exact copies of all imported
v2 runtime/case/scoring dependencies and the previous source manifest.

Use the original four arm cases and A/D ordering unchanged: coordinated move,
suppressed command, partial trajectory and missing agent sensor. Eight trials
per backend, with64 model requests maximum/backend. Sol runs before Qwen, using
the same actual ROSA executor and strict node-keyed tools. Resource limits remain
8 model calls,16 tool attempts,10 native reservations,180seconds,3corrections and
one dispatched write/trial; three-hour phase ceiling. No model-specific tuning,
extra retry rights, automatic report construction or inference optimization.

Keep original A/D definitions and reporting contract, including the documented
goal_verified=false/nested-verification ambiguity. Do not silently fix that
experimental interface while calling this a transfer of the same candidate.
Interpret redundant checks and costs with that limitation. A future interface
correction requires its own prospective validation. Ordinary trusted read evidence
is reusable for both models and arms, just as in the frozen mock study.

All accepted outcomes require separate sensor observation and truthful structured
reports. Independent observer reads occur at every report attempt and after each
trial. Archive reset measurements, native ledgers, model-generated calls/reports,
invalid attempts, automatic checks, original claims, latency and model calls.
The public topic is a publication request, not a controller-success receipt.
Do not substitute target echo or model cache for actual JointState measurements.

Every real tool/native/model span must close. Reconcile callback IDs, operation
ledger, model-attempt counters and exact persisted Phoenix span-ID sets in the
new rosa-ur5e-transfer-v1-20261022 project. Missing spans fail acceptance. Expected
model failures remain results; do not rerun until passing. Deterministic reference
and model trials share controller configuration, targets, faults and resets.

Use the existing memory-only OAuth renewal and cleanup. Initial consent stays
manual; the old session was revoked and must not be reused. The new hosted cap
is64 and does not reset spent requests from the preceding project work. Preserve
all progress and stop on unavailable authorization; never infer or bypass new
consent. No credential persistence is introduced.

Analysis remains the original exploratory comparison with small denominators.
Report both backend/arm outcomes, fault handling, claims, rejected calls, calls,
native work and latency alongside matched deterministic controls. Do not claim
generalization, safety, novelty, broad small-model benefit or statistical power.
The empty-world joint-space task does not test grasping, obstacles or perception.
