"""Capture real ROSA wrapper outputs and server-counted RPCs on isolated nodes.

Only this experiment's nodes are writable. The ROSA tools are unchanged; their
transport is replaced with bounded argv execution to avoid unbounded shell calls.
"""
import argparse
from datetime import datetime, timezone
import json
import multiprocessing as mp
import os
from pathlib import Path
import re
import shlex
import signal
import statistics
import subprocess
import sys
import time
from unittest.mock import patch

DOMAIN = '173'
NODES = ('/jtvr_alpha', '/jtvr_beta')
TYPE = 'rcl_interfaces/srv/GetParameters'


def server(ready, stop, rpc_path):
    import rclpy
    from rclpy.executors import SingleThreadedExecutor
    from rclpy.node import Node
    from rclpy.parameter_service import ParameterService
    from std_msgs.msg import String

    class CountedService(ParameterService):
        def record(self, kind, request):
            with open(rpc_path, 'a') as output:
                output.write(json.dumps({'node': self._get_node().get_fully_qualified_name(),
                    'kind': kind, 'names': list(getattr(request, 'names', [])),
                    'oracle_values': {name: self._get_node().get_parameter(name).value
                        for name in getattr(request, 'names', []) if name in ('alpha', 'beta', 'gamma')},
                    'time_ns': time.monotonic_ns()}) + '\n')

        def _get_parameters_callback(self, request, response):
            self.record('get_parameters', request)
            return super()._get_parameters_callback(request, response)

        def _get_parameter_types_callback(self, request, response):
            self.record('get_parameter_types', request)
            return super()._get_parameter_types_callback(request, response)

        def _describe_parameters_callback(self, request, response):
            self.record('describe_parameters', request)
            return super()._describe_parameters_callback(request, response)

        def _set_parameters_callback(self, request, response):
            self.record('set_parameters', request)
            return super()._set_parameters_callback(request, response)

    rclpy.init()
    executor = SingleThreadedExecutor()
    nodes, services, publishers = [], [], []
    try:
        for name in NODES:
            node = Node(name.lstrip('/'), start_parameter_services=False)
            for field, value in (('alpha', 1), ('beta', 2), ('gamma', 3)):
                node.declare_parameter(field, value)
            services.append(CountedService(node))
            publisher = node.create_publisher(String, name + '/status', 10)
            publishers.append(publisher)
            node.create_timer(0.25, lambda p=publisher: p.publish(String(data='test')))
            executor.add_node(node)
            nodes.append(node)
        ready.set()
        while not stop.is_set():
            executor.spin_once(timeout_sec=0.1)
    finally:
        executor.shutdown()
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()


class Capture:
    def __init__(self, destination):
        self.destination = destination
        self.rpc_path = destination / 'rpc-events.jsonl'
        self.rows = []
        self.native = []

    def transport(self, command):
        argv = shlex.split(command)
        if len(argv) < 3 or argv[0] != 'ros2' or argv[1] not in ('node', 'topic', 'param', 'service'):
            raise ValueError('unsupported_command')
        if argv[1:3] in (['param', 'get'], ['param', 'set']):
            if argv[3] not in NODES or argv[4] not in ('alpha', 'beta', 'gamma'):
                raise ValueError('out_of_scope_parameter')
        if argv[1:3] == ['service', 'call']:
            if argv[3] not in [n + '/get_parameters' for n in NODES] or argv[4] != TYPE:
                raise ValueError('unregistered_service')
            # Only our generated literal-name list is allowed. No other requests.
            match = re.fullmatch(r'\{names: \[([a-z, ]+)\]\}', argv[5])
            names = match[1].split(', ') if match else []
            if not names or len(names) != len(set(names)) or set(names) - {'alpha', 'beta', 'gamma'}:
                raise ValueError('out_of_scope_request')
        if argv[1:3] == ['node', 'info'] and argv[3] not in NODES:
            raise ValueError('out_of_scope_node')
        if argv[1:3] == ['topic', 'info'] and argv[3] not in [n + '/status' for n in NODES]:
            raise ValueError('out_of_scope_topic')
        before = len(self.rpc_path.read_text().splitlines()) if self.rpc_path.exists() else 0
        started = time.monotonic()
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=40)
            ok = process.returncode == 0
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            ok = False
            stderr += '\nTIMEOUT'
        elapsed = time.monotonic() - started
        events = self.rpc_path.read_text().splitlines()[before:] if self.rpc_path.exists() else []
        self.native.append({'argv': argv, 'success': ok, 'seconds': elapsed,
                            'stdout': stdout, 'stderr': stderr,
                            'server_rpcs': [json.loads(x) for x in events]})
        return ok, stdout if ok else stderr

    def call(self, tools, tool, args, purpose):
        before = len(self.native)
        raw = getattr(tools, tool).invoke(args)
        operations = self.native[before:]
        row = {'tool': tool, 'args': args, 'purpose': purpose, 'raw': raw,
               'cli_commands': len(operations),
               'seconds': sum(x['seconds'] for x in operations),
               'server_rpcs': sum(len(x['server_rpcs']) for x in operations)}
        self.rows.append(row)
        # Durable incremental records survive interruption, never treated as complete.
        with (self.destination / 'captures.jsonl').open('a') as output:
            output.write(json.dumps(row) + '\n')
        return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--compare-calibration', help='Run the frozen three-policy ROS smoke cases using these costs')
    args = parser.parse_args()
    destination = Path(args.output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    os.environ['ROS_DOMAIN_ID'] = DOMAIN
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    # Separate domain; never stop a daemon belonging to the user's normal graph.
    rpc_path = destination / 'rpc-events.jsonl'
    context = mp.get_context('spawn')
    ready, stop = context.Event(), context.Event()
    child = context.Process(target=server, args=(ready, stop, str(rpc_path)))
    capture = Capture(destination)
    status = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'ros_domain_id': DOMAIN, 'nodes': NODES, 'status': 'RUNNING',
              'scope': 'isolated declared integer parameters; no robot or actuator'}
    (destination / 'status.json').write_text(json.dumps(status, indent=2))
    child.start()
    try:
        if not ready.wait(20):
            raise RuntimeError('parameter_server_not_ready')
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'rosa-research' / 'src'))
        from rosa.tools import ros2 as tools
        with patch.object(tools, 'execute_ros_command', capture.transport):
            if args.compare_calibration:
                from .real_comparison import compare
                compare(tools, capture, Path(args.compare_calibration), destination)
            else:
                calibrate(tools, capture)
        if any(not x['success'] for x in capture.native):
            raise RuntimeError('one_or_more_native_commands_failed')
        if not args.compare_calibration:
            costs = {}
            for tool in ('ros2_param_get', 'ros2_service_info', 'ros2_service_call',
                         'ros2_node_info', 'ros2_topic_info'):
                values = [r['seconds'] for r in capture.rows if r['tool'] == tool
                          and r['purpose'].startswith('development_calibration_')]
                costs[tool] = statistics.median(values)
            (destination / 'calibration.json').write_text(json.dumps({
                'cost_seconds': costs, 'samples_per_tool': 2,
                'claim': 'small sequential development calibration, not a latency guarantee',
                'counting': 'server callback RPCs exclude DDS discovery; CLI counts are separate'}, indent=2))
        status['status'] = 'COMPLETE'
    except BaseException as error:
        status.update(status='FAILED', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        stop.set()
        child.join(10)
        if child.is_alive():
            child.terminate()
            child.join(5)
        status['cleanup'] = {'server_exitcode': child.exitcode}
        try:
            daemon = subprocess.run(['ros2', 'daemon', 'stop'], capture_output=True, text=True, timeout=15)
            status['cleanup']['daemon_stop_returncode'] = daemon.returncode
        except subprocess.TimeoutExpired:
            status['cleanup']['daemon_stop_error'] = 'timeout'
        status['finished_utc'] = datetime.now(timezone.utc).isoformat()
        (destination / 'native-commands.json').write_text(json.dumps(capture.native, indent=2))
        (destination / 'status.json').write_text(json.dumps(status, indent=2))
        print(json.dumps(status), flush=True)


def calibrate(tools, capture):
    capture.call(tools, 'ros2_service_list', {'pattern': 'jtvr_'}, 'bootstrap')
    for repeat in range(2):
        for tool, kwargs in (
            ('ros2_param_get', {'node_name': NODES[0], 'param_name': 'alpha'}),
            ('ros2_service_info', {'services': [NODES[0] + '/get_parameters']}),
            ('ros2_service_call', {'service_name': NODES[0] + '/get_parameters',
                'srv_type': TYPE, 'request': '{names: [alpha, beta, gamma]}'}),
            ('ros2_node_info', {'nodes': [NODES[0]]}),
            ('ros2_topic_info', {'topics': [NODES[0] + '/status']}),
        ):
            capture.call(tools, tool, kwargs, f'development_calibration_{repeat}')
    capture.call(tools, 'ros2_node_info', {'nodes': list(NODES)}, 'wrapper_native_count')
    capture.call(tools, 'ros2_param_set', {'node_name': NODES[0],
        'param_name': 'alpha', 'param_value': '20'}, 'write_smoke')
    capture.call(tools, 'ros2_param_get', {'node_name': NODES[0],
        'param_name': 'alpha'}, 'post_write_smoke')
    capture.call(tools, 'ros2_service_call', {'service_name': NODES[0] + '/get_parameters',
        'srv_type': TYPE, 'request': '{names: [alpha]}'}, 'single_bulk_smoke')
    capture.call(tools, 'ros2_param_get', {'node_name': NODES[1],
        'param_name': 'alpha'}, 'node_scope_smoke')


if __name__ == '__main__':
    main()
