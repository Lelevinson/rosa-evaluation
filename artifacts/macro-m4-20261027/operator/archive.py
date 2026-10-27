"""Archive closed M4 execution evidence, with pending reviews explicitly retained."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

base = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/macro-m4-20261027')
manifest = {}
patterns = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{24,}'),
    re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')]
files = sorted(p for p in base.rglob('*') if p.is_file() and p.name not in ('gazebo.lock', 'archive-manifest.json')
    and p.suffix != '.tmp' and '__pycache__' not in p.parts)
for path in files:
    assert path.suffix not in ('.dpapi', '.db', '.sqlite', '.sqlite3', '.pyc') and not path.name.startswith('.env')
    value = path.read_bytes()
    if any(pattern.search(value) for pattern in patterns):
        raise RuntimeError('possible_secret_in:' + path.relative_to(base).as_posix())
    manifest[path.relative_to(base).as_posix()] = hashlib.sha256(value).hexdigest()
frozen = json.loads((base / 'freeze.json').read_text())
for name, expected in frozen['files'].items():
    assert hashlib.sha256((base / 'source' / name).read_bytes()).hexdigest() == expected
(base / 'archive-manifest.json').write_text(json.dumps({'files': manifest, 'secret_pattern_scan': 'PASS',
    'kind': 'execution checkpoint; consult analysis for pending transcript reviews'}, indent=2))
archive = base.parent / 'ROSA_M4_EXECUTION_CHECKPOINT_2026-10-27.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as target:
    for path in [*files, base / 'archive-manifest.json']:
        target.write(path, arcname=base.name + '/' + path.relative_to(base).as_posix())
with zipfile.ZipFile(archive) as target:
    assert target.testzip() is None
    for name, expected in manifest.items():
        assert hashlib.sha256(target.read(base.name + '/' + name)).hexdigest() == expected
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.sha256').write_text(checksum + '  ' + archive.name + '\n')
status = {'archive': archive.name, 'sha256': checksum, 'manifest_files_verified': len(manifest),
    'bytes': archive.stat().st_size, 'zip_integrity': 'PASS', 'secret_pattern_scan': 'PASS'}
archive.with_suffix('.verification.json').write_text(json.dumps(status, indent=2))
print(json.dumps(status))
