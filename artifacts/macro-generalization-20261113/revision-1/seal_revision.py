"""Mechanical Stage0 checks and local integrity seal, never model/control execution."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def main():
    cases,skills,resources=read('cases.json'),read('skills-and-depths.json'),read('resources.json')
    issues=[]
    def check(condition,name):
        if not condition:issues.append(name)
    check(Counter(c['split'] for c in cases)=={'dev':16,'heldout':38},'case_counts')
    check(len({c['case_id'] for c in cases})==54,'case_ids')
    check(len(skills)==10 and Counter(s['domain'] for s in skills)=={'arm':5,'base':5},'skills')
    held=[c for c in cases if c['split']=='heldout']
    for domain in ('arm','base'):
        for d in (1,2,4,6):
            check(sum(c['domain']==domain and c['kind']=='ladder' and c['native_depth']==d for c in held)==3,
                  f'ladder:{domain}/{d}')
        check(sum(c['domain']==domain and c['kind']=='write' for c in held)==3,'write:'+domain)
        for kind in ('missing_prerequisite','ambiguous','write_fault','unavailable_source'):
            check(sum(c['domain']==domain and c['kind']==kind for c in held)==1,f'extra:{domain}/{kind}')
    groups={split:{c['template_group'] for c in cases if c['split']==split} for split in ('dev','heldout')}
    check(not groups['dev']&groups['heldout'],'split_leak')
    check(len(groups['heldout'])>=8,'heldout_template_minimum')
    check(all(c['author']=='Codex (AI)' and c['independent_author'] is False for c in cases),'false_authorship')
    check(not read('case-design-check.json')['exact_M4_literal_duplicates'],'exact_M4_duplicate')
    limits={'model_calls':8,'observed_output_tokens':2048,'native_operations':10,'tool_attempts':16,
            'corrections':3,'dispatches':1,'task_seconds':360,'campaign_seconds':28800}
    check(resources['fixed_limits']==limits,'M4_limits_changed')
    for name,n in [('Sol_dev',16),('Sol_heldout',38),('Qwen_heldout',38)]:
        cap=resources['ceilings'][name]
        check(cap['trials']==n*2 and cap['ordinary_logical_cap']==n*2*8 and
              cap['physical_request_ceiling']==n*2*8+3,'ceiling:'+name)
    check(resources['ceilings']['Stage4b_each_backend']['physical_request_ceiling']==117,'probe_cap')
    probe=read('catalogue-probe-plan.json')
    check(probe['cases']==38 and probe['responses_per_backend']==114 and probe['macro_sentence_only'],'probe_count')
    catalogues=read('catalogues.json')
    for row in probe['plan']:
        for count in (3,5,10):
            check(len(row['catalogues'][str(count)])==count,'catalogue_size:'+row['case_id'])
            if row['expected_skill'] is not None:
                check(row['expected_skill'] in row['catalogues'][str(count)],'target_missing:'+row['case_id'])
    for domain in ('arm','base'):
        check(len(catalogues['domains'][domain])==5,'public_catalogue:'+domain)
    check(len(catalogues['combined'])==10,'combined_catalogue')
    pairs=read('paired-order-proposal.json')['jobs']
    for label,n in [('siwc_dev',16),('siwc_heldout',38),('ollama_heldout',38)]:
        rows=pairs[label]
        check(len(rows)==n*2,'pair_count:'+label)
        firsts=Counter()
        for offset in range(0,len(rows),2):
            a,b=rows[offset:offset+2]
            check(a['case_id']==b['case_id'] and {a['condition'],b['condition']}=={'macro','primitives'},'pair_shape:'+label)
            firsts[a['condition']]+=1
        check(firsts['macro']==firsts['primitives'],'pair_order_balance:'+label)
    prompt=read('prompt-contract.json')
    old= json.loads((ROOT.parent/'M4_PROMPT_COMPONENTS.json').read_text())
    check(prompt['system']==old['system_prompt'] and prompt['rules']==old['rules'] and
          prompt['condition_sentences']==old['condition_sentences'],'prompt_components')
    sub=prompt['only_domain_substitution']
    check(prompt['base_suffix']==prompt['arm_suffix'].replace(sub['from'],sub['to']),'suffix_substitution')
    check(prompt['Qwen']['num_ctx']==8192 and prompt['Qwen']['num_predict']==1024 and
          prompt['Qwen']['think'] is False and prompt['Qwen']['KV']=='f16','serving_profile')
    observers=read('observer-separation-results.json')
    semantics=read('world-semantics-results.json')
    api=read('public-api-registration-results.json')
    check(observers['pass'] and observers['tests']==4 and observers['domain_checks']==8,'observer_proof')
    check(semantics['pass'] and semantics['test_methods']==5,'world_units')
    check(observers['world_source_sha256']==digest(ROOT/'worlds.py') and
          semantics['world_source_sha256']==digest(ROOT/'worlds.py'),'tested_world_digest')
    check(api['pass'] and len(api['constructors'])==4 and not api['Stage1_controls_run'],'API_constructor_checks')
    check(all(row['tool_invocations']==0 and row['native_operations']==0 for row in api['constructors']),
          'unexpected_tool_invocation')
    presence=read('authorization-presence.json')
    check(presence['provider_validity_checked'] is False and presence['credential_contents_read'] is False and
          presence['login_started'] is False,'unsafe_presence_record')
    protected=read('preserved-files-before.json')
    changed=[name for name,value in protected.items() if digest(WORKSPACE/name)!=value]
    check(not changed,'protected_file_changed')
    old_status=json.loads((ROOT.parent/'STAGE0_CHECKPOINT.json').read_text())['status']
    check(old_status=='STOPPED_INTERFACE_INCOMPATIBLE','old_status_rewritten')
    checkpoint=read('revision-checkpoint.json')
    check(checkpoint['pre_run_note_sha256']==digest(ROOT/'PRE_RUN_NOTE.md'),'pre_run_note_hash')
    check(checkpoint['model_requests']==0 and checkpoint['Stage1_started'] is False,'stage_advanced')
    missing=[]
    for doc in ROOT.glob('*.md'):
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
            target=target.split('#',1)[0]
            if target and '://' not in target and not (doc.parent/target).exists():missing.append([doc.name,target])
    check(not missing,'missing_link')
    validation={'mechanical_checks_pass':not issues,'issues':issues,'case_counts':dict(Counter(c['split'] for c in cases)),
        'template_groups':{key:len(value) for key,value in groups.items()},'observer_checks':8,'world_unit_methods':5,
        'API_constructor_checks':4,'protected_files_verified':len(protected),'protected_mismatches':changed,
        'old_STOPPED_status_unchanged':True,'missing_links':missing,'model_requests':0,
        'Stage1_controls_run':False,'persisted_Phoenix_audit':'not run','actual_model_turn_counts':'not recorded',
        'independent_teammate_cases':0,'original_authorship_gate_met':False,'advance_gate_passed':False,
        'pre_run_note_sha256':digest(ROOT/'PRE_RUN_NOTE.md'),
        'pre_run_clarification_sha256':digest(ROOT/'PRE_RUN_CLARIFICATION_01.md')}
    write('revision-validation.json',validation)
    assert not issues,issues
    excluded={'revision-manifest.json','revision-manifest-verification.json'}
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(ROOT.rglob('*'))
           if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts}
    write('revision-manifest.json',{'date':'2026-11-13','kind':'Stage0 revision proposal checkpoint; not the final post-dev experiment freeze',
        'files':files,'pre_run_note_sha256':digest(ROOT/'PRE_RUN_NOTE.md'),
        'pre_run_clarification_sha256':digest(ROOT/'PRE_RUN_CLARIFICATION_01.md')})
    mismatches=[name for name,value in files.items() if digest(ROOT/name)!=value]
    write('revision-manifest-verification.json',{'pass':not mismatches,'files_verified':len(files),'mismatches':mismatches,
          'manifest_sha256':digest(ROOT/'revision-manifest.json')})
    assert not mismatches,mismatches
    print(json.dumps({'mechanical_checks_pass':not issues,'protected_files_unchanged':len(protected),
        'manifest_files_verified':len(files),'template_groups':{key:len(value) for key,value in groups.items()},
        'model_requests':0,'advance_gate_passed':False}))


if __name__=='__main__':main()
