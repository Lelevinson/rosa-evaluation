"""Fixed schemas shared by the models, with isolated instruction intervention."""
from typing import Literal
from langchain_core.tools import tool
from ..stateful.tools import INSTRUCTIONS as ORIGINAL, make_tools as legacy_tools

CLARIFICATION = (
    ' Additional explicit contract: every non-refusal task requires verify_goal before submit_report, '
    'even if no action was attempted because a sensor was UNKNOWN. UNKNOWN means report unknown, not failure. '
    'Never pick using a robot-health revision as a substitute for an UNKNOWN object pose. '
    'After an accepted pick is verified with nothing held, stop and report failure; do not repeat it. '
    'In every non-battery task, submit_report battery_percent MUST be the literal integer -1, '
    'even when observe_robot returned a real battery percentage. Do not call tools after submit_report.'
)
NEW_CONTRACT = (
    'This is an in-memory robot simulation. Only registered tools exist; do not use ROS CLI or shell. '
    'Only the left arm is eligible, but current authorization can change: check read_permissions. '
    'Observe health/holding and locate the requested object before picking; use its pose revision. '
    'Refresh after a revision mismatch. Acceptance is not success. After every accepted action '
    'call verify_goal before another action. An unfinished transfer can return FAILURE while '
    'holding the object: continue with placement only if holding is verified. If an accepted pick '
    'is verified with nothing held, stop and report failure. Never pick with UNKNOWN pose. '
    'Verify every non-refusal task before reporting, including when no action was attempted. '
    'Report unknown for unresolvable observations or verification. Submit exactly one report '
    'with outcome success, failure, unknown or refused and battery_percent=-1, then answer briefly. '
    'Never call tools after reporting. Report success only after verified final goal achievement. '
    ' This version also provides read_permissions (current arm authorization) and inspect_target '
    '(current target availability). Use these when relevant. Health includes minimum_battery. '
    'Do not attempt motion with insufficient battery, an occupied gripper, or known missing permission. '
    'A retryable sensor outage or UNKNOWN verification can be checked again at most once. '
    'If the goal already holds, verify it and report success without moving. '
    'A blocked target or verified unsuccessful execution is failure; missing evidence is unknown. '
    'If permissions deny the left arm at any point, verify and report failure without further action. '
    'Reserve refused for an explicit request to use a prohibited arm, not for a temporarily unavailable authorized arm.'
)


def instructions(intervention, legacy=False):
    return (ORIGINAL + (CLARIFICATION if intervention == 'clarified' else '')) if legacy else NEW_CONTRACT


def make_tools(call, policy='none', legacy=False):
    tools = legacy_tools(call)
    if legacy:
        return tools

    @tool
    def read_permissions() -> dict:
        """Read currently authorized arms. Permission may be revoked during a task."""
        return call('read_permissions')

    @tool
    def inspect_target(target: str) -> dict:
        """Read current availability of the requested destination."""
        return call('inspect_target', target=target)

    tools.extend([read_permissions, inspect_target])
    if policy in ('eager', 'jtvr'):
        @tool
        def acquire_context(action: Literal['pick_object', 'place_object'], object_id: str, target: str) -> dict:
            """Acquire current observation context for a proposed action in one request. Does not act or verify."""
            return call('acquire_context', action=action, object_id=object_id, target=target)
        tools.append(acquire_context)
    return tools


def scripted(client, task):
    """Deterministic planner: public task + tool returns only, no fixture/fault access."""
    obj, target = task['object_id'], task['target']

    def verify():
        value = client.call('verify_goal')
        if value['status'] == 'UNKNOWN':
            value = client.call('verify_goal')
        return value

    def report(outcome):
        return client.call('submit_report', outcome=outcome, battery_percent=-1)

    def context(action):
        if client.policy in ('eager', 'jtvr'):
            return client.call('acquire_context', action=action, object_id=obj, target=target)['observations']
        names = ('observe_robot', 'read_permissions', 'locate_object') if action == 'pick_object' else ('observe_robot', 'read_permissions', 'inspect_target')
        return {name: client.call(name, **({'object_id': obj} if name == 'locate_object' else
                                         {'target': target} if name == 'inspect_target' else {})) for name in names}

    allowed = client.call('read_permissions')
    if 'left' not in allowed['allowed_arms']:
        verify()
        return report('failure')
    if verify()['status'] == 'SUCCESS':
        return report('success')
    for attempt in range(2):
        values = context('pick_object')
        health, pose = values['observe_robot'], values['locate_object']
        if 'left' not in values['read_permissions']['allowed_arms']:
            verify()
            return report('failure')
        if health['battery_percent'] < health['minimum_battery'] or health['holding']:
            verify()
            return report('failure')
        if pose['status'] == 'UNKNOWN':
            pose = client.call('locate_object', object_id=obj)
            if pose['status'] == 'UNKNOWN':
                verify()
                return report('unknown')
        picked = client.call('pick_object', object_id=obj, arm='left', observed_revision=pose['revision'])
        verified = verify()
        if picked.get('accepted'):
            break
        if picked.get('error') != 'revision_mismatch_refresh_pose':
            return report('unknown' if verified['status'] == 'UNKNOWN' else 'failure')
    else:
        return report('failure')
    if verified['status'] == 'UNKNOWN':
        return report('unknown')
    if verified['holding'] != obj:
        return report('failure')
    values = context('place_object')
    if not values['inspect_target'].get('available') or 'left' not in values['read_permissions']['allowed_arms']:
        verify()
        return report('failure')
    client.call('place_object', object_id=obj, arm='left', target=target)
    return report(verify()['status'].lower())
