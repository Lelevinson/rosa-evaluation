"""Seal the owner's authorship-policy amendment. No model, auth or Git actions."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
REVISION=ROOT.parents[1]
OLD=REVISION.parent


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def main():
    checked=0
    changed=[]
    for base,manifest_name in [(REVISION,'revision-manifest.json'),(OLD,'stage0-manifest.json')]:
        manifest=read(base/manifest_name)
        for name,expected in manifest['files'].items():
            checked+=1
            if digest(base/name)!=expected:changed.append(str(base/name))
    assert not changed,changed
    assert read(OLD/'STAGE0_CHECKPOINT.json')['status']=='STOPPED_INTERFACE_INCOMPATIBLE'
    cases=read(REVISION/'cases.json')
    assert len(cases)==54 and all(c['author']=='Codex (AI)' and c['independent_author'] is False for c in cases)
    status=read(ROOT/'amendment-status.json')
    assert status['authorship_fallback_authorized'] and status['original_authorship_requirement_replaced_for_G1']
    assert not status['original_independent_authorship_criterion_met']
    assert not status['Stage1_authorized_by_this_amendment'] and status['model_requests']==0
    docs=[ROOT/'AUTHORSHIP_AMENDMENT.md',REVISION/'CURRENT_STATUS.md']
    missing=[]
    for doc in docs:
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
            target=target.split('#',1)[0]
            if target and '://' not in target and not (doc.parent/target).exists():missing.append([doc.name,target])
    assert not missing,missing
    write('verification.json',{'pass':True,'historical_manifest_entries_checked':checked,'historical_mismatches':changed,
          'case_files_unchanged':True,'AI_authored_draft_cases':54,'old_STOPPED_status_unchanged':True,
          'authorship_requirement_replaced':True,'Stage1_authorized':False,'model_requests':0,'missing_links':missing})
    files={p.name:digest(p) for p in sorted(ROOT.iterdir()) if p.is_file() and p.name not in ('manifest.json','manifest-verification.json')}
    files['../../CURRENT_STATUS.md']=digest(REVISION/'CURRENT_STATUS.md')
    write('manifest.json',{'date':'2026-11-13','kind':'owner-approved authorship fallback; not experiment launch approval',
          'parent_revision_manifest_sha256':digest(REVISION/'revision-manifest.json'),
          'original_stopped_manifest_sha256':digest(OLD/'stage0-manifest.json'),'files':files})
    mismatches=[name for name,expected in files.items() if digest(ROOT/name)!=expected]
    assert not mismatches,mismatches
    write('manifest-verification.json',{'pass':True,'amendment_files_checked':len(files),'mismatches':mismatches,
          'manifest_sha256':digest(ROOT/'manifest.json')})
    print(json.dumps({'pass':True,'historical_files_unchanged':checked,'AI_authored_cases':54,
                     'authorship_fallback_recorded':True,'model_requests':0,'Stage1_started':False}))


if __name__=='__main__':main()
