# Stage 2 — combined results, problems and limitations

Date: **2026-11-14**. Scope: **G1 Stage 2, hosted Sol development validation only**.

Stage 2 execution and reporting are complete. All **36 scheduled attempts** are accounted for: **35 correct completions and one retained provider interruption**. The ten previously unstarted trials were completed in a separate, documented continuation. The interrupted trial was not rerun or replaced. No Qwen, held-out evaluation or later stage was launched.

This report combines the results and problems from both execution segments. It is a new reporting supplement; the original sealed reports, raw evidence, scores and manifests remain unchanged. It does not combine Stages 0–2.

## What was tested

Eighteen development cases were run in two conditions: model-managed primitive execution and a simple bounded macro. Each trial started with a fresh mock world, agent history and task-local evidence. The two domains were an articulated arm and a delivery base. Cases covered inspection depths of 1, 2, 4 and 6 native acquisitions, movement, unavailable observations, partial execution and ambiguous requests.

Both conditions used the same public tool interface, permissions, independent observer-based scoring and resource safeguards. The model made the live decisions. Scripted turn counts were descriptive comparators, not imposed live execution paths.

The cases were AI-authored. Independent teammate authorship and semantic-novelty review were not obtained. This was an exploratory engineering/dev check of execution, scoring, budgets and observability. **P1–P4 are not adjudicated from these results.** Correct completion includes appropriate FAILURE, UNKNOWN and preliminary clarification responses; it does not mean every trial successfully moved the robot.

## Results: all scheduled attempts

| Measure | Primitives | Macro |
|---|---:|---:|
| Primary correct | 17/18 | 18/18 |
| Charged physical inference attempts | 60 | 34 |
| Known input tokens | 90,425 | 50,552 |
| Known output tokens | 1,783 | 1,108 |
| Trials with incomplete token usage | 1 | 0 |
| Native attempts | 40 | 46 |
| Invalid attempts | 0 | 0 |
| Total measured task time | 194.91 s | 111.35 s |
| Mean task time | 10.83 s | 6.19 s |
| Median task time | 9.88 s | 6.09 s |

The all-attempt differences were **43.33% fewer inference attempts** and **42.87% less measured task time** for macros. These are descriptive observations. The primitive condition includes an interrupted call with unknown token usage, so its token totals are incomplete. Unknown usage is not zero.

Macros performed six more native attempts in this view because the interrupted Base depth-6 primitive trial acquired nothing, whereas its macro counterpart completed six acquisitions. This is not evidence that macros intrinsically require more robot operations.

## Results: 17 pairs in which both conditions completed correctly

This view excludes the entire pair containing the provider interruption; it complements rather than replaces the all-attempt view.

| Measure | Primitives | Macro |
|---|---:|---:|
| Correct trials in this subset | 17/17 | 17/17 |
| Inference attempts | 59 | 32 |
| Input tokens | 90,425 | 47,227 |
| Output tokens | 1,783 | 1,051 |
| Native attempts | 40 | 40 |
| Total measured task time | 192.49 s | 104.84 s |
| Mean task time | 11.32 s | 6.17 s |
| Median task time | 9.96 s | 6.07 s |

In this subset, macros used **45.76% fewer calls**, **47.77% fewer input tokens**, **41.05% fewer output tokens** and **45.53% less measured task time**, with equal native attempts.

Task timing includes local agent construction, instrumentation and evaluator reads. It excludes subsequent persisted-trace audits. The long pause and fresh execution segment limit causal timing interpretation. These figures do not establish general speed, correctness or reliability superiority.

## Execution, fault and trace checks

- All **35 correct completions** matched their scripted turn comparators. The sole count deviation was the interrupted primitive trial: one physical attempt versus three expected calls. No completed path showed extra reads or retries in its turn count.
- All **eight injected-fault trials** exercised the relevant fault. Missing-pose cases in both domains and conditions reported UNKNOWN with zero movement dispatches. Partial-execution cases in both domains and conditions dispatched once and reported FAILURE.
- There were **zero** invalid attempts, dispatch violations, unsupported accepted SUCCESS reports, wrong-goal accepted SUCCESS reports, output-length endings or budget endings.
- All **36 local audits** and **36 persisted Phoenix audits** passed, matching **1,472 spans**.
- The macro/primitive native-acquisition ratio was **1.00** in all seven fully measured domain/depth cells, within the predefined **0.75–1.25** band. The Base depth-6 ratio is undefined because the primitive path was interrupted; that cell is not a completed cost comparison.
- The continuation's integrity receipt verified **98 retained files**, with zero mismatches. It also verified **20 frozen continuation inputs** and **2,940 protected prior files**, with zero mismatches.

## Problems encountered and how they were handled

### 1. Provider-stream interruption; underlying cause unresolved

The original segment finalized 26 attempts: 25 correct completions and the interrupted trial **G1r1-dev-012-primitives**. That trial retained `SafeError(code=error)` before a completed model output, tool execution or native operation.

The existing sanitizer did not retain a provider HTTP status or raw error payload. Consequently, the evidence cannot distinguish quota, service or another provider-side cause. Failed-call token usage is also unknown. It must not be described as a proven quota error, a wrong Sol decision or evidence that macros are more reliable.

The generic error did not qualify for the narrowly defined HTTP 502/503/504 reserve. The batch checkpointed and stopped. Its result, charged request, trace and failed score were preserved. Only the ten unstarted trials were later executed; no failure was silently converted into a successful rerun.

### 2. The original execution window expired during the pause

The original eight-hour window expired at approximately **14:55 on November 14, 2026 (UTC+08:00)**. The owner authorized a new **30-minute continuation window**. The continuation ran approximately **16:46:49–16:50:11** that day, including its final input-integrity check.

It completed ten correct trials using **28 additional requests**. Combined use was **66 original + 28 continuation = 94/291** charged requests. Infrastructure-reserve use remained **0/3**. Cumulative accounting and the prior active-execution allowance were carried forward; the original deadline was not silently reset.

The owner's standing instruction now permits evidence-preserving recovery from external interruptions without repeatedly asking for confirmation. It does not authorize changes to frozen conditions, resets of hard budgets or automatic approval of new OAuth consent.

### 3. One scorer-defect amendment was needed before live inference

The Stage 1 structural scorer treated exact native counts as part of correctness. For live execution, that would incorrectly reject permitted repeated reads even when the requested goal, evidence, permissions and budgets were satisfied. It also risked confusing truthful evidence for a wrong selected skill with fabricated evidence.

The single allowed prospective amendment separated requested-goal correctness from evidence truth, and permitted authorized repeated reads while charging their full cost. Explicit requests forbidding additional acquisitions retained their stricter cap. Null evidence required actual failed acquisition and unavailable provenance rather than a case label alone.

Before live results, the revised scorer replayed all **132 retained Stage 1 controls without changing their primary scores**, alongside negative checks for actor-only truth, stale references, invented values and wrong-skill reporting. Original scores were preserved. No prompts, cases, guards, condition sentences or public modules were changed. **The one permitted amendment cycle is consumed; no additional cycle was used during continuation.**

## Remaining limitations

1. **Dev-only evidence.** Eighteen cases cannot establish broad generalization or support the later predictions. No held-out outcomes were inspected or produced by this run.
2. **No independent case authorship or semantic-novelty review.** AI-generated cases can share design assumptions with the implementation and scorer.
3. **Clarification still needs human review.** Four transcripts passed the frozen preliminary question screen, but independent semantic adjudication was not obtained. Automated acceptance is not independent human validation.
4. **Condition wording remains confounded with execution mode.** Differences cannot be attributed solely to an execution architecture independently of its condition sentence.
5. **Native depth is not model-decision depth.** The current inspection interface can acquire a group of native observations in one tool call. Deeper source acquisition does not automatically create a harder or longer sequence of model decisions. Observed scripted-turn agreement does not establish difficult planning or selection performance.
6. **One incomplete native-cost pair and one unknown-usage call remain.** Both are disclosed rather than imputed. The matched-success view excludes the affected pair and is therefore a selected subset.
7. **Observer separation has a defined scope.** Scoring uses the observer channel rather than actor records, but both operate over the same authoritative mock world. This is not a claim of independent physical sensing or independently authored ground truth.
8. **No backend comparison.** Sol was the only live model in Stage 2. Nothing here establishes Qwen performance, cross-model transfer, Gazebo transfer or superiority to stock ROSA.

## Conclusion and next gate

Stage 2 completed its scheduled dev execution with working live paths, accounting and trace audits, while preserving one unresolved infrastructure interruption. Macros reduced measured orchestration work in the completed paired cases without reducing scored correctness in those pairs. This is useful feasibility evidence, not a demonstrated general reliability improvement.

No additional architecture, prompt tuning or experiment was introduced. Before a later launch, review the separately frozen stage and its authorization/resource gates. Later P2 reporting remains restricted to **Against or Uninformative** at this sample size. A later Qwen run still requires its reviewed GPU-idle gate. No later stage was launched by this closeout, and no Git commit, push or upload was performed.

## Source records

- [Original Stage 2 confirmation, limits and thresholds](stage-2/CONFIRMATION_2026-11-14.md)
- [Prospective scorer amendment](stage-2/SCORER_AMENDMENT_01_2026-11-14.md)
- [Original interrupted-segment report](stage-2/STAGE2_REPORT.md)
- [Combined report with all 36 trial rows](stage-2-continuation-1/COMBINED_STAGE2_REPORT.md)
- [Detailed fault, turn-count and native-cost checks](stage-2-continuation-1/DETAILED_STAGE2_CHECKS.md)
- [Combined machine-readable results](stage-2-continuation-1/combined-analysis.json)
- [Machine-readable detailed checks](stage-2-continuation-1/detailed-checks.json)
- [Continuation integrity receipt](stage-2-continuation-1/manifest-verification.json)
- [Standing interruption policy](stage-2-continuation-1/STANDING_INTERRUPTION_POLICY_2026-11-14.md)
