# Parity Phase B: adapter record and iteration log (session A)

Owner instruction (2026-11-21, weekend update 1): **do not build adapters from scratch. Use native-schema-v1
(rosa-research `8713f9b`) as the Llama/Granite adapter**, record which parts are template or native-format
transport under the parity rules, flag anything that is not, freeze it, then run the one-time acceptance test.
Iterate only if it fails, inside the time box (3 h or 4 iterations per model), logged as a delta from
native-schema-v1. Update 2: if the Granite sentence is IBM's documented text, it is **transport**, and no owner
exception is needed. This supersedes the PA-1 "owner exception" label in `PA1_CONDITIONS_2026-11-21.md` for the
sentence itself. The flagged items below are recorded, not hidden.

Prior evidence for native-schema-v1 (reported, lab, Gazebo UR5e, 2026-11-17,
`artifacts/integration-rerun-20261117-r1/`): Llama 21→28 and Granite 5→9 known-goal (owner-stated figures).

## 1. Iteration 0 = native-schema-v1, unchanged (frozen before any Phase B model call)

| Item | Value |
|---|---|
| Source | `Lelevinson/rosa-research` commit `8713f9b205033a25f8ed8d9549610e9ad0b8bfde`, `src/rosa_backends/tool_contract_ollama.py` |
| File SHA-256 | recorded in each run's `RUN_META.json` (`adapter_sha256`) and checked again at execute; identical bytes to `integration-rerun-20261117-r1/preparation/tool_contract_ollama.py` (`diff` = none) |
| Wiring | `class ProfiledMeasuredOllama(ToolContractProfile, MeasuredOllama)`: the profile mixin before the frozen G1 `MeasuredOllama` (`stage-4-qwen-lab-20261119/local_model.py`), as `integration-rerun-20261117-r1/preparation/campaign.py:110` did. Runner: `tools/parity/acceptance_run.py` |
| Applies to | `llama3.1:8b-instruct-q4_K_M`, `granite3.3:8b` only. Qwen and Ministral run the frozen plain G1 adapter |

## 2. Classification of every part of native-schema-v1 under the parity rules

| Part | What it does | Source | Class |
|---|---|---|---|
| Granite guidance sentence | adds IBM's tool-format sentence | Verbatim IBM: `ibm-granite/granite-3.3-8b-instruct` `tokenizer_config.json` `chat_template`, HF commit `51dd4bc2ade4059a6bd87649d68aa11e4fb2529b`, URL <https://huggingface.co/ibm-granite/granite-3.3-8b-instruct/raw/main/tokenizer_config.json>. Text SHA-256 in the adapter = `7e12d9b58f45f60365ccc471bae05c77809f94d8947408becb8bce85f39e624e` = the SHA-256 session B verified (PA1_CONDITIONS) | **Transport** (model's documented native format; owner update 2) |
| Llama guidance sentence | adds `Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables.` | Verbatim from the model's own Ollama chat template (G1 `backends/llama/SERVER_SHOW.json` template, tools branch), which matches Meta's JSON tool-call format (PARITY_AUDIT §7 PA-2). Text SHA-256 `236cf22b7d5e10da690a9a9520b92e188b264e0ecc5e044f130a8986bf56ebcd` | **Transport** (model's own template text, kept present on later turns) |
| Tool schemas repeated every request | the JSON of the tools bound to *this* request, in a system message on every turn | Repairs the template defect found in Phase A: Llama's template renders tools only when the last message is a user message, so tools vanish after the first tool result; Granite's tool text is dropped when a system prompt is given | **Transport** (correct rendering of the model's own tool list). Same schemas as all models; nothing per-model in content |
| Header line `Available function schemas (retain these after tool results):` | 1 line of non-vendor text before the schemas | Written by the project, not vendor text | **FLAG: not vendor-documented.** Short, task-neutral, and the same for Llama and Granite, but it is extra instruction text. Reported with every Llama/Granite result |
| Placement | one extra `system` message inserted before the first non-system message, not merged into the existing system prompt (IBM joins with a space; Meta puts tool text in the user turn) | project choice | **FLAG: placement differs from both vendors' templates.** Wording unchanged |
| `stream: false` on the wire | forced non-streaming HTTP | profile requirement | **FLAG: serving difference from G1** (G1 wire `stream: true` for all four models). Output semantics are the same Ollama parser path; recorded per request in the physical-call journal |
| No argument repair, routing, retry, tool execution or template edit | — | profile docstring; code read | OK |
| **SDK list-string → array normalization** (owner note, 2026-11-21) | ChatOllama (`langchain-ollama` 0.3.10 `_parse_arguments_from_tool_call` → `_parse_json_string`) shallowly decodes string-valued arguments with `json.loads`, then `ast.literal_eval`, so a list sent as the string `'["a","b"]'` reaches the harness as an array. Not native-schema-v1's own code: it is in the SDK path used by **every** Ollama model here (and in G1) | langchain-ollama source ("Band-aid fix for issue in Ollama … ollama/ollama#6155") | **ASSISTANCE**, treated like argument coercion (as in Levinson's team). Reported **separately** from the model's own schema compliance: the runner records raw Ollama responses (`wire/`), `tools/parity/sdk_normalization.py` counts calls whose raw arguments needed this decoding (`SDK_NORMALIZATION.json` per run). The acceptance A2 rate (`acceptance_score.py`) is measured *after* the SDK, as frozen; both numbers are reported side by side for all four models |

Not used: no derived Ollama tag (the PA-2 plan in PARITY_AUDIT §7 is **not** built, per update 1), no lenient parsing,
no few-shot, no constrained decoding, no shared-prompt/catalogue/schema change, no held-out case.

Label for admitted Llama/Granite results: **"adapted (native-schema-v1: transport, with 3 flagged non-vendor
details)"**. For Granite, PA-1's sentence is the same IBM text; the owner exception is no longer needed (update 2).

## 3. Iterations

| # | Model | Change vs native-schema-v1 | Adapter SHA-256 | Scratch runs | Time used | Result |
|---|---|---|---|---|---|---|
| 0 | Llama, Granite | none (frozen as above) | see `RUN_META.json` | none before acceptance (update 1: acceptance first) | — | pending |

Further rows only if the acceptance test fails, inside the time box.
