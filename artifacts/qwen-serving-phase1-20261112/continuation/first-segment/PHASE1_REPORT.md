# Phase 1 Qwen serving screen

Client launch date: **2026-11-12**.

**Exploratory serving check, not an M4 result.** Known-input replay; no robot tools or Sol requests.

Current status: **STOPPED_NO_AUTOMATIC_RETRY**. Charged requests: **16**; known returned output tokens: **2905**; censored/unreturned output upper bound: **0**.

| Profile | Returned / 15 | Measured / 14 | Median unique tokens/s | Range unique tokens/s | Cap hits | A/historical family matches | Repeat agreements |
|---|---:|---:|---:|---|---:|---:|---|
| A | 15/15 | 14/14 | 8.388 | 7.796-10.142 | 0 | 10 | 3/3 |
| B | 1/15 | 0/14 | not recorded | not recorded | 0 | 0 | 0/0 |
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

## B versus A

Incomplete / not run. No candidate decision can be inferred.

## C versus A

Incomplete / not run. No candidate decision can be inferred.

## Limits and interpretation

Profiles are fixed A then B, conditionally C. A single block per profile leaves order/thermal limitations. Server prefix caching is preserved and request order matched. Repeats check stability, not independent variance. A throughput/first-call agreement candidate still needs fresh full-loop correctness validation. Matching a wrong historical call is not success. This study cannot establish robotic reliability or general model parity.

See [protocol](PROTOCOL.md), [freeze](freeze.json), [status](status.json), [analysis](analysis.json), profile hardware/logs, and per-request request/response/result records. All failures and charged reservations are retained.

**Stop reason:** effective_FA_not_enabled
