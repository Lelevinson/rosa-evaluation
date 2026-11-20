"""Resume only unstarted cells using the unchanged frozen trial and cumulative cap.

Operational recovery under the owner's standing instruction; no case, parser,
retry, scoring or protected-source edit. The first stream-error trial is retained.
"""
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
import runner as runtime
from common import REPO,WORKSPACE,read,write
from runtime_support import evaluate_progress

def now():return datetime.now(timezone.utc)
def utc(value):return datetime.fromisoformat(value.replace('Z','+00:00'))

def recovery_inputs():
    old=read(ROOT/'status.json')
    assert old['status']=='STOPPED' and old['planned']==76
    assert read(ROOT/'operator/continuation-02/phoenix-service.json')['stopped']
    initial=utc(old['started_utc'])
    elapsed=(now()-initial).total_seconds()
    if not 0<=elapsed<28800:raise RuntimeError('original_eight_hour_window_unavailable')
    plan=read(ROOT/'plan.json')
    rows=[]
    hashes={}
    for folder in sorted((ROOT/'trials').iterdir()):
        if not folder.is_dir():continue
        row=read(folder/'result.json')
        assert row['id']==folder.name and row['local_audit']['pass']
        assert read(folder/'phoenix-audit.json')['pass']
        rows.append(row)
        for p in folder.iterdir():
            if p.is_file():hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    ids={row['id'] for row in rows}
    assert len(ids)==len(rows)==old['completed']
    assert ids<={item['id'] for item in plan}
    assert sum(row['inference']['calls'] for row in rows)==old['campaign']['reserved_requests']
    freeze=read(ROOT/'freeze.json')
    assert all(hashlib.sha256((WORKSPACE/name).read_bytes()).hexdigest()==value
               for name,value in freeze['files_sha256'].items())
    remaining=[item for item in plan if item['id'] not in ids]
    assert len(remaining)+len(rows)==76
    return old,remaining,hashes

def campaign_from_prior(checkpoint,prior):
    campaign=runtime.Campaign(checkpoint)
    campaign.requests=prior['campaign']['reserved_requests']
    campaign.retries=prior['campaign']['infrastructure_retries']
    campaign.events=deepcopy(prior['campaign']['events'])
    # The frozen trial computes its deadline from this same monotonic origin.
    campaign.started=time.monotonic()-(now()-utc(prior['started_utc'])).total_seconds()
    return campaign

def start_phoenix():
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1',6006))==0:raise RuntimeError('phoenix_port_in_use_no_takeover')
    store=HERE/'phoenix';store.mkdir()
    env={k:v for k,v in os.environ.items() if k in ('HOME','PATH','LANG','LC_ALL','TMPDIR')}
    env.update(PYTHONPATH=str(REPO),PYTHONDONTWRITEBYTECODE='1',PHOENIX_HOST='127.0.0.1',PHOENIX_PORT='6006',
        PHOENIX_WORKING_DIR=str(store/'data'),PHOENIX_TELEMETRY_ENABLED='false',
        PHOENIX_ALLOW_EXTERNAL_RESOURCES='false',PHOENIX_DISABLE_AGENT_ASSISTANT='true',
        PHOENIX_ENABLE_MCP_SERVER='false',PHOENIX_ALLOWED_SANDBOX_PROVIDERS='')
    with (store/'server.log').open('x') as log:
        process=subprocess.Popen([runtime.PHOENIX,'-B','-m','tools.phoenix.phoenix_server','serve'],cwd=REPO,
            env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    (HERE/'phoenix-service.json').write_text(json.dumps({'pid':process.pid,'stopped':False,'storage':str(store)})+'\n')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline=time.monotonic()+60
    while True:
        if process.poll() is not None:raise RuntimeError('owned_phoenix_failed')
        try:
            with opener.open('http://127.0.0.1:6006/healthz',timeout=2) as response:
                if response.status==200:return process
        except OSError:pass
        if time.monotonic()>deadline:
            process.terminate();process.wait(timeout=10)
            raise RuntimeError('owned_phoenix_readiness_timeout')
        time.sleep(.5)

def main():
    assert not (HERE/'RUN_ONCE').exists()
    prior,plan,hashes=recovery_inputs()
    (HERE/'prior-status-exact.json').write_bytes((ROOT/'status.json').read_bytes())
    record={'date':'2026-11-19','scope':'Only currently unstarted Sol cells; every earlier attempted cell retained',
        'standing_owner_instruction':'After external interruptions, verify integrity, document pause and continue unstarted work',
        'prior_requests':prior['campaign']['reserved_requests'],'prior_retries':prior['campaign']['infrastructure_retries'],
        'remaining_cells':len(plan),'original_start_utc':prior['started_utc'],'physical_cap':611,
        'remaining_physical_allowance':611-prior['campaign']['reserved_requests'],
        'window_reset':False,'failed_trial_retried':False,'retry_rule_changed':False,
        'previous_trial_hashes':hashes,'frozen_inputs_verified':True,
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'CONTINUATION_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
    (HERE/'RUN_ONCE').write_text('Unstarted cells only; no new consent or reset.\n')
    status=deepcopy(prior)
    status.update(status='RESUMING',continuation='operator/continuation-03',current_trial=None)
    status.pop('completed_utc',None);status.pop('error_type',None);status.pop('error_code',None)
    def checkpoint(budget):
        status['campaign']=budget;status['live_model_requests']=budget['reserved_requests'];write('status.json',status)
    campaign=campaign_from_prior(checkpoint,prior)
    checkpoint(campaign.snapshot())
    auth={};model=transport=process=None
    try:
        process=start_phoenix()
        with runtime.restore_only(auth) as active:
            runtime.check_models(active,auth)
            transport=runtime.RecoverableSiwc(token_provider=active.access_token,
                request_budget=611-prior['campaign']['reserved_requests'])
            model=runtime.ChatSiwc(model=runtime.MODEL,backend=transport)
            status['status']='RUNNING'
            for item in plan:
                transport.raise_if_unavailable()
                assert not (ROOT/'trials'/item['id']).exists()
                status['current_trial']=item['id'];checkpoint(campaign.snapshot())
                row=runtime.trial(item,model,transport,campaign)
                status['completed']+=1;status['current_trial']=None;checkpoint(campaign.snapshot())
                print(json.dumps({'done':status['completed'],'planned':76,'id':item['id'],
                    'effective_status':evaluate_progress(row)['primary_status'],'calls':row['actual_turns'],
                    'native':len(row['actor_records']),'charged_total':campaign.requests}),flush=True)
                transport.raise_if_unavailable()
            assert campaign.requests==prior['campaign']['reserved_requests']+transport.requests
            status['status']='COMPLETE'
    except BaseException as error:
        status.update(status='STOPPED',error_type=type(error).__name__)
        status['error_code']=error.code if isinstance(error,runtime.SafeError) else 'inspect_retained_continuation'
        raise
    finally:
        if model:model.close()
        if transport:transport.close()
        status['completed_utc']=now().isoformat()
        checkpoint(campaign.snapshot())
        (HERE/'authorization-status.json').write_text(json.dumps(auth,indent=2)+'\n')
        try:
            # Preserve a partial/pending-safe view even if provider auth was lost.
            subprocess.run([sys.executable,'-B',str(ROOT/'analyze_results.py')],cwd=ROOT,timeout=180,check=True)
        finally:
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                    try:process.wait(timeout=20)
                    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
                (HERE/'phoenix-service.json').write_text(json.dumps({'pid':process.pid,'stopped':True,
                    'exit_code':process.returncode})+'\n')
        assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in hashes.items())

if __name__=='__main__':main()
