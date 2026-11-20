#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-research
exec /home/martin/.local/share/rosa-envs/research/bin/python -B -m unittest discover -s tests -p test_reliability.py -v
