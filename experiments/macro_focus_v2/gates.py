import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / 'artifacts/prompt-contract-v1-live-20261026'
CONTINUATION = ROOT / 'artifacts/prompt-contract-v1-live-resume-r2-20261026'
FIRST_CONTINUATION = ROOT / 'artifacts/prompt-contract-v1-live-resume-r1-20261026'


def require_validation():
    path = VALIDATION / 'analysis.json'
    if (FIRST_CONTINUATION / 'COMBINED_ANALYSIS.json').exists():
        path = FIRST_CONTINUATION / 'COMBINED_ANALYSIS.json'
    if (CONTINUATION / 'COMBINED_ANALYSIS.json').exists():
        path = CONTINUATION / 'COMBINED_ANALYSIS.json'
    if not path.exists():
        raise RuntimeError('live_validation_not_finalized_no_new_pilot')
    result = json.loads(path.read_text())
    if not (result['engineering_gate'] and result['progression_gate']):
        raise RuntimeError('live_validation_gate_failed_no_new_pilot')
    for backend in ('ollama', 'siwc'):
        item = result['backends'][backend]
        if not (item['trials'] == 9 and item['correct'] == 9 and item['audited_trials'] >= 9
                and item['cleanup_verified'] and item['status'] == 'COMPLETE'):
            raise RuntimeError('live_validation_backend_not_ready:' + backend)
    return result
