"""Create a review ZIP without altering either sealed Stage 2 segment."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent
REV = ROOT.parent
NAME = 'ROSA_G1_STAGE2_RESULTS_2026-11-14'
ARCHIVE = ROOT / (NAME + '.zip')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf-8')

def main():
    assert not ARCHIVE.exists(), 'Never overwrite an evidence archive'
    segments = {'stage-2': 'stage2-manifest.json',
                'stage-2-continuation-1': 'continuation-manifest.json'}
    original_integrity = {}
    for directory, manifest_name in segments.items():
        folder = REV / directory
        manifest = load(folder / manifest_name)
        receipt = load(folder / 'manifest-verification.json')
        assert receipt['pass']
        assert sha((folder / manifest_name).read_bytes()) == receipt['manifest_sha256']
        for relative, expected in manifest['files'].items():
            assert sha((folder / relative).read_bytes()) == expected, 'Sealed evidence changed: ' + directory + '/' + relative
        assert load(folder / 'phoenix-service.json')['stopped']
        original_integrity[directory] = dict(verified_files=len(manifest['files']),
                                            manifest_sha256=receipt['manifest_sha256'])
    analysis = load(REV / 'stage-2-continuation-1/combined-analysis.json')
    assert analysis['attempt_schedule_complete'] and analysis['all_attempts'] == 36
    assert analysis['cumulative_requests'] == 94
    candidates = [p for directory in segments for p in sorted((REV / directory).rglob('*')) if p.is_file()]
    context_names = ['STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md', 'worlds.py', 'catalogue.py',
                     'catalogues.json', 'prompt-contract.json', 'PREDICTIONS_AND_THRESHOLDS.md',
                     'SCORING_CONTRACT.md', 'BUDGETS_AND_ESTIMATES.md', 'SKILL_DEPTH_TABLE.md']
    candidates += [REV / name for name in context_names]
    assert all(p.is_file() for p in candidates)
    # Local Phoenix databases are unnecessary for review: each trial has JSON traces,
    # persisted audit receipts and its result. Preserve databases locally, unchanged.
    omitted = []
    content = {}
    source_paths = {}
    blocked_suffixes = ('.db', '.db-shm', '.db-wal', '.sqlite', '.sqlite3', '.pyc', '.dpapi')
    for path in candidates:
        relative = path.relative_to(REV).as_posix()
        if path.name.endswith(blocked_suffixes) or '__pycache__' in path.parts or path.name.startswith('.env'):
            omitted.append(relative)
            continue
        name = 'revision-1/' + relative
        assert name not in content
        content[name] = path.read_bytes()
        source_paths[name] = path
    content['packaging/build_results_zip.py'] = Path(__file__).read_bytes()
    readme = '''# ROSA G1 Stage 2 results package

Date: 2026-11-14. Hosted Sol development validation only.

Start with [the combined results and problems report](revision-1/STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md).
The [combined execution report](revision-1/stage-2-continuation-1/COMBINED_STAGE2_REPORT.md) includes all 36 trial rows.
The [detailed checks](revision-1/stage-2-continuation-1/DETAILED_STAGE2_CHECKS.md) cover fault exercise, native ratios and both cost views.

There are 36 retained trial records: 35 correct completions and one original provider interruption.
All ten continuation trials completed correctly. The interrupted trial was not rerun or replaced.
All 36 local and persisted audits passed, matching 1,472 spans; total inference attempts were 94/291.
This is AI-authored exploratory dev, without independent case authorship or semantic human review.
P1-P4 are not adjudicated. This package establishes no Qwen, held-out or stock-ROSA comparison.

## Included

- Both Stage 2 segments: results, transcripts in result records, JSON traces, per-trial Phoenix audit records/logs,
  aggregate analyses, interruption records, frozen execution/scoring helpers, plans, settings and integrity receipts.
- The combined report and selected shared protocol/catalogue/world definitions.
- A package-specific SHA-256 manifest, omission list and packaging script.

## Deliberate omissions and interpretation

The six local Phoenix database/sidecar files are preserved locally and omitted here. Review uses the retained
per-trial trace JSON and persisted audit records. No credential store, OAuth token cache, .env file, Git history,
held-out case collection or full earlier-stage archive is included. Authorization-status JSON contains sanitized
scope/cleanup metadata, not token credentials. Files retain original machine paths and historical status wording.

Original manifests are historical inventories of their complete local segments; they list the omitted database
files as well. Use PACKAGE_MANIFEST.json to verify this ZIP's contents. Selected protocol references do not make
this a turnkey reinstall or a complete source/dependency backup. Stages 0 and 1 are not combined into this report.

All retained source bytes are copied unchanged. The only new material is this package's README, manifest and builder.
No experiment, inference request, Git commit, upload or publication was performed to create this package.
'''
    content['README.md'] = readme.encode('utf-8')
    patterns = {
        'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
        'api_key': re.compile(rb'\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{24,}'),
        'jwt': re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),
        'bearer_credential': re.compile(rb'Bearer\s+[A-Za-z0-9._~+/-]{20,}', re.I),
        'token_value': re.compile(rb'["\x27](?:access_token|refresh_token|id_token|client_secret)["\x27]\s*:\s*["\x27](?!REDACTED|UNKNOWN|CLEARED|\[)[^"\x27\r\n]{16,}["\x27]', re.I),
    }
    for name, data in content.items():
        for label, pattern in patterns.items():
            if pattern.search(data):
                raise RuntimeError('Potential credential pattern; no content printed: ' + label + ' in ' + name)
    trial_results = [name for name in content if '/trials/' in name and name.endswith('/result.json')]
    assert len(trial_results) == 36
    assert len({json.loads(content[name])['id'] for name in trial_results}) == 36
    manifest = dict(kind='Stage 2 review package; original segments preserved', date='2026-11-14',
                    files={name: sha(data) for name, data in sorted(content.items())},
                    omitted_files=omitted, original_integrity=original_integrity,
                    retained_trial_results=36, correct_completions=35, original_interruption_retained=True,
                    credential_pattern_scan='PASS', scan_caveat='Pattern and path checks are not proof of absence of all possible secrets.')
    content['PACKAGE_MANIFEST.json'] = encoded(manifest)
    # Exclusive create: a completed archive is never overwritten.
    with zipfile.ZipFile(ARCHIVE, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, data in sorted(content.items()):
            output.writestr(NAME + '/' + name, data)
    with zipfile.ZipFile(ARCHIVE) as packaged:
        assert packaged.testzip() is None
        assert set(packaged.namelist()) == {NAME + '/' + name for name in content}
        for name, expected in manifest['files'].items():
            assert sha(packaged.read(NAME + '/' + name)) == expected
        assert packaged.read(NAME + '/PACKAGE_MANIFEST.json') == content['PACKAGE_MANIFEST.json']
    for name, path in source_paths.items():
        assert sha(path.read_bytes()) == manifest['files'][name], 'Original changed during packaging'
    checksum = sha(ARCHIVE.read_bytes())
    ARCHIVE.with_suffix('.sha256').write_text(checksum + '  ' + ARCHIVE.name + '\n', encoding='utf-8')
    receipt = dict(archive=ARCHIVE.name, sha256=checksum, bytes=ARCHIVE.stat().st_size,
                   zip_entries=len(content), content_hashes_verified=len(manifest['files']),
                   retained_trial_results=36, zip_integrity='PASS', credential_pattern_scan='PASS',
                   original_segments_verified=original_integrity, original_bytes_unchanged=True,
                   omitted_files=omitted, new_model_requests=0, uploaded=False)
    ARCHIVE.with_suffix('.verification.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
