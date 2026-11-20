from copy import deepcopy
from experiments.macro_transfer_v1.design import LIMITS as ORIGINAL_LIMITS, jobs as original_jobs

LIMITS = {**ORIGINAL_LIMITS, 'backend_request_cap': 72}
KNOWN_CASES = ('already_home', 'missing_prerequisite', 'transient_after_motion')


def jobs(phase):
    if phase != 'gazebo':
        raise ValueError('live validation uses Gazebo only')
    return [deepcopy(job) for job in original_jobs(phase) if job['case']['id'] in KNOWN_CASES]
