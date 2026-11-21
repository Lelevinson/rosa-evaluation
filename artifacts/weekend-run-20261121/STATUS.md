# Weekend run 2026-11-21 → 2026-11-23 — shared status (append-only)

Live copy: `C:\Proj\robotics\introtorobotics\weekend-status\STATUS.md` (outside every git worktree,
so neither session's working tree is touched by the other's appends).
At each gate push, the pushing session copies this whole file to
`artifacts/weekend-run-20261121/STATUS.md` on its own branch (a snapshot; never edited there).
Rules: append only, newest at the bottom, Taipei time, one entry per gate/problem. Never rewrite old entries.

Sessions: **A = runner** (worktree `wt-a-f1`, owns GPU queue, F1 branch). **B = designer** (main checkout
`rosa-evaluation` on `member/martin-parity`; worktree `wt-b-gazebo` on `member/martin-gazebo`). Zero model calls in B.

---

## 2026-11-21 15:24 — B — start
- Phase: B1 (parity Phase A audit + scratch/acceptance tasks).
- Found: Phase A audit already committed earlier today on `member/martin-parity` (bfb1d03, 1d75323, 0df57ec):
  PARITY_AUDIT.md, REDIAGNOSIS_G1.json, LAPTOP_TARGET_CONFIG.md. Owner decisions PA-1 (Granite IBM sentence,
  owner exception) and PA-2 (Llama template from Meta public code) recorded there.
- Created branch `member/martin-gazebo` from `freeze-2026-11-21` in worktree `wt-b-gazebo`.
- verify_freeze: PASS on member/martin-parity (main checkout) and member/martin-gazebo.
- Remaining B1: 12 scratch + 10 acceptance tasks, leakage check, frozen acceptance criteria, handoff note.
- ETA B1 handoff: ~18:00.
- Open question for Martin: PA-1 is a per-model instruction. The weekend task lists that as NOT ALLOWED.
  Does PA-1 still stand? (Affects A2 Granite only.)

## 2026-11-21 16:10 — B — GATE B1: PASS (handed off to A)
- Commit 8f50101 on `member/martin-parity`. Zero model calls.
- 12 scratch + 10 acceptance tasks; leakage check with the F1 checker: 22/22 OK (one scratch draft reworded first).
- Acceptance criteria, run order and scorer FROZEN: `artifacts/parity-integration-20261121/ACCEPTANCE_CRITERIA.md`.
- Scorer calibration on frozen G1 records: Qwen PASS, Ministral PASS, Granite FAIL (0 recognized calls), Llama FAIL (44% schema-valid).
- Handoff: `artifacts/parity-integration-20261121/PHASE_B_HANDOFF.md`. A2 may start (after A0).
- Still open: PA-1 (Granite) vs "no per-model instructions". Llama/Qwen/Ministral not affected.
- verify_freeze PASS. Next: B2 Gazebo D0 design, ETA 21:00, then STOP for Martin's approval.

## 2026-11-21 15:36 — B — correction
- The entry above headed "16:10" was mistimed. Gate B1 actually passed at about 15:30 (commit 8f50101). No other content changes.

## 2026-11-21 15:43 — B — GATE B2: D0 written, STOPPED for Martin's approval
- `artifacts/gazebo-d-20261121/D0_PROTOCOL.md` on `member/martin-gazebo`. Zero model calls, zero Gazebo runs.
- 26 fresh cases (6 dev, 20 held-out = 10 M4 families x 2); leakage 26/26 OK (5 drafts reworded first).
- Frozen M4 harness reused unchanged (62/62 files match). Wrapper not yet written (B3, frozen before D1).
- Estimate: held-out typical 3.4 h (3 models) to 6.6 h (5 models); fits Sun 12:00-Mon 06:00. Only the
  all-timeout bound for 5 models (18.3 h) is over; fallback 16-case option offered.
- A4 (D1) must NOT start until Martin approves D0. Next for B: B3 (wrapper, analysis + synthetic tests, report addenda).
- verify_freeze PASS.

## 2026-11-21 15:52 — B — owner decisions received (for session A)
- **D0 APPROVED, all 20 held-out cases** (record: gazebo branch `artifacts/gazebo-d-20261121/D0_APPROVAL_2026-11-21.md`).
  D1 (A4) may start once Phase B decides Granite/Llama admission. Wrapper + analysis still to be frozen by B (B3).
- **PA-1 stands, with conditions** (record: parity branch `artifacts/parity-integration-20261121/PA1_CONDITIONS_2026-11-21.md`).
  Only the verified verbatim IBM text (HF commit 51dd4bc2, text SHA-256 7e12d9b5…624e), same in both arms,
  URL logged in PHASE_B_ITERATION_LOG.md. New label: "adapted (vendor-documented tool prompt, owner exception PA-1)".
  Anything else -> drop PA-1 -> Granite "not adaptable under parity rules".
- B now on B3. ETA: wrapper + analysis frozen ~20:00; report addenda ~21:30.

## 2026-11-21 16:05 — B — owner updates applied + branch coordination proposal (for A)
- **PA-1 is now TRANSPORT, no owner exception** (owner). Verified: the sentence is byte-identical in rosa-research
  8713f9b `NATIVE_GUIDANCE['granite3.3']` and IBM's template (SHA-256 7e12d9b5…624e). Only that sentence; the rest of
  native-schema-v1 (schema copy block, forced non-streaming) is NOT allowed. Granite label:
  "adapted (transport only: vendor-documented IBM tool sentence)". Record: parity `PA1_RECLASSIFICATION_2026-11-21.md`.
- **D0 Amendment 01** (gazebo branch): cites the 11-17 lab Gazebo runs (Qwen, Ministral, repaired Llama/Granite on
  known M4 families); D adds fresh cases, Sol, one simultaneous harness. No design change.
- **Branch coordination (proposal, A please confirm here):** `member/martin-parity` is checked out in B's main
  checkout and `member/martin-gazebo` in `wt-b-gazebo`, so A cannot check them out. A commits its run outputs to
  its own branches made from B's frozen commits: `member/martin-parity-runs` (from member/martin-parity) and later
  `member/martin-gazebo-runs` (from the D1-frozen member/martin-gazebo commit). B never touches those.
  B will merge nothing from them without A's note here.

## 2026-11-21 16:05 — B — CHECKPOINT before VS Code restart (clean stop)
- **Done:** B1 (gate PASS), B2 (D0 approved, all 20 cases), owner updates (PA-1 = transport; D0 Amendment 01;
  rosa-research branches member/martin-parity 62ae05a and member/martin-gazebo 9fe6d58 from 8713f9b).
  B3 so far: D analysis `tools/gazebo_d/analysis.py` + 11/11 synthetic tests pass (`tools/gazebo_d/test_analysis.py`).
- **In progress (not frozen):** wrapper `experiments/gazebo_d/runner.py` is written and committed but NOT tested in
  WSL/Gazebo and NOT frozen. D1 must not use it until B freezes it (hashes) and the 52 zero-model controls pass.
- **Next for B:** (1) offline tests of runner pure logic (schedule filter, resume, deadline, ledger, reset check);
  (2) freeze wrapper + analysis; (3) report addenda drafts (F1, parity, Gazebo) with empty tables, citing the 11-17
  lab Gazebo runs; (4) master README entry.
- **Waiting on A:** confirm the run-branch proposal (member/martin-parity-runs / member/martin-gazebo-runs).
- No long job running in session B. Zero model calls by B. verify_freeze PASS on both B branches.
- B note: `member/martin-parity` has a local, unpushed session-A commit f8e7570 (Phase B runner, iteration log).
  B did not push it and did not touch those files; A should push it at its next gate.
  So A is committing on member/martin-parity: fine with B, as long as A only adds its own files (B keeps the
  parity design files unchanged). The run-branch proposal above is then optional.

## 2026-11-21 16:36 — B — CHECKPOINT before Windows reboot (clean stop)
- **Done since last checkpoint:** owner update 5 applied: detached launcher `experiments/gazebo_d/start_detached.ps1`
  (WMI → wsl.exe → `job.sh`; parent WmiPrvSE.exe, survives VS Code restart; NOT sleep/reboot/wsl --shutdown).
  Tested with a stub job: logs on disk, FINISHED state, duplicate launch refused. Runner logic tests 8/8 and
  analysis tests 11/11 pass in the WSL research env; M4 verify() PASS from a worktree.
  Runbook for A: `artifacts/gazebo-d-20261121/RUNBOOK_SESSION_A.md`. Hash record: `WRAPPER_FREEZE_2026-11-21.json`.
- **Not yet done:** wrapper never run against real Gazebo (that is A's 52 controls in D1). Report addenda drafts
  (F1, parity, Gazebo) and master README entry not started.
- **Next for B after reboot:** report addenda drafts with empty tables (cite 11-17 lab Gazebo runs), master README
  entry, rosa-research gate-log update.
- No job running in B. The stub test job finished. Zero model calls by B. Session A commit f8e7570 on parity still unpushed by A.
