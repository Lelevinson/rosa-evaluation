"""Bounded operational continuation of unstarted cells; never retry a trial.

Keeps the original deadline/counters and unchanged frozen trial. Stops for
authorization/non-provider/audit failures, no progress, or operational compromise.
"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from common import read,write
sys.path.append(str(ROOT.parent/'stage-3'))
from censoring import censor_class

def utc(value):return datetime.fromisoformat(value.replace('Z','+00:00'))
def report(value):
    (HERE/'status.json').write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value),flush=True)

def main():
    assert not (HERE/'RUN_ONCE').exists()
    (HERE/'RUN_ONCE').write_text('Existing authorized unstarted work only.\n')
    parent=ROOT/'operator/continuation-01'
    number=2
    template=(parent/'resume.py').read_text()
    while True:
        # Await normal cleanup by the previous owned launcher. No service takeover.
        deadline=time.monotonic()+180
        while not (parent/'phoenix-service.json').exists() or not read(parent/'phoenix-service.json').get('stopped'):
            if time.monotonic()>deadline:
                report({'status':'STOPPED','reason':'Previous continuation cleanup unavailable'});return
            time.sleep(2)
        state=read(ROOT/'status.json')
        rows=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))]
        censored=sum(censor_class(row) is not None for row in rows)
        common={'retained':len(rows),'censored':censored,'charged':state['campaign']['reserved_requests'],
                'original_cap':611,'original_start_utc':state['started_utc']}
        if state['completed']==76:
            report(dict(common,status='ALL_SCHEDULED_ATTEMPTS_RETAINED',semantic_review='PENDING_FOR_NEW_CLARIFICATIONS'));return
        if censored>=8:
            report(dict(common,status='OPERATIONALLY_COMPROMISED_STOPPED',reason='Frozen threshold8; no further unstarted launches without owner review'));return
        if state.get('error_type')!='SafeError' or state.get('error_code')!='error':
            report(dict(common,status='STOPPED',reason='Not an eligible generic provider-interruption continuation'));return
        if (datetime.now(timezone.utc)-utc(state['started_utc'])).total_seconds()>=28800:
            report(dict(common,status='STOPPED',reason='Original execution window expired'));return
        if state['campaign']['reserved_requests']>=611:
            report(dict(common,status='STOPPED',reason='Original physical cap exhausted'));return
        # Evidence must show an actual provider stream failure, not a model/tool error.
        plan=read(ROOT/'plan.json')
        attempted=[p for p in plan if (ROOT/'trials'/p['id']/'result.json').exists()]
        last=read(ROOT/'trials'/attempted[-1]['id']/'result.json')
        if not last.get('error_metadata') or last['error_metadata'][-1]['failure_surface']!='IN_STREAM':
            report(dict(common,status='STOPPED',reason='No observed stream-failure basis'));return
        phase=ROOT/'operator'/f'continuation-{number:02d}'
        phase.mkdir(exist_ok=False)
        label=phase.relative_to(ROOT).as_posix()
        source=template.replace('operator/continuation-01',label)
        source=source.replace("assert read(ROOT/'phoenix-service.json')['stopped']",
                              f"assert read(ROOT/'{parent.relative_to(ROOT).as_posix()}/phoenix-service.json')['stopped']")
        source=source.replace('Only73 unstarted Sol cells; first3 retained including censored trial',
                              'Only currently unstarted Sol cells; every earlier attempted cell retained')
        (phase/'resume.py').write_text(source,encoding='utf-8')
        appendix={'date':'2026-11-19','kind':'Operational continuation source appendix; frozen trial and inputs unchanged',
            'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
            'parent_freeze_sha256':hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest(),
            'prior_retained':len(rows),'prior_charged':common['charged'],
            'no_trial_replay':True,'no_new_consent':True,'no_budget_or_window_reset':True}
        (phase/'SOURCE_APPENDIX.json').write_text(json.dumps(appendix,indent=2)+'\n')
        report(dict(common,status='CONTINUING_UNSTARTED',phase=label,remaining=76-len(rows)))
        with (phase/'launcher.log').open('x') as log:
            child=subprocess.Popen([sys.executable,'-B',str(phase/'resume.py')],cwd=phase,
                stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        (phase/'worker.json').write_text(json.dumps({'pid':child.pid,'started_utc':datetime.now(timezone.utc).isoformat()})+'\n')
        child.wait()
        after=read(ROOT/'status.json')
        if after['completed']<=state['completed']:
            report(dict(common,status='STOPPED',reason='No progress; inspect retained phase without automatic repetition'));return
        parent=phase;number+=1

if __name__=='__main__':main()
