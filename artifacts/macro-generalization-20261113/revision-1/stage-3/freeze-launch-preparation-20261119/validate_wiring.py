"""Zero-model tests for the new execution/analysis assembly before freeze."""
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
STAGE3=HERE.parent
ROOT=STAGE3.parent/'stage-4'
sys.path.insert(0,str(ROOT))
import common
import runner
import runtime_support as support
from adjudication import summarize,project_complete_rows,PendingReview
from bind_existing_review import load_rows
from rosa_auth.oauth import SafeError
from rosa_reliability.execution import ControlledStop
from observed_transport import ObservedRecoverableSiwc

class WiringTests(unittest.TestCase):
    def test_roots_and_new_transport_are_effective(self):
        self.assertEqual(runner.ROOT,ROOT)
        self.assertEqual(runner.RecoverableSiwc,ObservedRecoverableSiwc)
        self.assertEqual(runner.Meter.__module__,'tracing')
        import tracing
        self.assertEqual(tracing.PROJECT,'rosa-g1-sol-heldout-20261119')
        self.assertEqual(tracing.ROOT_SPAN,'g1.sol.heldout')

    def test_plan_settings_and_prompts_are_unchanged(self):
        plan=common.read(ROOT/'plan.json')
        old=[r for r in common.read(common.REV/'stage-1/control-plan.json') if r['block']=='cases' and r['case']['split']=='heldout']
        self.assertEqual(plan,old)
        self.assertEqual(len(plan),76)
        self.assertEqual(len({r['case']['template_group'] for r in plan}),13)
        settings=common.read(ROOT/'settings.json')
        self.assertEqual(settings['ordinary_request_cap']+settings['reserve_cap'],611)
        self.assertEqual(settings['native_ratio_band'],[.75,1.25])
        source=(ROOT/'runner.py').read_text()
        self.assertIn("contract['condition_sentences'][item['mode']]",source)

    def test_campaign_ceiling_and_retry_rules(self):
        campaign=runner.Campaign(lambda _:None)
        for _ in range(611):campaign.reserve()
        with self.assertRaises(ControlledStop):campaign.reserve()
        self.assertEqual(campaign.requests,611)
        for _ in range(3):self.assertTrue(campaign.recovery(SafeError('http_error',503)))
        self.assertFalse(campaign.recovery(SafeError('http_error',503)))
        self.assertFalse(runner.Campaign(lambda _:None).recovery(SafeError('rate_limit_exceeded')))

    def test_failure_activity_is_recorded_before_later_tool_work(self):
        captures={}
        def write(name,value):captures[str(name)]=deepcopy(value)
        inv=SimpleNamespace(snapshot=lambda:{'operations':[]})
        meter=SimpleNamespace(tool_inputs=[])
        actor=SimpleNamespace(records=[])
        transport=SimpleNamespace(error_metadata_records=[{'failure_surface':'HTTP','http_status':503}])
        folder=ROOT/'trials'/'ZERO_MODEL_TEST'
        with patch.object(support,'write',side_effect=write):
            support.journal_progress(folder,{'calls':1},inv,meter,actor,transport,0,{'fired':False})
        value=captures['trials/ZERO_MODEL_TEST/failure-observations.json'][0]['analysis_failure_observation']
        self.assertEqual(value['tool_executions_before_failure'],0)
        self.assertEqual(value['native_operations_before_failure'],0)
        self.assertEqual(value['completed_response_in_failed_call'],False)

    def test_task_deadline_is_not_changed_into_infrastructure_censoring(self):
        captures={}
        with patch.object(support,'write',side_effect=lambda name,value:captures.update({str(name):value})):
            support.journal_progress(ROOT/'trials/ZERO_MODEL_TIMEOUT',{},SimpleNamespace(snapshot=lambda:{}),
                SimpleNamespace(tool_inputs=[]),SimpleNamespace(records=[]),
                SimpleNamespace(error_metadata_records=[{'failure_surface':'TIMEOUT'}]),0,{'fired':True})
        self.assertIsNone(captures['trials/ZERO_MODEL_TIMEOUT/failure-observations.json'][0]['analysis_failure_observation'])

    def test_new_heldout_analysis_withholds_unreviewed_semantics(self):
        rows=load_rows()
        bundle=support.empty_bundle()
        summary=summarize(rows,[r['id'] for r in rows],bundle,bundle['rubric_sha256'])
        self.assertEqual(len(summary['semantic_judgments_pending']),4)
        self.assertFalse(summary['final_correctness_ready'])
        self.assertEqual(summary['all_attempt_costs']['primitives']['calls'],60)
        with self.assertRaises(PendingReview):project_complete_rows(rows,bundle,bundle['rubric_sha256'])

def main():
    output=io.StringIO()
    with patch('socket.socket.connect',side_effect=AssertionError('unexpected_network')):
        result=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WiringTests))
    assert not (HERE/'wiring-validation.json').exists()
    (HERE/'wiring-validation.log').write_text(output.getvalue(),encoding='utf-8')
    receipt={'pass':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'model_requests':0,'network_requests':0,'historical_sources_edited':False}
    (HERE/'wiring-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    if not result.wasSuccessful():raise SystemExit(1)

if __name__=='__main__':main()
