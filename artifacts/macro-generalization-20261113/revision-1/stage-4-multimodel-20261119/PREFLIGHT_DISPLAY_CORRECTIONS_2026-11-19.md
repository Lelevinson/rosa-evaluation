# Preflight metadata display corrections

Date: **2026-11-19**. This is a factual documentation correction, not a protocol or configuration amendment.

I incorrectly transcribed three values into READY_PREFLIGHT.md. The acknowledged original is preserved byte for byte and still matches its recorded acknowledgment hash. The actual launch used the correct immutable MODEL_CONFIG.json/ELIGIBILITY.json data and verified the installed server digests against those sealed values. The original preflight explicitly designated those sealed files as authoritative. No model was substituted; no source, model, prompt, budget, scorer, seal or raw result is changed.

| Field | Incorrect prose value | Correct sealed value |
|---|---|---|
| Ministral disk bytes | `6018857966` | `6022236616` |
| Ministral digest | `1922f1a31a570dfb33f1f97e1e85f4110cd4c66c0364ff3572f00f17f27ef8f0` | `1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71` |
| Llama loaded size and VRAM bytes | `6356048280` | `5951214059` |

## Authoritative metadata

| Model | Exact tag | Digest | Disk bytes | Loaded/GPU bytes |
|---|---|---|---:|---:|
| ministral | `ministral-3:8b-instruct-2512-q4_K_M` | `1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71` | 6022236616 | 6356048280 |
| granite | `granite3.3:8b` | `fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7` | 4942891653 | 6524512501 |
| llama | `llama3.1:8b-instruct-q4_K_M` | `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e` | 4920753328 | 5951214059 |

All three current server digests rechecked against the unchanged seals. This check used metadata requests only, no inference. Do not copy the three incorrect display values into a paper or future setup. Full source hashes and the unchanged acknowledgment binding are in PREFLIGHT_DISPLAY_CORRECTIONS_2026-11-19.json.
