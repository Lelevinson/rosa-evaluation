#!/bin/bash
set -eo pipefail
export UV_CACHE_DIR=/work/runtime/uv-cache
export UV_PYTHON_DOWNLOADS=never
source /opt/ros/jazzy/setup.bash
uv venv --python /usr/bin/python3 --system-site-packages /work/runtime/envs/research
UV_PROJECT_ENVIRONMENT=/work/runtime/envs/research uv sync --frozen --project /work/baseline/rosa-research --python /usr/bin/python3
uv venv --python /usr/bin/python3 /work/runtime/envs/phoenix
UV_PROJECT_ENVIRONMENT=/work/runtime/envs/phoenix uv sync --frozen --project /work/baseline/rosa-evaluation/tools/phoenix --python /usr/bin/python3
/work/runtime/envs/research/bin/python -c 'import rclpy,rosa,langchain_ollama; print("Research and ROS imports passed")'
/work/runtime/envs/phoenix/bin/python -c 'import phoenix; print("Phoenix import passed")'
dpkg-query -W > /work/preparation/container-packages.txt
echo ENVIRONMENT_SETUP_COMPLETE
