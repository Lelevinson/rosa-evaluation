"""Read-only environment + code fingerprint for comparing the laptop Sol env with the lab copy (F1 D12).

No model, network or credential access; it only reads files and package metadata.
Hashes use CRLF->LF normalized content (as controls/FROZEN_INPUTS.json), so a Windows checkout and a
Linux copy of the same file compare equal.

Usage (run with the interpreter being fingerprinted):
  <python> -I -B tools/f1_wording/env_fingerprint.py --workspace <dir holding rosa-evaluation/ and rosa-research/> --out <file.json>
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
KEY_PACKAGES = ('langchain', 'langchain-core', 'langchain-community', 'langchain-openai', 'langchain-ollama',
                'jpl-rosa', 'pydantic', 'openai', 'ollama', 'httpx', 'openinference-instrumentation-langchain')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def tree(root, pattern='*'):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob(pattern))
            if p.is_file() and '__pycache__' not in p.parts}


def digest_of(mapping):
    return hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    ws = args.workspace.resolve()
    dists = sorted({(d.metadata['Name'].lower(), d.version) for d in metadata.distributions()})
    langchain_tools = None
    try:
        import langchain.agents.output_parsers.tools as t
        langchain_tools = sha(t.__file__)
    except Exception as error:  # recorded, not fatal
        langchain_tools = 'unavailable: ' + type(error).__name__
    groups = {
        'rosa_reliability': tree(ws / 'rosa-research/src/rosa_reliability', '*.py'),
        'rosa_auth': tree(ws / 'rosa-research/src/rosa_auth', '*.py'),
        'g1_frozen_inputs': json.loads((REPO / 'artifacts/f1-catalogue-wording-20261121/controls/FROZEN_INPUTS.json')
                                       .read_text(encoding='utf-8'))['files'],
        'f1_code': tree(HERE, '*.py'),
        'f1_cases': tree(REPO / 'artifacts/f1-catalogue-wording-20261121/cases'),
    }
    recheck = {rel: sha(ws / rel) for rel in groups['g1_frozen_inputs']}
    result = {
        'python': sys.version.split()[0], 'executable': sys.executable, 'platform': platform.platform(),
        'distributions': len(dists), 'distributions_sha256': digest_of(dists),
        'key_packages': {n: v for n, v in dists if n in KEY_PACKAGES},
        'langchain_output_parsers_tools_sha256': langchain_tools,
        'group_sha256': {k: digest_of(v) for k, v in groups.items()},
        'group_files': {k: len(v) for k, v in groups.items()},
        'g1_frozen_inputs_match_on_this_host': recheck == groups['g1_frozen_inputs'],
        'files': groups,
        'model_requests': 0, 'network_access': False, 'credential_access': False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('python', 'platform', 'distributions', 'distributions_sha256', 'key_packages',
                      'langchain_output_parsers_tools_sha256', 'group_sha256', 'group_files',
                      'g1_frozen_inputs_match_on_this_host')}, indent=1))


if __name__ == '__main__':
    main()
