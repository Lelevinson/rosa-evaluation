# B1 → A2 handoff (session B to session A), 2026-11-21

B1 is complete. Zero model calls were made by session B.

Read, in this order:
1. [PARITY_AUDIT.md](PARITY_AUDIT.md): gaps and transport fixes. Llama **L1/PA-2** (derived tag from the same
   weights blob `667b0c19…`, function list kept in the first user message on every request). Granite
   **G1/PA-1** (see the open point below). Ministral and Qwen: no gap.
2. [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md): **frozen** tasks, run order and pass criteria.
3. [LAPTOP_TARGET_CONFIG.md](LAPTOP_TARGET_CONFIG.md): exact G1 tags, digests and serving settings.

Files for the runner (branch `member/martin-parity`, read them from that branch; do not edit):
- `artifacts/parity-integration-20261121/tasks/scratch.json` (12) and `acceptance.json` (10), hashes in
  `tasks/SHA256SUMS.txt`. Check the hashes before each run.
- `tools/parity/acceptance_score.py <trials_dir> <out.json> --cases <acceptance.json>`: the frozen scorer.
  Its calibration on frozen G1 records is in `calibration/` (Qwen/Ministral PASS, Granite/Llama FAIL).

Where to write (session A owns these on `member/martin-parity`, new files only):
- `PHASE_B_ITERATION_LOG.md` (every adapter iteration: diff, SHA-256, scratch results, time used);
- `tools/parity/adapters/` (adapter code), `phase-b-runs/<model>/` (raw trials, acceptance result JSON).

Session B will not edit those paths. Session B keeps editing only its own design files
(`ACCEPTANCE_CRITERIA.md` is frozen; new owner amendments go in new dated files).

**Open owner point:** PA-1 versus the weekend rule "no per-model instructions". Session B has asked Martin.
Llama, Qwen and Ministral do not depend on it.
