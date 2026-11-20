"""Build/install a wheel into an empty target using existing supported deps."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
destination = root / 'rosa-evaluation/artifacts/macro-module-v1-20261027'
folder = destination / ('package-' + str(len(list(destination.glob('package-*'))) + 1).zfill(2))
folder.mkdir()
scratch = Path(tempfile.mkdtemp(prefix='rosa-macro-m1-package-'))
project = scratch / 'project'
project.mkdir()
shutil.copytree(root / 'rosa-research/src', project / 'src',
                ignore=shutil.ignore_patterns('__pycache__', '*.egg-info'))
for name in ('pyproject.toml', 'README.md', 'LICENSE'):
    if (root / 'rosa-research' / name).exists(): shutil.copy2(root / 'rosa-research' / name, project / name)
environment = {**os.environ, 'UV_PYTHON': sys.executable, 'PYTHONDONTWRITEBYTECODE': '1'}
uv = shutil.which('uv') or str(Path.home() / '.local/bin/uv')
commands = [[uv, 'build', '--wheel', '--offline', '--out-dir', str(folder)]]
result = {'pass': False, 'live_model_requests': 0, 'scratch': str(scratch),
          'dependency_environment': 'existing pinned research dependencies; empty wheel installation target'}
try:
    for index, command in enumerate(commands):
        run = subprocess.run(command, cwd=project, env=environment, capture_output=True, text=True, timeout=120)
        (folder / ('build-' + str(index) + '.log')).write_text(run.stdout + run.stderr)
        if run.returncode: raise RuntimeError('offline_wheel_build_failed')
    wheels = list(folder.glob('*.whl'))
    if len(wheels) != 1: raise RuntimeError('expected_one_wheel')
    target = scratch / 'installed'
    install = subprocess.run([uv, 'pip', 'install', '--no-deps', '--no-index',
        '--target', str(target), str(wheels[0])], capture_output=True, text=True, timeout=60)
    (folder / 'install.log').write_text(install.stdout + install.stderr)
    if install.returncode: raise RuntimeError('wheel_target_install_failed')
    script = '''import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import rosa, rosa_reliability.bounded_macro as public
from rosa_reliability.macro_agent import MacroROSA
from rosa_reliability.macro_demo import MemoryTransport, demo_registry
target = pathlib.Path(sys.argv[1])
assert pathlib.Path(public.__file__).is_relative_to(target)
assert pathlib.Path(rosa.__file__).is_relative_to(target)
inv = demo_registry().open(MemoryTransport())
inv.execute('station.right')
assert inv.submit_report('SUCCESS', inv.session.observations[-1]['observation_id'])['report_accepted']
print(json.dumps({'pass': True, 'module': public.__file__, 'version': public.__version__}))
'''
    probe = subprocess.run([sys.executable, '-I', '-c', script, str(target)],
                           capture_output=True, text=True, timeout=60)
    (folder / 'isolated-import.log').write_text(probe.stdout + probe.stderr)
    if probe.returncode: raise RuntimeError('isolated_installed_wheel_probe_failed')
    result.update(pass_=True, wheel=wheels[0].name, installed_probe=json.loads(probe.stdout))
    result['pass'] = result.pop('pass_')
except BaseException as error:
    result.update(error_type=type(error).__name__, error=str(error))
    raise
finally:
    (folder / 'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result))
