# G1 three-model extension — combined launch preflight

Date: **2026-11-19**. **Exploratory backends, added after Sol and Qwen results.**

**READY for owner review; NOT LAUNCHED.** One acknowledgment of this record is
required by the owner's supplied T2/T4 instructions. It covers the three models
below, in order, with **228 scheduled mock attempts** and separate **611-request,
eight-hour limits per model**. Six auxiliary load/unload requests have already
been charged: two per model. Thus at most **609 additional requests per model**
remain, including inference, eligible retries and any final unload. The aggregate
ceiling is **1,833**, not a shared pool that a model can borrow from.

The earlier Qwen container/image became unavailable during preparation. The new
container uses another **already installed ROS 2 Jazzy image**, disclosed below.
This is an environment change, not an identical-image replication. The pinned
Python dependencies and all scripted controls passed in the replacement container.
No protected source, original experiment, model, prompt, case or scorer was edited.

## What will run

- Lab machine via SSH only; models run sequentially, not concurrently.
- The same frozen **38 AI-authored G1 cases × primitives/macro**, 76 attempts per
  model. Arm and base operations are mocks. ROS 2 Jazzy is installed in the Docker
  environment; these trials do not exercise real ROS interfaces, Gazebo or a robot.
- Qwen and Sol are complete and are **not rerun**. Their results and raw records
  remain unchanged. This is model-generalization exploration on previously seen
  cases, not independent case-generalization evidence or a confirmatory new study.
- No downloads, OAuth, catalogue-size probe, optional first-turn replay, Git commit,
  publication, template repair, model-specific prompting or parser workaround.

## Installed models and eligibility

Eligibility uses only server-reported tool capability and full GPU loading at
8,192 context. It does not use benchmark performance. All three passed. A model
that subsequently fails tool calling remains in the results; no substitution.

| Fixed order / exact tag | Parameters; disk bytes | Quantization; family | Advertised context | Loaded GPU layers; context |
|---|---|---|---:|---|
| `ministral-3:8b-instruct-2512-q4_K_M` | 8.9B; 6,018,857,966 | Q4_K_M; mistral3 | 262,144 | 35/35; 8,192 |
| `granite3.3:8b` | 8.2B; 4,942,891,653 | Q4_K_M; granite | 131,072 | 41/41; 8,192 |
| `llama3.1:8b-instruct-q4_K_M` | 8.0B; 4,920,753,328 | Q4_K_M; llama | 131,072 | 33/33; 8,192 |

Exact disk bytes are recorded in each `MODEL_CONFIG.json`; that record governs if
a display transcription differs. Loaded sizes equal GPU-resident sizes: Ministral
6,356,048,280 bytes, Granite 6,524,512,501, Llama 6,356,048,280 where reported by
the corresponding `LOADED_MODEL.json` and `ELIGIBILITY.json` (the latter is the
authoritative source; no missing byte quantity is estimated).

Model digests:

- Ministral: `1922f1a31a570dfb33f1f97e1e85f4110cd4c66c0364ff3572f00f17f27ef8f0`
- Granite: `fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7`
- Llama: `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`

**Use the exact digest in each sealed `MODEL_CONFIG.json` for launch checks.**
Capabilities: Ministral reports completion, vision and tools; Granite and Llama
report completion and tools. None reports a thinking capability: thinking control
is recorded as not applicable, with the unchanged common `think=false` field.
Vision is unused. Native tool support in metadata does not demonstrate successful
integration. The earlier Granite text-JSON and Llama schema failures are retained
negative evidence, not grounds for exclusion or permission to repair this run.

## Common serving profile and bounds

- Ollama **0.40.6**, isolated local endpoint `127.0.0.1:11439`.
- Original `ConfiguredChatOllama` adapter: `num_ctx=8192`, `num_predict=1024`,
  temperature 0, seed 42, `use_mmap=true`, reasoning off, client cache false.
- Actual API streaming is **true**, despite the higher-level `streaming=false`
  option. Preserve existing server prompt caching. No cache flush or timing claim
  of a cold model. Keep-alive is not expanded to guarantee residence for eight
  hours: retain the original adapter/server behavior and record loads/residency.
- Per task: **8 decision calls, 360 s, 2,048 observed output tokens, 10 native
  operations, 16 tool attempts, 3 corrections, at most 1 dispatch**. Each response
  has a 1,024-token allowance. Extra calls and retries remain charged.
- Per model: **611 total physical requests**, with at most 3 eligible retry-reserve
  requests and an **eight-hour live window** from that backend's launch. Its two
  preparation requests are included. Final explicit unloads, if needed, are
  reserved and charged separately in the operator ledger, never hidden or doubled.
- Planning reference: Sol used 200 inference requests and Qwen 198. Approximately
  200 per new model is a planning figure, not a promised count or an estimate of
  absent usage. Local caps are not provider quota; no hosted provider is used here.

Retries remain limited to explicit **HTTP 502/503/504** under the unchanged reserve.
Transport/server failures such as connection resets and OOM-related HTTP failures
are preserved for unchanged A3 censoring. No robot command is replayed. A model
length stop or a task's bounded timeout is not automatically an infrastructure
failure. Unknown parser failures are not silently reclassified as infrastructure.
Sanitized metadata can identify HTTP status/exception type but does not retain raw
CUDA error messages; telemetry supplements diagnosis without promising full detail.

## Hardware, container and tracing

- NVIDIA **RTX 4080 SUPER, 16,376 MiB**, driver **570.195.03**. `nvidia-smi` reports
  CUDA compatibility **12.8**; this is not an assertion of installed toolkit version.
- Current extension container: `marvel-g1-extension-20261119`, user 1000:1000,
  host networking, project bind under `/work`, explicit `ROS_DOMAIN_ID=0`.
- New installed image ID:
  `sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2`.
  Original Qwen image:
  `sha256:472fb4307f978886524430f2fae764e168ca95acd13c45a3edb17cc5a33c819a`.
  These differ. No claim that image changes have zero behavioral effect.
- Restart policy **no**. Python 3.12.3; verified pinned dependencies include
  langchain-core 0.3.86, langchain-ollama 0.3.10, ollama 0.6.3, pydantic 2.14.1,
  httpx 0.28.1. ROS 2 Jazzy `rclpy` and the frozen trial imports passed.
- Flash Attention enabled and f16 KV cache are recorded from the load logs.
  No default is assumed. All three loaded wholly on the GPU at 8K context.
- The recorded compute list showed the existing GNOME remote-desktop process
  using 249 MiB. Other users' applications and their separate container/server
  were not closed or modified. No competing model was resident on this endpoint.
- Three-sample GPU idle gates require every sample to be at most 5%. Preparation
  and combined preflight gates passed; another fresh gate is required before each
  backend launches. See `COMBINED_GPU_IDLE_GATE.json`. A future contention failure
  stops the sequence rather than relaxing the gate.
- GPU utilization, memory, clocks, temperature, power, process list, model
  residency and container state will be sampled about every ten seconds by the
  extension's `operator/observe_live.py`. The copied historical backend helper
  naming the old container is unused.
- Extension-owned Phoenix is healthy on loopback port 6006, with separate storage
  under `service/phoenix/`. Earlier Sol/Qwen exported traces remain preserved.
  The new database is not represented as the earlier server dataset.
- At launch, detach the root worker under a scoped `systemd-inhibit` sleep/idle
  inhibitor. Keep the lab machine powered on and available. This does not prevent
  reboot, shutdown, disconnection of storage or other users' administrative actions.

## Zero-inference evidence and protected hashes

Preparation passed **24/24 scripted controls**, **24/24 local trace audits** and
**24/24 persisted Phoenix audits** (eight per backend). These are engineering
checks with scripted responses, not evidence of actual model correctness.
Across the backends, **144 serialized request bodies** matched the unchanged
adapter byte for byte, including original messages, tool schemas and serving
options. Each model has a sealed 48-comparison hash record.

An injected response verified retention of all six expected Ollama fields:
`total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`,
`eval_count`, `eval_duration`. Empty load/unload responses omitted them and are
marked **NOT_RECORDED**. The cached-token field `prompt_eval_cached_count` was not
returned in those responses; actual benchmark availability remains not recorded
until responses exist. Do not infer throughput or missing token counts.

The new runner's missing-flag and missing-authorization checks failed closed with
zero model requests. All **3,796 original frozen inputs**, retained Sol/Qwen
protected files and three backend seals reverified. Scorer SHA-256 remains
`90b0edd6d898ac749d121de29197a669593e022160503414413e0126766e8e4d`.
See `COMBINED_PROTECTED_HASH_CHECK.json` and per-backend `freeze.json`.

New root input freeze SHA-256:
`3fe79f9d42655bb35d4dce4959b1c0d92b19a30bc710fa04181e44d61a6bb7d3`.

## Retained preparation interruptions

These all preceded benchmark execution. No failure was erased or converted into
a successful model trial; the benchmark remains **0/228**.

1. A report absent from the curated lab snapshot stopped preparation before model
   requests. The exact retained local Sol report was copied to the absent path.
2. The old container/image and Phoenix service were unavailable. Preparation
   stopped; the disclosed installed-image container and separate Phoenix were
   established. A missing Phoenix launcher module caused one retained startup
   failure before its standalone G1 helper was used.
3. Ministral's one load succeeded, but a non-UTF-8 server-log byte stopped metadata
   reading. Its load was not repeated. A bounded binary log tail was decoded with
   replacement and cross-checked against loaded-model metadata. The original
   pre-load byte offset is **NOT_RECORDED** for Ministral, so not every recovered
   log line is claimed to be a fresh-load-only line.
4. Two post-unload idle checks stopped preparation. The first failing samples were
   not retained; the next diagnostic retained 26%, 0%, 0%. Later gates passed at
   the original threshold without closing other applications. Existing load,
   unload and control receipts were reused without generating replacement trials.

## Analysis, review gates and limitations

The Qwen write pattern (2/8 primitives vs 6/8 macro; 24/28 vs 24/28 other known
goals) is retrospective. The new models test a written **exploratory H-write**:
compare raw pass-count differences in eight write-bearing versus 28 other cases.
Either write arm scoring 0/8 or 8/8 overrides to Uninformative; missing/censored
comparisons remain Uninformative. Overall Support/Against requires at least two
of the original three models; ineligible models do not lower that denominator.
Fifteen synthetic boundary checks passed on the lab, with zero inference.

This raw-count rule can give Support even when total accuracy is worse. Report
both group counts and overall correctness, not the label alone. Macros bundle
deterministic execution, and writes offer more decision boundaries than reads;
neither reduced calls nor this eight-case pattern establishes a novel algorithm
or a general reliability advantage. Do not pool pass rates across backends.

The request's proposed P3/P4 relabeling conflicts with the actually adopted
November 14 definitions. The separate Qwen addendum preserves those definitions:
**P3 is dropped horizon reliability; P4 is the unrun Qwen catalogue probe**.
P1′ is originally Sol-specific. Any descriptive application to another backend
must not be presented as its original formal prediction.

After execution, report all attempts, evaluable denominators, paired outcomes,
fault exercise, calls, tokens, native work, invalid attempts, length stops, latency
and missing usage. Successful-pair costs are conditional and do not replace
all-attempt costs. Preserve known-goal correctness separately from report truth.

**Levinson is nominated, not yet attested or scored.** Build one shuffled, blinded
packet containing only the new models' ambiguous responses (up to 12). Keep it
separate from Sol, G1 development, M4 and Qwen Batch B. Include the unchanged
rubric, blank ratings and honest eligibility declaration; no assistant writes
ratings. Qwen's own four-transcript review remains outstanding separately.

T4 asks for immediate analysis but T6 and the unchanged formal analyzer require
real semantic ratings. Therefore produce provisional/descriptive execution reports
after each backend; **withhold formal analysis until actual ratings are bound**.
Then run the unchanged analyzer separately for each model. Do not infer judgments
from transcript wording or mark human gates complete prematurely.

## Recovery and final acknowledgment

Verify hashes, ledger and artifacts after an interruption. Preserve failed,
censored, interrupted and completed attempts; never replay or replace them.
Only unstarted cells may resume under existing authorization, the same original
backend deadline and cumulative request counters. No reset budget, changed
retry rule, modified frozen input, new stage, new model or new consent follows
from the standing recovery instruction. Root sequence execution is single-use;
any interrupted continuation is explicitly integrity-checked before resuming
unstarted work. An unresolved stop condition stops advancement to another model.

**Owner acknowledgment requested:** read this record, then authorize the fixed
three-model sequence of 228 mock attempts on the lab with the environment change,
611 total requests per model (two already spent each), eight hours per model,
unchanged safeguards and the retained human-review gates. Until that acknowledgment,
no backend launch acknowledgment or benchmark runner is created or started.
