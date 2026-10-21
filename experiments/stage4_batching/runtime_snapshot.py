"""Read-only runtime identity snapshot; no model generation or tuning."""
from datetime import datetime, timezone
import json
from urllib.request import ProxyHandler, build_opener

from dotenv import dotenv_values
from ..config import ROOT
from .runner import CAMPAIGN


def main():
    endpoint = dotenv_values(ROOT / '.env')['OLLAMA_BASE_URL']
    opener = build_opener(ProxyHandler({}))
    data = {'observed_utc': datetime.now(timezone.utc).isoformat(), 'endpoint': endpoint,
            'method': 'read-only version/tags/ps metadata; zero inference requests'}
    for name in ('version', 'tags', 'ps'):
        with opener.open(endpoint + '/api/' + name, timeout=15) as response:
            data[name] = json.load(response)
    path = CAMPAIGN / 'local-runtime-observation.json'
    if path.exists():
        raise RuntimeError('runtime_snapshot_already_exists')
    path.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'version': data['version'], 'loaded_models': [m.get('name') for m in data['ps'].get('models', [])]}))


if __name__ == '__main__':
    main()
