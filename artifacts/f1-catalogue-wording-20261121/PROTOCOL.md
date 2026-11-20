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

- **Dev:** the 16 frozen G1 dev cases (`cases/dev.json` points to them, with hashes), macro only, **Qwen
  only**. They are used to iterate W1/W2 with at most 2 revisions (`f1-w-r1`, `f1-w-r2`), each logged in
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
3. Freeze (§9).
4. **Stage 1b (held-out):** one attempt per case per arm, with no re-runs. Order: a seeded shuffle of the 30
   cases (seed 20261121). Within a case, the base/new order alternates by template group, so each arm runs
   first in about half the groups. Qwen arms run first, in one exclusive GPU window, then the Sol arms.
5. Censoring follows the G1 V1 rules (`revision-1/stage-3/CENSORING_RULES_V1.md`). Infrastructure-censored
   attempts are reported and never replaced. A pair is excluded from paired statistics if either side is
   censored.
6. Ambiguous cases go to Levinson as a blinded human-review kit (G1 kit pattern:
   `revision-1/stage-3/generate_clarification_kit.py`), with arm labels hidden.

## 6. Predictions (all thresholds are DEFAULTS awaiting owner confirmation)

| ID | Prediction | Measure | Default threshold |
|---|---|---|---|
| P-a | Q-new known-goal passes exceed Q-base | 24 known-goal pairs; discordant net = (new-only) − (base-only) | net ≥ **+3** |
| P-b | Inspection-first selections on movement types drop | first `select_skill` is a `read_only_inspection` skill, over 14 movement_prerequisite + direct_movement cases | Q-new count < Q-base count (Uninformative if Q-base = 0) |
| P-c (guard) | Inspection controls don't get worse | 8 inspection_control pairs | Q-new loses ≤ **1** vs Q-base |
| P-d (guard) | Sol not hurt | S-base − S-new passes **per F1 type** (5 types) | ≤ **1** on every type |
| P-e | Qwen length stops drop | trials with any `finish_reason == "length"`, all 30 | Q-new < Q-base (Uninformative if Q-base = 0) |

P-a's "exceed" is implied by net ≥ +3, because net discordance equals the difference in passes.

## 7. Decision rule

**Adopt W1+W2** only if P-a, P-c and P-d all hold. Otherwise report **"not adopted"**, which is a valid
result. P-b and P-e are mechanism diagnostics; they do not decide adoption. Ambiguous-case outcomes enter P-d
only after the human rating; until then P-d is reported with and without the ambiguous type. Results by F1
type separate W1 (movement types) from W2 (ambiguous).

## 8. Analysis (to be written as `analysis.py`, tested on control rows, then frozen before Stage 1b)

- Paired outcome tables per F1 type and arm pair: both pass, new only, base only, neither.
- Discordant counts with an exact two-sided binomial p (descriptive; no significance claim).
- Whole-template-group bootstrap: resample the 15 groups (12 for known-goal) with replacement, 10,000 draws,
  seed 20261113, giving a percentile 95% interval for the new − base pass-rate difference.
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
| Q dev (16 × base + up to 3 wording revisions) | ≤ 64 | ~128 (cap 512) | in ~4.1k / out ~0.5k per trial | ~17 min |
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
| G1 | Scripted controls C1–C3 on the lab (zero model) | **NOT RUN**: lab unreachable 2026-11-21 (SSH and ping time out). Ready: LAB_PLAN §2 |
| G2 | Owner confirms thresholds (§6) and the code-location deviation | pending |
| G3 | `analysis.py` and the Stage 1 runner written and tested on control rows | pending |
| G4 | Lab readiness check (read-only) and an agreed exclusive GPU window with the other project | pending |
| G5 | **Stage 1a (Qwen dev inference)** | needs authorization |
| G6 | Freeze (§9) | after G5 |
| G7 | **Stage 1b Qwen held-out** | needs authorization |
| G8 | **Sol arms**: uses the existing `siwc` OAuth session. No new OAuth consent is implied | needs authorization |
| G9 | Blinded human ratings of ambiguous cases (Levinson) | after G7/G8 |
