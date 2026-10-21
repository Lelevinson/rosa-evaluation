# Trace-read timeout before live inference

The scripted ROSA/real-parameter case completed, but the default Phoenix client's
read timed out while exporting from the accumulated project. Its run ID is
preserved in metadata.json. No live model requests were made.

The new campaign uses its own Phoenix project and an explicitly bounded 60-second
local HTTP read client with environment proxies disabled. Fresh trace acceptance
is recorded in trace-final, before freezing or starting live models.
