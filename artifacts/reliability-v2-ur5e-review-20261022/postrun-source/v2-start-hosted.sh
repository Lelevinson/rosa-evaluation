#!/usr/bin/env bash
set -eu
task_root=/mnt/c/Proj/robotics/introtorobotics
task_campaign="$task_root/rosa-evaluation/artifacts/reliability-v2-20261022"
mkdir -p "$task_campaign/operator"
nohup bash "$task_root/reports/v2-command.sh" experiments.reliability_v2.runner --backend siwc --pipeline > "$task_campaign/operator/hosted.log" 2>&1 < /dev/null &
task_pid=$!
printf '%s\n' "$task_pid" > "$task_campaign/operator/hosted.pid"
printf 'HOSTED_SUPERVISOR_PID=%s\n' "$task_pid"
