"""Record a dated preparation checkpoint, preserving the prior living context."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent.parents[3]
master = EVAL / 'PROJECT_MASTER_README.md'
original = master.read_bytes()
backup = HERE / 'PROJECT_MASTER_BEFORE_RESUMPTION.md'
assert not backup.exists()
backup.write_bytes(original)
text = original.decode('utf-8').replace('\r\n', '\n')
marker = '**Research standards adopted'
assert marker in text
entry = '''**G1 preparation resumed - 2026-11-19.** The owner returned to the three
outstanding Stage3 items: human-adjudicated clarification scoring, reduced error
metadata coverage with protected source unchanged, and actual uninvolved review
of four G1 cases. The two concrete methodological amendments still await explicit
confirmation; real human ratings/declaration have not been supplied. The four-case
ZIP and12 sealed Astra review artifacts verified intact. The old protection check
reports one mismatch, the living master after authorized updates; its FAIL result
is retained, and a new freeze must explicitly disposition mutable-document scope.
All other checked protected entries match. No new source/scoring change, review
substitution, inference, credential action or held-out launch occurred. See the
[current G1 checkpoint](artifacts/macro-generalization-20261113/revision-1/stage-3/LATEST_STAGE3_STATUS_2026-11-19.md).
Earlier dated checkpoints and all experimental evidence are preserved.

'''
text = text.replace(marker, entry + marker, 1)
master.write_text(text, encoding='utf-8', newline='\n')
(HERE / 'MASTER_UPDATE.json').write_text(json.dumps({'date':'2026-11-19',
    'before_sha256':hashlib.sha256(original).hexdigest(),
    'after_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
    'kind':'DOCUMENTED_PREPARATION_RESUMPTION_NOT_NEW_EXPERIMENT'},indent=2)+'\n')
print('Living master updated; prior bytes preserved. No experimental records changed.')
