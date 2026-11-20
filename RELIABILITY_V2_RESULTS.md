# Reliability v2 and six-axis UR5e follow-up

Completed2026-10-22 across two separately frozen versions. The first automated
attempt continued after the chat usage limit, completed validation and mock work,
then stopped at a failed independently observed UR5e home reset. Its failure and
cleanup remain preserved. A controller-readiness correction passed two regression
tests and four deterministic controls before the separate arm comparison began.

| Phase | Sol correct outcomes | Qwen correct outcomes |
| --- | ---: | ---: |
| Fresh validation | 8/8 | 8/8 |
| Four-arm mock matrix | 32/32 | 28/32 |
| UR5e A/D transfer | 8/8 | 2/8 |

All96 real persisted Phoenix trace sets match local exports;482 model calls across
both backends. Independent verification checks554 archived members against both
ZIP and working evidence. Earlier Stage4/reliability-v1 archives remain unchanged.

The combined D intervention did not outperform the strong A reference on the
prespecified screen. Qwen B/C each passed8/8 mock cases versus A/D6/8, but the
small matrix, pre-write failures and timing/input variation prevent a causal
improvement claim. B/C alone were not tested on the arm. A is modified ROSA with
the shared repaired interface and guards, not untouched upstream ROSA.

Qwen's six numeric-state arm cases stopped after provider length termination at
the unchanged256-token output limit, before requesting motion; its two missing
sensor cases reported UNKNOWN. This supports diagnosing bounded generation and
completion handling, not declaring Qwen inherently incapable of controlling UR5e.
The tested verification-status flag ambiguity remains documented, not silently
fixed during the experiment. All raw attempted calls, corrections and framework
assistance remain separately attributable.

Earlier progress messages incorrectly called Qwen32/32 correct; the frozen
follow-up protocol repeats that background error. The explicit erratum preserves
the correction to28/32 without changing any original score or frozen document.

- [Full report for ChatGPT](artifacts/reliability-v2-ur5e-review-20261022/REPORT_FOR_CHATGPT.md)
- [Independent replay, attribution and comparisons](artifacts/reliability-v2-ur5e-review-20261022/independent-review.json)
- [Complete evidence ZIP](artifacts/ROSA_RELIABILITY_V2_UR5E_COMPLETE_EVIDENCE_2026-10-22.zip)
- [Original frozen protocol](docs/RELIABILITY_V2_PROTOCOL_2026-10-22.md)
- [Separate arm protocol](docs/UR5E_TRANSFER_V1_PROTOCOL_2026-10-22.md)
- [Frozen-background erratum](artifacts/ur5e-transfer-v1-20261022/BACKGROUND_CORRECTION.md)

ZIP SHA256:`63188649d0c21bd7f0b9a8a70bce01de88b5d2df45845486aafa884d68cadae6`.
Both token sessions were revoked, the local model unloaded, simulators stopped
and the temporary sleep hold released. No experiment or consent remains pending.
These are bounded exploratory results, not safety or generalization evidence.
