"""Assemble and verify the M5 delivery without replacing historical archives."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from .backup import Scanner

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
OUT = ROOT / 'artifacts/macro-m5-20261027'
ARCHIVE = ROOT / 'artifacts/ROSA_M5_DELIVERY_2026-10-27.zip'


def git(repo, *args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo), *args])


def validate():
    freeze = json.loads((ROOT / 'artifacts/macro-m4-20261027/freeze.json').read_text())
    for name, digest in freeze['files'].items():
        assert hashlib.sha256((WORKSPACE / name).read_bytes()).hexdigest() == digest, name
    old = ROOT / 'artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.zip'
    assert hashlib.sha256(old.read_bytes()).hexdigest() == 'fb3a47aecfaaa380cb295ef5bfa8cca5d4511f2c842dc783144b5ba6a747b0ab'
    from pypdf import PdfReader
    assert len(PdfReader(OUT / 'ROSA_M5_RESEARCH_REPORT.pdf').pages) == 10
    assert len(PdfReader(OUT / 'ROSA_M5_CLAIM_LEDGER.pdf').pages) == 1
    assert json.loads((OUT / 'package/acceptance.json').read_text())['pass']
    video = json.loads((OUT / 'video-provenance.json').read_text())
    assert video['new_research_trials'] == 0 and video['new_demo_model_requests'] == 4
    for backend in ('siwc', 'ollama'):
        demo = json.loads((OUT / ('demo-' + backend) / 'result.json').read_text())
        assert demo['pass'] and demo['live_model_requests'] == 2 and demo['independent_goal_reached']
        assert demo['simulator_cleanup']['returncode'] == 0
    with zipfile.ZipFile(OUT / 'ROSA_M5_HUMAN_REVIEW_PACKET.zip') as packet:
        assert set(packet.namelist()) == {'INSTRUCTIONS.md', 'CASES.md', 'cases.json', 'ratings.csv'}
        assert len(json.loads(packet.read('cases.json'))) == 8
        assert b'siwc' not in packet.read('cases.json') and b'ollama' not in packet.read('cases.json')
    return {'m4_frozen_inputs_verified': len(freeze['files']), 'm4_final_archive_unchanged': True,
            'research_report_pages': 10, 'ledger_pages': 1, 'presentation_model_requests': 4,
            'new_research_trials': 0, 'both_presentation_goals_verified': True,
            'human_review': 'DEFERRED_BY_USER_PACKET_READY'}


def main():
    assert not ARCHIVE.exists(), 'Never replace a delivery archive'
    validation = validate()
    readme = '''# ROSA M5 delivery

Date: **2026-10-27**. This is a technical delivery, with independent human review
deferred at the user's request. Read the current status and off-machine verification
records for publication status; a local ZIP is not an off-machine backup.

Start with the ten-page research PDF or M5_RESEARCH_REPORT.md, then the one-page
claim ledger. PARTIAL_COMMAND_FORENSIC_REVIEW.md documents the four saved traces.
The video is50.4 seconds of genuine isolated Gazebo camera footage: both live
presentation runs reached the explicit goal in two calls each. Waiting is labeled8x,
motion1x. These four requests are not additional M4 research trials or a new speed
benchmark. Raw frames, results, source and editing provenance are retained.

The original frozen M4 final evidence ZIP is supplied separately inside the
evaluation/artifacts layout. Extract it into rosa-evaluation/artifacts before
running M5 postprocessing from that checkout. It creates macro-m4-20261027/;
never overwrite an existing populated campaign to rerun models. M5 analysis/report
commands use saved data only. See tools/m5/README.md for environment and commands.

The module wheel is under package/. Its offline empty-target acceptance uses the
existing research dependency/ROS stack, not a fresh OS. Runtime source and research/
Phoenix locks are included. The Windows reporting/video dependency versions and
source hashes are recorded; Arial/FFmpeg recording assumptions are explicit.
No new model training, architecture, stock-ROSA experiment or selection diagnostic
is part of this delivery.

For independent human scoring, share only ROSA_M5_HUMAN_REVIEW_PACKET.zip, not the
operator key or old scores. The packet withholds labels, but response style can
still reveal source. Preserve ratings and disagreements. No human ratings are
claimed in this package.

Full historical untracked/modified working material is protected separately by
ROSA_M5_RETAINED_WORK_BACKUP_2026-10-27.zip (4,423 files) and the dependency-lock
addendum (14 historical uv.lock copies). Those large historical backups are not
duplicated inside this focused bundle; their checksums/verification metadata are
included. They retain provenance and do not turn failed/partial studies into passes.

Original M4 and older archives remain unchanged. M5 reports/handoff snapshots are
derived delivery documents. Current canonical project context is PROJECT_MASTER_README.md;
outer archive checksums are generated after packaging and recorded in the sidecar.
Use DELIVERY_MANIFEST.json to verify this archive's entries. Hash checks establish
byte identity, not scientific validity or human adjudication.
'''
    (OUT / 'M5_DELIVERY_README.md').write_text(readme, encoding='utf-8')
    (OUT / 'delivery-validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    files = {}
    for path in OUT.rglob('*'):
        if path.is_file() and path.suffix not in ('.tmp', '.pyc') and '__pycache__' not in path.parts:
            files['rosa-evaluation/' + path.relative_to(ROOT).as_posix()] = path.read_bytes()
    # Include the focused original M4 archive, not all duplicate historical ZIPs.
    originals = ['artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.zip',
                 'artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.sha256',
                 'artifacts/ROSA_M4_FINAL_REVIEW_2026-10-27.verification.json']
    for stem in ('ROSA_M5_RETAINED_WORK_BACKUP_2026-10-27', 'ROSA_M5_RETAINED_LOCKFILES_ADDENDUM_2026-10-27'):
        originals += ['artifacts/' + stem + suffix for suffix in ('.sha256', '.verification.json')]
    for name in originals:
        files['rosa-evaluation/' + name] = (ROOT / name).read_bytes()
    # Committed non-artifact evaluation scaffolding plus the current M5 documents/tools.
    for relative in git(ROOT, 'ls-files').decode().splitlines():
        if relative.startswith('artifacts/'):
            continue
        path = ROOT / relative
        if path.is_file():
            files['rosa-evaluation/' + relative] = path.read_bytes() if relative in (
                'README.md', 'PROJECT_MASTER_README.md', 'PROJECT_LIVE_STATUS.json', 'tools/project_context.py') else git(ROOT, 'show', 'HEAD:' + relative)
    for path in (ROOT / 'tools/m5').rglob('*'):
        if path.is_file() and path.suffix != '.pyc' and '__pycache__' not in path.parts:
            files['rosa-evaluation/' + path.relative_to(ROOT).as_posix()] = path.read_bytes()
    source = WORKSPACE / 'rosa-research'
    for relative in git(source, 'ls-files').decode().splitlines():
        path = source / relative
        if path.is_file():
            files['rosa-research/' + relative] = git(source, 'show', 'HEAD:' + relative)
    frozen = json.loads((ROOT / 'artifacts/macro-m4-20261027/freeze.json').read_text())
    for name in frozen['files']:
        files[name] = (WORKSPACE / name).read_bytes()
    # Preserve the exact README used for the wheel metadata, without staging unrelated edits.
    files['rosa-research/README.md'] = (source / 'README.md').read_bytes()
    files['README.md'] = readme.encode()
    scanner = Scanner()
    for name, value in files.items():
        assert not any(part in ('.git', '.venv', '.local', '__pycache__') for part in Path(name).parts)
        assert not Path(name).name.startswith('.env') or Path(name).name == '.env.example'
        assert Path(name).suffix not in ('.dpapi', '.db', '.sqlite', '.sqlite3', '.pyc')
        scanner.scan(value, name)
    assert not scanner.findings, json.dumps(scanner.findings)
    manifest = {'kind': 'M5 technical delivery; human adjudication deferred; consult current publication status',
        'files': {name: hashlib.sha256(value).hexdigest() for name, value in sorted(files.items())},
        'validation': validation, 'credential_scan': 'PASS',
        'reviewed_noncredential_findings': scanner.reviewed_noncredentials,
        'note': 'The committed runtime is unchanged. Retained historical backups are separate and include unrelated working snapshots; no blanket validity claim follows from inclusion.'}
    with zipfile.ZipFile(ARCHIVE, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, value in sorted(files.items()):
            archive.writestr(name, value)
        archive.writestr('DELIVERY_MANIFEST.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    ARCHIVE.with_suffix('.sha256').write_text(digest + '  ' + ARCHIVE.name + '\n')
    verification = {'archive': ARCHIVE.name, 'sha256': digest, 'bytes': ARCHIVE.stat().st_size,
        'manifest_files_verified': len(files), 'zip_integrity': 'PASS', 'credential_scan': 'PASS',
        'm4_frozen_inputs_unchanged': 62, 'human_review': 'DEFERRED_BY_USER',
        'off_machine_status': json.loads((OUT / 'off-machine-verification.json').read_text())['status']}
    ARCHIVE.with_suffix('.verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    (OUT / 'delivery-verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':main()
