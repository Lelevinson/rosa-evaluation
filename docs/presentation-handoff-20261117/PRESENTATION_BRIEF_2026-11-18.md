# Three-slide presentation briefing

Prepared **2026-11-17** for **2026-11-18**. The same briefing is embedded in
[the master project record](../../PROJECT_MASTER_README.md).

Use exactly three presentation slides. The speaker notes and attribution rules below
are supporting material, not additional slides.

## Presentation briefing — three slides for 2026-11-18

Prepared **2026-11-17** from the retained evidence described in this master.
Scope: Martin's Improved ROSA project track. The following is suggested slide
wording and supporting notes, not a new research protocol or launch authorization.
Use the short slide text on screen; keep qualifications and extra figures in
speaker notes. Historical M1–M5 delivery, G1 stages and Qwen serving phases are
different numbering systems and must not be combined into one completion count.

### Slide 1 — Project introduction and goal

**Title:** Improving ROSA's robotic task execution

**Suggested slide text:**

- Improve how ROSA uses existing LLMs to execute and verify robot tasks.
- Let the LLM choose a permitted skill; let bounded Python routines handle its predictable execution steps.
- Evaluate correctness and overhead with local Qwen3.5 9B and hosted Sol.

**Speaker notes:** ROSA is an existing LLM-based robotic agent framework. We
improve its surrounding software rather than train a model. A bounded macro
is a registered routine: read prerequisites, make at most one permitted movement
when needed, then check fresh state. A separate read-only routine checks arm
readiness. This implements the project's divide-and-conquer idea through
pre-authored skills. Program logic manages routine substeps; the model still
interprets the request, selects the skill and handles unresolved intent.
It is not a general planner that automatically decomposes every new task.

Our research question is whether this arrangement reduces unnecessary model
interactions and execution overhead while preserving verified task completion.
Helping the tested smaller local model is an interest, not an achieved parity
claim. The intended deliverable is a reusable ROSA component, reproducible
evaluation and a working simulation demonstration. JTVR and verified episodic
memory are optional deferred directions, not required current deliverables.

### Slide 2 — Progress and measured results

**Title:** Working prototype; lower overhead, mixed correctness

**Suggested slide text:**

- Reusable macro module demonstrated on a Gazebo UR5e: named-pose movement and read-only readiness inspection.
- Completed M4: **80 Gazebo trials**, comparing model-managed primitives with macros inside the same repaired ROSA framework.

| Backend | Correct tasks: primitives → macro | Model calls | Mean task time |
|---|---:|---:|---:|
| Hosted Sol | 20/20 → 20/20 | 68 → 38 | 16.42 → 9.73 s |
| Local Qwen3.5 9B | 15/20 → 14/20 | 91 → 53 | 133.49 → 85.18 s |

**Takeaway:** Macros reduced model-call overhead; a general reliability improvement is not established.

**Speaker notes:** The 80 trials are ten task families × two repetitions ×
two conditions × two backends. Every table condition contains 20 trials.
Correctness includes appropriate FAILURE, UNKNOWN or clarification when required;
these are not 80 successful movements. Model-call and mean-time figures include
unsuccessful attempts. Task-loop times exclude the full campaign's setup,
reset and subsequent trace-audit work. Hardware and serving differ by backend,
so these times are observed system performance, not intrinsic model-speed rankings.

Sol used **44.1% fewer calls** and **40.7% less task time**, with unchanged
observed correctness. Qwen used **41.8% fewer calls** and **36.2% less task
time**, while correct tasks fell from 15 to 14. The preset engineering retention
screen passed for Sol and failed for Qwen. These small samples establish neither
statistical equivalence nor a general reliability advantage. Native operations
were Sol **38 → 40** and Qwen **50 → 48**; fewer model calls did not consistently
mean less robot work.

All 80 M4 live trace audits matched 3,290 persisted Phoenix spans. M1–M5 also
delivered the package/install guide, report, claim ledger and simulation video.
The comparison is against primitives with the same shared repairs, not untouched
upstream ROSA. A verified selected skill can still fail the user's actual goal:
wrong skill selection and ambiguous requests remain material limitations.

**Latest progress beyond M4:** exploratory G1 extends the engineering fixtures
to arm/base mock domains and different inspection acquisition depths. Its 36
hosted Sol development attempts finished with **35 preliminary correct outcomes
and one preserved provider-stream interruption**. The failed trial was not rerun.
Among 17 pairs with both arms scored correct, calls were 59 → 32 and native
attempts 40 → 40. These are dev-only selected pairs, not confirmed generalization.
Four clarification transcripts still need uninvolved human review. G1 Qwen live
and held-out model evaluation have not started.

Current Stage 3 engineering controls passed, but a separate GPT-6 Astra scorer
review found **six reachable clarification-classification errors in 41 new
adversarial tests**. These are new constructed counterexamples, not six live
Qwen/Sol failures. The scoring gate is not cleared. Full error-observability
requirements also remain unresolved under the owner's source-unchanged decision.
The experiment is paused before its final freeze, not running a held-out study.
This is the latest evaluation limitation to mention if asked about current work.

### Slide 3 — Future plan

**Title:** Validate the evaluation, then test broader use

**Suggested slide text:**

1. Resolve clarification scoring, obtain independent human review and settle error-observability requirements.
2. After validation and approval, freeze and run the planned held-out comparisons with matched budgets.
3. Consolidate the reusable macro, simulation demo and evidence; retain improvements only where their benefits justify their costs and limitations.

**Speaker notes:** First agree a documented disposition for the substantive
scorer finding. Any separately approved scorer amendment must receive renewed
review; previous scores and failed attempts remain preserved. Obtain actual
uninvolved human ratings for the four G1 clarification transcripts. Decide how
the full metadata requirement is satisfied or explicitly revised while honoring
the current decision to leave protected authentication source unchanged. Neither
a source change nor a methodological waiver is already approved.

Only after those gates pass can the study be frozen, authorization/storage/trace
preflight reviewed and a hosted held-out launch separately authorized. The current
design has 38 held-out-designated AI-authored cases, or 76 trials per backend
across two conditions. Qwen and catalogue-size work require their own later
gates, including reviewed GPU-idle conditions. This is planned work, not an
already launched or completed comparison. The AI-only authorship limitation must
remain visible; no independent case-generalization claim is available.

Keep the existing Gazebo capability and demonstration as completed engineering
assets. Any wider simulation transfer, runtime integration with a teammate or
physical hardware study is a conditional future proposal needing source/contract
checks and a matched protocol. Physical-robot deployment, general planning,
memory and a larger model are not automatic next steps or promised outcomes.
The practical objective remains a smaller, reproducible ROSA improvement with
honestly measured backend-specific trade-offs.

### Attribution and claim rules for the presentation writer

- **Martin's track:** bounded macros, shared ROSA repairs, UR5e movement/inspection,
  the M1–M5 deliverable, M4 comparison, serving diagnostic and G1 preparation/dev work.
- **Teammate-provided context:** Levinson supplied `Lelevinson/rosa-contexts`
  and its published member context. His fixed-loop C1, Forge and add-on studies
  are his track. Do not include 70/80, 55/80, 47/80, fresh 67/80 or his 320-episode
  build as Martin's measured progress. They may be mentioned with explicit teammate
  attribution if team coordination is relevant; they are not needed on these slides.
- **Evidence levels:** deterministic controls test engineering, live dev results
  test the development configuration, adversarial scorer tests expose evaluation
  defects, and neither AI review nor owner feedback substitutes for uninvolved
  human adjudication. G1 uses mock domains; M4 used Gazebo. Keep those environments separate.
- **Supported headline:** a reusable bounded macro reduced LLM orchestration
  overhead in the tested environment, with a favorable Sol result and mixed
  Qwen correctness. Do not claim general parity, novel tool-selection superiority,
  broad reliability gains, full JTVR/memory completion or physical-robot safety.
- **Status precedence:** this dated briefing and the current G1 gate section
  supersede older present-tense plans. The generated M4/M5 snapshot below is
  historical. Linked original reports retain their original dates and definitions.
- This one Markdown supplies the presentation narrative and numeric summaries;
  it does not embed every raw trace. If only the master is uploaded, do not claim
  to have independently opened its local links or reproduced the experiments.

**Presentation-ready summary:** We built and evaluated a bounded ROSA macro
module for robot movement and inspection. It reduced model-call overhead in
our Gazebo comparison, but correctness benefits were backend-dependent. We are
now addressing evaluation weaknesses before broader testing, while preserving
the existing results and keeping teammate research separately attributed.
