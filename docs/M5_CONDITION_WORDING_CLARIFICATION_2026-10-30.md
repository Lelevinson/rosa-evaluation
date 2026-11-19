# Follow-up: condition wording and the commitment policy

Date: **2026-10-30**. Documentation clarification only. M6 and the optional probe
remain unstarted and unauthorized.

Claude's final assessment is largely correct. Calling the existing restriction
"unnecessary" would be too strong: it is conservative, and changing it requires
a defined policy for evidence scope, permissions, cumulative budgets and writes.

The first-turn explanation can also be stated more precisely. Qwen used the
same fixed serving configuration: `temperature=0`, `seed=42`, `num_ctx=8192`
and `num_predict=1024`. Within each condition, both saved first inputs are identical;
their first visible content and requested tool name/arguments also match.
Opaque generated tool-call IDs differ and are not behavioral differences.
The only difference in the decoded first-call prompts/schemas across conditions
is the mode-description sentence. First-turn generation precedes tool execution.
The wording is therefore the strongest observed explanation for the first-action
difference, conditional on the recorded serving controls. Invoking generic
"model-generation behavior" does not add a distinct supported explanation here.

The study compares execution mode **together with its mode-specific instruction**.
Its effect on selection cannot be separated from the condition wording. These
records do not isolate a causal interaction between selection and execution
implementation, identify the influential words, or establish generality beyond
this repeated request. Identical repeats support local repeatability, not new
independent task coverage or a universal determinism guarantee.
The observed cost/correctness comparison of the two complete configurations
remains valid within its stated scope; this limits attribution of the effect.

Ollama documents the [seed parameter](https://docs.ollama.com/modelfile) as a
reproducibility control. A [historical llama.cpp CUDA repeatability report](https://github.com/ggml-org/llama.cpp/issues/7228)
illustrates why hardware/runtime reproducibility is a separate matter; it is
not evidence that this issue affected our pinned Ollama run. No such failure
was observed in the four inspected first outputs.

The later code-level restriction is directly observable: both macro runs ask for
park_right on call two, and the shared single-selection rule rejects that change.
One then ends with an accepted readiness SUCCESS; the other stops on response
length. Both primitive outputs already name park_right before their first
rejected read. These are different stages of the trace; a blocked later request
does not explain why the first action differed.

The proposed 2×2 of wording and request type can test first-turn sensitivity using
varied movement and correct-inspection requests. For paired wording comparisons,
hold the catalogue, schemas, permissions and serving settings constant within
each request. If the movement/inspection factor also changes available skills,
its effect is not isolated from that availability difference. Define how to
score premature reads separately from selecting a wrong skill. Use fresh
formulations, and keep ambiguous requests in any later candidate validation.

That simulator-free probe does not vary execution architecture, observe physical
outcomes, test recovery, or demonstrate improved task completion. Repeating an
identical request adds little coverage when outputs already match. It would be
a new post-hoc diagnostic, with its own frozen inputs and limits if authorized.
No simpler instruction has been selected or validated by this review.

Current decision: retain M1–M5, read the existing raw excerpts, and seek a separate
teammate review under the frozen criterion if practical. Do not launch M6 or the
probe. Current Markdown reporting now explicitly distinguishes the mode/wording
limitation from the later commitment restriction. The original PDFs, frozen
sources, trial scores and archives remain unchanged.
