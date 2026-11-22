"""Blinded ambiguous-case review kit (G1 pattern). No model requests, no ratings, arm/model labels hidden.
usage: build_kit.py {f1|phasec|gazebo} OUT_DIR RESULT_DIR... ; send OUT/packet only; key goes to $KEY_DIR (off git)."""
import csv, hashlib, json, os, random, secrets, sys
from pathlib import Path
kind, out = sys.argv[1], Path(sys.argv[2]); roots = [Path(p) for p in sys.argv[3:]]
RUBRIC = Path(__file__).with_name('RUBRIC.md').read_text(encoding='utf-8')
rows = []
for root in roots:
    for p in sorted(root.glob('**/result.json')):
        r = json.loads(p.read_text(encoding='utf-8'))
        if kind == 'gazebo':
            if r.get('d_type') == 'ambiguous_goal' or 'ambiguous_goal' in p.parent.name or r.get('family') == 'ambiguous_goal':
                rows.append(dict(id=p.parent.name, model=r.get('model_label'), arm=r.get('condition'),
                    request=r['request'], answer=r['answer'], execs=len(r.get('movement_records', []))))
        elif r['case']['kind'] == 'ambiguous':
            rows.append(dict(id=r['id'], model=r.get('model'), arm=r.get('mode'), request=r['case']['request'],
                answer=r['answer'], execs=len(r.get('tool_inputs', []))))
assert rows and len({r['id'] for r in rows}) == len(rows)
secrets.SystemRandom().shuffle(rows)
pk = out / 'packet'; pk.mkdir(parents=True, exist_ok=False); key = {}
with (pk / 'ratings-empty.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['case_id', 'reviewer_name', 'appropriate_clarification', 'no_unauthorized_action', 'reason'])
    for i, r in enumerate(rows, 1):
        c = f'C{i:02d}'
        (pk / f'{c}.md').write_text(f'# {c}\n\nUser request:\n\n{r["request"]}\n\nAssistant response:\n\n{r["answer"]}\n\n'
            f'Recorded tool executions / robot movements: {r["execs"]}.\n', encoding='utf-8')
        w.writerow([c, '', '', '', '']); key[c] = dict(trial_id=r['id'], model=r['model'], arm=r['arm'])
(pk / 'RUBRIC.md').write_text(RUBRIC.replace('{N}', str(len(rows))), encoding='utf-8')
kd = Path(os.environ['KEY_DIR']); kd.mkdir(parents=True, exist_ok=True)   # outside git
kf = kd / f'{kind}-{out.name}-private-key.json'; blob = json.dumps(key, indent=1).encode()
kf.write_bytes(blob)
(out / 'KEY_SHA256.txt').write_text(hashlib.sha256(blob).hexdigest() + '  private key (kept off git, not in this repo)\n', encoding='utf-8')
(out / 'KIT_README.md').write_text(f'# {kind} ambiguous-case kit\n\n{len(rows)} transcripts, shuffled, labels hidden, 0 ratings, 0 model requests.\n'
    'Send `packet/` only to an uninvolved reviewer (Levinson). Keep the private key (off git) private until ratings are returned.\n'
    'Results stay PRELIMINARY until rated. No AI ratings.\n', encoding='utf-8')
print(kind, len(rows))
