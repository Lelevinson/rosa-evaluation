"""Update living context and build an additive, verified sharing package."""
import hashlib
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parents[3]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    evidence = BASE / 'evidence'
    data = json.loads((evidence / 'INDEPENDENT_REPEAT_ANALYSIS.json').read_text())
    report = evidence / 'QWEN_LAB_REPEAT_COMPARISON_REPORT.md'
    assert report.exists() and data['audits']['all_pass']
    master = EVAL / 'PROJECT_MASTER_README.md'
    original = master.read_bytes()
    (BASE / 'preparation/PROJECT_MASTER_README_before_repeat_closeout.md').write_bytes(original)
    text = original.decode('utf-8')
    start = text.index('**Current additional work - Qwen lab repeatability, 2026-11-17.**')
    end = text.index('**Latest completed execution', start)
    block = ('**Latest completed addition - Qwen lab repeatability, 2026-11-17.**\n'
        'The second lab Qwen batch completed **80/80 trials**, following **20/20 deterministic controls**. '
        'All **80/80 live local/Phoenix audits** and **74 source/config hashes** passed. '
        'The original 69 frozen files and earlier archives remain unchanged. '
        'Both lab runs use the identical installed Qwen3.5 9B Q4_K_M digest, 8K context, '
        '1,024 output tokens per call, 2,048 per task, temperature 0 and seed 42; thinking is off. '
        'The current primary lab Qwen configuration uses the RTX 4080 SUPER with 16 GB VRAM. '
        'Historical laptop M4 used different hardware and is preserved as its own study. '
        'There was no new Sol run and no substitution into the historical paired Sol comparison.\n\n'
        '| Qwen lab run | Known-goal correct P / M | Calls across all 40 attempts P / M | Mean task seconds P / M |\n'
        '|---|---:|---:|---:|\n')
    for name in ['lab_run_1', 'lab_run_2']:
        p, m = (data['summary'][name][c] for c in ['primitives', 'macro'])
        block += f'| {name} | {p["known_goal_correct"]}/36 / {m["known_goal_correct"]}/36 | {p["calls"]} / {m["calls"]} | {p["mean_seconds"]:.2f} / {m["mean_seconds"]:.2f} |\n'
    changes = sum(s['first_only_correct'] + s['repeat_only_correct'] for s in data['same_lab_paired_comparison'].values())
    block += (f'\nThere were **{changes} changed correctness outcomes among 72 identical known-goal cells** '
        'between lab runs. The report records directions and individual cells, not just aggregate scores. '
        'Each lab run has eight ambiguous attempts pending actual human semantic review; '
        'legacy regex scores are diagnostics. These are four repetitions of already-seen families, '
        'not new held-out tasks or independent generalization evidence. Costs include failures; '
        'matched-success views are reported separately. The latest study does not resolve G1 gates.\n\n'
        'Full current lab reference and comparison: '
        '[Qwen repeat report](artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_COMPARISON_REPORT.md), '
        '[independent analysis](artifacts/qwen-lab-repeat-20261117/evidence/INDEPENDENT_REPEAT_ANALYSIS.json). '
        'The original multi-model comparison below remains unchanged. '
        'The misplaced outside-d1 paths were already absent; no matching temporary residue remained '
        'in the checked outside locations. Models, useful configuration, identity files and runtime dependencies were preserved.\n\n')
    master.write_bytes((text[:start] + block + text[end:]).encode('utf-8'))
    (BASE / 'preparation/MASTER_REPEAT_CLOSEOUT.json').write_text(json.dumps({
        'before_sha256': sha(original), 'after_sha256': sha(master.read_bytes()),
        'date': '2026-11-17', 'earlier_study_sections_unchanged': True}, indent=2))
    delivery = BASE / 'delivery'
    delivery.mkdir(exist_ok=True)
    paths = {'reports/' + report.name: report,
        'context/PROJECT_MASTER_README.md': master,
        'data/QWEN_LAB_REPEAT_RAW_2026-11-17.zip': evidence / 'QWEN_LAB_REPEAT_RAW_2026-11-17.zip',
        'data/ROSA_LAB_MULTIMODEL_2026-11-17.zip': EVAL / 'artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip'}
    for name in ['INDEPENDENT_REPEAT_ANALYSIS.json', 'INDEPENDENT_REPEAT_VERIFICATION.json']:
        paths['analysis/' + name] = evidence / name
    for name in ['repeat_study.py', 'repeat_operator.py', 'PROTOCOL.md', 'analyze_repeat.py', 'write_report.py']:
        paths['reproduction/' + name] = BASE / 'preparation' / name
    manifest = {name: sha(path.read_bytes()) for name, path in paths.items()}
    target = delivery / 'QWEN_LAB_REPEAT_REPORT_AND_EVIDENCE_2026-11-17.zip'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as out:
        for name, path in paths.items():
            out.write(path, name)
        out.writestr('BUNDLE_MANIFEST.json', json.dumps({'files': manifest, 'date': '2026-11-17'}, indent=2))
    with zipfile.ZipFile(target) as check:
        assert check.testzip() is None
        for name, expected in manifest.items():
            assert sha(check.read(name)) == expected
    receipt = {'sha256': sha(target.read_bytes()), 'bytes': target.stat().st_size,
        'content_files': len(paths), 'all_hashes_match': True, 'zip_integrity_pass': True}
    (delivery / 'DELIVERY_VERIFICATION.json').write_text(json.dumps(receipt, indent=2))
    target.with_suffix('.sha256').write_text(receipt['sha256'] + '  ' + target.name + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
