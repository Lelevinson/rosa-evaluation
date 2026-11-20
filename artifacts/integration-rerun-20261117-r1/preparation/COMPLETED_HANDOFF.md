# Completed native-schema repair and reruns — 2026-11-17

The latest user instruction (proceed with integration repair, then immediately
80 reruns) is complete. Do not restart these campaigns or change their freeze.

- Production opt-in profile: `rosa-research/src/rosa_backends/tool_contract_ollama.py`.
  Original backend and all historical runtime files remain unchanged. Native
  syntax guidance plus current system-message schemas, explicit HTTP stream=false;
  no skill routing, argument aliases, weakened validators or automatic write replay.
- Initial stopped attempt: `integration-rerun-20261117`, zero model calls, float
  readiness violated the existing bool contract. Archive retained locally as
  `evidence/INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip` (16 content hashes).
- Revision1 fixture-only amendment preceded live outcomes. Seven unit checks,
  12 deterministic mock controls, 24 live mock validation attempts, 20 deterministic
  Gazebo controls, then160 live Gazebo attempts completed. Local/persisted Phoenix
  audits passed for all216 completed attempts. Original69/new75 source hashes matched.
- Validation: Llama9/12,51 requests; Granite6/12,56 requests. Functional gate
  passed healthy inspection in both modes, not all-case reliability. Validation
  ineffective-write checker allowed truthful failure without dispatch; report
  explicitly limits that evidence. Main Gazebo fault-exercise requirements unchanged.
- Llama80/80: known-goal P21/36, M28/36; calls190/113, task means2.3665/2.1626 s;
  native99/112; accepted wrong-goal SUCCESS7/4. All partial-command cases failed.
- Granite80/80: P5/36,M9/36; calls210/193, task means6.8128/5.1796 s;
  native63/119; accepted wrong-goal SUCCESS9/12. Current configuration poor.
- Eight ambiguity attempts/model pending actual human review (16 total), never
  promote legacy regex results to completed adjudication. Known denominator36/mode;
  cost denominator40/mode. Four repeats of familiar M4 cases, not G1 held-out.
- Actual main requests:303 Llama,403 Granite; plus107 validation =813 total;
  input1,641,312/output53,559 tokens. Zero infrastructure retries. Caps96 validation
  and643 robot requests/model, original per-task limits maintained.
- Main raw/API names and call counts preserved through parsing. SDK normalized46
  Llama list arguments; this is existing software assistance, not raw-model accuracy.
  Granite normalization0; one length stop, Llama none. Actual HTTP requests captured;
  fully rendered/tokenized Ollama prompt not captured. LangChain cache=false does
  not prove Ollama prefix/KV reuse disabled. Cached-token field not recorded.
- Full pipeline56.70 min; model campaigns20.24/25.18 min. Task means exclude resets,
  simulator startup and persisted audits. Do not confuse task and campaign time.
- Combined profile changes do not isolate individual causes. Original condition
  sentence remains coupled to primitive/macro execution. Different profiles from
  Qwen/Ministral; no new hosted Sol run or stock-ROSA claim. G1 gates unchanged.

Local complete report: `evidence/INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md`
(49,808 bytes). Independent analysis: `evidence/INDEPENDENT_RERUN_ANALYSIS.json`.
Raw ZIP: `evidence/NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip`,12,978,238 bytes,
2643 content hashes, SHA256
`5b98ca99fadab0d2bd6c6a3abb0f9b7baab38bab7e9ce1bdd2e79da97dbdf685`.

Share ZIP in `delivery/ROSA_NATIVE_SCHEMA_RERUN_REPORT_AND_EVIDENCE_2026-11-17.zip`,
30,152,616 bytes,17 content hashes, SHA256
`c3249d584739d8697fce9c232545c911c657bb1d39a5a4054f6d0769693d81e3`.
Includes old source archive, diagnostic reconciliation, Qwen repeat, new raw,
retained preparation failure, report, JSON, module, analysis and master context.

Living master updated and snapshotted in evidence. Previous master bytes retained
in preparation. Report, master and share ZIP deployed under
`/media/naeem/d1/marvel proj/integration-rerun-20261117-r1/` on lab-rosa. Root
`PROJECT_MASTER_CONTEXT_2026-11-17.md` and `REPORTS_READY.md` updated with previous
bytes retained under reports. Lab clone received byte-identical opt-in module;
frozen baseline untouched. Models unloaded. Lab/local package, report and master
hashes matched; receipt `delivery/LAB_BACKUP_VERIFICATION.json`.

No Git commit, push, public upload or new study was performed. No default backend
switched. Recommendations: retain Llama as an opt-in experimental candidate;
Granite is not a suitable replacement on this evidence. Keep Qwen reference and
all historical results. Do not silently tune or retry known failures.
