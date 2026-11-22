# Laptop execution setup — inventory and G1 target configuration (2026-11-21)

Status: Part 1.1 + 1.2 complete, read-only. **Stopped at the Part 1 ⛔ gate.**
Nothing was downloaded, installed, started or loaded. Zero model calls.

## 0. Owner decision (recorded)

**PX-1 (owner, 2026-11-21).** The lab is unavailable, probably for days. Execution
moves to Martin's laptop (Windows 11 + WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB). This
replaces the lab-only rule for F1 and for parity Phases A–C. Phase D's machine is
decided at its D0 gate. Laptop and lab results must be explainable by the same model
bytes and settings, differing only in hardware. (Mirrored in F1 PROTOCOL.md as D16.)

## 1. Laptop inventory (read-only, 2026-11-21)

| Item | Observed | How |
|---|---|---|
| CPU / RAM | i7-13650HX, 15.7 GB host RAM; WSL sees ~7 GB (no `.wslconfig`, default NAT networking) | CIM, `free -g` |
| GPU | RTX 4050 Laptop, 6141 MiB total, 5374 MiB free at check (548 MiB used by desktop) | `nvidia-smi` in WSL |
| Driver / CUDA | 581.86 (Windows) / WSL nvidia-smi 580.110, CUDA 13.0 | `nvidia-smi` |
| Disk | **Only drive C:. 27.9 GB free of 475 GB (95% used).** WSL Ubuntu-24.04 `ext4.vhdx` (12.3 GB) also lives on C:, so anything stored "inside WSL" consumes C: too | `Get-PSDrive`, Lxss registry |
| Ollama A (PATH app) | `C:\Users\user\AppData\Local\Programs\Ollama\ollama.exe`, client 0.24.0, not running; env `OLLAMA_MODELS=C:\Users\user\.ollama\models` | `--version`, tasklist |
| Ollama B (project pin) | `C:\Proj\robotics\introtorobotics\.local\ollama-0.40.6\ollama.exe` (Windows build, 1.9 GB dir), fetched 2026-10-20 by `.local/fetch_ollama_release.py`, which checked the official `ollama-windows-amd64.zip` SHA-256 `e3596375…b427`. Not running | file listing, script |
| Which one M4 / timing used | **Ollama B, 0.40.6**, serving port **11436** on the WSL-private address, models `C:\Users\user\.ollama\models` (M4 server env; timing PHASE0_REPORT: "hidden pinned server … port 11436"; client 0.24.0 explicitly *not* used) | `macro-m4-20261027` env dump, `qwen-timing-probe-20261112/PHASE0_REPORT.md` |
| Ollama in WSL | none (Ubuntu-24.04 and 22.04 both stopped, no `ollama` on PATH, no server) | `which -a`, `pgrep` |
| Ports | 11434, 11436, 11440 not listening | `netstat` |
| Models present | only `qwen3.5:9b` in `C:\Users\user\.ollama\models` (6.2 GB on disk) | manifests dir |
| Qwen bytes | config `08f9698c…`, weights `02d45dc1cf45…278d` (5,629,109,120 B), projector `f836f08f…`; the manifest embeds platform manifest `56671c2a…` = the G1 digest. **Weights blob equals the one the lab llama-server loaded.** | manifest vs `stage-4-qwen-lab-20261119/MODEL_LOAD_PREFLIGHT.json` |
| Ministral / Granite / Llama | **not present** | — |
| D12 research env | `~/.local/share/rosa-envs/research`, Python 3.12.3, 92 dists `e368d815…`; langchain-core 0.3.86, langchain-ollama 0.3.10, ollama 0.6.3 (**same versions as the lab G1 container**); `g1_frozen_inputs_match_on_this_host: true` | `env_fingerprint_laptop_20261121.json` (F1 `env_fingerprint.py`) |

## 2. G1 target configuration

Sources: `R` = `artifacts/macro-generalization-20261113/revision-1/`.
`MC` = `R/stage-4-multimodel-20261119/backends/<m>/MODEL_CONFIG.json`;
`LM` = `…/LOADED_MODEL.json`; `LOG` = `…/FRESH_LOAD_LOG_FILTERED.txt`;
`QP` = `R/stage-4-qwen-lab-20261119/MODEL_LOAD_PREFLIGHT.json`;
`TAGS` = `R/stage-4-multimodel-20261119/SERVER_TAGS_BEFORE.json`;
`LMP` = `…/backends/<m>/local_model.py` (`configured_model`);
`J` = physical-call journals / trial `result.json` request records.

| Field | Qwen3.5-9B | Ministral-3-8B | Granite-3.3-8B | Llama-3.1-8B | Source |
|---|---|---|---|---|---|
| Tag | `qwen3.5:9b` | `ministral-3:8b-instruct-2512-q4_K_M` | `granite3.3:8b` | `llama3.1:8b-instruct-q4_K_M` | MC, TAGS |
| Digest | `56671c2a…3c90` | `1922accd…6b71` | `fd429f23…f1f7` | `46e0c10c…666e` | MC, TAGS |
| Quantization | Q4_K_M | Q4_K_M | Q4_K_M | Q4_K_M | TAGS |
| Download size (bytes) | 6,550,825,550 | 6,022,236,616 | 4,942,891,653 | 4,920,753,328 | TAGS |
| Template sha256 | built-in renderer `qwen3.5` | `5b74c26b…` (+ built-in parser `ministral`) | `3da071a0…` | `948af274…` | MC, SERVER_SHOW |
| Ollama | 0.40.6, **Linux** build, project-local in container | same | same | same | `operator/complete_preflight.py:66`, master README |
| Lab GPU | RTX 4080 SUPER 16 GB, driver 570.195.03, CUDA 12.8 | same | same | same | `ENVIRONMENT.json` |
| num_ctx | 8192 | 8192 | 8192 | 8192 | LMP, LM |
| temperature / seed | 0 / 42 | 0 / 42 (model default 0.15 overridden) | 0 / 42 | 0 / 42 | LMP, SERVER_SHOW |
| num_predict per call | 1024 | 1024 | 1024 | 1024 | LMP |
| think | false (wire) | false (wire; no thinking capability) | false (wire; n/a) | false (wire; n/a) | J, MC |
| stream (wire) | true (`streaming=False` in the constructor, but ChatOllama streams on the wire) | true | true | true | J (198/198 Qwen calls), LMP |
| use_mmap | true | true | true | true | LMP |
| KV cache | f16 (256 MiB) | f16 (1088 MiB) | f16 (1280 MiB) | f16 (1024 MiB) | QP, LOG |
| Flash attention | enabled (server default; no env override recorded) | enabled | enabled | enabled | QP, LOG |
| keep_alive | not sent → server default 5 min (load 18:46:28, expiry 18:51:28) | default | default | default | QP, LM |
| Parallel | `-np 1` | 1 | 1 | 1 | QP |
| Layers on GPU | 33/33 | 35/35 | 41/41 | 33/33 | QP, LOG |
| Loaded size at 8192 | 5,862,210,928 B (5.46 GiB) | 6,356,048,280 B (5.92 GiB) | 6,524,512,501 B (6.08 GiB) | 5,951,214,059 B (5.54 GiB) | LM, QP |
| Load wall time | 6.59 s | not recorded here | not recorded here | not recorded here | QP |
| Profile | none (plain adapter, built-in renderer/parser) | none (plain) | none (plain) | none (plain) | PARITY_AUDIT §0 |

Note on profiles: the rosa-research `8713f9b` native-schema Ollama profile was **not**
used in G1, and it is Llama/Granite-only, so it is not parity-clean (PARITY_AUDIT §0.1, §0.5).

## 3. Contradictions with the task's assumptions

1. **Disk.** The four models need ~22.4 GB, and a Linux 0.40.6 install ~1.4 GB download
   + ~2–3 GB unpacked. C: has 27.9 GB free and WSL storage also sits on C:. A Linux-in-WSL
   setup with a full Qwen copy would leave ~0–2 GB. Not safe.
2. **VRAM.** Every G1 model needed 5.5–6.1 GiB at num_ctx 8192. The laptop GPU has
   6.0 GiB total, ~5.2 GiB free. **None of the four will be fully GPU-resident.** The
   timing study saw Qwen at **17/33 layers** on this GPU. With partial CPU offload,
   outputs may not be token-identical to the lab, even with the same bytes and settings,
   and runs will be several times slower. This is "hardware only", but it is large.
3. **OS build.** The lab ran the Linux build. The existing laptop pin (and M4/timing)
   is the Windows build. Same version and llama.cpp, different binary.
4. **Not a problem:** a 0.40.6 pin already exists on the laptop (Windows build, the
   M4/timing one). It stays untouched.

## 4. Download plan (needs owner OK; nothing done yet)

| What | From | Size | Stored at |
|---|---|---|---|
| Ollama 0.40.6 Linux build `ollama-linux-amd64.tar.zst` | GitHub release v0.40.6 (asset digest `sha256:c164ab8b…c5e0`, checked against release `sha256sum.txt`) | 1.44 GB download, ~2–3 GB unpacked; tarball deleted after hash check | Option L only |
| — or — Ollama 0.40.6 Windows build `ollama-windows-amd64.zip` | same release (`sha256:e3596375…b427`) | 1.47 GB download, 1.9 GB unpacked | Option W only |
| `ministral-3:8b-instruct-2512-q4_K_M` | registry.ollama.ai | 6.02 GB | new model dir |
| `granite3.3:8b` | registry.ollama.ai | 4.94 GB | new model dir |
| `llama3.1:8b-instruct-q4_K_M` | registry.ollama.ai | 4.92 GB | new model dir |
| `qwen3.5:9b` | **no download**: reuse existing blobs (digest already matches) | 0 (hard link) or 6.55 GB (copy) | new model dir |
| **Total download** | | **~17.4 GB** | |

Options (owner picks one):

- **W (recommended given the disk).** Windows 0.40.6 in a new folder
  `C:\Proj\robotics\introtorobotics\.local\parity-ollama-0.40.6\`, models in
  `C:\Proj\robotics\introtorobotics\.local\parity-ollama-models\`, port **11440**,
  bound to the WSL-reachable address like the timing setup. Qwen blobs are **hard-linked**
  (same NTFS volume, zero extra bytes, the original store is not changed).
  Peak use ~19 GB, leaving ~9 GB free. Cost: Windows build, not the lab's Linux build.
- **L (closest to the lab).** Linux 0.40.6 inside WSL Ubuntu-24.04
  (`~/.local/share/parity-ollama-0.40.6/`, models `~/.local/share/parity-ollama-models/`,
  port 11440). Needs a full Qwen copy (6.55 GB) because WSL can't hard-link into the
  Windows store. Total ~26 GB on C:. **Only safe if ~15 GB is freed on C: first.**
- (L-variant: Linux binary with the model dir on `/mnt/c` to share Qwen. Not recommended:
  models are read over the slow WSL file bridge, and mmap over it is unreliable.)

Before long runs, see the settings list in `LAPTOP_SETUP_2026-11-21.md` (written at 1.5).
