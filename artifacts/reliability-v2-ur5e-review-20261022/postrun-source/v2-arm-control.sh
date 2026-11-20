#!/usr/bin/env bash
set -eo pipefail
exec 2>&1
source /opt/ros/jazzy/setup.bash
set -u
export ROS_DOMAIN_ID=193
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
/home/martin/.local/share/rosa-envs/research/bin/python -B -c 'from experiments.reliability_v2.arm import deterministic; from experiments.reliability_v2.runner import DESTINATION; deterministic(DESTINATION / "deterministic-arm")' &
task_control_pid=$!
sleep 8
ros2 control list_controllers > artifacts/reliability-v2-20261022/controller-states.txt 2>&1 || true
wait "$task_control_pid"
