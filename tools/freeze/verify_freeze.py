"""Verify the 2026-11-21 freeze. Exit 0 only if no frozen file changed, was added or deleted.

Python standard library plus the git command line; read-only.

Checks, against FREEZE_MANIFEST_2026-11-21.json:
  changed  - working-tree bytes or staged (index) content differ from the recorded SHA-256.
             A CRLF working copy is accepted only for files recorded as LF text
             (crlf_checkout_tolerated), i.e. git's own autocrlf checkout.
  deleted  - a manifest file is missing from disk, or no longer tracked by git.
  added    - a tracked or staged file sits in a frozen location but is not in the manifest.
             Frozen locations: every artifacts/<dir>/, docs/<dir>/, tools/<dir>/ subtree that
             holds frozen files; files directly in artifacts/, docs/, tools/; root reports
             (*.md, *.json) other than the living documents. New work in NEW directories passes.
Untracked files are not checked; the out-of-git backup carries its own SHA-256 list.

Usage:  python -I -B tools/freeze/verify_freeze.py
"""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_manifest import MANIFEST, REPO, TREES, blob_digests, in_scope, index_entries  # noqa: E402

SHOW = 50


def read_bytes(path):
    full = str(REPO / path)
    if os.name == 'nt':
        full = '\\\\?\\' + os.path.abspath(full)  # paths here exceed 260 characters
    with open(full, 'rb') as handle:
        return handle.read()


def main():
    manifest = json.loads((REPO / MANIFEST).read_text(encoding='utf-8'))
    files = manifest['files']
    frozen_children = {'/'.join(p.split('/')[:2]) + '/' for p in files
                       if p.startswith(TREES) and p.count('/') >= 2}

    def frozen_location(path):
        if '/' not in path:
            return in_scope(path)
        if not path.startswith(TREES):
            return False
        return path.count('/') == 1 or '/'.join(path.split('/')[:2]) + '/' in frozen_children

    index = index_entries()
    staged = blob_digests([index[p] for p in files if p in index])
    changed, deleted, untracked, normalized = [], [], [], 0
    for path, record in files.items():
        try:
            data = read_bytes(path)
        except FileNotFoundError:
            deleted.append(path)
            continue
        if path not in index:
            untracked.append(path)
            continue
        if hashlib.sha256(data).hexdigest() != record['sha256']:
            if (record['crlf_checkout_tolerated'] and
                    hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest() == record['sha256']):
                normalized += 1
            else:
                changed.append(path + '  (working tree)')
                continue
        if staged[index[path]][0] != record['sha256']:
            changed.append(path + '  (staged/committed content)')
    added = sorted(p for p in index if p not in files and frozen_location(p))

    print(f'manifest: {MANIFEST} ({manifest["freeze_tag"]}), {len(files)} frozen files, '
          f'{manifest["total_bytes"]} bytes')
    print(f'unchanged: {len(files) - len(changed) - len(deleted) - len(untracked)} '
          f'(of which {normalized} matched after CRLF->LF checkout normalization)')
    problems = (('changed', changed), ('deleted', deleted), ('no longer tracked', untracked), ('added', added))
    for name, items in problems:
        print(f'{name}: {len(items)}')
        for item in items[:SHOW]:
            print('   ' + item)
        if len(items) > SHOW:
            print(f'   ... {len(items) - SHOW} more')
    failed = any(items for _, items in problems)
    print('FREEZE VERIFY: ' + ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
