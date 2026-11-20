"""Capture M1 engineering evidence without altering any prior campaign."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
DESTINATION = ROOT / 'artifacts/macro-module-v1-20261027'


def main():
    from experiments.macro_focus_v2.runner import verify_freeze
    verify_freeze()
    checks = json.loads((DESTINATION / 'final-checks.json').read_text())
    scripted = json.loads((DESTINATION / 'scripted-03/result.json').read_text())
    gazebo = json.loads((DESTINATION / 'gazebo-01/result.json').read_text())
    package_path = sorted(DESTINATION.glob('package-*/result.json'))[-1]
    package = json.loads(package_path.read_text())
    if not all(r['pass'] for r in (checks, scripted, gazebo, package)):
        raise RuntimeError('m1_acceptance_gate_failed')
    if not (len(scripted['rows']) == 12 and len(gazebo['rows']) == 7 and
            gazebo['simulator_cleanup']['returncode'] == 0):
        raise RuntimeError('m1_coverage_or_cleanup_incomplete')
    sources = set()
    research = WORKSPACE / 'rosa-research'
    for base in (research / 'src', research / 'tests', ROOT / 'experiments/macro_module_v1'):
        sources.update(base.rglob('*.py'))
    for base in (research / 'docs',):
        sources.update(base.glob('MACRO_MODULE_V1*.md'))
        sources.update(base.glob('REMEMBERED_CHATGPT_AUTH.md'))
    sources.update(research / name for name in ('pyproject.toml', 'uv.lock', 'README.md'))
    sources.update((ROOT / 'docs').glob('MACRO_MODULE_V1*.md'))
    sources.update((WORKSPACE / 'reports').glob('m1-*'))
    digests = {}
    for path in sorted(p for p in sources if p.is_file()):
        name = path.relative_to(WORKSPACE).as_posix()
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    revisions = {}
    for name in ('rosa-research', 'rosa-evaluation'):
        folder = WORKSPACE / name
        base = ['git', '-c', 'safe.directory=' + str(folder), '-C', str(folder)]
        revisions[name] = {'head': subprocess.check_output(base + ['rev-parse', 'HEAD'], text=True).strip(),
            'branch': subprocess.check_output(base + ['branch', '--show-current'], text=True).strip(),
            'working_tree_has_uncommitted_changes': True}
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'module_version': '0.1.0',
        'live_model_requests': 0, 'historical_frozen_verification': 'PASS',
        'source_files': digests, 'git': revisions,
        'limitations': ['No new live Qwen/Sol study', 'No real remembered-provider login/resume',
            'No genuinely different second capability', 'Wheel probe reuses pinned dependencies',
            'No collision/path-safety or physical robot claim']}
    (DESTINATION / 'source-manifest.json').write_text(json.dumps(manifest, indent=2))
    processes = subprocess.check_output(['ps', '-eo', 'pid,comm,args'], text=True).splitlines()
    remaining = [line for line in processes if any(term in line for term in
        ('ur_sim_control.launch.py', 'gz sim', 'experiments.macro_module_v1.validate'))]
    (DESTINATION / 'environment-after.json').write_text(json.dumps({
        'remaining_simulator_or_validation_processes': remaining, 'live_model_requests': 0}, indent=2))
    if remaining: raise RuntimeError('unexpected_simulator_or_validation_process_still_running')
    # A source-agnostic archive manifest covers every included file, including the
    # original failed attempts. Exclude this manifest's own circular digest.
    files = sorted(p for p in DESTINATION.rglob('*') if p.is_file() and p.name != 'archive-manifest.json')
    archive_manifest = {p.relative_to(DESTINATION).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (DESTINATION / 'archive-manifest.json').write_text(json.dumps(archive_manifest, indent=2))
    archive = ROOT / 'artifacts/ROSA_MACRO_MODULE_V1_M1_ENGINEERING_2026-10-27.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(p for p in DESTINATION.rglob('*') if p.is_file()):
            bundle.write(path, path.relative_to(DESTINATION).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None: raise RuntimeError('archive_crc_failed')
        for name, expected in archive_manifest.items():
            if hashlib.sha256(bundle.read(name)).hexdigest() != expected:
                raise RuntimeError('archive_file_digest_mismatch:' + name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(json.dumps({'pass': True, 'source_files': len(digests), 'verified_archive_files': len(archive_manifest),
        'archive': str(archive), 'sha256': digest, 'live_model_requests': 0}))


if __name__ == '__main__': main()
