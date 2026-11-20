# ROSA Research — Macro Decision, Evidence Assessment, and Locked Execution Roadmap

**Decision memo and implementation handoff**  
**Date:** 2026-10-27 (Asia/Taipei)  
**Project:** Improving ROSA's reliability and efficiency as an LLM-based robotic agentic framework  
**Current decision:** **Promote the simple bounded macro to the preferred engineering candidate; finish it as a reusable ROSA component.** Keep the custom workflow and primitive execution as preserved comparators.  
**Evidence status:** Promising *observed* efficiency gains, **not** a complete two-backend retention result or proof of generalization/novelty.  
**Instruction for the next work cycle:** **Finish the product, expand a genuine capability, then conduct one final focused evaluation. Do not open another speculative research track.**

> **Use of this document.** This is an assessment and forward plan, not a replacement for the frozen experimental protocols or raw results. The latest quantitative results are taken from the user's supplied **“ROSA fresh macro pilot: final execution report, 2026-10-27.”** Earlier implementation details were checked against the archived `rosa_reliability/macro.py`, `workflow.py`, and `reference.py` snapshots in the prior macro-transfer evidence package. Recommendations below are explicitly distinguished from what the studies demonstrated.

---

## 1. Executive decision — what we are building

We are **not** training a new LLM, replacing ROSA, or attempting to make Qwen match a much larger hosted model at any cost.

We are building a **reusable, bounded skill-execution component within ROSA**:

1. **LLM (Qwen or Sol):** Understands the user's request, chooses an authorized high-level skill when judgment is required, and classifies/escalates unresolved outcomes.
2. **ROSA macro:** Uses deterministic Python/ROS 2 operations to obtain current state, enforce prerequisites, issue at most the authorized operation(s), acquire fresh evidence, and return a structured result.
3. **Independent checker and execution guards:** Verify the actual goal from trusted state and prevent unauthorized, stale-state, or improperly repeated robot actions.
4. **Shared reporting/termination:** Allow the model to cite trusted evidence and end immediately after an accepted terminal report; never infer success solely from a tool accepting a command.

**Recommended default architecture:** LLM selects the meaningful *skill*, while Python manages the predictable *steps inside that skill*. When evidence is missing, the action fails, or a new decision is required, the macro must return control or stop safely rather than inventing facts or retrying uncertain writes.

**Choice of implementation:** The **simple macro** is the leading candidate. The custom state-tracked workflow has not demonstrated enough additional benefit to justify growing it. **Do not delete shared workflow/session code on which the macro currently depends.** In the archived implementation, `MacroSession` inherits from `ReferenceWorkflowSession`, which inherits from `WorkflowSession`; the simpler execution *policy* is implemented in `macro.py` while existing session permissions, evidence, reporting and guards are reused. Preserve those validated shared components during refactoring.

This is a **project architecture and prioritization decision**, not a statistically proven declaration that the macro is globally optimal.

---

## 2. Latest report: what actually happened

### 2.1 Experiment design and completion

The frozen October 26–27 study scheduled:

- **6 new scenario templates × 2 repetitions × 3 execution conditions × 2 models = 72 trials**.
- **Conditions:** model-managed primitive calls; straight-line bounded macro; custom state-tracked workflow.
- **Backends:** local **Qwen3.5 9B**, Ollama Q4_K_M, and hosted **`gpt-6.1-sol`** via the existing OAuth adapter.
- **Environment:** Gazebo UR5e, independent joint-state scorer, controlled sensor/actuation faults, repaired common prompt contract, evidence-reference reporting and terminal behavior.

**Actual execution:** **69 of 72 scheduled trial attempts were recorded.** Sol completed **36/36**; Qwen recorded **33/36** before the frozen backend deadline was exhausted. Qwen's last recorded attempt was interrupted and is an unsuccessful/censored attempt; **three subsequent cells were never started**. Those unstarted cells are the second repetition of `three_constraints` across all three conditions. Do **not** assume their outcomes or silently count them as failures of the model, passes, or completed data.

All **69 recorded attempts passed** the reported local audit, model-input contract check and exact Phoenix span/closed-tree audit. All 12 premodeled deterministic controls passed. Simulator and OAuth teardown completed. **The study's formal two-backend retention decision remains incomplete because of the schedule**, not because a trace audit failed.

### 2.2 Primary results: all attempted trials

A primary pass means the full predefined task contract passed, including correct `SUCCESS`/`FAILURE`/`UNKNOWN` handling and required fault exercise. It is **not equivalent to successful robot movement** in every case.

| Backend | Model-managed primitives | Simple macro | Custom workflow |
|---|---:|---:|---:|
| **Qwen — primary passes / attempts** | **8/11** | **9/11** | **7/11** |
| Qwen — reserved model requests | 61 | **31** | 34 |
| Qwen — known input tokens | 147,006 | **66,162** | 69,394 |
| Qwen — known output tokens* | 10,868 | **6,245** | 7,155 |
| Qwen — native operations | 38 | **36** | 39 |
| Qwen — summed scored trial time | 1,619.09 s | **1,025.18 s** | 1,107.65 s |
| **Sol — primary passes / attempts** | **12/12** | **12/12** | **12/12** |
| Sol — reserved model requests | 60 | **32** | 32 |
| Sol — input tokens | 100,669 | **50,232** | 50,247 |
| Sol — output tokens | 2,028 | **946** | 953 |
| Sol — native operations | **36** | 38 | 38 |
| Sol — summed scored trial time | 311.74 s | 189.83 s | **177.76 s** |

*Qwen token figures are **known lower bounds**, not complete usage totals: six timed-out generations did not return usage metadata. “Reserved requests” count those attempts rather than treating them as free. Summed in-trial seconds do not include simulator setup, reset, teardown, audits, or all campaign overhead. Cross-backend token usage is not directly equalized.*

### 2.3 The strongest evidence in favor of the macro

**For Sol:** All three configurations completed **12/12** tasks. The macro reduced model requests from **60 to 32** (**46.7% fewer**) versus primitive orchestration. Recorded native operations changed from **36 to 38** (**5.6% more**). Summed trial time was **311.74 s → 189.83 s**, an observed **39.1% reduction**; this is not a controlled inference-only speedup claim. The workflow also used **32 calls and 38 native operations**, with a small latency difference, but did **not** meet the predefined screen for incremental advantage over the macro.

**For Qwen:** In the **11 recorded attempts per condition**, the macro obtained **9/11** primary passes versus **8/11** for primitives and **7/11** for the custom workflow. Reserved model requests were **61 → 31** (**49.2% fewer**) compared with primitives. Among **eight paired cases in which both macro and primitives passed**, the macro used **22 versus 40 calls** (**45% fewer**); native operations were **26 versus 24**, respectively. This matched-success subset is informative but does **not** replace all-attempt accounting. The predefined Qwen sufficiency screen did **not** pass because the 12th paired schedule cell was not completed.

**Relative to the custom workflow:** The macro was at least as convincing in the tested cases and is simpler conceptually. On Qwen, the workflow recorded two paired losses versus macro and no paired wins; **one of those losses was censored by the overall backend deadline and must not be described as intrinsic model/workflow incompetence**. On Sol, macro and workflow tied on correctness, requests, and native operations. We have **no demonstrated incremental algorithmic benefit** from the custom workflow's more elaborate state-based orchestration.

### 2.4 What *didn't* improve, and what the report does not prove

- **The 72-trial schedule did not finish.** There is no fully observed formal two-backend retention result. Do not publish 69/72 as a complete 72-trial study.
- **Only one UR5e movement primitive was tested**, albeit with different allowed poses and task constraints. Four poses are not four different robotic skills.
- **Qwen still had nine unsuccessful recorded attempts across its three conditions:** five 180-second trial timeouts; three correct `UNKNOWN` classifications that violated the newly scored observation/retry ceiling; one overall-backend-deadline interruption. Some timed-out cases reached the physical joint goal but failed to complete the required reporting protocol. These are distinct failure modes.
- **No accepted unsupported success, wrong-user-goal success, or unsafe dispatch** was recorded, but such zero counts do not certify physical safety or mean the model never attempted anything invalid.
- **The primitive reference is not untouched upstream ROSA.** It has the same repaired prompt contract, guards, evidence-reference reporting, safety budgets and terminal handling. The claimed comparison is therefore *among controlled ROSA configurations*.
- **A macro is not a novel planning algorithm by itself.** Bundling standard operations explains a large part of the reduced LLM-call count. Existing techniques such as deterministic skill execution, macro-actions and workflow orchestration are relevant prior art.
- **Latency and model differences have confounders:** cold loading, CPU/GPU offload, host load, changing observations, and deadline censoring. Treat the measured times as descriptive.
- **There is no validated collision-avoidance, grasping, perception, or hardware-safety claim.** Joint-state verification observes final poses; it does not establish path safety. Existing mesh-collision warnings remain limitations.

### 2.5 Verdict: is the simple macro the better option?

**Yes, as an engineering choice for the next stage.** The simpler macro delivers nearly all measured call savings of the workflow, matches it on Sol's complete comparisons, and has better observed Qwen outcomes without requiring a more complex orchestration policy. This is sufficient to **prioritize finishing and reusing the macro**.

**No, not yet as a universal scientific claim.** We cannot conclude that the macro is statistically equivalent or superior across robots, environments, task families or model populations. We also cannot claim the macro has already improved broad robot-task reliability. The more modest, defensible finding is that **bounded skill packaging substantially reduced LLM calls in these particular tested ROSA configurations, while the extra custom-workflow complexity showed no demonstrated added value**.

**Decision:** Prefer the macro; archive the custom workflow as a comparator; retain the primitive reference; stop adding new orchestration layers. The next work should turn the candidate into a **finished reusable module**, not immediately rerun another hundreds-of-trials campaign.

---

## 3. How we got here — close research detours instead of reopening them

| Prior direction | What the experiments taught us | Status now |
|---|---|---|
| Local/hosted ROSA integration | Shared tool-level integration can be tested with Qwen and Sol | **Keep: foundation** |
| Independent outcome checks, safety/limits, Phoenix traces | Essential to assess combined-system outcomes honestly | **Keep: non-negotiable infrastructure** |
| Structured feedback, post-action verification, bounded recovery | Useful safeguards; combined intervention lacked convincing independent benefit in small studies | **Preserve findings; no new expansion** |
| Caching, batching, original JTVR | Strong batching matched bounded-lookahead JTVR in the policy study; neither live batching retention screen was met | **Pause full JTVR** |
| Qwen 256/512/1024 token tuning and truncation recovery | More output sometimes allowed arm action, but increased compute; recovery did not show strict end-to-end gain | **Freeze serving profile; no Qwen rescue campaign** |
| Custom hierarchical/state-tracked workflow | Bundling reduced calls; explicit workflow state failed to show benefit beyond a simple macro | **Retain for reference; pause feature growth** |
| **Simple bounded macro** | Retains much of the observed call/cost benefit with a simpler execution policy | **Primary development target** |
| Verified episodic memory | No compelling history-dependent benchmark or justified prerequisite | **Deferred, not required to finish** |
| Gazebo UR5e integration | Works for bounded six-joint trajectory control and independent joint-state checks | **Keep and extend carefully** |

The original six-stage roadmap was a **set of research work packages**, not a contractual requirement to build all proposed mechanisms. Stage 5 memory does **not** need to precede Gazebo and is **not** necessary to finish this project. This decision replaces *implementation priorities*, not historical documentation.

**Scope-lock rule:** A new branch of research requires a concrete blocker to the agreed deliverable, a written hypothesis and a measurable reason the existing macro cannot solve it. A minor Qwen formatting error or a single failed trial is **not** by itself a reason to invent a new module. Engineering defects may be repaired with tests, but they do not automatically become the central research question.

---

## 4. Target architecture and code boundaries

### 4.1 Minimal end-to-end execution contract

```text
User instruction
    |
    v
Qwen / Sol (interpret goal; choose authorized skill or request clarification)
    |
    v
ROSA skill catalogue and simple bounded macro
    |-- Validate permission, arguments, task scope, limits
    |-- Read fresh prerequisite state
    |-- If missing/uncertain: NO WRITE; escalate or report UNKNOWN
    |-- If an allowed action is needed: dispatch bounded operation once
    |-- Check fresh post-action state (command acceptance != success)
    |-- Return evidence, actual outcome, and required next decision
    v
LLM (classify result / choose next meaningful skill / ask user when needed)
    |
    v
Evidence-referenced report -> validated terminal completion
```

**Design principle:** The macro owns routine execution; the model owns semantic judgment. Neither component gets to manufacture observations, bypass permissions, or declare a physical outcome without current evidence.

### 4.2 Existing implementation: preserve what already works

The archived research code already contains these concrete elements:

- `src/rosa_reliability/macro.py` — `MacroSession`, a straight-line read → conditional write → fresh verify execution policy, with no blind replay.
- `src/rosa_reliability/workflow.py` — `WorkflowSession`, the shared skill catalogue/session/ownership scaffolding and the more elaborate `run_workflow` policy.
- `src/rosa_reliability/reference.py` — task-local evidence-reference reporting; exact observed values are supplied by code and checked for freshness, while the model supplies `SUCCESS`/`FAILURE`/`UNKNOWN`.
- `src/rosa_reliability/terminal.py` — deterministic accepted-report termination and trace coordination.
- The bounded prompt adapter, execution guards, transport and evaluator already validated in the subsequent prompt-contract/Gazebo work.

**Important dependency warning:** `MacroSession(ReferenceWorkflowSession)` currently inherits through `WorkflowSession`. **Do not delete `workflow.py` or remove session logic because we have paused the custom workflow experiment.** Refactor carefully if a cleaner shared base class is truly needed; otherwise ship the existing stable inheritance with documentation. Avoid a broad rewrite that destroys evidence comparability.

### 4.3 What “reusable module” should mean

A usable component must be more than an experiment-specific script for four fixed poses. It should provide:

1. **Public skill registration:** a small typed interface for an authorized skill's name, parameter contract, required observations, execution callback(s) and postcondition checker. Keep the catalogue explicit and fail closed for unknown skill IDs.
2. **Transport independence:** do not hard-code Gazebo fixture names, `/ur5e`, `bench_arm`, pose names, injected-fault labels or private evaluator truth into core macro logic. ROS 2 is one adapter; scripted transport is another.
3. **Model independence:** identical skill semantics, safety restrictions and evidence/report shapes whether the caller is Qwen, Sol, or a deterministic test client. Models may require different serving settings; the macro must not use model-specific hacks.
4. **Bounded semantics:** native/tool/model/request/time/correction budgets; one dispatched write under the *current single-skill contract*; no replay after an uncertain/partially applied write. Future multi-step sessions must define a new authorized write budget rather than secretly relaxing this rule.
5. **Truthful outcomes:** distinguish `SUCCESS`, `FAILURE`, `UNKNOWN`, rejected attempt, accepted command, and physically verified goal. Preserve fault provenance without exposing hidden scorer state to the agent.
6. **Current task evidence:** observation IDs scoped to the selected task/skill/session; freshness invalidation after writes; report values copied from trusted records, not from LLM reconstruction; reject stale references or unsupported success claims.
7. **Consistent completion:** accepted terminal report ends the invocation deterministically; rejected reports remain correctable within limits. Never require a useless extra LLM acknowledgment.
8. **Observability:** owner attribution for model/program/native operations, Phoenix-compatible spans, structured events, resource accounting including unknown/censored usage, and deterministic audit-friendly outcomes.
9. **Installability and documentation:** fit the existing `jpl-rosa` Python/`uv` project packaging; expose intentional public imports; provide short API docs, an example and reproducible tests. No breaking change to ordinary upstream/default ROSA behavior.

**Avoid unnecessary abstraction:** Do *not* create a general planner, autonomous task decomposition engine, complex policy optimizer, new evidence database or dependency-heavy routing framework just to make this component reusable. Extract the smallest stable skill interface supported by working code.

### 4.4 Demonstration API (illustrative, not an existing callable contract)

```python
# Illustrative responsibility split only; adapt to existing code.
registry.register(
    skill_id="ur5e.move_to_named_pose",
    parameters_schema=NamedPoseRequest,
    observe=read_current_joint_state,
    authorize=check_skill_permission,
    execute_once=send_bounded_trajectory,
    verify=check_fresh_goal_state,
)

result = bounded_macro.execute(
    skill_id="ur5e.move_to_named_pose",
    arguments={"pose": "inspection"},
    session=session,
)
# result is evidence-backed SUCCESS / FAILURE / UNKNOWN / NEEDS_DECISION,
# not a self-certified completion inferred from command acceptance.
```

This example specifies *desired behavior*, not a request to rename the existing production APIs. Prefer a small adapter around the stable tested `MacroSession` rather than a rewrite.

---

## 5. Locked execution roadmap from here

This is the **one active path**. Milestones are sequential decision gates, not invitations to open parallel research branches.

### M0 — Close and preserve the current experiment **(immediate, low risk)**

**Goal:** Leave the October 26–27 study reproducible, with no ambiguous “72/72 completed” claim.

- Keep the **69 recorded / 72 scheduled**, **33 Qwen recorded / 36 planned**, and **36 Sol / 36 planned** figures unchanged.
- Keep the interrupted Qwen trial and three unstarted cells explicit. Preserve original time/deadline settings, failed primary criteria, raw messages, analyses and Phoenix span evidence.
- Record the architectural choice as **“simple macro preferred for productization; full two-backend research retention not established.”**
- Verify no experiment supervisor, WSL/Gazebo process, or old authorization session needs manual recovery; do not infer current process state from the report alone.
- Create a compact decision note pointing to the frozen protocol, `analysis.json`, `REPORT.md`, and the supplemental October 27 report. Do not overwrite any of them.

**Done when:** The status/limitations can be understood without manually reconstructing old chat messages, and all historical artifacts remain unchanged.

### M1 — Finish the reusable bounded macro module **(NEXT MAIN DEVELOPMENT MILESTONE)**

**Goal:** Produce a documented, importable Python component that executes an authorized robotic skill with fresh verification and bounded failure semantics, independently of the specific LLM.

**Implementation order:**

1. **Inspect current implementation and dependencies.** Map the actual `MacroSession`/`ReferenceWorkflowSession`/`WorkflowSession` inheritance, tool registry, ROS 2 transport and existing test suites. Identify what is already reusable and what is actually hard-coded. Do not refactor speculatively.
2. **Write a short stable interface contract** for skill registration and invocation. Separate model input, program-owned operations, evidence output and independent scoring. Identify what must be kept private from the model.
3. **Refactor only confirmed coupling points**: move experiment-specific skill IDs, pose dictionaries, fault injection, evaluator knowledge and runner-specific settings out of the macro policy when practical. Keep the core read/conditional-write/verify sequencing and guards unchanged.
4. **Make the existing adapter work end-to-end** with a scripted transport *and* the current Gazebo UR5e joint-movement skill. Do not introduce another robot dependency if unnecessary.
5. **Add targeted automated tests**, user-facing examples, installation instructions and concise README. Preserve shared tracing and reporting behavior.
6. **Run the existing regression suite and deterministic Gazebo readiness checks.** Start with *zero-model* tests. Live-model smoke checks only if necessary to verify integration, under a separately recorded bounded test, not as a new research campaign.

**M1 acceptance checklist:**

- [ ] A new consumer can import/register one authorized skill without copying the original experiment runner.
- [ ] The same public macro interface works with scripted transport and UR5e Gazebo transport.
- [ ] At least two distinct authorized skill IDs resolve correctly without hard-coded target selection.
- [ ] Unauthorized or malformed skill arguments are rejected **before** native dispatch.
- [ ] Already-at-goal runs do not issue unnecessary writes but still acquire valid fresh completion evidence.
- [ ] Missing prerequisite observations prevent writes and produce an explicit unresolved/`UNKNOWN` outcome.
- [ ] Ineffective or partially executed commands are not reported as verified success.
- [ ] Any uncertain command receipt cannot cause an automatic retry/replay.
- [ ] Evidence remains task-scoped and fresh; a later write invalidates older applicable observations.
- [ ] Accepted reports terminate normally; rejected reports may be corrected within limits.
- [ ] Resource ceilings and full program/model/native attribution remain intact.
- [ ] Unit/integration/trace regressions pass, and documented installation/example commands work from a clean supported environment.
- [ ] Existing upstream ROSA behavior, historical experiments and frozen hashes remain unchanged.

**M1 deliverables:** importable code in `rosa-research`; focused tests; README/API and one working example; a short integration report including decisions about reuse/refactoring; an evaluation-side validation log under `rosa-evaluation`.

**Stop rule:** Do not keep refactoring for aesthetic reasons. Once the checklist passes, label the module **v0.1 / research prototype** (or another clearly documented internal version) and move forward.

### M2 — Add one genuinely distinct robot capability **(after M1, not during core refactoring)**

**Goal:** Demonstrate that the macro interface isn't merely a wrapper for a fixed joint-pose dictionary.

- First **inventory what the installed simulator actually supports**: UR5e joint trajectory controller, sensors, possible gripper, ROS 2 actions/services, relevant state/limits. Do not assume a gripper, perception model, collision planner or grasping support exists.
- Choose the **smallest safe, bounded second capability** that is genuinely different from `move_to_named_pose`. **Preference if available:** a properly simulated and observed gripper open/close skill with a separate control/verification contract. If that hardware/model is absent or would require extensive installation, propose one feasible independent capability from available ROS 2 interfaces and clearly label whether it is read-only diagnostic/inspection rather than another actuator.
- Give the second skill its own permission, arguments, prerequisites, execution policy, fresh verification and failure/unknown handling.
- Run deterministic tests first, including one deliberately unavailable/failed observation.
- Show that the same macro package supports both skills without adding hard-coded dispatch paths or model-specific exceptions.

**M2 acceptance:** Two distinct capability contracts are demonstrated with independent outcome checks and truthful failure handling. If only one movement primitive remains, say so plainly; **do not relabel two poses or two joint dictionaries as multi-skill robotics**.

**Important technical gate:** The current frozen benchmark allows **one dispatched write per trial**. A genuine sequence involving two actuated skills may require more than one write, so define a *new prospective session-level authorization/budget contract* before attempting it; never silently reuse a one-write evaluation protocol for a multi-write task.

### M3 — Deliver a small multi-skill demonstration **(after two capabilities work)**

**Goal:** Show an actual end-user task with meaningful semantic selection and safe deterministic execution.

- Use one natural-language goal that selects the first skill and another that selects the second, plus one request that requires a reasonable choice, clarification or escalation.
- The LLM may choose a skill, supply authorized arguments, or ask the user; it must not micromanage known controller steps.
- The macro performs bounded operations and returns fresh evidence. The model handles remaining ambiguity, not safety-critical motion math.
- Include ordinary completion, already-satisfied state, unsuccessful execution, unavailable sensor result, and no-unjustified-replay behavior.
- Provide a **reproducible demo script and README**, with a deterministic non-LLM control showing what can be completed without language reasoning.

**M3 acceptance:** Someone unfamiliar with the benchmark can run the demonstration, see what the model actually decided, see what Python executed, and verify the outcome independently. If the procedure is entirely deterministic, acknowledge that plainly rather than pretending the model was indispensable.

### M4 — ONE final focused evaluation **(after the product/demo is stable)**

**Goal:** Test whether finished macro-based ROSA offers a credible efficiency/reliability tradeoff on fresh tasks, especially tasks spanning more than the original pose variant family.

- **Primary comparison:** same model with **model-managed primitives versus bounded macro**, under equivalent permissions, observation/report contracts, safeguards, outcome checker and resource limits.
- **Secondary comparator only if useful:** preserved state-tracked workflow. Do not maintain it as a third actively developed product; include it only if resources justify asking whether its added complexity helps.
- **Non-LLM reference:** deterministic procedure where goals are fully specified; it provides a lower-overhead control, not a fake model competitor.
- **Models:** Qwen and Sol assessed **within-backend** first. Cross-model rankings are secondary; they have different compute/token profiles.
- **Tasks:** independently designed and frozen cases spanning both capabilities, real authorization/selection decisions, satisfied goals, sensor unavailability, injected execution failures and correct escalation. More independent task types matter more than hundreds of near-identical poses.
- **Measures:** verified completion; success-report truthfulness; incorrect/unsafe attempted actions vs blocked dispatches; correct fault exercise; excessive acquisition/retries; task completion vs accepted-report/terminal completion; model calls; known and censored input/output tokens; native sensor/controller operations; end-to-end elapsed time and setup overhead separately.
- **Protocol:** freeze sources, prompts, cases, order, repeats, evaluator and budgets **before** inference. Counterbalance order, record restarts/censoring, prohibit replacing failures, and preserve actual Phoenix traces and independent observations.
- **Size:** choose based on actual diverse task coverage, available model/runtime quota, and the desired uncertainty bound; **do not arbitrarily jump to 144/300 trials**. Run a zero-model infrastructure preflight before the frozen study, but do not start a new iterative pilot/tuning branch.

**M4 acceptance:** A complete, audit-ready comparison with honest estimates and uncertainty, not a predetermined positive outcome. If macro matches primitives or the non-LLM control performs equally well, report it. Do not invent an additional mechanism to force a win.

### M5 — Close the project deliverable **(final consolidation)**

Produce:

1. A maintainable, versioned **Python ROSA macro component** with example skills and documented limits.
2. A working **Gazebo demonstration** that clearly exposes model versus program responsibility.
3. An **experimental report** covering baseline, macro (and optional custom-workflow comparator), verified task success and cost tradeoffs.
4. An **evidence/reproducibility package**: frozen protocols, configuration digests, commands, tests, traces, score summaries, limitations, and negative results.
5. A concise **research conclusion**: what was shown, what was not, how it relates to existing macro-action/robot skill ideas, and when the approach is worth using.

Physical dual-arm deployment is **future work**, not an M5 dependency, unless the professor later supplies a specified platform, permission and suitable control/safety infrastructure.

---

## 6. Immediate next actions for Codex — execute these now

**These are implementation tasks, not another brainstorming request.**

### Action 1 — Inspect, do not modify historical evidence

- Confirm the active repository/branch and clean or explain the working-tree status. The established user branch has been `member/martin`; inspect rather than assuming it remains checked out.
- Locate `macro.py`, `workflow.py`, `reference.py`, `terminal.py`, the bounded prompt contract, Gazebo transport adapters and the test suites.
- Find the latest October 27 report, protocol and `analysis.json` in `rosa-evaluation`. Confirm the study remains closed/incomplete at its original allowance.
- Record exact source revisions/dependencies already used by the current macro. Do not regenerate or overwrite old trial scores.

**Output:** a brief existing-code inventory and “reuse vs changes needed” table.

### Action 2 — Write the *minimal* reusable-module specification

Define the intended public interface, ownership, allowed transitions, evidence contract, safety bounds and transport boundary. State explicitly that the first version supports one selected skill per fresh invocation. Describe how the second capability will plug in without rearchitecting the framework.

**Output:** `docs/MACRO_MODULE_V1_SPEC.md` (suggested filename; place in the research repo's established documentation location).

### Action 3 — Implement the smallest workable packaging and examples

Prefer exporting a stable API or adding a thin adapter to existing tested classes. Remove fixture-coupled pieces only where they genuinely obstruct reuse. Keep the shared reporting, terminal, permissions, resource accounting and tracing paths intact. Add one scripted example and one real ROS 2/Gazebo-backed example; neither needs a new architecture or live LLM benchmark.

**Output:** module code, API entry point, examples and tests in `rosa-research`; validation logs/protocols in `rosa-evaluation`.

### Action 4 — Prove M1 with zero-model checks first

Run the focused test suite and deterministic Gazebo controls. Inspect rejected-command cases, post-write evidence freshness, terminal handling, identical behavior under the two available model adapters, and Phoenix auditing where a real session is used. If a test fails, fix that exact defect and rerun regression checks. Do **not** start another new research mechanism.

**Output:** an M1 acceptance-checklist report that marks each requirement **PASS / FAIL / NOT YET TESTED** with artifact links and specific evidence.

### Action 5 — Stop at the milestone boundary and report the result

Once M1 works, **finish and label the reusable module**. Then select the second capability for M2 based on the real simulator inventory. Do not silently launch the next large live-model campaign. The user wants concrete completed software and a clear next gate, not another series of unrelated experiments.

---

## 7. Guardrails that prevent another cycle of diversions

**Allowed changes:** A focused bug fix necessary for M1's public API, correctness, evidence handling, resource protection, tracing, installation, deterministic Gazebo demonstration or second skill compatibility.

**Not allowed without a new explicit project decision:** Reopening original JTVR, episodic memory, training/fine-tuning a local model, replacing Qwen as a way to hide system failures, adding a dynamic planner, making the custom workflow increasingly elaborate, inventing new cache policies, or launching a large unplanned benchmark.

**Do not conflate these outcomes:**

| Question | Proper evidence |
|---|---|
| Did the LLM choose the correct high-level skill? | Authorized choice compared with the user's independently evaluated goal |
| Was the robot command permitted and well-formed? | Controller/guard validation plus call record |
| Did a tool accept the command? | Dispatch receipt — **not** evidence the goal was reached |
| Did the physical/simulated goal occur? | Fresh independent joint/sensor state |
| Was the report correct? | Submitted classification and task-scoped evidence validated against independent outcome |
| Did the overall task complete? | Verified outcome **and** required accepted report/normal terminal under limits |
| Was it more efficient? | Model requests/tokens **and** native work/latency, including failures and censored attempts |
| Is it a new algorithm? | Mechanistic contribution plus comparison with established skill/macro/workflow techniques; not merely a positive score |

**Escalation rule for unexpected failures:**

1. Preserve the full failure and classify it: environment/setup, model behavior, macro implementation, controller, observer, scoring or accounting.
2. If it blocks the active milestone, make the **smallest justified repair** with regression tests.
3. If it does not block the active milestone, document as a limitation or future task. Do not broaden scope.
4. Never tune prompts, serving settings, cases or success criteria while calling the same frozen study unchanged.

**No performance hype:** Call reductions are a measured benefit in these cases; reliability/generalization and system-level speedups still require appropriate evidence. Model-independent software can compensate for bookkeeping without making the LLM intrinsically smarter.

---

## 8. Working definition of “done”

The current project direction is successfully delivered when **all** of the following are true:

- [ ] **Reusable product:** A separate project can import the ROSA macro component and register a permitted skill without copying a full experimental runner.
- [ ] **Verified behavior:** Permission, fresh-state, execution bounds, uncertain-command handling, postcondition verification, accurate report and terminal checks are tested.
- [ ] **Beyond one pose primitive:** At least one additional genuinely distinct robotic capability is demonstrated, with honest labeling if it is only a read-only skill.
- [ ] **Working simulation:** Gazebo can execute the documented skill demonstration and independent evaluation from a reproducible setup.
- [ ] **Controlled evaluation:** A complete frozen comparison against strong primitives and deterministic references reports verified success, inference use and native costs without rewriting failures.
- [ ] **Research honesty:** The final report explains exactly where simple macro bundling helps, where it does not, and why more complicated workflow machinery was not retained.

We do **not** require Qwen to score 100%, a novel algorithm to emerge, episodic memory to be implemented, a full JTVR system, a new LLM, or hardware deployment to close this undergraduate research milestone.

---

## 9. Codex handoff: instruction to follow after reading this document

> **Adopt this memo as the current implementation priority.** Our next milestone is **M1: finish a reusable, bounded ROSA macro module**. Do not propose a new research branch or automatically start a benchmark. Begin by inspecting the actual current `rosa-research` and `rosa-evaluation` working trees and the preserved October 27 experiment. Map existing `MacroSession` dependencies; reuse tested session, reporting, terminal, permission, trace and resource components. Specify a minimal public skill registration/invocation API, implement only the changes needed for reuse, add clean scripted and Gazebo examples, and run the M1 acceptance tests. Preserve all historical experiment outcomes, including Qwen's incomplete 72-trial schedule and all timeouts. Report your changes, exact PASS/FAIL/NOT TESTED status, and the smallest feasible second robot capability. **Stop after M1 and give a concrete handoff to M2 instead of beginning another exploratory experiment.**

---

## 10. Source and provenance map

**Latest numerical basis (user-provided):** `Pasted markdown(20261027-073338).md`, containing the supplemental **“ROSA fresh macro pilot: final execution report, 2026-10-27.”** Within the user's research workspace that report points to:

- `rosa-evaluation/docs/MACRO_FOCUS_V2_PROTOCOL_2026-10-26.md` — frozen study protocol.
- `rosa-evaluation/artifacts/macro-focus-v2-20261026/analysis.json` — machine-scored analysis.
- `rosa-evaluation/artifacts/macro-focus-v2-20261026/REPORT.md` — original automatic trial report.
- The separate October 27 supplemental interpretation — does not rewrite the protocol or scores.

**Earlier technical implementation evidence:** `ROSA_MACRO_TRANSFER_V1_COMPLETE_WITH_CONTINUATION_2026-10-23.zip`, with snapshotted `rosa-research/src/rosa_reliability/{macro,workflow,reference,terminal}.py`. This earlier archive demonstrates the inheritance/policy arrangement at that snapshot; **Codex must inspect the live repository before treating it as the latest code**.

**Roadmap background:** `PROJECT_ROADMAP_SIX_STAGES.md` (updated 2026-10-21), plus subsequent reliability, UR5e, prompt-contract and macro studies. The old roadmap is historical context; this memo sets the **current prioritized finish plan** without changing that record.

**Confidence boundary:** This document synthesizes supplied reports and archived code. It does **not** independently re-run the latest October 27 live study or verify the newest unpublished working-tree state. Any current status outside the supplied report requires Codex to inspect its own repositories and processes.
