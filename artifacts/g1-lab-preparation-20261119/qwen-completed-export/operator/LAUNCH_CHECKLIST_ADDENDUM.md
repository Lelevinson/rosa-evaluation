# Qwen lab launch checklist and operational addendum

Date: **2026-11-19**. Owner acknowledged the preflight and authorized launch.
This adds read-only operational evidence; the 81-file backend seal and 3,796 original frozen inputs remain unchanged.

The 76-trial batch launched on the lab at **19:45 Taipei time** (11:45 UTC).
Worker PID at launch: 3108164. Detached execution uses the existing Jazzy container.
The original eight-hour window and cumulative 611-request cap apply, including the one auxiliary load already spent.
No optional replay, new catalogue probe, Sol replication, OAuth consent, robot movement or Git publication is included.

## Checklist results

- **Environment:** RTX 4080 SUPER, NVIDIA driver 570.195.03; nvidia-smi reports CUDA compatibility 12.8. This is not a measurement of installed CUDA toolkit version. Container image identity and RepoDigest are sha256:472fb4307f978886524430f2fae764e168ca95acd13c45a3edb17cc5a33c819a. Restart policy is "no"; no automatic reboot recovery is claimed.
- **GPU gate:** fresh three-sample idle check passed before launch. Only the existing GNOME remote-desktop GPU process was observed beforehand. Future other-user activity is unknown; no application was stopped. GPU utilization, clocks, memory, power, temperature, process inventory, container state and loaded-model inventory are sampled during execution.
- **Power/terminal:** detached worker plus a separately detached, temporary systemd sleep/idle inhibitor. The inhibitor exits after terminal run status. This does not prevent power loss, administrator reboot, explicit shutdown or all update actions. No permanent system policy changed.
- **Request-body parity:** 48 byte-identical ChatRequest serializations against the unchanged frozen configured adapter, using the eight archived scripted controls' messages/tools and 1,024/512 output allowances. These checks made zero inference requests. They demonstrate port serialization parity, not identity of outputs across hardware or historical requests that were never captured.
- **Timing fields:** an injected, zero-network response verified preservation of total_duration, load_duration, prompt_eval_count, prompt_eval_duration, eval_count and eval_duration through the measured adapter. Real returned values are retained per call. Any omitted field remains not recorded; cached-token counts are not invented.
- **Local failures:** injected HTTP 500, timeout and connection-reset analogues retained bounded exception/status metadata and were ineligible for retries. HTTP 500 does not itself establish CUDA OOM; no raw error text is retained. The monitor counts fixed server-log signatures and records container state for diagnosis. Censoring follows frozen A3 and actual failure-stage evidence; unknown parser/model errors are not automatically classified as infrastructure. No automatic replay.
- **Keep alive:** frozen request bodies retain the original default idle model retention. No request override, maintenance inference, or unload-policy change was introduced. Active requests ordinarily refresh the idle window, but zero reloads are not guaranteed. Load duration and periodic loaded-model inventory make this visible. The model had auto-unloaded while awaiting review, so the first task may include a cold load.

The first supplementary check failed before any inference because ChatRequest is not exported from the installed ollama package root. Its source and log are retained; importing the existing class from ollama._types corrected this check only. The second check passed. Frozen runtime files were not edited.

## Gate provenance and interpretation

The parent freeze includes the approved reduced-metadata repair (G-c), the independent review clearance of the effective human-adjudicated scoring layer (G-e), and the separately returned development human review (G-f). Original failed reviews remain archived. See stage-3/error-metadata-v2-20261119/REPAIR_REPORT.md, stage-3/clarification-scoring-v2-20261119/independent-review/CLEARANCE.json, and stage-3/human-review-20261119/INTAKE_RECEIPT.json.

The completed first Sol batch remains 73 PASS and 3 infrastructure-censored attempts after its own four held-out human ratings. It is not rerun or replaced. New Qwen ambiguous responses need a new blinded packet and ratings.

Every Qwen results table must state **lab hardware; not directly comparable to M4**. The primitive/macro contrast is within the same backend and hardware. Different workloads and historical missing fields prevent calling this a controlled laptop-versus-lab speed experiment. Sol retains hosted inference and its original orchestration provenance; cross-backend time differences cannot isolate model or hardware effects.

Catalogue size is **P4**, and its separate probe is **not run** in this batch. P3 was dropped. AI-only case authorship and the approved P1-prime/P2 domain-specific rules remain unchanged.
