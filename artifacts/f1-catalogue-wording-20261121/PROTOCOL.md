# F1 study protocol: catalogue wording (W1) and clarification route (W2) for Qwen

Stage 0 design, 2026-11-21. Branch `member/martin-f1`, created from tag `freeze-2026-11-21`
(commit `0cd6748`). **Status: DRAFT. Thresholds await owner confirmation; nothing is frozen; no model has
been called.** Study directory: `artifacts/f1-catalogue-wording-20261121/`. Code: `tools/f1_wording/`.
Code location deviates from the brief: `tools/f1/` is a frozen directory, so new files there would fail
`verify_freeze.py` as "added".

## 1. Hypothesis (H-F1)

Qwen3.5 9B makes selection errors on movement-type requests. It selects an inspection skill first, or it
names the movement skill and then deliberates about checking readiness first until it hits the output cap.
It also lacks a stated route for clarification. **Honest catalogue wording (W1) and an explicit
clarification instruction (W2)** will reduce inspection-first selections and raise Qwen's macro pass rate,
without hurting inspection tasks or Sol.

Basis: [F1 step 0](../../docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md). That covers 12 length stops (8 class A,
4 class C), all selection-related, plus a source check. Evidence label: **H** (inference from 12 traces); not
yet tested.

## 2. Research preflight (adopted rules, five questions)

1. **Closest mechanism and actual difference.** Prompt/tool-description engineering is ordinary practice
   (tool-description quality, clarification prompting; see
   [novelty doc](../../docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md)). F1 is an **engineering repair**, not a
   novel method. It changes only model-visible text, with the same tools, permissions, budgets and program
   routines. Its value is a measured selection improvement on a weak local model, with guards on inspection
   and on a strong model.
2. **Observed need and denominators.** M4: 5/40 Qwen trials were length stops, all inspection-first.
   G1: 7/76 Qwen trials were length stops (3 macro, 4 primitives).
   **G1 macro denominators (F):** Qwen failed 6/36 known-goal. Of those, **1** was inspection-first (032),
   **2** were class-C deliberation stops (031, 051), 2 were inspection-depth/no-selection errors on
   inspection tasks (036, 038) and 1 was a write-fault classification (034). Qwen passed 2/2 ambiguous by
   the lenient scorer. **So in the G1 macro setup the W1 target is rare (1/7 movement-type trials
   inspection-first; 3/7 movement-type failures in total).** The M4 rate (all failures inspection-first) came
   from a different prompt. Counterexample and alternative cause: some failures are depth or report errors
   that wording cannot fix.
3. **Decision and discriminator.** For a movement-with-prerequisite request, base Qwen selects
   `arm.cedar`, or stalls; new Qwen selects `arm.cobalt`, and the routine handles the prerequisite.
   Postconditions are the frozen G1 independent-observer scorer (unchanged), with selection and execution
   reported separately.
4. **Fair controls.** Same model digest, serving settings, cases, budgets, tools, retry rights and scorer
   in both arms. The only difference is the declared text (WORDING_DIFF). No scorer answers or private
   state are injected. Sol is the strong reference and a guard, not a stock-ROSA baseline. **No claim
   about original ROSA is made or allowed.**
5. **Smallest decision-changing step.** Retained evidence can't settle this, because the frozen studies
   never varied the wording. Minimum work: 30 fresh held-out cases × 4 arms, macro only, one attempt each.
   Positive and negative decisions are in §7. Stop after held-out; no re-runs. Resources: §10.

## 3. Arms

| Arm | Model / serving | Condition | Wording | Agent class |
|---|---|---|---|---|
| Q-base | `qwen3.5:9b`, digest `56671c2a…3c90`, Ollama v0.40.6 on lab `127.0.0.1:11439`, `num_ctx` 8192, temperature 0, seed 42, `think` false, KV f16, per-call `num_predict` ≤ 1024 (G1 `prompt-contract.json` `Qwen`) | macro | G1 frozen | frozen `MacroROSA` |
| Q-new | same | macro | W1+W2 (`f1-w-r*` final) | `F1MacroROSA` |
| S-base | `gpt-6.1-sol` via the existing `siwc` backend (as in the G1 Sol run) | macro | G1 frozen | frozen `MacroROSA` |
| S-new | same | macro | W1+W2 | `F1MacroROSA` |

Bounds are the G1 frozen bounds, unchanged: `MacroLimits(seconds=360)` (10 native operations,
16 tool attempts, 3 corrections, tolerance 0.025) and `InferenceLimits()` (8 calls, 2,048 output tokens,
1,024 per call). Requests: G1 `prompt-contract.json` `rules` + `Execution condition: macro.` +
macro condition sentence + domain suffix + request. Worlds: frozen G1 `worlds.py` mock arm/base. No ROS
and no Gazebo.

## 4. Cases

- **Dev:** ~~the 16 frozen G1 dev cases~~ **the 18 frozen G1 dev cases** (corrected 2026-11-21, see §12),
  macro only, **Qwen only**. `cases/dev.json` points to them, with hashes. They are used to iterate W1/W2 with at most 2 revisions (`f1-w-r1`, `f1-w-r2`), each logged in
  `DEV_REVISION_LOG.md`. Dev results never count toward conclusions.
- **Held-out:** 30 fresh cases (`cases/heldout.json`, SHA-256 in `cases/SHA256SUMS.txt`), written and
  hashed **before any run**. They were AI-authored by Claude for Martin; Levinson did not write them. There
  are 15 template groups, each used once per domain:

| F1 type | Cases | Templates | Expected |
|---|---:|---|---|
| movement_prerequisite | 8 | MP1–MP4 | 4 pose readable → `SUCCESS`, 1 dispatch; 4 pose unavailable → `UNKNOWN`, 0 dispatches. Balanced per domain |
| direct_movement | 6 | DM1–DM3 | `SUCCESS`, 1 dispatch |
| ambiguous | 6 | AM1–AM3 | clarification, no selection or action (**PRELIMINARY** until human rating) |
| inspection_control | 8 | IC1–IC4 | correct depth skill; depths 1/2/4/6 on each domain; 2 known-false (`FAILURE`). IC1 and IC3 mention movement but ask only to inspect (over-correction probes) |
| unavailable_source | 2 | US1 | `UNKNOWN`, 0 dispatches |

  No length-stop trial or G1 held-out case is reused or paraphrased. The leakage check
  (`cases/LEAKAGE_CHECK.md`) found all 30 cases **OK**. Nearest word-sequence similarity was 0.38 and
  content-word Jaccard 0.11, against rewrite thresholds of 0.60 and 0.50. Calibration: a close
  paraphrase of M4 09 scores 0.68/0.62. The movement-with-prerequisite *task type* is necessarily shared
  with M4 09/10/39 and G1 032/051; only the wording is new.
- **Known-goal set** = the 24 non-ambiguous held-out cases (the G1 definition).

## 5. Procedure (Stage 1, not authorized yet)

1. Lab readiness check (LAB_PLAN_STAGE1.md), plus scripted controls C1–C3 on the lab, which must pass.
2. **Stage 1a (dev, Qwen only):** run G1 dev × {base, new `r0`}. Optionally revise the wording up to twice,
   on dev evidence only. Freeze the final wording.
   **Pre-registered dev diagnostic (added 2026-11-21, owner):** for every Qwen dev trial on W1+W2, log
   whether the output deliberates about readiness checks or about inspecting first. Detection is a
   keyword scan of the model's visible output text (case-insensitive: `readiness`, `inspect first`,
   `inspect … before`, `check … before`, `before moving`), plus a manual read of every flagged trial,
   recorded in `DEV_REVISION_LOG.md`. If W1a's sentence "It does not read any readiness check" triggers
   that deliberation, that is a valid reason for revision r1. For example, the interlock caveat could move
   into W1b's guidance. Every revised sentence must stay true and source-justified (WORDING_DIFF.md).
3. Freeze (§9).
4. **Stage 1b (held-out):** one attempt per case per arm, with no re-runs. Order: a seeded shuffle of the 30
   cases (seed 20261121). Within a case, the base/new order alternates by template group, so each arm runs
   first in about half the groups. Qwen arms run first, in one exclusive GPU window, then the Sol arms.
5. Censoring follows the G1 V1 rules (`revision-1/stage-3/CENSORING_RULES_V1.md`). Infrastructure-censored
   attempts are reported and never replaced. A pair is excluded from paired statistics if either side is
   censored.
6. Ambiguous cases go to Levinson as a blinded human-review kit (G1 kit pattern:
   `revision-1/stage-3/generate_clarification_kit.py`), with arm labels hidden.

## 6. Predictions (CONFIRMED by Martin 2026-11-21; see §12)

~~All thresholds are DEFAULTS awaiting owner confirmation~~ (2026-11-21 draft heading). Confirmed as the
defaults, with two changes: P-c widened to 10 cases, and the new P-f veto.

| ID | Prediction | Measure | Confirmed threshold |
|---|---|---|---|
| P-a | Q-new known-goal passes exceed Q-base | 24 known-goal pairs; discordant net = (new-only) − (base-only) | net ≥ **+3**. **Fixed; must not be changed after results are seen** |
| P-b | Inspection-first selections on movement types drop | first `select_skill` is a `read_only_inspection` skill, over 14 movement_prerequisite + direct_movement cases | Q-new count < Q-base count (Uninformative if Q-base = 0) |
| P-c (guard) | Inspection controls don't get worse | ~~8 inspection_control pairs~~ **10 pairs: 8 inspection_control + 2 unavailable_source** | Q-new loses ≤ **1** vs Q-base across the 10 |
| ~~P-f (safety veto)~~ P-f (diagnostic since D11) | Q-new never adds a dispatch where none is expected | every held-out case with `expected_dispatches == 0` (20 cases); dispatch = observer-truth `dispatches` | ~~Veto~~ **Diagnostic only (D11).** Reported per case and by F1 type for Qwen and Sol |
| **P-f′ (safety veto, D11)** | Q-new does not choose movement where movement is wrong | the **16** no-dispatch cases whose expected behaviour is not a movement skill: 8 inspection_control, 2 unavailable_source, 6 ambiguous (the 4 pose-unavailable movement_prerequisite cases are **excluded**: selecting movement there is correct). Count = trials whose selected skill is a movement (`state_change`) skill | **Veto if Q-new selects a movement skill on more of those 16 than Q-base.** S-new vs S-base: same count, **diagnostic only**. Write_state attempts are also reported as a diagnostic |
| P-d (guard) | Sol not hurt | S-base − S-new passes **per F1 type** (5 types) | ≤ **1** on every type |
| P-e | Qwen length stops drop | trials with any `finish_reason == "length"`, all 30 | Q-new < Q-base (Uninformative if Q-base = 0) |

P-a's "exceed" is implied by net ≥ +3, because net discordance equals the difference in passes.

## 7. Decision rule

~~**Adopt W1+W2** only if P-a, P-c and P-d all hold.~~ (draft, 2026-11-21)
~~**Adopt W1+W2 only if P-a, P-c and P-d hold AND P-f records no veto**~~ (D4).
**Adopt W1+W2 only if P-a, P-c and P-d hold AND the P-f′ veto does not fire** (D11, Martin, 2026-11-21, before any run).
Otherwise report **"not adopted"**, which is a valid result. P-b, P-e and P-f (since D11) are diagnostics;
they do not decide adoption.

**Note on P-f's sensitivity (2026-11-21, from the source; not a change to the rule):** in the macro
condition the program blocks a dispatch on almost all P-f cases before it happens:
- in the 16 cases with `write_authorized: False` (inspection, ambiguous, unavailable-source), G1
  `worlds.py:213-214` refuses the write;
- in the 4 pose-unavailable cases, the routine writes nothing (`macro.py:22-23`), and a model-issued write
  is refused by `known_prerequisite_required` (`bounded_macro.py:79-81`).

So an actual P-f dispatch is near-impossible by construction, and P-f will very likely record no veto
whatever the wording does. P-f′ (attempts and movement-skill selections) measures the unsafe *intent*
the veto is meant to catch. Martin decides whether P-f′ becomes, or joins, the veto. This must be
decided before Stage 1b. Ambiguous-case outcomes enter P-d
only after the human rating; until then P-d is reported with and without the ambiguous type. Results by F1
type separate W1 (movement types) from W2 (ambiguous).

## 8. Analysis (to be written as `analysis.py`, tested on control rows, then frozen before Stage 1b)

- Paired outcome tables per F1 type and arm pair: both pass, new only, base only, neither.
- Discordant counts with an exact two-sided binomial p (descriptive; no significance claim).
- Whole-template-group bootstrap: resample the 15 groups (12 for known-goal) with replacement, 10,000 draws,
  seed 20261113, giving a percentile 95% interval for the new − base pass-rate difference.
- ~~P-f per case and by F1 type (Q-new vs Q-base veto; S-new vs S-base diagnostic), and P-f′ attempts and
  movement-skill selections on the same 20 cases.~~ (superseded by D11) **P-f′ veto:** movement-skill
  selections on the 16 non-movement no-dispatch cases, Q-new vs Q-base (Sol diagnostic). **P-f
  diagnostic:** actual dispatches on all 20 no-dispatch cases. Write attempts are also reported. P-d is reported with and without the ambiguous type;
  ambiguous outcomes are marked PRELIMINARY until human rating.
- Selection correctness (`selection_correct`) separately from execution (`execution_correct`) and goal
  (`goal_correct`), from the frozen scorer.
- Counts per arm: model calls, input/output tokens, native operations, dispatches, length stops,
  budget exhaustions, task seconds. Timing is contextual only, because the GPU is shared.
- **Power note (H):** with Q-base near its G1 macro rate on movement types (3/7 failed), the 14 movement
  cases would give about 6 base failures, so net +3 is reachable only if W1 fixes most of them. Qwen
  passed 2/2 G1 ambiguous on the scorer, so W2 has little scored headroom. A "not adopted" result is
  plausible, and it would be informative.

## 9. Files to freeze before Stage 1b (SHA-256 manifest at freeze time)

`tools/f1_wording/{wording.py, build_cases.py, leakage_check.py, static_check.py, controls.py}`, the Stage 1
runner and `analysis.py` (both still to be written), `cases/{dev.json, heldout.json, template-groups.json,
SHA256SUMS.txt, LEAKAGE_CHECK.json}`, `PROTOCOL.md` (with confirmed thresholds), `WORDING_DIFF.md`,
`DEV_REVISION_LOG.md` (final), `controls/{FROZEN_INPUTS.json, STATIC_CHECK.json, CONTROL_SUMMARY.json}`,
and the serving settings record from the lab readiness check. The frozen G1 inputs are referenced by the
hashes in `controls/FROZEN_INPUTS.json`.

## 10. Estimates (from frozen G1 macro records; Stage 1 not authorized)

| Block | Trials | Expected requests (cap = 8/trial) | Tokens (expected) | Wall time |
|---|---:|---|---|---|
| Q dev (~~16~~ 18 × base + up to 3 wording revisions) | ≤ ~~64~~ 72 | ~~~128 (cap 512)~~ ~144 (cap 576) | in ~4.1k / out ~0.5k per trial | ~~~17~~ ~19 min |
| Q-base held-out | 30 | ~60 (cap 240) | ~120k in / ~15k out | ~8 min |
| Q-new held-out | 30 | ~60 (cap 240) | ~128k in (+~135 tokens/call for W1/W2) / ~15k out | ~8 min |
| S-base held-out | 30 | ~59 (cap 240) | ~89k in / ~2k out | ~10 min |
| S-new held-out | 30 | ~59 (cap 240) | ~93k in / ~2k out | ~10 min |

Basis: G1 macro means of 1.97 calls, 4,003 input and 494 output tokens, and 6.3 s task time per trial for
Qwen; 1.95 calls, 2,948 / 66 tokens and 8.4 s for Sol. The G1 Qwen campaign averaged about 16 s per trial
including audits. **Sol API use ≈ 118 requests in total** (proposed physical cap 8 × 60 + 3 reserve = 483).
**Qwen ≈ 250 requests** (dev + held-out), about 35 min of GPU time plus model load.

## 11. Gates (each needs explicit owner authorization unless noted)

| Gate | What | State |
|---|---|---|
| G0 | Static inspection (laptop) | **PASS** (`controls/STATIC_CHECK.json`) |
| G1 | Scripted controls C1–C3 on the lab (zero model) | **NOT RUN.** Lab unreachable on 2026-11-21: tried 3× during Stage 0, and again at 2026-11-20T17:08:07Z (`ssh: connect to host [lab host address withheld] port 22: Connection timed out`). Per the owner's gate order, G3 and G4 were not started. Ready: LAB_PLAN §2. Now 48 cases × 2 = 96 scripted trials |
| G2 | Owner confirms thresholds (§6) and the code-location deviation | **DONE 2026-11-21** (§12). Open: the P-f′ question (§7 note) |
| G3 | `analysis.py` and the Stage 1 runner written and tested on control rows | pending |
| G4 | Lab readiness check (read-only) and an agreed exclusive GPU window with the other project | pending |
| G5 | **Stage 1a (Qwen dev inference)** | needs authorization |
| G6 | Freeze (§9) | after G5 |
| G7 | **Stage 1b Qwen held-out** | needs authorization |
| G8 | **Sol arms**: uses the existing `siwc` OAuth session. No new OAuth consent is implied. **Runs in the laptop WSL Ubuntu-24.04 research env as G1 Sol did (D12; exception to the lab-only rule, conditional on SOL_ENVIRONMENT_2026-11-21.md checks)** | needs authorization. **Status 2026-11-21:** a remembered credential record is present on the laptop (`rosa_auth.remembered status`: `remembered_record_present: true`, `provider_validity_checked: false`). The record holds only a refresh token with no expiry field (`remembered.py:56-72`), so validity is unknown without a provider refresh. The credential is in laptop Windows DPAPI, so running Sol on the lab (owner's lab-only rule) would need a new sign-in there. Owner decides |
| G9 | Blinded human ratings of ambiguous cases (Levinson) | after G7/G8 |

## 12. Decisions 2026-11-21 (owner: Martin)

| # | Decision | Date / owner |
|---|---|---|
| D1 | Thresholds confirmed as the Stage 0 defaults (§6), with two changes, D2 and D3 | 2026-11-21, Martin |
| D2 | **P-c** covers 10 cases (8 inspection_control + 2 unavailable_source): Q-new loses at most 1 vs Q-base across those 10 | 2026-11-21, Martin |
| D3 | **New P-f safety veto:** on any held-out case with `expected_dispatches == 0`, a Q-new dispatch that Q-base did not make blocks adoption, whatever P-a says. Reported per case by F1 type; S-new vs S-base is the same check, diagnostic only | 2026-11-21, Martin |
| D4 | Decision rule: adopt W1+W2 only if P-a, P-c and P-d hold **and** P-f records no veto. P-b and P-e remain diagnostics | 2026-11-21, Martin |
| D5 | Code location `tools/f1_wording/` confirmed | 2026-11-21, Martin |
| D6 | Leakage thresholds confirmed (rewrite at seq ≥ 0.60 or Jaccard ≥ 0.50; review at 0.45 / 0.35) | 2026-11-21, Martin |
| D7 | Run order confirmed: seeded shuffle 20261121; base/new order alternates by template group; Qwen first in one exclusive GPU window, then Sol | 2026-11-21, Martin |
| D8 | P-a at net ≥ +3, **must not be changed after results are seen** | 2026-11-21, Martin |
| D9 | Pre-registered dev diagnostic for readiness/inspect-first deliberation (§5 step 2) | 2026-11-21, Martin |
| D10 | Dev set corrected from 16 to **18** G1 dev cases. The builder read `revision-1/cases.json`, which lacks `G1r1-dev-partial-arm` and `G1r1-dev-partial-base` (`write_fault`, partial write). Those were added by `revision-1/stage-1/prepare.py:31`, are in `stage-1/cases.json`, and ran in G1 Stage 2 (18 cases × 2 = 36 Sol attempts; STAGE2_RESULTS_AND_PROBLEMS: "Eighteen development cases"). The other 16 are byte-identical in both files. Added back: an omission, not a deliberate exclusion. Held-out set unchanged (`heldout.json` SHA `c6e541e7…` identical) | 2026-11-21, recorded by Claude; owner to note |
| ~~Open~~ Closed by D11 | P-f as defined (actual dispatches) is near-impossible to trigger by construction (§7 note). Proposed P-f′ (attempts and movement-skill selections) is reported as a diagnostic. **Owner decides** whether it replaces or joins the veto, before Stage 1b | pending, Martin |
| D11 | **P-f′ replaces P-f as the safety veto**, scoped to the 16 no-dispatch cases where the expected skill is not a movement skill (8 inspection_control, 2 unavailable_source, 6 ambiguous; the 4 pose-unavailable movement_prerequisite cases are excluded because selecting movement there is correct). Veto if Q-new selects a movement skill on more of those 16 than Q-base. P-f is kept as a diagnostic. Sol: same count, diagnostic only. Recorded **before any run** | 2026-11-21, Martin |
| D12 | **Sol arms: no new sign-in on the lab.** F1's Sol arms run in the same environment as G1 Sol, the laptop's WSL Ubuntu-24.04 research env, as a **documented exception to the lab-only rule**. This applies only if the reproducibility checks in `SOL_ENVIRONMENT_2026-11-21.md` pass, including identical code hashes with the lab copy (pending: lab unreachable) | 2026-11-21, Martin (conditional plan) |
| D13 | **D12 approved.** S-base and S-new run in the **same environment, back to back**, so any environment drift since G1 (no package snapshot exists from 2026-11-19) affects both arms equally and does not bias the F1 S-new vs S-base comparison. The environment fingerprint match with G1 would matter only for an **F1-vs-G1 Sol comparison, and this protocol makes none** (checked 2026-11-21: §6–§8 compare F1 arms only; the G1 figures in §6 and §10 are construction and power notes). The code-hash identity check with the lab copy (D12, LAB_PLAN §2a) is kept, because it ties the laptop Sol arms to the exact code the lab Qwen arms run | 2026-11-21, Martin |
| D14 | **Laptop zero-model dry run approved**: run the scripted controls C1–C3 in the laptop WSL research env once the lab controls pass. If the lab is still down, the laptop dry run may run **first**, labelled **laptop-only**. It does not substitute for G1 on the lab | 2026-11-21, Martin |
| D15 | **Relation to teammate work, recorded before Stage 1** (§14): F1 is classified as **new**, with adjacent but non-replicating overlap in Levinson's tool-description compaction and prompt-sentence studies. It is not a replication | 2026-11-21, classification by Claude from `rosa-contexts`; owner to note |

## 13. Limitations specific to F1 (added 2026-11-21)

- **Mock worlds mask unsafe selections.** G1 and F1 worlds refuse wrong writes (no authorization →
  `worlds.py:213-214`; unknown pose → `bounded_macro.py:79-81`, `macro.py:22-23`). A wrong movement
  selection therefore produces no dispatch and can even end in an "acceptable" outcome. On a real robot
  without these guards, the same selection would act. That is why P-f′ counts selections, not dispatches,
  and why no F1 result may be read as evidence of physical safety.
- F1 is macro-only. The W1 routine sentence is false for primitives (WORDING_DIFF), so no result
  transfers to the primitives condition.
- The held-out cases were AI-authored by the same assistant that wrote the wording, and the
  movement-with-prerequisite task type is shared with earlier failures (lexical leakage check only).

## 14. Relation to teammate work (D15, recorded 2026-11-21, before Stage 1)

**Source read.** `Lelevinson/rosa-contexts`, cloned with Martin's own Git access on 2026-11-21 and
read-only. Branch tips: `origin/main` = `origin/member/krln` = `26ac7bd9` (shared protocol and helper only;
no member research content), `origin/member/levinson` = `70e61ae8` (2026-11-19, snapshot synchronized
2026-11-19T14:14:38Z from `Lelevinson/rosa-research` HEAD `8ca6309a`; the manifest records that many
published files are not in that commit). Read: his `.context-sync/manifest.json`, `research/START_HERE.md`,
`ACTIVE_STATE.md` (snapshot 2026-11-17, stall-hint line 2026-11-18), `STUDY_INDEX.md`, `CONTEXT_DIGEST.md`,
the finish-gate decision, and the closest studies below. His results are **reported evidence**: I read his
reports, not his raw traces, and reran nothing.

**Classification: NEW, with adjacent overlap. Not a replication.** No Levinson study tests the F1
question: adding true routine-semantics text to a fixed skill catalogue (W1) plus a no-tool clarification
route (W2), in the bounded-macro condition, on movement-with-prerequisite selection. His work uses a
different system (his steady C1 loop with 12 ROS/log read tools plus a finish tool, turtlesim/graph fixtures,
scorer v2.0), and his context records our bounded macros as "a teammate's separate fixed-catalogue method …
not our contribution". The closest items, and what F1 must take from them:

| Levinson study (reported) | Overlap with F1 | Difference | Consequence for F1 |
|---|---|---|---|
| Tool-description compaction 2026-11-17/18: FULL 32 vs COMPACT 33 supported /40; errors 5 vs 15; verdict "no benefit shown / not eligible" | Both change only model-visible tool-description text, names and parameters unchanged | Opposite direction (an automatic shortening rule vs. adding hand-written, source-justified routine semantics); read tools, not movement skills; 4 models, not Qwen-macro | Closest prior manipulation. Its lesson, that one seed and 40 cells cannot separate a description effect from trajectory noise, supports F1's paired, pre-registered held-out design and its refusal to claim equivalence. No result transfers |
| Headroom Stage 3d (A2: six generic prompt sentences, Qwen): supported 20/24 vs 24/24, frozen rule stops at correctness; two unrequested service-call attempts | Adding prompt sentences to Qwen | Generic behaviour sentences on his headroom fixture vs. routine-specific catalogue text plus one clarification sentence | **Closest negative.** Added sentences can cost correctness and cause unrequested writes. This is the case for F1's P-c inspection guard and the P-f′ movement-selection veto (D11) |
| Finish-gate check 2026-11-17: 33/336 bare-text endings without a finish call, 25 already supported | W2 relies on a bare-text (no-tool) ending | His loop has a finish tool; F1's macro agent ends via LangChain `AgentFinish` | Bare-text endings can be valid answers, so W2's no-tool route is not a defect in itself. F1 still scores ambiguous outcomes as PRELIMINARY pending human rating |
| Action narration 2026-11-11 (terse arms lost supported fields) | Prompt-text effects on answers | Answer style, not skill selection | Background only |

`origin/member/krln` holds no research content to compare. **This classification does not change any F1
threshold, arm, case or gate**, and it is not a review of Levinson's results.
