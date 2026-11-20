"""Post-run integrity inventory; does not change the pre-run experimental freeze."""
from datetime import datetime,timezone
import json
from pathlib import Path
from prepare import read,write,digest

ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/'stage1-manifest.json').exists(),'Retain the first sealed receipt.'
    assert read(ROOT/'phoenix-service.json')['stopped']
    assert read(ROOT/'analysis.json')['pass']
    frozen=read(ROOT/'freeze.json')['files']
    assert all(digest(ROOT/name)==value for name,value in frozen.items())
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*'))
           if p.is_file() and p.name not in ('stage1-manifest.json','manifest-verification.json')}
    write('stage1-manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'kind':'Post-run retained source/evidence inventory, not the pre-run protocol freeze',
        'files':files})
    changed=[name for name,value in files.items() if digest(ROOT/name)!=value]
    receipt={'pass':not changed,'verified_files':len(files),'mismatches':changed,
        'manifest_sha256':digest(ROOT/'stage1-manifest.json'),'frozen_files_unchanged':len(frozen),
        'phoenix_owned_service_stopped':True,'live_model_requests':0}
    write('manifest-verification.json',receipt)
    print(json.dumps(receipt))
    assert receipt['pass']

if __name__=='__main__':main()
