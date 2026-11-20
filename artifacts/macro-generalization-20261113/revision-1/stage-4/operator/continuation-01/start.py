"""Detached continuation of acknowledged unstarted cells only."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
assert json.loads((HERE/'VALIDATION.json').read_text())['pass']
assert not (HERE/'worker.json').exists()
with (HERE/'launcher.log').open('x') as log:
    process=subprocess.Popen([sys.executable,'-B',str(HERE/'resume.py')],cwd=HERE,
        stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(HERE/'worker.json').write_text(json.dumps({'pid':process.pid,'started_utc':datetime.now(timezone.utc).isoformat(),
    'original_request_cap':611,'prior_spent':8,'unstarted_cells':73,'new_consent':False},indent=2)+'\n')
print(json.dumps({'pid':process.pid,'continuation_started':True,'unstarted_cells':73,'window_reset':False}))
