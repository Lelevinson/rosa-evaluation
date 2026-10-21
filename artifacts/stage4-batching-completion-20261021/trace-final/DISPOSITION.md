# Trace provenance accounting correction

The controlled task and complete trace were retained. Acceptance rejected the
initial nesting assumption: explicit native spans attach to the run, while the
installed LangChain instrumentor keeps its own tool-span context. Native spans
are now counted by their explicit stage4.actor provenance, separately from model
tool dispatches. The trace also exposed a transient one-second CLI discovery
failure; both arms now receive a common five-second parameter discovery allowance.

Fresh acceptance is trace-ready. No live model requests have occurred.
