# Llama / Granite integration diagnosis

Date: **2026-11-17**. Owner-authorized investigation, separate from every completed benchmark. No robot, ROS topic, actual tool execution, hosted service, OAuth grant, score alteration, or installed source/template change.

Use the existing pinned Ollama server, frozen Python environment, model digests and tool adapter. Check all 69 original frozen source/config hashes before and after. Freeze this diagnostic script and protocol before its first model request. Store actual HTTP request bodies and response objects for deliberately synthetic public fixtures; never store HTTP headers or credentials.

Maximum **48 generation requests**, each capped at **512 output tokens**, 8K context, temperature 0, seed 42; no retries. Total window 30 minutes. Run one model at a time, verify idle GPU before launch, unload each model afterwards. Every reserved request and error remains recorded. These are exploratory post-hoc integration probes, not a new correctness benchmark.

1. Zero-network checks: capture SDK serialization with an HTTP mock. Determine whether constructor `streaming=False` actually makes `stream=false` on the wire; compare explicit `stream=False`. Inspect whether ToolMessage names survive conversion. Retain installed adapter source/version/hash and exact saved model templates. Verify strict schema examples using the frozen argument models.
2. Qwen positive control: the harmless `lab_probe(value=ready)` through raw HTTP and the frozen adapter, explicit nonstreaming.
3. For Llama and Granite, cross raw HTTP versus adapter, stream false versus true, and three system variants: no custom system, the previous generic diagnostic system, and that generic system plus model-native formatting guidance copied from its saved template. Raw requests use the same SDK-serialized request structure as the adapter. Record server-native calls separately from the adapter's parsed calls.
4. Synthetic tool-result follow-ups for SUCCESS and UNKNOWN, plus one read-state call. Compare the existing generic system against the same system with the supplied tool schemas retained in the system message. This tests schema visibility, without accepting aliases, manufacturing sensor observations, or changing validation.
5. Synthetic correction after a deliberately malformed report: compare generic versus persistent-schema system. Separately test preserving tool_name in the serialized ToolMessage, with all other fields held fixed. These are opt-in diagnostic variants, never patches to the frozen adapter.
6. For each model, test two combined native-format-plus-persistent-schema follow-ups (SUCCESS and UNKNOWN), clearly labeled as a combined intervention.

The full schedule is two Qwen controls plus 23 requests per investigated model = **48**. Schema validity and expected argument equality are checked without executing tools. The mock responses and observations are explicitly fixtures, not real-world evidence. Stop rather than widen this schedule or tune on results. Persistent-schema and tool-name variants are diagnostic prototypes only; neither is silently deployed.

Readiness here is not robotics competence. Successful probes justify a later, separately defined validation of a new integration configuration; they do not repair or replace the 80-trial outcomes. Record any mismatch between intended serving settings and observed wire behavior as a dated correction, preserving earlier artifacts.
