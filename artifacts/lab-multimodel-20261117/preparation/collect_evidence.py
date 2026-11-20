"""Archive the new study only; omit weights, virtualenvs, repos and credentials."""
from pathlib import Path
import hashlib
import json
import time
import zipfile

ROOT = Path('/media/naeem/d1/marvel proj')


def main():
    for _ in range(4 * 8 * 60 * 6 + 60):
        status_path = ROOT / 'results/operator-status.json'
        if status_path.exists():
            state = json.loads(status_path.read_text())
            if state['phase'] in ('EXECUTION_COMPLETE', 'STOPPED'):
                break
        time.sleep(10)
    else:
        raise RuntimeError('Evidence collector window expired')
    paths = set()
    for sub in ['study', 'results']:
        paths.update(p for p in (ROOT / sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    original = json.loads((ROOT / 'baseline/original-m4-freeze.json').read_text())
    paths.add(ROOT / 'baseline/original-m4-freeze.json')
    paths.update(ROOT / 'baseline' / name for name in original['files'])
    paths.add(ROOT / 'README.md')
    paths.update(ROOT / name for name in [
        'baseline/rosa-research/README.md', 'baseline/rosa-research/LICENSE',
        'baseline/rosa-evaluation/experiments/__init__.py'])
    for path in (ROOT / 'preparation').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and (
            path.suffix in ('.json', '.log', '.txt', '.md', '.py', '.sh') or
            path.name in ('Dockerfile', '.dockerignore')):
            paths.add(path)
    # None of the selected paths is a credential-store/home directory. Hashes
    # describe exactly the bytes archived, rather than Git HEAD alone.
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)}
    destination = ROOT / 'evidence'
    destination.mkdir(exist_ok=True)
    archive = destination / 'ROSA_LAB_MULTIMODEL_2026-11-17.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as out:
        for path in sorted(paths):
            out.write(path, str(path.relative_to(ROOT)))
        out.writestr('ARCHIVE_MANIFEST.json', json.dumps({'files': manifest,
            'operator_phase': state['phase'], 'date': '2026-11-17',
            'models_and_credentials_excluded': True}, indent=2) + '\n')
    with zipfile.ZipFile(archive) as test:
        assert test.testzip() is None
        for name, expected in manifest.items():
            assert hashlib.sha256(test.read(name)).hexdigest() == expected
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256').write_text(digest + '  ' + archive.name + '\n')
    (destination / 'VERIFICATION.json').write_text(json.dumps({'files': len(manifest),
        'sha256': digest, 'bytes': archive.stat().st_size, 'all_hashes_match': True,
        'zip_integrity_pass': True, 'operator_phase': state['phase']}, indent=2))
    print('EVIDENCE_READY', archive, digest, flush=True)


if __name__ == '__main__':
    main()
