# Gazebo D runbook for session A (written by session B, 2026-11-21)

Follow D0_PROTOCOL.md (approved, frozen), D0_APPROVAL_2026-11-21.md and D0_AMENDMENT_01_2026-11-21.md.
Wrapper and analysis are frozen in [WRAPPER_FREEZE_2026-11-21.json](WRAPPER_FREEZE_2026-11-21.json). Do not edit
any file listed there. Session B made zero model calls and started no Gazebo.

## 0. Before D1

1. Phase B has decided Granite and Llama (admitted or "not adaptable"). D1 never starts before that.
2. Work in **your own worktree** of the frozen commit, e.g.
   `git -C rosa-evaluation worktree add -b member/martin-gazebo-runs ../wt-a-gazebo <frozen commit>`
   (or any branch you own). Runs write into `artifacts/gazebo-d-20261121/{runs,jobs}/` of that worktree only.
   Run outputs never go into session B's `wt-b-gazebo`.
3. Keep the main checkouts `rosa-evaluation` and `rosa-research` with their current bytes. M4's `verify()`
   reads its 62 frozen files from `<parent>/rosa-evaluation/...` and `<parent>/rosa-research/...` (checked
   PASS from a worktree on 2026-11-21). Switching or editing them can stop every trial.
4. Check AC power, sleep off and Windows Update paused. The detached job survives a VS Code restart,
   but **not** sleep, shutdown, reboot or `wsl --shutdown`.
5. Write `artifacts/gazebo-d-20261121/models.json` in your worktree (admitted models only):

```json
[
 {"name": "sol", "backend": "siwc", "model": "gpt-6.1-sol"},
 {"name": "qwen", "backend": "ollama", "tag": "qwen3.5:9b", "digest": "<full G1 digest>", "endpoint": "http://<wsl-reachable addr>:<port>", "adapter": null},
 {"name": "ministral", "backend": "ollama", "tag": "ministral-3:8b-instruct-2512-q4_K_M", "digest": "<full>", "endpoint": "…", "adapter": null},
 {"name": "granite", "backend": "ollama", "tag": "granite3.3:8b", "digest": "<full>", "endpoint": "…",
  "adapter": {"path": "<frozen Phase B adapter .py>", "sha256": "<Phase B frozen hash>", "label": "adapted (transport only: vendor-documented IBM tool sentence)"}},
 {"name": "llama", "backend": "ollama", "tag": "<derived PA-2 tag>", "digest": "<derived tag digest>", "endpoint": "…",
  "adapter": {"path": "…", "sha256": "…", "label": "adapted (transport only)"}}
]
```

   Names must be from `sol, qwen, ministral, granite, llama`. The adapter module must define
   `make_model(kwargs) -> chat model`, where kwargs are the wrapper's `OLLAMA_KWARGS` plus `model` and
   `base_url`. A Llama tag-only fix can use `"adapter": null` with the derived tag.
   Check the plan: `python -B -m experiments.gazebo_d.runner plan --stage dev --models artifacts/gazebo-d-20261121/models.json`.

## 1. D1: controls, freeze, dev

All long steps go through the **detached launcher** (WMI → `wsl.exe` → `job.sh`), from any PowerShell:

```powershell
$wt = 'C:\Proj\robotics\introtorobotics\wt-a-gazebo'
powershell -NoProfile -ExecutionPolicy Bypass -File "$wt\experiments\gazebo_d\start_detached.ps1" -RepoRoot $wt -Stage controls
```

1. **Controls** (52 zero-model trials, ~15 min). Gate: `runs/controls/status.json` has `status: COMPLETE` and all
   52 `primary_pass: true`. Any failure: stop and report.
2. **Freeze dev** (short, foreground is fine, in WSL from the worktree root):
   `python -B -m experiments.gazebo_d.runner freeze --stage dev --models artifacts/gazebo-d-20261121/models.json`
3. **Dev run**: `start_detached.ps1 -RepoRoot $wt -Stage dev -Models artifacts/gazebo-d-20261121/models.json`.
   The job runs the dev trials, then `analysis.py analyze dev`, then `analysis.py d1-gate`. The result is
   `runs/dev/D1_GATE.json` with `pass` and `reasons`.
4. If `D1_GATE.json` says pass: **freeze held-out** with the same models.json
   (`runner freeze --stage heldout --models …`). If it fails, stop and report. Do not change anything to get past it.

## 2. D2: held-out

`start_detached.ps1 -RepoRoot $wt -Stage heldout -Models artifacts/gazebo-d-20261121/models.json`.
The runner refuses held-out without a passing D1 gate. It stops starting rows at Mon 2026-11-23 06:00 Taipei.
The frozen analysis then runs automatically (`runs/heldout/analysis/ANALYSIS.md`). Ambiguous transcripts stay
PRELIMINARY until a human rates them. Package the kit from the 4 × models ambiguous trials.

## 3. Monitoring and interruptions

- Progress: `jobs/<stage>-<UTC>/job.json` (state RUNNING / ANALYZING / FINISHED / INTERRUPTED / EXITED_EARLY_n),
  `jobs/<stage>-<UTC>/runner.log` (one JSON line per trial), `runs/<stage>/status.json` (ledgers, reset checks,
  model switches, stopped models). Launch history: `jobs/LAUNCHES.jsonl`. Refused duplicates: `jobs/REFUSED.log`.
- A second launch of a running stage is refused. **Never edit job.sh or any frozen file while a job runs.**
- After an interruption: relaunch the same command. Rows with `result.json` are kept. A row whose folder exists
  without `result.json` is INTERRUPTED: it is recorded in `status.json` and **never rerun**. Only unstarted rows run.
  First check the frozen hashes (the runner does this) and that the interruption was external.
- Stops on: frozen-input change, reset-check failure, trace/Phoenix audit failure, control failure, Sol
  authorization loss. A model reaching its request ceiling stops only that model.

## 4. Per-stage numbers (full set / 3 models)

Dev: 60 / 36 trials, held-out: 200 / 120. Request cap per model = 8 × its trials + 3 (dev 99, held-out 323).
8 h per model of in-task time per stage. Estimates in D0 §10.
