"""Curate historical context, verify artifacts and build the final handoff ZIP."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

from ..config import ROOT, checkout
from .runner import CAMPAIGN
from .protocol import verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    verify()
    summary = json.loads((CAMPAIGN / 'analysis.json').read_text())
    if not summary['stage4_complete']:
        raise RuntimeError('stage4_not_complete')
    if not (CAMPAIGN / 'power-release.json').exists():
        raise RuntimeError('resource_monitor_has_not_released')
    history = ROOT / 'artifacts/historical-stage4-context'
    history.mkdir(exist_ok=True)
    jtvr_archive = ROOT / 'artifacts/stage4-policy-20261021-evidence.zip'
    if sha(jtvr_archive) != '1bd949a82d9060eab97268a06597b5913ea508f823c51fe478380b7789b61ba5':
        raise RuntimeError('original_jtvr_archive_changed')
    baseline = ROOT.parent / 'reports/ROSA_STAGE1_TO_4_CLEAN_RERUN_2026-10-21.zip'
    if sha(baseline) != '721d5960d82f49ea4b0c6f6470ad2c2b02e4e4379720f4b6936a67f13cd3fcad':
        raise RuntimeError('baseline_v1_hash_changed')
    copied = history / baseline.name
    if copied.exists() and sha(copied) != sha(baseline):
        raise RuntimeError('historical_archive_conflict')
    if not copied.exists():
        shutil.copy2(baseline, copied)
    shutil.copy2(ROOT.parent / 'reports/clean-stage1-4-20261021-r1/REVIEW_REPORT.md', history / 'BASELINE_V1_REVIEW_REPORT.md')
    # Archive the superseded preflight plus its final scripted batch and trials.
    old_archive = history / 'PHASE4_V2_PREFLIGHT_PRESERVED.zip'
    if not old_archive.exists():
        prior = ROOT.parent / 'reports/phase4-v2'
        pointer = json.loads((prior / 'scripted-batch.json').read_text())
        from ..config import run_dir
        batch_folder = run_dir(pointer['batch_id'])
        batch = json.loads((batch_folder / 'result.json').read_text())
        with zipfile.ZipFile(old_archive, 'x', zipfile.ZIP_DEFLATED) as output:
            for path in sorted(prior.rglob('*')):
                if path.is_file():
                    output.write(path, path.relative_to(ROOT.parent))
            folders = [batch_folder] + [run_dir(row['run_id']) for row in batch['trials']]
            for folder in folders:
                for path in sorted(folder.rglob('*')):
                    if path.is_file():
                        output.write(path, path.relative_to(ROOT.parent))
    preservation = {'baseline_v1_archive_sha256': sha(copied),
        'original_jtvr_evidence_zip_sha256': sha(ROOT / 'artifacts/stage4-policy-20261021-evidence.zip'),
        'v2_preserved_archive_sha256': sha(old_archive), 'live_freeze_verified': True,
        'research_base_commit': subprocess.check_output(['git', '-c', 'safe.directory=' + str(checkout('research')),
            '-C', str(checkout('research')), 'rev-parse', 'HEAD'], text=True).strip(),
        'evaluation_base_commit_before_publication': subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT),
            '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()}
    (CAMPAIGN / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')
    shutil.copy2(Path(__file__), CAMPAIGN / 'analysis-source/package_results.py')
    archive = ROOT / 'artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip'
    if archive.exists():
        raise RuntimeError('final_archive_exists_no_overwrite')
    sources = [p for folder in (CAMPAIGN, ROOT / 'artifacts/stage4-policy-20261021', history)
               for p in folder.rglob('*') if p.is_file() and p.name != 'evidence-manifest.json']
    sources += [p for p in (ROOT / 'docs').rglob('*') if p.is_file()]
    sources += [ROOT / 'artifacts/stage4-policy-20261021-evidence.zip',
                ROOT / 'artifacts/stage4-policy-20261021-evidence.sha256']
    sources = sorted(set(sources))
    forbidden = [str(p) for p in sources if p.name.startswith('.env') or p.suffix in ('.db', '.sqlite', '.sqlite3')
                 or p.name == 'registration.json' or '.git' in p.parts or '.venv' in p.parts]
    if forbidden:
        raise RuntimeError('forbidden_artifact_paths:' + repr(forbidden))
    manifest = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    (CAMPAIGN / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for path in sources + [CAMPAIGN / 'evidence-manifest.json']:
            output.write(path, path.relative_to(ROOT))
    with zipfile.ZipFile(archive) as output:
        bad = output.testzip()
        if bad:
            raise RuntimeError('zip_crc_failed:' + bad)
        for name, wanted in manifest.items():
            if hashlib.sha256(output.read(name)).hexdigest() != wanted:
                raise RuntimeError('zip_member_hash_failed:' + name)
    archive.with_suffix('.sha256').write_text(sha(archive) + '  ' + archive.name + '\n')
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'sha256': sha(archive), 'verified_members': len(manifest)}))


if __name__ == '__main__':
    main()
