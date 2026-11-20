"""Credential-free M1 environment/process inventory. No live inference."""
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
destination = root / 'rosa-evaluation/artifacts/macro-module-v1-20261027'
destination.mkdir(parents=True, exist_ok=False)
processes = subprocess.check_output(['ps', '-eo', 'pid,comm,args'], text=True)
relevant = [line for line in processes.splitlines()
            if any(term in line for term in ('ur_sim_control', 'gz sim', 'macro_focus_v2', 'phoenix.server'))
            and 'm1-inventory' not in line]
out = {'python': sys.version, 'packages': {name: version(name) for name in
       ('jpl-rosa', 'langchain', 'langchain-core', 'pydantic', 'langchain-ollama')},
       'relevant_processes': relevant, 'live_model_requests': 0}
(destination / 'environment-before.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
