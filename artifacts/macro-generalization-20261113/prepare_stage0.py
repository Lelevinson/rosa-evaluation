"""G1 Stage 0 planning only: no inference, credentials, simulator or module edits."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
REPO = WORKSPACE / 'rosa-evaluation'
SOURCE = WORKSPACE / 'rosa-research/src/rosa_reliability'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(name, content):
    (ROOT / name).write_text(content.strip() + '\n', encoding='utf-8')


def protect():
    paths = set()
    for folder in ('macro-m4-20261027', 'qwen-timing-probe-20261112', 'qwen-serving-phase1-20261112'):
        paths.update(p for p in (REPO / 'artifacts' / folder).rglob('*') if p.is_file())
    for folder in (WORKSPACE / 'rosa-research/src', REPO / 'docs', REPO / 'artifacts/macro-m5-20261027'):
        paths.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update(p for p in REPO.glob('*.md') if p.is_file())
    paths.update(WORKSPACE / name for name in load(REPO / 'artifacts/macro-m4-20261027/freeze.json')['files'])
    return {p.relative_to(WORKSPACE).as_posix(): digest(p) for p in sorted(paths)}


def locate(filename, class_name, method):
    tree = ast.parse((SOURCE / filename).read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    node = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method)
    return {'file': f'rosa-research/src/rosa_reliability/{filename}', 'class': class_name,
            'method': method, 'line': node.lineno, 'end_line': node.end_lineno,
            'source_sha256': digest(SOURCE / filename)}


def domains_and_skills():
    domains = {
        'arm': {'kind': 'stateful fixed-base arm mock',
                'reuse_candidate': 'experiments.reliability_v2.cases.MockTransport',
                'reuse_status': 'Candidate identified; separate observer NOT present or confirmed; no world instantiated.',
                'pose_units': {'yaw': 'radian', 'pitch': 'radian'},
                'checks': [('guard', 'guard_closed'), ('joint_sample', 'joint_sample_fresh'),
                           ('brake', 'brake_released'), ('thermal', 'temperature_safe'),
                           ('workspace', 'workspace_clear'), ('tool_mount', 'tool_mount_locked')],
                'faults': ['joint_read_timeout', 'guard_open', 'pitch_only_actuation'],
                'ids': ['arm.cedar', 'arm.quartz', 'arm.ember', 'arm.lumen', 'arm.cobalt', 'arm.umber'],
                'targets': [{'yaw': -.18, 'pitch': .11}, {'yaw': .24, 'pitch': -.16}]},
        'base': {'kind': 'new planar mobile-base mock, NOT implemented',
                 'reuse_candidate': None, 'reuse_status': 'New domain transport and observer not implemented.',
                 'pose_units': {'x_m': 'metre', 'y_m': 'metre', 'yaw_rad': 'radian'},
                 'checks': [('localization', 'pose_fix_valid'), ('energy', 'reserve_sufficient'),
                            ('lidar', 'corridor_clear'), ('map_lease', 'map_lease_valid'),
                            ('traction', 'wheel_slip_safe'), ('fix_clock', 'fix_age_acceptable')],
                 'quantities': {'battery_fraction': 'fraction [0,1]', 'clearance_m': 'metre',
                                'map_revision': 'integer generation', 'slip_ratio': 'ratio', 'fix_age_s': 'second'},
                 'faults': ['map_revision_changed', 'pose_fix_expired', 'goto_translation_without_heading', 'lidar_timeout'],
                 'ids': ['base.zephyr', 'base.jasper', 'base.mica', 'base.onyx', 'base.sable', 'base.nova'],
                 'targets': [{'x_m': .9, 'y_m': -.4, 'yaw_rad': .15}, {'x_m': -1.2, 'y_m': .8, 'yaw_rad': -.25}]}}
    skills = []
    for domain, spec in domains.items():
        for i, depth in enumerate((1, 2, 4, 6)):
            checks = dict(spec['checks'][:depth])
            skill = dict(domain=domain, skill_id=spec['ids'][i], kind='inspection', native_depth=depth,
                         sources=[f'/{domain}/{source}' for source in checks],
                         checks=checks, reads='independent', nominal_primitive_min_calls=3,
                         nominal_primitive_max_calls=depth + 2, actual_API_min_calls=3, actual_API_max_nominal_calls=3,
                         proposed_call_budget=depth + 6, proposed_native_budget=depth + 4,
                         API_status='Native ladder representable by source groups; per-source primitive calls NOT exposed.',
                         public_catalogue={'kind': 'read_only_inspection', 'subject': f'/{domain}/checks',
                             'required_checks': {k: [v] for k, v in checks.items()}, 'max_writes': 0,
                             'success_means': 'every required readiness check freshly observed true',
                             'evidence_encoding': 'true=1.0, false=0.0, unavailable=null'})
            skills.append(skill)
        for i, p in enumerate((1, 3)):
            target_node = '/arm/joints' if domain == 'arm' else '/base/pose'
            sources = ([target_node] if p == 1 else
                       ([target_node, '/arm/guard', '/arm/workspace'] if domain == 'arm' else
                        [target_node, '/base/localization', '/base/map_lease']))
            skills.append(dict(domain=domain, skill_id=spec['ids'][4 + i], kind='movement',
                               native_depth=p + 2, prerequisite_reads=p, sources=sources,
                               reads='Prerequisite reads independent; conditional write depends on all; verification depends on write.',
                               nominal_primitive_min_calls=5, nominal_primitive_max_calls=p + 4,
                               actual_API_min_calls=5 if p == 1 else None,
                               actual_API_max_nominal_calls=5 if p == 1 else None,
                               proposed_call_budget=p + 8, proposed_native_budget=p + 6,
                               API_status='Representable for one pose prerequisite.' if p == 1 else
                                   'BLOCKED: StateSkill has no multi-source prerequisite contract or acquisition policy.',
                               public_catalogue={'kind': 'state_change', 'targets': {target_node: spec['targets'][i]}, 'max_writes': 1},
                               prerequisite_contract_NOT_in_public_catalogue={
                                   'required_sources': sources, 'must_precede_write': True,
                                   'unavailable': 'UNKNOWN/no dispatch', 'known_unsafe': 'FAILURE/no dispatch'}))
    return domains, skills


def build_cases(domains, skills):
    cases = []
    def add(split, group, domain, family, skill, request, *, fault=None, expected='SUCCESS', writes=0):
        s = next((s for s in skills if s['skill_id'] == skill), None)
        calls = s['proposed_call_budget'] if s else 5
        native = s['proposed_native_budget'] if s else 4
        initial = ({'/arm/joints': {'yaw': 0.0, 'pitch': 0.0}, '/arm/guard': {'guard_closed': True},
                    '/arm/joint_sample': {'joint_sample_fresh': True, 'sample_age_s': .04},
                    '/arm/brake': {'brake_released': True}, '/arm/thermal': {'temperature_safe': True, 'temperature_c': 34.0},
                    '/arm/workspace': {'workspace_clear': True}, '/arm/tool_mount': {'tool_mount_locked': True}}
                   if domain == 'arm' else
                   {'/base/pose': {'x_m': 0.0, 'y_m': 0.0, 'yaw_rad': 0.0},
                    '/base/localization': {'pose_fix_valid': True},
                    '/base/energy': {'reserve_sufficient': True, 'battery_fraction': .76},
                    '/base/lidar': {'corridor_clear': True, 'clearance_m': 1.8},
                    '/base/map_lease': {'map_lease_valid': True, 'map_revision': 7},
                    '/base/traction': {'wheel_slip_safe': True, 'slip_ratio': .01},
                    '/base/fix_clock': {'fix_age_acceptable': True, 'fix_age_s': .08}})
        injection = {'type': fault, 'actor_only_unavailability': bool(fault and 'unavailable' in fault),
                     'observer_remains_available': True, 'implementation': 'not implemented'}
        if fault == 'required_safety_condition_false':
            node, field = ('/arm/guard','guard_closed') if domain == 'arm' else ('/base/localization','pose_fix_valid')
            initial[node][field] = False
            injection.update(source=node, field=field, value=False, activation='before selection')
        elif fault == 'required_source_unavailable_before_write':
            injection.update(source='/arm/workspace' if domain == 'arm' else '/base/map_lease', activation='before dispatch')
        elif fault == 'outcome_source_unavailable_after_write':
            injection.update(source='/arm/joints' if domain == 'arm' else '/base/pose', activation='after dispatched write')
        elif fault:
            injection['activation'] = 'on the single dispatched write'
        observer_goal = (None if family == 'ambiguous' else
                         False if fault in ('required_safety_condition_false','required_source_unavailable_before_write',
                                            'accepted_command_without_effect','pitch_only_actuation','goto_translation_without_heading')
                         else True)
        cases.append(dict(case_id=f'G1-{split}-{len(cases)+1:03d}', split=split, template_group=group,
                          author='Codex (AI)', independent_teammate_authorship=False,
                          domain=domain, family=family, skill_id=skill, request=request,
                          native_depth=s['native_depth'] if s else None,
                          depth_analysis=family in ('ladder', 'write_anchor'),
                          initial_state_recipe='All required sources available/safe; movement goal initially unmet.'
                              if fault is None else 'Private case recipe: ' + fault,
                          initial_values=initial, fault_injection=injection, expected_observer_goal=observer_goal,
                          fault=fault, expected_status=expected, expected_dispatches=writes,
                          calls_per_task=calls, native_operations=native, tool_attempts=2*calls,
                          corrections=3, seconds=360, max_dispatches=1,
                          state='DRAFT_NOT_RUN', semantic_template_novelty='not independently reviewed'))
    held_inspection = [
        'Return a readiness verdict using only {checks} on the {unit}; leave it stationary.',
        'Is the {unit} cleared on {checks}? Use exactly those sources and issue no motion.',
        'For this {unit} audit, obtain {checks} and no other sources. Give the observed verdict without moving.',
        'I need a stationary {unit} assessment covering {checks}, with all other sources out of scope.',
        'Report whether {checks} are satisfied for the {unit}. Limit acquisition to that list; motion is forbidden.']
    dev_inspection = [
        'Assess the {unit} with the following acquisition allowlist: {checks}. Observation only.',
        'For the {unit}, the allowed observations are {checks}. Decide readiness without commanding it.']
    held_move = [
        'The {unit} is assigned the following destination: {goal}. Complete the permitted relocation once and give a measured verdict.',
        'Settle the {unit} at {goal}; the required checks are {prereqs}. Confirm the actual final coordinates.',
        'Deliver the {unit} to {goal}, conditional on {prereqs}. Use a fresh observation to judge the resulting position.']
    dev_move = [
        'Authorized {unit} destination: {goal}. Obtain {prereqs}, command only if safe, and verify the result.',
        'For the {unit}, use {goal} as the fixed goal. Read {prereqs} before changing state, then measure the outcome.']
    for split in ('dev', 'heldout'):
        for domain in ('arm', 'base'):
            unit = 'inspection arm' if domain == 'arm' else 'delivery base'
            own = [s for s in skills if s['domain'] == domain]
            for s in own[:4]:
                for i, template in enumerate(dev_inspection if split == 'dev' else held_inspection):
                    group = f'{split}.inspection.' + ('allowlist' if split == 'dev' else str(i+1))
                    add(split, group, domain, 'ladder', s['skill_id'],
                        template.format(unit=unit, checks=', '.join(s['checks'].values())))
            for s in own[4:]:
                goal = ', '.join(f'{k}={v} {domains[domain]["pose_units"][k]}'
                                 for k, v in next(iter(s['public_catalogue']['targets'].values())).items())
                for i, template in enumerate(dev_move if split == 'dev' else held_move):
                    group = f'{split}.movement.' + ('authorized_destination' if split == 'dev' else str(i+1))
                    add(split, group, domain, 'write_anchor', s['skill_id'],
                        template.format(unit=unit, goal=goal, prereqs=', '.join(s['sources'])), writes=1)
            anchor = own[5]
            goal = ', '.join(f'{k}={v} {domains[domain]["pose_units"][k]}'
                             for k, v in next(iter(anchor['public_catalogue']['targets'].values())).items())
            if split == 'dev':
                extras = [
                    ('missing_prerequisite', 'required_safety_condition_false', 'FAILURE', 0,
                     f'Use {goal} as the {unit} destination, but a failed required safety check must prevent dispatch.'),
                    ('ambiguous', None, None, 0, f'The {unit} is next on the schedule. Handle its preparation.'),
                    ('fault', 'accepted_command_without_effect', 'FAILURE', 1,
                     f'For a one-command delivery of the {unit}, the goal is {goal}. Judge the measured result rather than the receipt.'),
                    ('fault', 'outcome_source_unavailable_after_write', 'UNKNOWN', 1,
                     f'A single relocation of the {unit} to {goal} is permitted. State uncertainty if its outcome cannot be observed.')]
            else:
                extras = [
                    ('missing_prerequisite', 'required_safety_condition_false', 'FAILURE', 0,
                     f'The {unit} may go to {goal} only with all mandatory safety conditions satisfied. Otherwise leave it stationary.'),
                    ('missing_prerequisite', 'required_source_unavailable_before_write', 'UNKNOWN', 0,
                     f'The destination for the {unit} is {goal}. Withhold the command if any required source cannot be obtained.'),
                    ('ambiguous', None, None, 0, f'Take care of the {unit} for the upcoming shift.'),
                    ('ambiguous', None, None, 0, f'The team will need the {unit} soon; arrange what it needs.'),
                    ('fault', 'pitch_only_actuation' if domain == 'arm' else 'goto_translation_without_heading', 'FAILURE', 1,
                     f'The complete {unit} goal is {goal}. A one-shot command is allowed; assess every final coordinate and do not resend.'),
                    ('fault', 'outcome_source_unavailable_after_write', 'UNKNOWN', 1,
                     f'Authorize one transfer of the {unit} to {goal}. If the final '
                     f'{"joint sample" if domain == "arm" else "localization"} is unavailable, report that limitation without another command.')]
            counters = {}
            for family, fault, expected, writes, request in extras:
                counters[family] = counters.get(family, 0) + 1
                group = f'{split}.{family}.{counters[family]}'
                add(split, group, domain, family, None if family == 'ambiguous' else anchor['skill_id'],
                    request, fault=fault, expected=expected, writes=writes)
    return cases


def make_budgets(cases):
    result = {}
    for split, reserve in [('dev', 6), ('heldout', 12)]:
        subset = [c for c in cases if c['split'] == split]
        normal = 2 * sum(c['calls_per_task'] for c in subset)
        result[split] = {'cases': len(subset), 'paired_trials': 2 * len(subset),
                         'logical_request_cap': normal, 'separate_infrastructure_reserve': reserve,
                         'physical_request_ceiling': normal + reserve,
                         'output_gate_per_task': 2048, 'local_per_call': 1024,
                         'max_trial_seconds': 360, 'aggregate_trial_deadline_envelope_seconds': 720 * len(subset),
                         'authorization': 'NOT APPROVED; design currently blocked'}
    result['stages'] = {'Sol_dev': result['dev'], 'Sol_heldout': result['heldout'], 'Qwen_heldout': result['heldout'],
                        'selection_probe_per_model_one_condition': {'logical_requests': 64*3, 'reserve': 3, 'ceiling': 195},
                        'selection_probe_per_model_both_condition_sentences': {'logical_requests': 64*3*2, 'reserve': 6, 'ceiling': 390}}
    result['provider_remaining_quota'] = 'not recorded'
    result['M4_request_cap_not_provider_quota'] = {'ceiling': 323, 'used': 106, 'unused_local_slots': 217}
    return result


def main():
    assert not (ROOT / 'STAGE0_CHECKPOINT.json').exists(), 'Do not overwrite a sealed preparation; use a dated amendment.'
    before = protect()
    save('protected-files-before.json', before)
    domains, skills = domains_and_skills()
    cases = build_cases(domains, skills)
    assert sum(c['split'] == 'dev' for c in cases) == 32
    assert sum(c['split'] == 'heldout' for c in cases) == 64
    assert not ({c['template_group'] for c in cases if c['split'] == 'dev'} &
                {c['template_group'] for c in cases if c['split'] == 'heldout'})
    request = WORKSPACE / 'rosa-evaluation/artifacts/qwen-serving-phase1-20261112/A/01/request.json'
    prompt = load(request)['messages'][0]['content']
    rule_tree = ast.parse((REPO / 'experiments/macro_capabilities_v2/m3.py').read_text())
    rules = ast.literal_eval(next(n.value for n in rule_tree.body if isinstance(n, ast.Assign)
                                 and any(isinstance(t, ast.Name) and t.id == 'RULES' for t in n.targets)))
    save('M4_PROMPT_COMPONENTS.json', {'system_prompt': prompt, 'rules': rules,
        'condition_sentences': {
            'macro': 'select_skill runs the bounded routine and returns evidence; do not repeat completed steps. ',
            'primitives': 'select_skill selects only; you manage the needed reads, conditional write and fresh check. '},
        'budget_suffix_conflict': 'M4 hard-codes eight calls, ten operations, sixteen attempts and joint tolerance; G1 proposes variable limits and a mobile domain. No substitution approved.'})
    save('domains.json', domains)
    save('skills-and-depths.json', skills)
    save('cases.json', cases)
    cols = ['case_id','split','template_group','author','independent_teammate_authorship','domain','family','skill_id',
            'native_depth','depth_analysis','request','fault','expected_status','expected_dispatches',
            'calls_per_task','native_operations','tool_attempts','seconds','state']
    with (ROOT / 'cases.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); writer.writeheader(); writer.writerows(cases)
    budgets = make_budgets(cases); save('budgets.json', budgets)
    compatibility = {'state': 'STOPPED_INTERFACE_INCOMPATIBLE', 'method': 'Static public-API/source inspection only; no controls executed.',
        'findings': [
            {'id': 'G1-API-1', 'finding': 'StateSkill accepts exactly one target node and no prerequisite definitions.',
             'evidence': locate('bounded_macro.py','StateSkill','validate_contract')},
            {'id': 'G1-API-2', 'finding': 'Macro state path is fixed read(target) / conditional write(target) / verify(target); p=3 cannot be declared.',
             'evidence': locate('macro.py','MacroSession','run_workflow')},
            {'id': 'G1-API-3', 'finding': 'Inspection read requires exactly the selected subject and loops over ALL source groups; primitive partial-source reads are not exposed.',
             'evidence': locate('capabilities.py','_CapabilitySession','read')},
            {'id': 'G1-API-4', 'finding': 'Capability catalogue does not include a state-skill prerequisite contract.',
             'evidence': locate('capabilities.py','CapabilityRegistry','catalogue')},
            {'id': 'G1-API-5', 'finding': 'Registration/open supports numeric single-node pose targets in a new transport, so second-domain registration alone is not disproved.',
             'evidence': locate('capabilities.py','CapabilityRegistry','open')}],
        'P5_observation': 'Against hosting the exact requested G1 contract unchanged; not evidence that every mobile-base use is incompatible.',
        'source_changes': [], 'new_domain_runtime_implemented': False, 'controls_run': False, 'model_requests': 0}
    save('source-compatibility.json', compatibility)
    grouped = {}
    for split in ('dev','heldout'):
        subset = [c for c in cases if c['split'] == split]
        grouped[split] = {'cases': len(subset), 'template_groups': len({c['template_group'] for c in subset}),
                          'authors': {'Codex (AI)': len(subset)}, 'independent_teammate_cases': 0,
                          'families': {family: sum(c['family'] == family for c in subset)
                                       for family in ('ladder','write_anchor','missing_prerequisite','ambiguous','fault')}}
    # Compare requests without importing or executing historical experiment modules.
    m4_tree = ast.parse((REPO / 'experiments/macro_m4/design.py').read_text())
    old_literals = {n.value for n in ast.walk(m4_tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    duplicates = [c['case_id'] for c in cases if c['request'] in old_literals]
    save('case-design-validation.json', {'counts': grouped, 'split_group_overlap': [],
        'exact_M4_literal_request_matches': duplicates, 'semantic_template_novelty': 'not independently reviewed',
        'authoring_protection': 'All cases are AI-authored; the original independent-teammate authorship criterion is not met.',
        'runtime_solvability': 'not tested', 'prompt_token_lengths': 'not recorded',
        'inference_requests': 0})
    table = ['# G1 skill and nominal depth proposal', '',
        '**Draft; not an executable catalogue or a confirmed design.** Native counts meter physical source acquisitions, not model calls.', '',
        '| Domain / ID | Kind | Native depth | Intended primitive min-max calls | Actual public-API nominal min-max | Proposed calls / native / attempts | Read dependence |',
        '|---|---|---:|---|---|---|---|']
    for s in skills:
        actual = 'unsupported' if s['actual_API_min_calls'] is None else f'{s["actual_API_min_calls"]}-{s["actual_API_max_nominal_calls"]}'
        table.append(f'| {s["domain"]} / {s["skill_id"]} | {s["kind"]} | {s["native_depth"]} | '
                     f'{s["nominal_primitive_min_calls"]}-{s["nominal_primitive_max_calls"]} | {actual} | '
                     f'{s["proposed_call_budget"]} / {s["proposed_native_budget"]} / {2*s["proposed_call_budget"]} | {s["reads"]} |')
    table += ['', 'The intended ranges assume exactly one tool per model response, one selection and one terminal report. '
              'Inspection min=3, max=d+2; healthy movement min=5, max=p+4 (start off target). '
              'Macro nominal model calls=2: select/bundle, then report. Errors and recovery are outside nominal minima/maxima but inside budgets.', '',
              'Current inspections always acquire every selected source group in one read/verify call in either condition. '
              'Thus actual nominal primitive calls=3 for every inspection depth: native depth increases but model decision depth does not. '
              'Replacing those source groups with hidden transport reads would not create the proposed experiment.', '',
              'For each domain the first four IDs cover source prefixes of length1,2,4,6; the names contain no depth labels. '
              'The last two IDs are fixed numeric targets with proposed p=1 and p=3. '
              'The public M4 state catalogue can represent the targets, but cannot represent the p=3 guard/acquisition contract. '
              'No extra catalogue descriptions or prerequisite keys were silently injected into the public schema. '
              'See skills-and-depths.json for public-schema proposals and separately labelled unsupported prerequisites.']
    text('SKILL_DEPTH_TABLE.md','\n'.join(table))
    changed = [name for name, value in before.items() if digest(WORKSPACE / name) != value]
    save('preservation-check.json', {'protected_files': len(before), 'mismatches': changed, 'pass': not changed})
    assert not changed
    save('STAGE0_CHECKPOINT.json', {'date': '2026-11-13', 'study': 'exploratory generalization study G1',
        'status': 'STOPPED_INTERFACE_INCOMPATIBLE', 'stage0_design': 'DRAFT; user confirmation not obtained',
        'stage1_started': False, 'model_requests': 0, 'credential_access': False,
        'sources_modified': False, 'committed': False, 'pushed_or_uploaded': False,
        'case_counts': grouped, 'request_ceiling_proposals': budgets['stages'],
        'pre_run_note_sha256': digest(ROOT / 'PRE_RUN_NOTE.md')})
    print(json.dumps({'status': 'STOPPED_INTERFACE_INCOMPATIBLE', 'draft_cases': len(cases),
                      'dev_ceiling': budgets['dev']['physical_request_ceiling'],
                      'heldout_ceiling_per_backend': budgets['heldout']['physical_request_ceiling'],
                      'protected_files': len(before), 'changed': len(changed), 'model_requests': 0}))


if __name__ == '__main__':
    main()
