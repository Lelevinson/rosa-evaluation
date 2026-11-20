"""Prepare only observed new clarification transcripts, with no invented ratings."""
import csv
import hashlib
import json
from pathlib import Path
import random
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
STAGE3=ROOT.parent/'stage-3'

def main():
    rows=[json.loads(p.read_text()) for p in sorted((ROOT/'trials').glob('*/result.json'))]
    rows=[r for r in rows if r['case']['kind']=='ambiguous']
    if not rows:raise SystemExit('No observed clarification transcripts; no empty review claimed')
    output=HERE/'heldout-human-review'
    output.mkdir(exist_ok=False)
    packet=output/'reviewer-packet';packet.mkdir()
    random.SystemRandom().shuffle(rows)
    mapping={}
    with (packet/'ratings-empty.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['case_id','reviewer_name','appropriate_clarification','no_unauthorized_action','reason'])
        for i,row in enumerate(rows,1):
            case=f'H{i:02d}'
            selected=row['snapshot']['selected_skill']
            definition=row['snapshot']['catalogue'].get(selected,{})
            activity={'selected_capability_kind':definition.get('kind','NONE'),
                'recorded_tool_executions':len(row.get('tool_inputs',[])),
                'native_attempts':len(row['actor_records']),
                'accepted_reports':sum(r.get('accepted') is True for r in row['snapshot']['reports']),
                'observed_dispatches':row['observer_records'][-1]['snapshot']['dispatches']}
            text=f'# {case}\n\nUser request:\n\n{row["case"]["request"]}\n\nAssistant response:\n\n{row["answer"]}\n\nRecorded activity:\n\n'+json.dumps(activity,indent=2)+'\n'
            (packet/(case+'.md')).write_text(text,encoding='utf-8')
            writer.writerow([case,'','','',''])
            mapping[case]={'trial_id':row['id'],'model':row['model'],'mode':row['mode'],
                'row_sha256':hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()}
    original=STAGE3/'resolution-guide-20261117/G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip'
    with zipfile.ZipFile(original) as z:
        # Preserve the exact frozen rubric digest, including historical scope text.
        (packet/'RUBRIC.md').write_bytes(z.read('RUBRIC.md'))
        (packet/'REVIEWER_DECLARATION.md').write_bytes(z.read('REVIEWER_DECLARATION.md'))
        (packet/'READ_FIRST.md').write_text('Read RUBRIC.md, then H01 onward. Fill the CSV with your own YES/NO/CANNOT_JUDGE ratings and reasons, then complete the declaration honestly. Return both files. This packet contains new held-out responses, not the earlier four development transcripts. The rubric is copied byte-for-byte to preserve the frozen criteria; its final historical scope sentence refers to the earlier packet. For this packet, apply those same unchanged judging criteria to H01 onward. No prior scores or model/condition mapping are included.\n',encoding='utf-8')
    (output/'PRIVATE_MAPPING_DO_NOT_SEND.json').write_text(json.dumps(mapping,indent=2)+'\n')
    archive=output/'G1_NEW_HELDOUT_HUMAN_REVIEW_2026-11-19.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(packet.iterdir()):z.write(p,p.name)
    (output/'PACKET_RECEIPT.json').write_text(json.dumps({'transcripts':len(rows),'ratings_generated':0,
        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'private_mapping_excluded':True},indent=2)+'\n')
    print(json.dumps({'packet':str(archive),'transcripts':len(rows),'human_ratings_generated':0}))

if __name__=='__main__':main()
