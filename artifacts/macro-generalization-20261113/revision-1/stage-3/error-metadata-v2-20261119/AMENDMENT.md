# G1 reduced error-metadata contract: approved before freeze

Date: **2026-11-19**. Owner instruction: **"Accept reduced metadata coverage and
keep protected code unchanged."** This adopts the second proposal in the
November17 decisions document, preserving the separate already-reviewed
clarification-scoring amendment. No held-out launch, new OAuth consent, robot
operation, budget expansion or Git publication is authorized.

This is an explicit additional prospective pre-freeze amendment to A2/G-c. The
old full-coverage requirement did not pass; its original failure evidence and
unapplied protected-source hook remain intact. The original Stage2 stream error's
underlying provider cause remains unknown. Do not retrospectively manufacture
metadata for that trial.

## Five-question preflight

1. **Closest implementation/change (F/P):** unchanged SiwcBackend/RecoverableSiwc
   plus the retained G1 boundary observer. Add an opt-in G1-local subclass that
   observes parsed events and sanitized exceptions while retaining the existing
   request builder, HTTP helper, parser and recovery implementation. This is
   instrumentation engineering, not a new research algorithm.
2. **Need/limits (F):** six retained zero-network boundary fixtures showed that
   open_request discards original HTTP error-body fields; the previous probes
   were not integrated transport validation. One dev interruption had no known
   underlying cause. No efficiency or reliability gain is inferred from this.
3. **Decision/discriminator (P):** record only fixed fields and allowed values
   at an actual observed boundary, at most64 characters per string. HTTP body
   details and unobservable stream state become NOT_RECORDED. Raw message text,
   prompts, headers, tokens, reasoning and payloads never enter metadata. Compare
   the unchanged transport with the observed subclass under six injected faults.
4. **Fair controls (P):** identical bodies, permissions, token source, parser,
   SafeError semantics, availability state and request charging. The same
   unchanged recovery gate decides eligibility and enforces one retry per
   logical call and the separate reserve. No observation authorizes replay.
5. **Smallest work/stop (P):** implement the local subclass and integrated
   zero-network golden/canary tests, including real request parsing and recovery
   accounting. Preserve source hashes and failures. Any change in request,
   parser, error, charging or retry semantics blocks G-c. No live model call is
   needed. All new implementation/evidence remains in this directory.

## Revised required coverage

| Field | Required v2 behavior |
|---|---|
| failure_surface | Fixed observable category; generic sanitized transport failure does not prove a timeout or provider cause. |
| http_status | Existing sanitized exception status when observed; otherwise NOT_RECORDED. |
| sanitized_transport_code | Fixed allowlisted existing exception code, explicitly distinct from original provider code; otherwise NOT_RECORDED. |
| stream_event_type | Fixed recognized failure event type when parsed; otherwise NOT_RECORDED. |
| provider_code / provider_type | Fixed allowlisted fields from an actually observed parsed failure event only. Original HTTP-body details already discarded remain NOT_RECORDED. |
| output_events_arrived / stream_events_received | Boolean and count at the parsed-event boundary once observable. Before a stream is available both remain NOT_RECORDED, not false/zero. |
| response_id | Only a recognized bounded response identifier observed in the stream; otherwise NOT_RECORDED. |
| elapsed_ms | Measured instrumentation wall time, nonnegative integer; not provider serving time. |

String values are rejected rather than truncated into misleading identities.
Unknown codes/types are NOT_RECORDED, never guessed from arbitrary messages.
No raw HTTP body is inspected a second time to defeat the protected boundary.
Success output and encrypted reasoning remain only in the unchanged return path.
Observations do not change censoring, outcome scoring, quotas or authorization.

G-c can pass against this adopted reduced contract only after integrated checks.
This is not evidence that the original full-coverage A2 requirement passed. The
next freeze must pin the new local source and its approved contract. Earlier
failed protection checks, including authorized mutable-master drift, are retained.
