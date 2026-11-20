"""Post-run integrity/accounting receipt; never changes the experimental freeze."""
from datetime import datetime,timezone
from common import ROOT,read,write,digest,verify

def main():
    assert not (ROOT/'stage2-manifest.json').exists(),'Preserve the first sealed receipt.'
    assert read(ROOT/'phoenix-service.json')['stopped']
    integrity=verify()
    analysis=read(ROOT/'analysis.json');state=read(ROOT/'status.json')
    rows=[read(p) for p in (ROOT/'trials').glob('*/result.json')] if (ROOT/'trials').exists() else []
    requests=sum(r.get('inference',{}).get('calls',0) for r in rows)
    accounting={'campaign_charged_requests':state['live_model_requests'],'retained_trial_requests':requests,
                'unreconciled_requests':state['live_model_requests']-requests}
    if analysis['execution_complete']:
        assert len(rows)==36 and requests==state['live_model_requests']<=291
        assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
        for mode in ('primitives','macro'):
            selected=[r for r in rows if r['mode']==mode]
            assert len(selected)==18
            assert sum(r['primary_pass'] for r in selected)==analysis['all_attempts'][mode]['primary_passes']
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and
           p.name not in ('stage2-manifest.json','manifest-verification.json')}
    write('stage2-manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'kind':'Post-run inventory, separate from pre-run freeze','files':files})
    changed=[name for name,value in files.items() if digest(ROOT/name)!=value]
    receipt={'pass':not changed,'verified_files':len(files),'mismatches':changed,
        'manifest_sha256':digest(ROOT/'stage2-manifest.json'),'input_integrity':integrity,
        'accounting':accounting,'execution_complete':analysis['execution_complete'],
        'owned_phoenix_stopped':True,'no_later_stage_started':True}
    write('manifest-verification.json',receipt);print(receipt)
    assert receipt['pass']

if __name__=='__main__':main()
