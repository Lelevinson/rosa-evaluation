"""Frozen held-out paths and atomic mutable checkpoints; historical files read-only."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
REV=ROOT.parent
STAGE3=REV/'stage-3'
REPO=ROOT.parents[3]
WORKSPACE=REPO.parent
METADATA=STAGE3/'error-metadata-v2-20261119'
ADJUDICATION=STAGE3/'clarification-scoring-v2-20261119'
sys.path[:0]=[str(WORKSPACE/'rosa-research/src'),str(REPO),str(REV),str(ROOT),
              str(REV/'stage-2'),str(METADATA),str(ADJUDICATION)]

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(name,value):
    path=ROOT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)

def verify():
    freeze=read(ROOT/'freeze.json')
    changed=[name for name,value in freeze['files_sha256'].items() if digest(WORKSPACE/name)!=value]
    if changed:raise RuntimeError('frozen_or_protected_input_mismatch:'+repr(changed))
    return {'pass':True,'files':len(freeze['files_sha256']),'mismatches':[]}

def check_protected():return verify()
