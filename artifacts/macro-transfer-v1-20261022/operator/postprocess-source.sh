#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
exec /home/martin/.local/share/rosa-envs/research/bin/python -B /mnt/c/Proj/robotics/introtorobotics/reports/finalize_macro_transfer_v1.py
