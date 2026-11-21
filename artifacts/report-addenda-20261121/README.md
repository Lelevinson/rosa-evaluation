# Report addenda drafts (weekend 2026-11-21 to 23)

Drafted by session B (Claude Opus 5.5, AI) on 2026-11-21, **before any result exists**. All results tables are
empty on purpose. Session A fills them from the frozen analysis outputs only. The claim wording stays as drafted,
unless a result forces a "partial" or "designed, not run" label (deadline rule: Mon 2026-11-23 08:00 Taipei).

Common facts for all three (owner decision **D16**): run on the laptop (Windows 11 + WSL Ubuntu-24.04,
RTX 4050 Laptop 6 GB, partial GPU offload for every local model at 8K context); G1 digests and serving settings
(num_ctx 8192, temperature 0, seed 42, num_predict ≤ 1024, thinking off); no machine mixing inside a comparison;
offload recorded per run; timing descriptive only. Sol is hosted (gpt-6.1-sol, existing session, no new consent).
Lab results (G1 and the 11-17 Gazebo runs) are not hardware-matched to these laptop results.

- [ADDENDUM_F1.md](ADDENDUM_F1.md): F1 catalogue wording (W1/W2) for Qwen, with a Sol guard.
- [ADDENDUM_PARITY.md](ADDENDUM_PARITY.md): parity integration, Phases A to C.
- [ADDENDUM_GAZEBO_D.md](ADDENDUM_GAZEBO_D.md): Gazebo D, fresh cases, multi-model.

Future work: reuse Levinson's original-ROSA baseline harness to add a stock-ROSA arm to the macro comparison.
