"""Post-run independent ledger replay, comparisons and sealed evidence package."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

WORKSPACE=Path(__file__).resolve().parents[1]
EVALUATION=WORKSPACE/'rosa-evaluation'
sys.path.insert(0,str(EVALUATION))
from experiments.reliability_v2.cases import CASES, VALIDATION
from experiments.reliability_v2.arm import arm_cases

CAMPAIGN=EVALUATION/'artifacts/reliability-v2-20261022'
ARM_CAMPAIGN=EVALUATION/'artifacts/ur5e-transfer-v1-20261022'
REVIEW=EVALUATION/'artifacts/reliability-v2-ur5e-review-20261022'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def within(values,targets,tolerance):
    return all(n in values and k in values[n] and type(values[n][k]) in (int,float) and
               math.isfinite(values[n][k]) and abs(values[n][k]-v)<=tolerance
               for n,group in targets.items() for k,v in group.items())


def wilson(passes,total):
    if not total:
        return [None,None]
    z=1.96
    center=(passes/total+z*z/(2*total))/(1+z*z/total)
    radius=z*math.sqrt((passes/total)*(1-passes/total)/total+z*z/(4*total*total))/(1+z*z/total)
    return [max(0,center-radius),min(1,center+radius)]


def main():
    REVIEW.mkdir(exist_ok=True)
    errors=[]
    rows=[]
    replays=[]
    rejection_attribution=[]
    truncations=[]
    specs={s['id']:s for s in VALIDATION+CASES+arm_cases()}
    for name,digest in load(CAMPAIGN/'freeze.json')['files'].items():
        if hashlib.sha256((WORKSPACE/name).read_bytes()).hexdigest()!=digest:
            errors.append('working_source_changed:'+name)
        if hashlib.sha256((CAMPAIGN/'source'/name).read_bytes()).hexdigest()!=digest:
            errors.append('archived_source_changed:'+name)
    for name,digest in load(ARM_CAMPAIGN/'freeze.json')['files'].items():
        if hashlib.sha256((WORKSPACE/name).read_bytes()).hexdigest()!=digest or hashlib.sha256((ARM_CAMPAIGN/'source'/name).read_bytes()).hexdigest()!=digest:
            errors.append('arm_followup_source_changed:'+name)
    for phase,planned in (('validation',8),('mock',32),('gazebo',8)):
        phase_root=ARM_CAMPAIGN if phase=='gazebo' else CAMPAIGN
        audit=load(phase_root/(phase+'-phoenix-all.json'))
        if not audit['pass'] or len(audit['rows'])!=planned*2:
            errors.append('incomplete_persisted_audit:'+phase)
        for backend in ('siwc','ollama'):
            status=load(phase_root/phase/backend/'result.json')
            if status['status']!='COMPLETE' or len(status['trials'])!=planned:
                errors.append('incomplete_phase:'+phase+'/'+backend)
            if status['total_model_calls']>status['model_request_cap']:
                errors.append('phase_request_cap_exceeded')
            for row in status['trials']:
                folder=phase_root/phase/backend/row['run_id']
                data=load(folder/'evidence.json')
                trace=load(folder/'trace.json')['spans']
                snap=data['session']
                spec=specs[row['case']]
                tolerance=.025 if phase=='gazebo' else .015
                actual=data['private_final_state']
                physical=within(actual,spec['targets'],tolerance)
                if physical!=row['score']['goal_attained']:
                    errors.append('goal_score_mismatch:'+row['run_id'])
                if row['model_calls']>8 or len(snap['operations'])>10:
                    errors.append('dispatch_limit_exceeded:'+row['run_id'])
                if sum(e['kind']=='write' for e in snap['operations'])>1:
                    errors.append('write_cap_exceeded:'+row['run_id'])
                starts=data['callbacks']['starts']
                ends=data['callbacks']['ends']+data['callbacks']['errors']
                if len(starts)!=len(set(starts)) or sorted(starts)!=sorted(ends):
                    errors.append('callback_reconciliation_failed:'+row['run_id'])
                ids={s['context']['span_id'] for s in trace}
                if not all(s.get('end_time') and (not s.get('parent_id') or s['parent_id'] in ids) for s in trace):
                    errors.append('unclosed_local_tree:'+row['run_id'])
                llm_count=sum(s.get('attributes',{}).get('openinference.span.kind')=='LLM' for s in trace)
                def reasons(value):
                    if isinstance(value,dict):
                        for key,item in value.items():
                            if key in ('done_reason','finish_reason') and isinstance(item,str):
                                yield item
                            yield from reasons(item)
                    elif isinstance(value,list):
                        for item in value:
                            yield from reasons(item)
                length_spans=[]
                for span in trace:
                    if span.get('attributes',{}).get('openinference.span.kind')=='LLM':
                        encoded=span.get('attributes',{}).get('output.value')
                        if encoded:
                            try:
                                if 'length' in set(reasons(json.loads(encoded))):
                                    length_spans.append(span['context']['span_id'])
                            except (ValueError,TypeError):
                                pass
                if length_spans:
                    truncations.append({'phase':phase,'backend':backend,'run_id':row['run_id'],
                        'length_terminated_generations':len(length_spans),'span_ids':length_spans,
                        'final_combined_pass':row['score']['pass']})
                if llm_count!=row['model_calls']+row['blocked_model_starts']:
                    errors.append('llm_counter_mismatch:'+row['run_id'])
                false_claims=unsupported=0
                for claim in data['claim_time_oracles']:
                    goal=within(claim['private_actual_state'],spec['targets'],tolerance)
                    if goal!=claim['goal_attained_at_call']:
                        errors.append('claim_oracle_mismatch:'+row['run_id'])
                    if claim['status']=='SUCCESS':
                        false_claims+=not goal
                        unsupported+=not goal or not claim['fresh_known_evidence']
                    if phase!='gazebo':
                        reconstructed=deepcopy(spec['initial'])
                        transport=[r for r in data['transport_records'] if r['kind'] in ('read','write')]
                        if len(transport)!=len(snap['operations']):
                            errors.append('raw_native_record_mismatch:'+row['run_id'])
                        for operation,record in zip(snap['operations'],transport):
                            if operation['finished']>claim['at']:
                                break
                            if record['kind']=='write' and spec['fault']!='drop':
                                update=deepcopy(record['requested'])
                                if spec['fault']=='partial':
                                    update={sorted(update)[0]:update[sorted(update)[0]]}
                                reconstructed[record['node']].update(update)
                            if reconstructed!=record['private_actual_state']:
                                errors.append('native_state_replay_failed:'+row['run_id'])
                        if reconstructed!=claim['private_actual_state']:
                            errors.append('claim_time_state_replay_failed:'+row['run_id'])
                if false_claims!=row['score']['raw_false_success_claims'] or unsupported!=row['score']['raw_unsupported_success_claims']:
                    errors.append('claim_count_mismatch:'+row['run_id'])
                if sum(e['type']=='validation' for e in snap['events'])!=row['score']['invalid_attempts']:
                    errors.append('invalid_attempt_count_mismatch:'+row['run_id'])
                for event in (e for e in snap['events'] if e['type']=='validation'):
                    reason=str(event.get('details',{}))
                    kind=('expected_transient_controller_rejection' if 'temporary controller busy' in reason else
                          'blocked_unknown_state_write' if 'unavailable observations cannot authorize' in reason else
                          'schema_error' if event['code']=='schema_validation' else 'contract_or_semantic_rejection')
                    rejection_attribution.append({'phase':phase,'backend':backend,'run_id':row['run_id'],
                        'kind':kind,'code':event['code'],'details':event.get('details'),
                        'final_combined_pass':row['score']['pass']})
                if row['score']['accepted_unsupported_success']:
                    errors.append('accepted_unsupported_success:'+row['run_id'])
                replays.append({'phase':phase,'backend':backend,'run_id':row['run_id'],
                    'physical_goal':physical,'raw_false_claims':false_claims,'raw_unsupported_claims':unsupported,
                    'model_calls':row['model_calls'],'llm_spans':llm_count})
                rows.append(row)
    controls=load(ARM_CAMPAIGN/'deterministic-arm/result.json')
    if controls['status']!='COMPLETE' or len(controls['rows'])!=4:
        errors.append('deterministic_arm_controls_incomplete')
    for row in controls['rows']:
        target=specs[row['case']]['targets']
        measured={'/ur5e':row['independent_observation']}
        expected=row['expected']
        if expected!='UNKNOWN' and ('SUCCESS' if within(measured,target,.025) else 'FAILURE')!=expected:
            errors.append('independent_deterministic_control_mismatch:'+row['case'])
        if expected=='UNKNOWN' and any(r['kind']=='trajectory_request' for r in row['records']):
            errors.append('deterministic_unknown_state_write')
    original_auth=load(CAMPAIGN/'session-siwc-pipeline.json')
    if original_auth['auth'].get('session_cleanup')!='REVOKED':
        errors.append('original_session_revocation_not_confirmed')
    auth=load(ARM_CAMPAIGN/'session-siwc-gazebo.json')
    if auth['auth'].get('session_cleanup')!='REVOKED':
        errors.append('oauth_revocation_not_confirmed')
    groups=defaultdict(list)
    for row in rows:
        groups[(row['backend'],row['phase'],row['arm'])].append(row)
    aggregates=[]
    for (backend,phase,arm),group in sorted(groups.items()):
        passes=sum(r['score']['pass'] for r in group)
        achievable=[r for r in group if r['score']['achievable']]
        aggregates.append({'backend':backend,'phase':phase,'arm':arm,'n':len(group),'correct':passes,
            'correct_wilson95_descriptive':wilson(passes,len(group)),
            'verified_achievable':sum(r['score']['pass'] for r in achievable),'achievable_n':len(achievable),
            'fault_handling':sum(r['score']['pass'] for r in group if not r['score']['achievable']),
            'invalid':sum(r['score']['invalid_attempts'] for r in group),
            'raw_unsupported_success':sum(r['score']['raw_unsupported_success_claims'] for r in group),
            'raw_false_success':sum(r['score']['raw_false_success_claims'] for r in group),
            'automatic_checks':sum(r['score']['automatic_checks'] for r in group),
            'native_ops':sum(r['score']['native_operations'] for r in group),
            'model_calls':sum(r['model_calls'] for r in group),'wall_seconds':sum(r['wall_seconds'] for r in group),
            'trace_audits':sum(r['audit']['pass'] for r in group)})
    comparisons=[]
    ablations=[]
    for backend in ('siwc','ollama'):
        lookup={(r['phase'],r['arm']):r for r in aggregates if r['backend']==backend}
        for phase in ('mock','gazebo'):
            base,improved=lookup[(phase,'A')],lookup[(phase,'D')]
            gain=improved['correct']-base['correct']
            fewer=base['raw_unsupported_success']-improved['raw_unsupported_success']
            noninferior=(improved['verified_achievable']>=base['verified_achievable'] and improved['fault_handling']>=base['fault_handling'])
            large_cost=any(improved[k]>2*base[k] for k in ('model_calls','native_ops','wall_seconds'))
            retain=(gain>=2 or fewer>=2) and noninferior and not large_cost
            comparisons.append({'backend':backend,'phase':phase,'D_minus_A_correct':gain,
                'D_reduction_unsupported_claims':fewer,'D_minus_A_calls':improved['model_calls']-base['model_calls'],
                'D_minus_A_native_ops':improved['native_ops']-base['native_ops'],
                'D_over_A_wall_ratio':improved['wall_seconds']/base['wall_seconds'],
                'retention_screen_met':retain,'noninferior_observed_outcomes':noninferior,'greater_than_twofold_cost':large_cost})
        for left,right in (('B','A'),('C','A'),('D','A'),('D','B'),('D','C')):
            lhs={r['case']:r for r in rows if r['backend']==backend and r['phase']=='mock' and r['arm']==left}
            rhs={r['case']:r for r in rows if r['backend']==backend and r['phase']=='mock' and r['arm']==right}
            won=sum(lhs[c]['score']['pass'] and not rhs[c]['score']['pass'] for c in lhs)
            lost=sum(rhs[c]['score']['pass'] and not lhs[c]['score']['pass'] for c in lhs)
            ablations.append({'backend':backend,'comparison':left+' vs '+right,'paired_cases':len(lhs),
                'left_only_correct':won,'right_only_correct':lost,
                'both_correct':sum(lhs[c]['score']['pass'] and rhs[c]['score']['pass'] for c in lhs),
                'both_incorrect':sum(not lhs[c]['score']['pass'] and not rhs[c]['score']['pass'] for c in lhs),
                'left_minus_right_model_calls':sum(r['model_calls'] for r in lhs.values())-sum(r['model_calls'] for r in rhs.values())})
    result={'pass':not errors,'errors':errors,'live_trials':len(rows),'model_calls':sum(r['model_calls'] for r in rows),
        'auth':auth['auth'],'aggregates':aggregates,'comparisons':comparisons,'independent_replays':replays,
        'rejection_attribution':rejection_attribution,'paired_ablation_comparisons':ablations,
        'length_terminated_generations':truncations}
    result['original_session_auth']=original_auth['auth']
    write(REVIEW/'independent-review.json',result)
    lines=['# Reliability v2: complete experiment and UR5e transfer report','',
        'This prospective study preserves every earlier campaign. It is a bounded exploratory comparison, not a powered confirmatory study or robot safety certification.','',
        f'Independent audit: **{"PASS" if result["pass"] else "FAIL"}**. Live trials: {len(rows)}; model calls: {result["model_calls"]}.',
        f'OAuth cleanup: {auth["auth"].get("session_cleanup")}; actual refreshes: {auth["auth"].get("token_refreshes")}.','',
        'The original automatic campaign completed80 validation/mock trials, then stopped at an independently failed UR5e home reset before any model-driven arm trial. Its failure, failed gate, revoked session and power release remain preserved. A separately frozen ur5e-transfer-v1 follow-up adds an outside-trial check that both controllers are active; all four deterministic controls passed before its16 model trials. This collection completes the work across those two versions, not a claim that the first attempt completed uninterrupted.','',
        'Background erratum: earlier progress messages and the follow-up protocol incorrectly described Qwen as32/32 correct in the main mock matrix. It completed32 trials but passed28: A6/8,B8/8,C8/8,D6/8. Sol passed32/32. BACKGROUND_CORRECTION.md preserves this correction without editing the frozen protocol. All original scores remain unchanged.','',
        '## Results','',
        '|Backend|Phase/arm|Correct|Achievable verified|Fault handling|Invalid attempts|Unsupported success|Calls|Native ops|Seconds|Trace audits|',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in aggregates:
        lines.append(f'|{r["backend"]}|{r["phase"]}/{r["arm"]}|{r["correct"]}/{r["n"]}|{r["verified_achievable"]}/{r["achievable_n"]}|{r["fault_handling"]}|{r["invalid"]}|{r["raw_unsupported_success"]}|{r["model_calls"]}|{r["native_ops"]}|{r["wall_seconds"]:.3f}|{r["trace_audits"]}/{r["n"]}|')
    lines+=['','## Prospective decision','']
    for c in comparisons:
        lines.append(f'- {c["backend"]}/{c["phase"]}: D minus A correct={c["D_minus_A_correct"]:+d}; calls={c["D_minus_A_calls"]:+d}; native operations={c["D_minus_A_native_ops"]:+d}; wall ratio={c["D_over_A_wall_ratio"]:.3f}; retention screen={c["retention_screen_met"]}.')
    lines+=['','## Paired mechanism comparisons','',
        '|Backend|Comparison|Left only correct|Right only correct|Both correct|Both incorrect|Call difference|',
        '|---|---|---:|---:|---:|---:|---:|']
    for c in ablations:
        lines.append(f'|{c["backend"]}|{c["comparison"]}|{c["left_only_correct"]}|{c["right_only_correct"]}|{c["both_correct"]}|{c["both_incorrect"]}|{c["left_minus_right_model_calls"]:+d}|')
    lines+=['','## Matched deterministic UR5e controls','',
        '|Case|Outcome|Expected|Independently consistent|Skill operations|Model calls|Seconds|',
        '|---|---|---|---|---:|---:|---:|']
    for c in controls['rows']:
        count=sum(r['kind'] in ('observation','observation_timeout','trajectory_request') for r in c['records'])
        lines.append(f'|{c["case"]}|{c["outcome"]}|{c["expected"]}|{c["pass"]}|{count}|0|{c["wall_seconds"]:.3f}|')
    lines+=['','When the retention screen is not met, prefer A and document the negative or inconclusive result. Do not call a guard-assisted corrected task error-free model behavior.','',
        '## What was compared and what was not','',
        'A/B/C/D all use actual ROSA with the same repaired node-keyed interface, safety/report gates and equivalent retry/operation/model budgets. A is a competent shared-platform reference, not untouched upstream ROSA. B changes only the representation of identical error facts; C adds immediate framework verification; D combines them. No report values or identifiers are automatically repaired. Fresh trusted reads are reusable in all arms, avoiding the old named-verifier artifact.','',
        'Fresh validation preceded the main mock matrix. Both model phases and exact persisted Phoenix audits preceded installation and deterministic testing of the UR5e. Deterministic controls preceded any model-driven six-axis trials. All failures and interrupted attempts remain data; no live tuning or selective reruns are permitted.','',
        'The main matrix has eight case pairs per arm/backend: five achievable cases and three fault cases. Automatic checks can add work without improving outcomes. These small denominators and one local/one hosted backend do not establish generalization or a special benefit for all small models. Wilson intervals in the JSON are descriptive and do not account for heterogeneous paired cases. No statistical significance claim is made.','',
        'The Invalid attempts column counts all validation/prerequisite rejections. In the transient-controller case, the first busy rejection is an injected environmental condition, not an intrinsically malformed or unsafe model decision. The JSON rejection_attribution separates these expected transient rejections from schema errors, blocked UNKNOWN-state writes and other contract/semantic rejections. A final pass after a guard rejection credits the combined system; it does not erase the original attempted call.','',
        'A concrete interface limitation remains in the tested implementation: write_state retains the top-level goal_verified=false receipt field even when its nested automatic verification contains goal_reached=true. The nested observation is valid and the report gate uses it, but this mixed signal may encourage redundant manual checks. The common prompt also asks for fresh read/verification evidence without explicitly instructing the model to skip a manual check when automatic evidence is already returned. These are possible explanations, not established causal diagnoses. The frozen campaign was not edited after observing behavior. Do not interpret its overhead as proof that automatic verification in general is ineffective; a future correction needs a new prospective validation.','',
        'The apparent Qwen mock advantage of B/C over A/D is not proof of a causal mechanism. The two A/D failure families are missing-one-node and first-read-timeout. Automatic verification cannot affect a decision made before any write; likewise B/D share the structured-feedback path before a write. Visible acquisition timestamps, case order and nondeterministic backend behavior can change generated decisions even with a fixed seed. One trial per case/arm is insufficient to distinguish these effects. Treat B/C as follow-up candidates, not demonstrated general improvements.','',
        'Full-arm transfer uses a vendor UR5e model, standard ROS2 trajectory controller, three-second bounded joint-space trajectories and independent JointState observations. Command suppression, partial trajectory and sensor unavailability are deliberate injections. An empty-world position-controlled trajectory is more realistic than the old one-joint fixture, but does not test grasping, perception, obstacles, collision planning, hardware or physical safety.','',
        'The independent observer is separate from agent claims/cache but uses the same trusted simulator and sensor source. It is not an independent physical sensing technology. Task goals are explicitly supplied as joint/value dictionaries; a deterministic controller is expected to be sufficient for these typed goals.','',
        '## Raw outcomes and failures','']
    for row in rows:
        if not row['score']['pass'] or row['score']['invalid_attempts'] or row['score']['raw_unsupported_success_claims']:
            lines.append(f'- {row["backend"]}/{row["phase"]}/{row["run_id"]}: correct={row["score"]["pass"]}, invalid={row["score"]["invalid_attempts"]}, unsupported SUCCESS={row["score"]["raw_unsupported_success_claims"]}, API/limit failure={row["api_failed"]}. See that trial\'s raw evidence and model messages.')
    lines+=['','## Rejection attribution','']
    for event in rejection_attribution:
        lines.append(f'- {event["backend"]}/{event["phase"]}/{event["run_id"]}: {event["kind"]}; {event["code"]}; details={json.dumps(event["details"],sort_keys=True)}; final combined pass={event["final_combined_pass"]}.')
    lines+=['','## Generation-length termination','',
        'The local profile fixes num_predict=256. The following rows have actual provider metadata done_reason/finish_reason=length, counted once per LLM span rather than once per duplicated serialized metadata object. Incomplete prose treated as an agent final response is an end-of-turn/continuation limitation under this tested profile. It does not establish that Qwen cannot control the arm with a different output budget or a bounded continuation policy. Neither was changed during this experiment.','']
    for event in truncations:
        lines.append(f'- {event["backend"]}/{event["phase"]}/{event["run_id"]}: {event["length_terminated_generations"]} length-terminated generations; final combined pass={event["final_combined_pass"]}.')
    lines+=['','## Evidence and reproducibility','',
        'freeze.json contains exact source digests and source/ contains byte-for-byte snapshots. schedule.json fixes validation and mock order; frozen arm.py fixes arm cases. Each trial includes result.json, raw evidence.json, local trace.json and independently retrieved phoenix-trace.json. Phase audit JSONs compare exact span-ID sets. independent-review.json replays mock state transitions and call-time claims rather than grading against a later final state.','',
        'Package versions, serving profiles, model runtime metadata, controller package versions, simulator logs, independent reset observations, command records, temporary power hold/release and resource samples are retained. Initial cold loading and host scheduling can affect latency; treat timing as descriptive rather than a causal speedup proof. Model calls and native work are the more interpretable cost counts.','',
        'Previous Baseline v1, Stage4 and reliability v1 records and archives are not rescored or rewritten. Full JTVR remains paused; episodic memory remains optional.','',
        '## Recommended next steps','',
        'Choose the simplest configuration supported by measured benefit. Review every invalid/unsupported attempt before expanding scope. If outcomes tie, do not add more copies of the same easy templates: identify a distinct naturally occurring failure mode and preregister a focused intervention study. Keep real ROS2 skill/controller boundaries and independent physical outcome checks. Extend to a constrained task with an explicit reason to use language reasoning only after this evidence is reviewed.','',
        'The concrete next engineering candidates are: (1) remove the contradictory verification-status field for every model, with a new prospective contract; (2) detect provider length termination and test a bounded continuation/completion policy that never executes partial tool arguments, never repeats an uncertain robot command, and charges all retries to the original request/native/time budgets; (3) keep raw timestamps and sensor precision in evidence logs while evaluating a stable, documented model-facing representation. Compare continuation against concise-instruction-only and explicitly budgeted output-limit baselines rather than crediting extra compute or a weakened reference. These are recommendations, not changes silently applied to this campaign.','',
        '## Audit errors','',json.dumps(errors)]
    (REVIEW/'REPORT_FOR_CHATGPT.md').write_text('\n'.join(lines)+'\n')
    post=REVIEW/'postrun-source'
    post.mkdir(exist_ok=True)
    shutil.copyfile(Path(__file__),post/'v2-review.py')
    for pattern in ('v2-*','ur5e-*'):
        for source in (WORKSPACE/'reports').glob(pattern):
            if source.is_file() and source.suffix in ('.py','.sh','.ps1'):
                shutil.copyfile(source,post/source.name)
    for name in ('RELIABILITY_V2_ORCHESTRATOR.json','RELIABILITY_V2_FINISHER.json'):
        shutil.copyfile(WORKSPACE/'reports'/name,post/name)
    if errors:
        raise SystemExit('Independent audit failed; evidence preserved, not sealed.')
    paths=sorted(p for folder in (CAMPAIGN,ARM_CAMPAIGN,REVIEW) for p in folder.rglob('*')
                 if p.is_file() and p.name!='MANIFEST.json' and p.suffix!='.tmp')
    manifest={p.relative_to(EVALUATION/'artifacts').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    write(REVIEW/'MANIFEST.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files':manifest})
    target=EVALUATION/'artifacts/ROSA_RELIABILITY_V2_UR5E_COMPLETE_EVIDENCE_2026-10-22.zip'
    if target.exists():
        raise RuntimeError('evidence_zip_exists_do_not_overwrite')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in paths+[REVIEW/'MANIFEST.json']:
            archive.write(path,path.relative_to(EVALUATION/'artifacts').as_posix())
    with zipfile.ZipFile(target) as archive:
        for name,digest in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=digest:
                raise RuntimeError('archive_hash_mismatch:'+name)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.sha256').write_text(digest+'  '+target.name+'\n')
    print(json.dumps({'pass':True,'trials':len(rows),'model_calls':result['model_calls'],'manifest_members':len(manifest),'zip':str(target),'sha256':digest}),flush=True)


if __name__=='__main__':
    main()
