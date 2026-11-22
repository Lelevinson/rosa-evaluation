# Addendum: parity integration for Granite and Llama (DRAFT, results empty)

**Source of truth:** branch `member/martin-parity`, `artifacts/parity-integration-20261121/` (PARITY_AUDIT.md,
ACCEPTANCE_CRITERIA.md frozen at `8f50101`, PA1_CONDITIONS and PA1_RECLASSIFICATION, the Phase B log and runs).

## Why
In G1 (lab, plain adapter, under the owner rule "no per-model fixes"), Granite produced 0 recognized tool calls:
it wrote JSON in code fences and prose. Llama's arguments failed the schema after turn 1, because its Ollama
template drops the tool list once a tool result is the last message. The audit found transport gaps, not proof
of model inability.

These gaps were already partly addressed on 2026-11-17 by the lab `native-schema-v1` profile (rosa-research
`8713f9b`): known-goal results in Gazebo on the known M4 families went from Granite 5/36 to 9/36 and Llama
21/36 to 28/36 (primitives to macro). That profile is not parity-clean: it adds the schemas as extra model-visible
text for two models only. This study asks a narrower question: can each model be fixed with transport-only
changes, under fixed parity rules?

## Fixes allowed (transport only)
- **Llama, PA-2:** a derived Ollama tag from the same weights blob. Meta's documented function-list wording stays
  in the first user message on every turn (taken from Meta's public `llama-models` code). The new digest is recorded.
- **Granite, PA-1:** append one sentence, byte-identical to IBM's official template (HF commit `51dd4bc2`) and to
  `native-schema-v1`'s Granite guidance (SHA-256 `7e12d9b5…624e`). The owner classified it as transport, not an
  exception.
- Qwen and Ministral: no gap found. They take the acceptance test as reference points.

## Phase B acceptance (frozen; one run per model; 10 tasks × 2 arms)
| Model | Adapter SHA-256 | Iterations used (≤ 4 or 3 h) | A1 recognized calls ≥ 0.90 (P / M) | A2 schema-valid ≥ 0.90 (P / M) | A3 parse crashes = 0 | Result |
|---|---|---:|---|---|---:|---|
| Granite | | | | | | |
| Llama | | | | | | |
| Qwen (ref.) | none | – | | | | |
| Ministral (ref.) | none | – | | | | |

Calibration on frozen G1 records (zero model calls): Qwen PASS, Ministral PASS, Granite FAIL A1 (0/36),
Llama FAIL A2 (0.44).

Labels:
- pass → "adapted (transport only)". For Granite: "adapted (transport only: vendor-documented IBM tool sentence)".
- fail → "not adaptable under parity rules".
- infrastructure problem → "acceptance incomplete".

## Phase C: adapted-integration rerun (laptop), frozen G1 held-out cases, both arms
| Model | Known-goal P | Known-goal M | Calls P → M | Native P → M | Censored | Matched pairs | Ambiguous (prelim.) |
|---|---:|---:|---|---|---:|---:|---|
| Granite (adapted) | /36 | /36 | | | | | |
| Llama (adapted) | /36 | /36 | | | | | |

The original G1 results stay unchanged and are not replaced. Phase C is an "adapted-integration rerun (laptop)"
on a different machine from G1 (lab). So any G1 vs Phase C difference mixes the adapter with the hardware.

## Limits to state
The shared prompt and catalogue were developed with Sol and Qwen; parity rules cannot remove that. A transport
repair is engineering credit to the combined system, not intrinsic model ability. No model ranking or parity claim.

Teammate overlap (reported by the teammates in rosa-contexts `member/levinson` `87eb2bd`, `member/krln` `8072aaf`; not verified by us): ADJACENT. Levinson's team uses no argument coercion in any arm (`exam_prep_20261121`, update 2). Report native-schema-v1's list-string → array normalization and ChatOllama's string-argument decoding as assistance, separate from the model's own schema compliance. See parity AMENDMENT_01.

Future work: reuse Levinson's original-ROSA baseline harness to add a stock-ROSA arm to the macro comparison.
