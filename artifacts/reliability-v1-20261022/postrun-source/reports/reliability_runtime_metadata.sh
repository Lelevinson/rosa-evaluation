#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
exec /home/martin/.local/share/rosa-envs/research/bin/python /mnt/c/Proj/robotics/introtorobotics/reports/reliability_runtime_metadata.py
