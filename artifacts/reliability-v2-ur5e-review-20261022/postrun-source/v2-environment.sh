#!/usr/bin/env bash
set -e
printf 'ARM_PACKAGE_CANDIDATES\n'
apt-cache policy ros-jazzy-ur-simulation-gz ros-jazzy-gz-ros2-control ros-jazzy-joint-trajectory-controller
printf '\nWSL_DISK\n'
df -h /
printf '\nNONINTERACTIVE_SUDO\n'
sudo -n true >/dev/null 2>&1 && printf 'available\n' || printf 'unavailable\n'
