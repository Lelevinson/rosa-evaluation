"""Detach the bounded recovery manager under the existing run authorization."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
assert not (HERE/'worker.json').exists()
with (HERE/'manager.log').open('x') as log:
    child=subprocess.Popen([sys.executable,'-B',str(HERE/'manage.py')],cwd=HERE,
        stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(HERE/'worker.json').write_text(json.dumps({'pid':child.pid,'started_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Unstarted cells only, same611 cap and8h origin','stop_at_frozen_compromise_threshold':8},indent=2)+'\n')
print(json.dumps({'manager_pid':child.pid,'continuation_scope':'Existing authorized unstarted cells only'}))
