#!/bin/bash
# usage: f1run.sh <stage1.py args...>   (D12 WSL research env)
cd /mnt/c/Proj/robotics/introtorobotics/wt-a-f1 || exit 2
export PYTHONDONTWRITEBYTECODE=1
exec /home/martin/.local/share/rosa-envs/research/bin/python -I -B tools/f1_wording/stage1.py "$@"
