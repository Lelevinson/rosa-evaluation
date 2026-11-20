"""Candidate held-out cases: initial-state, constraint and observation decisions.

These are new combinations within one bounded trajectory capability, not six
independent robot skills or a claim of broad task generalization.
"""
from copy import deepcopy
import json
from rosa_reliability.ros_arm import HOME_POSE
from experiments.prompt_live_v1.design import LIMITS as VALIDATION_LIMITS

LIMITS = {**VALIDATION_LIMITS, 'backend_request_cap': 288}
CONDITIONS = ('model', 'macro', 'workflow')


def catalogue(phase='gazebo'):
    poses = {'home': {'/ur5e': deepcopy(HOME_POSE)}}
    for name, pan, elbow, wrist in (('elm', .21, 1.49, -.30),
                                   ('fern', -.19, 1.75, .18),
                                   ('birch', .12, 1.86, .31)):
        values = deepcopy(HOME_POSE)
        values.update(shoulder_pan_joint=pan, elbow_joint=elbow, wrist_3_joint=wrist)
        poses[name] = {'/ur5e': values}
    return poses


def cases(phase='gazebo'):
    return [dict(id=name, goal=goal, skill=skill, fault=fault, expected=expected,
        required_dispatches=dispatches, initial_skill=initial) for
        name, goal, skill, fault, expected, dispatches, initial in (
        ('return_from_offset', 'Return to the documented home pose. Execute motion only if the current state requires it.',
         'home', None, 'SUCCESS', 1, 'elm'),
        ('retain_nonhome_goal', 'Maintain the authorized pose with shoulder_pan_joint < -0.15 and wrist_3_joint >= 0.15. Do not move if it is already achieved.',
         'fern', None, 'SUCCESS', 0, 'fern'),
        ('three_constraints', 'Reach an authorized pose satisfying ALL of: 0.05 < shoulder_pan_joint < 0.16, elbow_joint >= 1.82, wrist_3_joint >= 0.28.',
         'birch', None, 'SUCCESS', 1, 'home'),
        ('prerequisite_recovers', 'Reach an authorized pose with shoulder_pan_joint < -0.15 and elbow_joint >= 1.70. Do not move without an available prerequisite observation.',
         'fern', 'transient_before', 'SUCCESS', 1, 'home'),
        ('partial_execution', 'Reach an authorized pose satisfying shoulder_pan_joint >= 0.18 and wrist_3_joint <= -0.25. Verify all six joints; never replay an attempted movement.',
         'elm', 'partial', 'FAILURE', 1, 'home'),
        ('outcome_unavailable', 'Reach an authorized pose satisfying elbow_joint >= 1.82 and wrist_3_joint >= 0.28. Command acceptance is not outcome evidence; do not replay an attempted movement.',
         'birch', 'missing_after', 'UNKNOWN', 1, 'home'))]


def jobs(phase='gazebo'):
    orders = (('model', 'macro', 'workflow'), ('macro', 'workflow', 'model'),
              ('workflow', 'model', 'macro'), ('workflow', 'macro', 'model'),
              ('macro', 'model', 'workflow'), ('model', 'workflow', 'macro'))
    # Each permutation occurs twice. Repeat 2 shifts each case's position and
    # changes its condition order. Pair by case and repetition, never by outcome.
    return [{'case': spec, 'condition': condition, 'repetition': repetition + 1}
        for repetition in range(2)
        for index in range(6)
        for spec in [deepcopy(cases(phase)[(index + 3 * repetition) % 6])]
        for condition in orders[(index + 2 * repetition) % 6]]


def query(spec, condition, phase):
    mode = ('After select_skill you coordinate read / necessary write / fresh verify through primitive tools.'
            if condition == 'model' else
            'After select_skill ROSA performs a bounded read / conditional write / fresh verify bundle.')
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
    """Acquisition failures are injected in the task transport, not the oracle."""
    requires_observation = True

    def __init__(self, underlying, spec):
        self.underlying, self._fault = underlying, spec['fault']
        self.records, self.writes, self._transient_used = underlying.records, 0, False

    def validate_write(self, node, values):
        return self.underlying.validate_write(node, values)

    def read(self, node, names):
        transient = self._fault == 'transient_before' and not self.writes and not self._transient_used
        missing = self._fault == 'missing_after' and self.writes > 0
        if transient or missing:
            self._transient_used = True
            self.records.append({'kind': 'observation_timeout', 'injected': True,
                'transient_before_write': transient, 'persistent_after_write': missing})
            raise TimeoutError('observation_unavailable')
        return self.underlying.read(node, names)

    def write(self, node, values):
        self.writes += 1
        return self.underlying.write(node, values)


def initialize(controller, observer, spec):
    from experiments.ur5e_transfer_v1.arm import reset, configure_fault, JOINTS
    origin = reset(controller, observer)
    initial = catalogue()[spec['initial_skill']]['/ur5e']
    if spec['initial_skill'] != 'home':
        controller.write('/ur5e', initial)
        actual = observer.read('/ur5e', list(JOINTS))
        if any(abs(actual[k] - v) > .025 for k, v in initial.items()):
            raise RuntimeError('independent_case_initialization_failed')
        origin['case_initialization'] = {'outside_trial': True, 'observed': actual,
            'target': deepcopy(initial), 'observer_record': deepcopy(observer.records[-1])}
    configure_fault(controller, spec)
    controller.records.clear()
    return origin
