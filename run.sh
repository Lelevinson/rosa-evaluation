#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
variant=${1:-research}
if [[ $# -gt 0 ]]; then shift; fi
cd "$root"
checkout=$(python3 -B -c 'import sys; from experiments.config import checkout; print(checkout(sys.argv[1]))' "$variant")
[[ -f "$checkout/pyproject.toml" ]] || { echo "Missing ROSA checkout: $checkout. Set [checkouts] in config.local.toml." >&2; exit 1; }
set +u
source /opt/ros/jazzy/setup.bash
set -u
state=$(python3 -B -c 'from experiments.config import configured_path; print(configured_path("state"))')
export ROS_LOG_DIR="${ROS_LOG_DIR:-$state/ros-log}"
mkdir -p "$ROS_LOG_DIR"
venv="$checkout/.venv"
if [[ -d "$venv" ]]; then venv=$(realpath "$venv"); fi
# The Phoenix parent process can export its own UV_PROJECT_ENVIRONMENT.
# Always select the research checkout's environment before syncing its packages.
export UV_PROJECT_ENVIRONMENT="$venv"
uv sync --project "$checkout" --locked --python /usr/bin/python3
if [[ "${1:-}" == '--benchmark' ]]; then
    [[ "$variant" == research ]] || { echo 'The stateful benchmark targets the research checkout.' >&2; exit 2; }
    shift
    exec "$venv/bin/python" -B -m experiments.benchmark "$@"
fi
if [[ "${1:-}" == '--probe-backends' ]]; then
    [[ "$variant" == research ]] || { echo 'The shared backend probe targets the research checkout.' >&2; exit 2; }
    shift
    exec "$venv/bin/python" -B -m experiments.probe_backends "$@"
fi
if [[ "${1:-}" == '--probe-qwen' ]]; then
    [[ "$variant" == research ]] || { echo 'The Qwen readiness probe currently targets the research checkout.' >&2; exit 2; }
    shift
    exec "$venv/bin/python" -B -m experiments.probe_qwen "$@"
fi
if [[ "${1:-}" == '--probe-siwc' ]]; then
    [[ "$variant" == research ]] || { echo 'The OAuth readiness probe targets the research checkout.' >&2; exit 2; }
    shift
    exec "$venv/bin/python" -B -m experiments.probe_siwc "$@"
fi
exec "$venv/bin/python" -B -m experiments.run --rosa-root "$checkout" --variant "$variant" "$@"
