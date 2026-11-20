"""Bounded real ROS transport and independently queried evaluator state."""
from contextlib import contextmanager
import json
import multiprocessing as mp
import os
from pathlib import Path
import shlex
import signal
import subprocess
import time
from unittest.mock import patch

from ..jtvr_policy.ros_probe import server
from ..tracing import trace_operation


class RealEnvironment:
    def __init__(self, destination, domain):
        self.destination = destination
        self.destination.mkdir(parents=True, exist_ok=True)
        self.rpc_path = destination / 'rpc-events.jsonl'
        self.commands = []
        self.domain = domain
        self.child = None

    def start(self):
        os.environ['ROS_DOMAIN_ID'] = str(self.domain)
        os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
        context = mp.get_context('spawn')
        self.ready, self.stop = context.Event(), context.Event()
        self.child = context.Process(target=server, args=(self.ready, self.stop, str(self.rpc_path)))
        self.child.start()
        if not self.ready.wait(20):
            raise RuntimeError('parameter_nodes_not_ready')
        # CLI daemon discovery is a different participant from the evaluator's
        # service client. Wait for the graph, without reading parameter values.
        readiness = []
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            observed = subprocess.run(['ros2', 'node', 'list'], capture_output=True, text=True, timeout=15)
            readiness.append({'stdout': observed.stdout, 'stderr': observed.stderr, 'returncode': observed.returncode})
            if {'/jtvr_alpha', '/jtvr_beta'} <= set(observed.stdout.splitlines()):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError('cli_graph_not_ready')
        (self.destination / 'readiness.json').write_text(json.dumps(readiness, indent=2))
        import rclpy
        from rclpy.node import Node
        from rclpy.executors import SingleThreadedExecutor
        self.context = rclpy.Context()
        rclpy.init(context=self.context)
        self.node = Node('stage4_evaluator', context=self.context, start_parameter_services=False)
        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)

    def request(self, service, service_type, request):
        import rclpy
        client = self.node.create_client(service_type, service)
        try:
            if not client.wait_for_service(timeout_sec=10):
                raise TimeoutError('evaluator_service_missing')
            future = client.call_async(request)
            rclpy.spin_until_future_complete(self.node, future, executor=self.executor, timeout_sec=10)
            if not future.done():
                raise TimeoutError('evaluator_request_timeout')
            return future.result()
        finally:
            self.node.destroy_client(client)

    def reset(self, spec):
        from rcl_interfaces.srv import SetParameters
        from rcl_interfaces.msg import Parameter, ParameterValue
        records = []
        for node in spec['groups']:
            parameters = [Parameter(name=name, value=ParameterValue(type=2, integer_value=i + 1))
                          for i, name in enumerate(('alpha', 'beta', 'gamma'))]
            result = self.request(node + '/set_parameters', SetParameters,
                                  SetParameters.Request(parameters=parameters))
            if not all(r.successful for r in result.results):
                raise RuntimeError('reset_failed')
            records.append({'node': node, 'values': {'alpha': 1, 'beta': 2, 'gamma': 3}})
        with (self.destination / 'evaluator-operations.jsonl').open('a') as output:
            output.write(json.dumps({'role': 'outside_trial_reset', 'records': records}) + '\n')

    def oracle(self, spec):
        from rcl_interfaces.srv import GetParameters
        values = {}
        for node, group in spec['groups'].items():
            names = sorted(group['names'])
            response = self.request(node + '/get_parameters', GetParameters, GetParameters.Request(names=names))
            if len(response.values) != len(names) or any(v.type != 2 for v in response.values):
                raise RuntimeError('independent_evaluator_response_invalid')
            values[node] = {name: value.integer_value for name, value in zip(names, response.values)}
        with (self.destination / 'evaluator-operations.jsonl').open('a') as output:
            output.write(json.dumps({'role': 'outside_trial_final_oracle', 'values': values}) + '\n')
        return values

    def transport(self, command):
        argv = shlex.split(command)
        if len(argv) < 3 or argv[0] != 'ros2' or argv[1] not in ('node', 'topic', 'param', 'service'):
            raise ValueError('unregistered_cli')
        if argv[1:3] in (['param', 'get'], ['param', 'set']):
            argv += ['--timeout', '5']  # Shared bounded graph-discovery allowance.
        count_before = len(self.rpc_path.read_text().splitlines()) if self.rpc_path.exists() else 0
        started = time.perf_counter()
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        caught = None
        try:
            stdout, stderr = process.communicate(timeout=35)
            ok = process.returncode == 0
        except BaseException as error:
            caught = error
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            ok = False
        events = self.rpc_path.read_text().splitlines()[count_before:] if self.rpc_path.exists() else []
        record = {'argv': argv, 'success': ok, 'seconds': time.perf_counter() - started,
                  'stdout': stdout, 'stderr': stderr, 'server_rpcs': [json.loads(x) for x in events]}
        self.commands.append(record)
        with (self.destination / 'native-commands.jsonl').open('a') as output:
            output.write(json.dumps(record) + '\n')
        if caught is not None:
            raise caught
        return ok, stdout if ok else stderr

    def invoke(self, name, args, actor):
        from rosa.tools import ros2
        # func avoids a second automatic LangChain dispatch; the native operation
        # receives its own explicit nested TOOL span with honest actor provenance.
        with trace_operation(name, kind='TOOL') as span:
            if span:
                span.set_attribute('input.value', json.dumps(args))
                span.set_attribute('stage4.actor', actor)
            with patch.object(ros2, 'execute_ros_command', self.transport):
                raw = getattr(ros2, name).func(**args)
            if span:
                span.set_attribute('output.value', json.dumps(raw))
        return raw

    def close(self):
        result = {}
        if getattr(self, 'node', None) is not None:
            self.executor.shutdown()
            self.node.destroy_node()
            self.context.shutdown()
        if self.child:
            self.stop.set()
            self.child.join(10)
            if self.child.is_alive():
                self.child.terminate()
                self.child.join(5)
            result['server_exitcode'] = self.child.exitcode
            try:
                process = subprocess.run(['ros2', 'daemon', 'stop'], capture_output=True, text=True, timeout=15)
                result['daemon_stop_returncode'] = process.returncode
            except subprocess.TimeoutExpired:
                result['daemon_stop_error'] = 'timeout'
        (self.destination / 'cleanup.json').write_text(json.dumps(result, indent=2))
