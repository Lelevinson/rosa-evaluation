# Execution host: lab computer over SSH

Date: **2026-11-19**. Prospective owner instruction; previous evidence remains unchanged.

The owner clarified: "from now on run every test and trials in the lab computer
via ssh". This establishes the lab as the execution host for future automated
tests, deterministic controls, live trials and model probes. The laptop can be
used for editing, document/evidence review and SSH access. If the lab is
unavailable, report that fact; do not silently run a test on the laptop instead.

Use the existing `lab-rosa` SSH target and the canonical project directory
`/media/naeem/d1/marvel proj/`. Preserve existing repositories, models, results
and other users' workloads. No credentials belong in this document or Git.

## Read-only connection check

SSH succeeded on 2026-11-19. The live `nvidia-smi` query reported:

| Field | Observed value |
|---|---|
| GPU | NVIDIA GeForce RTX 4080 SUPER |
| Total VRAM | 16,376 MiB |
| Free VRAM at this instant | 15,916 MiB |
| GPU utilization at this instant | 0% |

This was an inventory query, with **zero inference requests, no automated tests,
no robot operations and no remote file changes**. A single idle observation is
not the frozen three-sample GPU preflight, model-digest check, loaded-model
offload measurement or full readiness validation. Availability can change.

## Effect on the current project

The completed G1 Sol batch was orchestrated in laptop WSL, while its model
inference was hosted remotely by OpenAI. Its retained 76 attempts, 200 requests,
timings, interruptions and frozen configuration are historical facts. This
prospective instruction does not relabel that execution host or rerun the batch.
Future hosted-model runners should also execute on the lab; hosted Sol inference
itself does not use the lab GPU.

Qwen local inference will execute on the lab GPU. Prior laptop memory/offload
constraints do not describe the lab's RTX 4080 SUPER. Resource accounting,
finite request/token/time budgets, model/settings checks and checks for
competing lab GPU use remain applicable. Laptop Chrome/Unity activity is not a
lab GPU preflight measurement.

The frozen G1 `REQUEST_RECEIVED.txt` explicitly permits a separately recorded lab
configuration, and `revision-1/PRE_RUN_NOTE.md` repeats that option. Preserve the
frozen originals. Before the next authorized model batch, record exact host and
software inventory, model digest/quantization, effective serving settings,
loaded offload and GPU samples in a dated execution appendix. Keep cases,
conditions, scorers, permissions, budgets and model settings unchanged unless
separately authorized. Different-host latency must be labeled rather than
pooled as a controlled hardware-matched model-speed comparison.

The four new Sol clarification judgments remain pending. This host decision
does not supply human ratings, new OAuth consent, authorization for an
additional stage, Git publication, or permission to copy encrypted authorization
stores between machines. Secure hosted authorization on the lab must be
established through supported existing mechanisms, without exposing credentials
or weakening their storage protection.

## Compact research preflight

1. **Difference:** execution-host configuration only; no new algorithm or ROSA
   mechanism. The existing primitive/macro comparison remains the control.
2. **Need:** the owner now explicitly selects the lab. Current observed lab
   hardware is above; earlier laptop limitations must not be asserted for it.
   No new performance result follows from this inventory query.
3. **Decision:** all future tests/trials execute over SSH on the lab; unavailable
   SSH means report/preserve, with no automatic laptop fallback. Independent
   goal verification and the established recovery rules remain unchanged.
4. **Fairness:** retain identical information, cases, tools, serving settings
   and budgets within each comparison. Record host/runtime differences and keep
   prior studies distinct. The completed Sol batch is not moved retrospectively.
5. **Smallest next step:** record this policy and verify SSH/hardware without
   inference (done). Prepare the specific lab execution environment before any
   separately authorized batch. Do not silently bypass outstanding stage gates.

Related records: [living master](../PROJECT_MASTER_README.md),
[completed G1 Sol batch](../G1_SOL_HELDOUT_REPORT_2026-11-19.md),
[frozen G1 pre-run note](../artifacts/macro-generalization-20261113/revision-1/PRE_RUN_NOTE.md).
