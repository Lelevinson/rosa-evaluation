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
uv sync --project "$checkout" --locked --python /usr/bin/python3
exec "$checkout/.venv/bin/python" -B -m experiments.run --rosa-root "$checkout" --variant "$variant" "$@"
