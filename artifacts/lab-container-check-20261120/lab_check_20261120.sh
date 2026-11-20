#!/usr/bin/env bash
# Read-only lab container check. Starts, stops and changes nothing.
# Only change from the owner-supplied text: `ros2 node list` / `ros2 topic list` get
# `--no-daemon`, because without it the ros2 CLI auto-starts a background ros2 daemon
# process inside the container (which would violate "start nothing").
echo "=== HOST ==="; hostname; date; uptime
echo; echo "=== GPU ==="; nvidia-smi 2>/dev/null || echo "no nvidia-smi"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>/dev/null
echo; echo "=== HOST OLLAMA ==="; (command -v ollama && ollama ps) 2>/dev/null || echo "no host ollama"
echo; echo "=== LISTENING PORTS (11434 ollama, 6006/4317 phoenix, 11311 ros1, 11345 gazebo) ==="
ss -ltnp 2>/dev/null | grep -E ':(11434|6006|4317|11311|11345)\b' || echo "none of the usual ports"
echo; echo "=== HOST ROS / GAZEBO / OLLAMA PROCESSES ==="
ps -eo pid,user,etime,cmd | grep -Ei 'gzserver|gzclient|gz sim|ign gazebo|ros2|rosmaster|roscore|ollama|phoenix' | grep -v grep || echo "none"
echo; echo "=== CONTAINERS ==="
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.RunningFor}}\t{{.Ports}}'
echo; docker network ls; echo; docker system df
for c in $(docker ps --format '{{.Names}}'); do
  echo; echo "########## CONTAINER: $c ##########"
  docker inspect -f 'image={{.Config.Image}} created={{.Created}} started={{.State.StartedAt}} network={{.HostConfig.NetworkMode}} gpus={{.HostConfig.DeviceRequests}} restart={{.HostConfig.RestartPolicy.Name}}' "$c"
  docker inspect -f '{{range .Mounts}}mount: {{.Source}} -> {{.Destination}} (rw={{.RW}}){{println}}{{end}}' "$c"
  docker exec "$c" sh -c '
    echo "-- env (ROS/Gazebo/Ollama/Phoenix only) --"
    env | grep -E "^(ROS_DISTRO|ROS_DOMAIN_ID|ROS_LOCALHOST_ONLY|RMW_IMPLEMENTATION|ROS_MASTER_URI|GZ_|IGN_|GAZEBO_|OLLAMA_HOST|PHOENIX)" \
      | sed -E "s/((KEY|TOKEN|SECRET|PASSWORD)[A-Z_]*)=.*/\1=<redacted>/"
    echo "-- installed --"
    for b in ros2 roscore gz ign gazebo gzserver ollama python3; do
      command -v $b >/dev/null 2>&1 && echo "  $b: yes" || echo "  $b: no"; done
    echo "-- running --"
    ps -eo pid,etime,cmd 2>/dev/null | grep -Ei "gzserver|gz sim|ign gazebo|ros2|ollama" | grep -v grep || echo "  none"
    if command -v ros2 >/dev/null 2>&1; then
      for f in /opt/ros/*/setup.sh; do [ -f "$f" ] && . "$f"; done
      echo "-- ros2 nodes visible from here (10s timeout) --"
      timeout 10 ros2 node list --no-daemon 2>&1 | head -40
      echo "-- ros2 topics visible from here (10s timeout) --"
      timeout 10 ros2 topic list --no-daemon 2>&1 | head -40
    fi
  ' 2>&1
done
echo; echo "=== STOPPED CONTAINERS (inspect only) ==="
for c in $(docker ps -a --filter status=exited --format '{{.Names}}'); do
  docker inspect -f "$c: image={{.Config.Image}} finished={{.State.FinishedAt}} network={{.HostConfig.NetworkMode}}" "$c"
done
