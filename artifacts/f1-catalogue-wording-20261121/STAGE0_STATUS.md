# F1 Stage 0: status report (for hand-off)

Date 2026-11-21. Branch `member/martin-f1`, created from tag `freeze-2026-11-21`. **Zero model calls.** No
Ollama, hosted API, OAuth or Gazebo was used. No frozen file was changed (`verify_freeze.py` PASS, see the
end). Stage 1 has **not** started.

## Deliverables

| # | Deliverable | Path | State |
|---|---|---|---|
| 1 | Protocol | [PROTOCOL.md](PROTOCOL.md) | draft; thresholds await owner |
| 2 | Wording diff with source quotes | [WORDING_DIFF.md](WORDING_DIFF.md) | done; one quote (the LangChain parser) is to be taken on the lab |
| 3 | Cases: dev pointers, 30 held-out, groups, hashes, leakage table | [cases/](cases/) | done; leakage 30/30 OK |
| 4a | Static inspection of the wrapper (laptop, source only) | [controls/STATIC_CHECK.json](controls/STATIC_CHECK.json) | **PASS** |
| 4b | Scripted controls C1 (W1 equivalence), C2 (no-tool route), C3 (pass counts) | `tools/f1_wording/controls.py` → `controls/CONTROL_*.json` | **NOT RUN: lab unreachable** |
| 5 | Lab plan for Stage 1 | [LAB_PLAN_STAGE1.md](LAB_PLAN_STAGE1.md) | done (not run) |
| 6 | Requests, wall time and Sol usage estimate | PROTOCOL §10 | done |
| 7 | Freeze verification | below | PASS |

Code: `tools/f1_wording/` (`wording.py`, `build_cases.py`, `leakage_check.py`, `static_check.py`,
`controls.py`). Every file is new; nothing under a frozen path changed.

## What could not be done, and why

- **Scripted controls C1–C3 did not run.** Owner rule: tests run on the lab only. The lab didn't
  answer on 2026-11-21 (`ssh lab-rosa` timed out on port 22 twice; ping 100% loss). ~~The laptop has no
  LangChain/ROSA environment~~ **(Corrected 2026-11-21: wrong. I had checked only Windows Python and the default
  WSL distro. The laptop's Ubuntu-24.04 WSL distro has the research env `~/.local/share/rosa-envs/research`,
  where G1 Sol ran; see `SOL_ENVIRONMENT_2026-11-21.md`.)** Per the lab-only rule, `controls.py` has
  **not been executed anywhere**. Its first lab run is
  its first test. Commands are in LAB_PLAN §1–2.
- **The LangChain source quote for W2** (the no-tool reply → `AgentFinish`) ~~is not in the doc yet: that
  package isn't installed on the laptop.~~ **Added 2026-11-21** from the laptop WSL research env
  (WORDING_DIFF, W2 table); the lab-env copy is still to be compared.
- **Code location deviates from the brief:** it is `tools/f1_wording/`, not `tools/f1/`. `tools/f1/` is
  frozen, so any new file there makes `verify_freeze.py` fail as "added".
- `analysis.py` and the Stage 1 live runner are not written. They are pre-freeze gates (PROTOCOL §9 and §11).

## Where the code or evidence pushes back on the hypothesis

1. **The W1 target is rare in the G1 macro setup.** Qwen had 6 G1 macro known-goal failures, and only 1
   was inspection-first (032). Two were class-C deliberation stops (031, 051); 2 were inspection
   depth or no-selection errors on inspection tasks (036, 038), which wording cannot obviously fix;
   1 was a write-fault classification (034). The "all failures selected inspection" pattern comes from M4,
   which used a different prompt. P-a (net ≥ +3 on 24 known-goal cases) may be hard to reach.
2. **W2 has little scored headroom.** Qwen already passed 2/2 G1 ambiguous cases on the scorer. One
   "pass" was deliberation text that happened to contain "which". So W2 may change *human-rated*
   quality more than scored passes. That is why ambiguous outcomes stay PRELIMINARY.
3. **`submit_report` has no clarification status** (`reference.py:16`). W2 is prompt-only. It relies on
   the existing no-tool path, as the brief anticipated.
4. **The wording is true only in the macro condition.** In primitives the model manages the reads
   (`workflow.py:95-97`), so the W1a routine sentence would be false. `make_agent()` refuses non-macro
   modes.
5. **W1b could mislead on interlock-conditioned moves** (for example "move only if the guard is closed"),
   because the movement routine doesn't read readiness checks. No F1 case asks that. W1a says so
   explicitly. The result must not be generalized to that request type.
6. **The hypothesis wording "check readiness interlocks" is never claimed.** The source check holds:
   movement routines read the target pose only (`macro.py:18`; `worlds.py:168`).

## Leakage check

All 30 held-out cases are **OK** (none REVIEW, none NEAR-PARAPHRASE). They were compared against the
12 length-stop trials, the 38 G1 held-out and 16 G1 dev requests. Maximum word-sequence similarity was
0.38, and maximum content-word Jaccard 0.11; the rewrite lines are 0.60 and 0.50. A close paraphrase of M4
09 would score 0.68/0.62. See [cases/LEAKAGE_CHECK.md](cases/LEAKAGE_CHECK.md).

## Thresholds and choices for Martin to confirm

1. P-a: net discordant ≥ **+3** on the 24 known-goal pairs. This is the same as "Q-new exceeds Q-base by
   ≥ 3".
2. P-b: Q-new inspection-first count < Q-base count on the 14 movement cases (Uninformative if the base
   count is 0).
3. P-c: Q-new loses ≤ **1** of 8 inspection controls. Should the 2 unavailable-source cases be included in
   this guard?
4. P-d: S-new loses ≤ **1** per F1 type (5 types). Ambiguous Sol outcomes count only after human rating.
5. P-e: Q-new length-stop trials < Q-base (Uninformative if the base count is 0).
6. Decision: adopt only if P-a, P-c and P-d all hold; P-b and P-e are diagnostics.
7. Leakage thresholds: rewrite at seq ≥ 0.60 or Jaccard ≥ 0.50; review at 0.45 / 0.35.
8. Code location `tools/f1_wording/` instead of `tools/f1/`.
9. Run order: seeded case shuffle (seed 20261121), base/new order alternating by template group, Qwen
   first in one exclusive GPU window, then Sol.

## Freeze verification after this work

See the commit message for the `verify_freeze.py` output, which is recorded at commit time.
