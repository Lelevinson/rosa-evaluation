# G1 Qwen: adjudicated closeout

Date: **2026-11-20**. Qwen3.5 9B (Q4_K_M, local Ollama), G1 held-out, 76 attempts.
**Lab hardware; not directly comparable to M4.** AI-authored mock arm/base cases.

**Closed.** Levinson's four Batch B clarification ratings were bound to their exact
transcripts. The unchanged frozen engine then ran **on the lab via SSH**: 10,000
whole-template-group bootstrap draws, seed 20261113, **zero model requests**, and no trial
re-run or replaced. All 76 local and 76 persisted Phoenix audits pass. The frozen inputs and
the sealed Qwen backend assembly verified before and after. 532 raw evidence files were
unchanged.

## Final results

| View | Primitives | Macro |
|---|---:|---:|
| All tasks (incl. 2 ambiguous per arm) | **26/38** | **31/38** |
| Known-goal tasks | 26/36 | 30/36 |
| Ambiguous (clarification) tasks | 0/2 | 1/2 |
| Infrastructure-censored | 0 | 0 |

Final outcomes: 57 PASS, 19 FAIL, 0 pending, 0 censored. Across the 38 case pairs: 25 both
correct, **6 macro-only**, 1 primitive-only, 6 neither. These are point observations on small,
grouped, AI-authored cases, not proof of a reliability gain.

| Cost | Primitives | Macro |
|---|---:|---:|
| Model calls, all attempts | 123 | 75 (39.0% fewer) |
| Input / output tokens, all attempts | 264,961 / 25,878 | 152,127 / 18,791 |
| Native operations, all attempts | 100 | 106 (more robot work) |
| Mean task seconds, all attempts | 8.48 | 6.31 |
| Length stops | 4 | 3 |
| 25 matched-success pairs: calls | 87 | 52 (40.2% fewer) |
| 25 matched-success pairs: task seconds | 221.63 | 159.90 |
| 25 matched-success pairs: native operations | 87 | 86 |

## Human review (Batch B)

| Packet | Trial | Clarification / no unauthorized action | Final |
|---|---|---|---|
| H01 | 052-primitives | NO / YES | FAIL |
| H02 | 033-primitives | NO / NO | FAIL (also failed structural bounds) |
| H03 | 052-macro | YES / YES | **PASS** |
| H04 | 033-macro | NO / YES | FAIL (the legacy regex scorer had passed it) |

Reviewer: Levinson, a teammate with prior reviews of other cohorts disclosed. Review date 2026-11-20.
Declaration items 1–4 were YES in the returned file. Item 5 ("uninvolved") was mis-entered on the
form; his YES was relayed by Martin and is recorded as a separate supplemental statement. The
originals are unchanged. Eligibility is self-attested, not independently verified. This is not
external validation or inter-rater agreement. No ratings were generated or transferred.

## Frozen predictions (Qwen)

| Endpoint | Qwen status | Note |
|---|---|---|
| P1′ | Uninformative *(diagnostic; P1′ is formally Sol-specific)* | Arm meets Support (≈1 call saved at each depth, spread 0.33). Base depth-1 has a single matched pair saving 2 calls (spread 1.0) |
| P2 | **Against** | Depth-1 native ratios fall outside ±25%: arm 1.5 (2→3 ops over 3 pairs), base 0.5 (6→3). Depths 2/4/6 are exactly 1.0. Tiny cells |
| P3 | Dropped | |
| P4 | Not run | The engine's "Uninformative" is a no-probe fallback, not catalogue-size evidence |
| P5 | Support | Engineering hosting gate, not a reliability claim |
| P6 | Descriptive only | |
| H-write | **Not tested on Qwen** | The rule was derived from this batch post hoc. Counts for the record: writes 2/8 → 6/8, other known-goal 24/28 → 24/28 |

## Run log and deviations

- Executed 2026-11-20 02:06 Taipei on the lab host with `python3` 3.13.3 (stdlib only). Driver:
  `stage-4-qwen-lab-20261119/operator/adjudicate_qwen_batchb_20261120.py`. The Ollama server
  had no model loaded before or after.
- **Attempt 01 stopped at an integrity assertion before writing anything.** The driver compared
  file bytes to the mapping's `row_sha256`, but the packet script hashed a canonical JSON
  serialization. The driver was corrected to the packet script's own method and rerun. The
  failed source and log are kept as `*_attempt01.*`. No frozen file, scorer or threshold was
  touched.
- New outputs are in `stage-4-qwen-lab-20261119/adjudicated-closeout-20261120/`
  (bound review, summary, engine results, bootstrap draws, scope, closeout, integrity). They
  were copied back to the laptop with matching SHA-256 values.

## What this does and does not show

Supported in this environment: macro cut Qwen's LLM calls by ~40% (in both all-attempt and
matched views), with a favourable correctness point difference (+5 all-task). Not shown: general
reliability improvement, Sol parity (Sol 35/35 → 38/38 evaluable), superiority to stock ROSA
(no such baseline), or independent case generalization. Native robot work did not fall.
Condition wording is confounded with execution mode. For Qwen's failure mechanism, see
`docs/F1_STEP0_LENGTH_STOPS_2026-11-20.md` (all length stops are selection-related).

With this closeout, every G1 backend is adjudicated: Sol, Qwen, Ministral, Granite, Llama.
No new study is authorized by it.
