# M4: completed paired evaluation — mixed findings

Date: 2026-10-27. Branch: member/martin.

The study and required reviews are complete. Frozen runtime/protocol checkpoint: 4412f05;
research component: c0c61a0. M4 introduces no new product policy or architecture.

- 80 scheduled live trials: ten families x two repetitions x two conditions x
  two backends. Sol runs40 first, then Qwen40; simulator access is serialized.
- Same-model primitives versus simple macro, with common permissions, reporting,
  guards, serving profile, inference allowance and independent outcome checks.
- Ten offline M4 tests passed. Research regression:187 executed successfully,
  43 skipped (including optional Windows integration not re-enabled this run).
- Zero-model gate:20/20 actual Gazebo controls,20/20 exact Phoenix audits,
  202 matched spans, simulator returncode0 and no cleanup errors.
- 62 source/configuration files frozen. All382 original M2/M3 manifest entries
  verified unchanged. Earlier scores, trials and archives remain preserved.
- Eight charged model calls/task; three separate transient-HTTP reserve slots
  per backend; hard maximum323 requests/backend,646 combined. Task limit360 seconds.
  The eight-hour backend ceiling accommodates the full schedule plus bounded
  overhead; it is not an estimate that the run should take eight hours.
- Remembered authorization is opt-in, protected and scope-validated. This runner
  stops if the stored grant is unavailable; it does not open fresh consent itself.

[Frozen protocol](docs/M4_MACRO_PROTOCOL_2026-10-27.md)

Progress is recorded under `artifacts/macro-m4-20261027/`: per-backend checkpoints,
per-task inference journals/results/traces, and operator/status.json. The detached
worker processes continue independently of the chat while the machine is running
and awake. Hosted quota or authorization loss can still stop the hosted backend;
that does not imply its remaining tasks passed. Qwen is launched independently
afterward even if the hosted process exits unsuccessfully.

At execution end the worker generates M4_EXECUTION_REPORT.md and analysis.json,
then builds a checksummed execution-checkpoint ZIP. These remain preliminary until
the saved clarification transcripts receive the frozen operator-review rubric.
Neither fewer calls nor a truthful selected-skill report automatically establishes
correct user-goal completion. Record all failures, recovery and unstarted cells.

Pre-freeze errors were retained: a zero-write fixture initially required a command,
and the first freeze referenced a nonexistent evaluation-root lock. Both were
corrected before controls/live inference; the actual runtime uses the shared
research lock and separate Phoenix lock. No dependency/model installation occurred.

Final retention: Sol passes; Qwen fails because macro primary completion is14/20
versus15/20 for primitives. Keep the module optional and consolidate the mixed
findings; no new experiment or architecture is launched. M5 is not yet started.
At the original M4 closeout, commits were local. M5 subsequently published and
verified the research branch; evaluation backup publication awaits an explicit
destination/disclosure choice. See the living master record for current status.

See the [final report](artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md),
[efficiency/timing](docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md) and
[living project record](PROJECT_MASTER_README.md). The original execution ZIP
predates final Qwen review and remains preserved; the final review package is separate.

## Completed hosted checkpoint

Sol completed all40 scheduled trials with all40 local/Phoenix audits passing and
clean simulator teardown. Primitives:20/20 primary passes,68 model requests,
38 native operations. Macro:20/20 primary passes,38 requests,40 native operations.
That is44.1% fewer model requests with5.3% more native operations in these cases.
It is a within-backend observation, not a broad reliability/generalization claim.

All four Sol clarification transcripts were reviewed against the frozen rubric:
each requests user clarification/confirmation before selecting a skill, acquiring
observations or reporting completion. The review is recorded as Codex operator
review, not independent human adjudication.

## Completed local checkpoint

Qwen completed40/40 trials: primitives15/20, macro14/20;91→53 model requests,
50→48 native operations. All40 local/Phoenix audits pass. All four Qwen clarification
cases fail operator review: readiness was inspected and reported instead of asking
for clarification. All eight campaign reviews are now recorded.

Mean task seconds: Sol16.42→9.73, Qwen133.49→85.18. Full backend time including
setup/reset/audit/cleanup: Sol17.68 minutes, Qwen81.97 minutes. Qwen's savings
do not overcome its failed correctness screen. The final report includes tokens,
medians, all-attempt and successful-pair costs, failures, fault exercise and limitations.

All80 trial audits match3,290 spans;20 deterministic controls add202 spans. Both
simulators cleaned up, with250 requests total, no infrastructure retries or missing
usage. The supervisor's old review-required phase is preserved; closeout.json records
the subsequent final decision. Execution/review closure is not a universal model
reliability or hardware-safety claim.
