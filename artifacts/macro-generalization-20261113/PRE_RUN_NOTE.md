# G1 pre-run planning note

Date: **2026-11-13**. Study: **exploratory generalization study G1**.

**No experiment is authorized to launch from this note.** This is the Stage 0
proposal checkpoint. The requested design cannot currently be hosted exactly
through the unchanged public API. Stage 0 is stopped at that compatibility gate;
Stage 1 controls, model development, final experiment freeze and live requests
have not started. The final runnable design, thresholds and ceilings are not
confirmed. This note's SHA-256 is recorded in STAGE0_CHECKPOINT.json and the
planning-package manifest; it is not a retrospective experimental preregistration.

## Protected scope

- Preserve M1-M5, M4's complete artifact tree/freeze, the timing probe, Phase 1
  serving artifacts and Phase 0/1 reports. No rescoring or historical edits.
- All G1 output, including code, stays in this directory. No source edits in
  `src/rosa`, `src/rosa_reliability` or other frozen source files.
- Use SkillRegistry/StateSkill/CapabilityRegistry/InspectionSkill through their
  public API. No subclassing private sessions, monkey-patching, or invisible
  transport operations to manufacture deeper macro paths.
- No Gazebo, real robot, model request, login, credential access, Git commit,
  upload or push in Stage 0. No agent delegation was used.
- All future attempted requests count, including eligible HTTP failures. Preserve
  every failed trial; never silently replace or rerun it.
- Future hosted runs may restore an existing protected grant only. If missing,
  expired without renewal, revoked or scope-invalid, checkpoint and stop. Never
  open a new sign-in flow. The generic remembered_session helper has a login
  fallback on an absent credential; it must not be invoked blindly by G1.
- Every new stage requires the owner's explicit confirmation after its gate.
  Model quota is not inferred from unused slots in an old local request cap.

## Draft design

Two mock domains: a stateful arm and a genuinely different planar mobile base.
Six public-schema skill proposals per domain: four independent-source inspection
bundles of native depths1,2,4,6 and two state-change anchors with p=1,3 prerequisite
reads, one conditional write, one fresh check (nominal depths3,5). Names do not
encode depth. No new natural-language descriptions are added to the catalogue.
Unsupported prerequisite metadata is kept outside the proposed public catalogue
and is explicitly marked unsupported, not smuggled into the schema.

The case proposal contains **32 dev and 64 held-out-designated cases** with
separate template groups. They are drafts, not an approved or validated held-out
benchmark. All cases are **Codex-authored**. Independent teammate authorship was
not obtained; the original one-third independent-author criterion is unmet.
No teammate authorship, blindness or human review is implied. This limits case
selection protection and must remain visible in any eventual study report.

Ten held-out cases per inspection depth (five/domain), twelve write-anchor cases
(three/skill), and twelve non-depth cases (two missing-prerequisite, two ambiguous,
two faults/domain). Dev counts are sixteen ladder, eight write and eight non-depth.
Ambiguity is scored primarily using the frozen M4 clarification criterion and
separately using an inspection-acceptable stakeholder view. It never enters the
depth analysis. Evidence truth, selected-skill attainment and requested-goal
correctness remain distinct.

The draft task call limit is nominal maximum primitive calls+4; native limit is
nominal depth+4; attempts=2*call limit; corrections3; dispatches<=1; time360s.
Qwen uses original A: 8192 context, 1024/call, temperature0, seed42, think=false,
2048 observed output/task, original auto/effective-enabled FA and f16 KV. Unknown
costs are reported as **not recorded**, never estimated from missing usage.

Compare primitives and macro within each model with identical available skills,
permissions, counters and independent scorer. Preserve the exact M4 system
contract, RULES and condition sentences. M4's hard-coded budget/unit suffix
conflicts with the proposed variable budgets and mobile units; no revised suffix
is authorized. The execution-mode/condition-wording confound carries over.

## Required gate order

0. Resolve public-API and prompt/budget conflicts; review draft cases, authorship
   limitation, predictions, thresholds, budgets and ceilings. Confirm before1.
1. Only after confirmation: scripted primitive/macro reference paths for all
   cases, exercised fault controls, separate observer state/transport/records,
   local trace audits and persisted Phoenix span-ID matching. Stop on failure.
2. Only after confirmation: Sol dev, one paired pass, counterbalanced. No prompt,
   guard or condition tuning. At most one documented case/scorer revision cycle.
3. User reviews dev/amendments; freeze all sources/cases/scorers/budgets/thresholds,
   verify hashes and obtain confirmation.
4. User-confirmed held-out paired execution, single run; preflight evidence is
   reviewed before inference. Proposed Sol/Qwen ordering is not scheduled.
5. Separately confirmed first-turn catalogue-size probe, no tool execution,
   3/6/12 skills, original A; resolve one/both condition-sentence factor and
   ambiguity handling first. Qwen can be deferred to a separately recorded lab
   hardware configuration. Three reviewed quiet-GPU samples and offload inventory
   precede any local inference.
6. Apply the frozen Support/Against/Uninformative rules; report all amendments,
   paired outcomes, clustered uncertainty, batching, output/budget endings and
   limits to generalization.

The supplied text omits numbered headers for its later gates. The numbering
above is a proposed interpretation, not evidence those stages were authorized.

Stop on required source changes, unavailable authorization, a ceiling violation,
protected-file hash mismatch or model-digest mismatch. Do not extend limits.
**The required-source-change stop has already been reached for the exact G1
design. No live step follows this checkpoint.**
