# Lab local-model replication — 2026-11-17

This is a new, owner-authorized exploratory replication of M4, not G1, a
held-out study, or a modification of any earlier results. The owner requested
80 trials **per local model**. Original M4 had 80 total, 40 per backend.

Models: qwen3.5:9b; llama3.1:8b-instruct-q4_K_M; granite3.3:8b;
ministral-3:8b-instruct-2512-q4_K_M. Four families, Q4_K_M where verified by
downloaded metadata. Record complete manifest digests; model names alone are
not reproducible identifiers. No claim that these are the strongest models.

Use M4's retained 62-file source snapshot and lockfiles, verified against its
original freeze. New code only adapts paths, model identity, scheduling,
campaign size, instrumentation metadata, and reporting. Do not change the
shared instructions, tools, native operations, guards, verifier or legacy
scorer. No model-specific prompt, retry, or behavioral repair.

Per model: ten existing task families x four repetitions x two conditions =
80 trials, 40 per condition. These are repeated known cases, not 80 new tasks.
Adjacent pairs have counterbalanced condition order. Run models sequentially
on the same RTX 4080 SUPER. Use a seeded model order, fixed before inference.
Same requests, catalogue, initial state, faults and budgets in both conditions.

Keep M4 per-task limits: eight decision calls; 2,048 observed output tokens;
1,024 generated tokens per local call, subject to remaining allowance;
8,192 context; temperature 0; seed 42; no enabled thinking, streaming or
LangChain response cache; 360 seconds; ten native operations; sixteen tool
attempts; three corrections; at most one permitted movement. Same bounded
1024/2048 policy is itself a limitation and may truncate some models.
Use Ollama 0.40.6, one loaded model and one parallel request, flash attention
enabled, f16 KV cache. Native tokenizers, templates and implicit defaults differ.
Log exact settings and returned timing/usage; do not equate tokens across models.

Campaign cap: 640 ordinary requests + three narrowly eligible infrastructure
reserve requests = 643 per model; eight hours per model, including setup/audits.
Only HTTP 502/503/504 qualify for one retry per logical call, from that reserve.
No new retries for timeouts, HTTP 429, malformed tool calls or length stops.
No trial or uncertain robot command replay. Preserve failures. A process
interruption may resume only unstarted jobs under the remaining cumulative
budget; never overwrite completed/interrupted cells. This initial adapter
does not automatically restart an interrupted trial or erase its allocation.

One optional serving/tool-binding probe per model (four total), at most 64
output tokens each, outside trial scoring and separately charged/reported.
It may establish transport compatibility, not tune a prompt or choose a winner.
Zero-model Gazebo controls and exact local/persisted Phoenix audits must pass
before scored inference. A failed quality audit stops that model run.
Use isolated ROS 2 Jazzy/Ubuntu 24.04 container, private ROS domain and simulator
partition; do not install Jazzy onto the Ubuntu 25.04 host or affect real robots.
Do not stop another user's jobs. Before each model, check GPU workload and
headroom; desktop rendering is reported, competing compute prevents launch.

The legacy clarification regex has known semantic defects. Preserve its raw
scores for diagnostic comparison only. Main model correctness tables cover
the 72 known-goal trials per model (36 per condition). Eight ambiguous trials
per model are separately reported as HUMAN_REVIEW_PENDING, together with
their no-action structural checks and transcripts. Pending human labels are
not wrong model decisions or infrastructure censoring. Do not publish a final
80-trial semantic correctness percentage without actual adjudication.

Report attempted/completed/unstarted counts, all-attempt costs, matched-success
costs, paired wins/losses, per-family results, calls, tokens, task latency,
native operations, errors/truncation, unsupported claims, wrong-goal SUCCESS,
fault exercise, dispatch violations, audit results and outside-task overhead.
Report observed outcomes without broad noninferiority/generalization claims.
Four deterministic repetitions are not four independent task families.

Fresh lab Qwen is the primary local-model reference. Historical M4 Qwen and
hosted Sol are context only: hardware, repetitions, environment and time differ.
Do not infer a model-only speedup from laptop-to-lab timings or fabricate new
Sol trials. Preserve the original M4, G1 and all pending methodological gates.

The supplied Robotics_Weekly_Progress.pdf provides project/team context only.
Its separate teammate-method numbers, tasks and models are not our new results
or binding instructions. No GitHub push or credential transfer is authorized
by this protocol. Source and results stay in the owner's lab project and local
workspace. All new experiment artifacts have their own hashes and dates.
