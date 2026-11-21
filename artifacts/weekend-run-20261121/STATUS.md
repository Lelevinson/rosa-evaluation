# Weekend run 2026-11-21 → 2026-11-23 — shared status (append-only)

Canonical live copy: `C:\Proj\robotics\introtorobotics\weekend-run-20261121\STATUS.md` (outside every
worktree, so both sessions append to one file). At each gate the owning session copies a snapshot to
`artifacts/weekend-run-20261121/STATUS.md` on its own branch and pushes.

Rules: append only; one entry per event; UTC timestamp + Taipei time; session tag [A] runner / [B] designer.
Only session A starts model processes. GPU queue owner: A.

Worktrees: main checkout `rosa-evaluation/` = member/martin-parity (left for session B);
session A = `wt-a-f1/` (member/martin-f1). Gazebo branch `member/martin-gazebo`: to be created by B from the freeze tag.

Inference server (D16): pinned Ollama 0.40.6 (`.local/ollama-0.40.6/ollama.exe`, the M4/timing binary, used
read-only) as a new process: `http://172.31.0.1:11440`, models `.local/parity-ollama-models`, state
`.local/parity-ollama-state`. Start: `.local/start-parity-ollama.ps1`. M4 server (11436) and store untouched.

---
- 2026-11-21T07:45Z (Sat 15:45 TPE) [A] A0 started. Lab unavailable (D16). Laptop on AC, 79% battery, power scheme Balanced. Parity server 0.40.6 up on :11440. Qwen in new store via hard links; manifest set to the G1 platform manifest → digest 56671c2a… size 6550825550 = G1 MATCH. Pulling Ministral, Granite, Llama (~15.9 GB). Next: F1 gate G1 (CPU-only) while downloads run.
- 2026-11-21T07:41Z [A] F1 gate G1 (laptop, lab unavailable): controls C1 48/48, C2 8/8, 26/26 frozen inputs, 0 model requests → PASS. Stage 1 runner + analysis written (G3); scripted dry run dev 36/36 pass, 0 model requests; held-out dry run running. Gazebo smoke (no model, ROS_DOMAIN_ID 231): ready 8.4 s, controllers active, home pose, clean shutdown → PASS. Downloads: Ministral done, Granite done, Llama in progress. Note: G1 stage-4 freeze lists artifacts/macro-m5-20261027/status.json, edited by commit 37a7e19 (2026-11-20, pre-freeze doc correction); recorded, not code, not a G1 input.
