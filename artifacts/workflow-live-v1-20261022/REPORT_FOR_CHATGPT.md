# Workflow live v1: feasibility report

**Status: COMPLETE.**

This tests the complete orchestration arrangement on six development-informed cases per backend. It is not a held-out benchmark, a novel routing algorithm claim, or a physical-robot safety evaluation.

| Backend | Condition | Correct / completed | Healthy correct / 2 | Calls | Known output tokens | Invalid attempts |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ollama | model | 6/6 | 2/2 | 35 | 3644 | 4 |
| ollama | program | 5/6 | 2/2 | 28 | 2212 | 8 |
| siwc | model | 6/6 | 2/2 | 29 | 802 | 1 |
| siwc | program | 6/6 | 2/2 | 15 | 436 | 1 |

A correct fault trial can truthfully report FAILURE or UNKNOWN; it is not a successful movement.

Both-backend progression gate: **False**.
Do not interpret a pending backend as a failed candidate; inspect status and paired records in analysis.json.

Sol uses unchanged account defaults with an observed cumulative output stopping threshold, not a hard generation cap. Qwen uses 1024 maximum per call and a hard cumulative requested allowance of 2048. Unreturned usage is censored; totals above are known returned usage only. Compare conditions within each backend.

All trial results, raw tool/model evidence, local spans and exact persisted Phoenix spans are retained. Authorization loss and interruptions are checkpointed; no failed trial is silently rerun.

Gazebo transfer requires a separately bounded protocol after this gate; no automatic large campaign is launched.
