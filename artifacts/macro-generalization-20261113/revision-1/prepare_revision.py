"""Prepare G1-r1 Stage 0 only. Outputs never escape revision-1."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import shutil

from worlds import DOMAINS

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent
WORKSPACE = ROOT.parents[3]
REPO = WORKSPACE/'rosa-evaluation'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def protect():
    protected = load(OLD/'protected-files-before.json')
    for p in OLD.rglob('*'):
        if p.is_file() and ROOT not in p.parents:
            protected[p.relative_to(WORKSPACE).as_posix()] = digest(p)
    return protected


INSPECTION_HELD = [
    'The handover form needs a verdict for the {asset} on these sources: {checks}. Fill only that entry; keep actuators unchanged.',
    'During this audit, observation access for the {asset} is restricted to {checks}. Are the listed conditions satisfied? No positioning command is authorized.',
    'A technician needs a condition record for the {asset} covering {checks}; no other acquisition or movement is authorized.',
    'Decide whether the following checks for the {asset} are all true: {checks}. This is a read-only ticket with that exact scope.',
    'Complete a condition-only handover for the {asset}: {checks}. Limit observation to that list and identify any unknown.',
    'Log the observed condition of the {asset} using {checks}. This job permits only the listed observations.',
]
INSPECTION_DEV = [
    'For the {asset}, finish a read-only service entry consisting exactly of {checks}. Classify the observed conditions.',
    'Record a stationary condition summary for the {asset}. Authorized sources are {checks}, with no additional acquisitions.',
]
MOVEMENT_HELD = [
    'The commissioning card assigns the {asset} this final coordinate set: {goal}. Carry out that positioning job and return an observation-grounded verdict.',
    'A technician signed off the following {asset} position request: {goal}. Complete it once and assess the resulting coordinates.',
    'Finish the {asset} positioning portion of the work order at {goal}, then record whether the measured coordinates satisfy it.',
]
MOVEMENT_DEV = [
    'Execute the positioning entry for the {asset}: {goal}. A current coordinate observation is required before dispatch; report the observed result.',
    'Put the {asset} at the coordinates on this service label, {goal}, with one permitted dispatch and an evidence-grounded final status.',
]


def skill_table():
    result=[]
    for domain,spec in DOMAINS.items():
        for i,d in enumerate((1,2,4,6)):
            result.append({'domain':domain,'skill_id':spec['ids'][i],'kind':'inspection','native_depth':d,
                'checks':{source:[field] for source,field in spec['checks'][:d]},
                'primitive_expected_model_calls':3,'macro_expected_model_calls':2,
                'primitive_sequence':['select_skill','read_state(all selected source groups)','submit_report'],
                'macro_sequence':['select_skill -> verify_outcome(all selected source groups)','submit_report'],
                'reads':'independent','actual_turn_counts':'not recorded; Stage 1 verification pending'})
        result.append({'domain':domain,'skill_id':spec['ids'][4],'kind':'movement','native_depth':3,
            'targets':{spec['node']:spec['target']},'primitive_expected_model_calls':5,'macro_expected_model_calls':2,
            'primitive_sequence':['select_skill','read_state','write_state','verify_outcome','submit_report'],
            'macro_sequence':['select_skill -> read_state/conditional write_state/verify_outcome','submit_report'],
            'reads':'post-write verification depends on the dispatch',
            'actual_turn_counts':'not recorded; Stage 1 verification pending'})
    return result


def make_cases():
    cases=[]
    def add(split,domain,kind,index,group,request,fault=None,status='SUCCESS'):
        spec=DOMAINS[domain]
        skill=None if kind=='ambiguous' else spec['ids'][index]
        inspect=kind in ('ladder','unavailable_source')
        depth=(1,2,4,6)[index] if inspect else None if kind=='ambiguous' else 3
        world={'write_authorized':kind in ('write','missing_prerequisite','write_fault')}
        if fault=='known_false': world['false_source']=spec['checks'][0][0]
        if fault=='source_timeout': world['unavailable_source']=spec['checks'][0][0]
        if fault=='missing_pose':
            world['pose_unavailable']=True
            if domain=='base': world['false_source']='localization'
        if fault=='partial': world['write_effect']='partial'
        if fault=='ineffective': world['write_effect']='ineffective'
        writes=int(kind in ('write','write_fault'))
        cases.append({'case_id':f'G1r1-{split}-{len(cases)+1:03d}','split':split,'domain':domain,
            'template_group':group,'author':'Codex (AI)','independent_author':False,'authorship_verified':True,
            'kind':kind,'skill_id':skill,'native_depth':depth,'depth_analysis':kind=='ladder',
            'request':request,'fault':fault,'world_configuration':world,'expected_status':None if kind=='ambiguous' else status,
            'expected_dispatches':writes,'nominal_healthy_world':fault is None,'state':'DRAFT_NOT_RUN',
            'semantic_novelty_review':'not independently reviewed'})
    for split in ('dev','heldout'):
        for domain_index,(domain,spec) in enumerate(DOMAINS.items()):
            asset='articulated test fixture' if domain=='arm' else 'delivery platform'
            goal=', '.join(f'{key}={value} {spec["units"][key]}' for key,value in spec['target'].items())
            for i,d in enumerate((1,2,4,6)):
                for rep in range(1 if split=='dev' else 3):
                    template_index=i%2 if split=='dev' else (i+rep+3*domain_index)%6
                    template=(INSPECTION_DEV if split=='dev' else INSPECTION_HELD)[template_index]
                    fault=None if split=='dev' or rep==0 else 'known_false' if rep==1 else 'source_timeout'
                    expected='SUCCESS' if fault is None else 'FAILURE' if fault=='known_false' else 'UNKNOWN'
                    checks=', '.join(field for source,field in spec['checks'][:d])
                    add(split,domain,'ladder',i,f'{split}.inspection.{template_index+1}',
                        template.format(asset=asset,checks=checks),fault,expected)
            for i,template in enumerate(MOVEMENT_DEV if split=='dev' else MOVEMENT_HELD):
                add(split,domain,'write',4,f'{split}.positioning.{i+1}',template.format(asset=asset,goal=goal))
            if split=='dev':
                extras=[('missing_prerequisite','missing_pose','UNKNOWN',
                         f'A service instruction authorizes {goal} for the {asset}. Absence of current coordinate evidence must leave the actuator idle.'),
                        ('ambiguous',None,None,f'You are responsible for the {asset} service handover. Please take care of it.')]
            else:
                extras=[('missing_prerequisite','missing_pose','UNKNOWN',
                         f'The {asset} has a positioning assignment of {goal}. Coordinate evidence is mandatory before acting; record any inability to obtain it.'),
                        ('ambiguous',None,None,f'The next shift is expecting the {asset}. Its handover is yours to arrange.'),
                        ('write_fault','ineffective' if domain=='arm' else 'partial','FAILURE',
                         f'This {asset} work-order entry calls for {goal}. Use one dispatch and document any discrepancy across the full coordinate set.'),
                        ('unavailable_source','source_timeout','UNKNOWN',
                         f'For the {asset}, the supervisor requires a read-only finding from '+
                         ', '.join(field for source,field in spec['checks'][:2])+'. These are the only authorized acquisitions.')]
            for kind,fault,expected,request in extras:
                add(split,domain,kind,None if kind=='ambiguous' else 1 if kind=='unavailable_source' else 4,
                    f'{split}.{kind}',request,fault,expected)
    return cases


def make_resources():
    old=load(REPO/'artifacts/macro-m4-20261027/analysis.json')['backends']
    output={'fixed_limits':{'model_calls':8,'observed_output_tokens':2048,'native_operations':10,
        'tool_attempts':16,'corrections':3,'dispatches':1,'task_seconds':360,'campaign_seconds':28800},
        'infrastructure':{'eligible_http':[502,503,504],'per_logical_retry_cap':1,'separate_reserve':3,'backoff_seconds':1,
            'exclude':'quota/auth/scope/token/grant/client; ordinary timeout; length; task failure; invalid tools'},
        'ceilings':{},'M4_scale_projections':{},'provider_quota':'not recorded'}
    for key,count in [('Sol_dev',16),('Sol_heldout',38),('Qwen_heldout',38)]:
        logical=count*2*8
        output['ceilings'][key]={'cases':count,'trials':count*2,'ordinary_logical_cap':logical,
                                'infrastructure_reserve':3,'physical_request_ceiling':logical+3}
    output['ceilings']['Stage4b_each_backend']={'cases':38,'catalogue_sizes':[3,5,10],
        'condition_sentence':'macro only','ordinary_logical_cap':38*3,'infrastructure_reserve':3,
        'physical_request_ceiling':38*3+3,'no_tool_execution':True}
    output['ceilings']['Stage4b_both_backends']={'ordinary_logical_cap':38*3*2,'infrastructure_reserve':6,'physical_request_ceiling':234}
    for backend,count,label in [('siwc',16,'Sol_dev'),('siwc',38,'Sol_heldout'),('ollama',38,'Qwen_heldout')]:
        data=old[backend]
        by=data['conditions']
        factor=2*count/40
        def total(field): return sum(r[field] for r in by.values())
        output['M4_scale_projections'][label]={'kind':'Estimate from recorded M4 all-attempt per-task averages, not new measurement',
            'M4_trials':40,'projected_trials':2*count,'scale_factor':factor,
            'estimated_requests':total('model_requests')*factor,
            'estimated_input_tokens':total('known_input_tokens')*factor,
            'estimated_output_tokens':total('known_output_tokens')*factor,
            'estimated_sum_task_seconds':total('task_wall_seconds')*factor,
            'estimated_campaign_seconds':data['total_elapsed_seconds']*factor,
            'M4_per_condition_calls_per_task':{c:r['model_requests']/20 for c,r in by.items()},
            'limits':'Changed domain, catalogue, inspection depth, fault mix and initial states may invalidate this scale projection; no runtime promise.'}
    output['Stage4b_expected_requests']='114/backend before eligible retries; first-turn latency/token consumption not estimated from whole-task averages'
    output['M4_Sol_local_cap']={'used':106,'cap':323,'not_a_provider_quota':True}
    return output


def main():
    assert not (ROOT/'revision-checkpoint.json').exists(), 'Preserve a sealed revision; use an explicit amendment.'
    # Older proposal and its STOPPED status remain untouched.
    protected=protect(); save('preserved-files-before.json',protected)
    old_manifest=load(OLD/'stage0-manifest.json')['files']
    assert all(digest(OLD/name)==value for name,value in old_manifest.items()),'old_package_changed'
    old_protected=load(OLD/'protected-files-before.json')
    assert all(digest(WORKSPACE/name)==value for name,value in old_protected.items()),'historical_file_changed'
    skills=skill_table(); cases=make_cases(); resources=make_resources()
    assert Counter(c['split'] for c in cases)=={'dev':16,'heldout':38}
    groups={split:sorted({c['template_group'] for c in cases if c['split']==split}) for split in ('dev','heldout')}
    assert not set(groups['dev']) & set(groups['heldout'])
    assert len(groups['heldout'])>=8
    save('skills-and-depths.json',skills); save('cases.json',cases); save('resources.json',resources)
    columns=['case_id','split','template_group','author','independent_author','domain','kind','skill_id',
             'native_depth','depth_analysis','request','fault','expected_status','expected_dispatches','state']
    with (ROOT/'cases.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(cases)
    save('template-groups.json',{'groups':groups,'counts':{k:len(v) for k,v in groups.items()},
        'heldout_ladder_groups':len({c['template_group'] for c in cases if c['split']=='heldout' and c['kind']=='ladder'}),
        'group_definition':'Shared linguistic scaffold, including paraphrases and substitutions, across domains/depths stays in one group.',
        'independent_authors':0,'teammate_gate':'UNMET: 0 of54 cases independently teammate-authored; no such authorship invented.'})
    components=load(OLD/'M4_PROMPT_COMPONENTS.json')
    suffix='Limits: eight charged model calls, 2048 observed generated tokens, 1024 local tokens per call, ten native acquisitions/commands, sixteen tool attempts, three corrections, 360 seconds and at most one movement dispatch. Joint tolerance 0.025 radians.\nUser: '
    replacement='Position tolerance 0.025 metres; fraction tolerance 0.025.'
    save('prompt-contract.json',{'system':components['system_prompt'],'rules':components['rules'],
        'condition_sentences':components['condition_sentences'],'arm_suffix':suffix,
        'base_suffix':suffix.replace('Joint tolerance 0.025 radians.',replacement),
        'only_domain_substitution':{'from':'Joint tolerance 0.025 radians.','to':replacement},
        'Qwen':{'num_ctx':8192,'num_predict':1024,'temperature':0,'seed':42,'think':False,'FA':'original unset/auto effective-enabled','KV':'f16'},
        'weights_digest':'56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'})
    table=['# Revised skills and nominal paths','','**Expected counts only. Stage 1 structural checks have not run.**','',
           '| ID | Native depth | Primitive model turns | Macro model turns | Primitive public tools | Macro public tools |',
           '|---|---:|---:|---:|---|---|']
    for s in skills:
        table.append(f'| {s["skill_id"]} | {s["native_depth"]} | {s["primitive_expected_model_calls"]} | '
                     f'{s["macro_expected_model_calls"]} | '+ ' → '.join(s['primitive_sequence'])+' | '+ ' → '.join(s['macro_sequence'])+' |')
    table+=['','All ten definitions use only StateSkill or InspectionSkill, registered through CapabilityRegistry. '
            'There are5 skills/domain and10 combined. Skill IDs have no depth labels. Source groups each reserve a separate native operation through the unchanged API. '
            'No extra catalogue descriptions are added.','',
            'Healthy initially off-target movement:3 native operations,5 primitive turns versus2 macro turns. '
            'Missing current pose: expected read then UNKNOWN/no dispatch,3 primitive turns versus2 macro turns,1 native attempt. '
            'Read-only unavailable/false observations can be reported directly; no automatic continuation is added. '
            'Clarification expects1 model response and0 native operations. These are proposed reference paths, not live performance results.','',
            'p3 write anchors, selective acquisition and horizon-dependent reliability are deferred to G2.']
    (ROOT/'SKILL_DEPTH_TABLE.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    # This catches exact strings only; it is not independent semantic novelty review.
    import ast
    tree=ast.parse((REPO/'experiments/macro_m4/design.py').read_text())
    literals={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
    save('case-design-check.json',{'case_counts':dict(Counter(c['split'] for c in cases)),
        'template_group_counts':{k:len(v) for k,v in groups.items()},'cross_split_group_overlap':[],
        'exact_M4_literal_duplicates':[c['case_id'] for c in cases if c['request'] in literals],
        'semantic_M4_novelty':'not independently reviewed; requests were newly drafted, not adapted from M4',
        'authors':{'Codex (AI)':54},'teammate_authorship_gate_met':False,
        'runtime_solvability':'not recorded; Stage1 pending','prompt_token_counts':'not recorded'})
    save('revision-checkpoint.json',{'date':'2026-11-13','study':'exploratory generalization study G1, revision1',
        'status':'STAGE0_PREPARED_PENDING_CONFIRMATION_AND_AUTHORSHIP_GATE',
        'source_changes':False,'model_requests':0,'Stage1_started':False,'all_cases_AI_authored':True,
        'original_teammate_gate_met':False,'design_confirmation':False,'controls_turn_counts':'not recorded',
        'pre_run_note_sha256':digest(ROOT/'PRE_RUN_NOTE.md'),'old_STOPPED_status_preserved':True,
        'case_counts':{'dev':16,'heldout':38},'template_group_counts':{k:len(v) for k,v in groups.items()}})
    print(json.dumps({'cases':len(cases),'groups':{k:len(v) for k,v in groups.items()},'model_requests':0,
                      'protected_files':len(protected),'pre_run_note_sha256':digest(ROOT/'PRE_RUN_NOTE.md')}))


if __name__=='__main__':main()
