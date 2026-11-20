"""Stage 0 constructor/schema check, not Stage 1 scripted tool paths."""
import json
from pathlib import Path
import platform

from catalogue import registry
from worlds import create_world
from rosa_reliability.bounded_macro import MacroLimits
from rosa_reliability.prompt_contract import bounded_contract

ROOT=Path(__file__).resolve().parent


def main():
    reference=json.loads((ROOT/'prompt-contract.json').read_text())
    records=[]
    for domain in ('arm','base'):
        reg=registry(domain)
        assert len(reg.catalogue())==5
        for mode in ('primitives','macro'):
            world,actor,observer=create_world(domain)
            inv=reg.open({'state':actor,'inspection':actor},mode=mode,limits=MacroLimits(seconds=360.0))
            snap=inv.snapshot()
            assert not snap['operations'] and not actor.records and not observer.records and not world.records()
            assert bounded_contract([tool.name for tool in inv.tools])==reference['system']
            records.append({'domain':domain,'mode':mode,'skills':len(inv.catalogue),
                            'catalogue':inv.catalogue,
                            'tools':[tool.name for tool in inv.tools],'tool_invocations':0,'native_operations':0,'pass':True})
    out={'pass':True,'scope':'Public registration/open/schema only; tool paths and model-turn counts untested',
         'python':platform.python_version(),'constructors':records,'model_requests':0,'Stage1_controls_run':False}
    (ROOT/'public-api-registration-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'constructor_checks':len(records),'model_requests':0,'tool_invocations':0}))


if __name__=='__main__':main()
