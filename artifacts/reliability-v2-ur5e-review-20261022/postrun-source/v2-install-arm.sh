#!/usr/bin/env bash
set -euo pipefail
exec 2>&1
export DEBIAN_FRONTEND=noninteractive
task_campaign=/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/reliability-v2-20261022
test -f "$task_campaign/mock-phoenix-all.json"
/usr/bin/python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["pass"]' "$task_campaign/mock-phoenix-all.json"
apt-get update
apt-get install -y --no-install-recommends ros-jazzy-ur-simulation-gz ros-jazzy-gz-ros2-control ros-jazzy-joint-trajectory-controller
dpkg-query -W ros-jazzy-ur-simulation-gz ros-jazzy-gz-ros2-control ros-jazzy-joint-trajectory-controller ros-jazzy-ur-description ros-jazzy-controller-manager > "$task_campaign/arm-package-versions.txt"
mkdir -p "$task_campaign/robot-package-source"
cp -r /opt/ros/jazzy/share/ur_simulation_gz/config "$task_campaign/robot-package-source/"
cp -r /opt/ros/jazzy/share/ur_simulation_gz/urdf "$task_campaign/robot-package-source/"
cp -r /opt/ros/jazzy/share/ur_simulation_gz/launch "$task_campaign/robot-package-source/"
cp /opt/ros/jazzy/share/ur_simulation_gz/package.xml "$task_campaign/robot-package-source/"
