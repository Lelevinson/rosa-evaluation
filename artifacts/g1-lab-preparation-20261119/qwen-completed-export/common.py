"""Qwen lab port; frozen original inputs and a separately sealed backend assembly."""
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REV=ROOT.parent
REPO=ROOT.parents[3]
WORKSPACE=REPO.parent
ADJUDICATION=REV/'stage-3/clarification-scoring-v2-20261119'
sys.path[:0]=[str(WORKSPACE/'rosa-research/src'),str(REPO),str(REV),str(ROOT),str(REV/'stage-2'),str(ADJUDICATION)]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,value):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(value,indent=2)+'\n');os.replace(t,p)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(require_seal=False):
 f=read(REV/'stage-4/freeze.json');bad=[n for n,d in f['files_sha256'].items() if digest(WORKSPACE/n)!=d]
 if (ROOT/'freeze.json').exists():bad += [n for n,d in read(ROOT/'freeze.json')['files_sha256'].items() if digest(ROOT/n)!=d]
 elif require_seal:raise RuntimeError('Qwen_backend_assembly_not_sealed')
 if bad:raise RuntimeError('Frozen_input_mismatch:'+repr(bad))
 return {'pass':True,'original_frozen_files':len(f['files_sha256']),'mismatches':bad}
