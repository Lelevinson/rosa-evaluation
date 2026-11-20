"""Start the acknowledged frozen launcher without tying it to a terminal session."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
ack=json.loads((ROOT/'owner-launch-acknowledgment.json').read_text())
assert ack['launch_allowed'] and ack['trials']==76 and ack['physical_request_cap']==611
assert ack['freeze_sha256']==hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest()
assert not (ROOT/'RUN_ONCE').exists() and not (HERE/'worker.json').exists()
with (HERE/'launcher.log').open('x',encoding='utf-8') as log:
    process=subprocess.Popen([sys.executable,'-B',str(ROOT/'launch.py')],cwd=ROOT,
        stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
record={'pid':process.pid,'started_utc':datetime.now(timezone.utc).isoformat(),
        'launcher':'Frozen stage-4/launch.py','detached':True,'scope':'76 Sol mock trials; cap611',
        'log':'operator/launcher.log','status':'stage-4/status.json'}
(HERE/'worker.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
