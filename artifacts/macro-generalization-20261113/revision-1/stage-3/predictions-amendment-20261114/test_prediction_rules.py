"""Threshold/analysis development tests; not independent scorer-review cases."""
from fractions import Fraction as F
import io
import json
from pathlib import Path
import unittest
from prediction_rules import p1_status, p2_status, combine_domains, sensitivity, p4_from_probe, p4_views, point_metrics, p5_status

class PredictionTests(unittest.TestCase):
    def test_p1_constant_one(self):
        self.assertEqual(p1_status({d:F(1) for d in (1,2,4,6)}),'Support')
    def test_p1_support_edges(self):
        self.assertEqual(p1_status({1:F(1,2),2:F(1),4:F(1),6:F(1)}),'Support')
    def test_p1_one_point_spread_is_not_against(self):
        self.assertEqual(p1_status({1:F(0),2:F(1),4:F(1),6:F(1)}),'Uninformative')
    def test_p1_spread_above_one(self):
        self.assertEqual(p1_status({1:F(0),2:F(1),4:F(1),6:F(10001,10000)}),'Against')
    def test_p1_two_boundary(self):
        self.assertEqual(p1_status({d:F(2) for d in (1,2,4,6)}),'Uninformative')
        self.assertEqual(p1_status({d:F(20001,10000) for d in (1,2,4,6)}),'Against')
    def test_p1_missing_cell(self):
        self.assertEqual(p1_status({1:F(1),2:F(1),4:F(1),6:None}),'Uninformative')
    def test_p2_inclusive_band(self):
        self.assertEqual(p2_status({1:F(3,4),2:F(1),4:F(1),6:F(5,4)}),'Support')
    def test_p2_outside_band(self):
        self.assertEqual(p2_status({1:F(3,4),2:F(1),4:F(1),6:F(12501,10000)}),'Against')
        self.assertEqual(p2_status({1:F(7499,10000),2:F(1),4:F(1),6:F(1)}),'Against')
    def test_p2_undefined(self):
        self.assertEqual(p2_status({1:F(1),2:F(1),4:F(1),6:None}),'Uninformative')
    def test_domain_requirement(self):
        self.assertEqual(combine_domains({'arm':'Support','base':'Uninformative'}),'Uninformative')
        self.assertEqual(combine_domains({'arm':'Support','base':'Against'}),'Against')
    def test_sensitivity_veto(self):
        self.assertEqual(sensitivity('Support','Uninformative'),'Uninformative')
        self.assertEqual(sensitivity('Against','Support'),'Uninformative')
        self.assertEqual(sensitivity('Support','Support',compromised=True),'Uninformative')
        self.assertEqual(sensitivity('Support','Support',campaign_complete=False),'Uninformative')
    @staticmethod
    def probe(n, correct_last):
        return [dict(case_id=f'case{i}',backend='qwen',catalogue_size=size,
                     selection_correct=size!=10 or i<correct_last)
                for i in range(n) for size in (3,5,10)]
    def test_p4_exact_twenty_against(self):
        result=p4_from_probe(self.probe(5,4))
        self.assertEqual(result['status'],'Against')
        self.assertEqual(result['worst_accuracy_fall'],.2)
    def test_p4_under_twenty_support(self):
        self.assertEqual(p4_from_probe(self.probe(100,81))['status'],'Support')
    def test_p4_no_or_incomplete_probe(self):
        self.assertEqual(p4_from_probe([])['status'],'Uninformative')
        self.assertEqual(p4_from_probe(self.probe(5,5)[:-1])['status'],'Uninformative')
    def test_p4_other_catalogue_rejected(self):
        with self.assertRaises(ValueError):
            p4_from_probe([dict(case_id='c',backend='qwen',catalogue_size=6,selection_correct=True)])
    def test_p4_censor_sensitivity(self):
        rows=self.probe(5,5)
        rows[-1]['censored']=True
        result=p4_views(rows)
        self.assertEqual(result['V2']['status'],'Support')
        self.assertEqual(result['V3']['status'],'Against')
        self.assertEqual(result['final'],'Uninformative')
    @staticmethod
    def paired(case_id, difference=1, primitive_native=2, macro_native=2):
        common=dict(case=dict(case_id=case_id,domain='arm',kind='ladder',depth_analysis=True,native_depth=2),primary_pass=True)
        return [dict(**common,id=case_id+'-p',mode='primitives',inference={'calls':2+difference},actor_records=[{}]*primitive_native),
                dict(**common,id=case_id+'-m',mode='macro',inference={'calls':2},actor_records=[{}]*macro_native)]
    def test_whole_pair_weights_preserved(self):
        first=self.paired('first',1)
        second=self.paired('second',2)
        metrics,cells=point_metrics(first+first+second,set(),'V2')
        self.assertAlmostEqual(metrics['arm/depth2/absolute_calls_saved'],4/3)
        self.assertEqual(next(c for c in cells if c['domain']=='arm' and c['depth']==2)['matched_success_pairs'],3)
    def test_censor_removes_entire_pair(self):
        rows=self.paired('c')
        metrics,cells=point_metrics(rows,{'c-p'},'V2')
        self.assertIsNone(metrics['arm/depth2/absolute_calls_saved'])
        self.assertIsNone(metrics['arm/depth2/native_ratio'])
        self.assertEqual(next(c for c in cells if c['domain']=='arm' and c['depth']==2)['excluded_censored_pairs'],1)
    def test_zero_primitive_denominator_not_imputed(self):
        metrics,_=point_metrics(self.paired('c',primitive_native=0),{'c-p'},'V3')
        self.assertIsNone(metrics['arm/depth2/native_ratio'])
    def test_p5_controls_and_source_changes(self):
        self.assertEqual(p5_status([],False),'Uninformative')
        self.assertEqual(p5_status([],True),'Support')
        self.assertEqual(p5_status(['hosting-diff'],True),'Against')

if __name__=='__main__':
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PredictionTests))
    root=Path(__file__).resolve().parent
    (root/'prediction-tests.log').write_text(output.getvalue(),encoding='utf-8')
    (root/'prediction-tests.json').write_text(json.dumps(dict(passed=result.wasSuccessful(),methods=result.testsRun,
        errors=len(result.errors),failures=len(result.failures),model_requests=0,independent_scorer_review=False),indent=2)+'\n',encoding='utf-8')
    print(dict(passed=result.wasSuccessful(),methods=result.testsRun))
    raise SystemExit(0 if result.wasSuccessful() else 1)
