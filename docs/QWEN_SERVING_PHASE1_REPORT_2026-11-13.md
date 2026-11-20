# Qwen serving Phase 1: results and decision

Date: **2026-11-13**. Status: **A/B complete; no serving candidate retained**.

The inexpensive KV-cache serving change did not meet the predefined screen.
It saved some GPU memory without increasing offloaded layers, produced slightly
lower observed generation throughput, and changed several tool calls. Keep the
existing A configuration as the reference. This is not evidence that all of B's
changed choices are worse, or that Qwen cannot improve through other means.

## What was tested

This was a simulator-free replay of known M4 requests, separate from frozen
M1-M5 results and Phase 0. No tools were executed. No Sol/OAuth requests were
made, and no new robotic correctness scores were assigned.

Both profiles used the pinned Ollama **0.40.6**, Qwen3.5:9b **Q4_K_M**, context
**8192**, temperature **0**, seed **42**, `think=false` and **1024 output
tokens/call**. All fourteen paired API request bodies matched exactly, including
messages, tool definitions and options. Client response caching remained off;
the server's existing prefix-cache policy remained active. The actual adapter
transport streamed internally, as recorded in Phase 0.

| Profile | Effective Flash Attention | K/V cache | GPU layers |
|---|---|---|---|
| A: original serving reference | Enabled under original auto policy | f16 | 17/33 |
| B: candidate serving package | Explicitly enabled | q8_0 | 17/33 |

The model digest was unchanged:
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
B changes a serving package; this design does not independently isolate the
effects of explicit FA selection from cache precision.

The schedule used ten first-turn macro-condition family inputs, the archived
maximum-length input (**4027 prompt tokens**, a later primitive-condition turn),
and three predetermined repeats. Primary throughput is the median over the
eleven unique inputs. Warm-ups and repeats do not enter that median. Generation
rate is `eval_count / (eval_duration / 1e9)`.

## Completed results

| Measure | A | B |
|---|---:|---:|
| Measured requests | 14 | 14 |
| Unique-input median generation tokens/s | 8.388 | 8.082 |
| Unique-input rate range | 7.796-10.142 | 7.652-8.863 |
| Family tool calls matching historical M4 /10 | 10 | 7 |
| Within-profile repeat agreements /3 | 3 | 3 |
| Output-cap hits /14 measured | 0 | 0 |
| Expected prompt count and output room | Pass | Pass |
| Measured input tokens | 23,687 | 23,687 |
| Measured output tokens | 2,212 | 3,134 |
| Summed measured client request seconds | 278.528 | 396.829 |
| Summed measured provider request seconds | 289.886 | 414.462 |
| Invalid parsed-call records | 0 | 0 |
| Multiple-call response records | 0 | 0 |

B/A median throughput was **0.9635**, approximately **3.7% lower observed
throughput**, against the required **1.5-times speed**. Its family agreement
with A was **7/10**, against **9/10** required. The separate longest-input safety
call also differed. Prompt counts/output room passed and no extra cap hits
occurred, but these did not compensate for the failed speed/agreement gates.
**B failed the screen. C was skipped; D was not scheduled.**

B generated **41.7% more output tokens** in the matched measured block. The
client request totals were approximately **4.64 minutes for A** and **6.61 minutes
for B**. These are summed replay request times, not robot task completion times.
The approximately **25.8-minute campaign elapsed time** also includes setup,
gates, cooldowns and the infrastructure interruption; it is not an inference
benchmark. Client and provider timing views remain separate, following the clock
limitations documented in Phase 0.

Three family inputs changed: already-satisfied, ineffective-command and
partial-command. The safety input also changed. Changes included different
observation requests, readiness inspection versus movement selection, and a
failure-report call instead of skill reselection. These tools were never
dispatched or validated against a running environment in this probe. In
particular, matching A's historical wrong skill is not correctness, and a changed
call is not automatically a regression. See the
[full model outputs and parsed-call differences](../artifacts/qwen-serving-phase1-20261112/MISMATCHES.md).

## Memory observations

GPU KV allocation fell **128 to 68 MiB**, a **60 MiB** saving. The effective logs
verified FA and K/V precision; GPU layer offload stayed **17/33**.

Post-warm-up NVIDIA snapshots showed A **4963 MiB used / 959 MiB free**, and B
**4915 MiB used / 1007 MiB free**, on the reported **6141 MiB** device. These are
snapshots, not peaks or synchronized measurements. They include desktop and
other allocations. Ollama's loaded-size estimates were approximately **6.4 GB**
for A and **6.3 GB** for B; `ps` reported **45%/55% CPU/GPU** for both. Those
allocation estimates should not be substituted for physical residency readings.
The proposed small KV saving did not eliminate meaningful CPU offload.

## Infrastructure deviations and exact resources

The initial preflight made zero model calls. After Chrome fully closed, a fresh
idle gate passed with NVIDIA samples **0%, 0%, 0%**. A pre-inference amendment
concerning small desktop-rendering activity is preserved with the original
freeze and did not change model inputs, serving settings or candidate gates.

A completed its fifteen requests. B's original warm-up then returned, but the
coordinator incorrectly required the literal log text `Flash Attention enabled`.
B's effective context log instead said `flash_attn = enabled`, with q8_0 K and V.
This was an observer error, not a model failure. The stopped checkpoint and all
original outputs remain archived.

A separately frozen continuation corrected log recognition and ran only the
unstarted B measured cases, preceded by **one extra discarded recovery warm-up**.
No A request or completed measured B outcome was rerun. This changed actual A/B
cost from thirty to **thirty-one requests**, within the original **45-request**
ceiling. It is a declared deviation; the run should not be represented as an
uninterrupted execution of the original schedule.

| Actual charged/returned cost, including all warm-ups | A | B | Total |
|---|---:|---:|---:|
| Requests | 15 | 16 | **31** |
| Input tokens | 25,378 | 27,069 | **52,447** |
| Output tokens | 2,560 | 3,824 | **6,384** |

There were **zero unreturned requests**, robot dispatches or hosted calls. The
remaining fourteen slots were not spent. Had B passed, a complete fifteen-call
C block would have required deferral rather than increasing the ceiling. In the
actual result, C was already ruled out by the failed gates. The frozen automatic
report still displays its original `/15` denominator for B; the actual total is
sixteen, including two warm-ups, with exactly fourteen measured requests.

## Checks and interpretation

All checks passed for **950 protected M4 files**, **62 M4 frozen source files**,
**93 Phase 0 manifest entries**, **10 Phase 1 frozen files**, **5 continuation
files**, and **13 first-segment snapshot files**. All 31 returned token counts
matched provider metadata; fourteen paired API request bodies were identical;
reservations and aggregate token totals matched the checkpoint. Owned test
servers were confirmed stopped. No Git push or public upload was performed.

The result is an exploratory negative screen, with one A block followed by B,
known cases, an interruption/reload, and three stability repeats rather than
independent repeated blocks. Order, thermal conditions, cache history and changed
response lengths limit causal interpretation. The study does not establish
robotic reliability, general Qwen/Sol parity, or Qwen's best possible serving
configuration. No new Phoenix/Gazebo trial audit is claimed for these text-only
requests.

The useful conclusion is narrower: **this tested q8_0 serving package did not
deliver the predefined worthwhile speedup while preserving recorded calls**.
Keep A. Any next work on intent/schema, concise examples or thinking mode remains
a separate prospective decision with fresh cases and explicit correctness and
resource gates. No such experiment was started automatically.

## Evidence to share

- [Full completed report, per-request table and caveats](../artifacts/qwen-serving-phase1-20261112/COMPLETED_REPORT.md).
- [Machine analysis](../artifacts/qwen-serving-phase1-20261112/analysis.json),
  [per-request CSV](../artifacts/qwen-serving-phase1-20261112/request-summary.csv),
  [warm-up-inclusive costs](../artifacts/qwen-serving-phase1-20261112/cost-summary.json),
  and [final checks](../artifacts/qwen-serving-phase1-20261112/closeout-validation.json).
- [Frozen protocol](../artifacts/qwen-serving-phase1-20261112/PROTOCOL.md),
  [continuation declaration](../artifacts/qwen-serving-phase1-20261112/continuation/CONTINUATION_NOTE.md),
  and [final checkpoint](../artifacts/qwen-serving-phase1-20261112/status.json).
- [Maintained Claude-roadmap tracker](CLAUDE_QWEN_ROADMAP_LIVE.md) and
  [project master README](../PROJECT_MASTER_README.md).
- [Phase 0 dated report](QWEN_TIMING_PHASE0_REPORT_2026-11-12.md), retained as its
  original checkpoint rather than rewritten to incorporate Phase 1 outcomes.
