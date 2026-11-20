"""Seal local evidence and check report links; never launch inference."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
EXCLUDED = {'evidence-manifest.json', 'evidence-manifest-validation.json'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    docs = [REPO / 'docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md',
            REPO / 'docs/CLAUDE_QWEN_ROADMAP_LIVE.md', REPO / 'PROJECT_MASTER_README.md',
            ROOT / 'COMPLETED_REPORT.md']
    missing = []
    checked = 0
    # The project master contains historical links; check new reports and tracker.
    for doc in (docs[0], docs[1], docs[3]):
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            target = target.split('#', 1)[0].strip('<>')
            if not target or '://' in target:
                continue
            checked += 1
            if not (doc.parent / target).exists():
                missing.append({'document': str(doc.relative_to(REPO)), 'target': target})
    assert not missing, missing
    assert json.loads((ROOT / 'status.json').read_text())['status'] == 'COMPLETE'
    files = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(ROOT.rglob('*'))
             if p.is_file() and p.name not in EXCLUDED and '__pycache__' not in p.parts}
    linked = {p.relative_to(REPO).as_posix(): digest(p) for p in docs if not p.is_relative_to(ROOT)}
    manifest = {'date': '2026-11-13', 'scope': 'Local serving evidence and linked current reports; no off-machine backup',
                'files': files, 'linked_report_files_relative_to_repo': linked}
    (ROOT / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    mismatches = [name for name, value in files.items() if digest(ROOT / name) != value]
    mismatches += [name for name, value in linked.items() if digest(REPO / name) != value]
    result = {'pass': not mismatches, 'artifact_files': len(files), 'linked_reports': len(linked),
              'report_links_checked': checked, 'missing_links': missing, 'hash_mismatches': mismatches,
              'manifest_sha256': digest(ROOT / 'evidence-manifest.json')}
    (ROOT / 'evidence-manifest-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    assert result['pass'], result
    print(json.dumps(result))


if __name__ == '__main__':
    main()
