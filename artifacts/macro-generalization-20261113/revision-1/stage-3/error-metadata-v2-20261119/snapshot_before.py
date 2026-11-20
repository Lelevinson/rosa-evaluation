"""Preserve hashes of prior G1 evidence and original protected entries."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
sys.path.insert(0, str(STAGE))
from common import REV, WORKSPACE, check_protected

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

output = HERE/'PRIOR_INPUTS_BEFORE.json'
assert not output.exists()
files = {str(p.relative_to(WORKSPACE)).replace('\\', '/'): sha(p)
         for p in REV.rglob('*') if p.is_file() and HERE not in p.parents
         and '__pycache__' not in p.parts}
for path in (STAGE/'protected-before.json', REV/'stage-2-continuation-1/protected-before.json'):
    for name in json.loads(path.read_text(encoding='utf-8-sig')):
        files[name.replace('\\', '/')] = sha(WORKSPACE/name)
receipt = dict(files_sha256=files, legacy_guard_before=check_protected(), model_requests=0)
output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'prior_files': len(files), 'legacy_guard': receipt['legacy_guard_before']}))
