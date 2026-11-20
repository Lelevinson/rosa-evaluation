#!/usr/bin/env bash
set -o pipefail
source /opt/ros/jazzy/setup.bash
set -u
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
task_campaign=artifacts/reliability-v1-20261022
echo 'HOSTED_VALIDATION_START'
"$task_python" -B -m experiments.reliability_v1.runner --backend siwc
hosted_exit=$?
echo "HOSTED_VALIDATION_EXIT=$hosted_exit"
echo 'LOCAL_VALIDATION_START'
"$task_python" -B -m experiments.reliability_v1.runner --backend ollama
local_exit=$?
echo "LOCAL_VALIDATION_EXIT=$local_exit"
/home/martin/.local/share/rosa-envs/phoenix/bin/python -B -m experiments.reliability_v1.phoenix_audit --destination "$task_campaign"
audit_exit=$?
printf '{"hosted_exit":%s,"local_exit":%s,"phoenix_audit_exit":%s}\n' "$hosted_exit" "$local_exit" "$audit_exit" > "$task_campaign/pipeline-completion.json"
echo 'PIPELINE_FINISHED'
