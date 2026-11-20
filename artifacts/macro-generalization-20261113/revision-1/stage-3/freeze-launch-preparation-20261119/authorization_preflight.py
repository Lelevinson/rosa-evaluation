"""Fresh restore-only check. No login and zero inference; never print secrets."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import socket
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent/'stage-4'
sys.path.insert(0,str(ROOT))
from common import verify,read,digest
from authorization import restore_only,check_models
from rosa_auth.oauth import SafeError

def main():
    output=HERE/'AUTHORIZATION_PREFLIGHT.json'
    assert not output.exists()
    verified=verify()
    status={'checked_utc':datetime.now(timezone.utc).isoformat(),'pass':False,
        'inference_requests':0,'automatic_login':False,'quota':'UNKNOWN',
        'freeze_sha256':digest(ROOT/'freeze.json'),'frozen_files_verified':verified['files'],
        'free_disk_bytes':shutil.disk_usage(ROOT).free,'execution_window_seconds':28800,
        'planned_trials':76,'estimated_requests':200,'ordinary_cap':608,'reserve_cap':3,
        'total_cap':611,'owner_final_preflight_review':'REQUIRED_BEFORE_LAUNCH'}
    with socket.socket() as probe:status['phoenix_port_available']=probe.connect_ex(('127.0.0.1',6006))!=0
    try:
        with restore_only(status) as active:check_models(active,status)
        status['pass']=status['phoenix_port_available']
        if not status['phoenix_port_available']:status['error_code']='phoenix_port_already_in_use_do_not_touch'
    except Exception as error:
        status['error_type']=type(error).__name__
        if isinstance(error,SafeError):status.update(error_code=error.code,http_status=error.status)
        else:status['error_code']='preflight_external_failure_inspect_safe_status'
    output.write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(status))
    if not status['pass']:raise SystemExit(1)

if __name__=='__main__':main()
