# ROSA workflow live v1: detailed review

Generated 2026-10-22T12:32:41.619877+00:00.

Scope: small, development-informed mock feasibility pilot. Same user goal, two permitted skills, bounded primitive operations and common accepted-report termination. The candidate transfers read / conditional write / verification coordination to ROSA; skill interpretation and reporting remain model responsibilities.

The intervention includes different select_skill execution semantics. Results describe the complete arrangement, not an isolated routing algorithm or novelty claim.

| Backend | Case | Condition | Correct | Report | Calls | Known output | Native | Invalid | Seconds | Persisted trace |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ollama | east_healthy | model | True | SUCCESS | 5 | 575 | 3 | 0 | 113.05 | True |
| ollama | east_healthy | program | True | SUCCESS | 4 | 183 | 4 | 1 | 24.43 | True |
| ollama | west_healthy | program | True | SUCCESS | 3 | 108 | 4 | 0 | 14.62 | True |
| ollama | west_healthy | model | True | SUCCESS | 6 | 582 | 4 | 0 | 76.21 | True |
| ollama | west_ineffective | model | True | FAILURE | 7 | 790 | 4 | 1 | 102.85 | True |
| ollama | west_ineffective | program | True | FAILURE | 5 | 199 | 5 | 1 | 25.97 | True |
| ollama | east_unavailable | program | False | (none) | 7 | 840 | 3 | 4 | 120.38 | True |
| ollama | east_unavailable | model | True | UNKNOWN | 6 | 643 | 2 | 2 | 93.21 | True |
| ollama | west_outcome_unavailable | model | True | UNKNOWN | 6 | 563 | 4 | 0 | 81.55 | True |
| ollama | west_outcome_unavailable | program | True | UNKNOWN | 3 | 288 | 4 | 0 | 41.75 | True |
| ollama | east_controller_busy | program | True | FAILURE | 6 | 594 | 4 | 2 | 86.05 | True |
| ollama | east_controller_busy | model | True | FAILURE | 5 | 491 | 2 | 1 | 64.56 | True |
| siwc | east_healthy | model | True | SUCCESS | 5 | 139 | 3 | 0 | 17.42 | True |
| siwc | east_healthy | program | True | SUCCESS | 2 | 64 | 3 | 0 | 7.09 | True |
| siwc | west_healthy | program | True | SUCCESS | 2 | 64 | 3 | 0 | 7.66 | True |
| siwc | west_healthy | model | True | SUCCESS | 5 | 139 | 3 | 0 | 15.58 | True |
| siwc | west_ineffective | model | True | FAILURE | 5 | 140 | 3 | 0 | 15.70 | True |
| siwc | west_ineffective | program | True | FAILURE | 2 | 65 | 3 | 0 | 6.83 | True |
| siwc | east_unavailable | program | True | UNKNOWN | 3 | 81 | 2 | 0 | 12.33 | True |
| siwc | east_unavailable | model | True | UNKNOWN | 4 | 110 | 2 | 0 | 15.37 | True |
| siwc | west_outcome_unavailable | model | True | UNKNOWN | 5 | 134 | 3 | 0 | 18.44 | True |
| siwc | west_outcome_unavailable | program | True | UNKNOWN | 3 | 75 | 4 | 0 | 9.55 | True |
| siwc | east_controller_busy | program | True | FAILURE | 3 | 87 | 2 | 1 | 9.30 | True |
| siwc | east_controller_busy | model | True | FAILURE | 5 | 140 | 2 | 1 | 17.88 | True |

## Aggregate costs (all attempts)

| Backend | Condition | Correct | Calls | Input tokens | Output tokens | Native operations | Invalid attempts | Trial seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ollama | model | 6/6 | 35 | 82133 | 3644 | 19 | 4 | 531.42 |
| ollama | program | 5/6 | 28 | 64041 | 2212 | 24 | 8 | 313.21 |
| siwc | model | 6/6 | 29 | 49327 | 802 | 16 | 1 | 100.39 |
| siwc | program | 6/6 | 15 | 24803 | 436 | 17 | 1 | 52.74 |

Native operations did not remain constant in live use: Qwen increased from 19 to 24 and Sol from 16 to 17. Extra model-requested reads after program verification/escalation are included, not hidden. Fewer inference calls must not be presented as fewer total robot/sensor operations.


## Status and interpretation

Pending/incomplete backends: none.

Frozen live source hashes unchanged: True.

Both-backend feasibility gate: False.

Per-backend frozen gate details:

```json
[
  {
    "backend": "ollama",
    "status": "COMPLETE",
    "valid": true,
    "candidate_feasibility_gate": false,
    "paired_losses": [
      "east_unavailable"
    ],
    "jointly_correct_healthy_call_savings": [
      "west_healthy"
    ]
  },
  {
    "backend": "siwc",
    "status": "COMPLETE",
    "valid": true,
    "candidate_feasibility_gate": true,
    "paired_losses": [],
    "jointly_correct_healthy_call_savings": [
      "east_healthy",
      "west_healthy"
    ]
  }
]
```

Use analysis.json for the frozen paired gate. A correct fault result may be FAILURE or UNKNOWN; it does not mean successful robot movement. Do not turn a pending or interrupted trial into a pass, or compare aggregate tail log entries.

Latency includes real model loading/inference and tool execution. The first local reference starts cold; inspect per-message load_duration, prompt_eval_duration and eval_duration in evidence before attributing latency savings to orchestration. No separate warm-up inference was added. Pair order is counterbalanced; only one observation per case/condition exists.

Qwen profile: pinned Qwen3.5:9b Q4_K_M digest, 8192 context, seed 42, temperature 0, thinking disabled, mmap enabled, 1024 per call clamped to a 2048 cumulative requested output allowance. Runtime model placement is retained in operator/local-loaded-profile.json. It is not assumed fully GPU-resident.

Sol profile: unchanged account-catalog gpt-6.1-sol via the existing ChatSiwc adapter. No per-call hard generation cap is exposed. Usage is metered; an observed output threshold stops additional execution, but cannot bound an already generated hosted response. Unreturned usage remains censored. Request/time/native limits are matched within each backend; cross-backend token equality is not claimed.

Program-native operations and verification provenance are distinct from model actions. Recovered reports count as combined-system outcomes. A wrong permitted skill fails user-goal completion even if that selected pose is locally verified.

Tokens, authorization headers and encrypted reasoning are excluded from saved records. New OAuth consent stays manual; session-siwc.json records cleanup without credential material. No credential persistence is enabled.

## Failed outcomes and corrections

### ollama / 06-east_unavailable-program

Terminal response: `An error occurred: validation_retry_budget_exhausted`.

Validation codes: report_scope_mismatch, report_scope_mismatch, report_scope_mismatch, report_scope_mismatch.

Length-terminated generations: 0; returned usage complete: True.

Submitted reports (rejections preserved):

```json
[
  {
    "status": "UNKNOWN",
    "observed_values": {
      "bench_arm": {
        "pitch": null,
        "yaw": null
      }
    },
    "actor": "model",
    "accepted": false
  },
  {
    "status": "UNKNOWN",
    "observed_values": {
      "bench_arm": {
        "pitch": null,
        "yaw": null
      }
    },
    "actor": "model",
    "accepted": false
  },
  {
    "status": "UNKNOWN",
    "observed_values": {
      "bench_arm": {
        "pitch": null,
        "yaw": null
      }
    },
    "actor": "model",
    "accepted": false
  },
  {
    "status": "UNKNOWN",
    "observed_values": {
      "bench_arm": {
        "pitch": null,
        "yaw": null
      }
    },
    "actor": "model",
    "accepted": false
  }
]
```

Successful outcomes after validation feedback: 8.

```json
[
  {
    "backend": "ollama",
    "run_id": "01-east_healthy-program",
    "codes": [
      "report_scope_mismatch"
    ]
  },
  {
    "backend": "ollama",
    "run_id": "04-west_ineffective-model",
    "codes": [
      "report_scope_mismatch"
    ]
  },
  {
    "backend": "ollama",
    "run_id": "05-west_ineffective-program",
    "codes": [
      "report_scope_mismatch"
    ]
  },
  {
    "backend": "ollama",
    "run_id": "07-east_unavailable-model",
    "codes": [
      "write_prerequisite_rejected",
      "outcome_classification_mismatch"
    ]
  },
  {
    "backend": "ollama",
    "run_id": "10-east_controller_busy-program",
    "codes": [
      "write_prerequisite_rejected",
      "write_prerequisite_rejected"
    ]
  },
  {
    "backend": "ollama",
    "run_id": "11-east_controller_busy-model",
    "codes": [
      "write_prerequisite_rejected"
    ]
  },
  {
    "backend": "siwc",
    "run_id": "10-east_controller_busy-program",
    "codes": [
      "write_prerequisite_rejected"
    ]
  },
  {
    "backend": "siwc",
    "run_id": "11-east_controller_busy-model",
    "codes": [
      "write_prerequisite_rejected"
    ]
  }
]
```

## What follows

Complete and audit both backends before drawing a comparison. If the frozen gate fails, preserve the negative result and diagnose the recorded failure; do not tune or replace these trials. If it passes, specify a small bounded UR5e Gazebo transfer protocol. No large campaign, physical deployment or generalization claim follows automatically. A strong macro-tool reference and genuinely held-out tasks remain necessary for broader research claims.

All earlier Stage 4, reliability and output-budget results remain separate.

## Recommendation from this completed pilot

- ollama: reference 6/6 correct with 35 calls; program 5/6 correct with 28 calls. Frozen progression gate: False.
- siwc: reference 6/6 correct with 29 calls; program 6/6 correct with 15 calls. Frozen progression gate: True.

Do not advance this version as a validated improvement for both backends. Preserve the useful efficiency evidence alongside the paired reliability loss.

The recorded unavailable-observation program failure chose UNKNOWN but repeatedly used bench_arm instead of /bench_arm. It did not dispatch motion and was not truncated. This isolates a remaining reporting-contract burden; it does not establish that the model failed to recognize uncertainty.

A reasonable next engineering candidate is a common evidence-reference reporting interface: the model classifies the outcome and cites trusted evidence; software retrieves exact identifiers/values and validates freshness. If pursued, apply it to both conditions and both backends, validate separately, and freeze fresh prospective cases before another comparison. Do not silently repair wrong identifiers in these trials or rescore them as passes.

This is a recommendation, not an implementation or a new authorized campaign. Full JTVR remains paused and episodic memory remains optional.
