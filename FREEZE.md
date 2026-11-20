# Project freeze — 2026-11-21

Frozen by **Martin** on **2026-11-21**, before any new study. No model calls and no
trials were run for the freeze. Nothing in the existing evidence or reports was changed.

| Item | Value |
|---|---|
| Branch | `member/martin` (Lelevinson/rosa-evaluation) |
| Frozen commit | the commit tagged **`freeze-2026-11-21`** (an annotated tag; its parent is `988cfd8`) |
| Manifest | [`FREEZE_MANIFEST_2026-11-21.json`](FREEZE_MANIFEST_2026-11-21.json): SHA-256 per file, 10,735 files |
| Tools | [`tools/freeze/make_manifest.py`](tools/freeze/make_manifest.py), [`tools/freeze/verify_freeze.py`](tools/freeze/verify_freeze.py) (standard library + git CLI, deterministic) |
| Companion repo | `Lelevinson/rosa-research` `member/martin` at `8713f9b` (not part of this manifest) |

## What is frozen

Every **tracked** file under:
- `artifacts/`: all study evidence (M1–M5, G1 revision 1 with all five backends, timing and
  serving screens, the lab container check, delivery receipts);
- `docs/`: protocols, reports, decision records and governance;
- `tools/`: analysis tools, including these freeze tools;
- the root reports: `*.md` and `*.json` at the repository root, including this file.

**Not frozen (living):** `PROJECT_MASTER_README.md`, `PROJECT_LIVE_STATUS.json` and `README.md`.
They keep being updated; their freeze-day version is preserved by the tag. Also not frozen:
`experiments/`, `tests/`, `scripts/` and root configuration files (`.gitignore`,
`.gitattributes`, `.env.example`, `config.toml`, `run.sh`). Their freeze-day versions are still
fixed by the tag.

Hashes are over the canonical repository bytes (the git blob), so the manifest is the same
on Windows and Linux. With `core.autocrlf=true`, Windows checks some LF text files out with
CRLF. The verifier accepts that only for files the manifest marks `crlf_checkout_tolerated`.

## Out-of-git backup

There are 2,727 untracked files (about 940 MB) that are deliberately not in git:
- raw span-trace dumps;
- the G1 exact-inputs tarball;
- duplicate delivery ZIPs;
- the old repo bundle;
- pre-update snapshots;
- the teammate repository snapshot.

They are archived outside the repository with a SHA-256 list, together with a `git bundle` of
this branch and tag. The commit message of `7260cb8` lists the categories. The private chat
handoff and scratch files are local-only and are not in the backup.

## How to verify

```bash
git checkout freeze-2026-11-21        # or any later commit on a branch built on it
python -I -B tools/freeze/verify_freeze.py
```

The verifier exits **0** and prints `FREEZE VERIFY: PASS` only if no frozen file is:
- **changed**, in either the working tree or the staged/committed content;
- **deleted**, including no longer tracked;
- **added**, meaning a new tracked file inside a frozen location.

Otherwise it exits 1 and lists the files. To regenerate the manifest for comparison, run
`python -I -B tools/freeze/make_manifest.py` from the tagged commit. It must reproduce the
committed file byte for byte.

## Rule for new work

1. **New work goes on a new branch.** Don't commit new studies to `member/martin` on top of the
   frozen state without a branch, and never rewrite or move the tag.
2. **Write new outputs only into new directories**, for example
   `artifacts/<new-study-yyyymmdd>/`, `docs/<new-topic-yyyymmdd>/` and `tools/<new-tool>/`. Never
   write into an existing frozen directory, and never edit, rename or delete a frozen file.
   `verify_freeze.py` must still pass on every new branch.
3. Corrections to frozen material go into a new, dated file that cites the frozen one. The
   original stays as it is.
4. The living documents listed above may be updated, recording what changed and when.
