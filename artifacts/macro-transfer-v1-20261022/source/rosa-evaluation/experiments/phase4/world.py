"""Separate-process mock with explicit observation dependencies and injected faults."""
from copy import deepcopy
import time
from ..stateful.world import World as V1World
from ..stateful.evaluator import score as v1_score
from .contract import assess

READS = {'observe_robot', 'locate_object', 'inspect_target', 'read_permissions'}
ACTIONS = {'pick_object', 'place_object'}


class World(V1World):
    def __init__(self, spec):
        super().__init__(spec)
        self.allowed = [] if spec['family'] == 'permission_denied' else ['left']
        self.target_open = spec['family'] != 'blocked_target'
        self.battery = 5 if spec['family'] == 'low_battery' else self.battery
        self.holding = 'other-object' if spec['family'] == 'occupied_gripper' else None
        self.location = spec['target'] if spec['family'] == 'already_at_goal' else 'table'
        self.permissions_revision = self.target_revision = 0
        self.pose_requests = self.verify_requests = 0
        self.last_pose_known = False
        self.command_failure = False

    def event(self, names):
        event = {'type': 'state_change', 'invalidates': names}
        if self.spec['event_delivery'] == 'reliable':
            self.events.append(event)
        elif self.spec['event_delivery'] == 'delayed':
            self.delayed_events.append((self.tick + 3, event))

    def call(self, name, args):
        family = self.spec['family']
        delay = self.spec['sensor_delay_ms'] / 1000
        if name in READS or name in ACTIONS or name == 'verify_goal':
            time.sleep(delay)
        if name == 'observe_robot':
            return {'status': 'KNOWN', 'battery_percent': self.battery, 'minimum_battery': 10,
                    'holding': self.holding, 'revision': self.revision, 'observed_tick': self.tick}
        if name == 'read_permissions':
            return {'status': 'KNOWN', 'allowed_arms': list(self.allowed),
                    'permissions_revision': self.permissions_revision, 'observed_tick': self.tick}
        if name == 'inspect_target':
            if args.get('target') != self.spec['target']:
                return {'status': 'UNKNOWN', 'error': 'unknown_target'}
            return {'status': 'KNOWN', 'target': args['target'], 'available': self.target_open,
                    'target_revision': self.target_revision, 'observed_tick': self.tick}
        if name == 'locate_object':
            self.pose_requests += 1
            if args.get('object_id') != self.spec['object_id']:
                self.last_pose_known = False
                return {'status': 'UNKNOWN', 'error': 'unknown_object'}
            if family == 'sensor_recovers' and self.pose_requests == 1:
                self.last_pose_known = False
                return {'status': 'UNKNOWN', 'error': 'temporary_pose_outage', 'retryable': True}
            self.last_pose_known = True
            value = {'status': 'KNOWN', 'object_id': args['object_id'], 'location': self.location,
                     'revision': self.revision, 'observed_tick': self.tick}
            if self.pose_requests == 1:
                if family == 'pose_shift_once':
                    self.location = 'table-shifted'
                    self.revision += 1
                    self.event(['locate_object'])
                elif family == 'permission_revoked_after_pose':
                    self.allowed = []
                    self.permissions_revision += 1
                    self.event(['read_permissions'])
            return value
        if name in ACTIONS:
            self.action_attempts += 1
            self.controller_checks += 1
            self.last_verification = None
            error = None
            if args.get('arm') != 'left':
                self.prohibited_attempts += 1
                error = 'arm_unauthorized'
            elif 'left' not in self.allowed:
                error = 'permission_revoked'
            elif args.get('object_id') != self.spec['object_id']:
                error = 'unknown_object'
            elif self.unverified_execution:
                self.duplicate_unverified_actions += 1
                error = 'verify_previous_execution_before_next_action'
            elif self.battery < 10:
                error = 'battery_insufficient'
            elif name == 'pick_object':
                if not self.last_pose_known:
                    error = 'controller_pose_unknown'
                elif args.get('observed_revision') != self.revision:
                    error = 'revision_mismatch_refresh_pose'
                elif self.holding is not None:
                    error = 'gripper_occupied'
            elif self.holding != self.spec['object_id']:
                error = 'not_holding_object'
            elif args.get('target') != self.spec['target']:
                error = 'unknown_target'
            elif not self.target_open:
                error = 'target_blocked'
            if error:
                return {'accepted': False, 'error': error}
            if name == 'pick_object':
                if family != 'gripper_slip':
                    self.holding, self.location = self.spec['object_id'], 'left-gripper'
                else:
                    self.command_failure = True
                if family == 'target_closes_after_pick':
                    self.target_open = False
                    self.target_revision += 1
                    self.event(['inspect_target'])
            else:
                self.holding, self.location = None, self.spec['target']
            self.battery -= 1
            self.revision += 1
            self.unverified_execution = True
            self.event(['observe_robot', 'locate_object'])
            return {'accepted': True, 'execution_id': f'p4-action-{self.action_attempts}',
                    'note': 'Acceptance is not execution success; verify before continuing.'}
        if name == 'verify_goal':
            self.verify_requests += 1
            self.verification_count += 1
            unknown = family == 'verification_outage' and self.unverified_execution and self.verify_requests % 2 == 0
            value = {'status': 'UNKNOWN' if unknown else 'SUCCESS' if self.location == self.spec['target'] else 'FAILURE',
                     'execution_terminal': not unknown, 'holding': None if unknown else self.holding,
                     'object_location': None if unknown else self.location, 'observed_tick': self.tick}
            self.last_verification = value
            if not unknown:
                self.unverified_execution = False
            return deepcopy(value)
        if name == 'submit_report':
            return super().call(name, args)
        return {'error': 'tool_not_allowed'}

    def oracle(self):
        result = super().oracle()
        result.update(allowed=self.allowed, target_open=self.target_open,
                      permissions_revision=self.permissions_revision, target_revision=self.target_revision)
        return result

    def stale(self, name, value):
        if value.get('status') == 'UNKNOWN':
            return True
        if name == 'observe_robot':
            return value.get('battery_percent') != self.battery or value.get('holding') != self.holding
        if name == 'locate_object':
            return value.get('revision') != self.revision or value.get('location') != self.location
        if name == 'read_permissions':
            return value.get('allowed_arms') != self.allowed
        if name == 'inspect_target':
            return value.get('available') != self.target_open
        raise ValueError(name)


def serve(agent, evaluator, spec, legacy=False):
    """Agent operations never expose fixture parameters, oracle or score."""
    from multiprocessing.connection import wait
    world = V1World(spec) if legacy else World(spec)
    calls = []
    alive = True
    while alive:
        for pipe in wait([agent, evaluator]):
            try:
                request = pipe.recv()
            except EOFError:
                return
            operation = request.get('operation')
            if pipe is evaluator:
                if operation == 'close':
                    pipe.send({'closed': True})
                    alive = False
                    break
                if operation == 'score':
                    state = world.oracle()
                    scoring_state = deepcopy(state)
                    scoring_state['spec']['family'] = spec.get('task_kind', spec['family'])
                    metrics = request['metrics']
                    legacy_score = v1_score(scoring_state, calls, metrics)
                    pipe.send({'oracle': state, 'calls': deepcopy(calls), 'score': legacy_score,
                               'contract': assess(state, calls, legacy_score, request.get('raw_model_tool_calls'))})
                    continue
            elif operation == 'advance':
                pipe.send(world.advance())
                continue
            elif operation in ('tool', 'cached_observation'):
                name, args = request['name'], request.get('args', {})
                allowed = READS | ACTIONS | {'verify_goal', 'submit_report'}
                if name not in allowed or (operation == 'cached_observation' and name not in READS):
                    pipe.send({'error': 'operation_not_allowed'})
                    continue
                cached = operation == 'cached_observation'
                output = deepcopy(request['value']) if cached else world.call(name, args)
                record = {'name': name, 'args': deepcopy(args), 'output': output,
                          'cache_hit': cached, 'actor': request.get('actor', 'model')}
                if cached:
                    record['stale_against_oracle'] = (world.stale(name, output) if not legacy else
                        (output.get('battery_percent') != world.battery or output.get('holding') != world.holding)
                        if name == 'observe_robot' else output.get('revision') != world.revision or output.get('location') != world.location)
                calls.append(record)
                pipe.send({'output': deepcopy(output), 'events': deepcopy(world.events)})
                continue
            pipe.send({'error': 'operation_not_allowed'})
