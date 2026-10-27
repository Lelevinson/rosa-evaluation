"""Credential-check branch history and preserve retained working research evidence."""
import io
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
OUT = ROOT / 'artifacts/macro-m5-20261027'
ARCHIVE = ROOT / 'artifacts/ROSA_M5_RETAINED_WORK_BACKUP_2026-10-27.zip'
PATTERNS = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'api_secret': re.compile(rb'\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{24,}'),
    'jwt': re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),
    'literal_credential': re.compile(rb'''(?i)(?:access_token|refresh_token|client_secret)["']?\s*[:=]\s*["'][A-Za-z0-9_.~-]{24,}["']'''),
    'callback_credential': re.compile(rb'https?://[^\s"<>]*(?:[?&](?:code|access_token|refresh_token)=)[A-Za-z0-9_-]{12,}'),
}
# Reviewed exact file contents, not a generic suppression of token-like strings.
# Both versions initialize an uppercase dummy access-token sentinel with
# _expires_at=0, forcing provider refresh before inference. No real token is here.
REVIEWED_SENTINEL_FILES = {
    '1edec36f59d19204e0803084897c092acbc4752e2916c5eb421153f4e468b34b',
    '70949125806976b4f6e52a2031c4048637b8d31d53aa89ce4b2e9e030b0880d1',
}


def git(repo, *arguments, binary=False):
    prefix = ['git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo)]
    return subprocess.check_output(prefix + list(arguments), text=not binary)


class Scanner:
    def __init__(self):
        self.findings = []
        self.reviewed_noncredentials = []
        self.seen = set()
        self.values = 0
        self.archive_entries = 0
        self.expanded_bytes = 0

    def scan(self, value, origin, depth=0):
        digest = hashlib.sha256(value).digest()
        if digest in self.seen:
            return
        self.seen.add(digest)
        self.values += 1
        for name, pattern in PATTERNS.items():
            if pattern.search(value):
                finding = {'origin': origin, 'kind': name, 'content_sha256': digest.hex()}
                if name == 'literal_credential' and digest.hex() in REVIEWED_SENTINEL_FILES:
                    self.reviewed_noncredentials.append({**finding,
                        'reason': 'Expired noncredential uppercase sentinel; forced renewal before inference. Exact-file review.'})
                else:
                    self.findings.append(finding)
        if value.startswith(b'PK\x03\x04'):
            if depth >= 4:
                raise RuntimeError('archive_depth_requires_review:' + origin)
            with zipfile.ZipFile(io.BytesIO(value)) as archive:
                for entry in archive.infolist():
                    if entry.is_dir():
                        continue
                    if entry.file_size > 64 * 1024**2:
                        raise RuntimeError('large_archive_entry_requires_review:' + origin)
                    self.expanded_bytes += entry.file_size
                    if self.expanded_bytes > 3 * 1024**3:
                        raise RuntimeError('archive_scan_budget_exceeded')
                    self.archive_entries += 1
                    self.scan(archive.read(entry), origin + '::' + entry.filename, depth + 1)


def history(repo, scanner):
    objects = git(repo, 'rev-list', '--objects', 'member/martin').splitlines()
    paths = {}
    for item in objects:
        digest, _, name = item.partition(' ')
        paths[digest] = name
    prefix = ['git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo)]
    headers = subprocess.check_output(prefix + ['cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)'],
        input=('\n'.join(paths) + '\n').encode()).splitlines()
    blobs = [line.split()[0].decode() for line in headers if line.split()[1] == b'blob']
    data = subprocess.check_output(prefix + ['cat-file', '--batch'], input=('\n'.join(blobs) + '\n').encode())
    offset = 0
    for digest in blobs:
        end = data.index(b'\n', offset)
        header = data[offset:end].split()
        size = int(header[2])
        value = data[end + 1:end + 1 + size]
        assert len(value) == size
        scanner.scan(value, repo.name + ':history:' + paths[digest])
        offset = end + 2 + size
    return {'head': git(repo, 'rev-parse', 'HEAD').strip(), 'history_blobs': len(blobs)}


def retained_paths():
    selected = set()
    for name in ('rosa-research', 'rosa-evaluation'):
        repo = WORKSPACE / name
        untracked = git(repo, 'ls-files', '--others', '--exclude-standard').splitlines()
        modified = git(repo, 'diff', '--name-only', 'HEAD').splitlines()
        for relative in untracked + modified:
            path = repo / relative
            if path.is_file():
                selected.add(path)
    # Historical research documentation is intentionally ignored by the old repo.
    selected.update(p for p in (WORKSPACE / 'rosa-research/docs').rglob('*') if p.is_file())
    for folder in (WORKSPACE, WORKSPACE / 'reports'):
        selected.update(p for p in folder.iterdir() if p.is_file() and p.suffix in ('.md', '.py', '.ps1', '.sh', '.toml'))
    result = []
    for path in sorted(selected):
        relative = path.relative_to(WORKSPACE).as_posix()
        if path == ARCHIVE or path.is_relative_to(OUT):
            continue
        if (path.name.startswith('.env') or path.suffix in ('.dpapi', '.db', '.sqlite', '.sqlite3', '.pyc', '.tmp')
                or path.name.endswith('.lock') or '__pycache__' in path.parts):
            continue
        result.append((path, relative))
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not ARCHIVE.exists(), 'Never replace a backup archive'
    positive = Scanner()
    positive.scan(b'sk-' + b'controltest' * 4, 'synthetic_positive_control')
    assert any(f['kind'] == 'api_secret' for f in positive.findings)
    scanner = Scanner()
    revisions = {}
    for name in ('rosa-research', 'rosa-evaluation'):
        revisions[name] = history(WORKSPACE / name, scanner)
        print(json.dumps({'history_scanned': name, **revisions[name]}), flush=True)
    candidates = retained_paths()
    manifest = {}
    for path, relative in candidates:
        value = path.read_bytes()
        scanner.scan(value, relative)
        manifest[relative] = hashlib.sha256(value).hexdigest()
    result = {'status': 'FAIL' if scanner.findings else 'PASS', 'heads': revisions,
        'unique_contents_checked': scanner.values, 'archive_entries_checked': scanner.archive_entries,
        'expanded_archive_bytes': scanner.expanded_bytes, 'retained_files': len(manifest),
        'findings': scanner.findings, 'credentials_not_printed': True,
        'reviewed_noncredentials': scanner.reviewed_noncredentials,
        'scope': 'All reachable blobs on intended member/martin branches, recursive archive contents, '
                 'retained untracked/modified research evidence, ignored research docs and orchestration source.',
        'limitations': 'Pattern checks cannot prove absence of every possible secret. Ignored environments, '
                       'local service databases, protected credential storage and transient locks are excluded.'}
    (OUT / 'credential-scan.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'unique_contents_checked', 'archive_entries_checked', 'retained_files', 'findings')}), flush=True)
    if scanner.findings:
        raise RuntimeError('credential_findings_require_review_before_publication')
    manifest_value = {'date': '2026-10-27', 'kind': 'Retained working material backup, not accepted new experimental results',
        'files': manifest, 'committed_source_heads': revisions,
        'note': 'Committed source/history and previously committed evidence are protected by the branch pushes. '
                'This snapshot additionally preserves retained untracked evidence and modified working files '
                'without staging those original files. Sources retain their original provenance and limitations.'}
    with zipfile.ZipFile(ARCHIVE, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in candidates:
            value = path.read_bytes()
            assert hashlib.sha256(value).hexdigest() == manifest[relative], 'working_file_changed:' + relative
            archive.writestr(relative, value)
        archive.writestr('BACKUP_MANIFEST.json', json.dumps(manifest_value, indent=2))
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        for relative, digest in manifest.items():
            assert hashlib.sha256(archive.read(relative)).hexdigest() == digest
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    ARCHIVE.with_suffix('.sha256').write_text(digest + '  ' + ARCHIVE.name + '\n')
    verification = {'archive': ARCHIVE.name, 'sha256': digest, 'bytes': ARCHIVE.stat().st_size,
        'manifest_files_verified': len(manifest), 'zip_integrity': 'PASS', 'credential_scan': 'PASS',
        'off_machine_status': 'NOT_YET_UPLOADED'}
    ARCHIVE.with_suffix('.verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    (OUT / 'retained-backup-manifest.json').write_text(json.dumps(manifest_value, indent=2) + '\n')
    print(json.dumps(verification), flush=True)


if __name__ == '__main__':
    main()
