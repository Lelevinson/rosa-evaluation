#!/usr/bin/env bash
# Gazebo D detached job (WSL side). Started by start_detached.ps1 through WMI, so it is not a child of VS Code.
# Usage: job.sh <repo_root_wsl_path> <stage: controls|dev|heldout> [models.json]
#   controls : runner controls (52 zero-model Gazebo trials)
#   dev      : runner live --stage dev, then analysis analyze dev, then analysis d1-gate
#   heldout  : runner live --stage heldout, then analysis analyze heldout (always runs, also after a stop)
# Everything goes to artifacts/gazebo-d-20261121/jobs/<stage>-<UTC timestamp>/ : job.json, runner.log, analysis.log.
# A second job for the same stage is refused while one is alive (pid check). The runner itself also holds the
# gazebo lock and only runs unstarted rows, so a relaunch after an interruption is a resume, never a rerun.
set -uo pipefail
ROOT="$1"; STAGE="$2"; MODELS="${3:-}"
PY=/home/martin/.local/share/rosa-envs/research/bin/python
JOBS="$ROOT/artifacts/gazebo-d-20261121/jobs"
mkdir -p "$JOBS"
for f in "$JOBS"/"$STAGE"-*/job.json; do
  [ -f "$f" ] || continue
  pid=$(sed -n 's/.*"pid": \([0-9]*\).*/\1/p' "$f" | head -1)
  if grep -q '"state": "RUNNING"' "$f" && [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "$(date -Iseconds) refused $STAGE: job already running (pid $pid, $f)" | tee -a "$JOBS/REFUSED.log"; exit 3
  fi
done
DIR="$JOBS/$STAGE-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$DIR"
record() {  # state, exit codes
  printf '{"stage": "%s", "state": "%s", "pid": %s, "root": "%s", "models": "%s", "started": "%s", "updated": "%s", "runner_exit": %s, "analysis_exit": %s, "gate_exit": %s}\n' \
    "$STAGE" "$1" "$$" "$ROOT" "$MODELS" "$STARTED" "$(date -Iseconds)" "${RUNNER_EXIT:-null}" "${ANALYSIS_EXIT:-null}" "${GATE_EXIT:-null}" \
    > "$DIR/job.tmp" && mv "$DIR/job.tmp" "$DIR/job.json"
}
STARTED=$(date -Iseconds)
DONE=0
trap 'record INTERRUPTED; exit 130' INT TERM HUP
trap '[ "$DONE" = 1 ] || record "EXITED_EARLY_$?"' EXIT
record RUNNING
set +u                                   # ROS setup scripts reference unset variables (as in reports/v2-command.sh)
source /opt/ros/jazzy/setup.bash > "$DIR/ros-setup.log" 2>&1 || { record FAILED_ROS_SETUP; DONE=1; exit 2; }
set -u
cd "$ROOT" || { record FAILED_NO_ROOT; DONE=1; exit 2; }
case "$STAGE" in
  controls) "$PY" -B -m experiments.gazebo_d.runner controls > "$DIR/runner.log" 2>&1; RUNNER_EXIT=$? ;;
  dev|heldout)
    [ -n "$MODELS" ] || { record FAILED_NO_MODELS; exit 2; }
    "$PY" -B -m experiments.gazebo_d.runner live --stage "$STAGE" --models "$MODELS" > "$DIR/runner.log" 2>&1
    RUNNER_EXIT=$?
    record ANALYZING
    "$PY" -I -B tools/gazebo_d/analysis.py analyze "$STAGE" > "$DIR/analysis.log" 2>&1; ANALYSIS_EXIT=$?
    if [ "$STAGE" = dev ]; then "$PY" -I -B tools/gazebo_d/analysis.py d1-gate >> "$DIR/analysis.log" 2>&1; GATE_EXIT=$?; fi ;;
  *) record FAILED_BAD_STAGE; exit 2 ;;
esac
record FINISHED
DONE=1
exit "${RUNNER_EXIT:-0}"
