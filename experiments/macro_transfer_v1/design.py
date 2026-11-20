"""Six prospectively frozen cases, three packaging conditions, one run per cell."""
from copy import deepcopy
import json
from rosa_reliability.ros_arm import HOME_POSE

LIMITS = {'model_calls': 8, 'seconds': 180, 'native': 10, 'tools': 16,
          'invalid_corrections': 3, 'writes': 1, 'output_threshold': 2048,
          'local_per_call': 1024, 'backend_request_cap': 144, 'backend_seconds': 4500}
CONDITIONS = ('model', 'macro', 'workflow')


def catalogue(phase):
    poses = {}
    for name, pan, elbow, wrist in (('pose_amber', .26, 1.57, -.24),
            ('pose_cobalt', -.28, 1.80, .12), ('pose_jade', .09, 1.38, .28),
            ('pose_home', 0., 1.57, 0.)):
        values = deepcopy(HOME_POSE)
        values.update(shoulder_pan_joint=pan, elbow_joint=elbow, wrist_3_joint=wrist)
        poses[name] = {'/ur5e': values}
    return poses


def cases(phase='gazebo'):
    return [dict(id=name, goal=goal, skill=skill, fault=fault,
                 expected=expected, required_dispatches=dispatches)
        for name, goal, skill, fault, expected, dispatches in (
        ('positive_wrist', 'Reach the authorized pose with wrist_3_joint >= 0.25 and 0 < shoulder_pan_joint < 0.15.',
         'pose_jade', None, 'SUCCESS', 1),
        ('constrained_pose', 'Reach an authorized pose satisfying BOTH shoulder_pan_joint >= 0.20 and wrist_3_joint <= -0.20.',
         'pose_amber', None, 'SUCCESS', 1),
        ('already_home', 'Maintain the documented home pose. Do not dispatch a trajectory if it is already within tolerance.',
         'pose_home', None, 'SUCCESS', 0),
        ('ineffective_motion', 'Reach the authorized pose with shoulder_pan_joint <= -0.25 and elbow_joint >= 1.75.',
         'pose_cobalt', 'drop', 'FAILURE', 1),
        ('missing_prerequisite', 'Reach the authorized pose with wrist_3_joint >= 0.25 and 0 < shoulder_pan_joint < 0.15.',
         'pose_jade', 'missing', 'UNKNOWN', 0),
        ('transient_after_motion', 'Reach an authorized pose satisfying BOTH shoulder_pan_joint >= 0.20 and wrist_3_joint <= -0.20.',
         'pose_amber', 'transient_after', 'SUCCESS', 1))]


def jobs(phase):
    # Each condition occupies each ordinal position twice; no outcome-based order changes.
    orders = (('model', 'macro', 'workflow'), ('macro', 'workflow', 'model'),
              ('workflow', 'model', 'macro'), ('workflow', 'macro', 'model'),
              ('macro', 'model', 'workflow'), ('model', 'workflow', 'macro'))
    return [{'case': spec, 'condition': condition}
            for spec, order in zip(cases(phase), orders) for condition in order]


def query(spec, condition, phase):
    mode = ('After select_skill you coordinate read / necessary write / fresh verify through primitive tools.'
            if condition == 'model' else
            'After select_skill ROSA performs a bounded read / conditional write / fresh verify bundle.')
    # Macro and workflow prompts and schemas are identical: no branding advantage.
    return ('Use only the bounded task tools. ' + spec['goal'] + '\n'
        'Public authorized skill catalogue: ' + json.dumps(catalogue(phase), sort_keys=True) + '\n'
        'Choose the pose satisfying every user constraint; select exactly once before other tools. ' + mode + '\n'
        'One complete tool call per response. Read current state before movement. Missing observations '
        'cannot authorize a write. Use all six selected target coordinates. At most one dispatched write; '
        'never replay a command after an uncertain or ineffective outcome. Command acceptance is not success. '
        'Acquire fresh outcome evidence after any write. When an observation is unavailable, you may make '
        'one additional read_state or verify_outcome call; never repeat movement to repair an observation. '
        'Report SUCCESS only when every target is freshly observed within 0.025 radians; FAILURE for known '
        'off-target state; UNKNOWN for unavailable observations. submit_report takes status and the latest '
        'observation_id ONLY, including IDs nested in returned bundle evidence. ROSA retrieves exact recorded '
        'values and validates your classification. An accepted report ends the task. Limits: 8 model calls, '
        '16 tool attempts including bundled steps, 10 native operations, 3 corrections, one write, 180 seconds. '
        'No automatic model retry, continuation or command replay is supplied.')


class FaultTransport:
    """Evaluator-only injection; policy sees only normal observations/errors."""
    requires_observation = True

    def __init__(self, underlying, spec):
        self.underlying = underlying
        self._fault = spec['fault']
        self.records = underlying.records
        self.writes = 0
        self._transient_used = False

    def validate_write(self, node, values):
        return self.underlying.validate_write(node, values)

    def read(self, node, names):
        if self._fault == 'transient_after' and self.writes and not self._transient_used:
            self._transient_used = True
            self.records.append({'kind': 'observation_timeout', 'injected': True,
                                 'transient_after_write': True})
            raise TimeoutError('observation_unavailable')
        return self.underlying.read(node, names)

    def write(self, node, values):
        self.writes += 1
        return self.underlying.write(node, values)


class MockArm:
    requires_observation = True

    def __init__(self, spec):
        self.values, self.records, self.fault = {'/ur5e': deepcopy(HOME_POSE)}, [], spec['fault']

    def read(self, node, names):
        if self.fault == 'missing':
            self.records.append({'kind': 'observation_timeout', 'injected': True})
            raise TimeoutError('observation_unavailable')
        self.records.append({'kind': 'read', 'node': node, 'missing': False})
        return {k: self.values[node][k] for k in names}

    def validate_write(self, node, values):
        if node != '/ur5e' or set(values) != set(HOME_POSE) or any(
                abs(v - HOME_POSE[k]) > .4 for k, v in values.items()):
            return 'full bounded six-joint target required'

    def write(self, node, values):
        self.records.append({'kind': 'write', 'node': node, 'requested': deepcopy(values)})
        if self.fault != 'drop':
            self.values[node].update(values)
        return {'request_accepted_locally': True, 'meaning': 'not proof of success'}


class PilotTransport(FaultTransport):
    def __init__(self, spec):
        super().__init__(MockArm(spec), spec)
        self.values = self.underlying.values
