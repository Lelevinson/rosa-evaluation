# Reliability v1: interface repairs and a bounded Gazebo skill

Completed 2026-10-22 as a separate post-Stage 4 engineering milestone. Both
backends use the actual ROSA executor and the same four bounded tools.

- [Consolidated report for ChatGPT, including every rejected call](artifacts/RELIABILITY_V1_REPORT_FOR_CHATGPT_2026-10-22.md)
- [Full metrics](artifacts/reliability-v1-20261022/analysis.json)
- [Independent persisted Phoenix audit](artifacts/reliability-v1-20261022/phoenix-audit.json)
- [Complete review ZIP](artifacts/ROSA_RELIABILITY_V1_COMPLETE_REVIEW_2026-10-22.zip) and [SHA-256](artifacts/ROSA_RELIABILITY_V1_COMPLETE_REVIEW_2026-10-22.sha256)
- [Unchanged primary evidence ZIP](artifacts/reliability-v1-20261022-evidence.zip)
- [Prospective protocol](docs/RELIABILITY_V1_PROTOCOL_2026-10-22.md)

| Validation | Result |
| --- | --- |
| Runtime tests | 8 passed |
| ROSA integration tests | 3 passed, including controlled-stop span closure |
| Scripted fixture/arm controls | 16 passed |
| Hosted backend | 32/32 mock and 4/4 Gazebo task/report checks |
| Local Qwen | 32/32 mock and 4/4 Gazebo task/report checks |
| Independent Phoenix trace equality | 72/72 |
| Matched deterministic controller | 2/2 Gazebo cases |

The native command range is [-0.6, 0.6] radians on a custom one-joint arm fixture.
Real physics and ROS joint-state observations are used; this is not a complete
manipulator, perception/grasping task or hardware validation. Fault cases count
correct failure/unknown handling, not achieved physical goals.

The repaired reference already passed every task. Automatic checks did not
increase completion. Local call-count reductions are exploratory and partly
depend on the dedicated-verifier API rule; they do not establish a general
efficiency or novelty claim. See the report for all costs and caveats.

Qwen made nine rejected calls in nine trials, including **three write attempts
despite unavailable observations**. The shared guard blocked all three before
dispatch; all nine trials recovered. The 36/36 result is for the combined system,
not error-free model behavior. Hosted had no rejected calls. The consolidated
review makes this explicit while preserving the sealed primary report.

From the workspace root in Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\rosa-evaluation\scripts\reliable-gazebo.ps1 -Backend deterministic
```

Change `deterministic` to `ollama` or `siwc` for either LLM. All use the same
skill. `siwc` requires fresh browser consent at the printed local URL. Use
`-Configuration A` for the strong reference or `-Configuration D` for combined
feedback/automatic verification, and `-Target 0.2` to select a bounded angle.
The default is the simpler A configuration. Evidence is saved under
`artifacts/reliability-demos/`. The demo is headless and cleans up its simulator.

Runtime code belongs in rosa-research/src/rosa_reliability; evaluation and raw
records live here. Source snapshots are included. No new research/evaluation
commit or push is asserted by this results entry.
