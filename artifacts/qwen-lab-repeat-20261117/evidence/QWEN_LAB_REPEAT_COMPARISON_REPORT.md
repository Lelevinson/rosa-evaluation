# Qwen lab evaluation and repeatability report

Date: **2026-11-17**.

The lab Qwen configuration is the current reference for the lab local-model comparison. Both completed lab runs are reported; the second is a replication rather than a replacement selected for a better result. This report does not revise historical M4 or its matched hosted-Sol comparison.

## What ran

Two lab runs of **80 Qwen trials each**, with ten known M4 families, four repetitions and two conditions: model-managed primitives and a bounded macro. Each run has 40 attempts per condition. Four ambiguous attempts per condition remain **pending human semantic review**. Known-goal correctness therefore uses **36 per condition**, while cost totals and means include all 40 attempts. Correctness includes appropriate FAILURE or UNKNOWN handling when required, not only successful physical movement. The underlying legacy ambiguity regex remains diagnostic and is not treated as human adjudication.

Hardware: **NVIDIA GeForce RTX 4080 SUPER, 16376 MiB, 570.195.03**. Model: `qwen3.5:9b`, Q4_K_M, digest `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`. The existing identical model was reused; no duplicate model was downloaded. The original 62-file M4 execution snapshot and frozen lab adapter were imported unchanged. The second run uses a new 74-file source/config freeze and separate Phoenix project/output paths.

Serving settings: Ollama 0.40.6, context 8,192, maximum output 1,024 per call, observed output allowance 2,048 per task, temperature 0, seed 42, thinking off, streaming off, application response cache off. The existing server uses one parallel request and one loaded model. Application caching off does not establish absence of internal prefix/KV reuse; cached-token counts are not recorded.

Bounds remain eight model calls, ten native operations, sixteen tool attempts, three corrections, 360 seconds and at most one movement dispatch per task. The repeat ceiling is 640 ordinary requests plus three narrow HTTP retry reserve and an eight-hour backend window. Only HTTP 502/503/504 can receive the existing one retry per logical call; generic errors and response-length failures cannot. There were no hosted requests and no changes to model prompts, schema acceptance, scoring, retry eligibility or robot guards.

## Observed results

| Run | Condition | Known-goal correct | Calls | Input tokens | Output tokens | Mean task s | Median task s | Native ops | Invalid attempts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lab_run_1 | primitives | 27/36 | 188 | 414,923 | 35,710 | 12.39 | 7.63 | 78 | 55 |
| lab_run_1 | macro | 28/36 | 98 | 198,325 | 25,200 | 8.56 | 4.31 | 97 | 11 |
| lab_run_2 | primitives | 26/36 | 185 | 403,666 | 36,223 | 12.01 | 7.62 | 75 | 55 |
| lab_run_2 | macro | 28/36 | 97 | 196,331 | 25,257 | 8.52 | 4.38 | 98 | 10 |

Task times are measured trial wall time, including framework and native work, rather than generation throughput alone. Simulator startup, intertrial preparation, deterministic controls and installation are excluded from those means. Lower calls or time do not establish useful efficiency if a requested task was not correctly completed.

| Condition | Correct in both runs | First only correct | Repeat only correct | Incorrect in both |
|---|---:|---:|---:|---:|
| primitives | 25 | 2 | 1 | 8 |
| macro | 28 | 0 | 0 | 8 |

Each paired cell has the same family, repetition and condition. This records behavioral repeatability, without assuming exact repeatability from a fixed seed.

The verified changed-cell records are:

- `partial_command`, repetition 1, primitives: correct True -> False; selected skill `ur5e.park_right` -> `ur5e.park_right`; accepted report FAILURE -> None; calls 8 -> 8.
- `ineffective_command`, repetition 4, primitives: correct True -> False; selected skill `ur5e.park_right` -> `ur5e.park_right`; accepted report FAILURE -> None; calls 7 -> 8.
- `partial_command`, repetition 4, primitives: correct False -> True; selected skill `ur5e.park_right` -> `ur5e.park_right`; accepted report None -> FAILURE; calls 8 -> 8.

In these three cells the selected movement skill remained `ur5e.park_right`, and the injected fault was actually exercised. The differences concerned completing a valid outcome report. The repeat partial-command r1 case exhausted eight calls without an accepted report; ineffective-command r4 stopped on response truncation without an accepted report; partial-command r4 obtained an accepted, evidence-grounded FAILURE in the repeat. These are not evidence of three new initial skill-selection mistakes. Full answers and validation errors are retained in `changed_cell_evidence` in the independent analysis.

| Known-goal family | First primitives | First macro | Repeat primitives | Repeat macro |
|---|---:|---:|---:|---:|
| already_satisfied | 4/4 | 4/4 | 4/4 | 4/4 |
| ineffective_command | 4/4 | 4/4 | 3/4 | 4/4 |
| inspect_healthy | 4/4 | 4/4 | 4/4 | 4/4 |
| inspect_inactive | 4/4 | 4/4 | 4/4 | 4/4 |
| inspect_missing_controllers | 4/4 | 4/4 | 4/4 | 4/4 |
| inspect_missing_joint | 4/4 | 4/4 | 4/4 | 4/4 |
| missing_prerequisite | 0/4 | 0/4 | 0/4 | 0/4 |
| move_constrained | 0/4 | 0/4 | 0/4 | 0/4 |
| partial_command | 3/4 | 4/4 | 3/4 | 4/4 |

## Costs on identical successful cells

| Condition | Cells correct in both runs | Calls first / repeat | Seconds first / repeat | Native ops first / repeat |
|---|---:|---:|---:|---:|
| primitives | 25 | 113 / 109 | 239.19 / 233.88 | 60 / 56 |
| macro | 28 | 61 / 60 | 154.36 / 151.57 | 69 / 68 |

Within the second run, costs for cells successfully completed in both architectures are:

- primitives: 26 tasks, 117 calls, 257.56 seconds, 60 native operations.
- macro: 26 tasks, 55 calls, 131.70 seconds, 61 native operations.

The complete machine-readable analysis includes tokens, correctness transitions and family counts. The earlier multi-model report remains authoritative for Ministral, Llama and Granite; they were not rerun here.

## Audits, limits and actual inference timing

The repeat completed **80/80 live trial audits** and **20/20 deterministic controls**, with **3,605 persisted live spans**. All 74 frozen source/config hashes matched; the original 69-file freeze remains intact. Raw trial files match checkpoints, persisted Phoenix records match local audits, and downloaded ZIP integrity and every manifest hash passed independent verification. The repeat used **282 physical requests**, matching traced model calls and the request journal. Token usage was complete; every checked task stayed inside call/output/native/dispatch/time bounds. Simulator cleanup completed successfully and no dispatch violation was recorded.

Final audited LLM spans retain actual Ollama durations: aggregate generation throughput **89.44 tokens/s**; largest prompt **4,373 tokens**; completion reasons `{"length": 13, "stop": 269}`. Total backend campaign elapsed time was **30.79 minutes**. This is separate from mean task time. Early `_generate` journal metadata may be empty because LangChain merges generation metadata later; the analysis reads the final spans rather than substituting zero durations.

A zero outer-exception count does not mean there were no errors: ROSA can return an error as answer text. Structured unsupported-success counters also do not audit every free-text claim. Both limitations are retained in the original study and in the machine-readable repeat aggregates. Fault handling should be interpreted alongside whether the injected command was actually attempted.

## Relationship to historical laptop M4

The historical laptop configuration used an RTX 4050 Laptop GPU with 6 GB VRAM and partial CPU offload, rather than the lab RTX 4080 SUPER with 16 GB. Historical M4 had two repetitions and 40 Qwen trials total; each lab run has four repetitions and 80. Its published 15/20 primitives and 14/20 macro legacy totals remain unchanged. Those totals include ambiguity cases; they are not directly interchangeable with the lab report's known-goal denominator.

- Historical primitives, known-goal subset: 15/18; all-attempt mean 133.49 seconds, 91 calls over 20 attempts.
- Historical macro, known-goal subset: 14/18; all-attempt mean 85.18 seconds, 53 calls over 20 attempts.

Restricting the repeat to the historical case/repetition/condition cells gives:

| Condition | Shared known-goal cells | Historical correct | Repeat correct | Both correct | Historical only correct | Repeat only correct |
|---|---:|---:|---:|---:|---:|---:|
| primitives | 18 | 15 | 13 | 13 | 2 | 0 |
| macro | 18 | 14 | 14 | 12 | 2 | 2 |

The new lab observations can establish how this lab setup performed, but do not isolate a causal hardware effect. Serving environment, system state, execution timing and repetition count differ. No fresh Sol run was made, so this cannot replace the earlier paired Sol/Qwen comparison with a purported same-environment comparison.

## Interpretation and next steps

These are repetitions of ten already-seen families, not 160 independent new task designs or held-out generalization evidence. Temperature zero and a fixed seed do not remove all inference or simulator nondeterminism. The evidence can show where correctness, calls and timing were stable or changed, but does not establish broad model parity, statistical equivalence, or physical-robot safety. Both conditions use the same previously repaired ROSA framework, not a stock-ROSA comparator. Execution mode and the condition instruction sentence remain bundled, so a selection difference cannot be attributed to execution code alone. The lab Qwen setup remains the current reference; retain both runs and the family-specific limitations rather than replacing failures or selecting a favorable repetition.

Use the verified aggregates to decide whether a specific error deserves a separately authorized prospective intervention. No prompt repair, automatic report repair, new model study or G1 held-out launch is authorized by this repeat. G1 human/scorer/observability gates remain unresolved.

## Files and cleanup

The raw repeat ZIP, independent analysis and verification accompany this report. The original full lab evidence ZIP is also required to reproduce the imported frozen runtime; the share bundle includes it. Earlier reports and archives are unchanged. Repeat raw ZIP SHA-256: `697ab75b80054f1e969ec108f9a6d68608cf63986cb390435d4a9cb13bf89b92`.

The old misplaced `/media/naeem/marvel proj` and `/media/naeem/d/marvel proj` paths were already absent. A targeted inventory found no project-named leftovers in `/tmp`, `/var/tmp` or `/home/naeem`. Useful Ollama identity/cache files, SSH/VPN configuration, installed models, shared tools and Docker runtime dependencies were preserved. No unrelated project directories were deleted. The project itself and all repeat outputs are under `/media/naeem/d1/marvel proj/`.
