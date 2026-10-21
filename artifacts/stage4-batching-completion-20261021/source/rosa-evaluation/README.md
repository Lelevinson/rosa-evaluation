# ROSA Evaluation

Shared experiment launchers and separate tool integrations for ROSA research.
Phoenix currently provides tracing and trace validation. Other evaluation tools
can be added under `tools/` with their own dependencies and configuration.

## Layout

```text
config.toml              shared paths and tool defaults
config.local.toml        optional machine-specific overrides (local only)
experiments/             ROSA runner, controlled fixtures, OTLP tracing, scenarios
tools/phoenix/           Phoenix server, inspection, validation, uv project
tests/                  shared configuration tests
results/                generated artifacts (local only)
.local/                 persistent service data, logs, backups (local only)
```

Clone this project next to `rosa-research`. The ROSA checkout needs its own uv
configuration, Python 3.12, and ROS 2 Jazzy. The experiment launcher sources Jazzy
and syncs the selected checkout. No baseline checkout is needed for research runs.

## Start Phoenix

From this repository's root:

```bash
./tools/phoenix/run.sh start
./tools/phoenix/run.sh status
./tools/phoenix/run.sh smoke
```

Open http://localhost:6006. Stop with `./tools/phoenix/run.sh stop`; stored traces
are retained. The wrapper uses Phoenix's own uv project and environment under
`tools/phoenix/`; the repository root has no Phoenix dependency installation.
To install dependencies separately, run `uv sync` from `tools/phoenix/`.

Phoenix is pinned to 20.23.0. Our existing server shim disables the upstream
gRPC listener so this local setup uses HTTP on loopback only. Revalidate the shim
before upgrading Phoenix. This launcher and shim are project code, not upstream
Phoenix requirements.

## Run an experiment

For the prepared Qwen readiness check (native single/dependent tool loops plus
custom-only ROSA dispatch and Phoenix tracing), start the services and run:

```bash
./run.sh research --probe-qwen
```

This requires the research branch's `load_default_tools=False` support and the
downloaded `qwen3.5:9b` model. It exposes only fixed in-memory read tools. Results
include model digest, inference settings, native parsed calls, timings, token
counts, a ROSA trace ID, and Ollama's runtime memory report. This is a readiness
smoke test, not the 60-scenario research benchmark or a model quality claim.

When environments are linked from `/mnt/c` to the Linux filesystem, launchers
resolve the environment path before running Python. Each launcher explicitly
selects its own uv environment so a Phoenix parent process cannot sync research
dependencies into Phoenix's environment. Shell scripts are checked out with LF
line endings for WSL.

```bash
./run.sh research --mode controlled
```

This exercises actual ROSA/LangChain dispatch with scripted model responses and
does not require Ollama. For a live run, copy `.env.example` to `.env`, set the
Ollama endpoint and model, start Ollama, then run:

```bash
./run.sh research --mode live
```

CLI model options override environment variables. Shell variables override the
evaluation `.env`, which takes precedence over the selected checkout's `.env`.
`experiments/scenarios/ros2-nodes.json` records an explicit read-only smoke query;
scenario files are references, not automatically executed by the launcher.
Use `--tracing off` to run without sending OTLP traces.

`rosa-baseline` is an optional separate reference checkout, not bundled with this
repository. Configure it only when you want comparisons, then use `./run.sh baseline`.
Each checkout runs in its own environment and process; its source path is recorded.

## Configuration and output

Edit shared defaults in `config.toml`. For local paths or a different Phoenix
port, put only your overrides in ignored `config.local.toml`, for example:

```toml
[paths]
results = "/home/your-user/experiment-results"

[checkouts]
research = "../my-rosa-checkout"

[tools.phoenix]
url = "http://127.0.0.1:6007"
```

Relative paths always resolve from this repository, regardless of the calling
directory. Stop Phoenix before changing its URL or state directory. Moving the
state setting does not migrate an existing database; keep it unchanged to retain
access to your current store, or move the stopped service's complete data directory.

Default output layout:

```text
results/
  runs/<run-id>/
    metadata.json          shared run identity and provenance
    result.json            ROSA answer and application error status
    phoenix/trace.json     Phoenix export, written by the inspect command
  validations/<suite-id>/phoenix/
    verified.json          validation evidence and per-case console logs
  archive/pre-layout-2026-10-20/   existing local results preserved during reorganization
.local/
  phoenix/data/            persistent Phoenix database
  phoenix/server.log
  phoenix/process.json
  ros-log/
```

The runner prints the run ID and output directory. Metadata is written before
execution; `result.json` is written when ROSA returns. An interrupted run may have
only metadata. Trace completeness is checked separately, not inferred from an answer.
Export a run's stored spans with:

```bash
./tools/phoenix/run.sh inspect --run-id RUN_ID
```

Use `--project NAME` if the experiment used a non-default Phoenix project. The
default export is `results/runs/RUN_ID/phoenix/trace.json`; `--output PATH` overrides it.
Local config overrides apply to both the runner and tool commands.

For a future tool, add `tools/<tool>/` with its own uv project, its settings under
`[tools.<tool>]`, service state under `.local/<tool>/`, and exports under the same
run's `results/runs/<run-id>/<tool>/`. Reuse the shared run ID to correlate outputs.
Only Phoenix is integrated today; no plugin framework or additional evaluator is
implemented. Tracing shows what happened; it does not establish answer quality or
robot task success.

## Checks

For the process-separated stateful engineering pilot and paired cache runs:

```bash
./run.sh research --benchmark --backend scripted --suite full --repeats 3 --tracing off
./run.sh research --benchmark --backend ollama --suite pilot --repeats 3 --request-budget 840
./run.sh research --benchmark --backend siwc --suite pilot --repeats 3 --request-budget 840
```

The world and independent scorer run in a separate process with distinct agent
and evaluator channels. Six fixed tools expose observations, simulated actions,
verification and structured reports. Commands and verification are never cached.
The agent cannot access the hidden fixture or scorer through its tool channel.
Only trusted local simulation code executes; no ROS or physical action is exposed.

`--suite pilot` uses 12 balanced fixtures and a limited live cache crossover;
three repetitions produce 60 trials per backend. `--suite full` uses all 60
fixtures. The scripted full control covers all fixtures under all three policies
(540 trials with three repetitions). These sets share generator/template families;
the reserved validation split is not an independently authored holdout-family set.
`--suite smoke --repeats 1 --policies none` checks one development case per family.

Batch output contains a frozen protocol, manifest, source hashes, incremental
results and summaries. Each trial has its own run ID, raw tool/oracle evidence,
structured score and Phoenix trace. A completed batch can contain failed tasks;
completion does not mean the model passed the readiness/usefulness criteria.
The legacy `api_failed` field also covers agent iteration exhaustion. State/claim
scores and operational completion are reported separately.

Audit a completed live batch against Phoenix and independently reconstructed
state, action contracts, counters and cached-observation staleness:

```bash
./tools/phoenix/run.sh audit --batch-id BATCH_ID
```

Use `--offline` to recheck previously exported traces. Use `--oracle-only` for
execution evidence without traces, such as the scripted control; this writes
`phoenix/oracle-audit.json` and does not claim a Phoenix trace audit.

OAuth requires fresh browser consent, uses memory-only renewable credentials,
and revokes its session on exit. Request/trial/wall budgets are enforced. TTL is
measured in logical tool-step ticks, not inference wall time. Injected read delays
are explicit fixture costs; results do not establish real sensor costs or safety.
Provider-managed prompt/KV caching is separate from the tested observation cache.

The shared ROSA integration probe runs the same agent, prompts, tool definitions,
and fixed mock single/dependent tasks with either candidate:

```bash
./run.sh research --probe-backends --backend ollama
./run.sh research --probe-backends --backend siwc
```

Use `--case single` or `--case dependent` for one case, `--tracing off` to disable
Phoenix, and `--model` to select an exact model. OAuth sign-in is interactive;
at most eight requests are permitted and the session is revoked afterward.
Its model comes from the live account catalog. Reports record provider settings
separately because sampling controls and context limits differ. This probe uses
the modified ROSA fork with an exact custom-only registry and fixed mock reads;
use the stateful benchmark above for independently scored action outcomes.

For the interactive ChatGPT OAuth readiness test, start Phoenix and run:

```bash
./run.sh research --probe-siwc
```

Open the printed loopback link and complete browser consent. This uses the
research checkout's locked `siwc` dependencies and chooses the first visible
account model, or an exact catalog slug supplied with `--model`. At most three
inference requests check text, one fixed mock-tool call, and its continuation.
Tokens stay in memory and the session is revoked afterward, so each run requires
sign-in. Only public registration identifiers and a hashed account subject are
saved under `~/.local/share/rosa-siwc/`. Reports exclude tokens and reasoning.
This native transport smoke checks the transport separately from the shared ROSA
adapter and stateful benchmark. Use the report's gates for application success and the Phoenix export
to inspect observed operations.

```bash
python3 -m unittest discover -s tests -v
./tools/phoenix/run.sh validate
```

Validation defaults to the research checkout. For explicit baseline comparisons:

```bash
./tools/phoenix/run.sh validate --variant research --variant baseline
```

The suite checks success, execution/validation errors, reported errors, nested
tools, unknown tools, tracing disabled, and interrupted traces by reading Phoenix.
It uses controlled model responses and does not benchmark live LLM performance.

## What belongs in Git

Share source code, launch scripts, tests, scenarios, `config.toml`, `.env.example`,
and each tool's `pyproject.toml`, `uv.lock`, and `.python-version`. Do not commit
`.env`, `config.local.toml`, virtual environments, results, databases, logs, or backups;
the repository's ignore rules cover the default locations. If you choose a different
output directory inside this repository, add that directory to `.gitignore` too.
External output paths are outside this repository. Old pip requirements and historical setup reports
are retained locally under `.local/archive/pre-layout-2026-10-20/`, not published.
