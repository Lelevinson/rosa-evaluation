"""Snapshot all prior G1 files and protected inventories before local repair."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
sys.path.insert(0, str(STAGE))
from common import REV, WORKSPACE, check_protected

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

output = HERE / 'PRIOR_INPUTS_BEFORE.json'
assert not output.exists()
paths = {str(p.relative_to(WORKSPACE)).replace('\\', '/'): digest(p)
         for p in REV.rglob('*') if p.is_file() and HERE not in p.parents
         and '__pycache__' not in p.parts}
# Include protected runtime/source paths that are outside the G1 artifact tree.
for inventory in (STAGE/'protected-before.json', REV/'stage-2-continuation-1/protected-before.json'):
    for name in json.loads(inventory.read_text(encoding='utf-8-sig')):
        paths[name.replace('\\', '/')] = digest(WORKSPACE/name)
output.write_text(json.dumps({'sha256': paths, 'legacy_guard_before': check_protected(),
    'scope': 'All prior G1 files plus original protected-inventory entries; no pycache',
    'model_requests': 0}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'prior_files': len(paths), 'legacy_guard_before': check_protected()}))
