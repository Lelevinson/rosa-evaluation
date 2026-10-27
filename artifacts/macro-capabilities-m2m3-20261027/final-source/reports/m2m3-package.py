"""Package only the new milestone's explicit evidence directory. No credentials."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

root = Path('/mnt/c/Proj/robotics/introtorobotics')
base = root / 'rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

shutil.copyfile(root / 'rosa-evaluation/docs/M2_M3_COMBINED_REPORT_2026-10-27.md', base / 'M2_M3_COMBINED_REPORT.md')
shutil.copyfile(root / 'rosa-evaluation/docs/M2_M3_CAPABILITIES_ENGINEERING_2026-10-27.md', base / 'ENGINEERING_PROTOCOL.md')
shutil.copyfile(root / 'rosa-evaluation/artifacts/macro-module-v1-20261027/simulator-inventory.json', base / 'simulator-inventory-from-m1.json')
shutil.copyfile(root / 'reports/m2m3-package.py', base / 'final-source/reports/m2m3-package.py')
(base / 'development-error-record.json').write_text(json.dumps({
    'wrong_working_directory_regression_attempt': {'discovered': 186, 'errors': 39, 'skipped': 41,
        'reason': 'workspace-root invocation could not resolve upstream src imports',
        'resolution': 'ran from each repository directory; final complete logs included'},
    'auth_restart_first_attempt': 'auth-resume-check-initial-failure.json',
    'invalidated_auth_grant': 'auth-resume-check-invalidated-grant.json',
    'operator_zero_ui_budget_mistake': 'auth-repair-invalid-ui-budget.log',
    'final_auth_validation': 'auth-resume-check.json'}, indent=2) + '\n')

revisions = {}
for name in ('rosa-research', 'rosa-evaluation'):
    revisions[name] = subprocess.check_output(['git', '-c', 'safe.directory=' + str(root / name),
        '-C', str(root / name), 'rev-parse', 'HEAD'], text=True).strip()
(base / 'checkpoint-revisions.json').write_text(json.dumps({'research_final': revisions['rosa-research'],
    'evaluation_parent_before_evidence_commit': revisions['rosa-evaluation'], 'branch': 'member/martin',
    'remote_push_performed': False}, indent=2) + '\n')

patterns = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{24,}'),
    re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')]
files = sorted(p for p in base.rglob('*') if p.is_file() and p.name not in ('archive-manifest.json', 'gazebo.lock')
    and '__pycache__' not in p.parts)
for path in files:
    assert path.suffix not in ('.dpapi', '.db', '.sqlite', '.sqlite3', '.pyc')
    assert not path.name.startswith('.env')
    contents = path.read_bytes()
    if any(pattern.search(contents) for pattern in patterns):
        raise RuntimeError('possible_secret_pattern_in:' + path.relative_to(base).as_posix())
manifest = {p.relative_to(base).as_posix(): sha(p) for p in files}
(base / 'archive-manifest.json').write_text(json.dumps({'algorithm': 'sha256', 'files': manifest,
    'secret_pattern_scan': 'PASS', 'protected_credential_files_included': False}, indent=2) + '\n')
archive = base.parent / 'ROSA_MACRO_M2_M3_ENGINEERING_AND_LIVE_DEMO_2026-10-27.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
    for path in [*files, base / 'archive-manifest.json']:
        target.write(path, arcname='macro-capabilities-m2m3-20261027/' + path.relative_to(base).as_posix())
with zipfile.ZipFile(archive) as packed:
    assert packed.testzip() is None
    for name, expected in manifest.items():
        actual = hashlib.sha256(packed.read('macro-capabilities-m2m3-20261027/' + name)).hexdigest()
        assert actual == expected, name
archive.with_suffix('.sha256').write_text(sha(archive) + '  ' + archive.name + '\n')
print(json.dumps({'archive': archive.name, 'manifest_files_verified': len(manifest),
    'zip_integrity': 'PASS', 'secret_pattern_scan': 'PASS', 'sha256': sha(archive), 'bytes': archive.stat().st_size}))
