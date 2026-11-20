"""Lab-only, zero-inference completion of the combined preparation record."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import runpy
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT.parent.parents[3]
ORDER = ['ministral', 'granite', 'llama']
CONTAINER = 'marvel-g1-extension-20261119'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2) + '\n')


def get(path):
    with urllib.request.urlopen('http://127.0.0.1:11439' + path, timeout=10) as r:
        return json.load(r)


def main():
    assert sys.platform == 'linux' and str(ROOT).startswith('/media/naeem/d1/marvel proj/')
    assert not (ROOT / 'owner-launch-acknowledgment.json').exists()
    assert not (ROOT / 'BENCHMARK_RUN_ONCE').exists()
    assert not (ROOT / 'operator/live').exists()
    for slug in ORDER:
        b = ROOT / 'backends' / slug
        assert not (b / 'RUN_ONCE').exists() and not (b / 'owner-launch-acknowledgment.json').exists()
        assert not list((b / 'trials').glob('*/result.json'))
        assert read(b / 'AUXILIARY_REQUESTS.json')['charged_requests'] == 2
    source_checks = []
    for name in ['run_sequence.py', 'report_backend.py', 'observe_live.py', 'make_pooled_packet.py', 'complete_preflight.py']:
        p = ROOT / 'operator' / name
        ast.parse(p.read_text(), filename=str(p))
        source_checks.append({'file': str(p.relative_to(ROOT)), 'sha256': sha(p), 'syntax': 'PASS'})
    guards = []
    for flags, expected in [([], 'AssertionError'), (['--execute'], 'FileNotFoundError')]:
        p = subprocess.run([sys.executable, '-B', str(ROOT / 'operator/run_sequence.py')] + flags,
                           capture_output=True, text=True, timeout=15)
        assert p.returncode != 0 and expected in p.stderr
        guards.append({'flags': flags, 'exit_code': p.returncode, 'expected_failure': expected,
                       'stderr': p.stderr[-1800:]})
    assert not (ROOT / 'BENCHMARK_RUN_ONCE').exists()
    assert not (ROOT / 'operator/live').exists()
    write('OPERATOR_ZERO_INFERENCE_CHECKS.json', {
        'pass': True, 'executed_on': 'lab host', 'model_requests': 0,
        'sources': source_checks, 'missing_authorization_guards': guards,
        'backend_acknowledgments_created': 0, 'benchmark_attempts': 0,
        'charged_auxiliary_requests_unchanged': 6})

    assert get('/api/version')['version'] == '0.40.6'
    assert get('/api/ps')['models'] == []
    tags = {m['name']: m for m in get('/api/tags')['models']}
    samples = []
    for i in range(3):
        line = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                                       '--format=csv,noheader'], text=True).strip()
        samples.append({'utc': datetime.now(timezone.utc).isoformat(), 'raw': line,
                        'utilization_percent': int(line.split(',')[-1].strip().split()[0])})
        if i < 2:
            time.sleep(2)
    write('COMBINED_GPU_IDLE_GATE.json', {'samples': samples, 'limit_percent': 5,
                                         'pass': all(s['utilization_percent'] <= 5 for s in samples)})
    assert all(s['utilization_percent'] <= 5 for s in samples), 'GPU contention: no launch'
    assert subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', CONTAINER], text=True).strip() == 'sha256:306205ffce29f89a7e138f130cd3ee0bd668c17ed5441a45532449dbcbf771d2'
    with urllib.request.urlopen('http://127.0.0.1:6006/healthz', timeout=10) as r:
        assert r.status == 200
    assert subprocess.run(['systemd-inhibit', '--list'], capture_output=True).returncode == 0
    table = []
    for slug in ORDER:
        b = ROOT / 'backends' / slug
        config = read(b / 'MODEL_CONFIG.json')
        assert tags[config['tag']]['digest'] == config['digest']
        checks = read(b / 'operator/FINAL_ZERO_INFERENCE_CHECKS.json')
        assert checks['pass'] and checks['comparison_count'] == 48
        assert len(checks['timing_fields_preserved']) == 6
        rows = list(b.glob('zero-model-validation-attempt02/trials/*/result.json'))
        assert len(rows) == 8
        for p in rows:
            row = read(p)
            assert row['local_audit']['pass'] and row['phoenix_audit']['pass']
        e = read(b / 'ELIGIBILITY.json')
        assert e['eligibility'] == 'ELIGIBLE' and e['gpu_layers'] == e['total_layers']
        table.append({'slug': slug, 'config': config, 'eligibility': e, 'auxiliary_charged': 2,
                      'remaining_total_cap': 609, 'controls': 8, 'serialized_body_checks': 48})

    root_names = [p for p in ROOT.iterdir() if p.is_file() and p.suffix in ['.json', '.md', '.log']]
    root_names += list((ROOT / 'operator').glob('*.py'))
    root_names += list((ROOT / 'provenance').glob('*'))
    excluded = {'EXTENSION_INPUT_FREEZE.json', 'COMBINED_PROTECTED_HASH_CHECK.json', 'READY_PREFLIGHT.md',
                'STATUS.json', 'STATUS.md', 'EVIDENCE_EXPORT_MANIFEST.json', 'MASTER_UPDATE_RECEIPT.json'}
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in root_names if p.is_file() and p.name not in excluded}
    write('EXTENSION_INPUT_FREEZE.json', {
        'label': 'exploratory backend, added after Sol and Qwen results',
        'prepared_utc': datetime.now(timezone.utc).isoformat(), 'benchmark_requests': 0,
        'root_files_sha256': frozen,
        'backend_seals_sha256': {slug: sha(ROOT / 'backends' / slug / 'freeze.json') for slug in ORDER},
        'mutable_outputs_excluded': ['owner acknowledgments', 'live telemetry/status', 'trial results',
                                     'human ratings', 'reports', 'master progress record', 'Phoenix live DB']})
    module = runpy.run_path(str(ROOT / 'operator/run_sequence.py'))
    assert module['verify']()
    parent = read(ROOT.parent / 'stage-4/freeze.json')
    protected = read(ROOT / 'PROTECTED_BEFORE.json')['files_sha256']
    write('COMBINED_PROTECTED_HASH_CHECK.json', {
        'pass': True, 'original_frozen_inputs': len(parent['files_sha256']),
        'protected_sol_qwen_files': len(protected), 'backend_seals_verified': 3,
        'protected_source_edits': 0, 'benchmark_requests': 0,
        'extension_input_freeze_sha256': sha(ROOT / 'EXTENSION_INPUT_FREEZE.json')})
    status = {
        'status': 'READY_AWAITING_COMBINED_OWNER_ACKNOWLEDGMENT',
        'benchmark_attempts': 0, 'benchmark_requests': 0, 'charged_auxiliary_requests': 6,
        'T1': {'status': 'PASS', 'note': 'Factual addendum preserves adopted P3/P4 definitions; no false relabeling.'},
        'T2': {'status': 'PASS', 'note': 'Combined technical preflight complete; owner reading and acknowledgment pending.'},
        'T3': {'status': 'PASS', 'note': '24 scripted controls, 24 local and 24 persisted audits; 144 serialized body checks.'},
        'T4': {'status': 'BLOCKED', 'note': 'One explicit acknowledgment of READY_PREFLIGHT.md is required before launch.'},
        'T5': {'status': 'BLOCKED', 'note': 'No live new-model transcripts yet. Pooled kit generator prepared, no human scores generated.'},
        'T6': {'status': 'BLOCKED', 'note': 'Actual eligible reviewer ratings required before unchanged formal analysis.'},
        'reviewer': 'Levinson (nomination only; declaration and ratings not yet obtained)',
        'models': table}
    write('STATUS.json', status)
    (ROOT / 'STATUS.md').write_text('# G1 three-model extension — preparation status\n\nDate: 2026-11-19.\n\n'
        '**Exploratory backend, added after Sol and Qwen results.**\n\n'
        '**0/228 live benchmark attempts; 6 auxiliary load/unload requests charged.**\n\n'
        + '\n'.join('- **' + k + ': ' + status[k]['status'] + '** — ' + status[k]['note'] for k in ['T1','T2','T3','T4','T5','T6'])
        + '\n\nRead [READY_PREFLIGHT.md](READY_PREFLIGHT.md). Old protected records are unchanged; see COMBINED_PROTECTED_HASH_CHECK.json.\n'
        + '\nThe former Docker image disappeared externally. This assembly uses another installed Jazzy image, with matching pinned Python dependencies. No image/model download or protected source edit occurred. No new model tool-call compatibility result exists. Prior Granite/Llama failures remain documented.\n')
    print(json.dumps({'status': status['status'], 'freeze_sha256': sha(ROOT / 'EXTENSION_INPUT_FREEZE.json'),
                      'models': len(table), 'benchmark_requests': 0, 'auxiliary_charged': 6}))


if __name__ == '__main__':
    main()
