"""Freeze code and cases before any live generation. Excludes all credentials."""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
from urllib.request import urlopen
import os
from .design import jobs
from .runner import DESTINATION, ROOT, write


def main():
    if (DESTINATION / 'freeze.json').exists():
        raise RuntimeError('freeze_already_exists_do_not_replace')
    if not json.loads((DESTINATION / 'preflight/result.json').read_text())['pass']:
        raise RuntimeError('preflight_not_passed')
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    with urlopen(os.environ['OLLAMA_BASE_URL'] + '/api/tags', timeout=10) as response:
        tags = json.load(response)
    model = next(m for m in tags['models'] if m['name'] == 'qwen3.5:9b')
    if model['digest'] != '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90':
        raise RuntimeError('local_model_digest_changed')
    write(DESTINATION / 'schedule.json', jobs())
    write(DESTINATION / 'local-model.json', model)
    paths = list((ROOT.parent / 'rosa-research/src').rglob('*.py'))
    paths += list((ROOT / 'experiments/workflow_live_v1').glob('*.py'))
    paths += [ROOT / 'experiments/reliability_v1/tracing.py', ROOT / 'experiments/workflow_v1/pilot.py',
              ROOT / 'tests/test_workflow_live_v1.py', ROOT / 'docs/WORKFLOW_LIVE_V1_PROTOCOL_2026-10-22.md',
              ROOT.parent / 'reports/workflow-live-v1-run.ps1',
              ROOT.parent / 'rosa-research/pyproject.toml', ROOT.parent / 'rosa-research/uv.lock',
              DESTINATION / 'schedule.json', DESTINATION / 'local-model.json']
    files = {}
    for path in sorted(set(paths)):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': files, 'package_versions': {n: version(n) for n in
            ('langchain', 'langchain-core', 'langchain-ollama', 'pydantic', 'openinference-instrumentation-langchain')},
        'planned_trials': 24, 'live_requests_before_freeze': 0})
    print('FROZEN', len(files), 'files; 24 trials, 96 maximum inference requests per backend')


if __name__ == '__main__': main()
