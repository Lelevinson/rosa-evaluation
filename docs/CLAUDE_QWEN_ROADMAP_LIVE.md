# Claude Qwen roadmap: living progress report

Last updated: **2026-11-13**.

**Current position: Phase 1 A/B completed; no serving candidate retained.** A's
eleven-unique-input median was **8.388 tokens/s**; B's was **8.082 tokens/s**,
or **0.963 times A**, below the 1.5-times gate. B matched A's parsed family calls
on **7/10** inputs, below the 9/10 gate. Both completed fourteen measured requests
without an output-cap hit; prompt counts/output room passed and repeats agreed
3/3 within each profile. C was skipped under the frozen gates. D and all new
full-loop correctness experiments remain unstarted.

Actual Phase 1 cost was **31 returned requests, 52,447 input tokens and 6,384
output tokens**, with no unreturned requests or robot dispatches. A had one
discarded warm-up; B had two because a log-validator false negative stopped the
first segment. The separately frozen observer correction preserved every
completed output and added only one declared recovery warm-up before unstarted
B measurements. The original global ceiling stayed 45; even if B had passed,
the full 15-request C block would not fit the remaining 14 slots. This is a
documented infrastructure deviation, not a clean uninterrupted original run.

See the [dated results](QWEN_SERVING_PHASE1_REPORT_2026-11-13.md),
[full completed report](../artifacts/qwen-serving-phase1-20261112/COMPLETED_REPORT.md),
[checkpoint](../artifacts/qwen-serving-phase1-20261112/status.json) and
[validation](../artifacts/qwen-serving-phase1-20261112/closeout-validation.json).
All owned test servers stopped. Protected M4 evidence, sources and Phase 0 hashes
passed verification. Reports and evidence remain local; no Git push occurred.

Phase 0 archived analysis remains complete. Its mismatched request and stopped
correction remain preserved as two separate charged requests; neither is reused
as a Phase 1 observation. A's warm-up supplied the planned fresh hardware observation,
without retroactively changing Phase 0's incomplete clean-baseline checkpoint.

This is the canonical **maintained tracker for Claude's Qwen timing/serving
roadmap**, separate from the project-wide M1-M5 milestones and original six-stage
research roadmap. Update the current state, evidence, decisions and next actions
as work progresses; do not turn this into only a chronological diary. Updates
occur during project work, not through an unattended background monitor.

For a shareable account of the first checkpoint, use the
[2026-11-12 Phase 0 report](QWEN_TIMING_PHASE0_REPORT_2026-11-12.md).

## Objective and scope

Determine whether inexpensive serving changes improve local Qwen generation
throughput on this laptop while preserving its recorded first tool calls closely
enough to justify a later full-loop test. Begin by diagnosing existing time costs
and actual memory/offload behavior. A negative finding is acceptable.

The project goal remains improving ROSA's surrounding software. Bringing Qwen's
verified correctness closer to Sol on bounded tasks is a broader proposed goal;
equal general capability or speed is neither established nor promised. This
serving probe cannot establish goal satisfaction, robotic reliability or transfer.
Text-only replay uses known M4 inputs; it is not a held-out correctness test.

No new Gazebo, Sol, OAuth or robot tool execution belongs to this serving probe.
M4 results, frozen sources, Baseline v1 and original M1-M5 reports remain intact.
JTVR, memory and planner development remain outside this roadmap.

## Current progress and gates

| Work item | State | Evidence / remaining condition |
|---|---|---|
| Phase 0.1: field inventory | Complete | Six fields on 144/144 calls; cached-token field not recorded |
| Phase 0.2: all 40 trial rows | Complete | Condition/family, ending, calls/tokens, task/native time retained |
| Phase 0.3: time decomposition | Complete with clock limitation | Direct provider components available; monotonic and timestamp totals disagree and remain separate |
| Phase 0.4: trial/call regression | Complete, exploratory | Trial R squared 0.99314; predictor correlation 0.83159; no causal interpretation |
| Phase 0.5: ending-type split | Complete | Five length-stop trials account for 27.91% of task time |
| Phase 0.6: matched comparison | Complete | All attempts and 13 both-pass pairs reported separately |
| Phase 0.7: original checkpoint incomplete; new observation available | Phase 1 A warm-up completed | Fresh matching hardware/response verified in Phase 1; original Phase 0 attempts remain unchanged |
| Phase 0: headroom assessment | Estimate followed by B measurement | B saved 60 MiB GPU KV but offload remained 17/33 and speed gate failed; C's extra context reduction was not tested |
| Phase 0 handoff decision | Owner authorized progression | Use A's discarded warm-up for a fresh verified hardware observation; retain earlier incomplete attempts |
| Phase 1 / Stage 1: A versus B | Complete; B failed candidate gates | A 8.388 vs B 8.082 tokens/s; B/A 0.963; family agreement 7/10; no cap hits; observer interruption preserved |
| Phase 1 / Stage 2: C | Skipped | B failed speed/agreement gates; no Phase 0 context-size bottleneck established |
| Optional D: smaller weight quantization | Not scheduled | Only if useful offload motivation and separately approved; different weights/digest |
| Later full-loop correctness study | Separate future decision | A serving candidate needs fresh verified outcomes; no automatic progression |

Phase 1's **Stage 1** is the A/B screen; its **Stage 2** is the conditional C
screen. These names do not refer to original research Stages 1-6 or milestones
M1-M5. This avoids treating a serving check as a new Gazebo milestone.

## Findings that currently guide decisions

| Established observation | Meaning / limitation |
|---|---|
| Generation: 4223.744 / 4417.966 server seconds, 95.60% | Generation dominates these archived request durations |
| Historical median generation rate: 7.807 tokens/s | Archive-derived; not a new serving speed claim |
| Length-stop trials: 1220.522 s, 27.91% of task time | Potential cost of unsuccessful long generation; not proof that fewer tokens improve correctness |
| Historical FA already enabled | Do not frame enabling FA as a newly demonstrated improvement over M4 |
| Historical offload: 17/33 layers; GPU KV 128 MiB f16 | KV savings alone have limited capacity to eliminate CPU weights |
| Cached-token count absent, but server prompt cache active | Client cache=False did not disable server reuse; future cache policy must be explicit |
| Maximum prompt: 4027 tokens, primitive partial_command call 8 | A 4096 context leaves inadequate output room; safety fixture is a later turn |
| Clock totals disagree | Keep provider, trace and task timer views separate; do not manufacture overhead |
| Corrected live log: FA enabled, f16, 8192, 17/33 | Valid partial observation; clean completed baseline still not obtained |
| Phase 1 A warm-up: complete, 1691 input / 348 output tokens | Effective FA/f16, 8192 context, digest and prompt count passed; first tool call matched historical stage_left |
| Phase 1 A profile: 15/15 returned | 25378 input / 2560 output tokens including warm-up; unique-input median 8.388 tokens/s; ten historical tool decisions and three repeats match |
| Phase 1 B profile: 16 returned, including two warm-ups | 27069 input / 3824 output tokens; median 8.082 tokens/s; 7/10 family agreement, safety call differs, repeats 3/3 |
| A/B GPU layers remain 17/33; GPU KV 128 to 68 MiB | 60 MiB KV saving did not increase layer offload or meet speed gate |
| Measured output: A 2212 tokens, B 3134 | B produced 41.7% more; summed client request times 278.528 vs 396.829 seconds; not robotic task times |
| M4 Qwen: primitives 15/20, macro 14/20 | Efficiency findings did not establish a general reliability improvement |

Native monotonic time summed to 36.489 s across all 40 trials; task time summed
to 4373.357 s. The non-native remainder is not pure inference time. The full
technical report explains the clock mismatch and records all cost views.

## Phase 1 configurations: frozen on 2026-11-12

| Profile | Proposal | Interpretation / gate |
|---|---|---|
| A | Pinned M4 weights/server; 8192 context; original unset/auto FA policy with effective FA verified enabled; f16 KV | Fresh live reference; verify runtime, not only startup flags |
| B | Same weights/version/context and model options; explicit FA enabled, q8_0 KV | Measured GPU KV saving 60 MiB; offload unchanged; speed/agreement gates failed |
| C | B with context 6144 | Conditional; estimated GPU KV saving about 77 MiB relative to historical A; validate input/output room |
| D | Smaller quantization of the same model family | Optional distinct model configuration; record digest; first-call agreement cannot establish adequate correctness |

Common proposed settings: Ollama 0.40.6, qwen3.5:9b Q4_K_M for A/B/C, temperature
0, seed 42, thinking disabled and 1024 output tokens/call. Actual API transport
in the pinned adapter streams internally despite LangChain streaming=False.
Client response cache and server prompt cache are different settings. D breaks
the unchanged-weights norm and must be labeled accordingly.

Full A/B/C digest:
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
Backend support, effective cache precision and actual allocation are not assumed
from environment variables. Avoid changing the normal M4 server; use isolated
process-local settings and capture the effective runtime.

## Frozen Stage 1 inputs, controls and decision rule

Use ten recorded repetition-1 first-turn macro inputs, one per M4 family, plus
the actual maximum-length input across either condition. Run each once per
profile; repeat only three predetermined inputs once: movement with constraints,
healthy inspection and ambiguous goal. One discarded warm-up per profile gives
**30 total A/B inference requests**; all 11 inputs are distinct. The owner has
authorized launch; no completed result is inferred from that authorization.
The [input manifest](../artifacts/qwen-timing-probe-20261112/proposed-stage1-inputs.json)
and [decoded fixtures](../artifacts/qwen-timing-probe-20261112/replay-inputs.json)
were selected before any Phase 1 output.

The previously proposed defaults were adopted and frozen for the authorized screen:

- At least **1.5 times A's newly measured median generation tokens/s**; neither
  the old M4 median nor the FA-disabled observation is the Phase 1 reference.
- At least **90% first-call agreement** on the ten family inputs, meaning 9/10;
  the context-safety input is reported separately. This is the frozen adaptation
  from the earlier 18/20 rule for the smaller ten-family screen.
- No newly truncated prompts and no increase in output-cap hits, assessed on
  the same prespecified comparable runs. Report repeats separately for stability.
- Record A versus historical outputs, B/C versus A, every mismatch, malformed or
  missing call, finish reason, timing field and resource cost. Compare parsed tool
  names/arguments, not opaque IDs. Agreement can preserve a wrong historical call.

The [frozen protocol](../artifacts/qwen-serving-phase1-20261112/PROTOCOL.md) fixes
warm-up, input order, A-then-B order, conditional C, 30-second unloaded cooldown,
preserved server prefix caching, exact prompt-count equivalence, 180-second
request/210-second external deadlines, 9000-second campaign limit and no retries.
The maximum Phase 1 envelope is 45 requests / 46080 possible output tokens;
the original schedule used 30 if B failed. The declared observer-recovery warm-up
made the actual A/B total 31 without increasing the ceiling. Repeats check stability, not
independent variance. One profile block per condition leaves order/thermal
limitations. No input may be selected after seeing new outputs.

Original proposed stops include digest/version mismatch, inability to verify the
intended server settings and competing GPU workloads. The original full-GPU plus
prompt-dominance stop is not established here. A decisive no-headroom stop is
also not established: small KV savings cannot eliminate all offload, but that
does not prove no possible runtime benefit. Review this before spending calls.

## Current exceptions and resource accounting

| Attempt | Charged calls | State |
|---|---:|---|
| hardware-01 | 0 | Pre-dispatch transport assertion error; retained |
| hardware-02 | 0 | PowerShell setup-variable collision; retained |
| hardware-03 | 1 | Returned 33 tokens under accidental FA-disabled configuration; excluded as a matching baseline |
| hardware-04 | 1 | Approved correction; stopped for unresolved browser GPU activity; no complete response |

**Phase 0 total: two charged inference requests. Its remaining allowance is zero.**
Known returned output is 33 tokens. The censored request has a 1024-token upper
bound; server progress reached at least 267 tokens but is not final usage. No
automatic inference retries, Sol calls, simulator runs or robot tool dispatches.
Both Phase 0 server trees were confirmed stopped. Phase 1 is a new, separately
authorized campaign; its counters are never mixed with these historical attempts.

**Phase 1:** the initial preflight stopped with **zero charged model requests**.
After Chrome closed and the gate passed, the coordinator restarted. A's warm-up
returned and passed runtime validation; all 15 A requests have returned.
Phase 1 A totals are 25378 input and 2560 output tokens including the discarded
warm-up. Its 11-unique median is 8.388 tokens/s; no output cap was hit. B completed
16 returned requests including its original and recovery warm-ups: 27069 input /
3824 output tokens. Its median was 8.082 tokens/s. Actual total is 31 requests,
52447 input / 6384 output tokens, no unreturned requests; all 28 measured requests
have expected prompt counts and no cap hits. B failed the candidate screen.
Charged/returned counts are maintained in its
[checkpoint](../artifacts/qwen-serving-phase1-20261112/status.json). All 11 inputs
passed offline pinned-adapter validation; six acceptance-boundary checks passed.
The prelaunch freeze verified 950 preserved M4 files and 62 frozen sources.
Original freeze SHA-256: `f95790c506e919f2d6d19d57e0ef8a1eed838cf194304c4749306c2b27fb6369`.
Current amended freeze SHA-256: `138beb9c0d3e5a68164e50a815b0ef7672fb9ace87f27cc2c52a1befc89af195`.
The [pre-inference amendment](../artifacts/qwen-serving-phase1-20261112/PRE_INFERENCE_AMENDMENT_01.md)
was recorded with zero Phase 1 model requests. It permits Chrome 3D window
rendering <=5% as bounded desktop UI, while video-decode/compute >2% and NVIDIA
total >10% still stop the run. This repairs an inconsistent desktop classification;
it does not establish a fully interference-free machine. Original freeze and all
nine original files are retained under `pre-inference-amendment-01/original/`.
Model profiles, inputs, budgets, deadlines and statistical gates did not change.
The A/B/C implementation is isolated from original ROSA and M4 source files.
The zero-call attempt is preserved in `preflight-attempt-01/`; only its runtime
markers and generated outputs were archived to prepare a fresh preflight.
At that pre-inference amendment no reservation had been removed/reset and no
Phase 1 output inspected. The later observer correction occurred after A and B's
original warm-up, preserved all results, and changed only runtime recognition and
continuation accounting. Neither update changed the inputs or candidate gates.
Original source/threshold history is retained. Earlier failed idle samples did not
prove a competing compute workload; the actual run began after Chrome closed and
the quiet-GPU gate passed.

The FA override and the first two setup failures were implementation errors.
Launching hardware-04 before reviewing the full GPU-engine preflight was a
protocol exception. Retain these failures and warnings in any later report;
do not reclassify them as Qwen capability failures or replace them with successful
reruns. Counter samples did not establish adapter-specific absence of contention.

## Next actions, in order

1. Keep the completed analysis, raw outputs, protocol amendments and manifests
   intact. No worker or model run remains active.
2. Retain A as the serving reference; B was not demonstrated useful under the
   predefined screen. Do not run C or download D as an automatic follow-up.
3. Share the dated and full reports, including the interruption, timing views
   and mismatch evidence. Do not equate first-call agreement with correctness.
4. Decide separately whether fresh intent/schema/examples or thinking-mode work
   is worthwhile within the project deadline. Freeze cases, resource budgets and
   correctness/overhead gates before any such new experiment.
5. Keep this tracker and the project master current when a new decision is made.

The earlier prompt/intent/examples/thinking recommendations remain separately
[assessed proposals](QWEN_NEAR_SOL_PROPOSAL_ASSESSMENT_2026-11-05.md). They are not
Phase 1 serving profiles. If pursued later, use a grouped development/held-out
split, select using development only, freeze one candidate, and run fresh Qwen
baseline/candidate/Sol comparisons. A schema must work with the actual tool
parser. Thinking/resource changes require fair controls and all costs counted.
No numeric near-Sol correctness target or new correctness protocol is frozen.

## Evidence and update rules

Primary current sources:

- [Phase 1 dated results](QWEN_SERVING_PHASE1_REPORT_2026-11-13.md),
  [complete results and deviations](../artifacts/qwen-serving-phase1-20261112/COMPLETED_REPORT.md),
  [per-request CSV](../artifacts/qwen-serving-phase1-20261112/request-summary.csv),
  [full mismatches](../artifacts/qwen-serving-phase1-20261112/MISMATCHES.md), and
  [closeout verification](../artifacts/qwen-serving-phase1-20261112/closeout-validation.json).
- [Phase 1 frozen protocol](../artifacts/qwen-serving-phase1-20261112/PROTOCOL.md),
  [freeze](../artifacts/qwen-serving-phase1-20261112/freeze.json),
  [live status](../artifacts/qwen-serving-phase1-20261112/status.json), and
  [current results report](../artifacts/qwen-serving-phase1-20261112/PHASE1_REPORT.md).
- [Dated shareable report](QWEN_TIMING_PHASE0_REPORT_2026-11-12.md).
- [Detailed Phase 0 report and 40-trial appendix](../artifacts/qwen-timing-probe-20261112/PHASE0_REPORT.md).
- [Machine-readable probe status](../artifacts/qwen-timing-probe-20261112/status.json).
- [Archived analysis](../artifacts/qwen-timing-probe-20261112/analysis.json),
  [per-trial CSV](../artifacts/qwen-timing-probe-20261112/per-trial.csv),
  [per-call CSV](../artifacts/qwen-timing-probe-20261112/per-call.csv).
- [First mismatched observation](../artifacts/qwen-timing-probe-20261112/HARDWARE_CHECK_REPORT.md)
  and [corrected stopped observation](../artifacts/qwen-timing-probe-20261112/CORRECTED_HARDWARE_CHECK_REPORT.md).
- [Preservation evidence](../artifacts/qwen-timing-probe-20261112/source-integrity.json)
  and [probe manifest](../artifacts/qwen-timing-probe-20261112/manifest.json).
- [Project master README](../PROJECT_MASTER_README.md) for project-wide context.

For every subsequent roadmap work session, update this file's date, current
position, progress table, open gates, findings, cumulative costs and next actions.
Link each new protocol/result/evidence package. Add a concise dated event below.
Distinguish proposed, authorized, frozen, running, stopped and complete states.
Do not infer liveness from saved checkpoints or assume an unfinished trial passed.
No background update or automatic restart is implied.

Keep dated reports as checkpoints; issue a new dated report or explicit addendum
for later findings rather than rewriting earlier observations. Preserve original
scores and budgets; new allowances and attempts must remain distinguishable.
Update the project master pointer/current context when the roadmap changes, while
retaining M1-M5 source results. Never write credentials into these records.

## Dated decisions and progress

| Date | Event / decision | Effect on current plan |
|---|---|---|
| 2026-11-12 | Owner authorized starting Phase 0 | Archived analysis and bounded hardware check began; no automatic Phase 1 progression |
| 2026-11-12 | 40 trials / 144 calls analyzed; six provider fields found | Direct timing available; estimation fallback unnecessary |
| 2026-11-12 | Historical FA enabled and small GPU KV cache established | Easy FA/cache speed-win assumption weakened; headroom remains an estimate |
| 2026-11-12 | First live request returned with accidental FA disable | Retained mismatch; not a matching baseline or a model regression |
| 2026-11-12 | Owner approved one corrected request | Additional allowance of one; original request retained |
| 2026-11-12 | Corrected request stopped after browser GPU activity identified | Runtime matching partially verified; no complete clean response; allowance spent |
| 2026-11-12 | Owner requested a dated report and continually maintained roadmap record | This tracker becomes the current roadmap handoff; no new experiments authorized |
| 2026-11-12 | Owner instructed "ok now commence phase 1" | Separate serving screen authorized; previous defaults frozen; A/B max 30, C max 15 only if B passes |
| 2026-11-12 | Offline validation and freeze completed; coordinator launched | 11 input constructions, six decision-rule checks, 950 M4 files and 62 frozen sources verified; live results pending |
| 2026-11-13 | First Phase 1 preflight stopped, then two metadata-only rechecks failed | 0 model calls; original preflight archived; settings and budget unchanged; quiet-GPU condition pending |
| 2026-11-13 | Owner confirmed apps paused and requested recheck/run | New check still saw browser GPU activity; no inference dispatched |
| 2026-11-13 | Adapter inventory and pre-inference amendment recorded | Small Chrome 3D UI rendering allowed; original freeze/files retained; model and statistical settings unchanged |
| 2026-11-13 | Amended recheck still showed video decoding about 3.2% and total NVIDIA up to 18% | Still stopped before all model calls; owner asked to fully exit Chrome; no new inference permission needed |
| 2026-11-13 | Owner confirmed Chrome fully closed; fresh gate passed 0%, 0%, 0% | Coordinator restarted without changing frozen settings; first profile A warm-up reserved and in flight |
| 2026-11-13 | A warm-up returned and runtime verification passed | 1691 input / 348 output tokens; FA enabled, f16, 8192, 17/33 offload; matched historical tool call; measured A replays started |
| 2026-11-13 | A finished all 15 requests | Ten family decisions match history, three repeats agree, no cap hits; median unique throughput 8.388 tokens/s; fixed cooldown before B |
| 2026-11-13 | B warm-up returned; overly literal FA-log validator stopped the first segment | Correct FA/q8_0 runtime retained; observer error, not a model failure; no measured B outcome rerun |
| 2026-11-13 | Separately frozen observer continuation completed B | One extra discarded warm-up; actual A/B31 requests under original45 ceiling; full original source/output history retained |
| 2026-11-13 | A/B screen closed; B failed speed and agreement gates | B/A0.9635, 7/10 family agreement, no cap hits; C skipped; no candidate adopted; servers stopped and preservation/accounting checks passed |
