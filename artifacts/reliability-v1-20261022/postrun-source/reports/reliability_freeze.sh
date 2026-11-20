#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation
/home/martin/.local/share/rosa-envs/phoenix/bin/python -B -m experiments.reliability_v1.phoenix_audit --controls --destination artifacts/reliability-v1-development
/home/martin/.local/share/rosa-envs/research/bin/python -B -m experiments.reliability_v1.prepare
