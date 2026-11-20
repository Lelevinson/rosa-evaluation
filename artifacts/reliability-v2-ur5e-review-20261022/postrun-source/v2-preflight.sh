#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
set -u
task_root=/mnt/c/Proj/robotics/introtorobotics
task_python=/home/martin/.local/share/rosa-envs/research/bin/python
cd "$task_root/rosa-research"
"$task_python" -B -m unittest discover -s tests -p 'test_evidence.py' -v
"$task_python" -B -m unittest discover -s tests -p 'test_reliability.py' -v
"$task_python" -B -m unittest discover -s tests -p 'test_siwc*.py' -v
"$task_python" -B -m unittest discover -s tests -p 'test_shared_backends.py' -v
cd "$task_root/rosa-evaluation"
"$task_python" -B -m unittest discover -s tests -p test_reliability_v2.py -v
printf '\nINSTALLED_ARM_PACKAGES\n'
dpkg-query -W ros-jazzy-ur-simulation-gz ros-jazzy-gz-ros2-control ros-jazzy-joint-trajectory-controller 2>/dev/null || true
