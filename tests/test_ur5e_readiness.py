import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from experiments.ur5e_transfer_v1.arm import ArmSimulator


class ReadinessTests(unittest.TestCase):
    def test_joint_states_alone_do_not_release_startup_gate(self):
        states=[{'joint_state_broadcaster':'active','joint_trajectory_controller':'inactive'},
                {'joint_state_broadcaster':'active','joint_trajectory_controller':'active'}]
        class Client:
            queries=0
            def wait_for_service(self,**kwargs): return True
            def call_async(self,request):
                state=states[self.queries]
                self.queries+=1
                return SimpleNamespace(done=lambda:True,result=lambda:SimpleNamespace(
                    controller=[SimpleNamespace(name=n,state=s) for n,s in state.items()]))
        client=Client()
        probe=SimpleNamespace(node=SimpleNamespace(create_client=lambda *a:client),
            records=[{'kind':'observation','sim_stamp':[1,0]}],close=lambda:None)
        def read(*args):
            self.assertEqual(client.queries,2)
            return {'joint':.1}
        probe.read=read
        with tempfile.TemporaryDirectory() as directory, patch(
                'experiments.ur5e_transfer_v1.arm.ArmTransport',return_value=probe), patch(
                'experiments.ur5e_transfer_v1.arm.subprocess.Popen'):
            simulator=ArmSimulator(Path(directory)/'sim')
            simulator.start()
            simulator.log.close()
            self.assertTrue((simulator.folder/'readiness.json').exists())

    def test_missing_active_controller_is_a_bounded_failure(self):
        closed=[]
        probe=SimpleNamespace(node=SimpleNamespace(create_client=lambda *a:object()),close=lambda:closed.append(True))
        with tempfile.TemporaryDirectory() as directory, patch(
                'experiments.ur5e_transfer_v1.arm.ArmTransport',return_value=probe), patch(
                'experiments.ur5e_transfer_v1.arm.subprocess.Popen'), patch('time.monotonic',side_effect=[0,121]):
            simulator=ArmSimulator(Path(directory)/'sim')
            with self.assertRaisesRegex(RuntimeError,'active_controllers_not_ready'):
                simulator.start()
            simulator.log.close()
        self.assertEqual(closed,[True])
