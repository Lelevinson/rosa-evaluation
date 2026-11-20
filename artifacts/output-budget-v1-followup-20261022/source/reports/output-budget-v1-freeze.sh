#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
task_campaign=artifacts/output-budget-v1-20261022
"$task_python" -B -m unittest discover -s tests -p test_output_completion.py -v > "$task_campaign/operator/offline-tests.log" 2>&1
"$task_python" -B -c 'from experiments.output_budget_v1.runner import DESTINATION,write; write(DESTINATION/"operator/offline-tests.json",{"pass":True,"tests":6,"live_model_requests":0})'
"$task_python" -B -m experiments.output_budget_v1.prepare
