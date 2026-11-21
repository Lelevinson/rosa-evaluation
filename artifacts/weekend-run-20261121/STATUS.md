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
- 2026-11-21T07:51Z [A] F1 G1 + dry runs committed and pushed (member/martin-f1 c6a37bd; verify_freeze PASS). Qwen load-only check FAILED twice on the default CUDA backend: 17/33 layers placed on GPU, then llama-server crashed 'CUDA error: shared object initialization failed' (cuda_v13, ggml_cuda_kernel_can_use_pdl, exit 0xc0000409). Same binary loaded Qwen 17/33 on 2026-11-12 with cuda_v13. No tokens generated. Plan: after the Llama pull finishes, restart the parity server with OLLAMA_LLM_LIBRARY=cuda_v12 (lab driver 570/CUDA 12.8 could only run v12 libraries; inference H) and retry. Model/settings unchanged.
- 2026-11-21T08:05Z [A] CHECKPOINT before owner's VS Code restart. Disk free C: 14.8 GB (only drive; all outputs on C:).
  DONE: F1 G1 PASS + D14 dry runs 36/36 and 60/60 + runner/analysis (G3), pushed member/martin-f1 c6a37bd. Gazebo smoke PASS. Qwen (56671c2a) and Ministral (1922accd) in the parity store, digests MATCH G1. Phase B adapter = native-schema-v1 (rosa-research 8713f9b) classified in PHASE_B_ITERATION_LOG.md (Granite sentence = IBM text, SHA 7e12d9b5 match → transport; Llama sentence = its own template text → transport; FLAGGED: non-vendor header line, separate system-message placement, stream:false). Acceptance runner tools/parity/acceptance_run.py written (not yet run).
  BLOCKED 1 (GPU): every model load crashes 'CUDA error: shared object initialization failed' (exit 0xc0000409), on cuda_v13 (2x) and cuda_v12 (1x). Same binary loaded Qwen 17/33 on 2026-11-12. Zero tokens generated. Likely a GPU/driver state problem; a Windows reboot is the first thing to try. No inference possible until fixed → F1 Stage 1a, Phase B, C, D1 all waiting.
  BLOCKED 2 (download): Granite and Llama pulls fail: 'connection aborted by the software in your host machine' on every part; traffic leaves via the GlobalProtect VPN address 140.138.83.224. Partial files kept (resumable). Suggest: disconnect the VPN (lab is down anyway), then I retry.
  NEXT (A): after restart → load check Qwen; if OK start F1 Stage 1a (pre-authorized); retry pulls; acceptance tests Granite, Llama, Qwen, Ministral.
