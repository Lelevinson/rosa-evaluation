"""Write FREEZE_MANIFEST_2026-11-21.json: SHA-256 of every frozen tracked file.

Python standard library plus the git command line; no model, network or lab access.

Scope (tracked files only, as staged in the git index):
  * everything under artifacts/, docs/ and tools/;
  * root-level reports (*.md, *.json), except the living documents in LIVING.
Hashes are taken over the canonical repository bytes (the git index blob), so the
manifest is identical on Windows and Linux checkouts. The script refuses to run if
any in-scope working-tree file differs from the index. Output is deterministic:
sorted paths, no timestamps, no commit id (FREEZE.md records the commit and tag).

Usage:  python -I -B tools/freeze/make_manifest.py
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = 'FREEZE_MANIFEST_2026-11-21.json'
TAG = 'freeze-2026-11-21'
TREES = ('artifacts/', 'docs/', 'tools/')
ROOT_SUFFIXES = ('.md', '.json')
# Living documents keep being updated after the freeze; the tag preserves their
# frozen-day version. The manifest cannot contain its own hash.
LIVING = frozenset(('PROJECT_MASTER_README.md', 'PROJECT_LIVE_STATUS.json', 'README.md', MANIFEST))


def git(*args, stdin=None):
    cmd = ['git', '-c', 'core.longpaths=true', '-c', 'core.quotepath=off', '-C', str(REPO), *args]
    result = subprocess.run(cmd, input=stdin, capture_output=True)
    if result.returncode:
        raise SystemExit('git failed: ' + ' '.join(args) + '\n' + result.stderr.decode('utf-8', 'replace'))
    return result.stdout


def in_scope(path):
    if path.startswith(TREES):
        return True
    return '/' not in path and path.endswith(ROOT_SUFFIXES) and path not in LIVING


def index_entries():
    """{path: blob id} for stage-0 index entries (regular files and symlinks)."""
    entries = {}
    for record in git('ls-files', '-s', '-z').split(b'\0'):
        if not record:
            continue
        meta, path = record.split(b'\t', 1)
        mode, blob, stage = meta.decode().split()
        if stage != '0':
            raise SystemExit('unmerged index entry: ' + path.decode('utf-8'))
        if mode == '160000':
            continue  # submodule pointer, no file content
        entries[path.decode('utf-8')] = blob
    return entries


def crlf_tolerated():
    """Paths whose index text is LF and that git may check out with CRLF (autocrlf)."""
    tolerated = set()
    for record in git('ls-files', '--eol', '-z').split(b'\0'):
        if not record:
            continue
        meta, path = record.split(b'\t', 1)
        fields = meta.decode().split()
        index_eol, attr = fields[0], fields[2] if len(fields) > 2 else 'attr/'
        if index_eol == 'i/lf' and '-text' not in attr:
            tolerated.add(path.decode('utf-8'))
    return tolerated


def blob_digests(blobs):
    """SHA-256 and size of each blob's content, via one git cat-file --batch."""
    unique = sorted(set(blobs))
    out = git('cat-file', '--batch', stdin=('\n'.join(unique) + '\n').encode())
    digests, pos = {}, 0
    for blob in unique:
        end = out.index(b'\n', pos)
        name, kind, size = out[pos:end].decode().split()
        if name != blob or kind != 'blob':
            raise SystemExit('unexpected cat-file record for ' + blob)
        size = int(size)
        content = out[end + 1:end + 1 + size]
        digests[blob] = (hashlib.sha256(content).hexdigest(), size)
        pos = end + 1 + size + 1
    return digests


def frozen_files():
    entries = {p: b for p, b in index_entries().items() if in_scope(p)}
    dirty = [p for p in git('diff', '--name-only', '-z').decode('utf-8').split('\0') if p and in_scope(p)]
    if dirty:
        raise SystemExit('working tree differs from index for in-scope files: ' + ', '.join(sorted(dirty)[:20]))
    digests, tolerated = blob_digests(entries.values()), crlf_tolerated()
    return {p: {'sha256': digests[b][0], 'bytes': digests[b][1], 'crlf_checkout_tolerated': p in tolerated}
            for p, b in sorted(entries.items())}


def main():
    files = frozen_files()
    manifest = {
        'manifest': MANIFEST, 'freeze_tag': TAG, 'freeze_date': '2026-11-21', 'frozen_by': 'Martin',
        'hash_basis': 'SHA-256 of the canonical repository bytes (git index blob content) of each file',
        'scope': {'trees': list(TREES), 'root_files_with_suffix': list(ROOT_SUFFIXES),
                  'living_not_frozen': sorted(LIVING), 'tracked_files_only': True},
        'file_count': len(files), 'total_bytes': sum(v['bytes'] for v in files.values()),
        'files': files}
    text = json.dumps(manifest, indent=1, sort_keys=True, ensure_ascii=False) + '\n'
    (REPO / MANIFEST).write_bytes(text.encode('utf-8'))
    print(f'wrote {MANIFEST}: {len(files)} files, {manifest["total_bytes"]} bytes, '
          f'sha256 {hashlib.sha256(text.encode("utf-8")).hexdigest()}')


if __name__ == '__main__':
    sys.exit(main())
