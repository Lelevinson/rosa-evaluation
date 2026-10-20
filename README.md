# ROSA Evaluation

Independent tools for observing ROSA. Phoenix is the only tool integrated today.
There is no experiment suite or scripted model harness in this repository.

## Start Phoenix

Prerequisites: uv and Python 3.12 on Ubuntu/WSL. From this repository:

```bash
cd tools/phoenix
uv sync --locked
uv run phoenix-local start
```

Open http://localhost:6006. From the same folder:

```bash
uv run phoenix-local status
uv run phoenix-local stop
```

`uv sync --locked` installs the committed dependency versions without changing the
lockfile. `uv run` selects this tool's environment. `phoenix-local` is our installed
launcher command. Stopping Phoenix preserves stored traces.

Starting the server does **not** automatically instrument ROSA. The agent process
must send traces to it. The launcher below does that for a live ROSA/Ollama run.

## Trace a real ROSA run

Keep the projects next to each other:

```text
project/
  rosa-research/
  rosa-evaluation/
```

The ROSA checkout needs its uv dependencies (including Ollama and tracing groups),
Python 3.12, and ROS 2 Jazzy. Ollama must be running with the selected model.
Copy the evaluation root `.env.example` to `.env` if you have no existing `.env`,
and set the Ollama endpoint/model there. On WSL the endpoint may be the Windows
host address rather than localhost.

With Phoenix running, from `tools/phoenix/`:

```bash
./trace-rosa.sh
```

This invokes the actual ROSA agent with Ollama and asks it to list ROS 2 nodes.
It sends model/tool traces to Phoenix; select `rosa-local` in the browser.
This is one live tracing launcher, not a test suite. For a different task:

```bash
./trace-rosa.sh --query "List the currently running ROS 2 nodes."
```

`--query` is our launcher's option for the message sent to ROSA. Other options
are listed by `./trace-rosa.sh --help`. The script sources ROS 2 Jazzy and uses
**ROSA's own environment**, keeping its dependencies separate from the server's.
The default query is read-only; a different query can cause ROSA to execute tools.
Existing team scripts need to enable instrumentation too; merely starting Phoenix
does not trace arbitrary Python processes. `tracing.py` contains the reusable
tracing context used by this launcher, and `trace_rosa.py` shows its integration.

## Configuration

Each tool owns its settings. Phoenix defaults are in
`tools/phoenix/config.toml`. Personal overrides belong in
`tools/phoenix/config.local.toml` (ignored by Git), for example:

```toml
[phoenix]
url = "http://127.0.0.1:6007"
project = "my-rosa"

[rosa]
checkout = "../../../my-rosa-checkout"
```

Paths resolve from `tools/phoenix/`, not from your terminal directory. The server
and tracing launcher read the same Phoenix URL/project settings. Stop the server
before changing its URL or state path. Changing the state path does not migrate
existing traces. No root configuration or baseline checkout is required.

CLI model options override shell variables, then the evaluation root `.env`, then
the ROSA checkout's `.env`. uv does not load these files; our live launcher does.
The server itself needs no `.env` file.

## Files and checks

```text
tools/phoenix/
  pyproject.toml, uv.lock   dependencies and installed launcher
  .venv/                   isolated Python environment (ignored)
  config.toml              shared Phoenix and ROSA connection settings
  config.local.toml        personal overrides (ignored)
  trace-rosa.sh             live ROSA tracing launcher
  trace_rosa.py, tracing.py live invocation and instrumentation
results/runs/<run-id>/      saved metadata, answers, exports (ignored)
.local/phoenix/             persistent database and server logs (ignored)
```

Existing results and historical archives remain local. The live launcher prints
the run ID and result directory. From repository root, export stored traces with:

```bash
./tools/phoenix/run.sh inspect --run-id RUN_ID
```

Replace `RUN_ID` with the printed ID. Exports go into that run's `phoenix/` folder.
The root convenience commands `./tools/phoenix/run.sh start|status|stop` also work;
choose one action in place of `start|status|stop`.

Configuration checks, from root:

```bash
python3 -m unittest discover -s tests -v
```

Optional Phoenix-only connectivity check, from `tools/phoenix/`:

```bash
uv run python -m rosa_phoenix.smoke
```

This sends and reads back one test span without ROSA or Ollama. It verifies the
server connection, not real ROSA behavior or answer quality.

## Setup with Codex

A teammate can clone this repository and give Codex this request:

> Read the README and inspect my ROSA checkout. Set up Phoenix with its committed
> uv lockfile and configure the checkout path/Ollama endpoint locally. Preserve
> existing configuration and traces. Run the Phoenix smoke check. With ROS 2 Jazzy
> and Ollama available, verify one real ROSA tracing run and read back its spans.
> Report anything unavailable. Do not upgrade dependencies, commit secrets, or
> change ROSA application code as part of setup.

For future tools, add `tools/<name>/` with its own uv project, environment,
configuration, and startup command. Store its state in `.local/<name>/` and
exports in `results/runs/<run-id>/<name>/`. No plugin framework is implemented.
Commit source, shared settings, lockfiles, and safe examples. Keep environments,
local configs, `.env`, results, databases, logs, and backups out of Git.

Phoenix is pinned to 20.23.0. Our shim disables upstream gRPC and binds HTTP to
loopback. Revalidate the shim before upgrading Phoenix.
