"""Offline wheel/empty-target acceptance using the existing ROS/dependency runtime."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027/package'


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    project = Path(tempfile.mkdtemp(prefix='rosa-m5-package-')) / 'project'
    project.mkdir()
    source = ROOT.parent / 'rosa-research'
    shutil.copytree(source / 'src', project / 'src', ignore=shutil.ignore_patterns('__pycache__', '*.egg-info'))
    for name in ('pyproject.toml', 'README.md', 'LICENSE'):
        shutil.copyfile(source / name, project / name)
    uv = shutil.which('uv') or str(Path.home() / '.local/bin/uv')
    env = {**os.environ, 'UV_PYTHON': sys.executable, 'PYTHONDONTWRITEBYTECODE': '1'}
    commands = [[uv, 'build', '--wheel', '--offline', '--out-dir', str(OUT)]]
    result = {'live_model_requests': 0, 'pass': False,
        'scope': 'Offline wheel build and empty installation target; existing research dependencies/ROS retained, not fresh OS.',
        'python': sys.version, 'source_pyproject_sha256': hashlib.sha256((source / 'pyproject.toml').read_bytes()).hexdigest(),
        'source_uv_lock_sha256': hashlib.sha256((source / 'uv.lock').read_bytes()).hexdigest()}
    try:
        build = subprocess.run(commands[0], cwd=project, env=env, capture_output=True, text=True, timeout=120)
        (OUT / 'build.log').write_text(build.stdout + build.stderr)
        assert build.returncode == 0, 'offline_build_failed'
        wheels = list(OUT.glob('*.whl'))
        assert len(wheels) == 1
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            assert archive.testzip() is None
            names = set(archive.namelist())
            assert {'rosa_reliability/capabilities.py', 'rosa_reliability/sim/arm.sdf',
                    'rosa_reliability/sim/bridge.yaml'} <= names
        target = project.parent / 'installed'
        install = subprocess.run([uv, 'pip', 'install', '--no-deps', '--no-index', '--target', str(target), str(wheel)],
                                 capture_output=True, text=True, timeout=60)
        (OUT / 'install.log').write_text(install.stdout + install.stderr)
        assert install.returncode == 0, 'empty_target_install_failed'
        probe = '''import json,pathlib,sys
sys.path.insert(0,sys.argv[1])
import rosa
import rosa_reliability.capabilities as cap
from rosa_reliability.bounded_macro import StateSkill,MacroLimits
from rosa_reliability.macro_agent import MacroROSA
class State:
 requires_observation=True
 def __init__(self):self.value=0.;self.writes=0
 def read(self,node,names):return {"joint":self.value}
 def write(self,node,values):self.value=values["joint"];self.writes+=1;return {"accepted":True}
class Inspect:
 def read_group(self,source,names):return {name:True for name in names}
registry=cap.CapabilityRegistry().register(StateSkill(skill_id="arm.move",targets={"/arm":{"joint":0.1}})).register(cap.InspectionSkill(skill_id="arm.inspect",subject="/ready",checks={"controllers":["active"],"sensor":["fresh"]}))
state=State()
movement=registry.open({"state":state,"inspection":Inspect()},limits=MacroLimits())
movement.execute("arm.move")
assert movement.submit_report("SUCCESS",movement.session.observations[-1]["observation_id"])["report_accepted"]
assert state.writes==1 and state.value==0.1
inspection=registry.open({"state":state,"inspection":Inspect()},allowed_skills=["arm.inspect"])
inspection.execute("arm.inspect")
assert inspection.submit_report("SUCCESS",inspection.session.observations[-1]["observation_id"])["report_accepted"]
assert state.writes==1 and len(inspection.snapshot()["operations"])==2
assert pathlib.Path(cap.__file__).is_relative_to(pathlib.Path(sys.argv[1]))
assert pathlib.Path(rosa.__file__).is_relative_to(pathlib.Path(sys.argv[1]))
assert not any(n.startswith("experiments.") for n in sys.modules)
print(json.dumps({"pass":True,"installed_module":cap.__file__,"version":cap.__version__,"movement_writes":state.writes,"inspection_sources":len(inspection.snapshot()["operations"]),"experiment_imports":False}))
'''
        run = subprocess.run([sys.executable, '-I', '-c', probe, str(target)], capture_output=True, text=True, timeout=60)
        (OUT / 'isolated-capability-probe.log').write_text(run.stdout + run.stderr)
        assert run.returncode == 0, 'installed_public_capability_probe_failed'
        help_code = 'import runpy,sys;sys.path.insert(0,sys.argv.pop(1));runpy.run_module("rosa_reliability.capability_demo",run_name="__main__")'
        help_run = subprocess.run([sys.executable, '-I', '-c', help_code, str(target), '--help'], capture_output=True, text=True, timeout=60)
        (OUT / 'installed-demo-help.log').write_text(help_run.stdout + help_run.stderr)
        assert help_run.returncode == 0 and '--mode' in help_run.stdout
        result.update({'pass': True, 'wheel': wheel.name, 'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                       'wheel_bytes': wheel.stat().st_size, 'probe': json.loads(run.stdout), 'installed_cli_help': 'PASS'})
    finally:
        (OUT / 'acceptance.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
