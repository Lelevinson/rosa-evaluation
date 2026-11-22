cd /mnt/c/Proj/robotics/introtorobotics/wt-a-f1 || exit 2
PY=/home/martin/.local/share/rosa-envs/research/bin/python
export PYTHONDONTWRITEBYTECODE=1
R=artifacts/f1-catalogue-wording-20261121/runs/stage1a-dev-qwen-r0b
$PY -I -B tools/f1_wording/dev_diagnostic.py --run stage1a-dev-qwen-r0b --out $R/DEV_DIAGNOSTIC.json
$PY -I -B tools/f1_wording/analysis.py --qwen-run stage1a-dev-qwen-r0b --out $R/DEV_ANALYSIS > /dev/null
$PY -I -c "
import json
a=json.load(open('$R/DEV_ANALYSIS.json'))['qwen']
print('arms', {k:{x:v[x] for x in ('pass_provisional','pending_human_review','calls','length_stops','censored','task_seconds')} for k,v in a['arms'].items()})
print('known_goal', {k:a['known_goal'][k] for k in ('both','new_only','base_only','neither','net')})
for t,v in a['by_type'].items(): print(t, {k:v[k] for k in ('both','new_only','base_only','neither')})
print('diag', a['diagnostics'])
for r in a['per_case']:
  if not r['pass_provisional']: print('FAIL', r)
"
