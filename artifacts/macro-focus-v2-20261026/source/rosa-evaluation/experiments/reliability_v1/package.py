"""Seal the completed new campaign without modifying earlier evidence."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
from .runner import DESTINATION, ROOT, verify_freeze


def main():
    verify_freeze()
    pipeline = json.loads((DESTINATION / 'pipeline-completion.json').read_text())
    if any(pipeline[key] != 0 for key in ('hosted_exit', 'local_exit', 'phoenix_audit_exit')):
        raise RuntimeError('pipeline_not_accepted_for_completed_package')
    audit = json.loads((DESTINATION / 'phoenix-audit.json').read_text())
    if not audit['pass'] or len(audit['traces']) != 72:
        raise RuntimeError('72_persisted_trace_audits_required')
    analysis = json.loads((DESTINATION / 'analysis.json').read_text())
    if analysis['independent_replay_failures']:
        raise RuntimeError('independent_replay_failed')
    for result in analysis['backends'].values():
        if result['status'] != 'COMPLETE' or result['completed_trials'] != 36:
            raise RuntimeError('backend_incomplete')
    reference = json.loads((DESTINATION / 'deterministic-reference/result.json').read_text())
    if len(reference['rows']) != 2 or not all(r['pass'] for r in reference['rows']):
        raise RuntimeError('matched_deterministic_reference_failed')
    demos = sorted((ROOT / 'artifacts/reliability-demos').glob('*/result.json'))
    demo = json.loads(demos[-1].read_text()) if demos else {}
    if demo.get('backend') != 'deterministic' or not demo.get('goal_attained'):
        raise RuntimeError('user_demo_not_validated')
    shutil.copytree(demos[-1].parent, DESTINATION / 'user-demo-check', dirs_exist_ok=True)
    previous = ROOT / 'artifacts/stage4-batching-completion-20261021/evidence-manifest.json'
    manifest = json.loads(previous.read_text())
    if any(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != value for name, value in manifest.items()):
        raise RuntimeError('historical_stage4_member_changed')
    old_zip = ROOT / 'artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip'
    old_hash = hashlib.sha256(old_zip.read_bytes()).hexdigest()
    if old_hash != '44bae743969d473359e5e6dcead7c89226851286a45c2d439ddf8a091a63b76c':
        raise RuntimeError('historical_stage4_archive_changed')
    writeup = {'previous_stage4_files_verified': len(manifest), 'previous_archive_sha256': old_hash,
               'new_persisted_trace_audits': len(audit['traces']), 'source_freeze_verified': True}
    (DESTINATION / 'preservation-check.json').write_text(json.dumps(writeup, indent=2))
    paths = list((ROOT / 'experiments/reliability_v1').glob('*.py')) + [
        ROOT / 'scripts/reliable-gazebo.sh', ROOT / 'scripts/reliable-gazebo.ps1', ROOT / 'docs/POST_STAGE4_ENGINEERING_MILESTONE_2026-10-22.md',
        ROOT.parent / 'rosa-research/PROJECT_VISION.md', ROOT.parent / 'rosa-research/src/rosa_reliability/README.md']
    paths += list((ROOT.parent / 'reports').glob('*reliability*.py'))
    paths += list((ROOT.parent / 'reports').glob('*reliability*.sh'))
    for file in paths:
        copy = DESTINATION / 'postrun-source' / file.relative_to(ROOT.parent)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, copy)
    # Include prerequisite development records without changing their originals.
    shutil.copytree(ROOT / 'artifacts/reliability-v1-development', DESTINATION / 'development', dirs_exist_ok=True)
    archive = ROOT / 'artifacts/reliability-v1-20261022-evidence.zip'
    if archive.exists():
        raise RuntimeError('sealed_archive_exists_do_not_overwrite')
    hashes = {str(file.relative_to(ROOT)): hashlib.sha256(file.read_bytes()).hexdigest()
              for file in sorted(DESTINATION.rglob('*')) if file.is_file() and file.name != 'evidence-manifest.json'}
    (DESTINATION / 'evidence-manifest.json').write_text(json.dumps(hashes, indent=2))
    patterns = [re.compile(p) for p in (
        rb'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
        rb'sk-[A-Za-z0-9_-]{24,}', rb'gh[pousr]_[A-Za-z0-9_]{30,}',
        rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', rb'Bearer [A-Za-z0-9_.-]{24,}')]
    findings = []
    for name in hashes:
        file = ROOT / name
        if file.name in ('registration.json', 'config.local.toml', '.env') or file.suffix in ('.db', '.sqlite', '.sqlite3'):
            findings.append(name)
        if any(pattern.search(file.read_bytes()) for pattern in patterns):
            findings.append(name)
    if findings:
        raise RuntimeError('credential_scan_findings: ' + repr(findings))
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for file in sorted(DESTINATION.rglob('*')):
            if file.is_file():
                output.write(file, str(file.relative_to(ROOT)))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256').write_text(digest + '  ' + archive.name + '\n')
    with zipfile.ZipFile(archive) as saved:
        assert saved.testzip() is None
        assert all(hashlib.sha256(saved.read(name)).hexdigest() == value for name, value in hashes.items())
    print(json.dumps({'archive': str(archive), 'sha256': digest, 'bytes': archive.stat().st_size,
                      'manifest_members': len(hashes), 'previous_stage4_members_verified': len(manifest)}))


if __name__ == '__main__':
    main()
