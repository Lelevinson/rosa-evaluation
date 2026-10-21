# Stage 4 results and evidence

The planned simplified campaign finished all **160 live attempts**. Neither
backend met the batching retention screen. This closes the agreed experiment
and analysis with a documented audit exception; it is not a robot-readiness pass.

- [Detailed report for ChatGPT](artifacts/stage4-batching-completion-20261021/FINAL_REPORT_FOR_CHATGPT.md)
- [Six-stage roadmap](docs/PROJECT_ROADMAP_SIX_STAGES.md)
- [Complete evidence ZIP](artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.zip) and [SHA-256](artifacts/ROSA_STAGE4_COMPLETE_EVIDENCE_2026-10-21.sha256)
- [Offline review and reproduction guide](docs/STAGE4_EVIDENCE_GUIDE.md)

| Result | Hosted gpt-6.1-sol | Local Qwen3.5 9B |
| --- | ---: | ---: |
| Reliability strict passes, all four arms | 42/48 | 8/48 |
| Parameter strict passes, model-selected / batching | 16/16 / 16/16 | 0/16 / 0/16 |
| Parameter native commands, model-selected / batching | 48 / 48 | 66 / 54 |
| Model requests across both tracks | 429 | 576 |

Hosted used the same native/model work in both parameter arms. Its observed
candidate total wall time was higher; this small screen does not establish a
causal slowdown. Qwen's lower candidate native work occurred in failed tasks:
28 report-schema aborts and four reports with noncanonical node keys. No
successful matched Qwen pairs exist, so completed-task benefit is unestimable.
Valid manifests when supplied are different from valid final reports.

The frozen audit passed **152/160** trials and failed eight recovery-stop traces.
Every state check passed; a separate [reconciliation](artifacts/stage4-batching-completion-20261021/audit-reconciliation.json)
accounts for those eight using the raw requests, callbacks, world calls and
orchestrator reports. The original FAILED supervisor and missing tool spans are
preserved. Full audit acceptance was not met. No score was changed or trial rerun.

Baseline v1 remains byte-for-byte preserved in the historical evidence archive.
The [original-JTVR policy study](artifacts/stage4-policy-20261021/REPORT_FOR_CHATGPT.md)
also remains frozen: 1,152 policy episodes and 15 real ROS smoke cases, with no
additional cost benefit over batching on the 96 primary fixtures. Full JTVR stays
paused; this live comparison shares the batching helper between both arms and
does not measure helper speedup over untouched upstream ROSA.

Next: a separately tested report-interface and recovery-tracing repair, followed
by one specified Gazebo arm skill. Episodic memory has not started. The exact
modified research dependency is included as a source snapshot; this evaluation
commit does not publish a separate research-repository commit.
