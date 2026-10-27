"""Independently read back approved GitHub backups; never upload or print credentials."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027'


def api(route, raw=False):
    command = ['gh', 'api']
    if raw:
        command += ['-H', 'Accept: application/vnd.github.raw+json']
    return subprocess.check_output(command + [route])


def git(repo, *args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo), *args])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evaluation-repo', help='Approved OWNER/REPO destination only; omit while approval is pending')
    args = parser.parse_args()
    source = ROOT.parent / 'rosa-research'
    head = git(source, 'rev-parse', 'HEAD').decode().strip()
    remote = json.loads(api('repos/Lelevinson/rosa-research/git/ref/heads/member/martin'))['object']['sha']
    assert remote == head, 'research_remote_head_not_current'
    archive = api('repos/Lelevinson/rosa-research/tarball/' + head)
    expected = {}
    for entry in git(source, 'ls-tree', '-rz', head).split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        mode, kind, oid = meta.split()
        assert kind == b'blob', 'submodule_requires_separate_backup'
        expected[name.decode()] = oid.decode()
    actual = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as downloaded:
        for entry in downloaded.getmembers():
            if entry.isdir():
                continue
            _, _, name = entry.name.partition('/')
            if entry.issym():
                value = entry.linkname.encode()
            else:
                assert entry.isfile()
                value = downloaded.extractfile(entry).read()
            actual[name] = hashlib.sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest()
    assert actual == expected, 'remote_source_tree_mismatch'
    record = {'date': '2026-10-27', 'status': 'PARTIAL',
        'research': {'repository': 'Lelevinson/rosa-research', 'branch': 'member/martin',
                     'commit': head, 'remote_tip_matches': True, 'remote_tarball_files_verified': len(expected),
                     'tarball_sha256': hashlib.sha256(archive).hexdigest()},
        'evaluation': {'status': 'AWAITING_PUBLIC_PRIVATE_DESTINATION_APPROVAL'}}
    if args.evaluation_repo:
        destination = args.evaluation_repo
        commit = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
        ref = json.loads(api(f'repos/{destination}/git/ref/heads/member/martin'))['object']['sha']
        assert ref == commit, 'evaluation_remote_tip_not_current'
        paths = ['artifacts/ROSA_M5_RETAINED_WORK_BACKUP_2026-10-27.zip',
                 'artifacts/ROSA_M5_RETAINED_LOCKFILES_ADDENDUM_2026-10-27.zip',
                 'artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.zip']
        verified = {}
        for name in paths:
            value = api(f'repos/{destination}/contents/{name}?ref={commit}', raw=True)
            expected_bytes = (ROOT / name).read_bytes()
            digest = hashlib.sha256(value).hexdigest()
            assert digest == hashlib.sha256(expected_bytes).hexdigest(), 'remote_archive_mismatch:' + name
            with zipfile.ZipFile(io.BytesIO(value)) as archive:
                assert archive.testzip() is None
                if name.endswith('RETAINED_WORK_BACKUP_2026-10-27.zip'):
                    manifest = json.loads(archive.read('BACKUP_MANIFEST.json'))['files']
                    for filename, sha in manifest.items():
                        assert hashlib.sha256(archive.read(filename)).hexdigest() == sha
                elif name.endswith('LOCKFILES_ADDENDUM_2026-10-27.zip'):
                    manifest = json.loads(archive.read('LOCKFILE_MANIFEST.json'))['files']
                    for filename, sha in manifest.items():
                        assert hashlib.sha256(archive.read(filename)).hexdigest() == sha
                else:
                    prefix = 'macro-m4-20261027/'
                    manifest = json.loads(archive.read(prefix + 'final-archive-manifest.json'))['files']
                    for filename, sha in manifest.items():
                        assert hashlib.sha256(archive.read(prefix + filename)).hexdigest() == sha
            verified[name] = {'sha256': digest, 'bytes_downloaded': len(value), 'manifest_files_verified': len(manifest)}
            print(json.dumps({'remote_archive_verified': name, **verified[name]}), flush=True)
        record['evaluation'] = {'repository': destination, 'branch': 'member/martin', 'commit': commit,
                                'remote_tip_matches': True, 'downloaded_archives': verified}
        record['status'] = 'PASS'
    record['summary'] = ('Research source tree and evaluation evidence were downloaded from the approved off-machine destinations and verified.'
                         if record['status'] == 'PASS' else
                         'Research branch and every file in its remote source tarball are verified; evaluation upload remains pending explicit destination/disclosure approval.')
    (OUT / 'off-machine-verification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__': main()
