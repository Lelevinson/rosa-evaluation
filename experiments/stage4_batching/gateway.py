"""Matched model-selected/algorithm-selected batching over existing ROSA tools.

The same convenience executor is exposed to BOTH arms. Native helpers are traced
individually. Requirement manifests are model arguments, not supplied to the
optimizer by the evaluator. A validation failure executes no hidden repair.
"""
from copy import deepcopy
from dataclasses import asdict
import json
import time
from typing import Literal

from ..jtvr_policy.core import Action, GET_TYPE, Key, Ledger, State, manifest, parse, select, type_key


class Gateway:
    def __init__(self, spec, policy, invoke, costs):
        self.spec, self.policy, self.invoke, self.costs = spec, policy, invoke, costs
        self.ledger = Ledger()
        self.events, self.manifests, self.reports = [], [], []
        self.dispatches = []
        self.illegal = []
        self.allowed_nodes = set(spec['groups'])
        self.completed_writes = set()
        self.selector_seconds = 0.0
        self.max_native_reads = 24

    def reject(self, reason):
        self.illegal.append(reason)
        return {'error': reason, 'native_executions': 0}

    def native(self, action, actor='model_primitive'):
        if len(self.events) >= self.max_native_reads:
            return {'error': 'native_operation_budget_exhausted'}
        node = action.entity.removesuffix('/status') if action.op == 'topic' else action.entity
        if node not in self.allowed_nodes:
            return self.reject('out_of_scope_node')
        names = set(self.spec['groups'][node]['names'])
        if action.op in ('get', 'bulk') and (not action.names or set(action.names) - names):
            return self.reject('out_of_scope_parameter')
        self.ledger.tick += 1
        started_tick = self.ledger.tick
        epochs = {name: self.ledger.epoch(Key(action.entity, 'param:' + name)) for name in action.names}
        started = time.perf_counter()
        caught = None
        try:
            raw = self.invoke(action.tool, action.arguments(), actor)
        except Exception as error:
            caught = error
            raw = {'error': type(error).__name__, 'execution_outcome': 'unknown'}
        parse_started = time.perf_counter()
        parsed = parse(action, raw)
        parser_seconds = time.perf_counter() - parse_started
        self.ledger.tick += 1
        ref = len(self.events)
        for name, value in parsed.items():
            graph = name in ('node_summary', 'service_type', 'topic_details')
            phase = 'graph' if graph else 'final'
            if not graph and any((node, n) not in self.completed_writes
                                 for n in self.spec['groups'][node]['expected_values']):
                phase = 'pre_write'
            key = Key(action.entity, name, phase)
            self.ledger.ingest(key, value, epoch=epochs.get(name[6:], self.ledger.epoch(key)),
                               started=started_tick, raw_ref=ref, tool=action.tool)
        self.events.append({'tool': action.tool, 'args': action.arguments(), 'actor': actor,
            'raw': raw, 'parsed': parsed, 'start_tick': started_tick, 'end_tick': self.ledger.tick,
            'epochs_at_start': epochs, 'wall_seconds': time.perf_counter() - started,
            'parser_seconds': parser_seconds})
        if caught is not None:
            raise caught
        return raw

    def write(self, node_name, param_name, param_value):
        wanted = self.spec['groups'].get(node_name, {}).get('expected_values', {})
        if param_name not in wanted or param_value != str(wanted[param_name]):
            return self.reject('unauthorized_write')
        key = Key(node_name, 'param:' + param_name)
        self.ledger.dispatch_write(key)
        caught = None
        try:
            raw = self.invoke('ros2_param_set', {'node_name': node_name,
                'param_name': param_name, 'param_value': param_value}, 'model_write')
        except Exception as error:
            caught = error
            raw = {'error': type(error).__name__, 'acknowledgment': 'unknown'}
        self.ledger.complete_write(key)
        self.completed_writes.add((node_name, param_name))
        self.events.append({'tool': 'ros2_param_set', 'args': {'node_name': node_name,
            'param_name': param_name, 'param_value': param_value}, 'actor': 'model_write',
            'raw': raw, 'parsed': {}, 'dispatch_epoch': self.ledger.epoch(key),
            'completed_tick': self.ledger.tick})
        if caught is not None:
            raise caught
        return raw

    def acquire(self, node_name, names, report_names, expected_values, strategy):
        request = {'node_name': node_name, 'names': deepcopy(names), 'report_names': deepcopy(report_names),
                   'expected_values': deepcopy(expected_values), 'strategy': strategy}
        group = self.spec['groups'].get(node_name)
        valid = bool(group and type(names) is list and all(type(n) is str for n in names)
            and len(names) == len(set(names)) and set(names) == set(group['names'])
            and type(report_names) is list and set(report_names) == set(group['report_names'])
            and type(expected_values) is dict and expected_values == group['expected_values']
            and all(type(v) is int for v in expected_values.values())
            and strategy in ('direct', 'bulk', 'node_bulk'))
        record = {'request': request, 'valid': valid}
        self.manifests.append(record)
        if not valid:
            return {'error': 'invalid_or_incomplete_requirement_manifest', 'native_executions': 0,
                    'fallback': 'Correct the manifest from the user request or use supported primitive tools.'}
        if any((node_name, n) not in self.completed_writes for n in group['expected_values']):
            record['phase_valid'] = False
            return {'error': 'post_write_phase_not_ready', 'native_executions': 0}
        record['phase_valid'] = True
        rows = []
        for name in names:
            roles = (['task'] if name in report_names else []) + (['verification'] if name in expected_values else [])
            row = {'entity': node_name, 'field': 'param:' + name, 'roles': roles}
            if name in expected_values:
                row['equals'] = expected_values[name]
            rows.append(row)
        include_summary = node_name + ':node_summary' in self.spec['extras'] and strategy == 'node_bulk'
        # B may credit a summary only if the MODEL requested node_bulk. Hidden
        # task extras are not silently inserted into the model's manifest.
        if include_summary:
            rows.append({'entity': node_name, 'field': 'node_summary', 'phase': 'graph', 'roles': ['task']})
        obligations = manifest(rows, rows)
        state = State(obligations, self.ledger, self.costs)
        before = len(self.events)
        if self.policy == 'model_selected':
            if strategy in ('bulk', 'node_bulk'):
                type_evidence = self.ledger.valid(type_key(node_name))
                if strategy == 'node_bulk' and not self.ledger.valid(Key(node_name, 'node_summary', 'graph')):
                    self.native(Action('node', node_name), 'matched_helper')
                elif not type_evidence or type_evidence.value != GET_TYPE:
                    self.native(Action('info', node_name), 'matched_helper')
                type_evidence = self.ledger.valid(type_key(node_name))
                due_names = tuple(n for n in sorted(names) if not self.ledger.valid(Key(node_name, 'param:' + n)))
                if due_names and type_evidence and type_evidence.value == GET_TYPE:
                    self.native(Action('bulk', node_name, due_names), 'matched_helper')
            for name in sorted(names):
                if not self.ledger.valid(Key(node_name, 'param:' + name)):
                    self.native(Action('get', node_name, (name,)), 'matched_helper')
        else:
            while state.due() and len(self.events) < self.max_native_reads:
                decision = select(state, 'batching')
                self.selector_seconds += decision.seconds
                if not decision.fragment:
                    break
                progressed = False
                for action in decision.fragment:
                    if not state.eligible(action, state.bindings()):
                        break
                    due_before = state.due()
                    self.native(action, 'batching_helper')
                    if not self.events[-1].get('parsed') or state.due() == due_before and action.op not in ('node', 'info'):
                        state.failed.add(action.family)
                        break
                    progressed = True
                if not progressed and not state.candidates(state.due()):
                    break
        values = {n: self.ledger.valid(Key(node_name, 'param:' + n)).value
                  for n in names if self.ledger.valid(Key(node_name, 'param:' + n))}
        record.update(native_executions=len(self.events) - before, resolved_names=sorted(values))
        return {'node_name': node_name, 'observed_values': values,
                'unresolved_names': sorted(set(names) - set(values)),
                'native_executions': len(self.events) - before,
                'evidence': [{'tool': e['tool'], 'args': e['args'], 'parsed': e.get('parsed', {})}
                             for e in self.events[before:]],
                'note': 'Read-only evidence. Compare requested targets before reporting.'}

    def call(self, name, **args):
        self.dispatches.append({'name': name, 'args': deepcopy(args)})
        if self.reports:
            return self.reject('tool_after_report')
        if name == 'read_parameter_evidence':
            return self.acquire(**args)
        if name == 'submit_parameter_report':
            self.reports.append({'args': deepcopy(args), 'event_count': len(self.events),
                                 'evidence': [asdict(e) for e in self.ledger.records]})
            return {'report_recorded': True}
        if name == 'ros2_param_set':
            return self.write(**args)
        if name == 'ros2_param_get':
            return self.native(Action('get', args['node_name'], (args['param_name'],)))
        if name == 'ros2_service_call':
            import yaml
            try:
                request = yaml.safe_load(args['request'])
            except yaml.YAMLError:
                return self.reject('invalid_service_request')
            node = args['service_name'].removesuffix('/get_parameters')
            if args['service_name'] != node + '/get_parameters' or args['srv_type'] != GET_TYPE:
                return self.reject('unregistered_service')
            if not isinstance(request, dict) or set(request) != {'names'} or not isinstance(request['names'], list):
                return self.reject('invalid_service_request')
            evidence = self.ledger.valid(type_key(node))
            if not evidence or evidence.value != GET_TYPE:
                return self.reject('type_discovery_required')
            return self.native(Action('bulk', node, tuple(request['names'])))
        if name in ('ros2_service_info', 'ros2_node_info', 'ros2_topic_info'):
            argument = {'ros2_service_info': 'services', 'ros2_node_info': 'nodes', 'ros2_topic_info': 'topics'}[name]
            op = {'ros2_service_info': 'info', 'ros2_node_info': 'node', 'ros2_topic_info': 'topic'}[name]
            combined = {}
            for item in args[argument]:
                entity = item.removesuffix('/get_parameters') if op == 'info' else item
                combined.update(self.native(Action(op, entity)))
            return combined
        return self.reject('unknown_tool')

    def score(self, oracle_values, raw_calls):
        errors, reports = [], self.reports
        report = reports[0] if reports else None
        if len(reports) != 1:
            errors.append('expected_exactly_one_report')
        if self.illegal:
            errors.extend(self.illegal)
        if report:
            values = report['args']['observed_values']
            for node, group in self.spec['groups'].items():
                for name in group['report_names']:
                    evidence = self.ledger.valid(Key(node, 'param:' + name))
                    value = values.get(node, {}).get(name)
                    if type(value) is not int or value != oracle_values[node][name]:
                        errors.append('incorrect_or_missing_report_value')
                    if evidence is None or evidence.value != value:
                        errors.append('unsupported_report_value')
                for name, target in group['expected_values'].items():
                    evidence = self.ledger.valid(Key(node, 'param:' + name))
                    if evidence is None or evidence.value != target or oracle_values[node][name] != target:
                        errors.append('unverified_goal')
                    if (node, name) not in self.completed_writes:
                        errors.append('requested_write_not_attempted')
            for extra in self.spec['extras']:
                entity, field = extra.rsplit(':', 1)
                if extra not in report['args']['acknowledged_details'] or not self.ledger.valid(Key(entity, field, 'graph')):
                    errors.append('missing_detail_evidence')
            if report['args']['outcome'] != 'success':
                errors.append('incorrect_nominal_outcome')
        for call in raw_calls:
            if call['name'] == 'read_parameter_evidence':
                vals = call['args'].get('expected_values', {})
                if not isinstance(vals, dict) or any(type(v) is not int for v in vals.values()):
                    errors.append('raw_manifest_type_error')
            if call['name'] == 'submit_parameter_report':
                vals = call['args'].get('observed_values', {})
                if not isinstance(vals, dict) or any(type(v) is not int for node in vals.values()
                    if isinstance(node, dict) for v in node.values()):
                    errors.append('raw_report_type_error')
        return {'strict_contract_pass': not errors, 'errors': errors,
            'oracle_values': oracle_values, 'manifests': self.manifests,
            'manifest_requests': len(self.manifests), 'valid_manifests': sum(m['valid'] for m in self.manifests),
            'first_manifest_valid': self.manifests[0]['valid'] if self.manifests else None,
            'manifest_union_complete': {m['request']['node_name'] for m in self.manifests if m['valid']} == self.allowed_nodes,
            'manifest_bypassed': not self.manifests, 'native_events': self.events,
            'model_dispatches': self.dispatches, 'reports': self.reports,
            'ledger': [asdict(e) for e in self.ledger.records], 'selector_seconds': self.selector_seconds}


def make_tools(call):
    from langchain_core.tools import tool
    from ..config import checkout
    from rosa.tools import ros2 as originals
    result = []
    # Preserve actual names/schemas/docstrings, substitute only the gateway.
    from langchain_core.tools import StructuredTool
    for name in ('ros2_param_get', 'ros2_param_set', 'ros2_service_info',
                 'ros2_service_call', 'ros2_node_info', 'ros2_topic_info'):
        original = getattr(originals, name)
        def invoke(_name=name, **kwargs):
            return call(_name, **kwargs)
        result.append(StructuredTool.from_function(func=invoke, name=name,
            description=original.description, args_schema=original.args_schema))

    @tool
    def read_parameter_evidence(node_name: str, names: list[str], report_names: list[str],
                                expected_values: dict[str, int],
                                strategy: Literal['direct', 'bulk', 'node_bulk']) -> dict:
        """Declare ALL needed parameter fields and acquire evidence. names is the union of report/verification names. report_names lists report fields. expected_values gives verification targets ({} for read-only). Choose direct, bulk (type + GetParameters), or node_bulk (node info + GetParameters). Both configurations support the same plans and read continuations. Never writes. Invalid/incomplete manifests execute no reads. Missing fields are not filled automatically."""
        return call('read_parameter_evidence', node_name=node_name, names=names,
                    report_names=report_names, expected_values=expected_values, strategy=strategy)

    @tool
    def submit_parameter_report(outcome: Literal['success', 'failure', 'unknown'],
                                observed_values: dict[str, dict[str, int]],
                                acknowledged_details: list[str]) -> dict:
        """Submit one final report of observed values and acquired entity:detail identifiers. Never call tools afterward. Use success only with current required evidence and verified targets."""
        return call('submit_parameter_report', outcome=outcome, observed_values=observed_values,
                    acknowledged_details=acknowledged_details)
    return result + [read_parameter_evidence, submit_parameter_report]
