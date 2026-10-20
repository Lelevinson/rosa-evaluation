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
