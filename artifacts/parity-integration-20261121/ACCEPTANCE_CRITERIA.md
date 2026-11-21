# Parity Phase B: tasks and acceptance criteria (FROZEN 2026-11-21)

Written by session B (designer) on 2026-11-21, before any Phase B model call. **Zero model calls.**
Frozen at the commit that adds this file. Session A (runner) executes; it may not edit this file.
Any change after freezing is an owner amendment, recorded as a new dated file. This file stays as it is.

Machine (owner decision D16 / PX-1): **laptop** (Windows 11 + WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB).
Serving = G1: num_ctx 8192, temperature 0, seed 42, num_predict 1024 per call, `think:false`, stream as G1,
same model digests as G1 (`LAPTOP_TARGET_CONFIG.md` §2). Record GPU layers/offload for every run.
Timing is descriptive only. Never mix machines within one comparison.

## 1. Task sets

| File | Tasks | Mix | Use |
|---|---|---|---|
| [tasks/scratch.json](tasks/scratch.json) | 12 (`PAR-sc-001…012`) | 4 inspection (1 healthy-2, 1 known-false-4, 1 timeout-6, 1 healthy-1), 4 write (2 healthy, 1 ineffective, 1 partial), 2 missing-prerequisite, 2 ambiguous; 6 arm / 6 base | adapter development only |
| [tasks/acceptance.json](tasks/acceptance.json) | 10 (`PAR-acc-001…010`) | 4 inspection ladder (healthy-1, known-false-6, healthy-4, timeout-2), 1 unavailable-source, 3 write (2 healthy, 1 ineffective), 1 missing-prerequisite, 1 ambiguous; 5 arm / 5 base | the single acceptance test |

File hashes: [tasks/SHA256SUMS.txt](tasks/SHA256SUMS.txt). Each task also carries `case_sha256`.
Generator: `tools/parity/build_tasks.py` (deterministic; rerun reproduces the bytes).
Schema: frozen G1 case fields, so the frozen G1 mock engine and scorer apply unchanged.
Authorship: AI (Claude Opus 5.5, session B). No human wrote or reviewed them.

**Leakage** ([tasks/LEAKAGE_CHECK.md](tasks/LEAKAGE_CHECK.md)): the F1 checker reused unchanged (same metric,
normalization and thresholds). References: M4/G1 length-stop requests, all 38 G1 held-out, 18 G1 dev and all
30 F1 held-out requests; acceptance tasks are also checked against the 12 scratch tasks. Result: **22/22 OK,
0 REVIEW, 0 near-paraphrase**, and no within-set near-duplicates. One scratch draft (PAR-sc-006) first scored
REVIEW (0.48 vs F1-ho-009); it was reworded before any use. The check is lexical and cannot detect a shared
task type, which is required by design.

These tasks are **not** held-out evidence for any study. They test transport only.

## 2. What session A may do with each set

- **Scratch:** any subset, any number of runs, inside the time box: **3 hours or 4 adapter iterations per
  model, whichever comes first.** One iteration = one adapter change + its scratch runs. Log every iteration
  (adapter diff, SHA-256, scratch results) in `PHASE_B_ITERATION_LOG.md`.
- **Acceptance:** run **once** per model, after the adapter is frozen (SHA-256 recorded before the run).
  No reruns, no replacements, no partial reruns. A censored trial is not replaced.
- Adapters may only use the ALLOWED transport changes (master task "Parity rules"; PARITY_AUDIT §4, §7).
  Owner decision PA-1 (Granite) is a recorded owner exception; its status is in §6.

## 3. Run protocol for the acceptance test

- 10 tasks × 2 arms (primitives, macro) = **20 trials per model**, one attempt each.
- Frozen G1 engine, G1 prompts, catalogue, tool names, descriptions, schemas, G1 per-trial bounds, G1 scorer,
  G1 V1 censoring and retry rights. Frozen G1 wording (not F1).
- Order (fixed; `random.Random(20261121).shuffle` of the 20 (task, arm) pairs, CPython 3.14.3; the list below
  is authoritative, not the code):

  1 acc-007 P · 2 acc-009 M · 3 acc-004 P · 4 acc-002 M · 5 acc-004 M · 6 acc-003 P · 7 acc-007 M ·
  8 acc-006 P · 9 acc-005 M · 10 acc-008 P · 11 acc-010 M · 12 acc-008 M · 13 acc-001 P · 14 acc-001 M ·
  15 acc-010 P · 16 acc-002 P · 17 acc-006 M · 18 acc-005 P · 19 acc-003 M · 20 acc-009 P

  (P = primitives, M = macro). Same order for every model. Models in order Granite, Llama, then Qwen and
  Ministral as reference points.

## 4. Pass criteria (per model; both arms must pass)

Scored by `tools/parity/acceptance_score.py` (frozen with this file) from the trial `result.json` files.

| # | Criterion | Threshold |
|---|---|---|
| A1 | **Recognized native tool calls:** outputs with ≥1 structured `tool_calls` entry ÷ model outputs in trials where a tool call is the correct next action | **≥ 0.90** |
| A2 | **Schema-valid arguments:** (recognized calls − invalid) ÷ recognized calls | **≥ 0.90** |
| A3 | **Parse crashes:** trials whose `error`/`model_errors` has a parse-path signature | **= 0** |

Definitions (fixed):
- *Turn where a tool call is the correct next action* = every model output in a trial whose task has
  `tool_call_expected: true` (all kinds except `ambiguous`). In G1 both arms end with the `submit_report` tool,
  so every such output should be a tool call. Length-stopped outputs count in the denominator.
- *Recognized* = the structured call reached the harness through Ollama's parser and ChatOllama. Tool-shaped
  text in `content` (fences, prose JSON) is **not** recognized.
- *Invalid* = a call whose name is not one of `select_skill, read_state, write_state, verify_outcome,
  submit_report`; a harness rejection with code `schema_validation`; a "not a valid tool" response; or a
  ChatOllama `invalid_tool_calls` entry. Semantic rejections (`unknown_observation_reference`,
  `invalid_node_scope`, `outcome_classification_mismatch`, …) are **not** transport failures; they are reported.
- *Ambiguous task* outputs are excluded from A1/A2 and reported (a tool call there is a behaviour, not a
  transport, finding).

Outcomes:
- **Pass** → freeze the adapter (SHA-256), admit the model to Phase C and Gazebo D. Label: "adapted
  (transport only)", plus "with owner exception PA-1" for Granite if PA-1 is used.
- **Fail** → "**not adaptable under parity rules**", with this evidence. No further tries.
- **Incomplete** (any arm with < 8 of its 9 tool tasks evaluable because of infrastructure censoring under G1
  V1) → "acceptance incomplete (infrastructure)", not admitted, not called "not adaptable". Reported to Martin.
- Qwen and Ministral take the same test unchanged, as reference points. A failure there is reported, never
  fixed.

## 5. Calibration on frozen G1 records (zero model calls)

The scorer was run on the 76 frozen G1 held-out trials per model (all kinds; ambiguous excluded as above).
Outputs: [calibration/](calibration/).

| G1 model (plain adapter, lab) | macro A1 | macro A2 | prim. A1 | prim. A2 | Crashes | Result |
|---|---:|---:|---:|---:|---:|---|
| Qwen | 68/73 (0.93) | 68/68 | 115/119 (0.97) | 115/115 | 0 | PASS |
| Ministral | 81/81 | 81/81 | 149/149 | 149/149 | 0 | PASS |
| Granite | 0/36 | – | 0/36 | – | 0 | FAIL (A1) |
| Llama | 173/177 (0.98) | 76/173 (0.44) | 192/193 (0.99) | 85/192 (0.44) | 0 | FAIL (A2) |

This matches the Phase A diagnosis (PARITY_AUDIT §3): Granite never emits a recognized call; Llama emits calls
whose arguments fail the schema after turn 1. Qwen's macro margin is small (0.93, mostly length stops), so a
reference-point failure for Qwen on the laptop is possible and would be reported as such.
This calibration is on G1 held-out cases. It was not used to choose the thresholds (they come from the
master task).

## 6. Open owner point (does not block Llama)

**PA-1 (Granite).** PA-1 (2026-11-21, PARITY_AUDIT §7) adds IBM's tool-format sentence to Granite's system
message as an owner exception. The weekend master task lists "per-model instructions" as NOT ALLOWED and says
a model that can only be fixed by breaking a rule is "not adaptable under parity rules". Session B cannot
decide which instruction wins. Until Martin answers:
- session A may still run Llama, Qwen and Ministral;
- for Granite, both labels are prepared: with PA-1 → "adapted with owner exception PA-1"; without PA-1 →
  per PARITY_AUDIT §4, no parity-clean fix exists → "not adaptable under parity rules".
