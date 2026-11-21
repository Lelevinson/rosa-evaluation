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
