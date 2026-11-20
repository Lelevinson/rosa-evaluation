# Pre-dispatch adapter clarification

Date: 2026-11-12. Written before any probe inference request.

Hardware setup attempt 01 verified server version and model digest but stopped
at an overly strict local assertion, before any model invocation or request
reservation. The original attempt/logs are retained. The isolated server was
stopped; no model generation, tool dispatch, or experimental retry occurred.

Read-only inspection of the pinned adapter confirms that `reasoning=False`
produces API `think=false`, but LangChain `streaming=False` does not produce
API `stream=false`: `_chat_params` defaults to `stream=true`, and the adapter
assembles those chunks into the returned message. This is the actual M4
transport behavior. The hardware check preserves it instead of forcing a new
wire mode. The setting remains nonstreaming from the ROSA caller's perspective.

The corrected setup attempt 02 still has the original global allowance of ONE
inference request, 1024 generated tokens, no inference retries and no tool
execution. A durable, exclusive reservation at the probe root prevents any
subsequent attempt from generating again after dispatch or an uncertain return.
Phase 1 remains unapproved and unstarted. The original pre-run note is unchanged;
this amendment and its digest clarify the adapter detail before dispatch.
