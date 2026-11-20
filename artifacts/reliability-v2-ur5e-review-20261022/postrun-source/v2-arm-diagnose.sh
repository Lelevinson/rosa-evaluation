#!/usr/bin/env bash
set -eo pipefail
exec 2>&1
source /opt/ros/jazzy/setup.bash
exec /home/martin/.local/share/rosa-envs/research/bin/python -B /mnt/c/Proj/robotics/introtorobotics/reports/v2-arm-diagnose.py
