#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/jazzy/setup.bash
cd "$(dirname "$0")/.."
exec /home/martin/.local/share/rosa-envs/research/bin/python -B -m experiments.reliability_v1.demo "$@"
