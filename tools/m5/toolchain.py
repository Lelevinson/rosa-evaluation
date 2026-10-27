"""Record operator dependencies/source hashes; do not install or change packages."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/macro-m5-20261027'
packages = {name: importlib.metadata.version(name) for name in ('matplotlib', 'numpy', 'Pillow', 'reportlab', 'pypdf', 'fonttools')}
scripts = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (ROOT / 'tools/m5').rglob('*') if p.is_file() and p.suffix in ('.py', '.sdf')}
record = {'operator_python': sys.version, 'platform': platform.platform(), 'reporting_packages': packages,
          'ffmpeg_version': subprocess.check_output([shutil.which('ffmpeg'), '-version'], text=True).splitlines()[0],
          'video_font_sha256': hashlib.sha256(Path('C:/Windows/Fonts/arial.ttf').read_bytes()).hexdigest(),
          'operator_source_sha256': scripts,
          'runtime_environment': 'Separate existing Python3.12 WSL research environment with unchanged research/Phoenix uv locks.',
          'scope': 'Recorded existing Windows report/video toolchain; not a fresh-machine installation guarantee or modification of runtime dependencies.'}
(OUT / 'operator-toolchain.json').write_text(json.dumps(record, indent=2) + '\n')
(ROOT / 'tools/m5/requirements-recorded.txt').write_text(''.join(f'{name}=={version}\n' for name, version in packages.items()))
print(json.dumps({'reporting_packages': packages, 'operator_sources': len(scripts)}))
