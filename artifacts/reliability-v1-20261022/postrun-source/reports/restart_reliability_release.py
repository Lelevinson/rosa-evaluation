from pathlib import Path
import os
import signal
import subprocess

pid = 25998
command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
assert '/reports/reliability_auto_release.py' in command and 'runner' not in command
os.kill(pid, signal.SIGTERM)
subprocess.run(['/home/martin/.local/share/rosa-envs/research/bin/python',
    '/mnt/c/Proj/robotics/introtorobotics/reports/launch_reliability_release.py'], check=True)
