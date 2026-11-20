# Phase 1: frozen exploratory Qwen serving screen

Client date: **2026-11-12**. Authorization: owner instructed "ok now commence
phase 1" after receiving the proposed profiles/gates and Phase 0 reports.
This starts a new bounded campaign. Phase 0's two charged requests remain
separate and are not reset, replaced or included as profile observations.

## Question and scope

Does the q8_0 KV serving package increase generation throughput by at least
1.5 times a fresh matching A reference while retaining at least 9/10 parsed
family tool-call decisions, without new prompt truncation or more cap hits?
This is a known-input first-turn replay, not held-out correctness, robot execution
or a causal full-loop speed experiment. No Sol/OAuth/Gazebo/tool execution.

The clean completed Phase 0 hardware response remains outstanding at launch.
A's discarded warm-up will supply a new hardware observation under matching
effective settings; it does not retroactively complete or replace Phase 0.
If that observation cannot be verified, stop before measured requests.

## Profiles and order

1. A: original unset/auto Flash Attention policy, effective FA enabled verified;
   f16 KV, context 8192.
2. B: explicit FA on, q8_0 KV, context 8192. Verify actual K/V precision and FA.
3. C: same as B, context 6144, **only if B passes all Stage 1 candidate gates**.
   Phase 0 has not independently established a context-size bottleneck.

The order is fixed A then B, conditionally C, with a fixed 30-second unloaded
cooldown before each subsequent profile. One block per profile leaves an order/
thermal limitation; record temperature, clocks and power where available and
make no strong causal/generalized speed claim. No D or weight downloads.

All profiles: pinned Ollama 0.40.6 binary; qwen3.5:9b Q4_K_M, digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90;
temperature 0, seed 42, mmap true, reasoning false, caller streaming false,
client response cache false, maximum 1024 generated tokens/request. The pinned
adapter's actual API transport streams internally and assembles the response.
Use ConfiguredChatOllama without executing returned tools.

Separate owned hidden server processes, serialized on the WSL-private address,
port 11437. Process-local environment only, one slot/model, local models only,
no pruning or cloud. Preserve server prompt-cache behavior, two-minute keep-alive
and the same request order in every profile; report reuse instead of pretending
client cache=False disables it. No normal server is restarted or reconfigured.

## Fixed inputs and request schedule

Copy and hash Phase 0's existing decoded replay inputs and proposed manifest
before any Phase 1 output. Ten repetition-1 macro first turns, one per family,
plus the actual 4027-token later-turn safety input. Original messages, content,
tool schemas and opaque history identifiers are preserved through the same
adapter. No instructions/examples are added. The safety input is not a first-turn
selection case. No fixture is chosen based on new model output.

Each profile: one discarded warm-up using the constrained-movement fixture;
then ten family inputs in manifest order; then the safety input; then one
repeat each of constrained movement, healthy inspection and ambiguous goal.
Total 15 requests/profile. Repeats measure stability, not independent variance.
The warm-up is excluded from performance/agreement/cap comparisons but counted
in all resource totals and retained with full output.

## Candidate rule and analysis

- Primary throughput: median eval_count / (eval_duration/1e9) over the 11 unique
  measured inputs. B/C must be at least 1.5 times fresh A, not historical M4.
- Agreement: at least 9/10 family inputs against A on the first measured pass.
  Compare parsed tool name and arguments, excluding call IDs. Preserve the whole
  ordered call list and report malformed/multiple/missing calls. A matching empty
  valid-call list is reported as the same no-tool decision, not proof of matching
  prose or correct clarification. Report safety-input agreement separately.
- No prompt-token mismatch from each input's historical expected count; mismatch
  is a setup/context-equivalence failure, not silently labeled proven truncation.
  Record available explicit server truncation diagnostics and context/output room.
- No increase in output-cap hits on the same 14 measured requests (unique+repeat).
  Count eval_count>=1024 or done_reason=length; report unique/repeat totals too.
- Report A versus historical calls, B/C versus A, within-profile repeat stability,
  full outputs side by side for every mismatch, all timings/counts, loaded ps,
  offload, buffers, physical VRAM and temperatures. API allocation percentages
  are not automatically physical-residency measurements.

Decision requires complete valid paired data. Otherwise report incomplete or no
demonstrated candidate, not failure-free imputation. Matching a wrong baseline
decision is still agreement, not correctness. No full-loop speed/reliability gain
is claimed. C is not selected after seeing its outputs; its condition is fixed.

## Limits, preflight and stops

Stage 1 A/B: at most 30 requests / 30720 possible generated tokens. Conditional
C: at most 15 additional / 15360. Entire Phase 1: at most 45 / 46080, including
warm-ups, errors and censored requests. No inference retries or hidden repairs.
Request timeout 180 seconds; external request deadline 210 seconds; worker setup
60 seconds; whole campaign 9000 seconds including server setup/cooldowns. Calls
are durably reserved before dispatch; never replay a reservation after interruption.

Review Windows/WSL process and GPU results **before launch**, before each request,
and during long requests. Known editor/simulator/unowned model workloads stop the
run. Desktop composition/VS Code/OS display activity is recorded; no other app is
closed. Any observed browser video-decode activity above 2%, or non-display GPU
process above 2%, fails the conservative gate (adapter-specific exclusion is not
assumed). Before requests, NVIDIA utilization must be <=10% in each of three
samples. During generation the own-model load is excluded from external-process
checks; NVIDIA total utilization is not treated as external contention then.

Stop on contention, digest/version mismatch, invalid effective FA/cache/context,
missing timing/usage, prompt-count mismatch, external timeout, unavailable model
or unexpected request failure. Retain completed/censored records and stop without
retry. Do not kill a user's applications. Stop/unload only the owned server tree.
Metadata/show/ps queries and empty unload requests do not generate tokens.

Scripts, fixtures, protocol, binary and preserved source checks are hashed before
the first request. Validate payload construction offline first. M4's 950-file
preservation manifest and 62 frozen source hashes must still match at closeout.
Keep the living roadmap and master current, with original dated reports retained.
