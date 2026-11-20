"""Fixed six-case pilot; development-informed cases, not a held-out benchmark."""
from copy import deepcopy

SKILLS = {
    'inspect_east': {'/bench_arm': {'yaw': .27, 'pitch': -.16}},
    'inspect_west': {'/bench_arm': {'yaw': -.23, 'pitch': .21}},
}
INITIAL = {'/bench_arm': {'yaw': .03, 'pitch': -.04}}
CASES = [
    {'id': 'east_healthy', 'goal': 'Use the eastern inspection station.', 'skill': 'inspect_east', 'fault': None, 'expected': 'SUCCESS'},
    {'id': 'west_healthy', 'goal': 'Use the western inspection station.', 'skill': 'inspect_west', 'fault': None, 'expected': 'SUCCESS'},
    {'id': 'west_ineffective', 'goal': 'Use the western inspection station.', 'skill': 'inspect_west', 'fault': 'drop', 'expected': 'FAILURE'},
    {'id': 'east_unavailable', 'goal': 'Use the eastern inspection station.', 'skill': 'inspect_east', 'fault': 'missing', 'expected': 'UNKNOWN'},
    {'id': 'west_outcome_unavailable', 'goal': 'Use the western inspection station.', 'skill': 'inspect_west', 'fault': 'post_missing', 'expected': 'UNKNOWN'},
    {'id': 'east_controller_busy', 'goal': 'Use the eastern inspection station.', 'skill': 'inspect_east', 'fault': 'reject', 'expected': 'FAILURE'},
]
LIMITS = {'model_calls': 8, 'seconds': 180, 'native': 10, 'tools': 16,
          'invalid_corrections': 3, 'writes': 1, 'output_threshold': 2048,
          'local_per_call': 1024, 'backend_request_cap': 96, 'backend_seconds': 2700}


def jobs():
    return [{'case': deepcopy(spec), 'program': program} for index, spec in enumerate(CASES)
            for program in ((False, True) if index % 2 == 0 else (True, False))]


def query(spec, program):
    import json
    mode = ('After select_skill ROSA automatically reads, conditionally writes, and verifies. '
            'Inspect its result; after escalation you retain the same bounded primitives.' if program else
            'After select_skill you must request the read, necessary write, and fresh verification yourself.')
    return (
        'Execute this request using only the registered tools. ' + spec['goal'] + '\n'
        'Public user-authorized catalogue: ' + json.dumps(SKILLS, sort_keys=True) + '\n'
        'Choose the skill matching the requested station; the other station is not a substitute for this task. '
        'Select exactly once, before other tools. Both catalogue entries are permitted, but only the requested goal earns completion. '
        + mode + '\n'
        'Request exactly one complete tool call per response. Read current state before any write; '
        'unavailable observations cannot authorize movement. At most one dispatched write. '
        'Command acceptance is not success. Acquire fresh post-write read or verify evidence. '
        'If an accepted command has no effect, do not repeat it. If prerequisites reject a command, '
        'use fresh evidence to report the outcome or stop; do not invent a fallback destination. '
        'Report SUCCESS only when all selected targets are freshly observed within tolerance 0.01; '
        'FAILURE for known off-target state; UNKNOWN for unavailable evidence. '
        'Use submit_report with the exact node-keyed observed_values; preserve null. '
        'An accepted report ends the task automatically. Do not claim an unobserved success. '
        'Limits: 8 model requests, 16 tool attempts including program steps, 10 native operations, '
        '3 invalid corrections, 1 dispatched write, 180 seconds. '
        'Model output is cumulatively metered; no inference retry or truncation continuation is added.'
    )


class PilotTransport:
    requires_observation = True

    def __init__(self, spec):
        self._fault = spec['fault']
        self.values = deepcopy(INITIAL)
        self.records = []
        self.writes = 0

    def read(self, node, names):
        missing = self._fault == 'missing' or (self._fault == 'post_missing' and self.writes > 0)
        self.records.append({'kind': 'read', 'node': node, 'missing': missing})
        if missing:
            raise TimeoutError('observation_unavailable')
        return {key: self.values[node][key] for key in names}

    def validate_write(self, node, values):
        if set(values) != {'yaw', 'pitch'} or any(abs(v) > .5 for v in values.values()):
            return 'complete yaw and pitch within [-0.5,0.5] required'
        if self._fault == 'reject':
            return 'controller unavailable; no command dispatched'

    def write(self, node, values):
        self.writes += 1
        self.records.append({'kind': 'write', 'node': node, 'requested': deepcopy(values)})
        if self._fault != 'drop':
            self.values[node].update(values)
        return {'accepted': True, 'meaning': 'request accepted, outcome unverified'}
