#!/usr/bin/env bash
set -euo pipefail
tool=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$tool"
checkout=$(python3 -B -c 'from config import rosa_checkout; print(rosa_checkout())')
[[ -f "$checkout/pyproject.toml" ]] || { echo "Missing ROSA checkout: $checkout. Set [rosa].checkout in tools/phoenix/config.local.toml." >&2; exit 1; }
set +u
source /opt/ros/jazzy/setup.bash
set -u
state=$(python3 -B -c 'from config import tool_state_dir; print(tool_state_dir("phoenix"))')
export ROS_LOG_DIR="${ROS_LOG_DIR:-$state/ros-log}"
mkdir -p "$ROS_LOG_DIR"
cd "$tool/../.."
# Use ROSA's dependencies while loading the tracing helper from this checkout.
exec uv run --project "$checkout" --locked python -B -m tools.phoenix.trace_rosa "$@"
