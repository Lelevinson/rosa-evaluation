# Qwen lab execution preparation

Date: **2026-11-19**. Engineering port of the frozen G1 comparison, not a new hypothesis or prompt-tuning campaign.

Owner direction: "Prioritize Qwen on the lab; retain completed Sol results".
The first Sol run and its actual human review remain separate and unchanged.
No Sol replication, catalogue probe, Gazebo/physical action, new OAuth consent
or Git publication is part of this preparation.

## Five-question preflight

1. **Mechanism and difference:** the same bounded-macro versus model-managed
   primitive comparison as G1. Use the frozen public ROSA module, case catalogue,
   prompt contract, pair order, scorer, independent observer and adjudication.
   Only the backend transport, model label, lab paths and related observation
   plumbing change. This is an execution port, not a new algorithm.
2. **Need and denominators:** the completed Sol batch has 73 evaluable passes
   and three retained infrastructure-censored attempts. Earlier M4 Qwen failures,
   output-length failures and the later lab integration results are separate
   evidence; none establishes the outcome of these 76 G1 Qwen attempts. Existing
   Sol results cannot answer the Qwen prediction or be combined with older Qwen
   tasks as if their inputs were matched.
3. **Decision and discriminator:** run the same 38 AI-authored cases, two arms,
   once each, across arm/base inspection depths 1/2/4/6 and existing write/fault/
   ambiguity cases. Model choices remain actual model decisions. Fresh observer
   records score goal correctness independently. No failing trial is replayed.
4. **Fairness:** same tools, permissions, inputs and budgets within Qwen, using
   profile A's exact weights and configured options. Hardware/server differences
   from historical laptop runs and Sol orchestration are explicit. No tuning to
   the now-observed Sol results, automatic semantic routing, model-specific tool
   schema rewrites or prose-to-tool conversion is introduced. The condition-text
   confound and AI authorship remain. No stock-ROSA superiority claim follows.
5. **Smallest next step and bounds:** eight scripted controls on the lab plus
   wire-parameter comparison to the unchanged configured adapter, then an exact
   source/input seal and owner-readable preflight. The new backend scope is 76
   mock attempts, at most 611 charged physical requests including the one
   auxiliary empty-prompt load, and an eight-hour live-backend window. Preserve
   the three-request narrow HTTP 502/503/504 retry reserve and eight-call,
   2,048-observed-output-token, 1,024-local-token-per-call, 360-second per-task
   limits. Aggregate ceilings take precedence if exhausted. New clarification
   answers need actual new human ratings. Final backend launch acknowledgment
   follows review of the preflight under the existing G1 gate.

## Actual serving semantics, without changing them

Configured model: `qwen3.5:9b`, digest
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`,
Q4_K_M, context8192, output1024/call, temperature0, seed42, reasoning=False,
streaming=False, cache=False, use_mmap=True, same configured HTTP timeout180s.
Dynamic remaining output allowances are forwarded with the other options.

The pinned adapter's configured `streaming=False` does **not** mean
`stream=False` in its actual Ollama payload: the unchanged adapter sends
`stream=True`. The first port check incorrectly assumed the latter, stopped
before model requests or scripted trials, and was retained. The corrected
check compares complete wire parameters with the unchanged configured adapter
and records the actual True value. No transport behavior was changed to pass
the check. Claims that transport streaming was off must not be made.

Likewise, `cache=False` disables LangChain response caching; it does not disable
Ollama's prompt cache. The lab server's loaded-model log explicitly reports
prompt caching enabled. This is recorded rather than silently disabled. The
existing lab server has flash attention explicitly enabled and KV cache f16;
the laptop profile described FA as auto/effectively enabled. Record this host
configuration difference, not an identical-server assertion.

## Preflight load, cost and observability

One documented empty-prompt `/api/generate` request loads the model without
evaluating a task prompt or generating output. Its actual response/zero counts,
duration and offload log are preserved in MODEL_LOAD_PREFLIGHT.json. It is
charged as one auxiliary request within the611 total, leaving at most610
charged inference/retry requests. It is not a scored case or evidence of model
correctness. The backend live timer starts at actual launch; this setup time is
reported separately. No hidden inference warmup or successful trial replacement
is allowed. The empty-load API is documented in the
[official Ollama repository](https://github.com/ollama/ollama/blob/main/docs/api.md#load-a-model).

Use the existing project Jazzy container and loopback Ollama endpoint11439.
The existing healthy loopback Phoenix6006 service is a dependency; this port
does not own or stop it. Exact new Qwen-project span identities and tree closure
are checked per trial. Existing model files and repositories are not replaced.
Frozen source files stay unchanged in the isolated snapshot.

On interruption, inspect freeze/counters and all retained local/persisted audits
before unstarted-only resumption. Preserve the original live time origin and
all spent requests, including the auxiliary load. Incomplete/audit-failing
records stop advancement for inspection. No new token, timeout, retry, scorer
or prompt policy is inferred from this host port. A native module change,
digest mismatch, unavailable service, unexplained audit failure or budget/window
exhaustion stops the run.
