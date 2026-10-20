#!/usr/bin/env bash
set -euo pipefail
tool=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root=$(cd -- "$tool/../.." && pwd)
action=${1:-status}
if [[ $# -gt 0 ]]; then shift; fi
case "$action" in
  start|stop|status) module=tools.phoenix.server; set -- "$action" "$@" ;;
  inspect) module=tools.phoenix.inspect_trace ;;
  validate|smoke) module="tools.phoenix.$action" ;;
  *) echo 'Usage: ./tools/phoenix/run.sh start|stop|status|smoke|inspect|validate [options]' >&2; exit 2 ;;
esac
cd "$root"
# Phoenix does not need inherited ROS Python paths. Each tool owns its environment.
exec env -u PYTHONPATH uv run --project "$tool" --locked python -B -m "$module" "$@"
