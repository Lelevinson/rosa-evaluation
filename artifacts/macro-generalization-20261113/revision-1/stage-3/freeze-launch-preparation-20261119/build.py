"""Build a new held-out workspace, preserving all historical sources/results."""
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE3 = HERE.parent
REV = STAGE3.parent
OLD = REV/'stage-2'
NEW = REV/'stage-4'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, value): p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    NEW.mkdir(exist_ok=False)
    plan = [r for r in read(REV/'stage-1/control-plan.json') if r['block']=='cases' and r['case']['split']=='heldout']
    assert len(plan)==76 and len({r['case']['case_id'] for r in plan})==38
    assert Counter(r['mode'] for r in plan)=={'primitives':38,'macro':38}
    write(NEW/'plan.json', plan)
    ports = {}
    def port(name, replacements):
        before = (OLD/name).read_text(encoding='utf-8')
        after = before
        for a,b in replacements:
            assert a in after, (name, a)
            after = after.replace(a,b)
        (NEW/name).write_text(after, encoding='utf-8')
        (HERE/(name+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile='preserved-stage-2/'+name, tofile='new-stage-4/'+name)), encoding='utf-8')
        ports[name] = dict(original_sha256=digest(OLD/name), new_sha256=digest(NEW/name))
    port('authorization.py', [('request_budget=291','request_budget=611')])
    port('tracing.py', [('rosa-g1-sol-dev-20261114','rosa-g1-sol-heldout-20261119'), ('g1.sol.dev','g1.sol.heldout')])
    port('persisted_audit.py', [('rosa-g1-sol-dev-20261114','rosa-g1-sol-heldout-20261119'), ('g1.sol.dev','g1.sol.heldout')])
    port('recovery.py', [('self.requests>=291','self.requests>=611'), ("'request_cap':291", "'request_cap':611"),
        ('from rosa_reliability.execution import ControlledStop',
         'from rosa_reliability.execution import ControlledStop\nfrom observed_transport import ObservedRecoverableSiwc as RecoverableSiwc')])
    port('runner.py', [
        ('Sol dev','Sol held-out'), ('g1_dev_', 'g1_heldout_'), ('planned\':36', 'planned\':76'),
        ('request_budget=291','request_budget=611'),
        ('from authorization import restore_only,check_models,MODEL',
         'from authorization import restore_only,check_models,MODEL\nfrom runtime_support import journal_progress, freeze_raw_result, evaluate_progress'),
        ('record_start=len(model.request_records)', 'record_start=len(model.request_records)\n    metadata_start=len(transport.error_metadata_records)'),
        ("journal=lambda value:(folder/'inference-progress.json').write_text(json.dumps(\n                    {'inference':value,'snapshot':inv.snapshot()},indent=2)+'\\n'))",
         'journal=lambda value:journal_progress(folder, value, inv, meter, actor, transport, metadata_start, timeout))'),
        ("row['trial_total_seconds']=time.monotonic()-started", "row['trial_total_seconds']=time.monotonic()-started\n        freeze_raw_result(row,folder,transport,metadata_start)"),
        ("'primary_pass':row['primary_pass']", "'legacy_diagnostic_pass':row['primary_pass'], 'effective_status':evaluate_progress(row)['primary_status']"),
        ("assert transport.requests==campaign.requests", "assert transport.requests==campaign.requests"),
    ])
    launch = (OLD/'launch.py').read_text(encoding='utf-8')
    for a,b in [('Sol dev','Sol held-out'), ('G1 Stage2 launch','G1 Stage4 launch'),
                ("read(ROOT/'authorization-review.json')['launch_allowed']", "read(ROOT/'owner-launch-acknowledgment.json')['launch_allowed']"),
                ("str(ROOT/'finish.py')", "str(ROOT/'analyze_results.py')")]:
        assert a in launch
        launch = launch.replace(a,b)
    (NEW/'launch.py').write_text(launch, encoding='utf-8')
    write(NEW/'settings.json', dict(study='G1 revision1 Sol held-out; AI-authored cases', model='gpt-6.1-sol',
        cases=38,trials=76,ordinary_request_cap=608,reserve_cap=3,total_physical_cap=611,backend_seconds=28800,
        calls_per_task=8,output_tokens_per_task=2048,local_tokens_per_call=1024,native_limit=10,tool_limit=16,
        corrections=3,task_seconds=360,max_dispatches=1,native_ratio_band=[.75,1.25],
        censored_backend_flag=8,pair_gap_minutes=30,near_duplicate_probe=False,Qwen_started=False,
        quota='UNKNOWN',authorship='AI-authored cases',template_groups=13,ladder_groups=6))
    write(HERE/'SOURCE_PORTS.json', ports)
    print(json.dumps({'new_workspace':str(NEW),'cases':38,'trials':76,'originals_edited':False}))

if __name__=='__main__':main()
