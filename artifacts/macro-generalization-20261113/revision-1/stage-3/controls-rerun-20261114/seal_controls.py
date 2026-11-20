"""Seal fresh control evidence and a new status record without replacing old ones."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STAGE3=ROOT.parent
WORKSPACE=ROOT.parents[5]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (ROOT/'CONTROL_EVIDENCE_MANIFEST.json').exists()
    summary=read(ROOT/'analysis.json')
    assert summary['passed'] and summary['controls']==132
    assert read(ROOT/'phoenix-service.json')['stopped']
    inputs=read(ROOT/'control-input-freeze.json')['files']
    protected=read(ROOT/'protected-before.json')
    assert all(digest(ROOT/name)==value for name,value in inputs.items())
    assert all(digest(WORKSPACE/name)==value for name,value in protected.items())
    status=STAGE3/'LATEST_STAGE3_STATUS_2026-11-14.md'
    assert not status.exists(), 'Preserve the previous current-status receipt'
    status.write_text(f'''# Stage 3 latest status after fresh controls

Updated: **2026-11-14**. **Fresh control rerun complete; freeze remains blocked by instrumentation and reviews.**

The previously pending independent engineering work is now complete: **132/132 scripted controls passed**,
including 20 structural, 76 held-out-designated fixture and 36 dev fixture paths. All 132 local and 132
persisted Phoenix audits passed, matching **{summary['persisted_spans']} spans**. The observer/world suites
passed **{summary['observer_world_unit_methods']} methods**. All eight domain/depth native ratios were 1.00.
These use real public adapters, the unchanged Stage 2 scorer and scripted decisions. They are not live model
results or independent scorer review. Both domains hosted without a protected source change.

The prediction-definition amendment and 20 tests remain preserved. P1-prime/P2 require both domains;
P4 is Against at exactly 20 points; sizes stay 3/5/10; P3 is dropped and P6 descriptive. No prediction is
adjudicated from dev or scripted fixtures. The original 62-file preparation and 13-file amendment remain unchanged.

## Gates

| Gate | Current status | Remaining action |
|---|---|---|
| G-a | PASS | Owner's existing AI-only fallback recorded; no independent case authorship claimed. |
| G-b | PASS | Fresh real-adapter controls, observer tests and exact persisted audits completed. |
| G-c | BLOCKED | Owner disposition of the optional protected HTTP metadata hook, then integrated golden/canary tests. Proposed diff remains unapplied. |
| G-d | Checks PASS; ordered advancement waits on G-c | Censoring/new prediction rules and dev analysis tested; final input hashes wait for instrumentation/review disposition. |
| G-e | BLOCKED | Actual new adversarial scorer review. Delegation to a separate GPT-6 Astra agent was requested, not assumed. |
| G-f | BLOCKED | An uninvolved person's actual four-case clarification ratings. A name alone is not a completed review. |
| G-g | BLOCKED | Final study freeze only after preceding gates pass. Control input/evidence inventories are not G-g. |
| G-h | BLOCKED | Fresh zero-inference restore-only preflight after the freeze, owner review, then separate Stage 4 authorization. |

## Evidence and approval scope

Read [the fresh control report](controls-rerun-20261114/CONTROL_RERUN_REPORT.md),
[prediction update](predictions-amendment-20261114/UPDATE_REPORT.md) and
[unapplied proposed hook](instrumentation/PROPOSED_HTTP_OBSERVATION_HOOK.patch).

The user asked why work was not complete; the remaining independently runnable controls were therefore finished.
The two pending questions ask permission for the protected hook and separate-model scorer review. Neither is
recorded as approved by silence. The clarification review still requires real uninvolved input under the prompt.

No live inference, OAuth, robot action, Gazebo, Git action or upload occurred. The owned local Phoenix service
was stopped normally. **{len(protected)} prior files** and **{len(inputs)} control inputs** matched their hashes.
No earlier source, result, transcript, report, frozen case, archive or review was changed or fabricated.
''',encoding='utf-8')
    files={path.relative_to(ROOT).as_posix():digest(path) for path in sorted(ROOT.rglob('*')) if path.is_file()
        and path.name not in ('CONTROL_EVIDENCE_MANIFEST.json','CONTROL_VERIFICATION.json')}
    write(ROOT/'CONTROL_EVIDENCE_MANIFEST.json',dict(kind='Fresh zero-model control inventory, not a study freeze',
        date='2026-11-14',files=files,latest_status_sha256=digest(status)))
    assert all(digest(ROOT/name)==value for name,value in files.items())
    result=dict(passed=True,verified_files=len(files),protected_files=len(protected),control_inputs=len(inputs),
        mismatches=[],manifest_sha256=digest(ROOT/'CONTROL_EVIDENCE_MANIFEST.json'),
        latest_status_sha256=digest(status),controls=132,persisted_spans=summary['persisted_spans'],
        live_model_requests=0,study_freeze=False,owned_phoenix_stopped=True)
    write(ROOT/'CONTROL_VERIFICATION.json',result)
    print(result)

if __name__=='__main__':main()
