"""Prepare the authorized G1 Stage1 control campaign, never invoke providers."""
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parent
REV=ROOT.parent
WORKSPACE=ROOT.parents[4]


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,obj):(ROOT/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'freeze.json').exists(),'Preserve each frozen attempt.'
    protected=read(REV/'preserved-files-before.json')
    for path in REV.rglob('*'):
        if path.is_file() and ROOT not in path.parents:
            protected[path.relative_to(WORKSPACE).as_posix()]=digest(path)
    changed=[name for name,value in protected.items() if digest(WORKSPACE/name)!=value]
    assert not changed,changed
    write('protected-before.json',protected)
    cases=read(REV/'cases.json')
    for domain,asset,goal in [('arm','joint fixture','yaw=-0.18 radians and pitch=0.11 radians'),
                              ('base','delivery platform','x=1.2 metres, y=-0.6 metres and heading=0.25 of a turn')]:
        spec=deepcopy(next(c for c in cases if c['split']=='dev' and c['domain']==domain and c['kind']=='write'))
        spec.update(case_id='G1r1-dev-partial-'+domain,template_group='dev.partial_'+domain,
            kind='write_fault',fault='partial',expected_status='FAILURE',nominal_healthy_world=False,
            request=(f'The signed service entry for the {asset} specifies {goal}. '
                     'Carry it out with one dispatch; document the measured final coordinates even if only part of the command takes effect.'
                     if domain=='arm' else
                     f'A delivery setup ticket requires {goal}. Position the {asset} once and include heading when judging whether the complete destination was attained.'),
            world_configuration={'write_authorized':True,'write_effect':'partial'})
        cases.append(spec)
    cases.sort(key=lambda c:(c['split']!='dev',c['domain'],c['case_id']))
    write('cases.json',cases)
    cols=['case_id','split','template_group','author','domain','kind','skill_id','native_depth','request','fault','expected_status','expected_dispatches']
    with (ROOT/'cases.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(cases)
    plan=[]
    old=read(REV/'cases.json')
    for skill in read(REV/'skills-and-depths.json'):
        case=deepcopy(next(c for c in old if c['split']=='dev' and c['skill_id']==skill['skill_id'] and c['fault'] is None))
        case['case_id']='structural-'+skill['skill_id']
        case['control_block']='structural'
        for mode in ('primitives','macro'):
            plan.append({'id':case['case_id']+'-'+mode,'block':'structural','mode':mode,'case':case,
                'expected_turns':skill['primitive_expected_model_calls'] if mode=='primitives' else skill['macro_expected_model_calls'],
                'expected_native':skill['native_depth']})
    for i,case in enumerate(cases):
        for mode in (('macro','primitives') if i%2==0 else ('primitives','macro')):
            expected=1 if case['kind']=='ambiguous' else 2 if mode=='macro' else 5 if case['kind'] in ('write','write_fault') else 3
            native=0 if case['kind']=='ambiguous' else 1 if case['kind']=='missing_prerequisite' else case['native_depth']
            plan.append({'id':case['case_id']+'-'+mode,'block':'cases','mode':mode,'case':case,
                         'expected_turns':expected,'expected_native':native})
    assert len(plan)==132 and sum(c['split']=='dev' for c in cases)==18
    write('control-plan.json',plan)
    write('settings.json',{'date':'2026-11-13','authorization':'Owner: ok commence the stage',
        'study_label':'Exploratory generalization study G1 — AI-authored cases; no independent teammate authorship or semantic-novelty review.',
        'scope':'Stage1 engineering controls only; no live model requests, OAuth or Gazebo',
        'project':'rosa-g1-ai-authored-controls-20261113','root_span':'g1.scripted.control',
        'phoenix_url':'http://127.0.0.1:6006','planned_structural_trials':20,'planned_case_trials':112,
        'dev_cases':18,'heldout_cases':38,'dev_template_groups':8,'heldout_template_groups':13,'ladder_template_groups':6,
        'native_ratio_threshold_each_inspection_depth':[.75,1.25],
        'future_proposed_caps':{'Sol_dev':291,'Sol_heldout':611,'Qwen_heldout':611,'probe_per_backend':117},
        'Stage2_authorized':False,'live_model_requests':0})
    files={p.name:digest(p) for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.py','.md','.json','.csv')
           and p.name not in ('freeze.json','status.json')}
    write('freeze.json',{'files':files,'pre_run_note_sha256':digest(ROOT/'PRE_RUN_NOTE.md'),
        'parent_revision_manifest_sha256':digest(REV/'revision-manifest.json'),
        'authorship_amendment_sha256':digest(REV/'amendments/ai-authored-20261113/manifest.json')})
    write('status.json',{'status':'PREPARED','completed':0,'planned':132,'live_model_requests':0,'Stage2_started':False})
    print(json.dumps({'frozen_files':len(files),'control_trials':132,'dev_cases':18,'heldout_cases':38,'live_model_requests':0}))


if __name__=='__main__':main()
