"""Update living context after successful independent reconciliation only."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parents[3]


def main():
    d = json.loads((BASE / 'evidence/INDEPENDENT_RERUN_ANALYSIS.json').read_text(encoding='utf-8'))
    assert d['all_checks_pass'] and d['operator']['phase'] == 'EXECUTION_COMPLETE'
    master = EVAL / 'PROJECT_MASTER_README.md'
    original = master.read_bytes()
    backup = BASE / 'preparation/PROJECT_MASTER_BEFORE_COMPLETION.md'
    assert not backup.exists(), 'Do not overwrite a context checkpoint'
    backup.write_bytes(original)
    text = original.decode('utf-8').replace('\r\n', '\n')
    start = text.index('**Active authorized work - integration profile and reruns, 2026-11-17.**')
    end = text.index('**Latest completed investigation - Llama/Granite integration, 2026-11-17.**', start)
    section = '''**Latest completed work - native-schema integration and robot reruns, 2026-11-17.**
The opt-in `native-schema-v1` profile was implemented and the authorized **80 Llama + 80 Granite Gazebo attempts completed**. This is a separate replication of known M4 cases, not a rescore or replacement of any historical result and not G1 held-out testing. Each model has40 attempts per condition:36 known-goal tasks and4 ambiguous requests. All16 ambiguous attempts across the two models remain pending actual human semantic review; their legacy regex scores are diagnostic.

| New backend/profile | Known-goal correct P / M | All-attempt calls P / M | Mean task seconds P / M |
|---|---:|---:|---:|
'''
    for model, value in d['models'].items():
        p, m = value['summary']['primitives'], value['summary']['macro']
        section += f"| {model}, native-schema-v1 | {p['known_goal_correct']}/36 / {m['known_goal_correct']}/36 | {p['calls']} / {m['calls']} | {p['mean_seconds']:.2f} / {m['mean_seconds']:.2f} |\n"
    section += '''
Both previous configurations scored0/36 in each condition; those results remain frozen and available. The new profile adds model-native formatting guidance and current bound schemas to system messages and explicitly enforces HTTP stream=false. It does not choose skills, alias arguments, relax verification or automatically replay robot commands. Existing SDK argument normalization remains combined-system assistance. Actual HTTP bodies/responses and corresponding trace metadata were archived; the final tokenized/rendered Ollama prompt was not captured. The original adapter remains unchanged; the new module is `rosa-research/src/rosa_backends/tool_contract_ollama.py` and is opt-in.

Seven zero-network checks,12 deterministic mock controls,24 live validation attempts and20 deterministic Gazebo controls preceded the160 live robot attempts. Fresh validation scored9/12 for Llama and6/12 for Granite. The functional gate required at least one healthy complete loop in each mode, with all safety/tracing/budget checks passing; it was not an all-case reliability gate. The mock ineffective-write checker could accept a truthful no-write failure: that cell does not prove a failed command was attempted. The main Gazebo scorer kept the original stricter fault-exercise/dispatch checks. The initial float-versus-bool fixture defect stopped deterministic validation with zero model calls; its failed source/control/archive are retained, and a documented fixture-only revision preceded all live validation outcomes.

All216 completed validation/control/live attempts in this campaign passed local and persisted Phoenix audits. Independent read-only reconciliation verified archive manifests,75 frozen source/config hashes including the original69, model digests, schedule order, raw/checkpoint consistency, actual wire calls, token/resource bounds and cleanup. This is scripted evidence reconciliation, not outside scientific replication or a human semantic review. Validation budgets were96 requests/model; robot budgets were643/model, with the original8-call,2048-output-token and360-second task limits retained.

Costs above include all40 attempts, including failures and ambiguity. Task latency excludes simulator setup/reset and persisted-audit overhead; campaign elapsed time and matched-success costs are in the full report. Accepted evidence-grounded SUCCESS for a wrong user goal remains a separate failure category. Fewer calls or fast failure does not establish reliability. See the per-family, discordant-pair, native-operation and fault-exercise tables before choosing a backend.

The profile and explicit HTTP setting changed together, so their individual effects are not isolated. Primitive/macro mode and its original condition sentence remain coupled; a selection effect cannot be separated from condition wording. Four repetitions of familiar cases do not demonstrate independent generalization or intrinsic model parity. Older Qwen/Ministral serving profiles differ; no new Sol trial was run and no historical hosted comparison was replaced. No global default backend switch, new architecture or further study was authorized by completion of this replication. G1's existing scorer, instrumentation and real human-review gates remain unchanged.

Current evidence: [complete integration-rerun report](artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md), [independent raw-data analysis](artifacts/integration-rerun-20261117-r1/evidence/INDEPENDENT_RERUN_ANALYSIS.json), [shareable report and evidence ZIP](artifacts/integration-rerun-20261117-r1/delivery/ROSA_NATIVE_SCHEMA_RERUN_REPORT_AND_EVIDENCE_2026-11-17.zip). The original Qwen lab repeat and first four-model lab study below are preserved reference configurations. Current documentation and evidence are backed up under the owner's lab project; no public upload or Git push was performed.

'''
    text = text[:start] + section + text[end:]
    text = text.replace('Next engineering step: implement an opt-in profile keeping current schemas and native formatting guidance visible, explicitly select HTTP streaming, and validate it on fresh complete-loop fixtures before another robot benchmark.',
        'That recommendation was subsequently implemented in the separately labeled native-schema rerun above; this investigation remains preserved as its preceding diagnostic evidence.')
    text = text.replace('**Latest completed execution ? lab local-model replication, 2026-11-17.**',
        '**Earlier completed execution - first lab local-model replication, original profiles, 2026-11-17.**')
    master.write_text(text, encoding='utf-8', newline='\n')
    (BASE / 'evidence/PROJECT_MASTER_CONTEXT_2026-11-17.md').write_bytes(master.read_bytes())
    print('Master updated with independently verified completed rerun; prior bytes preserved.')


if __name__ == '__main__':
    main()
