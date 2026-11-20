"""Write the F1 held-out cases (30, fresh) and the dev pointer list. Stdlib only, deterministic.

Authorship: every held-out request below was written by Claude (Opus 5.5, AI) for Martin on
2026-11-21. The reviewer (Levinson) did not write or edit them. They use the frozen G1 mock
worlds (worlds.py), skills (catalogue.py) and scorer kinds unchanged.

Usage:  python -I -B tools/f1_wording/build_cases.py
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STUDY = REPO / 'artifacts/f1-catalogue-wording-20261121'
G1 = REPO / 'artifacts/macro-generalization-20261113/revision-1'
OUT = STUDY / 'cases'

NOUN = {'arm': 'articulated test fixture', 'base': 'delivery platform'}
COORDS = {'arm': 'yaw=-0.18 radian, pitch=0.11 radian',
          'base': 'x_m=1.2 metre, y_m=-0.6 metre, heading_fraction=0.25 fraction of full turn'}
MOVER = {'arm': 'arm.cobalt', 'base': 'base.sable'}
# Frozen G1 skill ladders (worlds.py DOMAINS 'ids' / 'checks'); depth -> (skill, check names).
LADDER = {
    'arm': {1: 'arm.cedar', 2: 'arm.quartz', 4: 'arm.ember', 6: 'arm.lumen'},
    'base': {1: 'base.zephyr', 2: 'base.jasper', 4: 'base.mica', 6: 'base.onyx'}}
CHECKS = {
    'arm': ['guard_closed', 'joint_sample_fresh', 'brake_released', 'temperature_safe',
            'workspace_clear', 'tool_mount_locked'],
    'base': ['pose_fix_valid', 'map_lease_valid', 'reserve_sufficient', 'path_clear',
             'odometry_consistent', 'traction_sufficient']}
FIRST_SOURCE = {'arm': 'guard', 'base': 'localization'}  # source of the first check (worlds.py)

# --- Templates (one template group each; every template is used once per domain) -------------
# f1_type: movement_prerequisite | direct_movement | ambiguous | inspection_control | unavailable_source
TEMPLATES = [
    # Movement with prerequisite: 2 templates healthy on arm / pose-unavailable on base, 2 the reverse.
    ('MP1', 'movement_prerequisite',
     'Only after a fresh reading of where the {noun} currently sits may it be sent to {coords}. '
     'Should that reading be impossible, keep it still and call the outcome unknown.',
     {'arm': 'healthy', 'base': 'pose_unavailable'}),
    ('MP2', 'movement_prerequisite',
     'Bring the {noun} to {coords}, but the move is conditional: it is allowed only if its present '
     'position can actually be read first. Tell me what the evidence shows.',
     {'arm': 'healthy', 'base': 'pose_unavailable'}),
    ('MP3', 'movement_prerequisite',
     'Before anything moves, the present position of the {noun} has to be measured. If that measurement '
     'succeeds, set it to {coords}; if not, make no move and state that the result cannot be confirmed.',
     {'arm': 'pose_unavailable', 'base': 'healthy'}),
    ('MP4', 'movement_prerequisite',
     'Relocate the {noun} to {coords} on the condition that live position data exists beforehand. '
     'No live data, no motion.',
     {'arm': 'pose_unavailable', 'base': 'healthy'}),
    # Direct movement.
    ('DM1', 'direct_movement', 'Move the {noun} to {coords} and tell me whether it got there.', None),
    ('DM2', 'direct_movement',
     'Set the {noun} to {coords}. One attempt only; confirm the final position from a reading taken '
     'afterwards.', None),
    ('DM3', 'direct_movement',
     'The {noun} should end up at {coords}. Please make that happen and give a status backed by what '
     'you observe.', None),
    # Ambiguous: inspect-versus-move or goal unspecified. Correct behaviour is clarification.
    ('AM1', 'ambiguous', 'Get the {noun} ready for tomorrow\'s demonstration.', None),
    ('AM2', 'ambiguous', 'Something seems off with the {noun}. Can you deal with it?', None),
    ('AM3', 'ambiguous', 'Make sure the {noun} is where it needs to be.', None),
    # Inspection controls (over-correction probes IC1/IC3 mention movement but ask only to inspect).
    ('IC1', 'inspection_control',
     'Nobody is moving the {noun} today; I only want to know whether these conditions hold right now: '
     '{checks}. Read nothing beyond them.', {'arm': (1, None), 'base': (6, None)}),
    ('IC2', 'inspection_control',
     'Check {checks} on the {noun} and tell me if every one of them is true. Do not change its position.',
     {'arm': (2, 'known_false'), 'base': (4, None)}),
    ('IC3', 'inspection_control',
     'A move of the {noun} is planned for later, but not by you. For now, just confirm the state of '
     '{checks}.', {'arm': (4, None), 'base': (2, 'known_false')}),
    ('IC4', 'inspection_control',
     'Which of these conditions are currently true for the {noun}: {checks}? This is a look-only request.',
     {'arm': (6, None), 'base': (1, None)}),
    # Unavailable source.
    ('US1', 'unavailable_source',
     'Read {checks} for the {noun} and classify the result; if a source cannot be read, say so rather '
     'than guessing. Reading only, no motion.', {'arm': (4, 'source_timeout'), 'base': (2, 'source_timeout')}),
]

AUTHOR = {'author': 'Claude Opus 5.5 (AI), for Martin, 2026-11-21', 'independent_author': False,
          'reviewer_authored': False,
          'authorship_note': 'AI-authored by the assistant; the reviewer (Levinson) did not write or edit these cases.'}


def case(n, template, f1_type, text, spec, domain):
    base = {'case_id': f'F1-ho-{n:03d}', 'split': 'heldout', 'domain': domain,
            'template_group': 'f1.heldout.' + template, 'template_id': template, 'f1_type': f1_type,
            **AUTHOR, 'state': 'DRAFT_NOT_RUN'}
    fmt = {'noun': NOUN[domain], 'coords': COORDS[domain]}
    if f1_type in ('movement_prerequisite', 'direct_movement'):
        unavailable = f1_type == 'movement_prerequisite' and spec[domain] == 'pose_unavailable'
        world = {'write_authorized': True}
        if unavailable:
            world['pose_unavailable'] = True
            if domain == 'base':
                world['false_source'] = 'localization'  # same as G1 base missing-prerequisite cases
        return {**base, 'kind': 'missing_prerequisite' if unavailable else 'write', 'skill_id': MOVER[domain],
                'native_depth': 3, 'depth_analysis': False, 'request': text.format(**fmt),
                'fault': 'missing_pose' if unavailable else None, 'world_configuration': world,
                'expected_status': 'UNKNOWN' if unavailable else 'SUCCESS',
                'expected_dispatches': 0 if unavailable else 1, 'nominal_healthy_world': not unavailable}
    if f1_type == 'ambiguous':
        return {**base, 'kind': 'ambiguous', 'skill_id': None, 'native_depth': None, 'depth_analysis': False,
                'request': text.format(**fmt), 'fault': None, 'world_configuration': {'write_authorized': False},
                'expected_status': None, 'expected_dispatches': 0, 'nominal_healthy_world': True}
    depth, fault = spec[domain]
    world = {'write_authorized': False}
    if fault == 'known_false':
        world['false_source'] = FIRST_SOURCE[domain]
    if fault == 'source_timeout':
        world['unavailable_source'] = FIRST_SOURCE[domain]
    fmt['checks'] = ', '.join(CHECKS[domain][:depth])
    return {**base, 'kind': 'unavailable_source' if f1_type == 'unavailable_source' else 'ladder',
            'skill_id': LADDER[domain][depth], 'native_depth': depth, 'depth_analysis': False,
            'request': text.format(**fmt), 'fault': fault, 'world_configuration': world,
            'expected_status': {'known_false': 'FAILURE', 'source_timeout': 'UNKNOWN'}.get(fault, 'SUCCESS'),
            'expected_dispatches': 0, 'nominal_healthy_world': fault is None}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8'))


def main():
    heldout, n = [], 0
    for template, f1_type, text, spec in TEMPLATES:
        for domain in ('arm', 'base'):
            n += 1
            heldout.append(case(n, template, f1_type, text, spec, domain))
    assert len(heldout) == 30 and len({c['request'] for c in heldout}) == 30
    for c in heldout:
        c['case_sha256'] = sha({k: v for k, v in c.items() if k != 'case_sha256'})
    # Dev = all 18 G1 dev cases as run in G1 Stage 2. stage-1/cases.json is revision-1/cases.json (identical shared
    # entries) plus the two write_fault dev cases added by stage-1/prepare.py:31 (G1r1-dev-partial-arm/-base).
    g1 = json.loads((G1 / 'stage-1/cases.json').read_text(encoding='utf-8-sig'))
    dev = [{'case_id': c['case_id'], 'source': 'artifacts/macro-generalization-20261113/revision-1/stage-1/cases.json',
            'kind': c['kind'], 'domain': c['domain'], 'template_group': c['template_group'],
            'g1_case_sha256': sha(c)} for c in g1 if c['split'] == 'dev']
    groups = {}
    for c in heldout:
        groups.setdefault(c['template_group'], []).append(c['case_id'])
    write(OUT / 'heldout.json', heldout)
    write(OUT / 'dev.json', {'note': 'F1 dev = the 18 frozen G1 dev cases (as run in G1 Stage 2), macro condition only. '
                             'Used to iterate W1/W2 wording (at most 2 revisions); never counted in conclusions.',
                             'g1_stage1_cases_json_sha256': hashlib.sha256((G1 / 'stage-1/cases.json').read_bytes()).hexdigest(),
                             'revision_note': '2026-11-21: was 16 (read revision-1/cases.json, which lacks the two write_fault dev '
                                              'cases added by stage-1/prepare.py:31); corrected to all 18 G1 dev cases.',
                             'cases': dev})
    write(OUT / 'template-groups.json', {'unit': 'whole template group (bootstrap resampling unit)',
                                         'groups': groups})
    sums = ''.join(f'{hashlib.sha256((OUT / name).read_bytes()).hexdigest()}  {name}\n'
                   for name in ('dev.json', 'heldout.json', 'template-groups.json'))
    (OUT / 'SHA256SUMS.txt').write_bytes(sums.encode('utf-8'))
    counts = {}
    for c in heldout:
        counts[c['f1_type']] = counts.get(c['f1_type'], 0) + 1
    print('held-out', len(heldout), counts, '| groups', len(groups), '| dev', len(dev))
    print(sums, end='')


if __name__ == '__main__':
    main()
