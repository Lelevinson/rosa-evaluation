# Phase A: parity audit (Qwen, Ministral, Granite, Llama)

2026-11-21. Branch `member/martin-parity` (from tag `freeze-2026-11-21`). **Zero model calls.** No Ollama
generation and no server was started. The only network use was reading public vendor pages and the public
Ollama source at tag `v0.40.6`.

**Lab: unreachable** (`ssh lab-rosa`, port 22 timeout, 2026-11-21). Every item that needs the live lab is marked
**UNKNOWN (lab unreachable)**. The model templates did not need the lab: G1 archived each model's full
`/api/show` output on 2026-11-19 (`SERVER_SHOW.json`), and the digests match the G1 records.

Evidence produced here:
- `tools/parity/rediagnose.py`: a read-only scan of all 304 G1 held-out trial records (76 per model).
- Its output, [REDIAGNOSIS_G1.json](REDIAGNOSIS_G1.json).

## 0. Things that contradict the plan's background (read first)

1. **The native-schema profile in `rosa-research` 8713f9b was never Qwen's.** `tool_contract_ollama.py`
   supports only the `llama3.1` and `granite3.3` families and raises `native_schema_v1_unsupported_model_family`
   for anything else (`NATIVE_GUIDANCE`, lines 12-15 and 36-37). It was written for the 2026-11-17 Llama/Granite
   rerun. In G1, **Qwen used exactly the same adapter as the other three**: the four `local_model.py` files differ
   only in the model-name string (`stage-4-qwen-lab-20261119/local_model.py` vs `backends/*/local_model.py`, line 69).
2. **All three late models have already run in Gazebo** (UR5e, lab, M4's ten families × 4 repetitions, both arms).
   Source: [INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md](../integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md).
   - Ministral, original profile: 28/36 primitives, 28/36 macro.
   - Llama and Granite, original adapter: 0/36 in each arm.
   - Llama and Granite with `native-schema-v1`: Llama 21/36 → 28/36, Granite 5/36 → 9/36.

   These are replications on known M4 cases, not fresh held-out evidence. So "only Sol and Qwen have ever run in
   Gazebo" is not correct.
3. **G1's plain adapter was an owner rule, not an oversight.** The G1 multi-model request
   (`stage-4-multimodel-20261119/provenance/OWNER_REQUEST_ORIGINAL.txt`) says: "No prompt tuning, per-model prompt
   changes, template workarounds … If a model's chat template or tool-call format causes failures, record them as
   results." The G1 zeros and invalid attempts are therefore results of that rule.
4. **G1 serving was already identical for all four models.** Every first request records
   `think: false, stream: true, num_ctx 8192, temperature 0, seed 42, num_predict 1024, use_mmap true`
   (`result.json` → `sanitized_request_records[0].effective_settings`). Qwen got no extra serving setting in G1.
   What Qwen did get is in §2.
5. **The 2026-11-17 `native-schema-v1` profile is not parity-clean under the new rules.** For one model family it
   adds a system message with instructions and schemas. That is "extra instructions for one model only" (§4).

## 1. Per-model record

Wrapper (all four): `MeasuredOllama(ConfiguredChatOllama)`.
- `langchain-ollama` 0.3.10, `ollama` (Python) 0.6.3 and `langchain-core` 0.3.86 on both hosts. Laptop WSL record:
  `chat_models.py` sha `d7f16a67…`. Lab record: `stage-4-qwen-lab-20261119/operator/RUNTIME_ENVIRONMENT.json`
  (versions only; the lab file hash is **UNKNOWN (lab unreachable)**).
- Lab Ollama **0.40.6** (`LAB_INVENTORY.json`), with `OLLAMA_FLASH_ATTENTION=1` and KV cache `f16`.

| | Qwen | Ministral | Granite | Llama |
|---|---|---|---|---|
| Tag | `qwen3.5:9b` | `ministral-3:8b-instruct-2512-q4_K_M` | `granite3.3:8b` | `llama3.1:8b-instruct-q4_K_M` |
| Digest (lab, 2026-11-19) | `56671c2a…3c90` | `1922accd…6b71` | `fd429f23…f1f7` | `46e0c10c…666e` |
| Template SHA-256 (`MODEL_CONFIG.json`) | `{{ .Prompt }}` placeholder (13 B, blob `b507b9c2…`) | `5b74c26b…` | `3da071a0…` | `948af274…` |
| Modelfile directives | `RENDERER qwen3.5`, `PARSER qwen3.5` (config blob `08f9698c…`) | `PARSER ministral`; `PARAMETER temperature 0.15` | none | `PARAMETER stop` ×3 (`<\|start_header_id\|>`, `<\|end_header_id\|>`, `<\|eot_id\|>`) |
| How Ollama formats the prompt | Built-in Go renderer `model/renderers/qwen35.go` | Template: `[AVAILABLE_TOOLS]{{ $.Tools }}[/AVAILABLE_TOOLS]` before the **last user** message | Template: an `available_tools` role block after the system turn, on every request | Template: function list inside the user turn **only if it is the last message** (`if and $.Tools $last`) |
| Native tool-call format | Built-in parser `model/parsers/qwen35.go` | `[TOOL_CALLS]name[ARGS]{…}` via built-in `model/parsers/ministral.go` | `<\|tool_call\|>[{"name":…, "arguments":…}]` (template's ToolCalls section) | `{"name": …, "parameters": {…}}` (template; Meta docs) |
| Ollama parser used (v0.40.6) | built-in | built-in | generic `tools/` parser. The tag `<\|tool_call\|>` comes from the template (`tools/template.go` `parseTag`) | generic `tools/` parser (JSON object) |
| Thinking | capable; `think:false` sent | not capable | not capable | not capable |
| G1 serving (all identical) | 8192 / T 0 / seed 42 / 1024 out / stream true | same | same | same |
| Laptop Ollama | **same digest** `56671c2a…` in `C:\Users\user\.ollama` (manifest on disk, server not started), so the laptop template counts | not installed | not installed | not installed |
| Current lab tags/digests | **UNKNOWN (lab unreachable)** | UNKNOWN | UNKNOWN | UNKNOWN |

How ChatOllama 0.3.10 handles output (`chat_models.py:126-181`, read in the laptop WSL env):
- It reads only Ollama's structured `message.tool_calls`. Text in `content` is never parsed, so tool-shaped prose
  becomes an `AgentFinish` / text reply.
- String-valued arguments are shallowly JSON-decoded into dicts or lists (`_parse_arguments_from_tool_call`; a
  band-aid for ollama#6155). That is the SDK normalization the 2026-11-17 report already discloses.

Ollama's generic parser at `v0.40.6` (commit `2476d5ea`; `tools/tools.go` sha `ffbcb673…`, `tools/template.go`
`ff7b3241…`):
- With a custom tag, it looks for the tag.
- With a `{` tag, it parses only if the **first non-whitespace character** is `{` or `[` (`tools.go:72-80`).
- Arguments are read from `"arguments"`, then `"parameters"` (`tools.go:297-300`).
- There is no handling of markdown fences.

### Vendor documentation opened (2026-11-21)

| Model | URL | What it says |
|---|---|---|
| Granite 3.3 | <https://huggingface.co/ibm-granite/granite-3.3-8b-instruct> (card); <https://huggingface.co/ibm-granite/granite-3.3-8b-instruct/blob/main/tokenizer_config.json> (official chat template) | **The official template, like Ollama's, adds the tool sentence ("respond only with <\|tool_call\|> followed by a JSON list of tools used") only when the caller gives no system message.** Tools go in an `available_tools` block after the system turn. No recommended tool-use settings. ibm.com/granite/docs loaded empty (JavaScript), so it was not read |
| Llama 3.1 | <https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama3_1> (redirect from llama.com); <https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/prompt_format.md> | Format: `{"name": function name, "parameters": …}`; tool results use the `ipython` role. "The tool definition is provided in the user prompt." In Meta's multi-step example, step 3 re-sends the user message **with the function definitions**. "Llama 8B-Instruct can not reliably maintain a conversation alongside tool calling definitions." No settings given. HF `tokenizer_config.json` is gated (HTTP 401), so the official HF template was **not read** |
| Ministral 3 8B 2512 | <https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512>; <https://docs.mistral.ai/capabilities/function_calling/> | "Use a **temperature below 0.1** for daily-driver and production environments" (examples use 0.15). Serving requires the Mistral tool parser. The system prompt should explain the tool environment |
| Qwen3.5 9B | <https://huggingface.co/Qwen/Qwen3.5-9B>; <https://qwen.readthedocs.io/en/latest/framework/function_call.html> (Qwen3 page) | Thinking is on by default; disable it with `enable_thinking: False`. Non-thinking general settings: T 0.7, top_p 0.8, top_k 20, presence_penalty 1.5. Tool parser `qwen3_coder` |
| Ollama | <https://ollama.com/blog/streaming-tool>; source `tools/`, `model/parsers/`, `model/renderers/` at `v0.40.6` | Prefix derived from the template; JSON fallback only at the start of the output; built-in parsers exist for `qwen35`/`ministral`, none for granite/llama |

## 2. What Qwen got that the others did not

1. **Ollama's purpose-built renderer and parser** (`RENDERER/PARSER qwen3.5`, Go code). Ministral has a built-in
   parser. Granite and Llama rely on the generic template parser and on community templates.
2. **Development exposure.** The shared system prompt, user preamble, skill catalogue, tool descriptions and
   schemas were developed and iterated with Sol and Qwen from M1 onward. The late models never shaped them. Parity
   rules forbid per-model changes to these, so **this asymmetry cannot be removed**. It must be disclosed with every
   cross-model result.
3. **Serving:** nothing extra in G1 (§0 item 4). Qwen's earlier serving work (think off, context, timing) set the
   common profile that G1 then applied to everyone.
4. **Thinking control:** only Qwen has thinking capability, and it was sent `think:false`. The others are
   `NOT_APPLICABLE` (`MODEL_CONFIG.json`).

## 3. Re-diagnosis from the G1 trial records ([REDIAGNOSIS_G1.json](REDIAGNOSIS_G1.json))

| | Qwen | Ministral | Granite | Llama |
|---|---:|---:|---:|---:|
| Model outputs | 198 | 237 | 76 | 388 |
| Recognized calls | 185 | 234 | **0** | 383 |
| Outputs without a call | 13 | 3 | **76** | 5 |
| … of these with a code fence | 0 | 0 | **73** | 0 |
| … containing `<\|tool_call\|>` | 0 | 0 | **0** | 0 |
| … with a `"function"` key | 0 | 0 | 64 | 0 |
| Rejected tool responses | 11 | 42 | 0 | **215** |
| … `schema_validation` | 0 | 0 | 0 | **214** |
| … at turn 1 / turn 2+ | 3 / 8 | 0 / 42 | – | **0 / 215** |
| Turn 1→2 prompt **shrank** (pairs) | 0/68 (min +88 tokens) | 0/73 (min +78) | – | **61/76 (median −271)** |

Counting note: rejections come from tool messages in each trial's final transcript. They are not the report's
"invalid attempts" counter (150/135 P/M), which counts differently.

### Granite: never emitted its native format

Example from case 017, macro, turn 1 (`backends/granite/trials/G1r1-heldout-017-macro/result.json`):

> I will now call the select_skill function with the skill_id "arm.cedar".
> ` ```python {"function": "select_skill", "arguments": {"skill_id": "arm.cedar"}} ``` `

Ollama returned `tool_calls: []`, with `done_reason: stop`.

Why:
- ROSA supplies its own system prompt. Granite's template (Ollama and the **official IBM template** alike) then
  drops the sentence telling the model to answer with `<|tool_call|>`. The schemas still arrive in
  `available_tools`.
- With the tag never produced, the generic parser finds nothing.
- The fenced, prose-prefixed JSON also fails the `{`-at-start fallback.
- This is a **prompting/format gap, not a parser defect**: the output was never in Granite's native format.

### Llama: the template drops the schemas after the first tool result

Example from case 017, macro (`backends/llama/trials/G1r1-heldout-017-macro/result.json`):
- Turn 1 `select_skill {"skill_id":"arm.cedar"}` is accepted.
- Turns 2–5 are each `submit_report {"classification":"SUCCESS","observation_id":"obs-118ddb4865ad-1"}`, each
  rejected with `schema_validation`: `status` is missing and `classification` is `extra_forbidden`.
- Input tokens per turn: 1514 → **1323** → 1412 → 1501 → 1590.

Why:
- Ollama's Llama template renders the function list only inside the user message, and only when that message is
  the last one (`if and $.Tools $last`).
- From turn 2 on, the last message is a tool result, so **no tool schema is in the prompt at all**.
- The evidence:
  - the prompt shrinks at turn 2 in 61/76 trials, which never happens for Qwen or Ministral;
  - all 214 schema rejections are at turn 2 or later, none at turn 1;
  - the rejected fields are guesses: `classification` 81×, `checks` 79×, `node` 22× (with `nodes` missing 120×),
    `status` missing 89×.
- Meta's own multi-step example keeps the user message with the definitions in context, so this template is the
  defect.

### Ministral: no transport gap found

- 234/237 outputs are parsed calls, with 0 fenced or prose tool calls and 0 `schema_validation` rejections.
- Its `[AVAILABLE_TOOLS]` block is placed before the fixed last user message, so it persists on every turn.
- G1's temperature 0 satisfies Mistral's "below 0.1".
- Its 42 rejections are semantic (`unknown_observation_reference` 22, `invalid_node_scope` 9, …), not transport.
- Note: Ministral's default system prompt (with its tool-use guidance) is also dropped when ROSA supplies a system
  prompt. Ministral works anyway, so nothing to fix.

## 4. Gap table

| Item | Qwen | Ministral | Granite | Llama |
|---|---|---|---|---|
| Tag and digest recorded | OK | OK | OK | OK |
| Current lab digest unchanged | UNKNOWN (lab) | UNKNOWN (lab) | UNKNOWN (lab) | UNKNOWN (lab) |
| Tool schemas present on every turn | OK | OK | OK | **GAP (L1)** |
| Model told its native call format | OK | OK | **GAP (G1)** | OK |
| Native output parsed by Ollama | OK | OK | GAP (follows G1) | OK |
| LangChain conversion | OK | OK | OK | OK |
| Serving = common profile | OK | OK | OK | OK |
| Vendor-recommended settings compatible | N/A, common T 0 overrides the vendor's 0.7 | OK (T < 0.1) | none documented | none documented |
| Thinking off | OK | N/A | N/A | N/A |
| Shaped the shared prompt/catalogue | yes (asymmetry) | no | no | no |
| Lab Ollama binary and env file hashes | UNKNOWN (lab) | UNKNOWN (lab) | UNKNOWN (lab) | UNKNOWN (lab) |

### Proposed transport fixes and parity justification

**L1 (Llama): ALLOWED.** Build a derived Ollama tag from the **same weights blob** (`667b0c19…`). Its TEMPLATE
keeps Meta's documented user-turn function list in the prompt on every turn, instead of only when the user message
is last.
- Rule: "the correct chat template for the model, including its documented tool-calling format", and "model tag
  changes only if required for correct tool calling; record the digest".
- Prompt text, schemas and descriptions stay byte-identical across models. Only the placement of the
  already-rendered function list changes.
- Open point: the exact Meta placement (first user turn vs. every user turn) comes from Meta's docs only, because
  the official HF template is gated (401). Before Phase B, either Martin's Hugging Face access reads the template,
  or the public `llama-models` chat-format code is read.
- Needs the lab (`ollama create`). New digest to be recorded.

**G1 (Granite): no fix passes the parity rules as written.** I stopped here, as the plan requires.
- Granite's **official** template omits its tool-format sentence whenever the caller supplies a system prompt, so
  a "correct template" fix doesn't restore it.
- The options all hit the NOT ALLOWED list:
  - (a) Append IBM's own sentence to Granite's system message. This is per-model model-visible text, and the
    11-17 `native-schema-v1` did exactly this.
  - (b) Parse fenced or prose JSON with a `"function"` key. That is not Granite's documented native output, so it
    is lenient parsing of non-native output.
  - (c) Constrained decoding. Forbidden.
- Default under the plan: Granite is "**not adaptable under parity rules**". That would be a valid result,
  supported by the evidence above.
- **Martin decides** whether IBM's template sentence counts as part of Granite's "documented tool-calling format".
  If it does, option (a) becomes allowed, and the same rule would apply to Ministral's default tool guidance for
  symmetry.

**Ministral and Qwen: no gap.** They run Phase B's acceptance test unchanged as reference points.

## 5. Left for the lab (UNKNOWN until reachable)

1. Current `/api/tags` and `/api/show` on :11439, to confirm the digests and templates are unchanged since
   2026-11-19 (metadata only).
2. `ollama --version` in the container (0.40.6 expected).
3. The lab env's `langchain_ollama/chat_models.py` SHA-256, to compare with the laptop `d7f16a67…`.
4. Whether a foreign GPU compute process is present. Nothing is assumed.

## 7. Owner decisions and the Llama template source (2026-11-21)

| # | Decision | Owner |
|---|---|---|
| PA-1 | **Granite: option B.** Restore IBM's own tool-format sentence for Granite. Martin's justification: **"so we can use the model."** This is an **owner exception** to the NOT ALLOWED item "extra instructions … for one model only". Every Granite result must be labelled "adapted, with owner exception PA-1" | Martin |
| PA-2 | **Llama: build the template fix from Meta's public `llama-models` code**, not from the gated HF template | Martin |

**PA-1 details (to implement in Phase B, not yet written):**
- Text: append IBM's sentence, byte for byte as in the official template (`tokenizer_config.json`, the
  default-system branch), to the end of Granite's system message: "When a tool is required to answer the user's
  query, respond only with <|tool_call|> followed by a JSON list of tools used. If a tool does not exist in the
  provided list of tools, notify the user that you do not have the ability to fulfill the request."
- Nothing else changes: schemas are not duplicated (they are already in `available_tools` on every request), and
  there is no parsing of fenced or prose output.
- This is the Granite half of the 2026-11-17 `native-schema-v1` profile only, without the duplicated schemas.
- **Not extended to other models.** Ministral has no gap (§3), so its dropped default guidance is not restored.
  Qwen is unchanged. This asymmetry is disclosed with PA-1.

**PA-2 source (read 2026-11-21, public, commit `0e0b8c51` of `meta-llama/llama-models`):**
- `models/llama3_1/prompt_format.md` (sha `7f85a2e5…`), section "JSON based tool calling": "Instructions for tools
  added as a user message". The example places the function list in a **user message before the question**,
  inside the conversation, so it stays present on later turns.
- `models/llama3/chat_format.py` (sha `8442f8b7…`) `encode_dialog_prompt` encodes every message in order with
  no special handling. Nothing removes earlier messages.
- Meta's llama.com example (§1) uses the same instruction wording as Ollama's template ("Given the following
  functions, please respond with a JSON for a function call … Respond in the format {"name": function name,
  "parameters": …}. Do not use variables.") and re-sends that user message with the definitions at step 3.

**Conclusion:** Ollama's Llama template has the right wording and the wrong placement. It shows the function list
only when the user message is the **last** message.

**PA-2 fix (Phase B):** a derived tag built from the same weights blob (`667b0c19…`), with one template change.
- The function list is rendered inside the **first** user message on every request, instead of only when the
  user message is last.
- The wording is unchanged, so no new model-visible text is added. ROSA has one user message per task, so this
  matches Meta's step-3 example.
- The digest is recorded at creation. This needs the lab.

## 6. Next phase (not started)

Phase B needs Martin's written OK. The Granite and Llama questions are now decided (§7: PA-1, PA-2).
Phase B steps:
1. Write 12 scratch and 10 acceptance tasks and run the F1 leakage checker on them.
2. Write `tools/parity/adapters/llama.py`, which builds the derived template tag.
3. On the lab: `ollama create` the derived Llama tag.
4. Run the acceptance test for Llama (plus Granite if adaptable), and for Qwen and Ministral as reference.

No command can be given until the lab is back and the task files exist.
