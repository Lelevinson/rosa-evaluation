# Adopted research rules for Martin's Improved ROSA project

Adopted: **2026-11-17**. Owner instruction: "yeah im gonna need you to follow those rules too".

The rules were **provided by teammate Levinson**, through `Lelevinson/rosa-contexts`.
The owner has now explicitly adopted their research discipline for this workspace.
This is a prospective governance update, not a new experiment or a retrospective
claim that every historical study already met every requirement.

## Sources and scope

- [Upstream stable rules, pinned](https://github.com/Lelevinson/rosa-contexts/blob/76481368e1a2abff12147f89bde3bf54620ef3f5/research/RESEARCH_RULES.md)
  ([exact local reference](reference/RESEARCH_RULES.md)).
- [Upstream canonical context, pinned](https://github.com/Lelevinson/rosa-contexts/blob/76481368e1a2abff12147f89bde3bf54620ef3f5/research/ROSA_RESEARCH_CONTEXT.md)
  ([exact local reference](reference/ROSA_RESEARCH_CONTEXT.md)), especially
  sections0-4,12 and14, with applicable provenance/artifact guidance in8 and11.
- Martin's authoritative current context:
  [PROJECT_MASTER_README.md](../../PROJECT_MASTER_README.md).
- The [adoption record](ADOPTION_RECORD.md) distinguishes the standards adopted
  here from teammate-specific context. Exact source bytes and Git blob hashes
  are recorded in [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json).

Apply system/developer instructions and the owner's explicit current decisions.
Resolve a material conflict against actual dated evidence and the current
authorization; document it instead of silently dropping a gate. The teammate's
December2 deadline, Indonesian language preference, private paths, research
ownership and historical authorization/no-go decisions are his context. They
are not new decisions for Martin. His linked local AGENTS.md is deliberately
absent from the shared repository; do not claim to know its contents.

Martin's vision remains practical, experimentally validated improvements to
ROSA's reliability and/or tool-calling efficiency around existing LLM backends.
Engineering and methodological contributions are legitimate when labeled honestly;
a novel named algorithm is not a mandatory deliverable. JTVR and episodic memory
remain optional, subject to evidence and existing project decisions.

## Required research preflight

Before a substantial research recommendation, design, implementation or model
experiment, inspect the current state, relevant source/raw records and the closest
negative study. Write a compact dated decision record answering all five questions:

1. **Closest mechanism and actual difference.** Identify the nearest primary
   literature and strongest ordinary implementation. State the exact policy or
   behavior changed with the same information and capabilities. Describe an
   engineering repair as such; batching, caching, schema naming, a fixed macro or
   fewer model boundaries alone do not establish novelty. A useful incremental
   improvement is sufficient if its additional value is defined and tested.
2. **Observed need and denominators.** Cite the trace/source evidence, affected
   cases and costs, realistic opportunity, missing records, alternative causes
   and counterexamples. A correctness defect alone is not evidence of an
   efficiency opportunity. Separate wrapper calls, physical requests and native work.
3. **Concrete decision and discriminator.** Specify available inputs, state,
   actions, outputs and failure behavior. Give a plausible observable case in
   which candidate and strongest simple control choose differently. Define
   independent user-goal postconditions and complete answer support before costs.
4. **Fair capable controls without an oracle.** Match information, tools,
   permissions, serving settings, task wording, retry rights and budgets; record
   unavoidable differences. Enable and demonstrate applicable batching, reuse,
   concurrency or parameterized tools in the strong reference. Resolve conflicting
   prompt restrictions prospectively. Do not inject scorer answers, privileged
   semantic maps or uncharged preprocessing into the treatment. Include original
   ROSA and a strong simple reference when claiming an improvement over original
   ROSA; narrower comparisons must name their actual reference and limit claims.
5. **Smallest decision-changing next step.** Explain why retained evidence cannot
   already settle the question and why this does not repeat an earlier loop.
   Define the minimum discriminating work, positive and negative decisions,
   stopping rule, expected resources, durable artifact paths and authorization.

Label a material unresolved requirement **BLOCKED / NOT YET JUSTIFIED** and name
the missing fact. Do not launch major implementation or benchmarking around it.
A bounded diagnostic is appropriate when it can resolve a concrete pivotal
unknown; it still needs an explicit protocol, limits and authorization within the
owner's scope. Routine authorized maintenance and documentation do not require a
new research campaign or repetitive approval request. Do not replace an actionable
small test with endless audits, generic literature rounds or AI-to-AI agreement.

## Evidence, evaluation and costs

- Distinguish inspected primary evidence (**F**), externally reported evidence
  (**R**, with verification limits), inspected literature mechanisms (**L**),
  hypotheses/inferences (**H**) and proposals (**P**). Use these labels in decision
  records where useful; keep ordinary user-facing prose clear. Do not infer
  independent replication, exhaustive review or correctness from elapsed time,
  a confident assistant summary, a long report or agreement between models.
- Screen primary prior art, synonyms and the nearest negative work before claiming
  novelty. Revisit the claim openly if closer work is found. Prior overlap is a
  reason to identify and test the incremental difference, not an automatic veto.
- Freeze hypotheses, tasks, independent postconditions/scorers, conditions,
  prompts, seeds, configurations, budgets, metrics and stop rules before evaluation.
  Separate development from held-out work. Do not tune on held-out failures and
  continue calling subsequent results held-out. Document authorized amendments
  prospectively; preserve earlier revisions and results.
- Evaluate user-goal correctness and answer completeness first. Separate skill
  outcome, selected-goal correctness, accepted report truthfulness and appropriate
  clarification. A tool request, a trace, or a SUCCESS report does not prove the
  intended physical effect or satisfaction of the user's goal.
- Report all scheduled attempts, evaluable denominators, exclusions, uncertainty,
  failed/censored work, exercised faults and missing evidence. Preserve the
  applicable frozen censoring/retry rules. Unknown information is not zero cost,
  and an interrupted attempt is not automatically a wrong model decision.
- Count model requests, input/output tokens, native ROS operations, latency,
  setup/serialization, policy/preprocessing, feedback/retries and side effects.
  Keep all-attempt and matched-success views, measured task and campaign time,
  raw-model behavior and automatic framework assistance distinct. Do not infer
  cross-application generalization or model equivalence from familiar fixtures.
- Keep semantic interpretation with the model when judgment is required. A fixed
  authorized skill catalogue is legitimate scoped engineering; do not present it
  as a general policy that needs no application semantics. Identical observed
  outputs do not establish safe semantic tool substitution.

## Preservation, autonomy and living state

Preserve frozen source, protocols, model/environment configuration, raw requests
and traces, independent scoring, failures, null findings, provenance, hashes and
prior revisions. Keep durable repository-relative evidence and verified backups;
temporary storage or a second copy on the same host is not independent disaster
recovery. Never put credentials in logs, traces, archives or Git. Preserve normal
OAuth security and explicit consent; this adoption grants no new consent.

Continue unstarted cells after an external interruption only after checking
integrity and the existing run's authorization, freeze and cumulative limits.
Keep the pause documented and never silently replay failed/completed cells,
replace censored attempts, reset budgets, start a new stage or weaken a gate.
Existing Martin-specific G1 restrictions and human-review requirements remain.

Inspect tracked and untracked Git changes before handoff/publication. Preserve
other members' branches; no unrequested push, merge, history rewrite, baseline
mutation or physical/production execution. Existing owner authorization remains
valid within its stated scope; do not invent an extra permission flow.

After a material state change update the living master/current summary, retaining
dated immutable evidence and the decision history. Record what changed, what is
newly known versus previously known, remaining doubt, what would overturn the
decision and the next authorized action. Classify directions as exploring,
conditionally retained, rejected for this scope, systems integration only or
empirically supported. Source/documentation updates are not new model experiments.
Coordinate one writer for shared notes. Local edits do not update someone else's
uploaded ChatGPT sources or teammate mirror automatically; synchronize only when
authorized and report which copy is current.

No experiment, runtime change, historical rescore, Git commit/push or publication
is authorized merely by adopting these standards. Existing frozen studies and
their claim limitations remain intact. Do not rewrite them to imply retroactive
compliance; identify any later audit as retrospective.
