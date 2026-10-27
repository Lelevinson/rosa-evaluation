"""Preserve dependency-lock copies excluded by the original broad lock filter."""
import hashlib
import json
from pathlib import Path
import zipfile

from .backup import ROOT, WORKSPACE, OUT, Scanner, git


def main():
    selected = []
    for name in ('rosa-research', 'rosa-evaluation'):
        repo = WORKSPACE / name
        names = git(repo, 'ls-files', '--others', '--exclude-standard').splitlines()
        names += git(repo, 'diff', '--name-only', 'HEAD').splitlines()
        selected += [repo / n for n in names if Path(n).name == 'uv.lock']
    assert len(selected) == 14
    scanner, manifest = Scanner(), {}
    for path in selected:
        value = path.read_bytes()
        name = path.relative_to(WORKSPACE).as_posix()
        scanner.scan(value, name)
        manifest[name] = hashlib.sha256(value).hexdigest()
    assert not scanner.findings
    archive = ROOT / 'artifacts/ROSA_M5_RETAINED_LOCKFILES_ADDENDUM_2026-10-27.zip'
    metadata = {'kind': 'Dependency-lock backup addendum; original retained backup remains unchanged',
        'reason': 'The original filter treated every .lock as transient, excluding14 retained uv.lock copies. '
                  'Current committed locks were protected by repository history; this addendum preserves '
                  'the additional historical source-snapshot copies explicitly. The filter is corrected.',
        'files': manifest}
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as target:
        for path in selected:
            target.writestr(path.relative_to(WORKSPACE).as_posix(), path.read_bytes())
        target.writestr('LOCKFILE_MANIFEST.json', json.dumps(metadata, indent=2))
    with zipfile.ZipFile(archive) as target:
        assert target.testzip() is None
        for name, digest in manifest.items():
            assert hashlib.sha256(target.read(name)).hexdigest() == digest
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256').write_text(digest + '  ' + archive.name + '\n')
    result = {'archive': archive.name, 'sha256': digest, 'bytes': archive.stat().st_size,
              'manifest_files_verified': len(manifest), 'zip_integrity': 'PASS', 'credential_scan': 'PASS',
              'off_machine_status': 'NOT_YET_UPLOADED', 'reason': metadata['reason']}
    archive.with_suffix('.verification.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'lockfile-backup-addendum.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':main()
