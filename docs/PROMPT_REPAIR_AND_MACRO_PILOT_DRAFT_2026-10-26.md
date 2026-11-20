# Common prompt repair and next gates — draft, not a live protocol freeze

The teammate's rosa-llm package is parked. Preserve the existing Qwen/Ollama and
Sol/OAuth adapters, dependency locks, model profiles and every historical campaign.

## Repair implemented

ROSA._get_prompts prepends generic system instructions requiring discovery tools
that are absent from the bounded registry. load_default_tools=False does not
remove those instructions. Appending another paragraph leaves a contradiction.

BoundedPromptROSA uses the existing prompt-construction seam to replace the
generic system prefix with a common contract for the actual five-tool registry.
It preserves the robot-specific system message and history/user/scratchpad
scaffold. Unexpected registry/layout fails before inference. Default ROSA stays
unchanged; compose this class explicitly with the existing bounded agent.

The new common instructions preserve selection-first ordering, one tool at a
time, known prerequisites, authorized necessary motion, one dispatched write,
no uncertain command replay, fresh observations, validated reporting, uncertainty
handling and all existing budgets. They do not add native work, model retries,
special Qwen hints, goal labels or evaluator answers.

This implementation targets the validated five-tool prototype. It is not a
general semantic checker for arbitrary caller-written robot instructions or
every possible ROSA plugin. Caller-specific safety content is retained and must
also be reviewed for consistency.

## Separate engineering validation

New tests inspect actual model input, common-system equality across conditions,
preserved user goal/history/tool results/robot constraints, selection guard and
legacy behavior. Existing report, macro, workflow and inference regressions run
unchanged. Scripted providers exercise all18 known fixture/condition pairs with
real ROSA and actual local/persisted Phoenix span audits.

These are known development fixtures and synthetic responses. They validate
mechanics and observability; they do not establish improved Qwen/Sol task
performance or constitute the next held-out evaluation. No live model request
or OAuth session is required for this gate.

## Next: focused live repair validation

Before live calls, freeze a separate small engineering protocol using known
failure/recovery cases. A candidate scope is already-home, unavailable
prerequisites and post-write observation recovery across all three conditions
and both backends:18 trials, at most72 inference requests per backend at8/trial.
This is an estimate, not a frozen schedule or launched batch. Record actual
composed system input/hash, independent outcomes, complete trace exports,
resource bounds and all assistance. Separate task failures from engineering
errors; do not keep changing prompts until Qwen passes.

## Then: genuinely fresh macro evaluation

A model-managed primitive reference, simple bounded macro and existing workflow
remain the comparison. Same common corrected instructions and identical
permissions/schemas/reporting/budgets apply. Macro and workflow prompts remain
identical. Freeze new cases, scoring, repeats, counterbalancing, resource caps,
service-interruption classification and meaningful-benefit/reliability criteria
before inference. Do not redefine a failed numerical screen after results.

Six new cases with two repetitions would be72 total trials (36/backend,
at most288 requests/backend at8/trial). Size is provisional. Include already
satisfied goals, authorized selection, missing/freshness problems, actually
attempted ineffective commands, and a meaningful recovery/escalation decision.
Keep model selection, program assistance, goal truth and reporting correctness
distinct. Report tokens, calls, native work and latency with all-attempt costs;
premature failures are not efficiency gains.

Assess a true bounded read-only inspection capability if it can be implemented
with a small explicit task contract and independent scorer. Current skill
sessions accept one selected single-node numeric goal; another pose is not a
second underlying capability. Do not add a general planner or mislabel pose
variants to manufacture multi-skill generalization. Similarly, distinguish
rejected stale evidence references from validated stale sensor-packet detection.

Favor the simplest implementation supported by the new evidence. Keep workflow
as a comparator and do not expand it with planning/routing/caching/memory. JTVR,
episodic memory and physical deployment remain outside this milestone. Gazebo
integration already exists and does not need to be restarted.
