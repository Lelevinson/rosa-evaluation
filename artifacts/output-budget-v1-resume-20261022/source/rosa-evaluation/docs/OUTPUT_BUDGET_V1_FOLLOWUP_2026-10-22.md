# Output diagnostic v1: separately frozen timeout-accounting follow-up

The first scheduled trial (R256, healthy movement, repetition0) reached the robot
goal but exhausted180seconds before an accepted report. It remains FAILED. The
first six generations returned1026 output tokens; generation7 was interrupted
without usage metadata. Its original accounting audit failed completed_usage_records,
and the supervisor stopped exactly as declared, unloaded Qwen and released power.
Original source/data/score remain unchanged. No model-driven trial is rerun.

This version executes ONLY the remaining39 entries of the original frozen schedule.
The original trial is retained as the first of40 in the combined report. No targets,
faults, model options, prompts, recovery behavior, call limits,180second deadline,
2048token cap, operations, writes, scoring or schedule are changed. No additional
deterministic Gazebo trials are needed: the controller/skill code is unchanged and
the existing four fresh controls remain prerequisite evidence.

The harness now distinguishes a closed, intentionally interrupted LLM span from a
completed generation with usage. Missing usage is permitted only for the one last
generation terminated by the180second wall deadline. Record its actual output as
UNKNOWN and bound it by min(per-call allowance, remaining output budget). Known
totals are LOWER BOUNDS; never call these exact total usage. No further inference
occurs within that trial. Reserve the full unknown allowance in independent budget
checks. Afterward, serialize a model unload before the next reset/trial and archive
its duration separately. Do not replay a robot command or automatically retry an
uncertain provider response. Other missing metadata/errors still stop the batch.

Two additional offline actual-ROSA tests cover closed interrupted spans, no native
dispatch, honest missing-usage attribution and finite conservative bounds. The
original six recovery/design tests remain required. Freeze this source separately
before live continuation. Original batch cap320 remains: original7 calls plus at
most312 for39 remaining trials equals319, below320. No OAuth is needed.

The original first-trial audit exception is reported alongside independent
persisted span readback, not erased or relabeled as an original passing audit.
Any higher-level conclusion must preserve this interruption/accounting exception.
