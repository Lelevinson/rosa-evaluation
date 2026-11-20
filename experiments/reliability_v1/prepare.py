"""Create exact-byte source freeze after deterministic prerequisites pass."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from .runner import DESTINATION, ROOT, run_scripted


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    if (DESTINATION / 'freeze.json').exists():
        raise RuntimeError('freeze_already_exists_do_not_overwrite')
    controls = run_scripted()
    assert len(controls) == 16 and all(r['pass'] for r in controls)
    (DESTINATION / 'scripted-controls.json').write_text(json.dumps(controls, indent=2))
    research = ROOT.parent / 'rosa-research'
    paths = sorted(list((research / 'src').rglob('*.py'))
                   + list((research / 'src/rosa_reliability/sim').glob('*'))
                   + list((ROOT / 'experiments/reliability_v1').glob('*.py'))
                   + [ROOT / 'tests/test_reliability_integration.py', research / 'tests/test_reliability.py',
                      research / 'pyproject.toml', research / 'uv.lock',
                      ROOT / 'docs/RELIABILITY_V1_PROTOCOL_2026-10-22.md'])
    manifest = {}
    for file in paths:
        relative = str(file.relative_to(ROOT.parent))
        manifest[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
        copy = DESTINATION / 'source' / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, copy)
    (DESTINATION / 'freeze.json').write_text(json.dumps({'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'files': manifest, 'planned_trials_per_backend': 36, 'request_cap_per_backend': 288,
        'no_live_model_requests_before_freeze': True}, indent=2))
    print('Frozen', len(manifest), 'files; 16 deterministic case/arm controls passed.', flush=True)


if __name__ == '__main__':
    main()
