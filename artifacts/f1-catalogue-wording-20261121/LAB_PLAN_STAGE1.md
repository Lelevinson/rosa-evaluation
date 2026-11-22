# F1 lab plan: zero-model controls now, Stage 1 readiness later (nothing here has been run)

2026-11-21. On this date the lab was **unreachable** from the laptop: `ssh lab-rosa` timed out on port 22
twice, and ping lost 100%. Everything below is a plan. Per the owner's rule, every test runs on the lab
over SSH. No container, server or model is to be started, stopped or restarted. The other project's
Ollama on `:11435` is never queried or touched; it is only observed through `nvidia-smi` and the process list.

Paths: host `/media/naeem/d1/marvel proj/` is mounted at `/work` in our container
`marvel-g1-extension-20261119`. The research env is `/work/runtime/envs/research/bin/python`. The frozen G1
workspace mirror is `/work/preparation/g1-sol-review-and-lab-replication-20261119/workspace`. It holds
`rosa-evaluation/…/revision-1/` and `rosa-research/src/`.

## 1. Copy the study (new directory only)

```bash
# laptop, from the rosa-evaluation repo root (branch member/martin-f1)
D='/media/naeem/d1/marvel proj/preparation/f1-catalogue-wording-20261121/f1'
ssh lab-rosa "mkdir -p '$D'"     # new directory; refuse if it already exists with content
tar -cf - tools/f1_wording artifacts/f1-catalogue-wording-20261121 | ssh lab-rosa "tar -xf - -C '$D'"
ssh lab-rosa "cd '$D' && find . -type f -exec sha256sum {} + | sort -k2" > lab_copy_sha256.txt   # compare to laptop
```

## 2. Zero-model scripted controls (C1–C3) and the W2 source quote

```bash
ssh lab-rosa 'docker exec -e PYTHONDONTWRITEBYTECODE=1 \
  -w /work/preparation/f1-catalogue-wording-20261121/f1 marvel-g1-extension-20261119 \
  /work/runtime/envs/research/bin/python -I -B tools/f1_wording/controls.py \
  --workspace /work/preparation/g1-sol-review-and-lab-replication-20261119/workspace'
# W2: quote the installed parser that turns a no-tool reply into AgentFinish
ssh lab-rosa 'docker exec marvel-g1-extension-20261119 /work/runtime/envs/research/bin/python -I -c \
  "import inspect, langchain, langchain.agents.output_parsers.tools as t; print(langchain.__version__); \
   print(inspect.getsource(t.parse_ai_message_to_tool_action))"'
```

`controls.py` first re-checks the ~~25~~ 26 frozen-input hashes in `controls/FROZEN_INPUTS.json`, which were
recorded on the laptop with CRLF normalized to LF. It stops on any mismatch. The lab mirror's
`rosa_reliability` must equal `rosa-research` `8713f9b`. Then ~~46~~ 48 cases (18 dev + 30 held-out) × 2 wordings = ~~92~~ 96 scripted macro
trials, about 1 minute of CPU and **zero model requests**. Outputs go to `controls/CONTROL_ROWS.json` and
`controls/CONTROL_SUMMARY.json`, which are copied back and committed with a run report. Expected: all
pass; C1 identical program behaviour in ~~46/46~~ 48/48; C2 no-tool route OK in 8/8 ambiguous (2 dev + 6 held-out).

## 2a. Code/env identity with the laptop Sol environment (D12; zero model)

```bash
ssh lab-rosa 'docker exec -e PYTHONDONTWRITEBYTECODE=1   -w /work/preparation/f1-catalogue-wording-20261121/f1 marvel-g1-extension-20261119   /work/runtime/envs/research/bin/python -I -B tools/f1_wording/env_fingerprint.py   --workspace /work/preparation/g1-sol-review-and-lab-replication-20261119/workspace   --out artifacts/f1-catalogue-wording-20261121/controls/ENV_FINGERPRINT_lab_container.json'
```

Copy the file back and compare it with `controls/ENV_FINGERPRINT_laptop_wsl_2026-11-21.json`. The group
hashes `rosa_reliability`, `g1_frozen_inputs`, `f1_code` and `f1_cases` must be identical, and
`g1_frozen_inputs_match_on_this_host` must be true. Package and `langchain_output_parsers_tools_sha256`
differences are reported (see SOL_ENVIRONMENT_2026-11-21.md).

## 3. Stage 1 readiness check (read-only; run just before Stage 1a, after authorization)

| Check | Command (host unless noted) | Pass condition |
|---|---|---|
| Container | `docker inspect -f '{{.Id}} {{.State.StartedAt}} {{.Config.Image}}' marvel-g1-extension-20261119` | running; ID recorded |
| Our Ollama version | `curl -s 127.0.0.1:11439/api/version` | `0.40.6` |
| Qwen digest | `curl -s 127.0.0.1:11439/api/tags` | `qwen3.5:9b` digest `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90` (G1 `prompt-contract.json`) |
| Serving settings | runner record | `num_ctx` 8192, temperature 0, seed 42, `think` false, per-call `num_predict` ≤ 1024, KV f16, flash attention left at the G1 default (unset/auto) |
| GPU idle / foreign jobs | `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`; `nvidia-smi --query-gpu=memory.used,memory.total --format=csv` | no foreign compute process; record VRAM |
| Other project (observe only) | `pgrep -af 'rosa_exam/ollama' ; docker ps --format '{{.Names}} {{.Status}}'` | recorded; **never queried or touched** |
| Disk | `df -h / /media/naeem/d1` | root was 98% full on 11-20, so all outputs go to `/media/naeem/d1` (386 GB free on 11-20); record both |
| ROS domain | n/a | mock worlds only; no ROS or Gazebo in F1 |

**Exclusive GPU window:** two Ollama servers share the one RTX 4080 SUPER (ours on `:11439`, the
rosa-exam project's on `:11435`, whose queue runners were active for 16+ hours on 11-20). Martin agrees a
window with that project's owner. Before each Qwen block, the GPU must show no foreign compute process. If
one appears during a block, the runner stops **between** trials, never mid-trial. The stop is recorded,
and only unstarted trials may resume, under the G1 resume rules. Sol arms don't use the GPU.

## 4. Telemetry to record during Stage 1 (every 10 s, plus before/after snapshots)

- `nvidia-smi` compute processes (pid, name, VRAM) and total VRAM used/free.
- Our `127.0.0.1:11439/api/ps` (loaded model, size in VRAM, whether fully GPU-resident).
- Container ID/StartedAt, Ollama version and the model digest, in every run directory.
- Presence of foreign GPU processes and of the other project's processes (from the process list only).
- Disk free on `/` and `/media/naeem/d1`, before and after.
- Per trial (from the runner): calls, input/output tokens, finish reasons, task seconds, native operations,
  dispatches, censoring codes.
