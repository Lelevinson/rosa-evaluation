# PA-1 reclassified as transport (owner, 2026-11-21, after 15:52 Taipei)

Owner (Martin), verbatim: "PA-1: if the Granite sentence is the restored native-format guidance from
native-schema-v1 (rosa-research 8713f9b), quoted verbatim from IBM's documentation, it counts as transport. No owner
exception. Otherwise drop it, and Granite is "not adaptable under parity rules"."

This supersedes the label and the "owner exception" status in `PA1_CONDITIONS_2026-11-21.md` (kept unchanged as history).
All other conditions there still apply (byte-exact text, same in both arms, URL in the adapter log, wire check).

## Check (session B, zero model calls)

| Source | Text length | SHA-256 of the sentence |
|---|---:|---|
| rosa-research `8713f9b205033a25f8ed8d9549610e9ad0b8bfde`, `src/rosa_backends/tool_contract_ollama.py` (blob `69ddcc50`), `NATIVE_GUIDANCE['granite3.3']` | 251 | `7e12d9b58f45f60365ccc471bae05c77809f94d8947408becb8bce85f39e624e` |
| IBM `ibm-granite/granite-3.3-8b-instruct` `tokenizer_config.json` `chat_template`, HF commit `51dd4bc2ade4059a6bd87649d68aa11e4fb2529b` (occurs twice) | 251 | `7e12d9b58f45f60365ccc471bae05c77809f94d8947408becb8bce85f39e624e` |

**Identical.** So the PA-1 sentence is the native-schema-v1 Granite guidance and is verbatim IBM documentation.
**PA-1 = transport. No owner exception.**

## Scope (what counts and what does not)

- Counts as transport: **only** that 251-character sentence, appended to Granite's system message.
- Not included, because it is not IBM text: the rest of native-schema-v1 — the extra system message
  "Available function schemas (retain these after tool results):" with a JSON copy of the schemas, and its forced
  non-streaming transport. The Llama half of native-schema-v1 is also not used (Llama uses PA-2, the template fix).
- If the adapter adds anything else, PA-1 is dropped and Granite is "not adaptable under parity rules".

## Label

Granite, if it passes the frozen acceptance test: **"adapted (transport only: vendor-documented IBM tool sentence)"**.
The labels "with owner exception PA-1" and "adapted (vendor-documented tool prompt, owner exception PA-1)" are retired.
