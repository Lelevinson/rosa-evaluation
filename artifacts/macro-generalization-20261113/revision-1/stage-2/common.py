"""Paths, immutable input checks and JSON checkpoints for G1 dev."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REV=ROOT.parent
WORKSPACE=ROOT.parents[4]
REPO=ROOT.parents[3]
STAGE1=REV/'stage-1'
PROJECT='rosa-g1-sol-dev-20261114'
ROOT_SPAN='g1.sol.dev'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def verify():
    freeze=read(ROOT/'freeze.json')
    protected=read(ROOT/'protected-before.json')
    changed=[name for name,value in freeze['files'].items() if digest(ROOT/name)!=value]
    changed += [name for name,value in protected.items() if digest(WORKSPACE/name)!=value]
    if changed:raise RuntimeError('protected_or_frozen_file_mismatch:'+repr(changed))
    return {'pass':True,'frozen_files':len(freeze['files']),'protected_files':len(protected),'mismatches':[]}
