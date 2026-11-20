"""Stage 3 is zero-inference preparation; all writes stay in this directory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REV = ROOT.parent
REPO = ROOT.parents[3]
WORKSPACE = ROOT.parents[4]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, value):
    path = ROOT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

def check_protected():
    protected = read(ROOT/'protected-before.json')
    ancestral = read(REV/'stage-2-continuation-1/protected-before.json')
    changed = sorted({name for mapping in (protected, ancestral) for name, value in mapping.items()
                      if digest(WORKSPACE/name) != value})
    result = dict(pass_=not changed, files=len(protected), ancestral_files=len(ancestral), mismatches=changed)
    result['pass'] = result.pop('pass_')
    return result

def dev_rows():
    rows = [read(path) for name in ('stage-2', 'stage-2-continuation-1')
            for path in sorted((REV/name/'trials').glob('*/result.json'))]
    assert len(rows) == len({r['id'] for r in rows}) == 36
    return rows
