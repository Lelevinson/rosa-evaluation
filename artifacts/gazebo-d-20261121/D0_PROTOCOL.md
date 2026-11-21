# Gazebo D: macro vs primitives on fresh UR5e cases, multi-model (D0 protocol)

Date: 2026-11-21. Branch `member/martin-gazebo` (from `freeze-2026-11-21`). Author: Claude Opus 5.5 (AI),
session B (designer), for Martin. **Status: DRAFT, awaiting owner approval (the single manual gate).**
Zero model calls and zero Gazebo runs were made to write it. Nothing in D1/D2 may start before Martin approves.
After approval this file is frozen; later changes are dated amendments in new files.

## 0. Owner decisions and machine

- **D16 (owner, 2026-11-21):** the lab is unavailable until Monday. D runs on the **laptop**: Windows 11 +
  WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB, i7-13650HX. Same model digests and serving settings as G1
  (num_ctx 8192, temperature 0, seed 42, num_predict ≤ 1024 per call, thinking off where applicable).
  No machine mixing inside one comparison. GPU offload is recorded for every trial. Timing is descriptive only.
- Every local model is larger than the free VRAM at 8K context (5.5–6.1 GiB needed, ~5.2 GiB free;
  `parity-integration-20261121/LAPTOP_TARGET_CONFIG.md` §3). Layers will be split between GPU and CPU.
  Results are "laptop, partial offload". They are not comparable to lab G1 speed.
- Sol is hosted (gpt-6.1-sol via ChatSiwc, the existing remembered session in the D12 WSL env, no new consent).
  Orchestration and Gazebo still run on the laptop. All comparisons are within one model (P vs M), so no
  machine is mixed inside a comparison.
- Stock-ROSA arm: **excluded for time** (master task). Recorded as future work (§12).

## 1. Research preflight (ADOPTED_RESEARCH_RULES five questions)

1. **Closest mechanism and difference.** Same as M4: a fixed bounded macro (`select_skill` runs read /
   conditional write / fresh verify) vs the same model managing primitives. This is an engineering
   integration, not a new algorithm. D's addition: fresh cases, three to five backends on one harness, and
   transport-adapted Granite/Llama (Phase B). (L/F: M4 protocol, G1 reports.)
2. **Observed need.** (F) G1 mocks: macro used ~40–46% fewer calls for Sol, Qwen and Ministral on matched
   passes, with native work about equal. (F) M4 Gazebo: Sol 68→38 requests, 20/20 both arms; Qwen 15/20 vs
   14/20 (failed the screen). (F) 2026-11-17 rerun ran Ministral/Granite/Llama in Gazebo on the **M4 cases**
   (not fresh). Open: does the G1 pattern hold on fresh Gazebo cases with real controllers, per model?
   Counterexample to watch: Qwen M4 partial-command losses.
3. **Decision and discriminator.** Inputs/state/actions/outputs are the frozen M4 ones (§3). A case
   discriminates when one arm skips a needed read/verify, or replays, or mis-classifies, and the other does
   not. Postconditions are independent (observer joints within 0.025 rad; readiness facts).
4. **Fair controls.** Same model, prompts, catalogue, tools, permissions, bounds, retry rights and serving in
   both arms. The only difference is who owns routine operations. No oracle: the deterministic reference is a
   zero-model control, not a competitor.
5. **Smallest next step.** One held-out pass (20 cases × 2 arms per model), no reruns. Retained evidence
   can't settle it because M4 cases were seen and G1 was mock-only. Stop rules §9. Resources §8.

## 2. Question and claims

Within each model: on fresh UR5e Gazebo cases, does the macro reduce model calls without lowering
known-goal correctness, and are the G1 predictions (§7) borne out? **No** cross-model ranking, pooled rate,
general reliability claim, or claim of improvement over original ROSA (stock arm excluded).

## 3. Harness, scorer and launch (reused, not changed)

- **Reused unchanged** (all 62 M4 frozen files verified 2026-11-21: 61 byte-identical on disk, the 62nd
  `docs/M4_MACRO_PROTOCOL_2026-10-27.md` identical in git, differing only by CRLF checkout):
  `experiments/macro_m4/{design,scoring,recovery}.py` (registry, `query()`, `LIMITS`, `score()`,
  recovery gate), `experiments/macro_capabilities_v2/{observability,runner,persisted}.py`, rosa-research
  `c0c61a0` sources (`MacroROSA`, `GazeboDemo`, `ArmTransport`, `ArmReadinessTransport`, sim world
  `arm.sdf`, `bridge.yaml`), Phoenix audit. Headless Gazebo Harmonic + ROS 2 Jazzy, UR5e.
- **Study-local wrapper only** (to write in B3, frozen and hashed before D1):
  `experiments/gazebo_d/runner.py`. It imports the modules above unchanged. It copies M4 `run()`'s
  per-trial body verbatim (source hash recorded) into a loop over the D schedule, because M4's `run()`
  takes one backend and starts its own simulator. Differences, all outside the model's view:
  case list and schedule from this study; one Gazebo for the whole stage; per-row model factory;
  `ROS_DOMAIN_ID=231` (M4 used 217); output folder `artifacts/gazebo-d-20261121/runs/<stage>/`;
  per-model request/time ledgers; `/api/ps` offload record for the loaded model; the reset check (§6).
- **Model-visible wording = frozen M4 = frozen G1 wording.** Checked: the G1 `prompt-contract.json`
  rules string equals M4 `RULES` byte for byte, and the G1 condition sentences and limits suffix equal
  M4 `query()`'s. F1's catalogue wording (W1/W2) is **not** used.
- **Backends.** Sol: M4's `ChatSiwc` path. Qwen/Ministral: M4's `ConfiguredChatOllama` constructor with
  the G1 settings (model name is the only change). Granite/Llama: only if admitted by Phase B, with their
  frozen adapter (SHA-256 from Phase B; Llama's derived tag digest recorded). Labels as in Phase B
  ("adapted (transport only)"; Granite "with owner exception PA-1" if used).
- **Bounds = M4 frozen `LIMITS`:** 8 charged model calls/task, 2048 observed output tokens/task,
  1024/call, 10 native operations, 16 tool attempts, 3 corrections, 360 s/trial, 1 movement, joint
  tolerance 0.025 rad; retries only HTTP 502/503/504, 1/logical call, 1 s backoff, 3 reserve/model/stage.
  Request ceiling per model per stage = 8 × trials + 3 (held-out 323, dev 99). Time ceiling 8 h per model
  per stage, and the global deadline (§9).

## 4. Cases (fresh, AI-authored)

Files: [cases/dev.json](cases/dev.json) (6), [cases/heldout.json](cases/heldout.json) (20),
[cases/template-groups.json](cases/template-groups.json), hashes in [cases/SHA256SUMS.txt](cases/SHA256SUMS.txt).
Generator `tools/gazebo_d/build_cases.py` (deterministic). Frozen M4 case schema, so M4 `score()` applies.
Only the frozen M4 registry (home, stage_left, park_right, inspect_readiness) and M4 fault set are used.
Freshness comes from new wording and new start/goal pairs (e.g. home from stage_left, already at
park_right, ineffective return home from park_right).

**Held-out: 10 template groups × 2 cases = the 10 M4 families** (bootstrap unit = group):

| Group | Family | d_type | Cases (start → goal / expected) |
|---|---|---|---|
| G01 | move_constrained | constrained move | home→park_right SUCCESS; stage_left→home SUCCESS |
| G02 | already_satisfied | write | park_right→park_right 0 writes; home→home 0 writes |
| G03 | ineffective_command | write | home→stage_left FAILURE; park_right→home FAILURE |
| G04 | partial_command | write | home→stage_left FAILURE; home→park_right (by description) FAILURE |
| G05 | missing_prerequisite | missing prerequisite | →stage_left UNKNOWN 0 writes; stage_left→home UNKNOWN |
| G06 | inspect_healthy | inspection | SUCCESS ×2 (start home / park_right) |
| G07 | inspect_inactive | inspection | FAILURE ×2 |
| G08 | inspect_missing_controllers | inspection | UNKNOWN ×2 |
| G09 | inspect_missing_joint | inspection | UNKNOWN ×2 |
| G10 | ambiguous_goal | ambiguous | clarification ×2 |

Type mix: 8 inspection, 6 write, 2 constrained move, 2 missing prerequisite, 2 ambiguous; 18 known-goal.

**Dev (6):** constrained move (park_right→stage_left), partial, missing prerequisite, inspect inactive,
inspect missing controllers, ambiguous. Chosen to exercise every reset path (pose reset, controller
deactivate/restore, injected sensor loss) before held-out.

**Leakage** ([cases/LEAKAGE_CHECK.md](cases/LEAKAGE_CHECK.md)): F1 checker reused unchanged; references:
10 M4 requests, 68 F1 reference requests (M4/G1 length-stops, G1 held-out and dev), 30 F1 held-out, and
every other D case. **26/26 OK.** Five first drafts scored REVIEW (max 0.50 seq, vs M4 already_satisfied
and ambiguous) and were reworded before any use. Lexical check only; the family concepts are shared with
M4 by design.

## 5. Arms and models

Arms: primitives and macro (M4 condition text). Models (full set): Sol, Qwen, Ministral; Granite and Llama
only if admitted. Full held-out set = 20 × 2 × 5 = 200 trials; minimum (3 models) = 120.

## 6. Run order, isolation and reset

- Schedule files: [schedule/dev.json](schedule/dev.json) (60 rows full set),
  [schedule/heldout.json](schedule/heldout.json) (200 rows), by `tools/gazebo_d/schedule.py`.
- Held-out case order: `random.Random(20261121).shuffle`. **Models interleaved by case**: every model runs
  both arms of a case before the next case. Model order rotates by one per case. Arm order alternates
  within each template group (10 cases start with primitives, 10 with macro; one of each per group);
  all models use the same arm order for a case. Non-admitted models are dropped at launch, order kept.
  A late stop therefore leaves whole cases for every model.
- Sol shares the Gazebo queue (serialized, one trial at a time). One local model loaded at a time.
- Isolation: `ROS_DOMAIN_ID=231`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, one Gazebo instance, the M4
  gazebo lock, LangChain tracing off.
- **Scripted reset check (every trial; failure stops the stage):** (a) M4 reset: command the case's start
  pose, independent observer confirms all six joints within 0.025 rad (existing M4 check); (b) before the
  task, independent readiness = all true, except `trajectory_controller_active` false right after an
  `inactive` injection; (c) after the task, an `inactive` case's controller restore succeeds and the next
  trial's (b) passes; (d) no movement dispatch recorded outside the task window.

## 7. Predictions (frozen from G1, per model)

Evaluated on held-out V2 (§8); if V3 gives a different status, the status is **Uninformative** (G1 rule).

| ID | Prediction | Support | Against | Uninformative |
|---|---|---|---|---|
| D-P1 | ~40% fewer model calls in macro, on matched successful known-goal pairs: R = 1 − Σcalls_M/Σcalls_P | R ≥ 0.30 | R < 0.15 (0.15–0.30: Partial) | < 5 matched pairs |
| D-P1s | Per-turn structure: macro mostly 2 decision calls; primitives 3 (inspection, already-satisfied, missing prerequisite) or 5 (off-target move) | descriptive only, per family medians vs this table | – | – |
| D-P2 | Native operations not lower in macro (matched pairs) | Σnative_M ≥ Σnative_P | Σnative_M < Σnative_P | < 5 matched pairs |
| D-P3 | Macro not worse on known-goal passes (18 cases), ±2 per model | passes_M ≥ passes_P − 2 | passes_M < passes_P − 2 | ≥ 5 of 40 trials censored |
| D-P4 | Qwen's failures concentrate on inspection-first selection: selecting/acting on `ur5e.inspect_readiness` when the correct action is a movement skill or a clarification | ≥ 50% of Qwen's failed trials (both arms) and ≥ 3 such | < 50% | < 4 Qwen failures |

D-P4 includes ambiguous cases, so it stays PRELIMINARY until the clarification ratings are in.
These are descriptive tests on 10 groups, not significance claims.

## 8. Scoring and analysis (to implement in B3 and test on synthetic rows)

- Per trial: frozen M4 `score()` (primary pass, goal_correct, selected_outcome_correct, dispatches,
  fault exercised, invalid attempts, unsupported/wrong-goal successes, native operations by actor) and the
  M4 local + persisted Phoenix audits. Ambiguous: M4 automated screen, plus human rating of the transcript
  (kit packaged, results **PRELIMINARY** until rated; no AI ratings).
- **Censoring = G1 CENSORING_RULES_V1** (`revision-1/stage-3/CENSORING_RULES_V1.md`): V1 all scheduled
  (correct / incorrect / censored / unstarted), V2 evaluable only (prediction status), V3 censored = fail.
  ≥ 5 of a model's 40 held-out trials censored (8/76 scaled up) = operationally compromised → Uninformative.
- Analysis, per model, never pooled: paired by case; by type (d_type) and by family; **discordant counts**
  b (P pass, M fail) and c (M pass, P fail) with an exact two-sided binomial p on b + c (descriptive);
  **whole-template-group bootstrap**, 10,000 draws, seed 20261113, over the 9 known-goal groups (pass
  difference M − P, R, native ratio; percentile 95% intervals; draws without matched pairs counted, not
  dropped); **selection** (goal_correct) and **execution** (outcome correct ∧ dispatches = expected ∧
  fault exercised ∧ no violation, given correct selection) reported separately.
- Costs: all-attempt and matched-success views of calls, decision calls, known input/output tokens,
  native operations, task seconds; censored usage labelled unknown, not zero. Offload per model.
- Dev rows (D1) are reported separately and never pooled with held-out.

## 9. Gates, stops and deadline

- **D1 (dev).** First 52 zero-model Gazebo controls (26 cases × 2 arms, M4 deterministic reference; all
  must pass with clean teardown). Then every admitted model, both arms, 6 dev cases. **Auto-freeze D2 when
  all hold:** zero harness/scorer crashes; every model completes all dev trials or is censored only under
  V1 rules; every reset check passes; the D analysis runs end to end on the dev rows. Then write the
  freeze manifest (wrapper, cases, schedule, analysis hashes). Otherwise stop and report.
  Dev results may not change cases, bounds, wording or predictions.
- **D2 (held-out).** One attempt per case × arm × model. No reruns or replacements. Frozen analysis runs
  automatically at the end; ambiguous kit packaged.
- **Stops:** frozen-input hash mismatch; reset check failure; harness/scorer crash; Phoenix audit failure
  (as M4); model ceiling reached (that model stops, others continue); Sol authorization loss (Sol stops,
  local models continue); laptop interruption (stop between trials, resume only unstarted rows under the
  G1 resume rules).
- **Deadline: no trial starts after Mon 2026-11-23 06:00 Taipei.** Unstarted rows are "not run"; the
  stage is reported "partial" with whole-case balance.

## 10. Estimate (fits Sun 12:00 – Mon 06:00, 18 h)

Measured on this laptop in M4 (campaign wall incl. setup/audit): **Sol 27 s/trial** (40 trials, 18 min),
**Qwen 126 s/trial** (40 trials, 84 min; task median 57 s, max 287 s). No laptop data exists for
Ministral/Granite/Llama; assumed Qwen-like (H). Model swaps assumed 30 s each (H), up to one per local
model per case.

| Stage | Models | Trials | Sol requests (expected / cap) | Local requests cap / model | Typical | Pessimistic (locals 1.5×) | Bound (every local trial hits 360 s) |
|---|---|---:|---|---:|---:|---:|---:|
| D1 controls | – | 52 | 0 | 0 | ~15 min | – | – |
| D1 dev | 3 | 36 | ~32 / 99 | 99 | 1.0 h | 1.5 h | 2.8 h |
| D1 dev | 5 | 60 | ~32 / 99 | 99 | 2.0 h | 2.8 h | 5.5 h |
| D2 held-out | 3 | 120 | ~106 / 323 | 323 | **3.4 h** | 4.8 h | 9.3 h |
| D2 held-out | 5 | 200 | ~106 / 323 | 323 | **6.6 h** | 9.4 h | **18.3 h** |

(Sol expected requests use M4's 2.65/trial.) Typical and pessimistic estimates fit the 18 h window with
margin. Only the extreme bound for five models (every local trial timing out) is slightly over; the
case-interleaved order then leaves balanced partial data. **Recommendation: keep all 20 held-out cases.**
If Martin wants a guaranteed worst-case fit, the alternative is 16 cases (drop groups G04 and G08,
chosen now, before any data): bound 14.6 h. D1 must finish before Sun 12:00 and needs Phase B admission
first (it decides the model set); session A also runs F1 and parity on the GPU on Saturday night.

## 11. Outputs

`artifacts/gazebo-d-20261121/runs/{controls,dev,heldout}/` (raw trials, traces, ledgers), `analysis/`,
`D1_REPORT.md`, `D2_REPORT.md`, ambiguous review kit. STATUS.md entry at every gate; push at every gate.

## 12. Limits and future work

AI-authored cases (no independent author); only 3 registered poses and the M4 fault set; 10 groups, so
intervals are wide; laptop partial offload; Sol hosted; Granite/Llama only as adapted transports; no
stock-ROSA arm (future work: add it as a third arm with the same bounds); no physical robot.
