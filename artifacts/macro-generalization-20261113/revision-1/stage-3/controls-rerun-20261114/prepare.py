from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[5]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
