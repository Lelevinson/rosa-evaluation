from pathlib import Path
import subprocess
root = Path('/mnt/c/Proj/robotics/introtorobotics')
with (root/'rosa-evaluation/artifacts/reliability-v1-20261022/release-watcher.log').open('w') as output:
    child = subprocess.Popen(['/home/martin/.local/share/rosa-envs/research/bin/python',
                              str(root/'reports/reliability_auto_release.py')],
                             stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
print('Automatic sleep-hold release watcher PID', child.pid)
