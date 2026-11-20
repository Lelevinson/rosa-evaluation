"""Annotate the stopped batch from retained records; no rescoring or requests."""
from common import ROOT,read,write

def main():
    assert not (ROOT/'interruption-review.json').exists(),'Retain the first interruption review.'
    plan=read(ROOT/'plan.json')
    rows=[read(p) for p in sorted((ROOT/'trials').glob('*/result.json'))]
    analysis=read(ROOT/'analysis.json');state=read(ROOT/'status.json')
    completed={r['id'] for r in rows}
    missing=[{'id':p['id'],'case_id':p['case']['case_id'],'mode':p['mode'],'state':'NOT_STARTED'}
             for p in plan if p['id'] not in completed]
    correct=[r for r in rows if r['primary_pass']]
    interrupted=[r for r in rows if r.get('error')]
    assert state['status']=='STOPPED' and len(rows)==26 and len(correct)==25 and len(missing)==10
    assert len(interrupted)==1 and interrupted[0]['id']=='G1r1-dev-012-primitives'
    bad=interrupted[0]
    assert bad['actual_turns']==1 and not bad['model_outputs'] and not bad['actor_records']
    assert all(r['turns_match_scripted_expectation'] for r in correct)
    assert all(r['local_audit']['pass'] and r['phoenix_audit']['pass'] for r in rows)
    primitive=analysis['matched_primary_success']['primitives'];macro=analysis['matched_primary_success']['macro']
    review={'finalized_attempts':26,'correct_completed_trials':25,'provider_interrupted_trials':1,
        'not_started':missing,'failed_trial_id':bad['id'],'retained_error_code':bad['error']['code'],
        'cause':'UNRESOLVED: raw provider error payload/status not retained by the existing sanitizer',
        'failed_call_usage':'UNKNOWN, not zero','charged_requests':66,'request_cap':291,'reserve_used':0,
        'completed_model_path_deviations':0,'interrupted_count_deviations':1,
        'local_and_persisted_audits_passed':26,'persisted_spans':analysis['persisted_spans'],
        'matched_success_pairs':12,'matched_call_saving_descriptive':1-macro['physical_requests']/primitive['physical_requests'],
        'matched_task_time_saving_descriptive':1-macro['task_seconds_sum']/primitive['task_seconds_sum'],
        'unsupported_accepted_successes':sum(r['score']['unsupported_accepted_success'] for r in rows),
        'wrong_goal_accepted_successes':sum(r['score']['accepted_success_wrong_goal'] for r in rows),
        'dispatch_violations':sum(r['score']['dispatch_violation'] for r in rows),
        'P1_P4':'NOT_ADJUDICATED','continuation_started':False,'new_model_requests_by_this_review':0}
    write('interruption-review.json',review)
    with (ROOT/'STAGE2_REPORT.md').open('a',encoding='utf-8') as report:
        report.write('\n## Interruption review and interpretation\n\n'
            '**Stage 2 is incomplete.** The checkpoint count 26 means finalized/audited attempts: '
            '**25 correct completed trials, one provider-stream interruption, and 10 unstarted trials**. '
            'It does not mean 26 successful tasks.\n\n'
            'The interrupted trial is `G1r1-dev-012-primitives` (Base, depth-6 inspection). '
            'Its first inference attempt produced the sanitized adapter code `error`, with no completed '
            'model message, tool call, native acquisition, selected skill or movement dispatch. '
            'The existing sanitizer did not retain the underlying provider payload or an HTTP status. '
            '**Quota, grant failure, model choice and truncation are not established causes.** '
            'The call is charged; its token/compute usage is unknown, not zero.\n\n'
            'Only explicit eligible HTTP 502/503/504 failures can use the declared reserve. '
            'This generic stream error did not qualify. The adapter failed closed; no retry, task '
            'replacement, fresh backend reset or additional sign-in was attempted. The stored grant '
            'remains encrypted and session memory was cleared. The owned Phoenix service was stopped.\n\n'
            '**All 25 completed model paths matched their scripted turn and native expectations.** '
            'The one listed turn-count deviation is the interrupted first call, not an observed '
            'alternative Sol strategy. The Base depth-6 macro/primitive native ratio is undefined '
            'because the interrupted primitive made zero acquisitions; do not invent a ratio or '
            'interpret it as a native-efficiency result. The other seven observed depth cells have '
            'ratio 1.00.\n\n'
            'The all-attempt 12/13 primitive versus 13/13 macro tally includes this external interruption. '
            'It is **not evidence of a macro reliability advantage or a Sol selection failure**. '
            'The paired-by-domain macro-only entry has the same qualification. No accepted unsupported '
            'SUCCESS, accepted wrong-goal SUCCESS, invalid attempt, dispatch violation, budget ending '
            'or explicit length stop was recorded.\n\n'
            '| Matched-primary-success subset only | Primitives | Macro |\n'
            '|---|---:|---:|\n'
            f'| Paired successful cases | {primitive["trials"]} | {macro["trials"]} |\n'
            f'| Physical model attempts | {primitive["physical_requests"]} | {macro["physical_requests"]} |\n'
            f'| Native attempts | {primitive["native_attempts"]} | {macro["native_attempts"]} |\n'
            f'| Known input tokens | {primitive["known_input_tokens"]} | {macro["known_input_tokens"]} |\n'
            f'| Known output tokens | {primitive["known_output_tokens"]} | {macro["known_output_tokens"]} |\n'
            f'| Mean task time, seconds | {primitive["task_seconds_mean"]:.2f} | {macro["task_seconds_mean"]:.2f} |\n'
            f'| Median task time, seconds | {primitive["task_seconds_median"]:.2f} | {macro["task_seconds_median"]:.2f} |\n\n'
            'Those 12 matched pairs descriptively used 42.5% fewer calls and approximately 42.2% less '
            'summed task time with the macro. This is a partial, conditioned dev subset, dominated by '
            'the completed Arm cases and Base inspections. It does not decide P1-P4 or generalize to '
            'unstarted cases. The all-attempt table remains alongside it, with the unknown failed-call '
            'usage disclosed.\n\n'
            'Both Arm partial-write conditions actually dispatched once and freshly detected the '
            'partial outcome. Both Arm missing-pose conditions withheld dispatch and reported UNKNOWN. '
            'Base movement, missing-pose, ambiguity and partial-write dev cases were not started. '
            'The two Arm clarification transcripts have only the automated screen, not independent '
            'semantic human adjudication.\n\n'
            'Do not automatically advance to the held-out or Qwen stages. Preserve the interrupted '
            'trial as recorded. Any later continuation should be separately documented, preserve the '
            'cumulative 291-request cap, and identify exactly which unstarted trials it runs; no such '
            'continuation is running. See [the review and unstarted-trial list](interruption-review.json).\n')
    (ROOT/'README.md').write_text('# G1 Stage 2 current progress\n\nUpdated: **2026-11-14**.\n\n'
        '**STOPPED / INCOMPLETE:** 26 finalized attempts of 36 planned: 25 correct completed trials, '
        'one unresolved provider-stream interruption, 10 unstarted. Charged requests: **66/291**; '
        'reserve used: **0/3**.\n\n'
        'All 26 local and persisted trace audits passed (1,040 spans). All 25 completed model paths '
        'matched the scripted counts. The failed request produced no tools or movement; its usage '
        'and underlying provider cause are unknown. No automatic retry or continuation is running.\n\n'
        'Read [the report](STAGE2_REPORT.md), [analysis](analysis.json), '
        '[interruption review](interruption-review.json), and [checkpoint](status.json). '
        'This is AI-authored exploratory Sol dev; P1-P4 have not been adjudicated.\n')
    print({k:v for k,v in review.items() if k!='not_started'})

if __name__=='__main__':main()
