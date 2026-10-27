"""Build a separate final reviewed package; preserve the original execution ZIP."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

workspace = Path(__file__).resolve().parents[1]
root = workspace / 'rosa-evaluation'
base = root / 'artifacts/macro-m4-20261027'
archive = base.parent / 'ROSA_M4_FINAL_REVIEW_2026-10-27.zip'
assert not archive.exists(), 'Never overwrite an evidence archive'
analysis = json.loads((base / 'analysis.json').read_text())
assert analysis['complete'] and not analysis['clarification_review_pending']
assert json.loads((base / 'closeout.json').read_text())['study_complete']
old_archive = base.parent / 'ROSA_M4_EXECUTION_CHECKPOINT_2026-10-27.zip'
old_status = json.loads(old_archive.with_suffix('.verification.json').read_text())
assert hashlib.sha256(old_archive.read_bytes()).hexdigest() == old_status['sha256']
with zipfile.ZipFile(old_archive) as old:
    assert old.testzip() is None
    old_manifest = json.loads(old.read(base.name + '/archive-manifest.json'))['files']
    for name, digest in old_manifest.items():
        assert hashlib.sha256(old.read(base.name + '/' + name)).hexdigest() == digest

handoff = base / 'handoff'
handoff.mkdir(exist_ok=True)
for name in ('PROJECT_MASTER_README.md', 'PROJECT_LIVE_STATUS.json', 'MILESTONE_M4_STATUS.md',
             'docs/M4_EFFICIENCY_AND_TIMING_2026-10-27.md', 'tools/project_context.py'):
    destination = handoff / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / name, destination)
for name in ('m4-review-qwen.py', 'm4-final-report.py', 'm4-final-archive.py'):
    shutil.copyfile(workspace / 'reports' / name, base / 'operator' / name)

patterns = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{24,}'),
    re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')]
files = sorted(p for p in base.rglob('*') if p.is_file()
               and p not in (base / 'gazebo.lock', base / 'archive-manifest.json', base / 'final-archive-manifest.json')
               and p.suffix != '.tmp' and '__pycache__' not in p.parts)
manifest = {}
for path in files:
    assert path.suffix not in ('.dpapi', '.db', '.sqlite', '.sqlite3', '.pyc') and not path.name.startswith('.env')
    value = path.read_bytes()
    if any(pattern.search(value) for pattern in patterns):
        raise RuntimeError('possible_secret_in:' + path.relative_to(base).as_posix())
    manifest[path.relative_to(base).as_posix()] = hashlib.sha256(value).hexdigest()
manifest_path = base / 'final-archive-manifest.json'
manifest_path.write_text(json.dumps({'kind': 'final reviewed M4 evidence; mixed findings',
    'files': manifest, 'secret_pattern_scan': 'PASS',
    'original_execution_archive_sha256': old_status['sha256'],
    'original_execution_manifest_verified': len(old_manifest),
    'note': 'Historical review-history manifests belong to the unchanged original execution ZIP. '
            'Use this final manifest for the final package; handoff documents retain checkout-relative links.'}, indent=2) + '\n')
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as target:
    for path in [*files, manifest_path]:
        target.write(path, arcname=base.name + '/' + path.relative_to(base).as_posix())
with zipfile.ZipFile(archive) as target:
    assert target.testzip() is None
    for name, digest in manifest.items():
        assert hashlib.sha256(target.read(base.name + '/' + name)).hexdigest() == digest
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.sha256').write_text(checksum + '  ' + archive.name + '\n')
status = {'archive': archive.name, 'sha256': checksum,
    'manifest_files_verified': len(manifest), 'bytes': archive.stat().st_size,
    'zip_integrity': 'PASS', 'secret_pattern_scan': 'PASS',
    'original_execution_archive_preserved': True, 'original_manifest_files_verified': len(old_manifest),
    'study_complete': True, 'sol_retention': True, 'qwen_retention': False}
archive.with_suffix('.verification.json').write_text(json.dumps(status, indent=2) + '\n')
print(json.dumps(status, indent=2))
