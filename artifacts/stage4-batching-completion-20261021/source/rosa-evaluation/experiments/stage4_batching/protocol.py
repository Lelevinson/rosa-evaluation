"""Immutable live protocol/source snapshot, including the sibling dependency."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess

from ..config import ROOT, checkout
from .runner import CAMPAIGN
from .tasks import reliability_jobs, batching_jobs


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    frozen = json.loads((CAMPAIGN / 'freeze.json').read_text())
    for name, wanted in frozen['source_sha256'].items():
        if sha(ROOT.parent / name) != wanted:
            raise RuntimeError('frozen_live_source_changed:' + name)
    if sha(CAMPAIGN / 'jobs.json') != frozen['jobs_sha256']:
        raise RuntimeError('live_job_manifest_changed')
    return frozen


def main():
    path = CAMPAIGN / 'freeze.json'
    if path.exists():
        raise RuntimeError('freeze_exists_no_overwrite')
    accepted = CAMPAIGN / 'preflight-accepted/status.json'
    if json.loads(accepted.read_text())['status'] != 'COMPLETE':
        raise RuntimeError('preflight_not_complete')
    # Historical source snapshots are never rewritten to fit this protocol.
    for historical in (ROOT.parent / 'reports/phase4-v2/freeze.json',
                       ROOT / 'artifacts/stage4-policy-20261021/freeze.json'):
        for name, wanted in json.loads(historical.read_text())['source_sha256'].items():
            if sha(ROOT.parent / name) != wanted:
                raise RuntimeError('historical_source_changed:' + name)
    jobs = reliability_jobs() + batching_jobs()
    (CAMPAIGN / 'jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    files = []
    for root in (ROOT, checkout('research')):
        files += [root / name for name in ('pyproject.toml', 'uv.lock', 'README.md', 'config.toml', 'run.sh') if (root / name).is_file()]
        for folder in ('experiments', 'src', 'tests', 'scripts', 'tools'):
            files += [p for p in (root / folder).rglob('*') if p.is_file()
                      and p.suffix in ('.py', '.toml', '.lock', '.sh', '.ps1')
                      and '__pycache__' not in p.parts and '.venv' not in p.parts]
    files += [ROOT / 'docs/STAGE4_BATCHING_COMPLETION_PROTOCOL.md']
    if not json.loads((CAMPAIGN / 'trace-ready/result.json').read_text())['passed']:
        raise RuntimeError('trace_acceptance_not_passed')
    files += [p for folder in ('preflight-accepted', 'trace-ready')
              for p in (CAMPAIGN / folder).rglob('*') if p.is_file()]
    hashes = {}
    for file in sorted(set(files)):
        relative = file.relative_to(ROOT.parent)
        hashes[str(relative)] = sha(file)
        copy = CAMPAIGN / 'source' / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, copy)
    from importlib.metadata import version
    versions = {name: version(name) for name in ('langchain', 'langchain-core', 'langchain-ollama',
                                               'pydantic', 'PyJWT')}
    phoenix_python = str(Path.home() / '.local/share/rosa-envs/phoenix/bin/python')
    versions['arize-phoenix-client_in_separate_environment'] = subprocess.check_output(
        [phoenix_python, '-c', 'from importlib.metadata import version; print(version("arize-phoenix-client"))'], text=True).strip()
    data = {'frozen_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
            'platform': platform.platform(), 'dependencies': versions, 'source_sha256': hashes,
            'jobs_sha256': sha(CAMPAIGN / 'jobs.json'), 'trials_per_backend': len(jobs),
            'max_requests_per_backend': 1056, 'independent_authorship_or_blinding': False}
    path.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'freeze': str(path), 'trials_per_backend': len(jobs), 'files': len(hashes)}))


if __name__ == '__main__':
    main()
