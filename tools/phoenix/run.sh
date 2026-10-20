#!/usr/bin/env bash
set -euo pipefail
tool=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
action=${1:-status}
if [[ $# -gt 0 ]]; then shift; fi
case "$action" in
  start|stop|status) module=rosa_phoenix.server; set -- "$action" "$@" ;;
  inspect) module=rosa_phoenix.inspect_trace ;;
  smoke) module="rosa_phoenix.$action" ;;
  *) echo 'Usage: ./tools/phoenix/run.sh start|stop|status|smoke|inspect [options]' >&2; exit 2 ;;
esac
cd "$tool"
# Phoenix does not need inherited ROS Python paths. Each tool owns its environment.
exec env -u PYTHONPATH uv run --project "$tool" --locked python -B -m "$module" "$@"
