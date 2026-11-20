#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
task_campaign=artifacts/output-budget-v1-resume-20261022
mkdir -p "$task_campaign/operator"
"$task_python" -B -m unittest discover -s tests -p test_output_completion.py -v > "$task_campaign/operator/offline-completion-tests.log" 2>&1
"$task_python" -B -m unittest discover -s tests -p test_output_timeout.py -v > "$task_campaign/operator/offline-timeout-tests.log" 2>&1
"$task_python" -B -c 'from experiments.output_budget_v1_resume.runner import DESTINATION,write; write(DESTINATION/"operator/offline-tests.json",{"pass":True,"tests":8,"live_model_requests":0})'
bash /mnt/c/Proj/robotics/introtorobotics/reports/output-budget-v1-resume-control.sh > "$task_campaign/operator/deterministic-controls.log" 2>&1
