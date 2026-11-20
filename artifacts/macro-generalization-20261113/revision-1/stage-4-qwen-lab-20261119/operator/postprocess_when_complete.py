from pathlib import Path
import json,time,subprocess,shlex
r=Path(__file__).resolve().parents[1]
started=time.monotonic()
while time.monotonic()-started<8*3600+60:
 s=json.loads((r/'status.json').read_text())
 if s['status']=='STOPPED':
  print('STOPPED: preserve artifacts, no automatic replay or new stage',flush=True);break
 if s['status']=='COMPLETE':
  script=Path('/work')/(r/'operator/finalize_report.py').relative_to('/media/naeem/d1/marvel proj')
  command='source /opt/ros/jazzy/setup.bash && '+shlex.join(['/work/runtime/envs/research/bin/python','-B',str(script)])
  p=subprocess.run(['docker','exec','--user','1000:1000','marvel-rosa-lab-20261117','bash','-lc',command])
  print('REPORT_EXIT',p.returncode,flush=True);break
 time.sleep(10)
