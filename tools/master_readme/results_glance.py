"""Build the 'Results at a glance' section. Every row lists literal strings that MUST occur in its source file;
the build fails otherwise. Usage: python -I tools/master_readme/results_glance.py . <out.md>  (exits 1 if any figure is missing from its source)"""
import re, sys
from pathlib import Path
repo, out = Path(sys.argv[1]), Path(sys.argv[2])

S4 = 'artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md'
R1 = 'artifacts/reliability-v1-20261022/REPORT_FOR_CHATGPT.md'
R2 = 'artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md'
OB = 'artifacts/output-budget-v1-resume-20261022/REPORT_FOR_CHATGPT.md'
WL = 'artifacts/workflow-live-v1-20261022/REPORT_FOR_CHATGPT.md'
WR = 'artifacts/workflow-reference-v1-20261022/REPORT_FOR_CHATGPT.md'
MT = 'artifacts/macro-transfer-v1-resume-r1-20261023/COMBINED_REPORT_FOR_CHATGPT.md'
PC = 'artifacts/prompt-contract-v1-live-resume-r2-20261026/COMBINED_VALIDATION_REPORT.md'
MF = 'artifacts/macro-focus-v2-20261026/REPORT.md'
M1 = 'artifacts/macro-module-v1-20261027/M1_ACCEPTANCE_REPORT.md'
M23 = 'docs/M2_M3_COMBINED_REPORT_2026-10-27.md'
M4 = 'artifacts/macro-m4-20261027/FINAL_REPORT_FOR_CHATGPT.md'
SV = 'docs/QWEN_SERVING_PHASE1_REPORT_2026-11-13.md'
LM = 'artifacts/lab-multimodel-20261117/evidence/DETAILED_COMPARISON_REPORT.md'
QR = 'artifacts/qwen-lab-repeat-20261117/evidence/QWEN_LAB_REPEAT_COMPARISON_REPORT.md'
IF = 'artifacts/lab-integration-20261117/evidence/INTEGRATION_FINDINGS_2026-11-17.md'
IR = 'artifacts/integration-rerun-20261117-r1/evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md'
G2 = 'artifacts/macro-generalization-20261113/revision-1/STAGE2_RESULTS_AND_PROBLEMS_2026-11-14.md'
GS = 'G1_SOL_ADJUDICATED_REPORT_2026-11-19.md'
GQ = 'G1_QWEN_ADJUDICATED_REPORT_2026-11-20.md'
GM = 'G1_MULTIMODEL_ADJUDICATED_REPORT_2026-11-20.md'
F0 = 'docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md'

W_F1 = 'artifacts/f1-catalogue-wording-20261121/runs/STAGE1B_ANALYSIS_WITH_RATINGS.json'
W_LLA = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-llama/ACCEPTANCE_RESULT.json'
W_LLS = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-llama/SDK_NORMALIZATION.json'
W_GRA = 'artifacts/parity-integration-20261121/phase-b-runs/acceptance-granite/ACCEPTANCE_RESULT.json'
W_D2 = 'artifacts/gazebo-d-20261121/runs/heldout/analysis-with-ratings/ANALYSIS.md'
W_PCS = 'artifacts/parity-integration-20261121/phase-b-runs/phase-c-llama/PHASE_C_SUMMARY_WITH_RATINGS.json'

# (study, setting, backend, denominator/conditions, correctness, cost, source, [literal checks])
ROWS = [
 ('Stage 4 batching (2026-10-21)', 'mock + Gazebo, 4 arms', 'Sol', '80 attempts', '6 failures / 80', '—', S4,
  ['6 failures out of 80 attempts', 'All 160 live trials']),
 ('', '', 'Qwen', '80 attempts', '72 failures / 80; retention screen not met for either backend', '—', S4,
  ['72 failures out of 80 attempts', 'the predefined batching retention screen was not met']),
 ('Reliability v1 (2026-10-22)', 'mock 4 arms (A–D) + Gazebo A/D', 'Sol', 'mock 8 per arm; Gazebo 2 per arm', 'every arm 8/8 (mock), 2/2 (Gazebo)', '164 model calls', R1,
  ['| siwc | mock/A | 8/8', '| siwc | mock/D | 8/8', '| siwc | gazebo/A | 2/2', '164 model calls']),
 ('', '', 'Qwen', 'same', 'every arm 8/8 (mock), 2/2 (Gazebo)', 'mock calls 43 (A) → 38 (D)', R1,
  ['| ollama | mock/A | 8/8 | 4/4 | 4/4 | 43', '| ollama | mock/D | 8/8 | 4/4 | 4/4 | 38', '| ollama | gazebo/A | 2/2']),
 ('Reliability v2 + UR5e (2026-10-22)', 'mock 4 arms, validation, Gazebo UR5e', 'Sol', '96 live trials (both backends)', 'mock 32/32; Gazebo 4/4 per arm', 'retention screen not met', R2,
  ['Live trials: 96', 'Sol passed32/32', '|siwc|gazebo/A|4/4|', 'retention screen=False']),
 ('', '', 'Qwen', 'same', 'mock 28/32 (A 6/8, B 8/8, C 8/8, D 6/8); Gazebo 1/4 per arm', 'retention screen not met', R2,
  ['passed28: A6/8,B8/8,C8/8,D6/8', '|ollama|gazebo/A|1/4|', '|ollama|gazebo/D|1/4|']),
 ('Qwen output budget (2026-10-22)', 'UR5e, 5 conditions × 8', 'Qwen', '40/40 trials', 'L256 2/8, L512 3/8, L1024 5/8, C256 1/8, R256 2/8; no candidate retained', '—', OB,
  ['completed trials: 40/40', '|L256|2|', '|L512|3|', '|L1024|5|', '|C256|1|', '|R256|2|', 'prospective candidate screen=False']),
 ('Workflow live (2026-10-22)', 'mock, 6 cases', 'Sol', '6 per condition', 'model 6/6, program 6/6', 'calls 29 → 15', WL,
  ['| siwc | model | 6/6 | 2/2 | 29 |', '| siwc | program | 6/6 | 2/2 | 15 |']),
 ('', '', 'Qwen', '6 per condition', 'model 6/6, program 5/6; progression gate False', 'calls 35 → 28', WL,
  ['| ollama | model | 6/6 | 2/2 | 35 |', '| ollama | program | 5/6 | 2/2 | 28 |', 'Both-backend progression gate: **False**']),
 ('Report reference + UR5e (2026-10-22)', 'mock + Gazebo, 4 cases each', 'Sol', '4 per cell', 'all 4/4', 'Gazebo calls 19 → 8', WR,
  ['| gazebo | siwc | model | 4/4 | 19 |', '| gazebo | siwc | program | 4/4 | 8 |', '| mock | siwc | program | 4/4 | 9 |']),
 ('', '', 'Qwen', '4 per cell', 'mock 4/4 both; Gazebo model 3/4, program 4/4', 'Gazebo calls 18 → 14', WR,
  ['| gazebo | ollama | model | 3/4 | 18 |', '| gazebo | ollama | program | 4/4 | 14 |', '| mock | ollama | program | 4/4 | 12 |']),
 ('Macro transfer (2026-10-23)', 'Gazebo UR5e, 6 cases × 3 conditions', 'Sol', '6 per condition', 'model / macro / workflow 6/6 each', 'calls 29 / 14 / 14', MT,
  ['| siwc | model | 6/6 | 29 |', '| siwc | macro | 6/6 | 14 |', '| siwc | workflow | 6/6 | 14 |']),
 ('', '', 'Qwen', '6 per condition', 'model 4/6, macro 5/6, workflow 5/6', 'calls 39 / 22 / 21', MT,
  ['| ollama | model | 4/6 | 39 |', '| ollama | macro | 5/6 | 22 |', '| ollama | workflow | 5/6 | 21 |']),
 ('Prompt-contract validation (2026-10-26)', 'known cases, 3 conditions', 'Sol', '9 scoreable (1 censored)', '9/9', 'calls 16 / 8 / 8 (model / macro / workflow)', PC,
  ['Sol: 9/9 correct completed scoreable outcomes', '| model | 3/3 | 16 |', '| macro | 3/3 | 8 |']),
 ('', '', 'Qwen', '9', '9/9', '34 requests', PC, ['Qwen: 9/9 correct completed outcomes,34 model requests']),
 ('Macro-focus pilot (2026-10-26)', '6 cases × 2 reps × 3 conditions', 'Sol', '12 per condition', 'model / macro / workflow 12/12 each', 'calls 60 / 32 / 32', MF,
  ['| model | 12/12 | 60 |', '| macro | 12/12 | 32 |', '| workflow | 12/12 | 32 |']),
 ('', '', 'Qwen', '33 of 36 rows (stopped)', 'model 8/11, macro 9/11, workflow 7/11; no retention claim', 'calls 61 / 31 / 34', MF,
  ['Completed/audited trial rows: 33/33', '| model | 8/11 | 61 |', '| macro | 9/11 | 31 |', '| workflow | 7/11 | 34 |',
   'INCOMPLETE_OR_AUDIT_FAILURE_NO_RETENTION_CLAIM']),
 ('M1 reusable module (2026-10-27)', 'engineering acceptance', '—', 'no live trials', 'accepted', '0 live model requests', M1, ['Live Qwen requests: **0**']),
 ('M2 / M3 (2026-10-27)', 'Gazebo UR5e', 'deterministic / Sol / Qwen', 'M2 10 cases; M3 3 per backend', 'M2 10/10; M3 deterministic 3/3, Sol 3/3, Qwen 2/3', '—', M23,
  ['M2 passed 10/10 deterministic Gazebo cases', 'reference 3/3, Sol 3/3, Qwen 2/3']),
 ('**M4** (2026-10-27)', 'Gazebo UR5e, 10 families × 2 reps', 'Sol', '20 per condition', 'primitives 20/20 → macro 20/20', 'requests 68 → 38; mean task s 16.42 → 9.73', M4,
  ['| Sol / primitives | 20/20 | 68 |', '| Sol / macro | 20/20 | 38 |', '| Sol / primitives | 328.36 | 16.42', '| Sol / macro | 194.58 | 9.73']),
 ('', '', 'Qwen', '20 per condition', 'primitives 15/20 → macro 14/20', 'requests 91 → 53; mean task s 133.49 → 85.18', M4,
  ['| Qwen / primitives | 15/20 | 91 |', '| Qwen / macro | 14/20 | 53 |', '| Qwen / primitives | 2,669.72 | 133.49', '| Qwen / macro | 1,703.63 | 85.18']),
 ('Qwen serving Phase 1 (2026-11-13)', 'replay of M4 inputs, no tools', 'Qwen A vs B', '11 unique inputs', 'tool-call agreement 7/10 (9/10 required); B not retained', 'median gen tok/s 8.388 vs 8.082', SV,
  ['| Unique-input median generation tokens/s | 8.388 | 8.082 |', '**7/10**']),
 ('Lab local-model replication (2026-11-17)', 'lab Gazebo, M4 families, 40 per condition', 'Qwen3.5 9B', '36 known-goal per condition', 'primitives 27/36 → macro 28/36', 'calls 188 → 98', LM,
  ['| Qwen3.5 9B | primitives | 27/36 | 40/40 | 188 |', '| Qwen3.5 9B | macro | 28/36 | 40/40 | 98 |']),
 ('', '', 'Ministral 3 8B', 'same', '28/36 → 28/36', 'calls 156 → 82', LM,
  ['| Ministral 3 8B | primitives | 28/36 | 40/40 | 156 |', '| Ministral 3 8B | macro | 28/36 | 40/40 | 82 |']),
 ('', '', 'Llama 3.1 8B', 'same', '0/36 → 0/36 (integration failure)', 'calls 211 → 193', LM,
  ['| Llama 3.1 8B | primitives | 0/36 | 40/40 | 211 |', '| Llama 3.1 8B | macro | 0/36 | 40/40 | 193 |']),
 ('', '', 'Granite 3.3 8B', 'same', '0/36 → 0/36 (integration failure)', 'calls 40 → 40', LM,
  ['| Granite 3.3 8B | primitives | 0/36 | 40/40 | 40 |', '| Granite 3.3 8B | macro | 0/36 | 40/40 | 40 |']),
 ('Qwen lab repeat (2026-11-17)', 'second run of the replication', 'Qwen3.5 9B', '36 known-goal per condition', 'primitives 26/36 → macro 28/36', 'calls 185 → 97', QR,
  ['| lab_run_2 | primitives | 26/36 | 185 |', '| lab_run_2 | macro | 28/36 | 97 |']),
 ('Llama/Granite integration diagnosis (2026-11-17)', 'native-call probes, no robot', 'Llama, Granite', '48 requests', 'template/interface defects found (see report)', '48 requests', IF,
  ['All 48 scheduled local requests were made once']),
 ('Integration repair rerun (2026-11-17)', 'lab Gazebo, M4 families, repaired profile', 'Llama 3.1 8B', '36 known-goal per condition', 'primitives 21/36 → macro 28/36', 'calls 190 → 113', IR,
  ['| Llama 3.1 8B | primitives | 21/36 | 190 |', '| Llama 3.1 8B | macro | 28/36 | 113 |', 'All **160/160 robot attempts** completed']),
 ('', '', 'Granite 3.3 8B', 'same', 'primitives 5/36 → macro 9/36', 'calls 210 → 193', IR,
  ['| Granite 3.3 8B | primitives | 5/36 | 210 |', '| Granite 3.3 8B | macro | 9/36 | 193 |']),
 ('G1 Stage 2 dev (2026-11-14)', 'G1 mock arm/base, dev', 'Sol', '18 per condition', 'primitives 17/18 → macro 18/18', 'inference attempts 60 → 34', G2,
  ['| Primary correct | 17/18 | 18/18 |', '| Charged physical inference attempts | 60 | 34 |']),
 ('**G1 held-out** (2026-11-19/20)', 'G1 mock arm/base, held-out, 38 per condition', 'Sol', '38 per condition; 3 primitive attempts censored', 'V2 35/35 → 38/38; V3 35/38 → 38/38', 'calls 126 → 74; mean task s 13.273 → 8.361', GS,
  ['| V2: correct / evaluable | 35/35 | 38/38 |', '| V3: correct / scheduled, censored counted as failures | 35/38 (92.1%) | 38/38 (100%) |',
   '| Physical calls | 126 | 74 |', '| Mean task seconds | 13.273 | 8.361 |']),
 ('', '', 'Qwen3.5 9B', '38 per condition (36 known-goal + 2 ambiguous)', 'all 26/38 → 31/38; known-goal 26/36 → 30/36; ambiguous 0/2 → 1/2', 'calls 123 → 75; mean task s 8.48 → 6.31', GQ,
  ['| All tasks (incl. 2 ambiguous per arm) | **26/38** | **31/38** |', '| Known-goal tasks | 26/36 | 30/36 |',
   '| Ambiguous (clarification) tasks | 0/2 | 1/2 |', '| Model calls, all attempts | 123 | 75 (39.0% fewer) |', '| Mean task seconds, all attempts | 8.48 | 6.31 |']),
 ('', '', 'Ministral 3 8B', 'same', 'all 29/38 → 35/38; known-goal 28/36 → 33/36', 'calls 154 → 83; mean task s 5.32 → 3.18', GM,
  ['| ministral | 29/38 → 35/38 | 28/36 → 33/36 | 154 → 83 | 5.32 → 3.18 |']),
 ('', '', 'Granite 3.3 8B', 'same', 'all 1/38 → 0/38; known-goal 0/36 → 0/36', 'calls 38 → 38', GM, ['| granite | 1/38 → 0/38 | 0/36 → 0/36 | 38 → 38 |']),
 ('', '', 'Llama 3.1 8B', 'same', 'all 0/38 → 1/38; known-goal 0/36 → 1/36', 'calls 203 → 185', GM, ['| llama | 0/38 → 1/38 | 0/36 → 1/36 | 203 → 185 |']),
 ('F1 step 0 (2026-11-20)', 'trace classification, no runs', 'Qwen', '116 trials scanned (M4 40 + G1 76)', '12 length stops: 8 class A, 4 class C', '—', F0,
  ['| **Total** | 116 | **12** |', '| **8** (all 5 M4 + 3 G1) |', '| **4** (all G1, first call) |']),
 ('F1 Stage 1b held-out (2026-11-21, **laptop**)', 'mock F1 cases, base vs new catalogue wording; verdict **NOT ADOPTED**', 'Qwen3.5 9B', '24 known-goal pairs (60 trials/backend)', 'known-goal net 0 (15 both, 2 new-only, 2 base-only; P-a needs net ≥ 3); inspection-first 4 → 0 (diagnostic); ambiguous cases now rated by Levinson (2026-11-22): Qwen 0 of 12 clarified correctly under either wording, so with ambiguous cases net is still 0 (15 both, 2 new-only, 2 base-only, 11 neither; the earlier automated screen had shown +3)', 'length stops 5 → 5; no censoring', W_F1, ['"net": 0', '"both": 15', '"new_only": 2', '"base_only": 2', '"neither": 11', '"holds": false', '"decision": "NOT ADOPTED"']),
 ('', '', 'Sol', '24 known-goal pairs', '24/24 known-goal both wordings, and 6/6 ambiguous rated correct for each wording; net 0', 'no censoring', W_F1, ['"both": 24']),
 ('Parity Phase B acceptance (2026-11-21, **laptop**)', '10 tasks × 2 arms; criteria: recognized ≥ 0.90, schema-valid ≥ 0.90, 0 parse crashes', 'Llama 3.1 8B', '10 trials per arm', '**admitted (adapted, native-schema-v1)**: recognized 1.0 and schema-valid 1.0 in both arms; SDK list-string normalization is assistance (14 of 86 raw calls), reported separately', '—', W_LLA, ['"model_pass": true', '"schema_valid_rate": 1.0']),
 ('', '', 'Llama (assistance)', '86 raw tool calls', '14 calls had string-encoded list/object arguments before SDK normalization', '—', W_LLS, ['"raw_tool_calls": 86', '"calls_with_string_encoded_list_or_object": 14']),
 ('', '', 'Granite 3.3 8B', '10 trials per arm', '**not adaptable under parity rules**: schema-valid 0.791 (macro) / 0.809 (primitives), below 0.90; arguments double-wrapped, a fix would need argument repair', '—', W_GRA, ['"model_pass": false', '"schema_valid_rate": 0.7906976744186046', '"schema_valid_rate": 0.8085106382978723', '"tool_rejected_transport": 9']),
 ('Gazebo D2 held-out (2026-11-21/22, **laptop**)', 'fresh Gazebo cases, 160/160 trials, no censoring; 16 ambiguous cases rated by Levinson 2026-11-22 (Sol 4/4 correct, Qwen, Ministral, Llama 0/4 each; macro and primitives equal)', 'Sol', '18 known-goal per arm', 'primitives 18/18 → macro 18/18; macro not worse on passes.', 'calls (all attempts) 70 → 39; matched-pair call reduction 46%', W_D2, ['| sol | primitives | 18/18 | 18/18 | 0 | 70 | 41 | 18 | 0.4559 |', '| sol | macro | 18/18 | 18/18 | 0 | 39 | 41 | 18 | 0.4559 |']),
 ('', '', 'Qwen3.5 9B', '18 known-goal per arm', 'primitives 12/18 → macro 13/18; macro not worse on passes. Native-ops prediction D-P2: **against**. D-P4 (Qwen inspection-first) is now final: **Support**, 14 of 15 failures inspection-first (was 10 of 11 preliminary).', 'calls (all attempts) 91 → 50; matched-pair call reduction 48%', W_D2, ['| qwen | primitives | 12/18 | 12/18 | 0 | 91 | 50 | 11 | 0.4783 |', '| qwen | macro | 13/18 | 13/18 | 0 | 50 | 49 | 11 | 0.4783 |', "D-P4 (Qwen inspection-first): {'failed': 15, 'inspection_first': 14"]),
 ('', '', 'Ministral 3 8B', '18 known-goal per arm', 'primitives 16/18 → macro 15/18; macro not worse on passes.', 'calls (all attempts) 81 → 50; matched-pair call reduction 46%', W_D2, ['| ministral | primitives | 16/18 | 16/18 | 0 | 81 | 39 | 14 | 0.459 |', '| ministral | macro | 15/18 | 15/18 | 0 | 50 | 46 | 14 | 0.459 |']),
 ('', '', 'Llama 3.1 8B', '18 known-goal per arm', 'primitives 8/18 → macro 11/18; macro not worse on passes.', 'calls (all attempts) 89 → 56; matched-pair call reduction 33%', W_D2, ['| llama | primitives | 8/18 | 8/18 | 0 | 89 | 51 | 8 | 0.3333 |', '| llama | macro | 11/18 | 11/18 | 0 | 56 | 55 | 8 | 0.3333 |']),
 ('Phase C Llama rerun (2026-11-21/22, **laptop**, "adapted-integration rerun")', '76 G1 held-out cases (38 per arm), native-schema-v1; not a lab-G1 replacement', 'Llama 3.1 8B', '76 retained, 0 censored, 4 ambiguous rated by Levinson (all NO/NO = FAIL, same as the automated result)', "overall 43 PASS / 33 FAIL; **primitives 23/38 → macro 20/38** (per-arm counts taken from the file's 76 outcome rows; opposite direction to D2, where Llama went 8 → 11)", 'calls 164 → 118', W_PCS, ['"PASS": 43', '"FAIL": 33', '"calls": 164', '"calls": 118', '"retained": 38', '"final_correctness_ready": true', '"semantic_judgments_pending": []']),
]

problems = []
cache = {}
for row in ROWS:
    src = row[6]
    text = cache.setdefault(src, (repo / src).read_text(encoding='utf-8', errors='replace'))
    for check in row[7]:
        if check not in text:
            problems.append((src, check))
if problems:
    for p in problems:
        print('MISSING', p)
    sys.exit(1)

lines = ['## Results at a glance (all studies)', '',
 'Added 2026-11-21. One row per study and backend. **P → M** is model-managed primitives → bounded macro',
 'within the same backend. Correctness and costs are **as reported in the linked source**. Every figure',
 'in this table was checked mechanically against that file when the table was built (each row has',
 'literal source strings that must match). Denominators differ between studies, and settings, cases',
 'and hardware differ too. **Do not pool rows or compare across studies**; see the claims ledger below and §12.',
 'F1 Stage 0 (2026-11-21) is design only, with no trials, so it has no row. The weekend rows at the end (F1 Stage 1b, parity Phase B, D2, Phase C) were added 2026-11-22.', '',
 '| Study (date) | Setting | Backend | Denominator | Correctness | Cost | Source |',
 '|---|---|---|---|---|---|---|']
for study, setting, backend, den, corr, cost, src, _ in ROWS:
    name = Path(src).name
    lines.append(f'| {study} | {setting} | {backend} | {den} | {corr} | {cost} | [{name}]({src}) |')
lines += ['', 'Weekend rows (2026-11-21/22) were run on the **laptop stratum** (RTX 4050 6 GB; Qwen only 17/33 layers on GPU) with G1 digests and settings; never compare them with lab rows. '
  'Timing is descriptive only and not reported here. Ambiguous cases were rated by Levinson (teammate) on 2026-11-22; eligibility is self-attested from forwarded declaration text and AI assistance was denied (self-reported), so this is not independent validation. The three review kits were regenerated after their first keys were pushed publicly (incident 2026-11-22, no ratings existed). '
  'Llama pointed in opposite directions (D2 macro better, Phase C primitives better): report both, do not pool them.']
lines += ['', f'Source checks: {sum(len(r[7]) for r in ROWS)} literal strings across {len(ROWS)} rows, all found.', '']
out.write_text('\n'.join(lines), encoding='utf-8', newline='\n')
print('rows', len(ROWS), 'checks', sum(len(r[7]) for r in ROWS), 'all found')
