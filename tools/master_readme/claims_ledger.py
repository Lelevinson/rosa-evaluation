"""Build the master README 'Claims ledger'. Each row cites evidence files; any figure quoted in a row is listed
as a literal string that must occur in its evidence file, or the build fails.
Usage: python -I tools/master_readme/claims_ledger.py . <out.md>  (exits 1 if any check fails)"""
import sys
from pathlib import Path
repo, out = Path(sys.argv[1]), Path(sys.argv[2])

NOV = 'docs/NOVELTY_AND_RELATED_WORK_2026-11-20.md'
M1 = 'artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md'
M23 = 'docs/M2_M3_COMBINED_REPORT_2026-10-27.md'
M4 = 'artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md'
GS = 'G1_SOL_ADJUDICATED_REPORT_2026-11-19.md'
GQ = 'G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md'
GM = 'G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md'
IR = 'artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md'
F0 = 'docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md'
LAB = 'docs/LAB_CONTAINER_CHECK_2026-11-20.md'
S4 = 'artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md'
SV = 'docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md'
PM = 'PROJECT_MASTER_README.md'
W_F1 = 'artifacts/f1-catalogue-wording-20261121/runs/STAGE1B_ANALYSIS.json'
W_LLA = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-llama/ACCEPTANCE_RESULT.json'
W_LLS = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-llama/SDK_NORMALIZATION.json'
W_GRA = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-granite/ACCEPTANCE_RESULT.json'
W_D2 = 'artifacts/gazebo-d-20261121/runs/heldout/analysis/ANALYSIS.md'
W_PCS = 'artifacts/parity-integration-20261121/phase-b-runs/phase-c-llama/PHASE_C_SUMMARY.json'

A, Q, N = 'Allowed', 'Allowed, with the stated qualification', '**Not allowed**'
# (claim, status, qualification / reason, [evidence files], [(file, literal check), ...])
ROWS = [
 ('A reusable bounded-skill component for NASA-JPL ROSA was built: the LLM selects one registered skill; Python performs its reads, at most one write and a fresh verification', A,
  'Engineering contribution; not an algorithmic novelty.', [M1, M23], [(M1, 'Live Qwen requests: **0**'), (M23, 'M2 passed 10/10 deterministic Gazebo cases')]),
 ('The macro cut LLM calls for every backend with working tool calls', Q,
  'All-attempt G1: Sol 126 → 74, Qwen 123 → 75, Ministral 154 → 83; M4 Sol 44.1% fewer requests. The saving is per model turn, not per unit of robot work.',
  [GS, GQ, GM, M4], [(GS, '| Physical calls | 126 | 74 |'), (GQ, '| Model calls, all attempts | 123 | 75 (39.0% fewer) |'),
                     (GM, '154 → 83'), (M4, '44.1% fewer model requests')]),
 ('Savings track model turns, not native acquisition depth (P1′)', Q,
  'This was predicted by design (the primitive read already batches sources) and supported for Sol; present it as a confirmed design consequence, not a discovery.',
  [GS, NOV], [(GS, 'P1′: approximately constant inspection-call saving across depth | Support')]),
 ('Predictions were frozen before held-out runs', Q,
  'Say "frozen internally before held-out runs", **not** "pre-registered": they were amended after dev data, are not on a public registry, and three backends were added after Sol/Qwen results.',
  [NOV], [(NOV, '**"pre-registered"** overstates it')]),
 ('Costs are reported for all attempts and for matched successes, with infrastructure censoring', A,
  'State both views; never quote only the favourable one.', [GS], [(GS, 'Matched-success reductions')]),
 ('Correctness effects were mixed and small', A,
  'M4 Qwen went 15/20 → 14/20; G1 Qwen known-goal 26/36 → 30/36. Say "mixed", not "improved".',
  [M4, GQ], [(M4, '| Qwen / macro | 14/20 | 53 |'), (GQ, '| Known-goal tasks | 26/36 | 30/36 |')]),
 ('Repairing the Ollama integration profile made Llama and Granite usable', Q,
  'Llama known-goal 21/36 → 28/36, Granite 5/36 → 9/36 (P → M), from 0/36 before. The three repairs changed together, so their individual effects are not isolated; G1 used the old profile.',
  [IR], [(IR, '| Llama 3.1 8B | macro | 28/36 | 113 |'), (IR, '| Granite 3.3 8B | macro | 9/36 | 193 |')]),
 ('Qwen\'s length stops are selection failures, not a need for more output tokens', Q,
  'Inference (H) from 12 traces (8 class A, 4 class C); the F1 wording fix built on it is untested.', [F0], [(F0, '| **Total** | 116 | **12** |')]),
 ('Clarification behaviour was human-reviewed', Q,
  'Say "rated by one teammate with self-attested eligibility"; not independent or external validation.', [GM, NOV],
  [(GM, 'Eligibility is self-attested, not independently verified.')]),
 ('A new algorithm or novel mechanism', N, 'AWO, PyRUA-Lean, BT-Agent, LLMCompiler, ReWOO and SayCan cover the mechanism.', [NOV],
  [(NOV, '| A new algorithm or novel mechanism |')]),
 ('First work to improve or benchmark ROSA', N, 'MetaTool/ROS (vs vanilla ROSA) and ROSClaw (parity protocol vs ROSA) exist.', [NOV],
  [(NOV, '| First work to improve/benchmark ROSA |')]),
 ('Better than (stock) ROSA', N, 'Unmodified ROSA was never run as a baseline (§12 item 20).', [NOV, PM], [(NOV, '| Better than (stock) ROSA |')]),
 ('Improves reliability', N, 'M4 Qwen 15/20 → 14/20; G1 gains are small, grouped, AI-authored and confounded with condition wording.', [NOV, M4],
  [(NOV, '| Improves reliability |'), (M4, '| Qwen / primitives | 15/20 | 91 |')]),
 ('Generalizes to new tasks or robots', N, 'AI-authored, reused cases; mock domains; one Gazebo arm; no physical robot.', [NOV], [(NOV, '| Generalizes to new tasks/robots |')]),
 ('Small local models reach parity with Sol', N, 'Different hardware and provenance; Qwen and Ministral stay below Sol on the same G1 cases.', [NOV],
  [(NOV, '| Small models reach parity with Sol |')]),
 ('Fewer calls means less robot work', N, 'Native operations rose with the macro (G1 Qwen 100 → 106, Ministral 102 → 127).', [NOV, GQ, GM],
  [(NOV, '| Fewer calls means less robot work |'), (GQ, '| Native operations, all attempts | 100 | 106 (more robot work) |'), (GM, '102 → 127')]),
 ('Savings grow with task depth', N, 'The opposite was predicted and supported (P1′); the depth-growth idea (Stage 0 P1) was dropped before testing.', [NOV],
  [(NOV, '| Savings grow with task depth |')]),
 ('Granite/Llama results show the macro does not help', N, 'Those G1 results are tool-call integration failures, not macro evidence.', [NOV, GM],
  [(NOV, '| Granite/Llama show the macro doesn\'t help |')]),
 ('Reliability across repeated runs (pass^k)', N, 'Each G1 case/condition ran once. (The separate M4-family Qwen lab repeat is one replication, not pass^k.)', [NOV],
  [(NOV, '| Reliability across repeated runs (pass^k) |')]),
 ('Independent or externally validated human review', N, 'One teammate reviewer, self-attested eligibility (§12 item 23).', [NOV],
  [(NOV, '| Independent / externally validated human review |')]),
 ('Lab timing shows a controlled speed difference', N, 'The GPU was shared with another project\'s Ollama server; timing is contextual (§12 item 22).', [LAB],
  [(LAB, 'no evidence of interference, but not proven absent')]),
 ('Batching (Stage 4) or the serving change (Phase 1) was an improvement', N, 'Both failed their predefined retention screens.', [S4, SV],
  [(S4, 'the predefined batching retention screen was not met'), (SV, 'no serving candidate retained')]),
 ('The F1 catalogue wording fixes Qwen', N, 'F1 Stage 1b held-out ran (verdict NOT ADOPTED): Qwen known-goal net 0 (needed ≥ 3).', [W_F1], [(W_F1, '"net": 0'), (W_F1, '"threshold": 3')]),
 ('The F1 wording fixed the mechanism it targeted', Q, 'Qwen inspection-first on movement types 4 → 0, but no net pass gain; the 4 → 0 count is a diagnostic, not a pass-rate claim; laptop stratum.', [W_F1], [(W_F1, '"base": 4')]),
 ('Llama 3.1 8B can be integrated under the parity rules', Q, 'Admitted with native-schema-v1 on the laptop; SDK list-string normalization (14 of 86 raw calls) is assistance and reported separately.', [W_LLA, W_LLS], [(W_LLA, '"model_pass": true'), (W_LLS, '"raw_tool_calls": 86'), (W_LLS, '"calls_with_string_encoded_list_or_object": 14')]),
 ('Granite 3.3 8B can be integrated under the parity rules', N, 'Not adaptable under the parity rules (schema-valid 0.791 / 0.809; double-wrapped arguments would need argument repair).', [W_GRA], [(W_GRA, '"model_pass": false'), (W_GRA, '"schema_valid_rate": 0.7906976744186046')]),
 ('On fresh Gazebo cases (D2) the macro cut calls for all four models without lowering passes', Q, 'Matched-pair call reduction 33–48%; macro passes ≥ primitives for Sol, Qwen and Llama, and 15 vs 16 for Ministral (not worse by the frozen rule); native operations not lower in macro was **against** for Qwen; 18 known-goal per arm, laptop stratum, ambiguous cases PRELIMINARY.', [W_D2], [(W_D2, '| 0.4783 |'), (W_D2, '| 0.3333 |')]),
 ('The macro helps Llama', N, 'D2 shows 8 → 11, but the Phase C rerun shows primitives 23/38 → macro 20/38; opposite directions, not pooled.', [W_D2, W_PCS], [(W_D2, '| llama | primitives | 8/18'), (W_PCS, '"PASS": 43')]),
 ('Weekend ambiguous-case results are final', N, 'PRELIMINARY until a human rates the blinded kits. Kit keys were pushed publicly once and the kits regenerated before any rating (2026-11-22).', [W_PCS], [(W_PCS, '"final_correctness_ready": false')]),
 ('Qwen was trained or its weights improved; JTVR or episodic memory was completed; physical-robot safety was shown; the full ROSA catalogue was benchmarked', N,
  'None of these happened (§17 closing note).', [PM], [(PM, 'memory/JTVR was completed, or physical robot safety was demonstrated')]),
]

problems, cache = [], {}
for claim, status, why, files, checks in ROWS:
    for f in files:
        if not (repo / f).exists():
            problems.append(('missing file', f))
    for f, lit in checks:
        text = cache.setdefault(f, (repo / f).read_text(encoding='utf-8', errors='replace'))
        if lit not in text:
            problems.append((f, lit))
if problems:
    for p in problems:
        print('FAILED', p)
    sys.exit(1)

def link(f):
    return 'this README' if f == PM else f'[{Path(f).name}]({f})'

lines = ['## Claims ledger (what the report may and may not say)', '',
 'Added 2026-11-21. It starts from the novelty review\'s "claims we must NOT make" table, plus §12 and §17.',
 '"Allowed" claims still need their qualification in the report text. Figures quoted here were checked',
 'mechanically against the linked evidence (`tools/master_readme/claims_ledger.py`). Results per study: see',
 '[Results at a glance](#results-at-a-glance-all-studies). Suggested wording for the contribution statement:',
 f'[novelty review §4]({NOV}).', '',
 '| Claim | Status | Qualification / reason | Evidence |', '|---|---|---|---|']
for claim, status, why, files, _ in ROWS:
    lines.append(f'| {claim} | {status} | {why} | {", ".join(link(f) for f in files)} |')
lines += ['', f'Ledger checks: {sum(len(r[4]) for r in ROWS)} literal strings across {len(ROWS)} rows, all found.', '']
out.write_text('\n'.join(lines), encoding='utf-8', newline='\n')
print('rows', len(ROWS), 'checks', sum(len(r[4]) for r in ROWS), 'all found')
