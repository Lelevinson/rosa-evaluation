"""Detached, bounded, zero-inference report/export continuation.

Never launches/resumes experiments. Stops if the authorized sequence stops.
All research/runtime/scoring sources and original evidence remain untouched.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import runpy
import shlex
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LAB = Path('/media/naeem/d1/marvel proj')
CONTAINER = 'marvel-g1-extension-20261119'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def status(phase, **extra):
    p = ROOT / 'operator/COMPLETION_WORKER_STATUS.json'
    temp = p.with_suffix('.tmp')
    temp.write_text(json.dumps({'phase': phase, 'utc': datetime.now(timezone.utc).isoformat(),
                                'model_requests': 0, **extra}, indent=2) + '\n')
    temp.replace(p)


def main():
    assert sys.platform == 'linux' and str(ROOT).startswith(str(LAB) + '/')
    marker = ROOT / 'operator/COMPLETION_WORKER_RUN_ONCE'
    assert not marker.exists()
    marker.write_text('Reporting/export only. No model requests or automatic trial recovery.\n')
    start = time.monotonic()
    status('WAITING_FOR_AUTHORIZED_SEQUENCE')
    while time.monotonic() - start < 26 * 3600:
        state = read(ROOT / 'SEQUENCE_STATUS.json')
        if state['status'] == 'STOPPED':
            status('STOPPED_SEQUENCE_REQUIRES_INSPECTION')
            return
        if (state['status'] == 'EXECUTION_COMPLETE_HUMAN_REVIEW_PENDING'
                and (ROOT / 'pooled-human-review/PACKET_RECEIPT.json').exists()):
            break
        time.sleep(20)
    else:
        status('WAIT_DEADLINE_EXPIRED_NO_ACTION')
        return
    assert (ROOT / 'pooled-human-review/PACKET_RECEIPT.json').exists(), 'packet_not_finished'
    status('COMPUTING_DESCRIPTIVE_REPORTS')
    internal = Path('/work') / (ROOT / 'operator/consolidate_descriptive.py').relative_to(LAB)
    cmd = 'source /opt/ros/jazzy/setup.bash && ' + shlex.join([
        '/work/runtime/envs/research/bin/python', '-B', str(internal)])
    subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-lc', cmd], check=True)
    data = read(ROOT / 'DESCRIPTIVE_EXTENSION_RESULTS.json')
    packet = ROOT / 'pooled-human-review/G1_EXTENSION_CLARIFICATION_REVIEW_2026-11-19.zip'
    receipt = read(ROOT / 'pooled-human-review/PACKET_RECEIPT.json')
    assert receipt['transcripts'] == 12 and receipt['ratings_generated'] == 0
    assert sha(packet) == receipt['sha256']
    with zipfile.ZipFile(packet) as z:
        assert z.testzip() is None
        assert not any('PRIVATE' in n or 'MAPPING' in n for n in z.namelist())
        import csv
        rows = list(csv.DictReader(z.read('ratings-empty.csv').decode().splitlines()))
        assert len(rows) == 12 and all(not value for row in rows for key, value in row.items() if key != 'case_id')
    progress = read(ROOT / 'STATUS.json')
    progress.update(status='EXECUTION_COMPLETE_REAL_HUMAN_REVIEW_PENDING',
                    benchmark_attempts=228, benchmark_requests=sum(m['inference_requests'] for m in data['models'].values()),
                    total_charged_requests=data['total_charged_requests'])
    progress['T4'] = {'status': 'PASS', 'note': 'All three 76-attempt batches retained; local/persisted audits and frozen hashes pass. Formal analysis is deferred under T6.'}
    progress['T5'] = {'status': 'PASS', 'note': 'Twelve-transcript pooled blinded packet prepared; blank ratings and unchanged rubric. Real reviewer response not yet obtained.'}
    progress['T6'] = {'status': 'BLOCKED', 'note': 'Actual eligibility declaration and semantic ratings required; frozen analysis and H-write closeout withheld.'}
    (ROOT / 'STATUS.json').write_text(json.dumps(progress, indent=2) + '\n')
    (ROOT / 'STATUS.md').write_text('# G1 three-model extension — execution complete\n\nDate: 2026-11-19. '
        '**Exploratory backends, added after Sol and Qwen results.**\n\n'
        '**228/228 attempts retained. No actual new human ratings obtained.**\n\n'
        + '\n'.join('- **' + k + ': ' + progress[k]['status'] + '** — ' + progress[k]['note'] for k in ['T1','T2','T3','T4','T5','T6'])
        + '\n\nSee MULTIMODEL_EXECUTION_REPORT.md and DESCRIPTIVE_EXTENSION_RESULTS.json. '
        'No frozen predictions, H-write verdicts or reviewer scores were invented.\n')
    time.sleep(15)
    assert runpy.run_path(str(ROOT / 'operator/run_sequence.py'))['verify']()
    status('REPORTS_COMPLETE_PACKAGING_SNAPSHOT')
    archive = ROOT.parents[5] / 'G1_MULTIMODEL_COMPLETED_20261119.zip'
    assert not archive.exists()
    patterns = [re.compile(x) for x in [rb'sk-(?:proj-)?[A-Za-z0-9_-]{20,}',
                rb'Bearer [A-Za-z0-9._-]{24,}', rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']]
    hashes = {}
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT)
            if '__pycache__' in rel.parts or p.suffix in ['.pyc', '.tmp'] or rel.parts[:3] == ('service','phoenix','data') or p.name == 'COMPLETED_EXPORT_MANIFEST.json':
                continue
            content = p.read_bytes()
            assert not any(pattern.search(content) for pattern in patterns), 'credential_pattern_file_hit:' + str(rel)
            hashes[rel.as_posix()] = hashlib.sha256(content).hexdigest()
            z.writestr(rel.as_posix(), content)
        manifest = {'label': data['label'], 'files_sha256': hashes,
                    'raw_result_sha256': data['raw_result_sha256'], 'attempts': 228,
                    'total_charged_requests': data['total_charged_requests'],
                    'excluded': ['active Phoenix DB/WAL; not a database backup', '__pycache__', 'temporary writes'],
                    'snapshot_limit': 'Per-file captured bytes; live service logs are not an atomic database snapshot.',
                    'credential_scan': 'High-confidence pattern scan passed; limited regex coverage.'}
        encoded = (json.dumps(manifest, indent=2) + '\n').encode()
        (ROOT / 'COMPLETED_EXPORT_MANIFEST.json').write_bytes(encoded)
        z.writestr('COMPLETED_EXPORT_MANIFEST.json', encoded)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, expected in hashes.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == expected
    assert all(sha(ROOT / name) == expected for name, expected in data['raw_result_sha256'].items())
    assert runpy.run_path(str(ROOT / 'operator/run_sequence.py'))['verify']()
    digest = sha(archive)
    export = {'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': digest,
              'sha256_parts': [digest[:32], digest[32:]], 'manifest_entries_verified': len(hashes),
              'retained_attempts': 228, 'model_requests_for_reporting': 0,
              'formal_analysis': 'WITHHELD_PENDING_REAL_HUMAN_REVIEW', 'review_transcripts': 12}
    archive.with_suffix('.receipt.json').write_text(json.dumps(export, indent=2) + '\n')
    status('COMPLETE_EVIDENCE_EXPORTED_REVIEW_PENDING', **export)
    print(json.dumps(export), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        status('STOPPED_POSTPROCESSING', error_type=type(error).__name__)
        raise
