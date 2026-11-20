from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
import shutil
from urllib.request import urlopen
from .design import jobs
from .runner import DESTINATION, ROOT, write


def main():
    if (DESTINATION / 'freeze.json').exists(): raise RuntimeError('freeze_exists_do_not_replace')
    for prerequisite in ('preflight/result.json', 'deterministic-preflight/result.json'):
        if not json.loads((DESTINATION / prerequisite).read_text())['pass']:
            raise RuntimeError('prerequisite_failed:' + prerequisite)
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    with urlopen(os.environ['OLLAMA_BASE_URL'] + '/api/tags', timeout=10) as response:
        model = next(m for m in json.load(response)['models'] if m['name'] == 'qwen3.5:9b')
    if model['digest'] != '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90':
        raise RuntimeError('local_model_digest_changed')
    write(DESTINATION / 'schedule.json', {p: jobs(p) for p in ('mock', 'gazebo')})
    write(DESTINATION / 'local-model.json', model)
    paths = list((ROOT.parent / 'rosa-research/src').rglob('*.py'))
    paths += list((ROOT / 'experiments/workflow_reference_v1').glob('*.py'))
    paths += [ROOT / 'experiments/reliability_v1/tracing.py', ROOT / 'experiments/ur5e_transfer_v1/arm.py',
              ROOT / 'tests/test_reference_report.py', ROOT / 'tests/test_workflow_v1.py',
              ROOT / 'tests/test_workflow_live_v1.py', ROOT / 'experiments/workflow_live_v1/inference.py',
              ROOT / 'experiments/workflow_live_v1/design.py', ROOT / 'experiments/workflow_live_v1/runner.py',
              ROOT / 'experiments/workflow_v1/pilot.py', ROOT.parent / 'reports/workflow-reference-v1-run.ps1',
              ROOT / 'docs/WORKFLOW_REFERENCE_V1_PROTOCOL_2026-10-22.md',
              ROOT.parent / 'rosa-research/pyproject.toml', ROOT.parent / 'rosa-research/uv.lock',
              DESTINATION / 'schedule.json', DESTINATION / 'local-model.json']
    files = {}
    for path in sorted(set(paths)):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(), 'files': files,
        'package_versions': {n: version(n) for n in ('langchain', 'langchain-core', 'langchain-ollama', 'pydantic', 'openinference-instrumentation-langchain')},
        'planned_mock_trials': 16, 'conditional_gazebo_trials': 16, 'model_cap_per_backend': 128,
        'live_requests_before_freeze': 0})
    print('FROZEN', len(files), 'files; 16 validation trials then 16 conditional Gazebo trials')


if __name__ == '__main__': main()
