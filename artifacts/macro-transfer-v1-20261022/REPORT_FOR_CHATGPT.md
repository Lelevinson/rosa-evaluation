# Strong macro reference and fresh UR5e cases

This is a small prospective pilot, one run per cell. Previous studies are unchanged.

| Backend | Condition | Correct/completed | Calls | Input tokens | Output tokens | Native | Invalid | Faults exercised/completed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ollama | model | 4/6 | 39 | 122340 | 5088 | 25 | 4 | 3/3 |
| ollama | macro | 5/6 | 22 | 61179 | 3615 | 19 | 5 | 3/3 |
| ollama | workflow | 5/6 | 21 | 57269 | 3436 | 19 | 4 | 3/3 |
| siwc | model | 5/5 | 23 | 48067 | 747 | 13 | 0 | 2/2 |
| siwc | macro | 5/5 | 11 | 21353 | 309 | 13 | 0 | 2/2 |
| siwc | workflow | 4/5 | 9 | 15348 | 229 | 11 | 0 | 1/2 |

```json
[
  {
    "backend": "ollama",
    "status": "COMPLETE",
    "trials": 18
  },
  {
    "backend": "siwc",
    "status": "STOPPED",
    "trials": 15
  }
]
```

Macro and workflow deliberately implement the same acquisition policy. Their contrast tests software packaging and live feasibility, not a novel selection algorithm. Bundling gains over primitive tools belong to the combined system. Observed equality is not statistical equivalence; six cases cannot establish general reliability.

Primary correctness includes exact dispatch/fault coverage. A truthful FAILURE without attempting the authorized ineffective command fails this new contract; earlier scores are unchanged. Detailed per-case outcomes, latency, tool attempts, invalid attempts, censored usage and native costs appear in analysis.json and raw records.

Qwen uses a requested generation allowance. Sol uses an observed threshold; cross-backend hard output-budget equivalence is not claimed. Unreturned generations are not zero-cost.
