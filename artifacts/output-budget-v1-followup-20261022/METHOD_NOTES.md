# Interpretation notes recorded during the diagnostic

These are observational/methodological notes, not edits to the frozen protocol,
schedule, settings or scoring. The study is still running when this note is written.

- All conditions share180seconds,2048 generated tokens and8 requests. This asks
  what works within that fixed resource envelope. It does not establish maximum
  Qwen capability with longer time or a different output budget. A length stop and
  a wall stop are different mechanisms and must remain separate in conclusions.
- The first R256 healthy trial reached the independent joint goal but exhausted
  time before reporting. It is a failed complete workflow, with meaningful partial
  progress. Its original metadata-accounting audit exception remains preserved.
- The first L1024 healthy trial also reached the goal but hit the time limit before
  an accepted report. Its second response used446 tokens and issued a tool call.
  This demonstrates progress beyond the former256 cutoff, not full completion.
- The first L512 healthy trial moved and read fresh evidence, then hit512 tokens
  while composing its report. More output can shift a cutoff to a later step.
- The first concise256 healthy response still narrated state and hit256. Raw input
  confirms that the concise instruction was present. Do not silently tune it.
- Missing-sensor cases require UNKNOWN, suppressed/partial commands require
  independently verified FAILURE, and healthy cases require attained goals plus
  a truthful accepted SUCCESS report. Aggregate correctness is not all movement.
- Post-timeout unload serializes cleanup before another trial. The next trial can
  include model cold-loading time. Startup, resource contention and order can
  affect wall latency; counts are easier to interpret than a causal speed claim.
- The five-condition order is preselected, rotated and reversed within case blocks.
  Two repetitions cannot fully balance every condition across all five positions.
  Blocking reduces some order confounds; it does not eliminate them.
- Full-precision live sensor values and acquisition timestamps differ between
  trials, even with seed42 and nominally identical resets. These are mechanistic
  diagnostics on known tasks, not a holdout demonstration of generalization.
- Only completed generations have exact returned usage/finish reasons. An
  interrupted last generation has unknown usage and finish reason; record known
  lower totals and conservative requested-allowance upper bounds. Do not equate
  partial token totals with exact efficiency or count an unknown finish as length.
- Unsupported-success counters cover structured submit_report SUCCESS attempts
  against fresh evidence and the call-time oracle. They are not an exhaustive
  semantic grading of every sentence of free-form prose. Raw prose is preserved
  for review; avoid claiming that a zero counter proves all narration was sound.
- No new Sol trials are planned. Historical Sol outcomes provide context only.
- The completion integration is opt-in and tested here in synchronous local ROSA.
  These results do not validate every provider, asynchronous streaming integration,
  arbitrary tools, physical hardware or robot safety certification.
