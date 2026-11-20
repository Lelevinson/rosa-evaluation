# Llama and Granite integration review

Date: **2026-11-17**. Read-only review of retained evidence, prompted by the owner's question. No new model requests, runtime changes, rescoring or benchmark reruns.

The 0/72 known-goal full-task results apply to the tested configurations. They do not establish that Llama or Granite cannot perform robotic tasks or cannot work with ROSA in other integrations.

## Llama: real tool calls, recurring schema failures

Llama selected the expected skill in 32/36 known-goal cases per condition in the original independent analysis. It returned native calls both in main trials and in the separate simple post-run probe. In `02-move_constrained-r1-macro`, the bounded macro reached the independently observed target, but the model repeatedly submitted `classification: SUCCESS` rather than the required `status`, leaving no accepted report. Primitive runs also repeatedly used `subject` instead of required `nodes`.

The archived first LLM span for that macro trial contains the supplied JSON schemas. `submit_report` requires `status` and `observation_id`; `read_state` requires `nodes`. Thus these fields were present in the model-visible tool definitions. This observation rules out missing field definitions in that inspected request, not every possible interface defect. Repeated errors after feedback show schema adherence/recovery problems in the tested combined system. They do not establish an inherent transport incompatibility.

## Granite: unresolved native-tool integration, with a specific template concern

The saved model metadata advertises `completion` and `tools`. Ollama's official [Granite 3.3 page](https://ollama.com/library/granite3.3) and IBM's official [model card](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct) describe function calling. Granite is not categorically a model without tool support.

In all 80 main trials, Granite returned text rather than recognized native calls; no native operations executed. The separate one-request post-run probe likewise returned JSON text with an empty native `tool_calls` list.

Reviewing `preparation/model-granite3.3_8b.json` inside the original verified raw archive reveals a concrete interaction: the saved template builds its default tool-format instruction only inside the branch where the supplied system message is empty. That default instruction calls for the `<|tool_call|>` marker and a JSON list. ROSA's main request and the post-run probe both supplied custom system messages. Consequently, that default instruction branch was skipped. The separate `available_tools` block still renders; tools were not simply absent from the template.

This is a **plausible contributing setup/prompt-template mismatch, not a tested root cause**. We have not yet compared the same harmless request with and without a custom system prompt, verified raw server requests against adapter responses, or tested a documented model-specific formatting configuration. A parser/server interaction or model instruction-following failure remains possible. Do not claim that restoring this instruction would fix Granite without a prospective diagnostic.

## Procedural limitation and next action

A passing native-tool smoke test should have been a readiness gate before spending Granite's 80 robot-trial slots. The diagnostic was instead performed afterwards. Preserve the campaign as evidence about the tested arrangement, but do not use Granite's zero to rank its intrinsic robotics/reasoning ability. Its faster failure times are not useful task efficiency.

Before another full comparison, establish a small simulator-free compatibility gate: a harmless native call, correct required arguments, and a short follow-up using a fake tool result. Isolate raw Ollama behavior from the ROSA adapter and system-template interaction. For Llama, separately validate the supplied report/read schemas and feedback behavior. Any changed prompt, template, parser or schema acceptance is a new documented configuration; old failures remain unchanged. Do not automatically execute code or JSON prose to rescue the original scores.

This review authorizes no new experiment and resolves none of the G1 gates. The original raw archives, reports and existing delivery ZIPs remain unchanged; they predate this additional review note.
