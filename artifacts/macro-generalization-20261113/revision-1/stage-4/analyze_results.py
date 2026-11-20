"""Pending-safe analysis; no new human labels or final verdicts are invented."""
import importlib.util
from pathlib import Path
import sys
from common import ROOT,REV,STAGE3,read,write,verify
from runtime_support import empty_bundle
from adjudication import summarize,project_complete_rows

def main():
    verify()
    paths=sorted((ROOT/'trials').glob('*/result.json'))
    rows=[read(p) for p in paths]
    bundle=read(ROOT/'human-review-bound.json') if (ROOT/'human-review-bound.json').exists() else empty_bundle()
    schedule=read(ROOT/'plan.json')
    summary=summarize(rows,[r['id'] for r in schedule],bundle,bundle['rubric_sha256'])
    summary['study_label']='AI-authored cases; no independent generalization claim'
    summary['scope']='G1 Sol held-out; preliminary until all required human judgments exist'
    write('analysis/current.json',summary)
    if not summary['final_correctness_ready']:
        write('analysis/verdict.json',{'status':'WITHHELD','reason':'Pending human judgments or missing results',
            'pending':summary['semantic_judgments_pending'],'unstarted':summary['unstarted'],
            'all_costs_preserved':True})
        return
    source=STAGE3/'predictions-amendment-20261114/run_analysis.py'
    sys.path.insert(0,str(source.parent))
    spec=importlib.util.spec_from_file_location('frozen_g1_prediction_analysis',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    projected=project_complete_rows(rows,bundle,bundle['rubric_sha256'])
    output=ROOT/'analysis/final'
    output.mkdir(exist_ok=False)
    result=module.analyze(projected,schedule,{read(p)['id']:p.parent for p in paths},output,
                          scope='heldout',hosting_source_changes=(),fresh_controls_passed=True)
    write('analysis/final/results.json',result)

if __name__=='__main__':main()
