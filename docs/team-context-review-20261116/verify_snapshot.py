"""Offline verification of downloaded bytes and published table arithmetic only."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'snapshot'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    download = json.loads((ROOT / 'downloaded-snapshot.json').read_text(encoding='utf-8'))
    for file in download['files']:
        raw = (SNAP / file['path']).read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == file['sha'], file['path']
    manifest = json.loads((SNAP / '.context-sync/manifest.json').read_text())
    assert set(manifest['include']) == {item['path'] for item in manifest['files']}
    for file in manifest['files']:
        assert hashlib.sha256((SNAP / file['path']).read_bytes()).hexdigest() == file['published_sha256'], file['path']
    models = ['lfm3:1.7b', 'qwen3.5:9b', 'gpt-oss:20b', 'bonsai-2:4b']
    rows = []
    for line in (SNAP / 'research/studies/forge_baseline_20261115/SAME_CELL_COMPARISON.md').read_text().splitlines():
        cells = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(cells) != 5 or cells[0] not in models:
            continue
        values = [tuple(int(value.strip()) for value in cell.split('/')) for cell in cells[2:]]
        rows.append(dict(model=cells[0], cell=cells[1], values=values))
    assert len(rows) == len({(row['model'], row['cell']) for row in rows}) == 80
    totals = {arm: dict(cells=80, supported=sum(row['values'][i][0] for row in rows),
                       requests=sum(row['values'][i][1] for row in rows))
              for i, arm in enumerate(['A1', 'C1', 'Forge'])}
    assert [(value['supported'], value['requests']) for value in totals.values()] == [(47, 472), (70, 486), (55, 643)]
    build = collections.defaultdict(lambda: dict(episodes=0, supported=0, requests=0, tokens=0))
    for line in (SNAP / 'research/studies/build_round1_20261115/REPORT.md').read_text().splitlines():
        cells = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(cells) != 7 or cells[0] not in models:
            continue
        for key, value in zip(['episodes', 'supported', 'requests', 'tokens'], cells[2:6]):
            build[cells[1]][key] += int(value)
    assert len(build) == 4 and sum(value['episodes'] for value in build.values()) == 320
    assert [(value['supported'], value['requests'], value['tokens']) for value in build.values()] == [
        (67, 506, 1995814), (70, 541, 2791741), (67, 435, 1524630), (69, 468, 1630657)]
    syntax = ast.parse((SNAP / 'tests/test_context_sync.py').read_text())
    tests = [node.name for node in ast.walk(syntax) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    assert len(tests) == 10
    code = (SNAP / 'scripts/context_sync.py').read_text().splitlines()
    patterns = {
        'source_final_symlink_check': 'source_path.is_symlink()',
        'target_final_symlink_check': 'destination.is_symlink()',
        'manifest_final_symlink_check': 'manifest_path.is_symlink()',
        'atomic_replace': 'os.replace(temporary_path, destination)',
        'path_resolve': '.resolve(',
        'containment_check': '.is_relative_to(',
    }
    locations = {key: [i for i, line in enumerate(code, 1) if pattern in line] for key, pattern in patterns.items()}
    result = dict(
        date='2026-11-16', passed=True,
        scope='Published table arithmetic, byte integrity and static source inspection; not raw-trace reproduction or test execution',
        unique_git_blobs_verified=len(download['files']),
        manifest_context_files_verified=len(manifest['files']),
        source_git_states=dict(collections.Counter(file['source_git_state'] for file in manifest['files'])),
        files_present_in_source_commit=sum(file['source_commit_contains_bytes'] for file in manifest['files']),
        forge_table_rows_recounted=len(rows), forge_table_totals=totals,
        build_table_totals=dict(build), defined_unit_tests=tests,
        static_code_line_locations=locations, runtime_unit_tests_executed=False,
        studies_reproduced=False, experimental_backend_requests=0,
        sync_executed=False, remote_writes=False,
        analyst_note='The initial one-off arithmetic check used an eight-column build-table assumption and stopped before writing a receipt. The actual table has seven columns. Corrected parsing reproduces every published total; source tables were not edited.')
    (ROOT / 'READ_ONLY_CHECKS.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ['defined_unit_tests', 'static_code_line_locations']}, indent=2))


if __name__ == '__main__':
    main()
