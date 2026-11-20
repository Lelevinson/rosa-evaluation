"""Replace only the idle report worker; never signal the live model supervisor."""
from pathlib import Path
import os
import signal
import subprocess
import sys
import time

pid = int(sys.argv[1])
command = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
assert '/reports/finish_reliability.py' in command and 'runner' not in command, command
os.kill(pid, signal.SIGTERM)
time.sleep(0.2)
workspace = Path('/mnt/c/Proj/robotics/introtorobotics')
log = workspace / 'reports/RELIABILITY_V1_POSTPROCESS.log'
log.rename(log.with_name('RELIABILITY_V1_POSTPROCESS-previous-' + str(pid) + '.log'))
subprocess.run(['/home/martin/.local/share/rosa-envs/research/bin/python', str(workspace / 'reports/launch_reliability_finish.py')], check=True)
