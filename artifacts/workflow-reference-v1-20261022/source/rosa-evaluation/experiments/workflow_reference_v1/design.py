from copy import deepcopy
import json
from rosa_reliability.ros_arm import HOME_POSE

LIMITS = {'model_calls': 8, 'seconds': 180, 'native': 10, 'tools': 16,
          'invalid_corrections': 3, 'writes': 1, 'output_threshold': 2048,
          'local_per_call': 1024, 'backend_request_cap': 128, 'backend_seconds': 2700}


def catalogue(phase):
    if phase == 'mock':
        return {'inspect_north': {'/fixture_delta': {'yaw': .22, 'pitch': -.29}},
                'inspect_south': {'/fixture_delta': {'yaw': -.31, 'pitch': .14}}}
    north, south = deepcopy(HOME_POSE), deepcopy(HOME_POSE)
    north.update(shoulder_pan_joint=.14, wrist_3_joint=.21)
    south.update(shoulder_pan_joint=-.21, elbow_joint=1.73, wrist_3_joint=-.14)
    return {'inspect_north': {'/ur5e': north}, 'inspect_south': {'/ur5e': south}}


def cases(phase):
    return [{'id': phase + '_' + name, 'goal': goal, 'skill': skill, 'fault': fault, 'expected': expected}
        for name, goal, skill, fault, expected in (
            ('north_move', 'Use the northern inspection pose.', 'inspect_north', None, 'SUCCESS'),
            ('south_move', 'Use the southern inspection pose.', 'inspect_south', None, 'SUCCESS'),
            ('north_no_effect', 'Use the northern inspection pose.', 'inspect_north', 'drop', 'FAILURE'),
            ('south_no_observation', 'Use the southern inspection pose.', 'inspect_south', 'missing', 'UNKNOWN'))]


def jobs(phase):
    return [{'case': spec, 'program': program} for i, spec in enumerate(cases(phase))
            for program in ((False, True) if i % 2 == 0 else (True, False))]


def query(spec, program, phase):
    tolerance = .025 if phase == 'gazebo' else .01
    mode = ('After select_skill ROSA coordinates read / conditional write / fresh verify.' if program else
            'After select_skill you coordinate read / necessary write / fresh verify through the primitive tools.')
    return ('Use only the bounded task tools. ' + spec['goal'] + '\n'
        'Public authorized skill catalogue: ' + json.dumps(catalogue(phase), sort_keys=True) + '\n'
        'Choose the requested pose. Select exactly once before other tools. ' + mode + '\n'
        'One complete tool call per response. Read current state before movement. Missing observations '
        'cannot authorize a write. At most one dispatched write; do not replay an accepted ineffective command. '
        'Use all named coordinates for movement. Command acceptance is not success. '
        'Acquire fresh outcome evidence after any write. Report SUCCESS only if all targets are observed '
        f'within {tolerance}; FAILURE for known off-target state; UNKNOWN for missing observations. '
        'submit_report takes status and observation_id ONLY. Copy the latest observation_id returned '
        'by read_state or verify_outcome (including nested workflow evidence); ROSA retrieves the actual '
        'node identifiers and values. Never reconstruct observed_values or invent a reference. '
        'If escalation occurs, use the same bounded tools to obtain evidence, report uncertainty or stop. '
        'An accepted report ends the task automatically. Limits: 8 model calls, 16 tool attempts '
        'including program steps, 10 native operations, 3 corrections, one dispatched write, 180 seconds. '
        'No automatic inference retry or truncation continuation is added.')


class PilotTransport:
    requires_observation = True
    def __init__(self, spec):
        self._fault = spec['fault']
        self.values = {'/fixture_delta': {'yaw': -.02, 'pitch': .04}}
        self.records, self.writes = [], 0
    def read(self, node, names):
        missing = self._fault == 'missing'
        self.records.append({'kind': 'read', 'node': node, 'missing': missing})
        if missing:
            raise TimeoutError('observation_unavailable')
        return {k: self.values[node][k] for k in names}
    def validate_write(self, node, values):
        if set(values) != {'yaw', 'pitch'} or any(abs(v) > .5 for v in values.values()):
            return 'complete yaw and pitch within [-0.5,0.5] required'
    def write(self, node, values):
        self.writes += 1
        self.records.append({'kind': 'write', 'node': node, 'requested': deepcopy(values)})
        if self._fault != 'drop':
            self.values[node].update(values)
        return {'accepted': True, 'meaning': 'request acceptance, not verified outcome'}
