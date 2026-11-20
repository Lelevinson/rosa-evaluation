"""Deterministic transport and matched two-read fragment executor.

No LLM, ROSA custom Runnable, native tool IDs or inferred model-call savings are
used here. Real CLI shapes come from the separate isolated-node calibration.
"""
from copy import deepcopy
from dataclasses import asdict
import json
import time

from .core import (Action, GET_TYPE, Key, Ledger, State, coverage, manifest, parse,
                   select, type_key)
from .fixtures import NODES, PARAMS


class World:
    def __init__(self, spec, captures):
        self.spec = spec
        self.samples = {r['tool']: r['raw'] for r in captures
                        if r['purpose'] == 'development_calibration_0'}
        self.values = {node: {name: i + 1 + spec['seed'] * 10
                              for i, name in enumerate(PARAMS)} for node in NODES}
        self.events = []

    def read(self, action):
        values = self.values.get(action.entity, {})
        condition, seed = self.spec['condition'], self.spec['seed']
        if action.op == 'get':
            raw = {action.names[0]: f'Integer value is: {values[action.names[0]]}\n'}
        elif action.op == 'info':
            kind = 'example_interfaces/srv/Trigger' if condition == 'wrong_bulk_type' else GET_TYPE
            raw = {action.entity + '/get_parameters': kind + '\n'}
        elif action.op in ('node', 'topic'):
            original = self.samples[action.tool]
            original_key = next(iter(original))
            raw = {action.entity: original[original_key].replace('/jtvr_alpha',
                    action.entity.removesuffix('/status') if action.op == 'topic' else action.entity)}
            if condition == 'wrong_bulk_type' and action.op == 'node':
                raw[action.entity] = raw[action.entity].replace(GET_TYPE, 'example_interfaces/srv/Trigger')
        else:
            if condition == 'wrong_bulk_type':
                return {'error': 'registered GetParameters type not offered at this endpoint'}
            chunks = []
            for index, name in enumerate(action.names):
                kind = 0 if condition == 'partial_bulk' and seed == 1 and index == 0 else 2
                chunks.append(f'rcl_interfaces.msg.ParameterValue(type={kind}, integer_value={values[name]})')
            if condition == 'partial_bulk' and seed == 0:
                chunks = chunks[:-1]  # Positional correspondence is no longer reliable.
            raw = {'response': 'response:\nrcl_interfaces.srv.GetParameters_Response(values=['
                    + ', '.join(chunks) + '])\n'}
        return raw


def execute(spec, policy, costs, captures, *, profile='calibrated', depth=2,
            role_separated=False):
    obligations = manifest(spec['requirements'], spec['requirements'])
    ledger = Ledger(run_id=f"{spec['id']}:{profile}:{policy}:d{depth}")
    pricing = dict(costs)
    if profile == 'unit_cost':
        pricing = {tool: 1.0 for tool in pricing}
    if spec['condition'] == 'high_setup_cost':
        for tool in ('ros2_service_info', 'ros2_node_info'):
            pricing[tool] *= 4
    state = State(obligations, ledger, pricing, strict_discovery=profile != 'prior_type_allowed')
    world = World(spec, captures)
    transcript, decisions, provenance = [], [], []
    parser_seconds = 0.0
    started = time.perf_counter()
    # Common service-list bootstrap: known node-scoped endpoint NAMES, not types
    # or values. Cost and work are included separately in every episode.
    bootstrap = next(r for r in captures if r['purpose'] == 'bootstrap')
    transcript.append({'actor': 'bootstrap', 'tool': 'ros2_service_list',
        'arguments': {'pattern': 'jtvr_'}, 'raw': bootstrap['raw'],
        'cli_commands': 1, 'modeled_server_rpcs': 0,
        'cost': bootstrap['seconds'] if profile != 'unit_cost' else 1.0})
    for write in spec['writes']:
        key = Key(write['entity'], write['field'])
        # A previous value cannot satisfy post-write obligations, even if the
        # desired value happens to equal it. Dispatch always advances the epoch.
        ledger.ingest(key, world.values[key.entity][key.field[6:]], epoch=0,
                      started=ledger.tick, raw_ref=-1, tool='pre_write_seed')
        ledger.dispatch_write(key)
        world.values[key.entity][key.field[6:]] = write['value']
        ledger.complete_write(key)
        ambiguous = spec['condition'] == 'ambiguous_write_ack'
        transcript.append({'actor': 'controlled_write', 'tool': 'ros2_param_set',
            'arguments': {'node_name': key.entity, 'param_name': key.field[6:],
                          'param_value': str(write['value'])},
            'raw': {'error': 'acknowledgment lost; actual outcome unknown to policy'} if ambiguous
                   else {key.field[6:]: 'Set parameter successful'},
            'epoch': ledger.epoch(key), 'write_completed_tick': ledger.tick,
            'cli_commands': 1, 'modeled_server_rpcs': 1,
            'cost': 1.0 if profile == 'unit_cost' else next(
                r['seconds'] for r in captures if r['purpose'] == 'write_smoke')})
    if spec['warm_type']:
        # Charge acquiring metadata; this study does not treat cache warm-up as
        # free. Primary reuse is within this episode; no cross-run state leaks.
        for node in sorted({o.key.entity for o in obligations if o.key.field.startswith('param:')}):
            action = Action('info', node)
            raw = world.read(action)
            result = parse(action, raw)
            ledger.tick += 1
            if 'service_type' in result:
                ledger.ingest(type_key(node), result['service_type'], epoch=0,
                    started=ledger.tick, raw_ref=len(transcript), tool=action.tool)
            transcript.append({'actor': 'cache_warmup', 'tool': action.tool,
                'arguments': action.arguments(), 'raw': raw, 'cli_commands': 1,
                'modeled_server_rpcs': 0, 'cost': pricing[action.tool]})

    full_obligations = state.obligations
    phases = [('joint', full_obligations)]
    if role_separated:
        phases = [(role, [o for o in full_obligations if role in o.roles])
                  for role in ('task', 'verification')]
    calls = 0
    terminal = 'RESOLVED'
    for phase_label, active in phases:
        state.obligations = active
        while state.due():
            if calls >= 24 or len(decisions) >= 24:
                terminal = 'BUDGET_EXHAUSTED'
                break
            decision = select(state, policy, depth=depth)
            decisions.append({'phase': phase_label, **asdict(decision)})
            if not decision.fragment:
                terminal = 'UNRESOLVED'
                break
            epoch_snapshot = dict(ledger.epochs)
            for position, planned in enumerate(decision.fragment):
                due = state.due()
                # Bind child to ACTUAL results, current scope and remaining names.
                if position and epoch_snapshot != ledger.epochs:
                    break
                if planned.op == 'bulk':
                    names = tuple(n for n in planned.names
                                  if Key(planned.entity, 'param:' + n) in due)
                    if not names:
                        break
                    action = Action('bulk', planned.entity, names)
                else:
                    action = planned
                if not state.eligible(action, state.bindings()) or action.family in state.failed:
                    break
                if position and not coverage(action, due) and action.op not in ('info', 'node'):
                    break
                # Child must never proceed after mismatch; recovery needs an LLM.
                if any(o.equals is not None and ledger.valid(o.key)
                       and ledger.valid(o.key).value != o.equals for o in active):
                    terminal = 'MISMATCH'
                    break
                ledger.tick += 1
                read_start = ledger.tick
                raw = world.read(action)
                before_parse = time.perf_counter()
                parsed = parse(action, raw)
                parser_seconds += time.perf_counter() - before_parse
                ledger.tick += 1
                ref = len(transcript)
                for name, value in parsed.items():
                    key = Key(action.entity, name, 'graph' if name in
                              ('node_summary', 'service_type', 'topic_details') else 'final')
                    ledger.ingest(key, value, epoch=ledger.epoch(key), started=read_start,
                                  raw_ref=ref, tool=action.tool)
                intended = coverage(action, due)
                unresolved_after = intended & state.due()
                if not parsed or unresolved_after:
                    state.failed.add(action.family)
                entry = {'actor': 'policy_root' if position == 0 else 'read_continuation',
                    'fragment_id': len(decisions) - 1, 'op': action.op,
                    'tool': action.tool, 'arguments': action.arguments(), 'raw': raw,
                    'parsed': parsed, 'read_started_tick': read_start, 'read_ended_tick': ledger.tick,
                    'epochs_at_start': {name: ledger.epoch(Key(action.entity, name)) for name in parsed},
                    'oracle_at_read': deepcopy(world.values.get(action.entity, {})),
                    'cli_commands': 1, 'modeled_server_rpcs': int(action.op in ('get', 'bulk')),
                    'cost': state.cost(action)}
                transcript.append(entry)
                calls += 1
                provenance.append(action.identity)
                if not parsed or unresolved_after:
                    break
            if terminal == 'MISMATCH':
                break
        if terminal != 'RESOLVED':
            break
    state.obligations = full_obligations
    remaining = state.due()
    predicates = {f'{o.key.entity}:{o.key.field}': ('UNKNOWN' if not ledger.valid(o.key)
        else 'TRUE' if ledger.valid(o.key).value == o.equals else 'FALSE')
        for o in full_obligations if o.equals is not None}
    passed = not remaining and all(p == 'TRUE' for p in predicates.values())
    output = {'fixture_id': spec['id'], 'template': spec['template'], 'condition': spec['condition'],
        'seed': spec['seed'], 'policy': policy, 'profile': profile, 'depth': depth,
        'role_separated': role_separated, 'opportunity': spec['opportunity'],
        'terminal': terminal, 'all_observations_resolved': not remaining,
        'verified_contract_pass': passed, 'goal_predicates': predicates,
        'unresolved': [asdict(k) for k in sorted(remaining)],
        'trace': transcript, 'decisions': decisions, 'evidence': [asdict(e) for e in ledger.records],
        'acquisition_sequence': provenance, 'policy_decisions': len(decisions),
        'tool_wrappers': len(transcript), 'cli_commands': sum(r['cli_commands'] for r in transcript),
        'modeled_server_rpcs': sum(r['modeled_server_rpcs'] for r in transcript),
        'modeled_cost': sum(r['cost'] for r in transcript),
        'acquisition_cost': sum(r['cost'] for r in transcript if r['actor'] in ('policy_root', 'read_continuation')),
        'selector_seconds': sum(d['seconds'] for d in decisions),
        'parser_seconds': parser_seconds, 'simulation_wall_seconds': time.perf_counter() - started,
        'model_requests': 0, 'measured_ros_wall_seconds': None,
        'claim_scope': 'policy-only simulated work with real-wrapper-derived contracts; no LLM or robot'}
    return output
