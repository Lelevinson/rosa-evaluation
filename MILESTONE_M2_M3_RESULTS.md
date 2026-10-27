# M2/M3 completion record

Branch: member/martin. M1 checkpoint commits: research cc4a170, evaluation 0c95c9b.
Research completion: cf722cf (OAuth rotation fix), c0c61a0 (M2 capability/M3 demo).

- M2: 10/10 deterministic Gazebo checks, including actual inactive controller,
  explicit missing-source faults and blocked inspection writes.
- M3: deterministic reference 3/3; Sol 3/3 in five calls; Qwen 2/3 in seven calls.
  Qwen inspected an ambiguous request instead of asking for clarification. The
  evidence report was truthful, but the task decision was wrong. No replacement.
- All 19 trace audits passed, with 331 exact persisted Phoenix spans.
- Final research tests: 188 passed, 42 skipped; two evaluation bound tests passed.
- One actual protected OAuth renewal across processes passed after a focused
  Windows storage fix. No inference requests were made during auth checks.

[Combined report for review](docs/M2_M3_COMBINED_REPORT_2026-10-27.md)

[Evidence ZIP](artifacts/ROSA_MACRO_M2_M3_ENGINEERING_AND_LIVE_DEMO_2026-10-27.zip)
and [SHA256](artifacts/ROSA_MACRO_M2_M3_ENGINEERING_AND_LIVE_DEMO_2026-10-27.sha256).
All 382 manifest file hashes matched archived bytes; ZIP integrity and credential
pattern scanning passed. The raw evidence directory is also committed for inspection.

M2 accepted; M3 demo/attempts complete with the documented Qwen limitation.
No comparative improvement claim or large experiment is authorized by these
results. M4 is not started. Historical evidence remains unchanged. Commits are
local; no remote push was performed.
