# Metric operationalization before end-to-end results

Recorded after protocol freeze while the hosted reliability track was running:
zero Track B batching results were available.

The protocol's native-work retention metric is operationalized as **actual CLI
commands**, the native work unit used in the preceding calibrated comparison.
Server parameter RPC counts remain a separate secondary metric; they will not
replace CLI work post hoc to make a threshold pass. All automatic reads, writes
and charged warm-up commands count.

Within each backend, pair the two arms by task template and repetition. Compare
all planned outcome denominators. For cost/time benefits, separately report the
pairs where both complete strictly and operationally; disclose how many pairs
are excluded and preserve their all-attempt costs/failures. A candidate passes
the screening retention criterion only with no observed overall completion loss,
at least 10% lower paired successful CLI work or end-to-end time, and the same
nonnegative direction in both repetitions for that selected metric. Zero matched
successful pairs cannot satisfy a benefit criterion. Show both metrics even when
neither qualifies. Descriptive uncertainty does not establish noninferiority.

The strict matched baseline includes the same helper, native capabilities,
continuations and conservative evidence as candidate. Any benefit is an effect
of the combined model plus selected orchestration, not a claim of improved
intrinsic reasoning. Manifest errors, bypasses and recovery remain explicit.
