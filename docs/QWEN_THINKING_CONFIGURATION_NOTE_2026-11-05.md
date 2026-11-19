# Qwen thinking-mode clarification

Date: **2026-11-05**. Read-only configuration investigation; no model requests,
serving changes or new experiment.

The experiment runner explicitly sets `reasoning=False`. In the installed
langchain-ollama0.3.10 adapter, `_chat_params` maps that value to the Ollama request's
`think` field. The small project subclass only adds the explicit `use_mmap` option;
it does not change that mapping. This is a request for non-thinking generation,
not merely suppression of a UI display or omission from a report.

The setting is recorded in the initial2026-10-20 setup and retained in subsequent
protocols, including M4. The records establish an inherited, fixed serving profile.
They do not establish through an on/off experiment that disabling thinking was
faster on these tasks, more correct, or the best local configuration. The practical
trade-off is extra generated thinking before an answer versus bounded latency
and output allowance; that rationale must not be presented as a measured result.

[Qwen's official model card](https://huggingface.co/Qwen/Qwen3.5-9B) documents both
default thinking behavior and a non-thinking/direct-response mode.
[Ollama's thinking documentation](https://docs.ollama.com/capabilities/thinking)
describes `think=false` as requesting no thinking output when supported. Current
documentation clarifies the control's intent; the inspected installed adapter
establishes the parameter mapping used by the pinned project configuration.

Disabling a dedicated thinking mode does not establish that the model performs
no reasoning. Qwen's stored ordinary response content still contains explicit
task analysis. Nor does enabling thinking guarantee better task selection or
completion. Its behavior and cost were not measured in this study.

The M4 results therefore apply to Qwen3.5:9b Q4_K_M with thinking disabled,
context8192, maximum1024 generated tokens per call within the total task allowance,
temperature0 and seed42. Both primitive and macro Qwen conditions use that same
profile. The within-profile comparison remains meaningful; it does not establish
the best Qwen profile, the same macro effect under thinking, or a reasoning/compute
budget matched to hosted Sol's provider-default generation.

An on/off evaluation would be a separate prospective diagnostic, with generation
settings, accounting, tool handling, tasks and budgets explicitly specified.
It has not been authorized or run. Existing frozen protocols, outputs, scores
and original archives remain unchanged.
