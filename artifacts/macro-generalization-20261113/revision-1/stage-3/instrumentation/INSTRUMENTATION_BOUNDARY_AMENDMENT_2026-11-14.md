# Instrumentation proposal — blocked, no protected source edit applied

Date: 2026-11-14. Scope: prospective error observability only; no request-body, retry, parser or SafeError-semantic change authorized/applied.

The six zero-network probes cover HTTP 503, HTTP 429, an in-stream failed event with a code, an in-stream error without a code, mid-stream termination and timeout. Stream-event observation preserves the event objects and yielded order. Golden exception signatures and unchanged retry eligibility match in the stream cases; HTTP signatures have the original eligibility (503 yes, 429 no). A canary in fake error/output text does not enter retained records. Per-field strings are limited to 64 characters and only the fixed record-field allow-list is used.

However, this is a boundary probe, not a completed integrated transport. The original `rosa_auth.oauth.open_request()` consumes HTTP error bodies and returns only sanitized code/status through SafeError. A provider type that was present, and an unrecognized original provider code, cannot be recovered by a G1 wrapper outside that function. Both HTTP probes demonstrate the loss. No retry or error sanitizer was bypassed to obtain those values.

**G-c is BLOCKED.** The complete requested instrumentation test cannot pass under the unchanged interface. `PROPOSED_HTTP_OBSERVATION_HOOK.patch` supplies a minimal optional observation hook for owner review. It is not applied. The hook emits canonical allow-listed metadata only; arbitrary messages, payloads, headers, tokens and error strings are excluded. Existing callers retain the same SafeError code/status/message and parser behavior. The future G1 wrapper would observe parsed stream events and elapsed time locally and use the optional HTTP hook.

If approved, this diff still needs implementation, full golden comparison through the actual subclassed transport, canary tests for all surfaces, elapsed-time validation and a fresh protected-source policy amendment before a freeze. The current six probes do not substitute for that validation. The Stage 3 source-protection rule expressly requires stopping and presenting the diff rather than applying it.

Source hashes before and after, the six fixture outcomes and all retained sanitized probe records are in `observability-boundary-tests.json`. No real network, model or OAuth request was made. The canary exists only as a fake test input in the test source; no canary value occurs in the output records.
