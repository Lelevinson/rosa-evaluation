from copy import deepcopy
import random
from experiments.ur5e_transfer_v1.arm import arm_cases
from experiments.reliability_v2.cases import INSTRUCTIONS

CONDITIONS = {
    'L256': {'per_call': 256, 'concise': False, 'recover': False},
    'L512': {'per_call': 512, 'concise': False, 'recover': False},
    'L1024': {'per_call': 1024, 'concise': False, 'recover': False},
    'C256': {'per_call': 256, 'concise': True, 'recover': False},
    'R256': {'per_call': 256, 'concise': False, 'recover': True},
}
CONCISE = (
    '\nResponse style for this task: prioritize the next permitted tool call. '
    'Do not narrate plans or restate target/current joint dictionaries in prose. '
    'Put required numeric values in tool arguments. After the accepted report, '
    'finish with a brief acknowledgement. All existing evidence and safety rules apply.'
)


def instructions(condition):
    return INSTRUCTIONS + (CONCISE if CONDITIONS[condition]['concise'] else '')


def jobs():
    rng = random.Random(20261022)
    cases = arm_cases()
    rng.shuffle(cases)
    labels = list(CONDITIONS)
    rng.shuffle(labels)
    result = []
    # Each case/repetition is a block with all five interventions. Reverse the
    # second repetition and rotate labels; do not tune order after seeing data.
    for repeat in range(2):
        for index, spec in enumerate(cases if repeat == 0 else list(reversed(cases))):
            offset = (index + 2*repeat) % len(labels)
            order = labels[offset:] + labels[:offset]
            if repeat:
                order = list(reversed(order))
            for label in order:
                result.append({'repeat': repeat, 'condition': label, 'spec': deepcopy(spec)})
    return result
