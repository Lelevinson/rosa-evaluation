"""Public-tool gateway, conservative cache, and separately attributed interventions."""
from collections import Counter
from copy import deepcopy
import json
import multiprocessing
import time
from .world import serve, READS, ACTIONS

DEPENDENCIES = {'pick_object': ('observe_robot', 'read_permissions', 'locate_object'),
                'place_object': ('observe_robot', 'read_permissions', 'inspect_target')}


class InterventionStop(BaseException):
    """A declared recovery intervention, not an unreported model success."""


class Client:
    def __init__(self, spec, policy='none', intervention='original', legacy=False):
        if policy not in ('none', 'conservative', 'eager', 'jtvr'):
            raise ValueError(policy)
        context = multiprocessing.get_context('spawn')
        self.agent, child = context.Pipe()
        self.evaluator, child_eval = context.Pipe()
        self.process = context.Process(target=serve, args=(child, child_eval, spec, legacy), daemon=True)
        self.process.start()
        child.close()
        child_eval.close()
        self.policy, self.intervention = policy, intervention
        self.entries = {}
        self.metrics = {'sensor_backend_reads': 0, 'cache_hits': 0, 'cache_validation_calls': 0,
                        'sensor_backend_ms': 0.0, 'cache_policy_ms': 0.0, 'bytes_read': 0,
                        'action_invalidations': 0, 'automatic_verifications': 0,
                        'system_reports': 0, 'guard_stops': 0, 'context_acquisitions': 0}
        self.dispatches = []
        self.last_pose = self.last_verification = None
        self.last_accepted = None
        self.attempts = Counter()

    def request(self, pipe, value):
        pipe.send(value)
        if not pipe.poll(15):
            raise TimeoutError('phase4_ipc_deadline')
        return pipe.recv()

    def invalidate(self, events):
        names = {n for event in events for n in event.get('invalidates', [])}
        for key in list(self.entries):
            if key[0] in names:
                del self.entries[key]

    def _call(self, name, args, actor='model'):
        clock = self.request(self.agent, {'operation': 'advance'})
        started = time.perf_counter()
        self.invalidate(clock['events'])
        key = (name, json.dumps(args, sort_keys=True))
        eligible = self.policy != 'none' and name in READS and clock['notifications_reliable']
        self.metrics['cache_validation_calls'] += int(name in READS and self.policy != 'none')
        entry = self.entries.get(key)
        cached = bool(eligible and entry and 0 <= clock['tick'] - entry[0] < 5)
        self.metrics['cache_policy_ms'] += (time.perf_counter() - started) * 1000
        payload = {'operation': 'cached_observation' if cached else 'tool',
                   'name': name, 'args': args, 'actor': actor}
        if cached:
            payload['value'] = entry[1]
        started = time.perf_counter()
        response = self.request(self.agent, payload)
        value = response['output']
        if name in READS:
            if cached:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['sensor_backend_reads'] += 1
                self.metrics['sensor_backend_ms'] += (time.perf_counter() - started) * 1000
                self.metrics['bytes_read'] += len(json.dumps(value).encode())
            if eligible and value.get('status') != 'UNKNOWN' and not value.get('error'):
                self.entries[key] = (clock['tick'], deepcopy(value))
        self.invalidate(response['events'])
        if name in ACTIONS:
            self.entries.clear()
            self.metrics['action_invalidations'] += 1
            self.last_verification = None
            if value.get('accepted'):
                self.last_accepted = name
        elif name == 'locate_object':
            self.last_pose = value
        elif name == 'verify_goal':
            self.last_verification = value
        return deepcopy(value), response['events']

    def call(self, name, **args):
        # This list records model-visible dispatches, not nested observation work.
        self.dispatches.append({'name': name, 'args': deepcopy(args)})
        if name == 'acquire_context':
            action = args.get('action')
            if action not in DEPENDENCIES or self.policy not in ('eager', 'jtvr'):
                return {'error': 'invalid_context_request'}
            self.metrics['context_acquisitions'] += 1
            names = tuple(sorted(READS)) if self.policy == 'eager' else DEPENDENCIES[action]
            values = {}
            for read in names:
                read_args = ({'object_id': args['object_id']} if read == 'locate_object' else
                             {'target': args['target']} if read == 'inspect_target' else {})
                value, events = self._call(read, read_args, actor='context_manager')
                values[read] = value
                # Refresh only when public notifications establish invalidation.
                for event in events:
                    for invalid in event.get('invalidates', []):
                        if invalid in values:
                            refresh_args = ({'object_id': args['object_id']} if invalid == 'locate_object' else
                                            {'target': args['target']} if invalid == 'inspect_target' else {})
                            values[invalid] = self._call(invalid, refresh_args, actor='context_manager')[0]
            return {'action': action, 'observations': values,
                    'note': 'Information only. No action, verification, retry, or report was performed.'}
        if name in ACTIONS and self.intervention == 'bounded_recovery':
            key = (name, args.get('object_id'), args.get('arm'))
            if self.attempts[key] >= 1:
                unknown = bool(self.last_pose and self.last_pose.get('status') == 'UNKNOWN')
                verified_failed_pick = (self.last_accepted == 'pick_object' and self.last_verification
                    and self.last_verification.get('execution_terminal') and not self.last_verification.get('holding'))
                if unknown or verified_failed_pick:
                    if not self.last_verification:
                        self._call('verify_goal', {}, actor='orchestrator')
                        self.metrics['automatic_verifications'] += 1
                    outcome = 'unknown' if unknown else 'failure'
                    self._call('submit_report', {'outcome': outcome, 'battery_percent': -1}, actor='orchestrator')
                    self.metrics['system_reports'] += 1
                    self.metrics['guard_stops'] += 1
                    raise InterventionStop('bounded_recovery_stopped_and_reported')
            self.attempts[key] += 1
        if name == 'submit_report' and self.intervention == 'enforce_verification' and not self.last_verification and args.get('outcome') != 'refused':
            self._call('verify_goal', {}, actor='orchestrator')
            self.metrics['automatic_verifications'] += 1
        return self._call(name, args)[0]

    def score(self, raw_model_tool_calls=None):
        return self.request(self.evaluator, {'operation': 'score', 'metrics': deepcopy(self.metrics),
                                           'raw_model_tool_calls': raw_model_tool_calls})

    def close(self):
        if self.process.is_alive():
            try:
                self.request(self.evaluator, {'operation': 'close'})
            except (TimeoutError, OSError, EOFError):
                pass
        self.process.join(2)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(2)
        self.agent.close()
        self.evaluator.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
