# Lab container check — 2026-11-20 (read-only)

Raw output: `artifacts/lab-container-check-20261120/lab_check_20261120.txt` (110 lines, run
2026-11-20 16:56 Taipei). Script: `lab_check_20261120.sh` beside it, SHA-256 `e6d8a767…c8dc72`,
identical on the lab and the laptop. **The script differs from the owner-supplied text in one
way:** `ros2 node list` and `ros2 topic list` got `--no-daemon`, because the plain commands would
start a background ROS 2 daemon process. No container, process, server, model or file was
started, stopped or changed. No sudo was needed. A secret-pattern scan of the output found 0
hits. "Line N" below refers to the raw output.

## 1. Summary

There are **two running containers**, both Ubuntu/ROS 2 Jazzy images with host networking and
no GPU attached:
- **Ours:** `marvel-g1-extension-20261119`.
- **Another project's:** `rosa-exam-main`. Its two "mini exam" queue runners use their own
  Ollama on port 11435.

There are also **two Ollama servers running directly on the host**, sharing the one RTX 4080
SUPER:
- ours, v0.40.6 on port 11439;
- the other project's, v0.40.16 on port 11435.

**No Gazebo** process and **no ROS 2** process is running anywhere. Our Phoenix server (port 6006)
is the only trace server. Two exited containers are months old, are not ours, and hold no GPU
memory. The GPU was idle at check time (277 MiB used).

**Levinson's problem: can't tell exactly**, because no symptom was given. The checks found one
structural problem and some risks:
- **The structural problem:** two independent Ollama servers share one GPU with no scheduling
  between them.
- Both containers use host networking.
- Our container runs at the default `ROS_DOMAIN_ID=0`.
- From the earlier check today: the host root disk is 98% full (20 GB free), with Docker's data
  on it.

Two of the other project's queue runners (`mini_exam_lab`, `mini_exam_lab_r2`, lines 44–46) have
been running side by side for 16+ hours against the same Ollama server. Whether that is
intended, I can't tell.

## 2. Checklist

| Check | Verdict | Evidence |
|---|---|---|
| ROS domain | **OK** (with a caveat) | Both containers are on host networking with distinct domains and localhost-only DDS. Ours `ROS_DOMAIN_ID=0`, `ROS_LOCALHOST_ONLY=1` (lines 72–73); rosa-exam `ROS_DOMAIN_ID=220`, `ROS_LOCALHOST_ONLY=1` (lines 93–94). Caveat: 0 is the default, so any future container that leaves it unset would join ours |
| Cross-talk | **CAN'T TELL** | The script's ROS test never ran. `ros2: no` in both containers (lines 75, 96), because `command -v ros2` runs before any `/opt/ros/*/setup` is sourced, so the `ros2 node/topic list` block was skipped. No ROS process is running anywhere (lines 38–46, 84, 104–106), so there is nothing to cross-talk *now*. A corrected command is proposed in §4 (not run) |
| Gazebo | **OK** (nothing running) | No `gzserver`/`gz sim` processes on the host or in either container (lines 38–46, 84, 104–106). Port 11345 is not listening (lines 35–36). Whether Gazebo is installed is unknown, for the same PATH reason (`gz: no`, `gzserver: no`) |
| Ollama / GPU | **PROBLEM** (structural) | Two Ollama servers on one GPU with no coordination: `runtime/bin/ollama serve` (ours, line 39) and `rosa_exam/ollama/bin/ollama serve` (line 41). The GPU is idle now (lines 16, 29–30). The script's "no host ollama" (line 33) only means the `ollama` CLI isn't on PATH; both servers are running. The port check only looked for 11434, so it missed 11435/11439 (seen in today's earlier diagnosis) |
| Phoenix | **OK** | A single instance, ours: `127.0.0.1:6006`, pid 3206419 (line 36), started by `docker exec … marvel-g1-extension-20261119 … phoenix_server.py serve` with its working directory inside our study (line 42). The other project's command lines set no `PHOENIX_*` (lines 44–46). A separate port or project per person is still advisable |
| Mounts | **OK** (no overlap) | Ours: `/media/naeem/d1/marvel proj → /work (rw=true)` (line 68). rosa-exam: `/media/naeem/d1/rosa_exam (rw)` and `…/custodian (ro)` (lines 88–89). Nothing foreign mounts our folder. Note: **our own** container mounts the whole project, frozen artifacts included, read-write |
| Leftovers | **OK** | `exegol-default` exited 2026-07-27 and `quizzical_rubin` (a VS Code dev container) exited 2026-07-07 (lines 52–53, 109–110). Neither is ours. They hold no GPU and are identifiable by image; their owner is not recorded. 10.4 GB of container storage is reclaimable (line 62); not ours to remove |

Nothing urgent was found. No other container writes into our artifacts folder.

## 3. Could my completed lab runs have been affected?

**What the runs used**, confirmed from records rather than memory:

| Batch (UTC) | Container | Ollama | ROS / Gazebo |
|---|---|---|---|
| Qwen G1 held-out: 2026-11-19 11:45:22 → 12:05:33 (`status.json`) | Name not recorded. Telemetry shows a container started 2026-11-17 08:54 UTC, pid 963878; it no longer exists | `127.0.0.1:11439` | **None.** `trial.py` builds `worlds.create_world` mock worlds. No `rclpy`/`ros_*`/Gazebo import in the batch code or the extension backends |
| Ministral 14:26:20 → 14:42:25; Granite 14:42:39 → 14:57:33; Llama 14:57:46 → 15:11:10 (backend `status.json`) | `marvel-g1-extension-20261119` (telemetry `StartedAt 2026-11-19T13:45:31Z` matches line 67) | `127.0.0.1:11439`, the same server process, alive since 2026-11-17 (line 39) | **None**, as above |

**Overlap with the other project:** `rosa-exam-main` was created and started at 2026-11-19
13:36:17 UTC (line 87), and its Ollama server about the same time (line 41, 19:20:50 elapsed).
- **Qwen batch: no overlap.** It ended at 12:05 UTC, 1.5 h before those existed.
- **All three extension batches: they overlap.** The other container and Ollama server were up
  throughout 14:26–15:11 UTC.

**What our telemetry shows during those windows:** 393 samples, about every 10 s (Qwen 122,
Ministral 98, Granite 91, Llama 82).
- **Zero GPU compute processes other than our `llama-server` and GNOME remote desktop.**
- Minimum free VRAM was 8,755 MiB.
- Every loaded-model sample was fully GPU-resident.

**Correctness (pass/fail, call counts): no plausible path, and no evidence.**
- The runs used no ROS or Gazebo, so domains and topics are irrelevant.
- The Python mock worlds lived in our own process and folder; no foreign container mounts it.
- Model outputs come from our own server at temperature 0. Another server competing for the GPU
  could slow or offload ours, but would not change the request we sent.
- All 228 extension trials and all 76 Qwen trials passed exact local-vs-persisted span audits,
  so no foreign spans entered our Phoenix projects.

**Timing (task seconds): no evidence of interference, but not proven absent.**
- 10-second sampling can miss brief GPU use by the other server.
- The other project's activity *before* its current jobs (started about 00:27 and 00:43 Taipei
  on 11-20, lines 44–46) is not visible to me.
- Timing results should keep their existing qualification: contextual lab measurements, not a
  controlled speed comparison.

**What the evidence cannot show:** containers that existed between 11-17 and 11-19 and were later
removed; the other server's model loads between our samples; and whether the other project
ran anything at all during 14:26–15:11 UTC.

## Additional observations (earlier read-only collection, 2026-11-20 13:16 Taipei)

This merges the separate earlier diagnosis note, which has been removed.
- **Listening ports:** Ollama `127.0.0.1:11439` (ours) and `127.0.0.1:11435` (rosa-exam);
  Phoenix `127.0.0.1:6006` (ours). Phoenix health returned 200 on 6006 and nothing on
  6007/6008/4317/4318. Other host services (RDP 3389/3390, 22, 111, 631 and some on 10.0.0.1)
  are unrelated.
- **Disk:** `/` is 915 GB with **20 GB free (98% used)**, and Docker's data root `/var/lib/docker`
  lives there. `/media/naeem/d1` has 386 GB free. `docker system df`: images 75.4 GB,
  containers 10.4 GB (99% reclaimable), volumes 7.9 GB, build cache 11.8 GB.
- **Ollama start times:** ours has been up since 2026-11-17 16:43 Taipei, the same process for
  the Qwen and multi-model runs. rosa-exam's has been up since 2026-11-19 21:36.
- **Lab vs laptop hashes** for G1 `revision-1`: 4,901 of the 4,905 shared files match. The 4
  differences are lab logs/status files that grew after copy-back; not fixed.

## 4. Isolation for Levinson's new trials (proposed commands — not run)

1. **Re-run the cross-talk check correctly**, with approval, from the host:
   ```bash
   for c in marvel-g1-extension-20261119 rosa-exam-main; do
     docker exec "$c" bash -c 'source /opt/ros/jazzy/setup.bash 2>/dev/null || { echo "no ROS"; exit; };
       timeout 10 ros2 node list --no-daemon; timeout 10 ros2 topic list --no-daemon'
   done
   ```
2. **One container per study, with a unique name, a unique ROS domain and read-only access to
   frozen work.** His own folder is read-write; Martin's work is a separate read-only mount, and
the whole `marvel proj` folder is never mounted read-write:
   ```bash
   docker run -d --name levinson-<study>-<yyyymmdd> --network host \
     -e ROS_DOMAIN_ID=42 -e ROS_LOCALHOST_ONLY=1 \
     -v "/media/naeem/d1/levinson-<study>:/work" \
     -v "/media/naeem/d1/marvel proj/preparation:/frozen-martin:ro" \
     <image@sha256:digest> sleep infinity
   ```
   Pick a domain ID not used by anyone (0 = ours, 220 = rosa-exam). Use a bridge network with
   explicit `-p` ports when Gazebo/DDS doesn't need the host network.
3. **One Ollama server per study on its own port, run in agreed exclusive GPU time slots:**
   ```bash
   OLLAMA_HOST=127.0.0.1:11441 OLLAMA_MODELS=/media/naeem/d1/levinson-<study>/models \
     OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_NUM_PARALLEL=1 <ollama-binary> serve
   nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv   # must show no foreign jobs before a run
   ```
   Agree slots with the rosa-exam owner. Abort a batch if foreign GPU processes appear.
4. **A separate Phoenix instance:** `PHOENIX_PORT=6016`, `PHOENIX_GRPC_PORT=4327`, and
   `PHOENIX_WORKING_DIR` in his own study folder, with a project name prefixed `levinson-`.
5. **Record the environment in every run directory:** `docker inspect -f '{{.Id}} {{.Image}}' <name>`,
   the Ollama `/api/version` and the port, `nvidia-smi` before and after, and the disk free space.
6. **Disk:** check `df -h /` before a campaign (it is 98% full today). Write outputs to
   `/media/naeem/d1`.
7. **Do not** stop or reuse `marvel-g1-extension-20261119`, port 11439, port 6006, or anything in
   the rosa-exam project.
