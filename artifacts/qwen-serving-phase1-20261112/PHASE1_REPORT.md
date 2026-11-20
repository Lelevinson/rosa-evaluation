# Phase 1 Qwen serving screen

Client launch date: **2026-11-12**.

**Exploratory serving check, not an M4 result.** Known-input replay; no robot tools or Sol requests.

Current status: **COMPLETE**. Charged requests: **31**; known returned output tokens: **6384**; censored/unreturned output upper bound: **0**.

| Profile | Returned / 15 | Measured / 14 | Median unique tokens/s | Range unique tokens/s | Cap hits | A/historical family matches | Repeat agreements |
|---|---:|---:|---:|---|---:|---:|---|
| A | 15/15 | 14/14 | 8.388 | 7.796-10.142 | 0 | 10 | 3/3 |
| B | 16/15 | 14/14 | 8.082 | 7.652-8.863 | 0 | 7 | 3/3 |
| C | 0/15 | 0/14 | not recorded | not recorded | 0 | 0 | 0/0 |

Warm-ups count toward resources but not measured metrics. Partial medians are not completed profile results.

## Recorded hardware after each warm-up

| Profile | Offload layers | GPU KV MiB | Warm-up load s | Effective FA / KV |
|---|---|---:|---:|---|
| A | [17, 33] | 128.0 | 13.355 | True / f16 |

A physical GPU reading:
```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%], temperature.gpu, clocks.current.sm [MHz], power.draw [W]
NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 4963 MiB, 959 MiB, 12 %, 51, 480 MHz, 10.25 W
```
A pinned ps output (allocation estimate, not independent proof of physical residency):
```text
NAME          ID              SIZE      PROCESSOR          CONTEXT    RUNNER      UNTIL                   
qwen3.5:9b    56671c2ab938    6.4 GB    45%/55% CPU/GPU    8192       llamacpp    About a minute from now
```

| B | [17, 33] | 68.0 | 13.667 | True / q8_0 |

B physical GPU reading:
```text
name, memory.total [MiB], memory.used [MiB], memory.free [MiB], utilization.gpu [%], temperature.gpu, clocks.current.sm [MHz], power.draw [W]
NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB, 4915 MiB, 1007 MiB, 0 %, 49, 255 MHz, 6.88 W
```
B pinned ps output (allocation estimate, not independent proof of physical residency):
```text
NAME          ID              SIZE      PROCESSOR          CONTEXT    RUNNER      UNTIL                   
qwen3.5:9b    56671c2ab938    6.3 GB    45%/55% CPU/GPU    8192       llamacpp    About a minute from now
```

## B versus A

Median generation speed ratio: **0.963x**. Family agreement: **7/10**. Cap hits A/candidate: **0/0**. Prompt equivalence/room: **True**. Candidate screen: **False**.

- 03-already_satisfied-r1-macro-call-1: A `[{"name": "read_state", "args": {"nodes": ["/ur5e", "/ur5e_readiness"]}}]`; B `[{"name": "read_state", "args": {"nodes": ["/ur5e"]}}]`. Full outputs: [A/02/response.json](A/02/response.json), [B/02/response.json](B/02/response.json).
- 06-ineffective_command-r1-macro-call-1: A `[{"name": "select_skill", "args": {"skill_id": "ur5e.park_right"}}]`; B `[{"name": "read_state", "args": {"nodes": ["/ur5e_readiness"]}}]`. Full outputs: [A/03/response.json](A/03/response.json), [B/03/response.json](B/03/response.json).
- 07-partial_command-r1-macro-call-1: A `[{"name": "select_skill", "args": {"skill_id": "ur5e.inspect_readiness"}}]`; B `[{"name": "select_skill", "args": {"skill_id": "ur5e.park_right"}}]`. Full outputs: [A/04/response.json](A/04/response.json), [B/04/response.json](B/04/response.json).
- 08-partial_command-r1-primitives-call-8: A `[{"name": "select_skill", "args": {"skill_id": "ur5e.inspect_readiness"}}]`; B `[{"name": "submit_report", "args": {"status": "FAILURE", "observation_id": "obs-39ab00e6374c-3"}}]`. Full outputs: [A/11/response.json](A/11/response.json), [B/11/response.json](B/11/response.json).

## C versus A

Incomplete / not run. No candidate decision can be inferred.

## Limits and interpretation

Profiles are fixed A then B, conditionally C. A single block per profile leaves order/thermal limitations. Server prefix caching is preserved and request order matched. Repeats check stability, not independent variance. A throughput/first-call agreement candidate still needs fresh full-loop correctness validation. Matching a wrong historical call is not success. This study cannot establish robotic reliability or general model parity.

See [protocol](PROTOCOL.md), [freeze](freeze.json), [status](status.json), [analysis](analysis.json), profile hardware/logs, and per-request request/response/result records. All failures and charged reservations are retained.
