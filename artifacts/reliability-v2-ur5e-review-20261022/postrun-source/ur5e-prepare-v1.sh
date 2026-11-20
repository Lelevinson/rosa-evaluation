#!/usr/bin/env bash
set -eo pipefail
exec 2>&1
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
/home/martin/.local/share/rosa-envs/research/bin/python -B -m unittest discover -s tests -p test_ur5e_readiness.py -v
exec /home/martin/.local/share/rosa-envs/research/bin/python -B -m experiments.ur5e_transfer_v1.prepare
