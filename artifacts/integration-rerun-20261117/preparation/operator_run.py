"""Detached operator: validate, gate, then run the two authorized 80-trial batches."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import traceback
import zipfile
from urllib.request import urlopen

ROOT=Path('/media/naeem/d1/marvel proj')
BASE=ROOT/'integration-rerun-20261117'
CONTAINER='marvel-rosa-lab-20261117'
MODELS=['llama3.1:8b-instruct-q4_K_M','granite3.3:8b']
PREFIX=('source /opt/ros/jazzy/setup.bash; '
    'export PYTHONPATH=/work/baseline/rosa-research/src:/work/baseline/rosa-evaluation:/work/integration-rerun-20261117/source:${PYTHONPATH:-}; '
    'exec /work/runtime/envs/research/bin/python -B ')
state={'phase':'PREPARING','planned_robot_trials':160,'planned_validation_trials':24,'started_unix':time.time(),'steps':[]}


def save():
    tmp=BASE/'operator-status.tmp';tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(BASE/'operator-status.json')


def command(label,args,timeout=1800):
    state['phase']=label;step={'label':label,'started_unix':time.time(),'status':'RUNNING'}
    state['steps'].append(step);save()
    with (BASE/(label+'.log')).open('x') as log:
        completed=subprocess.run(['docker','exec','--user','1000:1000','-e','HOME=/work/runtime/home',CONTAINER,
            'bash','-lc',PREFIX+args],stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
    step.update(exit_code=completed.returncode,status='COMPLETE' if completed.returncode==0 else 'STOPPED',finished_unix=time.time());save()
    if completed.returncode:raise RuntimeError(label+' failed; no automatic replay')


def gpu(model):
    samples=[]
    for _ in range(3):
        u,f=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(','))
        samples.append({'utilization_percent':u,'free_MiB':f});time.sleep(1)
    processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=process_name','--format=csv,noheader'],text=True).splitlines()
    record={'at_unix':time.time(),'model':model,'samples':samples,'processes':processes,
        'pass':not any(p and 'gnome-remote-desktop' not in p for p in processes) and all(s['utilization_percent']<=15 and s['free_MiB']>=9000 for s in samples)}
    target=BASE/('gpu-'+model.replace(':','_')+'.json')
    if target.exists():
        (BASE/(state['phase']+'-prior-'+target.name)).write_bytes(target.read_bytes())
    target.write_text(json.dumps(record,indent=2))
    if not record['pass']:raise RuntimeError('GPU gate failed; competing work left untouched')


def collect():
    paths=[p for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.zip'
        and p.name not in ['operator.log','evidence-verification.json']]
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    target=BASE/'NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip'
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
        for name in manifest:z.write(ROOT/name,name)
        z.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':manifest,'operator_phase':state['phase']},indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    (BASE/'evidence-verification.json').write_text(json.dumps({'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'bytes':target.stat().st_size,'content_files':len(manifest),'all_hashes_pass':True,'operator_phase':state['phase']},indent=2))


def main():
    if (BASE/'operator-status.json').exists():raise RuntimeError('Existing operator: no blind restart')
    save()
    try:
        with urlopen('http://127.0.0.1:6006',timeout=5) as r:assert r.status==200
        command('unit','/work/integration-rerun-20261117/source/test_profile.py',120)
        command('freeze','/work/integration-rerun-20261117/source/campaign.py freeze',120)
        command('validation-controls','/work/integration-rerun-20261117/source/campaign.py validation-controls')
        for model in MODELS:
            gpu(model)
            command('validation-'+model.replace(':','_'),'/work/integration-rerun-20261117/source/campaign.py validation --model '+model,5400)
        command('gazebo-controls','/work/integration-rerun-20261117/source/campaign.py controls')
        for model in MODELS:
            gpu(model)
            command('robot-'+model.replace(':','_'),'/work/integration-rerun-20261117/source/campaign.py run --model '+model,29100)
            command('report-'+model.replace(':','_'),'/work/integration-rerun-20261117/source/campaign.py report',120)
        state['phase']='EXECUTION_COMPLETE'
    except BaseException as error:
        state.update(phase='STOPPED',error_type=type(error).__name__,error=str(error)[:300],traceback=traceback.format_exc())
    finally:
        state['finished_unix']=time.time();save();collect()


if __name__=='__main__':main()
