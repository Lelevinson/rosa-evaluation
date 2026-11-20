"""Create an immutable protocol/source snapshot before any new live inference."""
from datetime import datetime, timezone
import hashlib
import json
import shutil
from pathlib import Path
from ..config import ROOT, checkout
from .runner import CAMPAIGN, plan
from .scenarios import suite, digest


def main():
    target = CAMPAIGN / 'freeze.json'
    if target.exists():
        raise RuntimeError('Freeze already exists; create an explicitly new campaign for any revision')
    hashes = {}
    for repository in (ROOT, checkout('research')):
        candidates = [repository / n for n in ('pyproject.toml', 'uv.lock', '.python-version', 'config.toml', 'run.sh', 'README.md') if (repository / n).is_file()]
        for folder in ('experiments', 'src', 'tests', 'scripts', 'tools'):
            candidates += [p for p in (repository / folder).rglob('*') if p.is_file() and p.suffix in ('.py', '.sh', '.ps1', '.toml', '.lock') and '.venv' not in p.parts and '__pycache__' not in p.parts]
        for path in candidates:
            relative = path.relative_to(ROOT.parent)
            hashes[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
            destination = CAMPAIGN / 'source' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    protocol = ROOT.parent / 'PHASE4_V2_PLAN.md'
    hashes[str(protocol.relative_to(ROOT.parent))] = hashlib.sha256(protocol.read_bytes()).hexdigest()
    shutil.copy2(protocol, CAMPAIGN / 'PHASE4_V2_PLAN.md')
    data = {'frozen_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': hashes,
            'manifest_sha256': digest(suite()), 'live_trials_per_backend': len(plan()),
            'scripted_trials': len(plan(True)), 'evaluation_used_for_prompt_tuning': False,
            'independent_authorship_or_blinding': False,
            'scope': '60 new mechanism-varied fixtures; model evaluation families disjoint from development; one live repetition'}
    (CAMPAIGN / 'scenario-manifest.json').write_text(json.dumps(suite(), indent=2) + '\n')
    target.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({k: v for k, v in data.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
