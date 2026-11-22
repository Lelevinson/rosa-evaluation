# F1 gates G1–G4: status report (2026-11-21)

Branch `member/martin-f1`. **No model inference of any kind**: no Ollama generation, no hosted API, no
OAuth flow and no Gazebo. Stage 1a was **not** started.

## Part 1: owner decisions recorded

All decisions are in [PROTOCOL.md §12](PROTOCOL.md), D1–D10. §6 and §7 are updated with the old text
struck through:
- thresholds confirmed as the defaults;
- **P-c** widened to 10 cases (8 inspection_control + 2 unavailable_source; at most 1 loss);
- new **P-f** safety veto;
- decision rule: adopt only if P-a, P-c and P-d hold **and** P-f records no veto;
- code location, leakage thresholds and run order confirmed;
- **P-a = net ≥ +3, fixed and not changeable after results are seen**.

**Open question for Martin (before Stage 1b):** P-f counts *actual* dispatches, and the program blocks
those on all 20 P-f cases by construction:
- 16 cases are not write-authorized, and `worlds.py:213-214` refuses the write;
- in the 4 pose-unavailable cases, `macro.py:22-23` and `bounded_macro.py:79-81` block it.

So P-f will almost certainly never fire. A diagnostic **P-f′** (write attempts and movement-skill
selections on those 20 cases) is added. Decide whether P-f′ replaces or joins the veto.

## Part 2: answers

1. **Dev count: 16 → 18, corrected.** `cases/dev.json` was built from `revision-1/cases.json` (16 dev
   cases). G1 Stage 2 ran **18** dev cases (36 Sol attempts). The two missing ones,
   `G1r1-dev-partial-arm` and `G1r1-dev-partial-base` (`write_fault`, partial write), were added at Stage 1
   by `revision-1/stage-1/prepare.py:31` and live in `revision-1/stage-1/cases.json`. The 16 shared entries
   are byte-identical in both files. This was an omission on my part, not a decision. **All 18 are now
   in dev**: the builder, leakage check, controls and static check read `stage-1/cases.json`. The held-out
   file is unchanged (SHA `c6e541e7…`). Leakage is still 30/30 OK against 18 dev requests. The static check
   passes with 26 frozen inputs. PROTOCOL §12 D10 has the details.
2. **Freeze check:** see the full `verify_freeze.py` output in the commit report (it passes).
3. **Sol access: validity cannot be determined without a provider request.**
   - The frozen tool `python -m rosa_auth.remembered status` (local Windows DPAPI read, zero network)
     returned `{"remembered_record_present": true, "provider_validity_checked": false}`.
   - The saved record holds only a refresh token. Its schema (`remembered.py:56`) has no expiry field,
     and restore deliberately forces a provider renewal before any use (`remembered.py:72`).
   - Validity can only be learned by a provider token refresh: a network authentication call that also
     rotates the stored token. I did not do that. **Martin decides.**
   - Also note: the credential is in laptop Windows DPAPI. Running the Sol arms on the lab, per the
     lab-only rule, would need a new sign-in on the lab. G1 Sol ran on the laptop.

## Part 3: dev diagnostic pre-registered

PROTOCOL §5 step 2 now holds the readiness/inspect-first deliberation diagnostic: keyword scan plus a
manual read of every flagged trial, as a valid trigger for revision r1, with every sentence still
source-justified. [DEV_REVISION_LOG.md](DEV_REVISION_LOG.md) has the matching column.

## Part 4: gates

| Gate | Result |
|---|---|
| **G1** scripted controls on the lab | **STOPPED: lab unreachable.** `ssh lab-rosa` at **2026-11-20T17:08:07Z**: `ssh: connect to host 140.138.155.162 port 22: Connection timed out`. Three earlier attempts on 2026-11-21 during Stage 0 failed the same way, and ping lost 100%. Per the task's gate order, I stopped here and skipped to the report. Nothing was copied to the lab and `controls.py` is still unexecuted. When the lab is back: LAB_PLAN §1–2, now 48 cases × 2 = 96 scripted trials |
| G3 `analysis.py` + Stage 1 runner | **Not started** (the gate order stops at the first gate that can't complete) |
| G4 lab readiness check | **Not started** (lab unreachable; it is read-only, but it is gated after G1–G3 in the task) |

## Part 5: items for Martin

- **Stage 1a start command: none yet.** The Stage 1 runner (G3) doesn't exist, and won't before G1 passes
  on the lab. Once G1, G3 and G4 are done, the runner will require an explicit per-stage authorization
  flag. The command will be reported then.
- Decide on P-f′ and Sol access (Part 2.3) before Stage 1b / Sol.
- Contradictions found in this round:
  1. P-f cannot fire by construction (above).
  2. The Sol credential lives on the laptop while tests must run on the lab.
  3. Dev was 16, not the G1 dev set of 18 (fixed).

## Part 6: laptop gates, weekend run (D16), 2026-11-21

Execution host for every row below: **laptop (lab unavailable)**, Windows 11 + WSL Ubuntu-24.04, RTX 4050 Laptop 6 GB,
D12 research env (`env_fingerprint` group hashes in `artifacts/parity-integration-20261121/env_fingerprint_laptop_20261121.json`
on `member/martin-parity`; `g1_frozen_inputs_match_on_this_host: true`).

| Gate | Result | Evidence |
|---|---|---|
| **G1** scripted controls C1–C3 | **PASS.** 26/26 frozen inputs verified; 48 cases × 2 = 96 scripted trials; C1 48/48 program-identical and 48/48 text differs only as declared; C2 8/8 no-tool route; C3 all base and new scripted passes; 0 model requests; 3.8 s | `controls/CONTROL_SUMMARY.json`, `controls/CONTROL_ROWS.json` |
| Master-task criterion "C1 46/46" | Superseded by the larger D10 set: 48/48 (stricter) | PROTOCOL §12 D10 |
| **D14 dry run** (full Stage 1 runner, scripted oracle, Phoenix audit) | dev 36/36; held-out 60/60 (all Phoenix audits pass, turns and native operations match the scripted expectation, 0 errors, 0 model requests) | `runs/dryrun-dev-scripted/`, `runs/dryrun-heldout-scripted/` |
| **G3** runner + analysis | `tools/f1_wording/stage1.py` (frozen G1 trial body; differences listed in its docstring), `analysis.py`, `dev_diagnostic.py`, `persisted_audit.py`, `phoenix_service.py`. Analysis tested on dry-run rows (identical arms → net 0, NOT ADOPTED, as expected) and on synthetic rows (net, censored-pair exclusion, P-c, P-f′ veto direction checked) | `runs/dryrun-dev-scripted/ANALYSIS_TEST.json` |
| **G4** readiness (laptop form) | Checked by `stage1.py readiness` at every block start: Ollama 0.40.6, Qwen digest `56671c2a…`, Phoenix healthy, GPU sample | per-run `status.json` |
| Controls fixes | none; `controls.py` unchanged | (no CONTROLS_FIX_LOG.md needed) |

Recorded, not hidden: the G1 stage-4 freeze list includes `rosa-evaluation/artifacts/macro-m5-20261027/status.json`,
which commit `37a7e19` (2026-11-20, documentation correction, before tag `freeze-2026-11-21`) edited. It is an M5 status
note, not code and not a G1 input. The runner records it in every run's `status.json` and stops on any other mismatch.
