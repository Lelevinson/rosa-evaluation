"""Post-run descriptive reporting only; frozen predictions await real human ratings."""
import sys,json,hashlib,statistics,shutil,subprocess,zipfile,time
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from common import read,verify
from runtime_support import empty_bundle
from adjudication import summarize
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def costs(rows):
    times=[r['task_seconds'] for r in rows]
    return {'attempts':len(rows),'calls':sum(r['inference']['calls'] for r in rows),
      'known_input_tokens':sum(r['inference']['known_input_tokens'] for r in rows),
      'known_output_tokens':sum(r['inference']['known_output_tokens'] for r in rows),
      'incomplete_usage_attempts':sum(not r['inference']['usage_complete'] for r in rows),
      'native_operations':sum(len(r['actor_records']) for r in rows),
      'task_seconds':sum(times),'mean_task_seconds':statistics.mean(times) if times else None,
      'median_task_seconds':statistics.median(times) if times else None,
      'invalid_attempts':sum(r['score']['invalid_attempts'] for r in rows),
      'budget_exhaustions':sum(bool(r['score']['budget_exhaustion']) for r in rows),
      'length_stops':sum(bool(r['score']['length_stop']) for r in rows)}
def compare(rows):return {mode:costs([r for r in rows if r['mode']==mode]) for mode in ['primitives','macro']}
def main():
    state=read(ROOT/'status.json')
    assert state['status']=='COMPLETE' and state['completed']==76
    before=verify(require_seal=True)
    paths=sorted((ROOT/'trials').glob('*/result.json'))
    raw_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    rows=[read(p) for p in paths]
    assert len(rows)==len({r['id'] for r in rows})==76
    assert {r['id'] for r in rows}=={r['id'] for r in read(ROOT/'plan.json')}
    assert all(r['local_audit']['pass'] and read(ROOT/'trials'/r['id']/'phoenix-audit.json')['pass'] for r in rows)
    assert sum(r['inference']['calls'] for r in rows)==state['live_model_requests']
    assert state['charged_total_requests']==state['live_model_requests']+1<=611
    bundle=empty_bundle();summary=summarize(rows,[r['id'] for r in read(ROOT/'plan.json')],bundle,bundle['rubric_sha256'])
    outcomes={r['trial_id']:r for r in summary['outcomes']}
    pairs=defaultdict(dict)
    for r in rows:pairs[r['case']['case_id']][r['mode']]=r
    matched={key for key,pair in pairs.items() if len(pair)==2 and all(outcomes[r['id']]['primary_status']=='PASS' for r in pair.values())}
    matched_rows=[r for r in rows if r['case']['case_id'] in matched]
    evaluable=[r for r in rows if outcomes[r['id']]['primary_status'] in ['PASS','FAIL']]
    per_arm={m:dict(Counter(outcomes[r['id']]['primary_status'] for r in rows if r['mode']==m)) for m in ['primitives','macro']}
    family=[]
    for domain,kind,depth in sorted({(r['case']['domain'],r['case']['kind'],r['case']['native_depth']) for r in rows}):
        subset=[r for r in rows if (r['case']['domain'],r['case']['kind'],r['case']['native_depth'])==(domain,kind,depth)]
        family.append({'domain':domain,'kind':kind,'native_depth':depth,'outcomes':{m:dict(Counter(outcomes[r['id']]['primary_status'] for r in subset if r['mode']==m)) for m in ['primitives','macro']},'costs':compare(subset)})
    fields=['total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration']
    timing={}
    for mode in ['primitives','macro']:
        records=[entry for r in rows if r['mode']==mode for entry in r.get('sanitized_request_records',[])]
        timings=[x.get('generation_info') or {} for x in records]
        captured={field:sum(isinstance(info.get(field),(int,float)) for info in timings) for field in fields}
        totals={field:sum(info[field] for info in timings if isinstance(info.get(field),(int,float))) for field in fields}
        timing[mode]={'physical_records':len(records),'field_presence':captured,'recorded_sums':totals,
          'decode_tokens_per_second':totals['eval_count']/(totals['eval_duration']/1e9) if totals['eval_duration'] else None,
          'prompt_tokens_per_second':totals['prompt_eval_count']/(totals['prompt_eval_duration']/1e9) if totals['prompt_eval_duration'] else None,
          'prompt_eval_cached_count_presence':sum('prompt_eval_cached_count' in x for x in timings),
          'durations_unit':'nanoseconds; sums from recorded fields only','missing_fields_estimated':False}
    starts=[datetime.fromisoformat(state['started_utc'])]
    campaign_seconds=(datetime.fromisoformat(state['completed_utc'])-starts[0]).total_seconds()
    result={'status':'EXECUTION_COMPLETE_HUMAN_REVIEW_PENDING' if summary['semantic_judgments_pending'] else 'EXECUTION_COMPLETE',
      'provenance':'lab hardware; not directly comparable to M4','cases':'AI-authored cases',
      'summary':summary,'outcomes_per_arm':per_arm,'all_attempt_costs':compare(rows),
      'evaluable_costs':compare(evaluable),'matched_success_costs':compare(matched_rows),
      'matched_success_pairs':len(matched),'pending_pairs':sorted(key for key,pair in pairs.items() if any(outcomes[r['id']]['primary_status']=='PENDING_HUMAN_REVIEW' for r in pair.values())),
      'pair_outcomes':[{'case_id':key,**{m:outcomes[r['id']]['primary_status'] for m,r in pair.items()}} for key,pair in sorted(pairs.items())],
      'per_family':family,'timing':timing,'campaign_seconds':campaign_seconds,
      'charged_total_requests':state['charged_total_requests'],'auxiliary_load_requests':1,
      'infrastructure_retries':state['campaign']['infrastructure_retries'],
      'audits':{'local':76,'persisted':76,'all_pass':True},'frozen_verification':before,
      'raw_result_hashes':raw_hashes,'predictions':'WITHHELD_PENDING_REAL_HUMAN_REVIEW; P4 probe NOT RUN; P3 DROPPED',
      'failures':[{'id':r['id'],'error':r['error'],'component_columns':outcomes[r['id']]['component_columns'],
          'codes':r['execution_error_codes'],'length_stop':r['score']['length_stop'],'budget_exhaustion':r['score']['budget_exhaustion']}
          for r in rows if outcomes[r['id']]['primary_status']=='FAIL'],
      'model_requests_for_reporting':0}
    out=ROOT/'operator/completed-report';out.mkdir(exist_ok=False)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    allc=result['all_attempt_costs'];matchc=result['matched_success_costs']
    lines=['# G1 Qwen lab execution report','',
      'Date: **2026-11-19**. **Lab hardware; not directly comparable to M4.**','',
      f"All **76/76** scheduled mock attempts are retained. Outcomes: **{summary['counts']}**. New clarification responses require real blinded human ratings; no previous ratings have been reused.",
      '',f"Requests: **{state['live_model_requests']} inference + 1 auxiliary model load = {state['charged_total_requests']}/611 charged**. Reserve retries: {state['campaign']['infrastructure_retries']}. Campaign elapsed: {campaign_seconds:.2f}s. Local and persisted Phoenix audits: **76/76 each**. All frozen hashes reverified.",
      '', '## Correctness and costs','',
      '| Measure | Primitives | Macro |','|---|---:|---:|',
      f"| Outcomes | {per_arm['primitives']} | {per_arm['macro']} |"]
    for label,key in [('All-attempt calls','calls'),('Known input tokens','known_input_tokens'),('Known output tokens','known_output_tokens'),('Native operations','native_operations'),('Total measured task seconds','task_seconds'),('Mean task seconds','mean_task_seconds'),('Median task seconds','median_task_seconds'),('Invalid attempts','invalid_attempts'),('Length stops','length_stops'),('Budget exhaustion','budget_exhaustions')]:
        lines.append(f"| {label} | {allc['primitives'][key]} | {allc['macro'][key]} |")
    lines+=['',f"**{len(matched)} matched successful pairs** exclude any failed, censored or human-pending pair. These are a conditional efficiency view; all-attempt costs above remain primary operational accounting.",'',
      '| Matched successful pairs | Primitives | Macro |','|---|---:|---:|']
    for key in ['calls','known_input_tokens','known_output_tokens','native_operations','task_seconds']:
        lines.append(f"| {key} | {matchc['primitives'][key]} | {matchc['macro'][key]} |")
    lines+=['','## Returned Ollama timing evidence','']
    for mode in ['primitives','macro']:
        t=timing[mode]
        lines.append(f"- {mode}: {t['physical_records']} physical records; decode {t['decode_tokens_per_second']} tokens/s, prompt {t['prompt_tokens_per_second']} tokens/s from summed recorded counts/durations. Field presence: {t['field_presence']}.")
    lines+=['','Missing counters are not zero or estimated. Prompt cache and cold-load effects are retained. This is not a controlled hardware comparison, and hosted Sol time cannot isolate model speed against this local backend.','',
      '## Scope, limitations and next action','',
      'Frozen G1 AI-authored mock cases, shared tools and matched task budgets were used. This is not new Gazebo work, an unmodified-ROSA comparison, independent case authorship or evidence of general model parity. Condition wording remains part of the manipulated package. The optional catalogue-size probe is not run (P4); P3 was dropped.',
      '',
      'All attempts, unsuccessful outcomes and raw traces are preserved. No runtime prompt tuning, failed-trial replacement, new inference for reporting or architecture change occurred. The independent observer establishes the scoped goal outcome separately from accepted report truthfulness.',
      '',
      'Return the new blinded review CSV and declaration to complete ambiguous-case adjudication. The frozen final analysis and prediction verdicts remain withheld while required judgments are pending. No new experiment is started by this report.',
      '',
      'Detailed per-family outcomes, failure components, timing coverage and raw-result hashes: [completed-report/results.json](operator/completed-report/results.json). Launch evidence: [checklist](operator/LAUNCH_CHECKLIST_ADDENDUM.md).']
    (ROOT/'QWEN_EXECUTION_REPORT.md').write_text('\n'.join(lines)+'\n')
    assert all(sha(ROOT/name)==value for name,value in raw_hashes.items())
    assert verify(require_seal=True)==before
    target=ROOT/'operator/prepare_human_packet.py'
    assert target.is_file(), 'Existing packet helper must be copied with source provenance before reporting'
    p=subprocess.run([sys.executable,'-B',str(target)],capture_output=True,text=True)
    (out/'human-packet-generation.log').write_text(p.stdout+p.stderr);assert p.returncode==0
    time.sleep(12)
    archive=ROOT.parent/'G1_QWEN_LAB_COMPLETED_20261119.zip'
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.tmp'] and p.name!='EXPORT_MANIFEST.json']
    manifest={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    (ROOT/'EXPORT_MANIFEST.json').write_text(json.dumps({'freeze_sha256':sha(ROOT/'freeze.json'),'files_sha256':manifest},indent=2)+'\n')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files+[ROOT/'EXPORT_MANIFEST.json']:z.write(p,p.relative_to(ROOT).as_posix())
    receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files)+1,'outcomes':summary['counts'],'model_requests':0}
    (ROOT.parent/'G1_QWEN_LAB_COMPLETED_EXPORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()

