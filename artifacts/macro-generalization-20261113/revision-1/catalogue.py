"""Public API factory only; import occurs when explicitly called for a gate."""
from worlds import DOMAINS


def definitions(domain):
    from rosa_reliability.bounded_macro import StateSkill
    from rosa_reliability.capabilities import InspectionSkill
    spec = DOMAINS[domain]
    result = []
    for index, depth in enumerate((1,2,4,6)):
        result.append(InspectionSkill(skill_id=spec['ids'][index], subject=f'/g1_{domain}/checks',
                      checks={source:[field] for source,field in spec['checks'][:depth]}))
    result.append(StateSkill(skill_id=spec['ids'][4], targets={spec['node']: spec['target']}))
    return result


def registry(domain):
    from rosa_reliability.capabilities import CapabilityRegistry
    result = CapabilityRegistry()
    for skill in definitions(domain):
        result.register(skill)
    return result
