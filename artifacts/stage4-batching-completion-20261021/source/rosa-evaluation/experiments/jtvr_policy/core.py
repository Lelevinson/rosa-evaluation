"""Shared contracts, conservative evidence and three policy-only selectors.

Hypothetical coverage is represented by sets, never by fabricated values in the
real ledger. All selectors have the same candidates, failed-provider records,
parsers, batch bindings and bounded read-continuation runner.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
import json
import math
import re
import time
from typing import Any

GET_TYPE = 'rcl_interfaces/srv/GetParameters'
TOOLS = {'get': 'ros2_param_get', 'info': 'ros2_service_info',
         'node': 'ros2_node_info', 'bulk': 'ros2_service_call',
         'topic': 'ros2_topic_info'}


@dataclass(frozen=True, order=True)
class Key:
    entity: str
    field: str
    phase: str = 'final'


@dataclass(frozen=True)
class Obligation:
    key: Key
    roles: frozenset[str]
    equals: int | None = None


def manifest(requirements: list[dict], expected: list[dict]) -> list[Obligation]:
    """Strict validator for our supported annotated templates, not arbitrary NLP.

    The later model-generated manifest must satisfy this same task contract.
    Missing fields/roles, changed targets, expanded scope and contradictory
    duplicates cause explicit fallback rather than optimizing a wrong manifest.
    """
    def compile_rows(rows):
        result = {}
        for row in rows:
            if set(row) - {'entity', 'field', 'phase', 'roles', 'equals'}:
                raise ValueError('unknown_manifest_property')
            entity, name, phase = row['entity'], row['field'], row.get('phase', 'final')
            if not all(type(x) is str and x for x in (entity, name, phase)):
                raise ValueError('invalid_key')
            roles = row['roles']
            if not isinstance(roles, list) or not roles or set(roles) - {'task', 'verification'}:
                raise ValueError('invalid_roles')
            target = row.get('equals')
            if target is not None and type(target) is not int:
                raise ValueError('invalid_predicate')
            key = Key(entity, name, phase)
            if key in result:
                old = result[key]
                if old.equals != target:
                    raise ValueError('contradictory_predicate')
                result[key] = Obligation(key, old.roles | frozenset(roles), target)
            else:
                result[key] = Obligation(key, frozenset(roles), target)
        return result
    actual, truth = compile_rows(requirements), compile_rows(expected)
    if actual != truth:
        raise ValueError('manifest_does_not_match_supported_task_contract')
    return [actual[k] for k in sorted(actual)]


@dataclass
class Evidence:
    key: Key
    value: Any
    epoch: int
    started: int
    ended: int
    raw_ref: int
    tool: str
    status: str = 'VALID'
    parser_version: str = 'jtvr-scoped-cli-v1'


@dataclass
class Ledger:
    run_id: str = 'unit'
    tick: int = 0
    epochs: dict[tuple[str, str], int] = field(default_factory=dict)
    records: list[Evidence] = field(default_factory=list)
    pending: set[tuple[str, str]] = field(default_factory=set)
    write_barriers: dict[tuple[str, str], int] = field(default_factory=dict)

    def epoch(self, key):
        return self.epochs.get((key.entity, key.field), 0)

    def valid(self, key):
        age_limit = 64 if key.phase == 'graph' else 32
        for evidence in reversed(self.records):
            if evidence.key == key and evidence.status == 'VALID':
                if evidence.epoch != self.epoch(key) or self.tick - evidence.ended > age_limit:
                    continue
                if (key.entity, key.field) in self.pending:
                    continue
                return evidence
        return None

    def dispatch_write(self, key):
        pair = key.entity, key.field
        self.tick += 1
        self.epochs[pair] = self.epoch(key) + 1
        self.pending.add(pair)
        for evidence in self.records:
            if (evidence.key.entity, evidence.key.field) == pair:
                evidence.status = 'INVALID'

    def complete_write(self, key):
        self.tick += 1
        pair = key.entity, key.field
        self.pending.discard(pair)
        self.write_barriers[pair] = self.tick

    def ingest(self, key, value, *, epoch, started, raw_ref, tool):
        pair = key.entity, key.field
        valid = (epoch == self.epoch(key) and pair not in self.pending
                 and started >= self.write_barriers.get(pair, 0))
        item = Evidence(key, value, epoch, started, self.tick, raw_ref, tool,
                        'VALID' if valid else 'INVALID')
        self.records.append(item)
        return valid


@dataclass(frozen=True)
class Action:
    op: str
    entity: str
    names: tuple[str, ...] = ()

    @property
    def tool(self):
        return TOOLS[self.op]

    @property
    def identity(self):
        return json.dumps([self.op, self.entity, self.names], separators=(',', ':'))

    @property
    def family(self):
        # Failed bulk responses disable bulk for this node for this episode.
        return self.op, self.entity, () if self.op == 'bulk' else self.names

    def arguments(self):
        if self.op == 'get':
            return {'node_name': self.entity, 'param_name': self.names[0]}
        if self.op == 'info':
            return {'services': [self.entity + '/get_parameters']}
        if self.op == 'node':
            return {'nodes': [self.entity]}
        if self.op == 'topic':
            return {'topics': [self.entity]}
        if self.op == 'bulk':
            if any(re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', n) is None for n in self.names):
                raise ValueError('unregistered_parameter_name')
            return {'service_name': self.entity + '/get_parameters', 'srv_type': GET_TYPE,
                    'request': '{names: [' + ', '.join(self.names) + ']}' }
        raise ValueError('unsupported_action')


def type_key(node):
    return Key(node, 'service_type', 'graph')


@dataclass
class State:
    obligations: list[Obligation]
    ledger: Ledger
    costs: dict[str, float]
    failed: set[tuple] = field(default_factory=set)
    strict_discovery: bool = True

    def due(self):
        return {o.key for o in self.obligations if self.ledger.valid(o.key) is None}

    def bindings(self):
        return {o.key for o in self.obligations if self.ledger.valid(o.key)} | {
            type_key(n) for n in {o.key.entity for o in self.obligations}
            if self.ledger.valid(type_key(n)) and self.ledger.valid(type_key(n)).value == GET_TYPE}

    def cost(self, action):
        return self.costs[action.tool]

    def candidates(self, due):
        result = set()
        for node in sorted({k.entity for k in due}):
            keys = {k for k in due if k.entity == node}
            names = tuple(sorted(k.field[6:] for k in keys if k.field.startswith('param:')))
            if names:
                result.update(Action('get', node, (n,)) for n in names)
                result.add(Action('bulk', node, names))
                known = self.ledger.valid(type_key(node))
                if known is None:
                    result.add(Action('info', node))
                    result.add(Action('node', node))
            if any(k.field == 'node_summary' for k in keys):
                result.add(Action('node', node))
            if any(k.field == 'service_type' for k in keys):
                result.add(Action('info', node))
                result.add(Action('node', node))
            if any(k.field == 'topic_details' for k in keys):
                result.add(Action('topic', node))
        return sorted((a for a in result if a.family not in self.failed), key=lambda a: a.identity)

    def eligible(self, action, bindings):
        if action.op != 'bulk':
            return True
        known = self.ledger.valid(type_key(action.entity))
        if known and known.value != GET_TYPE:
            return False
        return not self.strict_discovery or type_key(action.entity) in bindings


def coverage(action, due):
    if action.op in ('get', 'bulk'):
        return {k for k in due if k.entity == action.entity and k.field in
                {'param:' + name for name in action.names}}
    if action.op == 'node':
        return {k for k in due if k.entity == action.entity and k.field in ('node_summary', 'service_type')}
    if action.op == 'info':
        return {k for k in due if k.entity == action.entity and k.field == 'service_type'}
    return {k for k in due if k.entity == action.entity and k.field == 'topic_details'}


def shadow(action, bindings):
    updated = bindings.copy()
    if action.op in ('node', 'info'):
        updated.add(type_key(action.entity))
    return updated


def greedy_completion(state, due, bindings, cap=32):
    due, bindings = due.copy(), bindings.copy()
    total, steps = 0.0, []
    for _ in range(cap):
        if not due:
            return total, steps
        candidates = state.candidates(due)
        useful = [a for a in candidates if state.eligible(a, bindings) and coverage(a, due)]
        if useful:
            action = min(useful, key=lambda a: (-len(coverage(a, due)) / state.cost(a),
                                                state.cost(a), a.identity))
        else:
            prerequisites = [a for a in candidates if a.op in ('info', 'node')
                             and type_key(a.entity) not in bindings]
            if not prerequisites:
                return math.inf, steps
            action = min(prerequisites, key=lambda a: (state.cost(a), a.identity))
        total += state.cost(action)
        steps.append(action)
        due -= coverage(action, due)
        bindings = shadow(action, bindings)
    return math.inf, steps


@dataclass
class Decision:
    fragment: tuple[Action, ...]
    predicted_completion: float
    reference_completion: float
    expansions: int = 0
    seconds: float = 0.0


def batching_completion(state, due, bindings):
    """Amortize each compatible node group, including all setup and leftovers.

    Each group's direct and bulk strategies may use either existing discovery
    provider. Mandatory node summaries and topic details are included; node_info
    can satisfy a required summary and the bulk prerequisite in the SAME call.
    This is deliberately strong on the real small catalogue, not eager read-all.
    """
    total, result = 0.0, []
    for node in sorted({k.entity for k in due}):
        group = {k for k in due if k.entity == node}
        possible = state.candidates(group)
        choices = []
        for bulk in (False, True):
            for discovery in (None, 'info', 'node'):
                outstanding, bound, seq = group.copy(), bindings.copy(), []
                if discovery:
                    action = Action(discovery, node)
                    if action not in possible:
                        continue
                    seq.append(action)
                    outstanding -= coverage(action, outstanding)
                    bound = shadow(action, bound)
                if any(k.field == 'node_summary' for k in outstanding):
                    action = Action('node', node)
                    if action.family in state.failed:
                        continue
                    seq.append(action)
                    outstanding -= coverage(action, outstanding)
                    bound = shadow(action, bound)
                if any(k.field == 'service_type' for k in outstanding):
                    action = Action('info', node)
                    if action.family in state.failed:
                        continue
                    seq.append(action)
                    outstanding -= coverage(action, outstanding)
                    bound = shadow(action, bound)
                names = tuple(sorted(k.field[6:] for k in outstanding if k.field.startswith('param:')))
                if names:
                    actions = [Action('bulk', node, names)] if bulk else [Action('get', node, (n,)) for n in names]
                    if any(a.family in state.failed or not state.eligible(a, bound) for a in actions):
                        continue
                    for action in actions:
                        seq.append(action)
                        outstanding -= coverage(action, outstanding)
                if any(k.field == 'topic_details' for k in outstanding):
                    action = Action('topic', node)
                    if action.family in state.failed:
                        continue
                    seq.append(action)
                    outstanding -= coverage(action, outstanding)
                if not outstanding:
                    choices.append((sum(state.cost(a) for a in seq), tuple(seq)))
        if not choices:
            return math.inf, result
        price, seq = min(choices, key=lambda x: (x[0], len(x[1]), tuple(a.identity for a in x[1])))
        total += price
        result.extend(seq)
    return total, result


def select(state, policy, *, depth=2, max_roots=16, max_expansions=128,
           margin_fraction=0.01, extra_decision_cost=0.0001):
    started = time.perf_counter()
    due, bindings = state.due(), state.bindings()
    if not due:
        return Decision((), 0.0, 0.0, seconds=time.perf_counter() - started)
    reference, sequence = greedy_completion(state, due, bindings)
    if not sequence:
        return Decision((), reference, reference, seconds=time.perf_counter() - started)
    if policy == 'greedy':
        best, score, expansions = tuple(sequence[:depth]), reference, 0
    elif policy == 'batching':
        score, seq = batching_completion(state, due, bindings)
        best, expansions = tuple(seq[:depth]), 0
    elif policy == 'jtvr':
        best, score, expansions = tuple(sequence[:depth]), reference, 0
        roots = [a for a in state.candidates(due) if state.eligible(a, bindings)]
        roots.sort(key=lambda a: (a != sequence[0], -len(coverage(a, due)) / state.cost(a), a.identity))
        roots = roots[:max_roots]
        for root in roots:
            after = due - coverage(root, due)
            bound = shadow(root, bindings)
            prefixes = [(root,)]
            if depth > 1 and after:
                prefixes += [(root, child) for child in state.candidates(after)
                             if state.eligible(child, bound)]
            for prefix in prefixes:
                if expansions >= max_expansions:
                    break
                expansions += 1
                remaining, structural = due.copy(), bindings.copy()
                cost = 0.0
                for action in prefix:
                    cost += state.cost(action)
                    remaining -= coverage(action, remaining)
                    structural = shadow(action, structural)
                tail, _ = greedy_completion(state, remaining, structural)
                estimate = cost + tail
                margin = margin_fraction * min(state.costs.values()) + extra_decision_cost
                if estimate + margin < score:
                    best, score = prefix, estimate
    else:
        raise ValueError('unknown_policy')
    return Decision(best, score, reference, expansions, time.perf_counter() - started)


def parse(action, raw):
    """Return only validated fields. A short positional bulk list is ambiguous."""
    parsed = {}
    if action.op == 'get':
        text = raw.get(action.names[0], '')
        match = re.fullmatch(r'Integer value is: (-?\d+)\s*', text) if isinstance(text, str) else None
        if match:
            parsed['param:' + action.names[0]] = int(match[1])
    elif action.op == 'info':
        text = raw.get(action.entity + '/get_parameters')
        if isinstance(text, str) and re.fullmatch(r'[A-Za-z_][\w]*/srv/[A-Za-z_][\w]*\s*', text):
            parsed['service_type'] = text.strip()
    elif action.op == 'node':
        text = raw.get(action.entity)
        if isinstance(text, str) and text.startswith(action.entity + '\n') and 'Service Servers:' in text:
            parsed['node_summary'] = text
            section = text.split('Service Servers:', 1)[1].split('Service Clients:', 1)[0]
            pattern = r'^\s*' + re.escape(action.entity + '/get_parameters') + r':\s*([^\s]+)\s*$'
            match = re.search(pattern, section, re.MULTILINE)
            if match:
                parsed['service_type'] = match[1]
    elif action.op == 'topic':
        text = raw.get(action.entity)
        if isinstance(text, str) and 'Type:' in text and 'QoS profile:' in text:
            parsed['topic_details'] = text
    elif action.op == 'bulk':
        text = raw.get('response', '')
        if not isinstance(text, str) or 'response:' not in text:
            return parsed
        try:
            tree = ast.parse(text.split('response:', 1)[1].strip(), mode='eval').body
            if not isinstance(tree, ast.Call) or ast.unparse(tree.func) != 'rcl_interfaces.srv.GetParameters_Response':
                return parsed
            values = next(k.value for k in tree.keywords if k.arg == 'values')
            if not isinstance(values, ast.List) or len(values.elts) != len(action.names):
                return parsed
            for name, value in zip(action.names, values.elts):
                if not isinstance(value, ast.Call) or ast.unparse(value.func) != 'rcl_interfaces.msg.ParameterValue':
                    return {}
                fields = {k.arg: k.value for k in value.keywords}
                kind = ast.literal_eval(fields['type'])
                if type(kind) is int and kind == 2:
                    number = ast.literal_eval(fields['integer_value'])
                    if type(number) is int:
                        parsed['param:' + name] = number
        except (SyntaxError, ValueError, TypeError, KeyError, StopIteration):
            return {}
    return parsed
