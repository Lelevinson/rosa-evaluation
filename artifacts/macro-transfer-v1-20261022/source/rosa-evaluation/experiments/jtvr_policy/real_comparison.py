"""Small real-transport check of the same policies; no LLM or custom agent loop."""
from dataclasses import asdict
import json
import random
import time

from .core import Action, Key, Ledger, State, coverage, manifest, parse, select
from .fixtures import suite

REAL_TEMPLATES = ('one_parameter', 'three_cold', 'node_summary_and_parameters',
                  'two_node_scope', 'write_report_verify')


def compare(tools, capture, calibration, destination):
    costs = json.loads((calibration / 'calibration.json').read_text())['cost_seconds']
    cases = [s for s in suite() if s['template'] in REAL_TEMPLATES
             and s['condition'] == 'nominal' and s['seed'] == 0]
    schedule = [(s, p) for s in cases for p in ('greedy', 'batching', 'jtvr')]
    random.Random(20261021).shuffle(schedule)  # Fixed before measuring; one repeat only.
    results = []
    for spec, policy in schedule:
        ledger = Ledger(run_id='real:' + spec['id'] + ':' + policy)
        state = State(manifest(spec['requirements'], spec['requirements']), ledger, costs)
        first_row, first_native = len(capture.rows), len(capture.native)
        capture.call(tools, 'ros2_service_list', {'pattern': 'jtvr_'}, 'real_bootstrap')
        for write in spec['writes']:
            key = Key(write['entity'], write['field'])
            ledger.dispatch_write(key)
            capture.call(tools, 'ros2_param_set', {'node_name': key.entity,
                'param_name': key.field[6:], 'param_value': str(write['value'])}, 'real_write')
            ledger.complete_write(key)
        sequences, decisions, dispatches = [], [], []
        started = time.perf_counter()
        while state.due() and len(sequences) < 24:
            decision = select(state, policy)
            decisions.append(asdict(decision))
            if not decision.fragment:
                break
            snapshot = dict(ledger.epochs)
            for index, planned in enumerate(decision.fragment):
                if index and snapshot != ledger.epochs:
                    break
                due = state.due()
                action = planned
                if action.op == 'bulk':
                    names = tuple(n for n in action.names if Key(action.entity, 'param:' + n) in due)
                    if not names:
                        break
                    action = Action('bulk', action.entity, names)
                if not state.eligible(action, state.bindings()) or action.family in state.failed:
                    break
                ledger.tick += 1
                read_start = ledger.tick
                raw = capture.call(tools, action.tool, action.arguments(),
                                   'real_root' if index == 0 else 'real_continuation')
                parsed = parse(action, raw)
                ledger.tick += 1
                for name, value in parsed.items():
                    key = Key(action.entity, name, 'graph' if name in
                              ('node_summary', 'service_type', 'topic_details') else 'final')
                    ledger.ingest(key, value, epoch=ledger.epoch(key), started=read_start,
                                  raw_ref=len(capture.rows) - 1, tool=action.tool)
                sequences.append(action.identity)
                dispatches.append({'action': asdict(action), 'parsed': parsed,
                    'raw_ref': len(capture.rows) - 1, 'start_tick': read_start,
                    'end_tick': ledger.tick, 'epoch': {name: ledger.epoch(Key(action.entity, name)) for name in parsed},
                    'decision': len(decisions) - 1, 'position': index})
                if not parsed or coverage(action, due) & state.due():
                    state.failed.add(action.family)
                    break
        success = not state.due() and all(o.equals is None or ledger.valid(o.key).value == o.equals
                                         for o in state.obligations)
        commands = capture.native[first_native:]
        rows = capture.rows[first_row:]
        result = {'fixture_id': spec['id'], 'template': spec['template'], 'policy': policy,
            'verified_contract_pass': success, 'acquisition_sequence': sequences,
            'decisions': decisions, 'dispatches': dispatches,
            'evidence': [asdict(e) for e in ledger.records], 'row_range': [first_row, len(capture.rows)],
            'native_range': [first_native, len(capture.native)],
            'tool_wrappers': len(rows), 'cli_commands': len(commands),
            'server_rpcs': sum(len(c['server_rpcs']) for c in commands),
            'actual_cli_wall_seconds': sum(c['seconds'] for c in commands),
            'acquisition_wall_seconds': time.perf_counter() - started,
            'model_requests': 0, 'scope': 'single-repeat real transport smoke; not a latency comparison'}
        results.append(result)
        with (destination / 'episodes.jsonl').open('a') as output:
            output.write(json.dumps(result) + '\n')
        if not success:
            raise RuntimeError('real_policy_case_failed:' + spec['id'] + ':' + policy)
    (destination / 'summary.json').write_text(json.dumps({
        'episodes': len(results), 'passed': sum(r['verified_contract_pass'] for r in results),
        'model_requests': 0, 'policy_scope': 'same policy code; existing ROSA wrappers; no AgentExecutor integration',
        'order_seed': 20261021, 'templates': REAL_TEMPLATES}, indent=2))
