"""Map actual teammate submissions without changing their request wording."""
import argparse
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
from common import ROOT, REV, read, write, digest

OUTCOMES = {'inspect': 'ladder', 'move': 'write', 'missing_prerequisite': 'missing_prerequisite',
            'partial_write': 'write_fault', 'unavailable_source': 'unavailable_source', 'ambiguous': 'ambiguous'}
EXPOSURES = {'project_documents', 'dev_cases', 'dev_results', 'heldout_drafts', 'stage2_transcripts', 'none'}
ALLOWED_OVERRIDES = {'kind', 'fault', 'world_configuration', 'expected_status', 'expected_dispatches'}

def validate_request(request):
    required = {'case_ref', 'domain', 'intended_outcome', 'intended_skill_plain_words', 'request_text',
                'author_name', 'date_written', 'seen_before_writing', 'paraphrase_group'}
    assert set(request) == required, 'request_schema_fields'
    for key in ('case_ref', 'intended_skill_plain_words', 'request_text', 'author_name'):
        assert isinstance(request[key], str) and request[key].strip(), 'empty_'+key
    assert request['domain'] in ('arm', 'base') and request['intended_outcome'] in OUTCOMES
    date.fromisoformat(request['date_written'])
    seen = request['seen_before_writing']
    assert set(seen) == EXPOSURES and all(type(value) is bool for value in seen.values())
    assert seen['none'] == (not any(value for key, value in seen.items() if key != 'none'))
    assert request['paraphrase_group'] is None or isinstance(request['paraphrase_group'], str)
    return not any(value for key, value in seen.items() if key != 'none')

def build(requests, mappings):
    original = [case for case in read(REV/'stage-1/cases.json') if case['split'] == 'heldout']
    assert len(original) == 38
    cases = {case['case_id']: deepcopy(case) for case in original}
    skills = {skill['skill_id']: skill for skill in read(REV/'skills-and-depths.json')}
    mapping_by_ref = {mapping['case_ref']: mapping for mapping in mappings}
    assert len(mapping_by_ref) == len(mappings)
    assert len({r['case_ref'] for r in requests}) == len(requests)
    logs, replaced, blocked = [], [], []
    for request in requests:
        try:
            blind = validate_request(request)
            assert blind, 'author_exposure_not_independent'
            mapping = mapping_by_ref[request['case_ref']]
            baseline = cases[mapping['replaces_case_ref']]
            assert not any(item['case_id'] == baseline['case_id'] for item in replaced), 'duplicate_replacement'
            assert mapping['author_confirmed_group'] is True, 'template_group_not_confirmed_by_author'
            assert mapping['template_group'] and (request['paraphrase_group'] is None or
                                                 request['paraphrase_group'] == mapping['template_group'])
            assert set(mapping['fixture_overrides']) <= ALLOWED_OVERRIDES
            result = deepcopy(baseline)
            result.update(mapping['fixture_overrides'])
            result['skill_id'] = mapping['skill_id']
            assert baseline['domain'] == request['domain']
            assert result['kind'] == OUTCOMES[request['intended_outcome']] == baseline['kind'], 'replacement_kind_mismatch'
            if result['kind'] == 'ambiguous':
                assert mapping['skill_id'] is None and result['expected_dispatches'] == 0
            else:
                skill = skills[mapping['skill_id']]
                assert mapping['skill_id'].startswith(request['domain']+'.')
                result['native_depth'] = skill['native_depth']
                assert result['native_depth'] == baseline['native_depth'], 'replacement_depth_mismatch'
            assert result['expected_dispatches'] in (0, 1)
            result.update(request=request['request_text'], author=request['author_name'], independent_author=True,
                          date_written=request['date_written'], author_exposure=request['seen_before_writing'],
                          template_group=mapping['template_group'], teammate_case_ref=request['case_ref'],
                          authorship_verified=False, semantic_novelty_review='NOT_REVIEWED')
            assert result['request'] == request['request_text']
            replaced.append(deepcopy(baseline))
            cases[baseline['case_id']] = result
            logs.append(dict(case_ref=request['case_ref'], mapping=mapping, exact_request_preserved=True,
                changed_fixture_fields={key: {'before': baseline.get(key), 'after': value}
                                        for key, value in result.items() if baseline.get(key) != value}, operator_wording_edits=[]))
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            blocked.append(dict(case_ref=request.get('case_ref'), reason=str(error), wording_changed=False))
    result = list(cases.values())
    groups = {case['template_group'] for case in result}
    teammate_count = sum(bool(case.get('independent_author')) for case in result)
    passed = not blocked and 35 <= len(result) <= 41 and teammate_count >= 13 and len(groups) >= 8
    return dict(status='MAPPINGS_READY_CONTROLS_PENDING' if passed else 'BLOCKED',
        cases=result if passed else None, mapping_log=logs, unmapped_or_incompatible=blocked,
        replaced_drafts=replaced, teammate_cases=teammate_count, heldout_count=len(result),
        heldout_template_groups=len(groups), ladder_template_groups=len({case['template_group'] for case in result if case['kind'] == 'ladder'}),
        full_authorship_gate_passed=False,
        note='Author assertions are recorded, not independently proven. New fixtures still need owner review and zero-model controls.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('requests_file', type=Path)
    parser.add_argument('mappings_file', type=Path)
    args = parser.parse_args()
    result = build(read(args.requests_file)['requests'], read(args.mappings_file)['mappings'])
    output = ROOT/'intake/submissions'/digest(args.requests_file)[:16]
    output.mkdir(parents=True, exist_ok=False)
    (output/'requests-exact.json').write_bytes(args.requests_file.read_bytes())
    (output/'mappings-exact.json').write_bytes(args.mappings_file.read_bytes())
    result['requests_sha256'] = digest(args.requests_file)
    result['mapping_sha256'] = digest(args.mappings_file)
    (output/'mapping-result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print({key: result[key] for key in ('status', 'teammate_cases', 'heldout_count', 'heldout_template_groups')})
    if result['status'] == 'BLOCKED':
        raise SystemExit(2)

if __name__ == '__main__':
    main()
