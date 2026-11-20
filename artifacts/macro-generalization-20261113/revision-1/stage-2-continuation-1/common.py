"""Continuation paths and immutable input checks; never write the original run."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REV=ROOT.parent
REPO=ROOT.parents[3]
WORKSPACE=ROOT.parents[4]
ORIGINAL=REV/'stage-2'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def verify():
    freeze=read(ROOT/'freeze.json');protected=read(ROOT/'protected-before.json')
    changed=[n for n,v in freeze['files'].items() if digest(ROOT/n)!=v]
    changed += [n for n,v in protected.items() if digest(WORKSPACE/n)!=v]
    if changed:raise RuntimeError('protected_or_frozen_file_mismatch:'+repr(changed))
    return {'pass':True,'frozen_files':len(freeze['files']),'protected_files':len(protected),'mismatches':[]}
def require_approval():
    path=ROOT/'window-approval.json'
    if not path.exists():raise RuntimeError('explicit_new_time_window_approval_required')
    approval=read(path)
    if not (approval.get('approved') is True and approval.get('window_seconds')==1800 and
            approval.get('cumulative_request_cap')==291 and approval.get('prior_requests')==66 and
            approval.get('freeze_sha256')==digest(ROOT/'freeze.json')):
        raise RuntimeError('continuation_approval_does_not_match_frozen_scope')
    return approval
