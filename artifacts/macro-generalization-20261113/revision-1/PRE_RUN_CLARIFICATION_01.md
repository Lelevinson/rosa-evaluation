# Stage0 clarification 01

Date: **2026-11-13**. No model requests have occurred.

The pre-run note's phrase “no cross-trial memory/cache assistance” concerns
agent history, episodic memory and reuse of task evidence. It does **not** turn
off Ollama's server prefix/KV reuse. Original A/M4 server prompt-cache policy is
preserved; client response caching stays off and each task starts with fresh
agent history and mock state. Do not describe this as a cache-disabled server.

The base mock now derives readiness from typed quantities and map-revision
relationships, rather than merely renamed Boolean flags. A goto updates planar
position and heading fraction, with simple distance-proportional battery use;
partial actuation leaves heading unchanged. The exact source thresholds and
model constants are recorded in worlds.py and the observer report. These are
mock definitions, not measured hardware properties or extra agent acquisitions.

This is Stage0 engineering completion before controls/dev/live trials, not the
post-Sol-dev case/scorer revision cycle. Earlier passing development observer/API
records are retained under development-before-base-semantics. Their counts do
not increase the research sample size. Current source digests accompany rerun
observer/world unit checks; no failed model outcome was rerun.

The original pre-run note remains intact. This clarification is separately
checksummed with it in the revision manifest. Thresholds and stage advancement
remain unconfirmed.
