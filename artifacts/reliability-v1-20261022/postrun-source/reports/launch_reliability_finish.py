from pathlib import Path
import subprocess
workspace = Path('/mnt/c/Proj/robotics/introtorobotics')
with (workspace/'reports/RELIABILITY_V1_POSTPROCESS.log').open('x') as output:
    child = subprocess.Popen(['/home/martin/.local/share/rosa-envs/research/bin/python', str(workspace/'reports/finish_reliability.py')],
                             stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
print('Durable report/packaging worker PID', child.pid)
