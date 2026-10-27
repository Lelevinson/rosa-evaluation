"""Read-only evidence aggregation; never rescore/replace a completed attempt."""
from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import sys

root = Path('/mnt/c/Proj/robotics/introtorobotics')
base = root / 'rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027'
load = lambda path: json.loads(path.read_text())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
summary = {'purpose': 'engineering demonstration, not comparative research', 'm3': {}, 'm2': []}
m2 = load(base / 'm2-01/result.json')
assert m2['pass'] and len(m2['rows']) == 10
for row in m2['rows']:
    summary['m2'].append({key: row[key] for key in ('case', 'pass', 'expected_status', 'dispatches')})
    summary['m2'][-1].update(native=len(row['snapshot']['operations']),
        local_audit=row['local_audit']['pass'], phoenix_audit=row['phoenix_audit']['pass'],
        spans=row['phoenix_audit']['persisted_spans'])
assert m2['inspection_has_no_publisher']
all_audits = list(summary['m2'])
for backend in ('deterministic', 'ollama', 'siwc'):
    folder = base / ('m3-' + backend)
    data = load(folder / 'checkpoint.json')
    assert data['status'] == 'COMPLETE' and len(data['trials']) == 3
    assert data['simulator_cleanup']['returncode'] == 0 and not data['cleanup_errors']
    rows = []
    freeze = load(folder / 'freeze.json')
    for name, expected in freeze['files'].items():
        assert digest(folder / 'source' / name) == expected
    for row in data['trials']:
        audit = load(folder / row['task'] / 'phoenix-audit.json')
        assert row['local_audit']['pass'] and audit['pass'] and audit['exact_span_ids'] and audit['closed_tree']
        spans = load(folder / row['task'] / 'trace.json')['spans']
        trace_root, = [s for s in spans if s['name'] == 'rosa.capability.demo']
        seconds = (datetime.fromisoformat(trace_root['end_time'].replace('Z', '+00:00')) -
            datetime.fromisoformat(trace_root['start_time'].replace('Z', '+00:00'))).total_seconds()
        inf = row['inference']
        assert inf['usage_complete'] and inf['calls'] <= 8
        assert inf.get('known_output_tokens', 0) <= 2048
        result = {'task': row['task'], 'pass': row['pass'], 'selected': row['selected_skill'],
            'calls': inf['calls'], 'input_tokens': inf.get('known_input_tokens', 0),
            'output_tokens': inf.get('known_output_tokens', 0), 'native': len(row['snapshot']['operations']),
            'dispatches': row['dispatches'], 'invalid_attempts': row['snapshot']['validation_errors'],
            'seconds_trace_root': round(seconds, 6), 'spans': audit['persisted_spans'],
            'local_audit': row['local_audit']['pass'], 'phoenix_audit': audit['pass'],
            'service_censored': row.get('service_censored', False)}
        rows.append(result)
    assert sum(r['calls'] for r in rows) == data['total_model_calls'] <= 24
    summary['m3'][backend] = {'correct': sum(r['pass'] for r in rows), 'rows': rows,
        'totals': {key: sum(r[key] for r in rows) for key in ('calls', 'input_tokens', 'output_tokens',
            'native', 'dispatches', 'invalid_attempts', 'seconds_trace_root', 'spans')},
        'frozen_files': len(freeze['files']), 'cleanup': data['simulator_cleanup']}
    all_audits.extend(rows)
summary['audit_totals'] = {'traces': len(all_audits), 'passing': sum(r['local_audit'] and r['phoenix_audit']
    for r in all_audits), 'exact_spans': sum(r['spans'] for r in all_audits)}
history = []
allowed_changes = {'rosa-research/src/rosa_auth/' + name for name in
    ('oauth.py', 'remembered.py', 'protected_store.py')}
for campaign, filename, key in [('macro-focus-v2-20261026', 'freeze.json', 'files'),
        ('macro-module-v1-20261027', 'source-manifest.json', 'source_files')]:
    original = base.parent / campaign
    source_map = load(original / filename)[key]
    changes = []
    for name, expected in source_map.items():
        assert digest(original / 'source' / name) == expected
        current = digest(root / name)
        if current != expected:
            assert name in allowed_changes, name
            changes.append({'file': name, 'archived_sha256': expected, 'current_sha256': current,
                'reason': 'post-M3 optional OAuth rotation storage/cleanup-notice hotfix'})
    history.append({'campaign': campaign, 'archived_sources_verified': len(source_map),
        'prospective_working_source_differences': changes})
summary['historical_sources'] = history
archive = base.parent / 'ROSA_MACRO_MODULE_V1_M1_ENGINEERING_2026-10-27.zip'
assert digest(archive) == archive.with_suffix('.sha256').read_text().split()[0]
summary['m1_archive_sha256'] = digest(archive)
summary['authorization_resume'] = load(base / 'auth-resume-check.json')
summary['tests'] = {}
for name in ('research-final-tests.log', 'evaluation-final-tests.log'):
    text = (base / name).read_text()
    match = re.search(r'Ran (\d+) tests? in', text)
    assert match and re.search(r'^OK', text, re.M)
    summary['tests'][name] = {'discovered': int(match[1]),
        'skipped': int(re.search(r'skipped=(\d+)', text)[1]) if 'skipped=' in text else 0}

# Add current sources and locks without rewriting any per-backend frozen sources.
source = base / 'final-source'
paths = list((root / 'rosa-research/src').rglob('*.py'))
paths += list((root / 'rosa-research/src/rosa_reliability/sim').glob('*'))
paths += list((root / 'rosa-evaluation/experiments/macro_capabilities_v2').glob('*.py'))
paths += [root / name for name in ('rosa-research/uv.lock', 'rosa-research/pyproject.toml',
    'rosa-evaluation/uv.lock', 'rosa-evaluation/pyproject.toml',
    'rosa-evaluation/tools/phoenix/uv.lock', 'rosa-evaluation/tools/phoenix/pyproject.toml',
    'rosa-research/tests/test_capabilities.py', 'rosa-research/tests/test_protected_rotation.py',
    'rosa-research/tests/test_auth_cleanup_notice.py', 'rosa-evaluation/tests/test_m2_m3_bounds.py',
    'rosa-research/docs/MACRO_CAPABILITIES_V2_SPEC.md', 'rosa-research/docs/MACRO_CAPABILITIES_V2_README.md',
    'rosa-research/docs/REMEMBERED_AUTH_ROTATION_VALIDATION_2026-10-27.md', 'rosa-research/MILESTONE_M2_M3.md',
    'rosa-evaluation/docs/M2_M3_CAPABILITIES_ENGINEERING_2026-10-27.md')]
paths += [root / 'reports' / name for name in ('m2m3-summarize.py', 'm2m3-final-checks.py',
    'm3-auth-resume-check.py', 'm3-auth-repair-check.py', 'm3-storage-diagnose.py',
    'm3-launch.ps1', 'm2m3-ollama.ps1', 'v2-command.sh', 'm1-command.sh')]
manifest = {}
for path in paths:
    if not path.is_file(): continue
    name = path.relative_to(root).as_posix()
    target = source / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    manifest[name] = digest(path)
(base / 'final-source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
packages = {}
for name in ('jpl-rosa', 'pydantic', 'langchain', 'langchain-core', 'langchain-ollama',
        'ollama', 'openinference-instrumentation-langchain', 'opentelemetry-sdk', 'PyJWT'):
    packages[name] = importlib.metadata.version(name)
(base / 'runtime-packages.json').write_text(json.dumps({'python': sys.version, 'packages': packages}, indent=2) + '\n')
(base / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
