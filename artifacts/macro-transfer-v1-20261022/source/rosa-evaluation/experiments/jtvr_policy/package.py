"""Create a portable evidence archive and verify its bytes before handoff."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from .campaign import DEFAULT, ROOT, assert_frozen, json_write


def main():
    assert_frozen(DEFAULT)
    destination = DEFAULT
    archive = destination.parent / (destination.name + '-evidence.zip')
    if archive.exists():
        raise RuntimeError('archive_exists_do_not_overwrite')
    shutil.copy2(Path(__file__), destination / 'analysis-source/package.py')
    # Include explanatory context. Historical archives/checkout links remain local.
    context_files = [ROOT / 'docs/STAGE4_POLICY_PROTOCOL_2026-10-21.md',
        ROOT / 'docs/RECAP_FOR_CHATGPT_2026-10-21.md',
        ROOT / 'docs/PROJECT_ROADMAP_SIX_STAGES.md',
        ROOT / 'docs/JTVR_SPEC_REVIEW_AND_MINIMAL_EXPERIMENT.md']
    hashes = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in destination.rglob('*') if p.is_file() and p.name != 'evidence-manifest.json'}
    json_write(destination / 'evidence-manifest.json', hashes)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for path in sorted(destination.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(ROOT))
        for path in context_files:
            output.write(path, path.relative_to(ROOT))
    with zipfile.ZipFile(archive) as output:
        error = output.testzip()
        if error:
            raise RuntimeError('bad_zip_member:' + error)
        for name, wanted in hashes.items():
            data = output.read(str((destination.relative_to(ROOT) / name).as_posix()))
            if hashlib.sha256(data).hexdigest() != wanted:
                raise RuntimeError('archive_hash_mismatch:' + name)
        files = len(output.namelist())
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    sidecar = archive.with_suffix('.sha256')
    sidecar.write_text(archive_hash + '  ' + archive.name + '\n')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'sha256': archive_hash, 'files': files, 'crc_and_member_hashes_verified': True}))


if __name__ == '__main__':
    main()
