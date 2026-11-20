# ROSA lab local-model comparison

Date: **2026-11-17**.

A new M4-based replication on the lab RTX 4080 SUPER. Original M4 results remain unchanged. The owner requested **80 trials per model**, so this schedules **320 total** across four model families. Original M4 had **80 total**, 40 each for Sol and Qwen.

**Semantic correctness covers 72 known-goal trials/model (36 per condition).** Eight ambiguous trials/model remain separately pending human semantic review; legacy regex passes are not a final judgment. Calls, tokens, native operations and timing below include **all attempted trials**, including failures and ambiguous cases.

| Model | Condition | Known-goal correct | Recorded trials | Calls | Input tokens | Output tokens | Mean task s | Median task s | Native ops |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 9B | primitives | 27/36 | 40/40 | 188 | 414,923 | 35,710 | 12.39 | 7.63 | 78 |
| Qwen3.5 9B | macro | 28/36 | 40/40 | 98 | 198,325 | 25,200 | 8.56 | 4.31 | 97 |
| Llama 3.1 8B | primitives | 0/36 | 40/40 | 211 | 257,465 | 5,860 | 2.16 | 1.81 | 18 |
| Llama 3.1 8B | macro | 0/36 | 40/40 | 193 | 259,262 | 5,845 | 2.84 | 1.99 | 88 |
| Granite 3.3 8B | primitives | 0/36 | 40/40 | 40 | 54,072 | 11,782 | 3.13 | 2.58 | 0 |
| Granite 3.3 8B | macro | 0/36 | 40/40 | 40 | 54,032 | 9,897 | 2.64 | 1.52 | 0 |
| Ministral 3 8B | primitives | 28/36 | 40/40 | 156 | 265,042 | 13,538 | 4.83 | 4.10 | 76 |
| Ministral 3 8B | macro | 28/36 | 40/40 | 82 | 122,410 | 4,650 | 2.31 | 1.39 | 78 |

## Findings and recommendation

**Ministral 3 8B is a promising faster alternative, not an unqualified replacement for Qwen.** Its macro condition passed 28/36 known-goal cases, matching Qwen's 28/36, with 82 versus 98 calls over all 40 attempts and mean task time 2.31 versus 8.56 seconds. That all-attempt time difference is 73.0%, but the two models failed different cases. On the **24 identical macro cells both passed**, Ministral took **45.53 seconds versus Qwen's 101.42** (55.1% less), while using **53 versus 48 calls** and **57 versus 52 native operations**. Lower latency did not mean fewer calls or robot operations on every comparable subset.

**Their errors are complementary.** Ministral passed all four macro constrained-pose cases that Qwen failed; Qwen passed all four partial-command cases that Ministral failed. Both failed all four missing-prerequisite cases in each condition. Therefore equal aggregate macro scores do not establish interchangeability, general parity, or a model that is dependable enough across these tasks.

**Macros helped orchestration in the two working backends.** Qwen's known-goal passes were 27/36 with primitives and 28/36 with macros; calls fell 188 to 98, and mean task time fell 12.39 to 8.56 seconds. Ministral's pass count stayed 28/36 in both conditions; calls fell 156 to 82, and mean task time fell 4.83 to 2.31 seconds. Qwen's all-attempt native operations increased 78 to 97; Ministral's increased 76 to 78. On within-model pairs where both conditions passed, Qwen used 128 to 58 calls and 66 to 65 native operations; Ministral used 110 to 62 calls and 60 to 70 native operations. These are distinct efficiency trade-offs, not a universal reduction in work or proof of reliability improvement.

**Llama's 0/72 full-task score is an interface/compliance result, not zero task understanding.** It selected the required skill in 32/36 known-goal cases in each condition, versus 28/36 for Qwen and Ministral. It nevertheless produced no accepted correct outcome. The macro often performed the selected routine correctly, but the model repeatedly sent `classification` instead of the schema's required `status`. For example, `02-move_constrained-r1-macro` selected `ur5e.stage_left`, reached the independently observed target, then made four rejected `submit_report` calls with `classification: SUCCESS`, missing `status`. Across known-goal macro cases there were 125 missing-status and 121 forbidden-classification field errors; these are field-error counts, not 246 separate failed tasks. Primitive cases also commonly sent `subject` instead of required `nodes`. The same correction limits and validator were applied to every model. No aliases were added and no failures were rescored.

**Granite was nonfunctional through this exact native-tool configuration.** It made one model call per trial, zero native operations, and passed 0/72 known-goal tasks. It often wrote descriptions, JSON or code depicting unexecuted tools and observations. A later small tool-binding probe also returned JSON text rather than a native tool-call object. This establishes failure of this model/template/server/adapter/prompt arrangement; it does not isolate a model-intrinsic inability or prove every Granite deployment fails.

**Qwen's extra verbosity remains material.** It generated 60,910 tokens over the main schedule versus Ministral's 18,188. Qwen had 12 returned length stops. The observed generation rates were about 89.49 and 99.87 tokens/second, respectively: the task-time difference cannot be reduced to raw decoder speed alone. Source traces show wrong initial choices, rejected reselection and truncated responses; this study does not isolate their causal contributions. More tokens, clearer common instructions and altered recovery would be separate interventions, not fixes silently applied to this campaign.

The near-term recommendation is to retain **Qwen as the reference and Ministral as the strongest additional candidate from this test**, with explicit per-family limitations. Do not choose Llama or Granite for this pipeline based on their short failure times. Before considering Llama a hopeless model, prospectively test a clearer, consistent reporting contract using fresh cases and the same safeguards; credit any repair to the combined system. Investigate Granite's native-call compatibility separately before making an ability comparison. Do not redesign the framework around each failure or add JTVR/memory for this result.

Continue resolving the existing G1 scoring, observability and independent-review gates before any G1 held-out launch. These known M4 repetitions do not satisfy those gates or authorize a new architecture or held-out campaign.

## Macro versus primitives: cost and correctness together

Matched-success costs use only known-goal pairs where **both** conditions passed. This selected subset cannot erase failures in the full schedule.

| Model | Known-goal macro minus primitive passes | Macro-only / primitive-only correct pairs | Matched-success pairs | Matched calls P / M | Calls saved | Matched native P / M | Matched time P / M (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 9B | +1 | 1 / 0 | 27 | 128 / 58 | 54.69% | 66 / 65 | 280.82 / 140.80 |
| Llama 3.1 8B | +0 | 0 / 0 | 0 | 0 / 0 | N/A (no successful pairs) | 0 / 0 | 0.00 / 0.00 |
| Granite 3.3 8B | +0 | 0 / 0 | 0 | 0 / 0 | N/A (no successful pairs) | 0 / 0 | 0.00 / 0.00 |
| Ministral 3 8B | +0 | 0 / 0 | 28 | 110 / 62 | 43.64% | 60 / 70 | 131.40 / 71.18 |

## Direct paired comparison against fresh lab Qwen

Each candidate is aligned with Qwen on case, repetition and execution condition. Repeated cases are not independent task families.

| Candidate | Condition | Known-goal pairs | Candidate-only correct | Qwen-only correct |
|---|---|---:|---:|---:|
| Llama 3.1 8B | primitives | 36 | 0 | 27 |
| Llama 3.1 8B | macro | 36 | 0 | 28 |
| Granite 3.3 8B | primitives | 36 | 0 | 27 |
| Granite 3.3 8B | macro | 36 | 0 | 28 |
| Ministral 3 8B | primitives | 36 | 4 | 3 |
| Ministral 3 8B | macro | 36 | 4 | 4 |

Across-model matched-success costs below use only identical case/repetition/condition cells that both the candidate and Qwen passed. They accompany, rather than replace, the all-attempt and discordant-outcome views.

| Candidate | Condition | Both-correct cells | Calls candidate / Qwen | Task seconds candidate / Qwen | Native candidate / Qwen |
|---|---|---:|---:|---:|---:|
| Llama 3.1 8B | primitives | 0 | 0 / 0 | 0.00 / 0.00 | 0 / 0 |
| Llama 3.1 8B | macro | 0 | 0 / 0 | 0.00 / 0.00 | 0 / 0 |
| Granite 3.3 8B | primitives | 0 | 0 / 0 | 0.00 / 0.00 | 0 / 0 |
| Granite 3.3 8B | macro | 0 | 0 / 0 | 0.00 / 0.00 | 0 / 0 |
| Ministral 3 8B | primitives | 24 | 84 / 105 | 73.52 / 209.22 | 48 / 56 |
| Ministral 3 8B | macro | 24 | 53 / 48 | 45.53 / 101.42 | 57 / 52 |

## Family outcomes

Each known-goal cell is passes/recorded for that family and condition. **Pending** is not a failure. The ambiguous family is excluded from semantic pass totals.

| Family | Qwen P | Qwen M | Llama P | Llama M | Granite P | Granite M | Ministral P | Ministral M |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| move_constrained | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| already_satisfied | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| ineffective_command | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| partial_command | 3/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| missing_prerequisite | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| inspect_healthy | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| inspect_inactive | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| inspect_missing_controllers | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| inspect_missing_joint | 4/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| ambiguous_goal | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

## Errors, claims and fault exercise

| Model | Condition | Invalid attempts | Unsupported SUCCESS attempts | Accepted wrong-goal SUCCESS (known goals) | Fault exercised / required | Dispatch violations | Error types |
|---|---|---:|---:|---:|---:|---:|---|
| Qwen3.5 9B | primitives | 55 | 0 | 0 | 20/24 | 0 | {} |
| Qwen3.5 9B | macro | 11 | 0 | 0 | 20/24 | 0 | {} |
| Llama 3.1 8B | primitives | 157 | 0 | 0 | 0/24 | 0 | {} |
| Llama 3.1 8B | macro | 143 | 0 | 0 | 20/24 | 0 | {} |
| Granite 3.3 8B | primitives | 0 | 0 | 0 | 0/24 | 0 | {} |
| Granite 3.3 8B | macro | 0 | 0 | 0 | 0/24 | 0 | {} |
| Ministral 3 8B | primitives | 30 | 0 | 2 | 16/24 | 0 | {} |
| Ministral 3 8B | macro | 4 | 0 | 0 | 16/24 | 0 | {} |

**Metric boundary:** unsupported-SUCCESS attempts count validation events at the structured reporting tool. This is not a semantic audit of every free-text claim. A model can describe invented tool execution without invoking a tool, fail the task, and still have zero structured unsupported-SUCCESS events. Accepted wrong-goal SUCCESS in this table covers known-goal tasks; raw legacy flags across all trials remain separately available in JSON.

## Selection, reporting and feedback are different outcomes

These rows concern the 36 known-goal tasks in each condition. Correct skill selection does not imply successful execution or an accepted report. A pass after validation errors credits the combined model/feedback/framework system, not an unaided first-pass model improvement.

| Model | Condition | Correct selection | Correct selected outcome | Full-task pass | Pass after validation errors | Agent returned an error message |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 9B | primitives | 28/36 | 27/36 | 27/36 | 14 | 8 |
| Qwen3.5 9B | macro | 28/36 | 28/36 | 28/36 | 0 | 8 |
| Llama 3.1 8B | primitives | 32/36 | 0/36 | 0/36 | 0 | 33 |
| Llama 3.1 8B | macro | 32/36 | 0/36 | 0/36 | 0 | 30 |
| Granite 3.3 8B | primitives | 0/36 | 0/36 | 0/36 | 0 | 0 |
| Granite 3.3 8B | macro | 0/36 | 0/36 | 0/36 | 0 | 0 |
| Ministral 3 8B | primitives | 28/36 | 28/36 | 28/36 | 8 | 2 |
| Ministral 3 8B | macro | 28/36 | 28/36 | 28/36 | 0 | 0 |

The legacy outer `error_type` can be empty while ROSA returns a controlled error as answer text. It does not mean that generation truncation or validation exhaustion never occurred. Structured validation codes, schema details and these returned-error codes are preserved in INDEPENDENT_ANALYSIS.json.

## Speed, inference and resource accounting

Task time includes the agent loop and its native operations. Campaign time additionally includes simulator startup, resets, independent observations, logging and trace audits. The inference throughput below is returned eval tokens divided by returned eval duration, not wall-clock task throughput. Cold-load time is shown rather than silently removed.

| Model | Campaign s | Physical calls | Returned length stops | Max returned prompt tokens | Load s | Prompt evaluation s | Generation s | Generated tokens/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 9B | 1,865.67 | 286 | 12 | 4127 | 23.96 | 49.15 | 680.60 | 89.49 |
| Llama 3.1 8B | 1,225.85 | 404 | 0 | 1871 | 5.85 | 22.25 | 101.26 | 115.60 |
| Granite 3.3 8B | 1,265.92 | 80 | 0 | 1533 | 1.53 | 7.76 | 215.46 | 100.62 |
| Ministral 3 8B | 1,318.76 | 238 | 0 | 3052 | 5.36 | 17.19 | 182.11 | 99.87 |

Unknown usage and whether `prompt_eval_cached_count` exists are retained explicitly in INDEPENDENT_ANALYSIS.json. LangChain response cache is disabled; that does not prove the Ollama server reused no prompt prefix/KV state. Token counts use each model's tokenizer and do not represent equal semantic work.

## Reproducibility and limits

- Operator phase: **EXECUTION_COMPLETE**. Verify completed per-model schedules before calling the study finished.
- Archive CRC and **3233 content hashes** matched; **69 frozen source/config hashes** matched.
- **320 live local/persisted audit pairs** checked, totaling **12,506 persisted live spans**. Twenty deterministic controls passed separately.
- Qwen digest identical to retained original M4: **True**.
- Four models use Q4_K_M, the same requested 8K context, 1024 output tokens/call, 2048 observed output tokens/task, temp0, seed42, non-thinking policy, and unchanged tools/guards. Architecture, tokenizer, templates, stop tokens and other native defaults differ.
- Limits: eight decisions, 360 seconds, ten native operations, sixteen tool attempts, three corrections and at most one permitted movement/task. Each model has 640 ordinary plus three narrowly eligible reserve request slots and an eight-hour campaign window. Failed/unknown usage is not free compute.
- Lab host is Ubuntu 25.04; the owned ROS 2 Jazzy container uses Ubuntu 24.04. Locked Python environments and exact container package inventory are archived. Actual simulator package versions can differ from the historical laptop.
- Seeded model order is Ministral, Granite, Qwen, Llama. GPU is checked at each launch, not continuously proven idle throughout. Model timing is observed combined-system performance on a shared host.
- All conditions share the repaired framework. This does not compare against untouched upstream ROSA. Execution mode and condition wording remain packaged together.
- These are known M4 cases repeated four times, not 80 independent tasks/model or unseen generalization. There are only nine known-goal families plus one ambiguity family; no population-level equivalence or general reliability claim follows.
- Human clarification judgments remain pending. Structural no-action counts and raw legacy regex diagnostics are available; no names or judgments were fabricated.
- Frozen historical M4/G1/M1–M5 artifacts were not rewritten. G1 held-out remains paused. No new Sol requests, OAuth grant or physical robot action was involved.

## Historical comparison context

Original M4 used **20 trials/condition/backend**, including two ambiguous trials per condition. Its reported whole-task outcomes were Sol **20/20 → 20/20** and Qwen **15/20 → 14/20**. Calls were **68 → 38** and **91 → 53**; mean task time was **16.42 → 9.73 s** and **133.49 → 85.18 s**, respectively. These original totals are preserved, not rescored.

The new schedule doubles repetitions and reports clarification separately because of the known regex defect. Historical Sol is not a fresh lab control. A laptop-to-lab Qwen speed difference combines GPU/offload, environment, schedule and time effects; it is not an intrinsic model or framework improvement.

## Interpretation and next step

Use known-goal correctness and paired disagreements first, then compare all-attempt and matched-success costs. A model that stops cheaply on the wrong skill is not more effective. An evidence-grounded readiness SUCCESS can still fail a movement goal. Native-operation savings, inference savings and task-time savings are different claims.

Treat any ranking here as a ranking of these model/configuration/framework combinations on this small known catalogue. Retain a cheaper macro only where its correctness trade-off is acceptable; do not enlarge limits or tune prompts after observing these outcomes and present that as the same experiment. Obtain actual clarification review before an 80-case semantic verdict, and resolve the existing G1 gates before any G1 held-out launch.

Official model references: [Qwen3.5](https://ollama.com/library/qwen3.5), [Llama 3.1](https://ollama.com/library/llama3.1), [Granite 3.3](https://ollama.com/library/granite3.3), [Ministral 3](https://ollama.com/library/ministral-3). Exact downloaded identities and licenses are in preparation/model-*.json and study/freeze.json.

## Separate post-run tool-binding diagnostic

This was a **post-hoc diagnostic after the main outcomes were seen**, using the protocol's optional allowance: one request/model, at most 64 output tokens, the same harmless `lab_probe(value=ready)` request and schema. No returned tool or code was executed. No main trial, failed task, prompt, guard or score was changed or retried.

| Model | Correct native call in this one probe | Input / output tokens |
|---|---|---:|
| qwen3.5:9b | True | 315 / 26 |
| llama3.1:8b-instruct-q4_K_M | True | 196 / 17 |
| granite3.3:8b | False | 113 / 29 |
| ministral-3:8b-instruct-2512-q4_K_M | True | 100 / 12 |

Qwen, Llama and Ministral returned the requested native function call. Granite returned JSON text (`tool_name`/`arguments`) with an empty native `tool_calls` list. Thus Llama's main failure cannot be explained by a total inability to return a basic native tool call, while Granite's compatibility question remains unresolved. One tiny probe does not establish comprehensive tool competence, and this is not held-out evidence.

All four diagnostic persisted audits passed (eight spans total), with zero native executions. The diagnostics used **4 requests, 724 input tokens and 84 output tokens**, reported outside the **1,008 main model requests**. Combined observed inference total: **1,012 requests**. The main campaign had zero infrastructure reserve uses and complete returned usage; the diagnostics were not charged as unrecorded free work.

The original main archive remains byte-identical. Diagnostic source, responses and traces are in `ROSA_LAB_TOOL_PROBE_ADDENDUM_2026-11-17.zip` (23 content hashes verified). Main archive SHA-256: `fa5c14cb31ab4079317106af815bf86a810effff595fefa05f2eb6d6d51d9356`. Addendum SHA-256: `e0780f578c6d328a5912176dd8ff9afa2f54df230cb07e4436ac07394a4e8f49`.

## Deployment, provenance and retained setup failures

The requested real directory is **`/media/naeem/d1/marvel proj/`**, containing `rosa-research/`, `rosa-evaluation/`, `models/`, `baseline/`, `study/`, `runtime/`, `results/`, `preparation/` and `evidence/`. The earlier empty file and intermediate root/d locations were removed after checks. A hyphenated compatibility symlink points to the same directory; it is not a duplicate copy of the models.

Both repositories use `member/martin`. Research commit: `b13df0f03677754f42383dee95424cded862b117`. Evaluation commit: `ec42ee72f53d95004c51b803c1a5d41f58e08d1c`. GitHub's evaluation branch was older, so local commits were transferred by a verified Git bundle and fast-forwarded on the lab machine; nothing was pushed to GitHub. Experimental source comes from the original M4 retained snapshot, not an uncontrolled mix of current uncommitted files. The updated living master is documentation, not a frozen runtime source.

The lab has an RTX 4080 SUPER (16,376 MiB VRAM), about 123 GiB RAM, and Ubuntu 25.04. `Lab_Project1` was full and the root partition nearly full, so weights/runtime use the spacious d1 disk. No existing shared Ollama service or ROS installation was found; the existing uv installation was reused. Ollama was installed project-locally, rather than adding a duplicate system service. Its model API is localhost-only on port 11439. ROS 2 Jazzy/Gazebo uses the owned Ubuntu 24.04 container `marvel-rosa-lab-20261117`, with evaluation runs as uid1000 and a private HOME. No host OS upgrade, real-robot deployment or existing users' project modification was performed.

Phoenix is HTTP-only on localhost port 6006, with the pinned 20.23.0 compatibility launcher and 3.5.0 client. No cloud credentials, lab password or OAuth authorization was copied into this experiment. Temporary sleep inhibition covered the active main study and released after completion; no permanent power settings were changed.

Ollama official release asset SHA-256: `c164ab8b1b28e2a247c29719b8e404c423c5b83ae64c3ab4e59d50c7ff7fc5e0`. Container image ID: `sha256:472fb4307f978886524430f2fae764e168ca95acd13c45a3edb17cc5a33c819a`. Exact installed ROS/system package versions are retained in `preparation/container-packages.txt`.

| Exact model tag | Parameters | Quantization | Downloaded model digest |
|---|---:|---|---|
| qwen3.5:9b | 9.0B | Q4_K_M | `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90` |
| llama3.1:8b-instruct-q4_K_M | 8.0B | Q4_K_M | `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e` |
| granite3.3:8b | 8.2B | Q4_K_M | `fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7` |
| ministral-3:8b-instruct-2512-q4_K_M | 8.9B | Q4_K_M | `1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71` |

Before scored inference, the new adapter had retained setup failures: an ambiguous-family count assertion was corrected to eight ambiguous/72 known-goal trials per model; the host helper was renamed to avoid shadowing Python's `operator` module; the inherited ROS PYTHONPATH was preserved instead of overwritten; and container output ownership was corrected by using uid1000. Failed preflights are kept in `preparation/preflight-history/01` and `02`; there were zero scored model calls before the corrections and the successful new freeze. Earlier M4/G1 sources were not edited. The initial Phoenix startup was also retained and replaced with the existing HTTP-only launcher before the successful controls.

Finalized audited LLM spans contain the real Ollama duration fields. The early `_generate` journal's message metadata is empty because LangChain merges `generation_info` afterward; the independent report therefore reads the finalized trace output, not an invented zero-duration substitute. Request/usage/wall-time journal counts were still cross-checked against the same traces and checkpoint events.

Main active campaign times were approximately 21.98 minutes for Ministral, 21.10 for Granite, 31.09 for Qwen and 20.43 for Llama (about 94.60 minutes total, excluding initial deployment/preflight and later diagnostics). Each includes its simulator setup/reset/verification/audit work; these are not model-only times. Main model requests were 238, 80, 286 and 404 respectively, all under their own 643-request caps, with zero infrastructure reserve uses. The four post-run probes were separate and used no robots.

To inspect the installed models from the remote project folder:

```bash
cd '/media/naeem/d1/marvel proj'
OLLAMA_HOST=127.0.0.1:11439 runtime/bin/ollama list
cat results/operator-status.json
```

ROS Python environments live **inside the container**; do not expect the host's Python 3.13 terminal to provide Jazzy's Python 3.12 modules. Keep both source repositories and the frozen experiment snapshot distinct. The original operator refuses a duplicate run into the completed output directory. Any later test should use a new dated study/version, with failures and consumed budgets preserved.
