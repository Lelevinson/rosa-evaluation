# G1 reduced error-metadata repair completed

Date: **2026-11-19**. **G-c PASS against the explicitly adopted reduced contract.**
This does not relabel the original full-coverage requirement as passed.

The owner explicitly selected **"Accept reduced metadata coverage and keep
protected code unchanged."** The [dated amendment](AMENDMENT.md) records that
choice. The new [observed transport](observed_transport.py) stays in the G1
directory. Protected authentication, Responses parser, adapter, recovery gate,
resource limits and credential cleanup code remain unchanged.

## Recorded information and limits

The subclass retains the existing request builder, HTTP helper and parser. A
small local port of the existing respond method inserts a parsed-event observer
and stores only bounded, sanitized failure metadata. Recovery and token cleanup
are inherited unchanged. No global production functions are monkey-patched.

Records contain only the fixed fields in the amended contract: failure surface,
HTTP status, explicitly sanitized transport code, recognized stream failure type,
visible allowlisted provider code/type, parsed-event count, whether a recognized
output event arrived, bounded response ID and measured elapsed milliseconds.

Original HTTP-body provider fields are already discarded by the protected
helper and stay **NOT_RECORDED**. Before a stream can be observed, output-event
presence and parsed-event count also stay NOT_RECORDED. A generic transport
failure does not prove timeout, quota exhaustion or revocation. The original dev
interruption's provider cause remains unknown; it was not rescored or backfilled.

The observer yields the same event objects in the same order, leaving parser
consumption and mutations unchanged. No raw payload, headers, error messages,
prompts, assistant text, encrypted reasoning or access/refresh credentials enter
the metadata. Unknown code/type strings are discarded. String fields are limited
to64 characters; identifiers that fail the bounded format are not recorded.
Successful Responses output, including private reasoning continuation material,
stays in the unchanged return path and produces no failure metadata record.

## Integrated zero-model validation

**12 test methods PASS on their first integrated run.** See the
[exact log](validation-attempt-01/test.log),
[golden records and source hashes](validation-attempt-01/RESULTS.json), and
[test implementation](test_observed_transport.py).

The tests use the actual unchanged OAuth HTTP helper, SSE parser and completion
parser. They compare the existing RecoverableSiwc transport to the new observed
subclass with a fake opener. A second comparison goes through the actual
ChatSiwc model interface, G1 LoggedGate/Campaign and original RecoveryGate. Socket
connections are explicitly blocked during execution. No actual provider call,
OAuth renewal or robot operation is involved.

| Injected failure | Same resulting exception | Same requests through gate | Same eligible retries |
|---|---|---:|---:|
| HTTP503 | SafeError: http_error, status503 |2|1|
| HTTP429 | SafeError: http_error, status429 |1|0|
| In-stream failed event with code | SafeError: rate_limit_exceeded, no HTTP status |1|0|
| In-stream error without code | SafeError: error |1|0|
| Mid-stream end | SafeError: stream_ended_without_completed |1|0|
| Observable stream timeout | TimeoutError |1|0|

For each comparison, request method/URL, body bytes and headers matched via
in-memory comparisons of retained cryptographic signatures. Raw bodies and
headers were not saved. Exception type, code, HTTP status, message digest,
availability latch, parser behavior and stream closure matched. Successful return
content also matched by digest. Timing values are measured independently and
checked for validity rather than incorrectly required to be numerically equal.

The real gate comparisons preserve normal decisions, charged physical calls,
known usage, incomplete-usage flags, campaign counts and reserve accounting. A
503 retry consumes two physical attempts but one ordinary decision slot, exactly
as before. Extra checks show that a second503 is not retried again, an exhausted
reserve does not expand, and the transport request ceiling still stops execution.
No metadata observation authorizes a replay or changes robot-command policy.

Additional checks cover malformed parsed events, event-object identity/order,
observable125ms elapsed time with an injected clock, unrecognized codes/response
IDs, detached metadata snapshots, unavailable-session suppression, token-reference
cleanup, and a connect timeout whose cause the HTTP helper sanitizes away. That
last record correctly says TRANSPORT with unknown stream fields rather than
claiming a known timeout. The fake secret canary is absent from every retained
test metadata record and test log. Synthetic input source contains the canary
by design; no actual credential was read or used.

The Windows Python3.14 environment lacked JWT/LangChain dependencies. Initial
WSL enumeration was sandbox-denied; the authorized escalated read succeeded.
Tests used the existing WSL research Python3.12.3 and installed dependencies.
Nothing was installed or upgraded. These were environment-discovery checks,
not failed model trials or failed integrated tests.

## Preservation and use

Before/after hashes for the actual transport, parser, adapter, inference budget,
recovery code and new observer match in the test receipt. A separate inventory
records all3,757 prior G1/protected entries before this work. Final preservation
verification and the local repair manifest accompany this report. Earlier
boundary probes, the unapplied protected-code hook, all experiment records,
human submissions and the renewed clarification review remain unchanged.

The old protection guard's previously recorded master-README mismatch remains
explicit; updating the living record is not reported as a clean pass of that
historical guard. No protection rule was silently relaxed and no freeze was
created. A future freeze must explicitly pin mutable-document scope, new sources
and their actual execution/analysis wiring.

The transport is opt-in. A future authorized G1 executor can import
ObservedRecoverableSiwc and use it in place of RecoverableSiwc, leaving ChatSiwc,
the existing gate and permission logic unchanged. It must checkpoint the
sanitized `error_metadata_records` beside existing progress and include this
module/contract in its source freeze. This work validates that transport path;
it does not claim a held-out executor has been frozen or run. The original
completed dev executor is deliberately not edited or rerun.

## Current readiness

- **G-c: PASS for approved reduced metadata coverage**, original full-coverage
  failure retained.
- **G-e: PASS for the previously reviewed clarification-v2 layer**, with its
  original legacy review still failed as historical evidence.
- **G-f: PASS on Levinson's real ratings and eligibility self-declaration.**
- **G-g/G-h: not completed**. The remaining preparation is assembling and
  verifying the exact new freeze/execution/analysis wiring and protection scope,
  then the fresh restore-only authorization preflight. Earlier draft records are
  historical and do not prove provider validity or quota.

Both owner decisions are now recorded and neither repair awaits another approval
to be considered implemented. No new human ratings were invented, no model-driven
experiment or authentication operation occurred, and no Git commit/push/upload
was performed. Stage4 still requires the separate authorization specified by the
original protocol after the freeze and preflight record are reviewed.
