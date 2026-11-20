#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
"$task_python" -B -m experiments.reliability_v1.deterministic_reference
bash scripts/reliable-gazebo.sh --backend deterministic --configuration A --target 0.2
