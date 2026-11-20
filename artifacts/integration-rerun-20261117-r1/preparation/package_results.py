"""Create and independently hash-check the explicit local share-package allowlist."""
import hashlib
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parents[3]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    delivery = BASE / 'delivery'
    delivery.mkdir(exist_ok=True)
    paths = {
        'START_HERE.md': BASE / 'evidence/START_HERE.md',
        'INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md': BASE / 'evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md',
        'INDEPENDENT_RERUN_ANALYSIS.json': BASE / 'evidence/INDEPENDENT_RERUN_ANALYSIS.json',
        'REMOTE_RAW_VERIFICATION.json': BASE / 'evidence/REMOTE_RAW_VERIFICATION.json',
        'NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip': BASE / 'evidence/NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip',
        'INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip': BASE / 'evidence/INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip',
        'ORIGINAL_LAB_STUDY_AND_SOURCE_2026-11-17.zip': EVAL / 'artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip',
        'INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip': EVAL / 'artifacts/lab-integration-20261117/evidence/INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip',
        'INTEGRATION_FINDINGS_2026-11-17.md': EVAL / 'artifacts/lab-integration-20261117/evidence/INTEGRATION_FINDINGS_2026-11-17.md',
        'QWEN_LAB_REPEAT_RAW_2026-11-17.zip': EVAL / 'artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_RAW_2026-11-17.zip',
        'QWEN_LAB_REPEAT_COMPARISON_REPORT.md': EVAL / 'artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_COMPARISON_REPORT.md',
        'PROJECT_MASTER_CONTEXT_2026-11-17.md': EVAL / 'PROJECT_MASTER_README.md',
        'analysis/analyze_rerun.py': BASE / 'preparation/analyze_rerun.py',
        'analysis/write_report.py': BASE / 'preparation/write_report.py',
        'analysis/package_results.py': Path(__file__),
        'analysis/shared_repeat_analysis.py': EVAL / 'artifacts/qwen-lab-repeat-20261117/preparation/analyze_repeat.py',
        'module/tool_contract_ollama.py': EVAL.parent / 'rosa-research/src/rosa_backends/tool_contract_ollama.py',
    }
    assert all(p.is_file() for p in paths.values())
    data = {name: p.read_bytes() for name, p in paths.items()}
    manifest = {name: sha(b) for name, b in data.items()}
    target = delivery / 'ROSA_NATIVE_SCHEMA_RERUN_REPORT_AND_EVIDENCE_2026-11-17.zip'
    assert not target.exists(), 'Do not overwrite an earlier published package'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, b in data.items():
            z.writestr(name, b)
        z.writestr('ARCHIVE_MANIFEST.json', json.dumps({'date': '2026-11-17', 'files': manifest}, indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name, digest in manifest.items():
            assert sha(z.read(name)) == digest
    record = {'date': '2026-11-17', 'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes()),
        'content_files': len(manifest), 'all_hashes_pass': True,
        'public_upload': False, 'credentials_or_weights_intentionally_included': False}
    (delivery / 'DELIVERY_VERIFICATION.json').write_text(json.dumps(record, indent=2) + '\n')
    (delivery / (target.stem + '.sha256')).write_text(record['sha256'] + '  ' + target.name + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
