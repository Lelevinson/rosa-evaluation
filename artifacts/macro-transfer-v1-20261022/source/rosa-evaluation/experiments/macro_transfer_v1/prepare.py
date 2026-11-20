"""Freeze sources, cases and serving settings after engineering prerequisites."""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
import shutil
from urllib.request import urlopen
from .design import jobs, LIMITS
from .runner import DESTINATION, ROOT, write


def main():
    if (DESTINATION / 'freeze.json').exists():
        raise RuntimeError('freeze_exists_do_not_replace')
    for prerequisite in ('preflight/result.json', 'deterministic-preflight/result.json'):
        if not json.loads((DESTINATION / prerequisite).read_text())['pass']:
            raise RuntimeError('prerequisite_failed:' + prerequisite)
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    with urlopen(os.environ['OLLAMA_BASE_URL'] + '/api/tags', timeout=10) as response:
        model = next(m for m in json.load(response)['models'] if m['name'] == 'qwen3.5:9b')
    if model['digest'] != '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90':
        raise RuntimeError('local_model_digest_changed')
    write(DESTINATION / 'schedule.json', {'gazebo': jobs('gazebo')})
    write(DESTINATION / 'local-model.json', model)
    paths = list((ROOT.parent / 'rosa-research/src').rglob('*.py'))
    # Include transitive experiment helpers as well as the new campaign.
    paths += list((ROOT / 'experiments').rglob('*.py'))
    paths += list((ROOT / 'tools/phoenix').glob('*.py'))
    paths += [ROOT / 'tests' / name for name in ('test_macro_transfer_v1.py',
        'test_reference_report.py', 'test_workflow_v1.py', 'test_workflow_live_v1.py')]
    paths += [ROOT.parent / 'reports/macro-transfer-v1-run.ps1',
        ROOT.parent / 'reports/v2-command.sh', ROOT.parent / 'reports/finalize_macro_transfer_v1.py',
        ROOT / 'docs/MACRO_TRANSFER_V1_PROTOCOL_2026-10-22.md',
        ROOT.parent / 'rosa-research/pyproject.toml', ROOT.parent / 'rosa-research/uv.lock',
        ROOT / 'tools/phoenix/pyproject.toml', ROOT / 'tools/phoenix/uv.lock',
        DESTINATION / 'schedule.json', DESTINATION / 'local-model.json']
    files = {}
    for path in sorted(set(paths)):
        name = path.relative_to(ROOT.parent).as_posix()
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        target = DESTINATION / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write(DESTINATION / 'freeze.json', {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': files, 'limits': LIMITS, 'planned_trials_per_backend': 18, 'planned_total_trials': 36,
        'package_versions': {n: version(n) for n in ('langchain', 'langchain-core',
            'langchain-ollama', 'pydantic', 'openinference-instrumentation-langchain')},
        'live_requests_before_freeze': 0,
        'prelive_structural_finding': 'Macro and workflow use the same acquisition policy; no algorithmic novelty contrast.',
        'previous_archive_correction': json.loads((ROOT / 'artifacts/WORKFLOW_REFERENCE_V1_ARCHIVE_CORRECTION.json').read_text())})
    print('FROZEN', len(files), 'files; 36 trials, at most 144 requests per backend')


if __name__ == '__main__':
    main()
