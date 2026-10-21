# Original-spec policy comparison

This package is separate from the frozen movement experiment in `phase4/` and
its legacy fixed dependency bundle. It implements the original bounded
prefix/residual selection core for a small grounded ROSA information catalogue,
plus greedy and strong amortized batching. It does not implement a production
ROSA Runnable or model-generated manifests.

The frozen protocol is
[STAGE4_POLICY_PROTOCOL_2026-10-21.md](../../docs/STAGE4_POLICY_PROTOCOL_2026-10-21.md).
Artifacts and the detailed report are under
[`artifacts/stage4-policy-20261021/`](../../artifacts/stage4-policy-20261021/).

In the prepared research environment, from the evaluation checkout:

```bash
python -B -m experiments.jtvr_policy.campaign verify
python -B -m experiments.jtvr_policy.report
```

`campaign prepare` and `campaign run` refuse overwrite. Do not rerun the real
probe into an existing directory. Real probes create only isolated parameter
nodes in domain 173 and stop their server/daemon on exit. They never expose robot
actuators. Raw outputs, server-counted requests, frozen inputs, per-episode
decisions, parsers, evidence, independent read-back checks and limitations are
preserved. No model requests or OAuth session are used in this tier.
