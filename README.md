# ROSA Evaluation

Local tools for observing and testing ROSA experiments. Each tool owns its Python
virtual environment, dependency lockfile, and configuration. Phoenix is the only
integrated tool today; it records traces, not answer-quality scores.

## Teammate setup

Prerequisites: Ubuntu 24.04 (or WSL), uv, and Python 3.12. Running ROSA experiments
also requires ROS 2 Jazzy and a sibling `rosa-research` checkout. Phoenix itself
does not require ROS, ROSA, or Ollama.

```text
project/
  rosa-research/
  rosa-evaluation/
```

After cloning this repository, start Phoenix from its own directory:

```bash
cd tools/phoenix
uv sync --locked
uv run phoenix-local start
uv run phoenix-local status
uv run python -m rosa_phoenix.smoke
```

Open http://localhost:6006. The smoke command sends one test trace and reads it
back; it does not run an LLM. To stop the server:

```bash
uv run phoenix-local stop
```

`uv sync --locked` installs the versions recorded in `uv.lock` without changing
that lockfile. `uv run` uses this tool's environment automatically. `phoenix-local`
is **our project's installed command**, not a uv or upstream Phoenix command.
`python -m rosa_phoenix.smoke` runs our smoke-check module. No environment
activation or repository-root Python imports are needed for these tool commands.

From the repository root, the existing convenience script also works:

```bash
./tools/phoenix/run.sh start
./tools/phoenix/run.sh smoke
./tools/phoenix/run.sh stop
```

For a teammate using Codex, this is a suitable setup request:

> Read this README and inspect the project first. Set up the Phoenix uv project
> using the committed lockfile, start it, and run its smoke check. Preserve local
> configuration and stored data. If rosa-research and ROS 2 Jazzy are available,
> run the controlled integration validation too. Report what passed and anything
> still needed. Do not upgrade dependencies, commit credentials, or change ROSA
> application code as part of setup.

## Configuration

Phoenix owns `tools/phoenix/config.toml`. Put personal overrides in
`tools/phoenix/config.local.toml`, which Git ignores. For example:

```toml
[phoenix]
url = "http://127.0.0.1:6007"
project = "my-experiments"
```

Both the server and ROSA tracing read these settings. There is no Phoenix `.env`
file to configure. Paths in the Phoenix config resolve from `tools/phoenix/`,
regardless of where a command is called. Defaults preserve the existing database
under `.local/phoenix/data/` and generated files under `results/` at repository root.
Stop Phoenix before changing its URL or state path. Changing the state path does
not move existing traces; keep the default to continue using the existing store.

The **repository-root** `config.toml` separately configures ROSA checkout paths and
experiment result paths. Its ignored `config.local.toml` can override them:

```toml
[checkouts]
research = "../my-rosa-checkout"
```

Root config paths resolve from the repository root. If relocating all results,
set the root `[paths].results` and Phoenix `[paths].results` to the same absolute
directory. Each tool owns its output setting; changing one does not change another.

## Run ROSA experiments

Return to the repository root. Start Phoenix first, then:

```bash
./run.sh research --mode controlled
```

This runs actual ROSA tool dispatch using scripted model responses, without
Ollama. The launcher sources ROS 2 Jazzy and uses the selected ROSA checkout's
own environment. Phoenix's environment does not contain ROSA dependencies.

For live experiments, copy root `.env.example` to `.env`, set the Ollama endpoint
and model, ensure Ollama is running, then:

```bash
./run.sh research --mode live
```

Keep an existing `.env` if already configured. CLI model options override shell
variables, which override evaluation `.env`, then the selected ROSA checkout's
`.env`. Use `--tracing off` to run without sending traces.

`experiments/` contains our ROSA runner, controlled test fixtures, tracing code,
and reference scenarios. It is custom integration code; starting Phoenix does
not run it. Scenario JSON files are references, not automatically executed.
`rosa-baseline` is optional for comparisons, not needed for research-only runs.

## Saved data and checks

```text
tools/phoenix/
  pyproject.toml, uv.lock       tool dependencies and installed launcher
  config.toml                  shared Phoenix settings
  config.local.toml            optional local overrides (ignored)
  .venv/                       tool's Python environment (ignored)
experiments/                   ROSA integration scripts
config.toml                    ROSA checkout and experiment paths
results/runs/<run-id>/          run metadata and results (ignored)
results/runs/<run-id>/phoenix/  exported Phoenix records (ignored)
results/validations/            controlled validation reports (ignored)
.local/phoenix/                persistent database, process record, logs (ignored)
```

The runner prints each run ID and saved-file location. Phoenix also stores traces
in its own database. Export a specific run from repository root:

```bash
./tools/phoenix/run.sh inspect --run-id RUN_ID
```

Replace `RUN_ID` with the printed ID. The export goes to that run's `phoenix/`
directory. `--project NAME` selects a non-default Phoenix project; this inspect
option belongs to our script and is different from uv's `--project` option.

Run configuration checks and controlled ROSA/Phoenix integration checks:

```bash
python3 -m unittest discover -s tests -v
./tools/phoenix/run.sh validate
```

Validation defaults to research and checks eight cases, including errors,
tracing disabled, and interrupted runs. It checks instrumentation behavior,
not live model quality. Optional comparisons use:

```bash
./tools/phoenix/run.sh validate --variant research --variant baseline
```

## Adding another tool

Create `tools/<name>/` with its own `pyproject.toml`, `uv.lock`, `.venv`, config,
and startup command. It should start without importing `experiments/` or another
tool. Keep service data under `.local/<name>/` and exported records under
`results/runs/<run-id>/<name>/`. Connecting it to ROSA is a separate integration
step; no automatic plugin system is implemented.

Commit source, shared config, lockfiles, and safe examples. Keep local configs,
`.env`, environments, databases, results, logs, and backups out of Git. Ignore
rules cover default locations; add rules if choosing other in-repository paths.
Existing historical results and setup backups remain locally in ignored archive
folders.

Phoenix is pinned to 20.23.0. Our server shim disables its upstream gRPC listener
and serves HTTP on loopback only. Revalidate that shim before upgrading Phoenix.
