#!/bin/bash
# usage: job.sh <tmux session> <log file> <command...>   detached; refuses duplicates; records pid
S=$1; LOG=$2; shift 2
if tmux has-session -t "$S" 2>/dev/null; then echo "REFUSED: tmux session $S already running"; exit 3; fi
CMD=$(printf '%q ' "$@")
tmux new-session -d -s "$S" "bash -c 'echo \$\$ > $LOG.pid; echo START \$(date -u +%FT%TZ) >> $LOG; $CMD >> $LOG 2>&1; echo EXIT \$? \$(date -u +%FT%TZ) >> $LOG'"
sleep 1; echo "session=$S pid=$(cat $LOG.pid 2>/dev/null) log=$LOG"
