# Assessment: improving Qwen's task correctness toward the hosted reference

Date: **2026-11-05**. Planning and existing-evidence analysis only. No model
calls, serving changes, runtime implementation or new experiment.

**Goal clarification.** The user wants Qwen performance on par with, or close to,
Sol. The feasible research target to define is verified correctness on a bounded
held-out robotic task suite, with latency, tokens and calls reported separately.
No near-parity threshold or acceptable cost has been frozen. General model parity
or equal speed on the present laptop is not demonstrated or promised. M1–M5 and
their frozen findings remain intact.

## What is promising in Claude's proposal

Making the goal/skill decision easier with concise instructions, meaningful public
descriptions, a small explicit intent representation or separate worked examples
is consistent with this framework-focused project. Any gain belongs to the combined
system. Thinking on/off is also a legitimate serving question, not an established
rescue. A development/held-out split is better than tuning against known M4 failures.
Larger models, training and a separate classification call are not necessary first
steps. There is no evidence for ranking these interventions by actual improvement
in this system yet.

## Corrections to the diagnosis and resource arguments

1. **Execution is not fully solved.** All eleven failed Qwen M4 trials selected
   inspection, but the known partial-command macro runs already attempt the correct
   movement skill on call two. Commitment blocks that request; later reporting or
   generation limits also matter. Better initial selection may help, but the data
   do not establish that every failure has one cause or that a better first turn
   guarantees full-loop success.
2. **The context calculation uses the wrong unit.** Qwen macro input totals average
   5,288.95 tokens per task, summed across multiple requests. They are not a single
   prompt near the 8K window. Exact M4 accounting is:

   | Condition | Calls | Mean input tokens/call | Maximum input tokens/call |
   |---|---:|---:|---:|
   | Qwen primitives | 91 | 2,285.25 | 4,027 |
   | Qwen macro | 53 | 1,995.83 | 3,928 |

   This does not prove future prompts will fit, but it does not support an existing
   near-full-window diagnosis. Added examples, schemas, history and any carried
   thinking must be measured per request.
3. **M4 had no task timeouts.** Five timeout cases belong to an earlier pilot with
   a different 180-second limit; M4 used 360 seconds. Its six error-ending Qwen
   failures comprised five response-length stops and one validation-retry exhaustion.
   Several terminal errors followed an earlier selection/commitment problem.
4. **No extra calls is not no extra cost.** Intent fields, examples and explanations
   add input/output tokens, processing and sometimes context or parser overhead.
5. **Thinking is not inherently incompatible with tools.** The official
   [Ollama tool-calling examples](https://docs.ollama.com/capabilities/tool-calling)
   support thinking and tools with separate fields. Our pinned integration still
   needs verification before a thinking-enabled trial. Installed LangChain maps
   generated usage to Ollama `eval_count`; the actual mode's accounting and
   continuation behavior must be checked rather than treating thinking as free.
6. **Speed parity is not a proven impossibility.** The present macro means are
   85.18 s for Qwen and 9.73 s for Sol. Local offload is a plausible contributor, but
   output length, invalid-attempt corrections and execution paths also differ. Correctness should be
   primary; equal latency should not be promised or ruled out by these aggregates.

## How to interpret the proposed interventions

**Intent-first output:** plausible, not an established best bet. Correctly formatted
JSON can still contain a wrong intent or skill. A short explanation is not proof
of understanding. Prefer public task constraints/targets over a demand for long
reasoning. The existing select_skill accepts skill_id only; generic JSON containing
intent/skill is not automatically a native ROSA tool call. Ollama's
[structured-output format](https://docs.ollama.com/capabilities/structured-outputs)
and the current tool parser are different interfaces. Preserve the native contract
for a first prompt-only development condition, or explicitly implement/validate
an isolated candidate schema before testing it. Do not pass private goal labels
into either version. Measure raw first output, corrections and automatic assistance
separately if the runtime checks intent/skill consistency.

**Worked examples:** reasonable low-complexity candidate. Use examples authored
from development material, never held-out answers or close paraphrases. Measure
their full prompt cost. Separate their effect from the intent instruction before
combining them. Catalogue descriptions should be consistent across conditions;
changing them simultaneously is another intervention to declare.

**Thinking enabled:** untested. Keep it a labeled serving arm if later pursued.
If it receives a larger output/time allowance, provide an appropriate non-thinking
control with that same allowance, or describe the result as a combined mode/resource
configuration comparison. Mode alone does not imply a loss of reproducibility.
The [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-9B) recommends different
sampling profiles by mode; our `temperature=0` profile was not demonstrated optimal.
Changing mode, sampling and allowance together cannot isolate the effect of thinking.
The historical reason for disabling thinking remains an inherited configuration
choice, not a recorded controlled optimization.

**Separate classifier:** defer until cheaper conditions fail. It adds a model
call, a new error boundary and interface work. It does not eliminate interpretation
errors merely by producing three labels. Application constraints from genuine
user inputs are valid; hidden scorer answers are not.

## Recommended experiment shape, if separately approved

- Use a small text-only **development** screen first: unchanged baseline, concise
  goal-first instructions and a separately measured examples condition. A schema
  condition is useful only with validated tool-parser integration. Thinking may
  be a later separate arm. Nothing is ranked by unseen results in advance.
- Split requests before tuning, grouping related scenarios/template descendants
  together. Paraphrases of one M4 template are not new task diversity. Include
  real inspection goals, movement constraints, clarification and conservative
  prerequisite behavior. Do not make success equivalent to choosing movement.
- Choose and freeze the candidate on development results only. Do not run several
  variants on held-out requests and call the winner's score an untouched test.
- Run Qwen baseline, the frozen candidate and a fresh Sol reference on the same
  held-out cases. This answers a combined-system comparison. For a broader
  backend-independent mechanism claim, also evaluate that mechanism on Sol.
- Test full-loop verified outcomes in Gazebo before claiming robotic correctness
  near Sol. Selection-only accuracy is a diagnostic, not task completion.
- Define a numeric correctness target/gap and acceptable overhead before the
  first confirmatory test. With only 40–60 requests before the split, uncertainty
  will be substantial; closeness in observed scores is not proof of population
  equivalence. Preserve failures, matched budgets and independent scoring.

This is a new proposed question, not an unstarted requirement of M5 or an
automatic approval of the earlier M6 reselection proposal. No test protocol,
resource budget or launch is authorized by the quoted recommendations themselves.

Existing evidence: [M4 final results](../artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md),
[Qwen per-call ledgers](../artifacts/macro-m4-20261027/ollama/checkpoint.json),
[exact partial-command excerpts](../artifacts/macro-m5-20261027/external-discussion-20261030/RAW_FOUR_TRIAL_EXCERPTS.md),
[thinking configuration note](QWEN_THINKING_CONFIGURATION_NOTE_2026-11-05.md).
