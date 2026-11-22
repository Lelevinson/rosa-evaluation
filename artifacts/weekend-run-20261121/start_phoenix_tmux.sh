#!/bin/bash
L=/mnt/c/Proj/robotics/introtorobotics/weekend-run-20261121/logs
if tmux has-session -t phoenix 2>/dev/null; then echo "phoenix tmux session already exists"; else
tmux new-session -d -s phoenix "cd /tmp && /home/martin/.local/share/rosa-envs/phoenix/bin/python -I -B /mnt/c/Proj/robotics/introtorobotics/wt-a-f1/tools/f1_wording/phoenix_service.py start --store /mnt/c/Proj/robotics/introtorobotics/weekend-run-20261121/phoenix >> $L/phoenix-service.log 2>&1; exec sleep infinity"
fi
for i in $(seq 1 60); do curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:6006/healthz | grep -q 200 && break; sleep 2; done
tail -2 $L/phoenix-service.log; cat /mnt/c/Proj/robotics/introtorobotics/weekend-run-20261121/phoenix/phoenix-service.json; tmux ls
