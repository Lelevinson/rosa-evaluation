# Where and how G1's Sol arms ran, and the F1 Sol plan (D12)

2026-11-21. Read-only investigation; no model request, network call or credential refresh.

## Correction first

Stage 0 said "the laptop has no LangChain/ROSA environment". **That was wrong.** I had checked only Windows
Python and the default WSL distro (Ubuntu-22.04). The research environment lives in the laptop's
**Ubuntu-24.04** WSL distro, which was stopped at the time. It has been corrected in STAGE0_STATUS.md.

## How G1 Sol ran (from the frozen run records)

| Item | Evidence |
|---|---|
| Host | **Laptop, WSL2 Ubuntu-24.04** (kernel 6.6.87.2-microsoft-standard-WSL2), not the lab and not a container. Paths in the run logs are `/mnt/c/Proj/robotics/introtorobotics/...` (`stage-4/operator/launcher.log`, `stage-4/phoenix-service.json` storage). The distro name was not logged; the envs exist only in Ubuntu-24.04 |
| Interpreters | `stage-4/launch.py:13-14`: `PHOENIX='/home/martin/.local/share/rosa-envs/phoenix/bin/python'`, `RESEARCH='/home/martin/.local/share/rosa-envs/research/bin/python'` (a venv on `/usr/bin/python3.12`, Python 3.12.3) |
| Entry point | `stage-4/launch.py`, started detached (`operator/worker.json`: pid 437, 2026-11-19T07:01:45Z). It starts the owned Phoenix on 127.0.0.1:6006, then `RESEARCH -B stage-4/runner.py` with a cleaned environment (`launch.py:49-52`), then `analyze_results.py` |
| Interruptions | Provider interruptions; unstarted cells resumed through `operator/continuation-01..03/resume.py` (last: pid 1302, 07:24:08Z), with every attempted cell retained. Status: COMPLETE, 76/76, 200 requests, 07:02:57 → 07:38:02 UTC |
| Credential | Windows DPAPI remembered record via `rosa_auth.remembered` (`launch-authorization-status.json`: `PROTECTED_REFRESH`, 1 token refresh, 0 inference before launch) |
| Frozen code | `stage-4/freeze.json`: **3,796** file SHA-256s (3,744 evaluation, 50 rosa-research, 2 reports) |

## Is it reproducible today?

- **Frozen code: yes, apart from one documented non-code file.** I re-ran the frozen `stage-4/common.verify()`
  in the same env, which is read-only. 3,795/3,796 files match byte-for-byte, including all 50
  `rosa-research` files. The one mismatch is `artifacts/macro-m5-20261027/status.json`, the M5 status record
  edited on 2026-11-20 (`publication_update`, commit `37a7e19`). It is a status document, not code.
- **Environment: present and fingerprinted.** Python 3.12.3; 92 distributions (SHA `e368d815…`).
  `langchain` 0.3.30, `langchain-core` 0.3.86, `langchain-openai` 0.3.35, `jpl-rosa` 1.0.10, `openai` 2.54.0,
  `pydantic` 2.14.1. Full record: `controls/ENV_FINGERPRINT_laptop_wsl_2026-11-21.json`, made with
  `tools/f1_wording/env_fingerprint.py`. **No package-version snapshot was saved at G1 time**, so env
  identity with 2026-11-19 is inferred from the unchanged interpreter path and venv, not proven.
- **Credential:** a remembered record is present. Its validity is unknown without a provider refresh,
  which is Martin's decision (GATES_STATUS Part 2.3).

## F1 Sol plan (D12, a documented exception to the lab-only rule)

Run S-base and S-new in **this same laptop WSL Ubuntu-24.04 research env**, as G1 Sol did, with no new
sign-in on the lab. Conditions before any Sol request:
1. **Code identity with the lab copy:** run `env_fingerprint.py` with the lab container's research env on
   the lab copy (LAB_PLAN §2a). `rosa_reliability`, `g1_frozen_inputs`, `f1_code` and `f1_cases` group
   hashes must be **identical** to this laptop record, and `g1_frozen_inputs_match_on_this_host` must be true
   on both. Package versions are compared and reported. The Sol arms don't use the lab env, so a package
   difference there is a reported difference, not a blocker for Sol. It does matter for comparing W2's
   LangChain parser file hash.
2. Scripted controls C1–C3 pass on the lab (G1). Then repeat them as a **zero-model dry run in this laptop
   env** too, so the exact Sol execution env is also shown to give identical program behaviour. Martin
   must approve that laptop dry run, because it is a test outside the lab.
3. Owner authorization for G8 (Sol), including the credential refresh.
4. Phoenix: use a separate owned instance and port for the laptop (not 6006, if anything else is using it),
   recorded per run.
