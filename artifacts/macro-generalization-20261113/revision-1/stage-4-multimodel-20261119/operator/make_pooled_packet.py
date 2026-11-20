"""Pooled new-backend clarification packet; labels, ratings and private mapping withheld."""
from pathlib import Path
import json,random,csv,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 output=ROOT/'pooled-human-review';output.mkdir(exist_ok=False);packet=output/'reviewer-packet';packet.mkdir()
 rows=[]
 for slug in ['ministral','granite','llama']:
  for p in (ROOT/'backends'/slug/'trials').glob('*/result.json'):
   row=json.loads(p.read_text())
   if row['case']['kind']=='ambiguous':rows.append((slug,row,p))
 assert rows and len(rows)<=12;random.SystemRandom().shuffle(rows);mapping={}
 with (packet/'ratings-empty.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['case_id','reviewer_name','appropriate_clarification','no_unauthorized_action','reason'])
  for index,(slug,row,path) in enumerate(rows,1):
   case=f'H{index:02d}';snapshot=row['snapshot']
   activity={'selected_capability_kind':snapshot['catalogue'].get(snapshot['selected_skill'],{}).get('kind','NONE'),'tool_executions':len(row['tool_inputs']),'native_attempts':len(row['actor_records']),'accepted_reports':sum(x.get('accepted') is True for x in snapshot['reports']),'observed_dispatches':row['observer_records'][-1]['snapshot']['dispatches']}
   (packet/(case+'.md')).write_text('# '+case+'\n\nUser request:\n\n'+row['case']['request']+'\n\nAssistant response:\n\n'+row['answer']+'\n\nRecorded activity:\n\n'+json.dumps(activity,indent=2)+'\n')
   writer.writerow([case,'','','','']);mapping[case]={'backend':slug,'trial_id':row['id'],'source':str(path.relative_to(ROOT)),'row_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 original=ROOT.parent/'stage-3/resolution-guide-20261117/G1_FOUR_CASE_HUMAN_REVIEW_2026-11-17.zip'
 with zipfile.ZipFile(original) as z:
  for name in ['RUBRIC.md','REVIEWER_DECLARATION.md']:(packet/name).write_bytes(z.read(name))
 (packet/'READ_FIRST.md').write_text('This packet contains new extension responses only, not the earlier development, Sol, or Batch B responses. Apply the unchanged rubric; its historical scope sentence refers to the earlier packet. Fill the blank CSV with your own judgments and reasons and complete the declaration honestly. Prior separate reviews must be disclosed. No model labels, conditions, prior scores or private mapping are supplied. Return CSV and declaration.\n')
 (output/'PRIVATE_MAPPING_DO_NOT_SEND.json').write_text(json.dumps(mapping,indent=2)+'\n')
 archive=output/'G1_EXTENSION_CLARIFICATION_REVIEW_2026-11-19.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in packet.iterdir():z.write(p,p.name)
 (output/'PACKET_RECEIPT.json').write_text(json.dumps({'transcripts':len(rows),'ratings_generated':0,'private_mapping_excluded':True,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2)+'\n')
 print(json.dumps({'packet_transcripts':len(rows),'human_ratings_generated':0}))
if __name__=='__main__':main()

