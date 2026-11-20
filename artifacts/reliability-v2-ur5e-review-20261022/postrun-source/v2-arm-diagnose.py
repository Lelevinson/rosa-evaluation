"""Post-failure deterministic diagnostics; no frozen experiment changes or LLMs."""
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'rosa-evaluation'))
from experiments.reliability_v2.arm import ArmSimulator
from rosa_reliability.ros_arm import ArmTransport,JOINTS,HOME_POSE
from controller_manager_msgs.srv import ListControllers

folder=ROOT/'rosa-evaluation/artifacts/arm-development'/('diagnostic-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
folder.mkdir(parents=True,exist_ok=False)
os.environ['ROS_DOMAIN_ID']='194'
os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE']='LOCALHOST'
sim=ArmSimulator(folder/'simulator')
controller=observer=None
result={'diagnostic_only':True,'model_calls':0,'samples':[]}
try:
    sim.start()
    controller,observer=ArmTransport(),ArmTransport(read_only=True)
    client=controller.node.create_client(ListControllers,'/controller_manager/list_controllers')
    deadline=time.monotonic()+120
    active=False
    while time.monotonic()<deadline:
        if not client.wait_for_service(timeout_sec=2):
            continue
        future=client.call_async(ListControllers.Request())
        while not future.done() and time.monotonic()<deadline:
            controller.executor.spin_once(timeout_sec=.05)
        if future.done() and future.result():
            states={c.name:c.state for c in future.result().controller}
            result['controller_states']=states
            if states.get('joint_trajectory_controller')=='active' and states.get('joint_state_broadcaster')=='active':
                active=True
                break
    if not active:
        raise RuntimeError('controllers_not_active_within_120s')
    result['initial']=observer.read('/ur5e',list(JOINTS))
    result['requested_home']=HOME_POSE
    result['receipt']=controller.write('/ur5e',HOME_POSE)
    for index in range(12):
        actual=observer.read('/ur5e',list(JOINTS))
        sample={'index':index,'actual':actual,'errors':{n:actual[n]-HOME_POSE[n] for n in JOINTS},
                'sensor':deepcopy(observer.records[-1]),'at':time.monotonic()}
        result['samples'].append(sample)
        print(json.dumps(sample),flush=True)
        if all(abs(actual[n]-HOME_POSE[n])<=.025 for n in JOINTS):
            result['home_verified']=True
            break
        time.sleep(.5)
except BaseException as error:
    result['error']=str(error)
    raise
finally:
    for item in (controller,observer):
        if item:
            item.close()
    result['cleanup']=sim.close()
    (folder/'diagnostic.json').write_text(json.dumps(result,indent=2))
    print('DIAGNOSTIC_EVIDENCE',folder,flush=True)
