"""Read-only readback of pre-interruption traces; never fabricate/re-export spans."""
import inspect
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DESTINATION=ROOT/'artifacts/output-budget-v1-resume-20261022'


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    import httpx
    from phoenix.client import Client
    campaigns=((ROOT/'artifacts/output-budget-v1-20261022','rosa-output-budget-v1-20261022'),
               (ROOT/'artifacts/output-budget-v1-followup-20261022','rosa-output-budget-v1-followup-20261022'))
    rows=[]
    with httpx.Client(base_url='http://127.0.0.1:6006',timeout=60,trust_env=False) as http:
        client=Client(http_client=http)
        for campaign,project in campaigns:
            status=json.loads((campaign/'gazebo/ollama/result.json').read_text())
            for row in status['trials']:
                local=json.loads((campaign/'gazebo/ollama'/row['run_id']/'trace.json').read_text())['spans']
                expected={s['context']['span_id'].removeprefix('0x') for s in local}
                remote=client.spans.get_spans(project_identifier=project,trace_ids=[row['trace_id']],limit=10000)
                received={s['context']['span_id'].removeprefix('0x') for s in remote}
                write(DESTINATION/'recovered-evidence'/row['run_id']/'phoenix-trace.json',remote)
                rows.append({'run_id':row['run_id'],'local_spans':len(expected),'persisted_spans':len(received),
                    'exact_ids_match':expected==received})
        # Capture any persisted children of the externally interrupted trial by
        # timestamp; an unfinished root is not invented or declared complete.
        last=campaigns[-1][0]
        status=json.loads((last/'gazebo/ollama/result.json').read_text())
        recent=client.spans.get_spans(project_identifier=campaigns[-1][1],limit=10000)
        cutoff=status['updated_utc'].replace('+00:00','Z')
        from datetime import datetime
        interrupted=[s for s in recent if datetime.fromisoformat(s['start_time'])>=datetime.fromisoformat(cutoff)]
        write(DESTINATION/'recovered-evidence/interrupted-partial-spans.json',interrupted)
    result={'pass':len(rows)==35 and all(r['exact_ids_match'] for r in rows),
            'saved_trials':len(rows),'rows':rows,'interrupted_partial_spans':len(interrupted),
            'partial_trace_is_not_a_completed_or_scored_trial':True}
    write(DESTINATION/'pre-resume-phoenix-audit.json',result)
    print(json.dumps({'pass':result['pass'],'saved_trials':len(rows),'partial_spans':len(interrupted)}),flush=True)
    if not result['pass']:raise SystemExit(1)


if __name__=='__main__':main()
