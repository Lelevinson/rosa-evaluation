#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=197
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
exec /home/martin/.local/share/rosa-envs/research/bin/python -B -c 'from experiments.ur5e_transfer_v1.arm import deterministic; from experiments.output_budget_v1.runner import DESTINATION; deterministic(DESTINATION / "deterministic-arm")'
