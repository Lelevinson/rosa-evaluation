"""Validate/seal the Stage 0 proposal. No models, credentials or runtime controls."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    cases = read(ROOT / 'cases.json')
    skills = read(ROOT / 'skills-and-depths.json')
    budgets = read(ROOT / 'budgets.json')
    checkpoint = read(ROOT / 'STAGE0_CHECKPOINT.json')
    issues = []
    def check(condition, issue):
        if not condition: issues.append(issue)
    check(len(cases) == 96 and len({c['case_id'] for c in cases}) == 96, 'case_count_or_ids')
    check(len(skills) == 12 and len({s['skill_id'] for s in skills}) == 12, 'skill_count_or_ids')
    check(all(not re.search(r'\d', s['skill_id']) for s in skills), 'depth_encoded_in_id')
    check(all(c['author'] == 'Codex (AI)' and not c['independent_teammate_authorship'] for c in cases), 'authorship')
    check(not ({c['template_group'] for c in cases if c['split'] == 'dev'} &
               {c['template_group'] for c in cases if c['split'] == 'heldout'}), 'template_split_leak')
    held = [c for c in cases if c['split'] == 'heldout']
    for domain in ('arm','base'):
        for depth in (1,2,4,6):
            check(sum(c['domain'] == domain and c['family'] == 'ladder' and c['native_depth'] == depth for c in held) == 5,
                  f'held_ladder_cell:{domain}/{depth}')
        for skill in (s for s in skills if s['domain'] == domain and s['kind'] == 'movement'):
            check(sum(c['family'] == 'write_anchor' and c['skill_id'] == skill['skill_id'] for c in held) == 3,
                  f'held_anchor_cell:{skill["skill_id"]}')
        for family in ('missing_prerequisite','ambiguous','fault'):
            check(sum(c['domain'] == domain and c['family'] == family for c in held) == 2, f'held_extra:{domain}/{family}')
    for split, count in [('dev',32), ('heldout',64)]:
        subset = [c for c in cases if c['split'] == split]
        check(len(subset) == count, 'split_count:'+split)
        computed = 2*sum(c['calls_per_task'] for c in subset)
        check(computed == budgets[split]['logical_request_cap'], 'logical_ceiling:'+split)
        check(computed + budgets[split]['separate_infrastructure_reserve'] == budgets[split]['physical_request_ceiling'],
              'physical_ceiling:'+split)
    for case in cases:
        check(case['tool_attempts'] == 2*case['calls_per_task'], 'tool_budget:'+case['case_id'])
        check(case['state'] == 'DRAFT_NOT_RUN', 'not_draft:'+case['case_id'])
        if case['family'] == 'ambiguous':
            check(not case['depth_analysis'] and case['skill_id'] is None, 'ambiguity_depth:'+case['case_id'])
    protected = read(ROOT / 'protected-files-before.json')
    changed = [name for name, value in protected.items() if digest(WORKSPACE / name) != value]
    check(not changed, 'protected_file_changed')
    check(checkpoint['status'] == 'STOPPED_INTERFACE_INCOMPATIBLE' and checkpoint['model_requests'] == 0,
          'inaccurate_checkpoint')
    check(checkpoint['pre_run_note_sha256'] == digest(ROOT / 'PRE_RUN_NOTE.md'), 'pre_run_note_hash')
    missing = []
    for doc in ROOT.glob('*.md'):
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            name = target.split('#',1)[0]
            if name and '://' not in name and not (doc.parent / name).exists(): missing.append([doc.name,name])
    check(not missing, 'missing_report_link')
    validation = {'scope': 'Stage 0 structural/design checks only; no Stage 1 controls or model trials',
                  'pass': not issues, 'issues': issues, 'case_count': len(cases), 'skill_count': len(skills),
                  'protected_files_verified': len(protected), 'changed_protected_files': changed,
                  'missing_links': missing, 'model_requests': 0, 'independent_teammate_authorship_met': False,
                  'API_gate_passed': False, 'runtime_solvability_validated': False,
                  'pre_run_note_sha256': digest(ROOT / 'PRE_RUN_NOTE.md')}
    write('stage0-validation.json', validation)
    assert not issues, issues
    excluded = {'stage0-manifest.json','stage0-manifest-verification.json'}
    files = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(ROOT.rglob('*'))
             if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts}
    write('stage0-manifest.json', {'date': '2026-11-13', 'kind': 'proposal checkpoint, not final experimental freeze',
                                 'files': files, 'pre_run_note_sha256': digest(ROOT / 'PRE_RUN_NOTE.md')})
    mismatches = [name for name, value in files.items() if digest(ROOT / name) != value]
    write('stage0-manifest-verification.json', {'pass': not mismatches, 'files_verified': len(files),
          'mismatches': mismatches, 'manifest_sha256': digest(ROOT / 'stage0-manifest.json')})
    assert not mismatches, mismatches
    print(json.dumps({'structural_checks_pass': not issues, 'API_gate_passed': False,
                      'draft_cases': len(cases), 'protected_files_unchanged': len(protected),
                      'pre_run_note_sha256': digest(ROOT / 'PRE_RUN_NOTE.md'), 'model_requests': 0,
                      'manifest_files': len(files)}))


if __name__ == '__main__':
    main()
