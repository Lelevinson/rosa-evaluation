"""F1 Stage 0 static source inspection (laptop; no execution of frozen code, no model, no network).

1. AST of wording.py: F1MacroROSA subclasses MacroROSA and defines ONLY _get_prompts and invoke;
   the module assigns no attribute of any other object (no monkey-patching).
2. No F1 study module imports a model client, network library or protected rosa_auth.
3. Records SHA-256 (CRLF->LF normalized) of every frozen file the controls import, relative to the
   workspace that holds rosa-evaluation/ and rosa-research/, and checks rosa-research/src/rosa_reliability
   equals commit 8713f9b. controls.py re-checks these hashes on the lab before running.

Usage:  python -I -B tools/f1_wording/static_check.py
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORKSPACE = REPO.parent
OUT = REPO / 'artifacts/f1-catalogue-wording-20261121/controls'
RESEARCH_COMMIT = '8713f9b205033a25f8ed8d9549610e9ad0b8bfde'
G1 = 'rosa-evaluation/artifacts/macro-generalization-20261113/revision-1/'
FROZEN = [G1 + n for n in ('worlds.py', 'catalogue.py', 'stage-2/scoring.py', 'prompt-contract.json', 'cases.json',
                           'stage-1/cases.json')]
FORBIDDEN = ('ollama', 'langchain_ollama', 'langchain_openai', 'openai', 'rosa_auth', 'requests', 'httpx',
             'urllib.request', 'socket', 'http.client')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def wrapper_shape():
    tree = ast.parse((HERE / 'wording.py').read_text(encoding='utf-8'))
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert len(classes) == 1 and classes[0].name == 'F1MacroROSA'
    cls = classes[0]
    methods = sorted(n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    other = [type(n).__name__ for n in cls.body if not isinstance(n, (ast.FunctionDef, ast.Expr))]
    attribute_writes = [ast.unparse(t) for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign))
                        for t in (n.targets if isinstance(n, ast.Assign) else [n.target]) if isinstance(t, ast.Attribute)]
    setattr_calls = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, ast.Call) and
                     isinstance(n.func, ast.Name) and n.func.id in ('setattr', 'delattr')]
    result = {'class': cls.name, 'bases': [ast.unparse(b) for b in cls.bases], 'methods_defined': methods,
              'other_class_members': other, 'attribute_assignments_in_module': attribute_writes,
              'setattr_or_delattr_calls': setattr_calls}
    result['pass'] = (result['bases'] == ['MacroROSA'] and methods == ['_get_prompts', 'invoke'] and not other
                      and not attribute_writes and not setattr_calls)
    return result


def imports():
    found = {}
    for path in sorted(HERE.glob('*.py')):
        names = []
        for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(n, ast.Import):
                names += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module:
                names.append(n.module)
        bad = sorted({m for m in names if any(m == f or m.startswith(f + '.') for f in FORBIDDEN)})
        found[path.name] = {'imports': sorted(set(names)), 'forbidden': bad}
    return {'files': found, 'pass': not any(v['forbidden'] for v in found.values())}


def frozen_inputs():
    research = sorted((WORKSPACE / 'rosa-research/src/rosa_reliability').glob('*.py'))
    rels = FROZEN + [p.relative_to(WORKSPACE).as_posix() for p in research]
    diff = subprocess.run(['git', '-C', str(WORKSPACE / 'rosa-research'), 'diff', '--quiet', RESEARCH_COMMIT, '--',
                           'src/rosa_reliability'], capture_output=True)
    untracked = subprocess.run(['git', '-C', str(WORKSPACE / 'rosa-research'), 'ls-files', '--others',
                                '--exclude-standard', 'src/rosa_reliability'], capture_output=True, text=True).stdout.split()
    files = {rel: sha(WORKSPACE / rel) for rel in rels}
    return {'hash_basis': 'SHA-256 of file content with CRLF normalized to LF', 'rosa_research_commit': RESEARCH_COMMIT,
            'rosa_reliability_equals_commit': diff.returncode == 0 and not untracked, 'files': files}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = frozen_inputs()
    (OUT / 'FROZEN_INPUTS.json').write_bytes((json.dumps(frozen, indent=1, sort_keys=True) + '\n').encode())
    result = {'wrapper_shape': wrapper_shape(), 'study_imports': imports(),
              'frozen_inputs_recorded': len(frozen['files']),
              'rosa_reliability_equals_commit': frozen['rosa_reliability_equals_commit'],
              'note': 'Static inspection only. Behavioural equivalence is control C1 in controls.py (lab).'}
    result['pass'] = (result['wrapper_shape']['pass'] and result['study_imports']['pass']
                      and frozen['rosa_reliability_equals_commit'])
    (OUT / 'STATIC_CHECK.json').write_bytes((json.dumps(result, indent=1, sort_keys=True) + '\n').encode())
    print(json.dumps({k: result[k] for k in ('pass', 'frozen_inputs_recorded', 'rosa_reliability_equals_commit')}),
          json.dumps(result['wrapper_shape']), {k: v['forbidden'] for k, v in result['study_imports']['files'].items()})


if __name__ == '__main__':
    main()
