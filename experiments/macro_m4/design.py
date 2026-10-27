from copy import deepcopy

from rosa_reliability.bounded_macro import StateSkill
from rosa_reliability.capabilities import CapabilityRegistry, InspectionSkill
from rosa_reliability.capability_demo import CHECKS
from rosa_reliability.ros_arm import HOME_POSE
from experiments.macro_capabilities_v2.m3 import RULES

LIMITS = {'repetitions': 2, 'calls_per_task': 8, 'output_tokens_per_task': 2048,
    'local_per_call': 1024, 'context': 8192, 'trial_seconds': 360.0,
    'native_operations': 10, 'tool_attempts': 16, 'corrections': 3,
    'tolerance': .025, 'backend_requests': 323, 'infrastructure_reserve': 3,
    'backend_seconds': 28800, 'retries_per_logical_call': 1, 'backoff_seconds': 1}


def registry():
    return (CapabilityRegistry()
        .register(StateSkill(skill_id='ur5e.home', targets={'/ur5e': dict(HOME_POSE)}))
        .register(StateSkill(skill_id='ur5e.stage_left', targets={'/ur5e':
            {**HOME_POSE, 'shoulder_pan_joint': -.14, 'wrist_3_joint': .20}}))
        .register(StateSkill(skill_id='ur5e.park_right', targets={'/ur5e':
            {**HOME_POSE, 'shoulder_pan_joint': .16, 'wrist_3_joint': -.12}}))
        .register(InspectionSkill(skill_id='ur5e.inspect_readiness', subject='/ur5e_readiness', checks=CHECKS)))


def cases():
    def move(identifier, request, skill, status='SUCCESS', fault=None, initial='ur5e.home', writes=1):
        return dict(id=identifier, request=request, skill=skill, expected=status, fault=fault,
            initial=initial, writes=writes, allowed=None, kind='movement')
    def inspect(identifier, request, status='SUCCESS', fault=None):
        return dict(id=identifier, request=request, skill='ur5e.inspect_readiness', expected=status,
            fault=fault, initial='ur5e.home', writes=0, allowed=['ur5e.inspect_readiness'], kind='inspection')
    return [
        move('move_constrained', 'Move to the registered pose whose pan is negative and final wrist is positive. '
             'Keep the other joints at home; do not choose the positive-pan pose.', 'ur5e.stage_left'),
        move('already_satisfied', 'Place the arm at stage_left. If that goal is already reached, '
             'verify it without sending a trajectory.', 'ur5e.stage_left', initial='ur5e.stage_left', writes=0),
        move('ineffective_command', 'Move to park_right and report the observed outcome. '
             'Do not repeat a dispatched trajectory if it fails.', 'ur5e.park_right', 'FAILURE', 'ineffective'),
        move('partial_command', 'Move to the permitted positive-pan, negative-final-wrist pose. '
             'Verify the whole six-joint goal and do not replay a failed command.', 'ur5e.park_right', 'FAILURE', 'partial'),
        move('missing_prerequisite', 'Move to stage_left only if a current complete joint observation '
             'is available. Otherwise report uncertainty without moving.', 'ur5e.stage_left', 'UNKNOWN', 'missing_motion', writes=0),
        inspect('inspect_healthy', 'Check both controller activation and availability of a fresh complete '
                'joint sample. Report readiness; this task grants no movement permission.'),
        inspect('inspect_inactive', 'Inspect whether the arm is ready: query controller activation '
                'and a fresh joint sample. Report the actual readiness without changing controllers.', 'FAILURE', 'inactive'),
        inspect('inspect_missing_controllers', 'Inspect controller and joint-sample readiness. '
                'Missing evidence means uncertainty, never assumed readiness. Do not move.', 'UNKNOWN', 'controllers'),
        inspect('inspect_missing_joint', 'Check controller activation and fresh joint-state availability. '
                'Report uncertainty if a required observation is unavailable; do not command motion.', 'UNKNOWN', 'joint_state'),
        dict(id='ambiguous_goal', request='Get the arm set for the next activity.', skill=None,
             expected=None, fault=None, initial='ur5e.home', writes=0,
             allowed=['ur5e.inspect_readiness'], kind='clarification'),
    ]


def jobs(backend):
    result = []
    # Every case/repetition is an adjacent pair. Reverse order for the other
    # repetition/backend; rotate case order so repetition is not a simple replay.
    specifications = cases()
    for repetition in (1, 2):
        ordered = specifications if repetition == 1 else specifications[5:] + specifications[:5]
        for index, spec in enumerate(ordered):
            first_macro = (index + repetition + (backend == 'siwc')) % 2 == 0
            order = ('macro', 'primitives') if first_macro else ('primitives', 'macro')
            for condition in order:
                result.append({'id': f'{len(result)+1:02d}-{spec["id"]}-r{repetition}-{condition}',
                    'case': deepcopy(spec), 'repetition': repetition, 'condition': condition})
    return result


def query(spec, condition):
    return (RULES.removesuffix('\nUser: ') + f' Execution condition: {condition}. ' +
        ('select_skill runs the bounded routine and returns evidence; do not repeat completed steps. '
            if condition == 'macro' else
         'select_skill selects only; you manage the needed reads, conditional write and fresh check. ') +
        'Limits: eight charged model calls, 2048 observed generated tokens, 1024 local tokens per '
        'call, ten native acquisitions/commands, sixteen tool attempts, three corrections, '
        '360 seconds and at most one movement dispatch. Joint tolerance 0.025 radians.\nUser: ' + spec['request'])
