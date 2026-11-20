"""G1-r1 mock I/O only. No ROSA internals, model routing, credentials or oracle cache reuse.

Independence here means distinct actor/observer state, channels and record streams
over one authoritative world. It does not mean different authors or sensors.
"""
from copy import deepcopy
import math
import threading
import time


DOMAINS = {
    'arm': {
        'node': '/g1_arm/joints', 'initial': {'yaw': 0.0, 'pitch': 0.0},
        'target': {'yaw': -.18, 'pitch': .11}, 'units': {'yaw': 'radian', 'pitch': 'radian'},
        'checks': [('guard', 'guard_closed'), ('joint_sample', 'joint_sample_fresh'),
                   ('brake', 'brake_released'), ('thermal', 'temperature_safe'),
                   ('workspace', 'workspace_clear'), ('tool_mount', 'tool_mount_locked')],
        'ids': ['arm.cedar', 'arm.quartz', 'arm.ember', 'arm.lumen', 'arm.cobalt'],
        'raw': {'temperature_c': 34.0, 'joint_sample_age_s': .04}},
    'base': {
        'node': '/g1_base/pose', 'initial': {'x_m': 0.0, 'y_m': 0.0, 'heading_fraction': 0.0},
        'target': {'x_m': 1.2, 'y_m': -.6, 'heading_fraction': .25},
        'units': {'x_m': 'metre', 'y_m': 'metre', 'heading_fraction': 'fraction of full turn'},
        'checks': [('localization', 'pose_fix_valid'), ('map_lease', 'map_lease_valid'),
                   ('energy', 'reserve_sufficient'), ('path', 'path_clear'),
                   ('odometry', 'odometry_consistent'), ('traction', 'traction_sufficient')],
        'ids': ['base.zephyr', 'base.jasper', 'base.mica', 'base.onyx', 'base.sable'],
        'raw': {'battery_fraction': .76, 'clearance_m': 1.8, 'map_revision': 7,
                'lease_map_revision': 7, 'localization_confidence_fraction': .98,
                'odometry_error_m': .01, 'slip_fraction': .01}},
}


class MockWorld:
    """Authority owns physical truth; each channel response is a detached value."""
    def __init__(self, domain, *, initial=None, false_source=None, write_effect='normal', write_authorized=True):
        if domain not in DOMAINS:
            raise ValueError('unknown_domain')
        if write_effect not in ('normal', 'ineffective', 'partial'):
            raise ValueError('unknown_write_effect')
        self.domain, self._spec = domain, deepcopy(DOMAINS[domain])
        self._pose = deepcopy(self._spec['initial'] if initial is None else initial)
        self._validate_pose(self._pose)
        self._sources = {source: {field: source != false_source} for source, field in self._spec['checks']}
        if false_source is not None and false_source not in self._sources:
            raise ValueError('unknown_false_source')
        self._raw, self._write_effect = deepcopy(self._spec['raw']), write_effect
        if domain == 'base':
            # Mobile sources derive from typed quantities, rather than renamed arm flags.
            false_values = {'localization': ('localization_confidence_fraction', .1),
                            'map_lease': ('lease_map_revision', 6), 'energy': ('battery_fraction', .1),
                            'path': ('clearance_m', .1), 'odometry': ('odometry_error_m', .15),
                            'traction': ('slip_fraction', .3)}
            if false_source is not None:
                key, value = false_values[false_source]
                self._raw[key] = value
            self._refresh_base_sources()
        self._write_authorized = write_authorized
        self._records, self._revision, self._dispatches = [], 0, 0
        self._lock = threading.RLock()

    def _refresh_base_sources(self):
        raw = self._raw
        flags = {'localization': raw['localization_confidence_fraction'] >= .8,
                 'map_lease': raw['lease_map_revision'] == raw['map_revision'],
                 'energy': raw['battery_fraction'] >= .2,
                 'path': raw['clearance_m'] >= .5,
                 'odometry': raw['odometry_error_m'] <= .05,
                 'traction': raw['slip_fraction'] <= .1}
        self._sources = {source: {field: flags[source]} for source, field in self._spec['checks']}

    def _validate_pose(self, values):
        if set(values) != set(self._spec['initial']) or any(type(v) not in (int, float) or not math.isfinite(v) for v in values.values()):
            raise ValueError('complete_finite_pose_required')
        if self.domain == 'arm' and any(abs(v) > .6 for v in values.values()):
            raise ValueError('arm_range_exceeded')
        if self.domain == 'base' and (any(abs(values[k]) > 3 for k in ('x_m','y_m')) or not 0 <= values['heading_fraction'] < 1):
            raise ValueError('base_range_exceeded')

    def actor_channel(self):
        return ActorChannel(self)

    def observer_channel(self):
        return ObserverChannel(self)

    def _actor_pose(self, node, fields):
        with self._lock:
            if node != self._spec['node'] or not set(fields) <= set(self._pose):
                raise ValueError('pose_scope_invalid')
            self._records.append({'kind': 'actor_pose_acquisition', 'revision': self._revision, 'fields': list(fields)})
            if self.domain == 'base' and not self._sources['localization']['pose_fix_valid']:
                raise TimeoutError('localization_fix_invalid')
            return {name: self._pose[name] for name in fields}

    def _actor_group(self, source, fields):
        with self._lock:
            if source not in self._sources or set(fields) != set(self._sources[source]):
                raise ValueError('source_scope_invalid')
            self._records.append({'kind': 'actor_source_acquisition', 'source': source, 'revision': self._revision})
            return deepcopy(self._sources[source])

    def _command(self, node, values):
        with self._lock:
            if not self._write_authorized:
                raise ValueError('movement_not_authorized_for_this_request')
            if node != self._spec['node']:
                raise ValueError('write_scope_invalid')
            self._validate_pose(values)
            if self._dispatches:
                raise RuntimeError('world_single_dispatch_limit')
            self._dispatches += 1
            old_pose = deepcopy(self._pose)
            actual = deepcopy(values)
            if self._write_effect == 'partial':
                if self.domain == 'arm':
                    actual = {'pitch': values['pitch']}  # yaw remains off target
                else:
                    actual = {k: values[k] for k in ('x_m','y_m')}  # heading unchanged
            if self._write_effect != 'ineffective':
                self._pose.update(actual)
            if self.domain == 'base':
                distance = math.hypot(self._pose['x_m']-old_pose['x_m'], self._pose['y_m']-old_pose['y_m'])
                self._raw['battery_fraction'] = max(0.0, self._raw['battery_fraction'] - .01*distance)
                self._refresh_base_sources()
            self._revision += 1
            self._records.append({'kind': 'movement_dispatch', 'requested': deepcopy(values),
                                  'domain_command': 'goto' if self.domain == 'base' else 'joint_command',
                                  'effect': self._write_effect, 'revision': self._revision})
            return {'accepted': True, 'meaning': 'acceptance does not verify the outcome'}

    def _observe(self):
        with self._lock:
            snapshot = {'domain': self.domain, 'node': self._spec['node'], 'pose': self._pose,
                        'sources': self._sources, 'raw_quantities': self._raw,
                        'units': self._spec['units'], 'revision': self._revision, 'dispatches': self._dispatches}
            # The observer never reads ActorTransport.state or ActorTransport.records.
            return deepcopy(snapshot)

    def records(self):
        with self._lock:
            return deepcopy(self._records)


class ActorChannel:
    """Distinct actor-facing transport interface; no observer snapshots."""
    def __init__(self, world):
        self._world = world
    def read_pose(self, node, fields):
        return self._world._actor_pose(node, fields)
    def read_source(self, source, fields):
        return self._world._actor_group(source, fields)
    def command(self, node, values):
        return self._world._command(node, values)


class ObserverChannel:
    """Read-only ground-truth interface, separate from the actor channel."""
    def __init__(self, world):
        self._world = world
    def observe(self):
        return self._world._observe()


class ActorTransport:
    """Public StateTransport + inspection read_group, with actor-only faults.

    Each read_group performs one source acquisition. write/validate_write do not
    secretly acquire prerequisite sources. The ROSA adapter owns native metering.
    """
    requires_observation = True
    def __init__(self, channel, domain, *, pose_unavailable=False, unavailable_source=None,
                 corrupt_read=False, drop_ack=False, write_authorized=True):
        self._channel, self.domain = channel, domain
        self._pose_unavailable, self._unavailable_source = pose_unavailable, unavailable_source
        self._corrupt_read, self._drop_ack = corrupt_read, drop_ack
        self._write_authorized = write_authorized
        self.state, self.records, self.writes = {}, [], 0

    def _record(self, kind, **values):
        self.records.append(deepcopy({'kind': kind, 'monotonic': time.monotonic(), **values}))

    def read(self, node, fields):
        if self._pose_unavailable:
            self._record('pose_read_timeout', node=node, fields=list(fields))
            raise TimeoutError('actor_pose_unavailable')
        try:
            values = self._channel.read_pose(node, fields)
        except TimeoutError:
            self._record('pose_read_timeout', node=node, fields=list(fields))
            raise
        if self._corrupt_read:
            values = {name: value + .1 for name, value in values.items()}
        self.state[node] = deepcopy(values)
        self._record('pose_read', node=node, values=values, corrupted=self._corrupt_read)
        return deepcopy(values)

    def read_group(self, source, fields):
        if source == self._unavailable_source:
            self._record('source_read_timeout', source=source, fields=list(fields))
            raise TimeoutError('actor_source_unavailable')
        try:
            values = self._channel.read_source(source, fields)
        except TimeoutError:
            self._record('source_read_timeout', source=source, fields=list(fields))
            raise
        self.state[source] = deepcopy(values)
        self._record('source_read', source=source, values=values)
        return deepcopy(values)

    def validate_write(self, node, values):
        spec = DOMAINS[self.domain]
        if not self._write_authorized:
            return 'movement is not authorized for this request'
        if self.writes:
            return 'only one dispatch is permitted'
        if node != spec['node'] or values != spec['target']:
            return 'registered complete target required'

    def write(self, node, values):
        error = self.validate_write(node, values)
        if error:
            raise ValueError(error)
        self.writes += 1
        receipt = self._channel.command(node, deepcopy(values))
        self._record('write', node=node, requested=values, receipt_available=not self._drop_ack)
        if self._drop_ack:
            raise TimeoutError('acknowledgement_lost_after_dispatch')
        return deepcopy(receipt)


class ObserverTransport:
    """Separate state/cache and records over its own read-only channel."""
    def __init__(self, channel):
        self._channel, self.state, self.records = channel, {}, []
    def observe(self):
        payload = self._channel.observe()
        self.state = deepcopy(payload)
        self.records.append(deepcopy({'kind': 'observer_read', 'monotonic': time.monotonic(), 'snapshot': payload}))
        return deepcopy(payload)


def create_world(domain, **faults):
    world_keys = {'initial','false_source','write_effect','write_authorized'}
    world = MockWorld(domain, **{k:v for k,v in faults.items() if k in world_keys})
    actor = ActorTransport(world.actor_channel(), domain, **{k:v for k,v in faults.items() if k not in world_keys},
                           write_authorized=faults.get('write_authorized', True))
    observer = ObserverTransport(world.observer_channel())
    return world, actor, observer
