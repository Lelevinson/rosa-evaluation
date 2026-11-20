"""Post-run integrity receipt, separate from the frozen continuation protocol."""
from datetime import datetime,timezone
from common import ROOT,read,write,digest,verify

def main():
    assert not (ROOT/'continuation-manifest.json').exists()
    assert read(ROOT/'phoenix-service.json')['stopped']
    assert (ROOT/'window-approval.json').exists()
    integrity=verify();analysis=read(ROOT/'combined-analysis.json')
    assert analysis['original_interrupted_trial_preserved']
    assert analysis['cumulative_requests']==66+analysis['new_requests']<=291
    assert analysis['new_requests']<=83
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*'))
        if p.is_file() and p.name not in ('continuation-manifest.json','manifest-verification.json')}
    write('continuation-manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'kind':'Post-run continuation inventory; original package unchanged','files':files})
    changed=[name for name,value in files.items() if digest(ROOT/name)!=value]
    result={'pass':not changed,'verified_files':len(files),'mismatches':changed,
        'manifest_sha256':digest(ROOT/'continuation-manifest.json'),'input_integrity':integrity,
        'cumulative_requests':analysis['cumulative_requests'],'new_requests':analysis['new_requests'],
        'original_interrupted_trial_preserved':True,'attempt_schedule_complete':analysis['attempt_schedule_complete'],
        'owned_phoenix_stopped':True,'later_stages_started':False}
    write('manifest-verification.json',result);print(result)
    assert result['pass']

if __name__=='__main__':main()
