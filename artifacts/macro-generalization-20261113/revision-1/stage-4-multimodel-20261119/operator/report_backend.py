"""Read-only per-backend descriptive report. Formal frozen analysis waits for real ratings."""
from pathlib import Path
import sys,json,statistics,collections
ROOT=Path(__file__).resolve().parents[1]
slug=sys.argv[1];assert slug in ['ministral','granite','llama']
b=ROOT/'backends'/slug
sys.path.insert(0,str(b))
from common import read,verify
from runtime_support import empty_bundle
from adjudication import summarize
def costs(rows):
 times=[r['task_seconds'] for r in rows]
 return {'attempts':len(rows),'calls':sum(r['inference']['calls'] for r in rows),'known_input_tokens':sum(r['inference']['known_input_tokens'] for r in rows),
 'known_output_tokens':sum(r['inference']['known_output_tokens'] for r in rows),'incomplete_usage_attempts':sum(not r['inference']['usage_complete'] for r in rows),
 'native_operations':sum(len(r['actor_records']) for r in rows),'task_seconds':sum(times),'mean_seconds':statistics.mean(times) if times else None,'median_seconds':statistics.median(times) if times else None,
 'invalid_attempts':sum(r['score']['invalid_attempts'] for r in rows),'length_stops':sum(r['score']['length_stop'] for r in rows)}
def main():
 verify(require_seal=True);rows=[read(p) for p in sorted((b/'trials').glob('*/result.json'))];assert len(rows)==76
 bundle=empty_bundle();summary=summarize(rows,[r['id'] for r in read(b/'plan.json')],bundle,bundle['rubric_sha256'])
 outcomes={x['trial_id']:x for x in summary['outcomes']};pairs=collections.defaultdict(list)
 for row in rows:pairs[row['case']['case_id']].append(row)
 matched={case for case,pair in pairs.items() if len(pair)==2 and all(outcomes[r['id']]['primary_status']=='PASS' for r in pair)}
 views={'all_attempts':rows,'matched_success':[r for r in rows if r['case']['case_id'] in matched]}
 data={'label':'exploratory backend, added after Sol and Qwen results','model':read(b/'MODEL_CONFIG.json'),'summary':summary,'views':{k:{m:costs([r for r in group if r['mode']==m]) for m in ['primitives','macro']} for k,group in views.items()},'matched_success_pairs':len(matched),'formal_analysis':'WITHHELD_PENDING_REAL_HUMAN_RATINGS','P1_prime_scope':'original endpoint is Sol-specific, not a formal new-backend verdict','P3':'DROPPED','P4':'NOT RUN','new_model_requests':0}
 (b/'DESCRIPTIVE_RESULTS.json').write_text(json.dumps(data,indent=2)+'\n')
 lines=['# '+slug+' G1 exploratory backend report','','**Exploratory backend, added after Sol and Qwen results.** Same AI-authored cases; no new case-generality claim.','',str(summary['counts']),'',
 '| Metric: all attempts | Primitives | Macro |','|---|---:|---:|']
 for key in data['views']['all_attempts']['primitives']:
  lines.append('| '+key+' | '+str(data['views']['all_attempts']['primitives'][key])+' | '+str(data['views']['all_attempts']['macro'][key])+' |')
 lines += ['',str(len(matched))+' matched successful pairs; see DESCRIPTIVE_RESULTS.json for conditional costs.','',
 'Raw attempts, independent observer records, native activity and local/persisted audits are retained. Unknown usage is not zero. Accepted report truthfulness is separate from requested-goal correctness.',
 '', 'No template, prompt, parser, schema or budget workaround was applied. A failure under this frozen integration is not a ranking of intrinsic model capability. Formal frozen analysis and H-write closeout await real human ratings. No human labels were generated.']
 (b/'EXECUTION_REPORT.md').write_text('\n'.join(lines)+'\n');verify(require_seal=True)
if __name__=='__main__':main()

