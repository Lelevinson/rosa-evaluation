"""Create proposed pair order/catalogue views only. Never run a model or tool."""
from pathlib import Path
import json
import random

ROOT=Path(__file__).resolve().parent


def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def write(name,value):(ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def main():
    cases=read('cases.json')
    constructors=read('public-api-registration-results.json')['constructors']
    catalogues={domain:next(row['catalogue'] for row in constructors if row['domain']==domain and row['mode']=='macro')
                for domain in ('arm','base')}
    combined={key:value for domain in ('arm','base') for key,value in catalogues[domain].items()}
    assert len(combined)==10
    plan=[]
    for case in (c for c in cases if c['split']=='heldout'):
        names=sorted(catalogues[case['domain']])
        rng=random.Random('20261113:'+case['case_id'])
        if case['kind']=='ambiguous':
            small=sorted(rng.sample(names,3))
            policy='No unique target: fixed seeded sample from the domain, chosen before results.'
        else:
            target=case['skill_id']
            small=sorted([target]+rng.sample([name for name in names if name!=target],2))
            policy='Target plus two same-domain seeded distractors.'
        plan.append({'case_id':case['case_id'],'condition':'macro only','expected_skill':case['skill_id'],
                     'sampler_policy':policy,'catalogues':{'3':small,'5':names,'10':sorted(combined)},
                     'tools_execute':False,'response_cap':1})
    jobs={}
    for backend,split in [('siwc','dev'),('siwc','heldout'),('ollama','heldout')]:
        ordered=[]
        selected=[c for c in cases if c['split']==split]
        for index,case in enumerate(selected):
            first_macro=(index+1+(backend=='siwc'))%2==0
            for condition in (('macro','primitives') if first_macro else ('primitives','macro')):
                ordered.append({'case_id':case['case_id'],'condition':condition,'reset_world_and_agent_history':True})
        jobs[backend+'_'+split]=ordered
    write('catalogues.json',{'domains':catalogues,'combined':combined,'schema':'Actual public CapabilityRegistry.catalogue output; no added descriptions'})
    write('catalogue-probe-plan.json',{'state':'PROPOSAL_NOT_RUN','cases':len(plan),'responses_per_backend':3*len(plan),
        'macro_sentence_only':True,'five_underlying_tool_types_unchanged':True,
        'seed_policy':'Python Random with string seed 20261113:<case_id>; sorted catalogue keys',
        'plan':plan})
    write('paired-order-proposal.json',{'state':'PROPOSAL_NOT_RUN','method':'Adjacent pairs; alternate first condition by case; reverse for the other backend as in M4',
                                    'jobs':jobs})
    print(json.dumps({'heldout_cases':len(plan),'probe_requests_per_backend':3*len(plan),'model_requests':0}))


if __name__=='__main__':main()
