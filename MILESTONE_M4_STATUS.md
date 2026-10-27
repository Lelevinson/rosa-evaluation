# M4: frozen paired evaluation

Date: 2026-10-27. Branch: member/martin.

The study is launched, not completed. Frozen runtime/protocol checkpoint: 4412f05;
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

No M4 conclusion, final retention decision or M5 progression is claimed here.
Commits remain local; no remote push was performed.

## Completed hosted checkpoint

Sol completed all40 scheduled trials with all40 local/Phoenix audits passing and
clean simulator teardown. Primitives:20/20 primary passes,68 model requests,
38 native operations. Macro:20/20 primary passes,38 requests,40 native operations.
That is44.1% fewer model requests with5.3% more native operations in these cases.
It is a within-backend observation, not a broad reliability/generalization claim.

All four Sol clarification transcripts were reviewed against the frozen rubric:
each requests user clarification/confirmation before selecting a skill, acquiring
observations or reporting completion. The review is recorded as Codex operator
review, not independent human adjudication. Qwen is running; its results and four
clarification reviews remain pending. The full M4 verdict therefore remains pending.
