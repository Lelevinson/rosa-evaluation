# PA-1 conditions (owner, 2026-11-21 15:47 Taipei)

Owner (Martin), verbatim: "PA-1 stands, conditionally. The Granite sentence must be verbatim from IBM's official
Granite tool-calling template or model card, with the URL recorded in the adapter log. No task- or ROSA-specific
content. Identical in both arms. Label: "adapted (vendor-documented tool prompt, owner exception PA-1)". If the
text isn't verbatim IBM documentation, drop it, and Granite is "not adaptable under parity rules"."

This record adds to `ACCEPTANCE_CRITERIA.md` §6 (which stays unchanged) and closes its open point.

## Verified source (session B, zero model calls)

- URL: <https://huggingface.co/ibm-granite/granite-3.3-8b-instruct/raw/main/tokenizer_config.json>
- Hugging Face `X-Repo-Commit`: `51dd4bc2ade4059a6bd87649d68aa11e4fb2529b`; ETag `1ad83527e5d46456be211e7391ecae541401fda6`;
  file SHA-256 `f65a6a5a911424c85f157c40cfbdf06e025814c755480ba2e998d7fba1178664` (downloaded 2026-11-21).
- In `chat_template`, the default system message for the tools branch is built as
  `system_message + " You are a helpful assistant with access to the following tools. " + <the text below>`.
  The text below occurs **verbatim twice** in the template (tools branch, tools+documents branch).

## The only text PA-1 may add (byte-exact, 251 characters, ASCII, SHA-256 `7e12d9b58f45f60365ccc471bae05c77809f94d8947408becb8bce85f39e624e`)

```
When a tool is required to answer the user's query, respond only with <|tool_call|> followed by a JSON list of tools used. If a tool does not exist in the provided list of tools, notify the user that you do not have the ability to fulfill the request.
```

- Appended to the end of Granite's system message, separated by one space (IBM's template joins with a space).
- Contains no task- or ROSA-specific content. Same bytes in primitives and macro.
- The preceding IBM sentence ("You are a helpful assistant with access to the following tools.") is **not** added,
  as fixed in PARITY_AUDIT §7.

## Rules for session A

- The adapter log (`PHASE_B_ITERATION_LOG.md`) must record the URL, the commit above and the SHA-256 of the
  inserted text, which must equal `7e12d9b5…624e` (above).
- A wire check must show the text present, unchanged, in every Granite request in both arms, and absent for
  every other model.
- Any other wording, any extra text, or a different text per arm: drop PA-1. Granite is then
  "not adaptable under parity rules".
- Label for every Granite result: **"adapted (vendor-documented tool prompt, owner exception PA-1)"**.
  This replaces the earlier label "adapted, with owner exception PA-1".
- Granite must still pass the frozen acceptance test (ACCEPTANCE_CRITERIA §4). PA-1 does not change the criteria.
