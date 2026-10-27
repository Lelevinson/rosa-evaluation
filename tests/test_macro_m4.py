from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr
from rosa_auth.oauth import SafeError
from rosa_reliability.bounded_macro import MacroLimits
from rosa_reliability.execution import ControlledStop
from rosa_reliability.macro_agent import InferenceLimits, MacroROSA
from rosa_reliability.ros_arm import HOME_POSE
from experiments.macro_m4.design import LIMITS, cases, jobs, query, registry
from experiments.macro_m4.recovery import CampaignBudget, RecoveryGate, RecoverableSiwc, transient
from experiments.macro_m4.runner import reference
from experiments.macro_m4.scoring import score


class Arm:
    requires_observation = True
    def __init__(self, spec):
        self.spec, self.values, self.records = spec, deepcopy(registry().catalogue()[spec['initial']]['targets']['/ur5e']), []
    def read(self, node, names):
        if self.spec['fault'] == 'missing_motion':
            self.records.append({'kind': 'observation_timeout'})
            raise TimeoutError('synthetic_missing')
        return dict(self.values)
    def write(self, node, values):
        self.records.append({'kind': 'trajectory_request', 'published': self.spec['fault'] != 'ineffective',
            'injected_partial': self.spec['fault'] == 'partial'})
        if self.spec['fault'] != 'ineffective': self.values = dict(values)
        if self.spec['fault'] == 'partial': self.values['wrist_3_joint'] = HOME_POSE['wrist_3_joint']
        return {'accepted_locally': True}


class Inspection:
    def __init__(self, spec): self.spec = spec
    def read_group(self, source, names):
        if self.spec['fault'] == source: raise TimeoutError('synthetic_missing')
        return {n: not (self.spec['fault'] == 'inactive' and n == 'trajectory_controller_active') for n in names}


def fixture(spec, mode):
    arm = Arm(spec)
    inv = registry().open({'state': arm, 'inspection': Inspection(spec)}, mode=mode,
        allowed_skills=spec['allowed'], limits=MacroLimits(seconds=360.0))
    return inv, arm


class SequenceModel:
    def __init__(self, values): self.values = iter(values)
    def invoke(self, *args, **kwargs):
        value = next(self.values)
        if isinstance(value, Exception): raise value
        return value


def good_message(reason='stop'):
    return AIMessage(content='Which authorized task do you want?',
        usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15},
        response_metadata={'finish_reason': reason})


class ScriptedModel(BaseChatModel):
    _inv: object = PrivateAttr()
    _step: int = PrivateAttr(default=0)
    _fail_first: bool = PrivateAttr(default=True)
    def __init__(self, invocation):
        super().__init__()
        self._inv = invocation
    @property
    def _llm_type(self): return 'offline-m4-contract-test'
    def bind_tools(self, tools, **kwargs): return self
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self._fail_first:
            self._fail_first = False
            raise SafeError('http_error', 503)
        index = self._step
        self._step += 1
        targets = registry().catalogue()['ur5e.stage_left']['targets']['/ur5e']
        steps = [('select_skill', {'skill_id': 'ur5e.stage_left'})]
        if self._inv.mode == 'primitives':
            steps.extend([('read_state', {'nodes': ['/ur5e']}),
                ('write_state', {'node_name': '/ur5e', 'values': targets}), ('verify_outcome', {})])
        name, args = steps[index] if index < len(steps) else ('submit_report',
            {'status': 'SUCCESS', 'observation_id': self._inv.session.observations[-1]['observation_id']})
        message = AIMessage(content='', tool_calls=[{'name': name, 'args': args, 'id': f'call-{index}', 'type': 'tool_call'}],
            usage_metadata={'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15},
            response_metadata={'finish_reason': 'stop'})
        return ChatResult(generations=[ChatGeneration(message=message)])


class M4Tests(unittest.TestCase):
    def test_real_rosa_loop_uses_recovery_gate_without_replaying_native_work(self):
        for mode, calls in (('macro', 3), ('primitives', 6)):
            inv, arm = fixture(cases()[0], mode)
            campaign = CampaignBudget(lambda value: None)
            agent = MacroROSA(ScriptedModel(inv), inv, backend='scripted')
            gate = RecoveryGate(inv, backend='scripted', campaign=campaign, sleeper=lambda seconds: None)
            agent.inference_budget = agent.completion_gate = gate
            answer = agent.invoke(query(cases()[0], mode))
            self.assertTrue(json.loads(answer)['report_accepted'])
            self.assertEqual(campaign.requests, calls)
            self.assertEqual(gate.snapshot()['calls'], calls)
            self.assertEqual(campaign.retries, 1)
            self.assertEqual(len(arm.records), 1)

    def test_paired_complete_schedule_and_counterbalanced_condition_order(self):
        for backend in ('ollama', 'siwc'):
            plan = jobs(backend)
            self.assertEqual(len(plan), 40)
            self.assertEqual(len({(j['case']['id'], j['repetition'], j['condition']) for j in plan}), 40)
            self.assertEqual(sum(j['condition'] == 'macro' for j in plan), 20)
            for index in range(0, 40, 2):
                self.assertEqual(plan[index]['case'], plan[index + 1]['case'])
                self.assertNotEqual(plan[index]['condition'], plan[index + 1]['condition'])
            self.assertEqual(sum(plan[i]['condition'] == 'macro' for i in range(0, 40, 2)), 10)
        for a, b in zip(jobs('ollama'), jobs('siwc')): self.assertNotEqual(a['condition'], b['condition'])
        self.assertEqual(LIMITS['backend_requests'], 40 * 8 + 3)
        self.assertGreaterEqual(LIMITS['backend_seconds'], 40 * (360 + 120 + 60) + 180)

    def test_read_only_permissions_targets_and_hidden_labels(self):
        for spec in cases():
            for condition in ('macro', 'primitives'):
                text = query(spec, condition)
                for key in ('expected_status', 'fault', 'initial_skill', 'injected_partial', 'required_dispatches'):
                    self.assertNotIn(key, text)
            if spec['kind'] != 'movement': self.assertEqual(spec['allowed'], ['ur5e.inspect_readiness'])
        for definition in registry().catalogue().values():
            for field, value in definition.get('targets', {}).get('/ur5e', {}).items():
                self.assertLessEqual(abs(value - HOME_POSE[field]), .4)

    def test_all_twenty_control_paths_and_independent_scores(self):
        for spec in cases():
            for mode in ('primitives', 'macro'):
                with self.subTest(case=spec['id'], condition=mode):
                    inv, arm = fixture(spec, mode)
                    answer = reference(inv, spec, mode, {})
                    checks = {'trajectory_controller_active': spec['fault'] != 'inactive',
                        'joint_state_broadcaster_active': True, 'joint_sample_fresh': True}
                    scored = score(spec, inv.snapshot(), answer, arm.records, arm.values, checks)
                    self.assertTrue(scored['pass'], scored)
                    self.assertLessEqual(len(inv.snapshot()['operations']), 10)

    def test_truthful_wrong_goal_and_unexercised_fault_cannot_pass(self):
        spec = cases()[-1]
        inv, arm = fixture(spec, 'macro')
        inv.execute('ur5e.inspect_readiness')
        observation = inv.session.observations[-1]
        inv.submit_report('SUCCESS', observation['observation_id'])
        scored = score(spec, inv.snapshot(), '{}', arm.records, arm.values, {})
        self.assertFalse(scored['pass'])
        self.assertTrue(scored['accepted_success_wrong_user_goal'])
        spec = next(s for s in cases() if s['fault'] == 'ineffective')
        inv, arm = fixture(spec, 'macro')
        reference(inv, spec, 'macro', {})
        scored = score(spec, inv.snapshot(), '{}', [], arm.values, {})
        self.assertFalse(scored['pass'])
        self.assertFalse(scored['injected_fault_exercised'])

    def test_transient_retry_keeps_physical_cost_and_charges_successful_decision(self):
        inv, arm = fixture(cases()[0], 'macro')
        saved = []
        campaign = CampaignBudget(lambda value: saved.append(value))
        journal = []
        gate = RecoveryGate(inv, backend='ollama', campaign=campaign,
            journal=lambda value: journal.append(value), sleeper=lambda seconds: None)
        gate.invoke(SequenceModel([SafeError('http_error', 503), good_message()]), [])
        snap = gate.snapshot()
        self.assertEqual((snap['calls'], snap['decision_calls'], campaign.retries), (2, 1, 1))
        self.assertFalse(snap['usage_complete'])
        self.assertTrue(snap['returned_usage_valid'])
        self.assertIsNone(snap['output_upper_bound'])
        self.assertEqual([e['physical_request_index'] for e in snap['events']], [1, 2])
        self.assertEqual(campaign.requests, 2)
        self.assertTrue(journal)
        self.assertFalse(inv.snapshot()['operations'])

    def test_no_recovery_for_quota_auth_timeout_truncation_or_bad_tool_output(self):
        for error in (SafeError('subscription_sharing_quota', 503), SafeError('invalid_grant', 503),
                SafeError('http_error', 429), TimeoutError('timeout'), ControlledStop('truncated')):
            inv, _ = fixture(cases()[0], 'macro')
            campaign = CampaignBudget(lambda value: None)
            gate = RecoveryGate(inv, backend='ollama', campaign=campaign, sleeper=lambda seconds: None)
            with self.assertRaises(type(error)): gate.invoke(SequenceModel([error]), [])
            self.assertEqual(campaign.requests, 1)
            self.assertEqual(campaign.retries, 0)
        inv, _ = fixture(cases()[0], 'macro')
        campaign = CampaignBudget(lambda value: None)
        gate = RecoveryGate(inv, backend='ollama', campaign=campaign)
        with self.assertRaises(ControlledStop): gate.invoke(SequenceModel([good_message('length')]), [])
        self.assertEqual(campaign.retries, 0)

    def test_retry_once_and_shared_reserve_hard_ceiling(self):
        inv, _ = fixture(cases()[0], 'macro')
        campaign = CampaignBudget(lambda value: None)
        gate = RecoveryGate(inv, backend='ollama', campaign=campaign, sleeper=lambda seconds: None)
        with self.assertRaises(SafeError):
            gate.invoke(SequenceModel([SafeError('http_error', 503), SafeError('http_error', 503)]), [])
        self.assertEqual((campaign.requests, campaign.retries), (2, 1))
        self.assertTrue(campaign.recovery(SafeError('http_error', 502)))
        self.assertTrue(campaign.recovery(SafeError('http_error', 504)))
        self.assertFalse(campaign.recovery(SafeError('http_error', 503)))
        campaign.requests = 323
        with self.assertRaises(ControlledStop): campaign.reserve()

    def test_only_matching_transient_siwc_failure_can_be_released(self):
        transport = RecoverableSiwc('SYNTHETIC_NOT_A_TOKEN')
        transport._unavailable = ('http_error', 503)
        transport.release_transient_failure(SafeError('http_error', 503))
        self.assertIsNone(transport.availability_error)
        transport._unavailable = ('invalid_grant', 401)
        with self.assertRaises(ControlledStop): transport.release_transient_failure(SafeError('invalid_grant', 401))
        self.assertIsNotNone(transport.availability_error)

    def test_analysis_never_rewards_cheap_failed_macro_or_assumes_missing_cells(self):
        import experiments.macro_m4.analysis as module
        rows = []
        for job in jobs('siwc'):
            passed = job['condition'] == 'primitives'
            rows.append({'job': {'id': job['id']}, 'case': job['case']['id'],
                'repetition': job['repetition'], 'condition': job['condition'], 'answer': 'Which goal?',
                'primary_pass': passed, 'completion_including_recovery': passed,
                'local_audit': {'pass': True}, 'phoenix_audit': {'pass': True},
                'inference': {'calls': 5 if passed else 1, 'decision_calls': 5 if passed else 1,
                    'known_input_tokens': 10, 'known_output_tokens': 5, 'usage_complete': True},
                'score': {'pass': passed, 'dispatch_violations': [], 'native_operations': 3,
                    'invalid_attempts': 0, 'accepted_success_wrong_user_goal': False, 'unsupported_success_attempts': 0},
                'infrastructure_recovered': False, 'wall_seconds': 1.})
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'siwc').mkdir()
            (base / 'siwc/checkpoint.json').write_text(json.dumps({'status': 'COMPLETE', 'trials': rows,
                'current_trial': None, 'campaign': {}, 'simulator_cleanup': {}, 'total_elapsed_seconds': 1}))
            with patch.object(module, 'BASE', base), patch('builtins.print'):
                result = module.analyze()
            sol = result['backends']['siwc']
            self.assertEqual(sol['matched_primary_success_pairs'], 0)
            self.assertIsNone(sol['matched_call_reduction'])
            self.assertFalse(sol['engineering_screen_pass'])
            self.assertEqual(result['backends']['ollama']['status'], 'UNSTARTED')
            self.assertFalse(result['complete'])


if __name__ == '__main__': unittest.main()
