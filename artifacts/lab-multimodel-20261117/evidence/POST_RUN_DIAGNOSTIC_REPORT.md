# Post-run native tool-binding diagnostic ? 2026-11-17

## Separate post-run tool-binding diagnostic

This was a **post-hoc diagnostic after the main outcomes were seen**, using the protocol's optional allowance: one request/model, at most 64 output tokens, the same harmless `lab_probe(value=ready)` request and schema. No returned tool or code was executed. No main trial, failed task, prompt, guard or score was changed or retried.

| Model | Correct native call in this one probe | Input / output tokens |
|---|---|---:|
| qwen3.5:9b | True | 315 / 26 |
| llama3.1:8b-instruct-q4_K_M | True | 196 / 17 |
| granite3.3:8b | False | 113 / 29 |
| ministral-3:8b-instruct-2512-q4_K_M | True | 100 / 12 |

Qwen, Llama and Ministral returned the requested native function call. Granite returned JSON text (`tool_name`/`arguments`) with an empty native `tool_calls` list. Thus Llama's main failure cannot be explained by a total inability to return a basic native tool call, while Granite's compatibility question remains unresolved. One tiny probe does not establish comprehensive tool competence, and this is not held-out evidence.

All four diagnostic persisted audits passed (eight spans total), with zero native executions. The diagnostics used **4 requests, 724 input tokens and 84 output tokens**, reported outside the **1,008 main model requests**. Combined observed inference total: **1,012 requests**. The main campaign had zero infrastructure reserve uses and complete returned usage; the diagnostics were not charged as unrecorded free work.

The original main archive remains byte-identical. Diagnostic source, responses and traces are in `ROSA_LAB_TOOL_PROBE_ADDENDUM_2026-11-17.zip` (23 content hashes verified). Main archive SHA-256: `fa5c14cb31ab4079317106af815bf86a810effff595fefa05f2eb6d6d51d9356`. Addendum SHA-256: `e0780f578c6d328a5912176dd8ff9afa2f54df230cb07e4436ac07394a4e8f49`.
