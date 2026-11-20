# Common bounded prompt repair: engineering validation

The opt-in repair removes the shared prompt/tool contradiction in the tested
bounded agent configuration. All48 regression tests and all18 scripted ROSA
fixture/condition executions passed, with actual persisted Phoenix span IDs and
closed trees matching local traces. No live Qwen/Sol request, OAuth session or
dependency change occurred. This is engineering validation, not evidence of
improved live model performance.

## Change and scope

ROSA._get_prompts retains generic discovery/math instructions even when their
tools are disabled. The new BoundedPromptROSA class in
`rosa-research/src/rosa_reliability/prompt_contract.py` replaces only that generic
system prefix for the supported five-tool bounded prototype. It checks the
registered tool set, preserves robot-specific constraints and the original
history/user/tool-result placeholders, and gives every condition the same common
system contract. It adds no model calls, native operations or automatic repairs.

Default ROSA and historical runners remain unchanged. The new agent in
`experiments/prompt_contract_v1/agent.py` explicitly composes the prompt repair
with the existing completion/terminal seams. Execution permissions, one-write
guard, correction/resource budgets, evidence validation and termination are
unchanged. Arbitrary caller-provided robot instructions are preserved, not
semantically certified; this is not a general prompt compiler.

## Checks

- Eight new test methods inspect actual input delivered to a scripted model,
  correct registry/order, preserved user goal/history/tool results/robot safety,
  identical system instructions across conditions, fail-closed registry checks,
  unchanged legacy behavior, and the existing selection guard.
- Forty previous report/macro/workflow/inference regression methods passed.
- Six existing fixtures x primitives/macro/workflow =18 scripted executions;
  every expected outcome, local trace audit and actual Phoenix persistence audit
  passed. The common system prompt digest is identical across all18 executions.
- Historical original/continuation frozen source checks passed before and after.

The provider responses are scripted and the cases are existing development
fixtures. No inference-efficiency or Qwen-reliability claim follows. Failed
historical cases remain unchanged and cannot be relabeled repaired successes.

## Evidence and next gate

Results, test logs, actual model inputs, session evidence, local traces and
persisted Phoenix traces are under
`artifacts/prompt-contract-v1-engineering-20261026`.

Next is a separately frozen, small real-model engineering validation using the
existing backends, then a fresh repeated/counterbalanced held-out macro study.
The scope/budgets in PROMPT_REPAIR_AND_MACRO_PILOT_DRAFT_2026-10-26.md remain a
draft; no live schedule is frozen or launched. The teammate's package migration
is parked and is not a prerequisite. JTVR, memory, general planning and physical
deployment remain outside this milestone.
