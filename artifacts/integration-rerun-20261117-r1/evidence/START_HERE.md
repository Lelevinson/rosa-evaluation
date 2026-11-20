# Native-schema integration reruns — 2026-11-17

Read `INTEGRATION_RERUN_COMPLETE_REPORT_2026-11-17.md` first, then
`INDEPENDENT_RERUN_ANALYSIS.json`. The current master context includes earlier
project milestones and unresolved gates; it is a living record, not a replacement
for frozen evidence.

This package preserves a newly authorized engineering replication: 80 Llama and
80 Granite Gazebo trials, separate fresh validation, and the initial failed
zero-model preparation attempt. It does not reopen G1 held-out testing or revise
M4/M1–M5 scores. Eight ambiguous attempts per model remain pending real human
semantic review.

- `NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip`: new source freeze, protocol,
  tests, checkpoints, controls, traces, Phoenix audit results, physical request
  journals and actual loopback HTTP request/response captures.
- `INITIAL_STOPPED_ZERO_MODEL_ATTEMPT_2026-11-17.zip`: retained fixture-type
  defect, source and failed deterministic control, with zero inference requests.
- `ORIGINAL_LAB_STUDY_AND_SOURCE_2026-11-17.zip`: unchanged original 69-file
  frozen runtime/configuration, lockfiles, model metadata and first four-model
  lab study; required transitive source for replaying the new wrappers.
- `INTEGRATION_RECONCILED_EVIDENCE_2026-11-17.zip`: preceding integration
  diagnosis, including retained instrumentation errors and offline reconciliation.
- `QWEN_LAB_REPEAT_RAW_2026-11-17.zip` and its report: separate Qwen reference
  repeat, not a new matched-profile comparator in this campaign.
- `module/`: exact opt-in reusable profile. The frozen runtime uses its copy
  inside the new raw archive. Original adapters and validators are unchanged.

Every ZIP has a SHA-256 manifest; check each manifest independently, including
nested archives. No model weights, credentials or complete Python environments
are included. Model digests, locked dependency files, launcher/environment
settings and machine provenance are retained. Reproduction requires the declared
Ollama models and a compatible ROS 2 Jazzy/Gazebo UR5e environment. The exact
execution commands and limits are in the raw archive's `source/operator_run.py`
and `source/PROTOCOL.md`; do not run them blindly over an existing output folder.

For the offline analysis, recreate the original evaluation folder structure:
place the original lab archive at
`artifacts/lab-multimodel-20261117/evidence/ROSA_LAB_MULTIMODEL_2026-11-17.zip`,
the new raw archive at
`artifacts/integration-rerun-20261117-r1/evidence/NATIVE_SCHEMA_RERUN_RAW_2026-11-17.zip`,
the analysis scripts in that campaign's `preparation/`, and the shared repeat
analysis at `artifacts/qwen-lab-repeat-20261117/preparation/analyze_repeat.py`.
Run `analyze_rerun.py` and `write_report.py` with Python. They perform zero model
requests and use the archived data only. Do not mistake an analysis rerun for a
new robot trial.

The known-goal denominator is 36 per model/condition; all-attempt cost tables use
40. Match-success tables are selected subsets. Four repetitions of familiar
families are not independent generalization evidence. The old zero scores remain
valid for the old integration, and this combined profile does not isolate the
causal effects of formatting, schema persistence and HTTP streaming separately.
