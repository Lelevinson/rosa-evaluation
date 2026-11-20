# G1 — current status after the authorship decision

Updated: **2026-11-13**.

**The owner selected the AI-authored-case fallback.** G1 may use the accurately
labeled AI-authored draft cases without obtaining the originally required
teammate contribution. The original independent-authorship criterion was not met;
it has been **replaced explicitly for this exploratory study**. No independent
author or semantic-novelty review is claimed.

Required result label: **Exploratory generalization study G1 — AI-authored cases;
no independent teammate authorship or semantic-novelty review.**

The [dated amendment](amendments/ai-authored-20261113/AUTHORSHIP_AMENDMENT.md)
records the decision, limitations and exact scope. The preserved
[Stage0 revision report](README.md), checkpoint and manifests retain the earlier
unmet-gate finding as historical records. This current-status note supersedes
their *pending authorship decision* status, not their technical evidence.

## Current proposal and evidence

- 16 dev and 38 held-out-designated cases, all Codex/AI-authored; no cases changed.
- 6 dev template groups; 13 held-out groups, including **6 ladder groups**.
- Observer separation: 4 test methods covering 8 domain checks passed; 5 additional
  world/transport unit methods passed.
- Both domains registered/opened through the public API in 4 constructor checks,
  without source changes. Actual model-turn counts remain **not recorded**;
  Stage1 structural controls and full local/Phoenix audits have not run.
- Current proposed caps: 259 Sol dev, 611 held-out/backend, 117 probe/backend.
  These remain proposals, not confirmed inference allowances.

## Before Stage1

The authorship decision is settled. Thresholds, suffix, counts and ceilings still
need their explicit stage-gate confirmation. The latest review proposes adding
one dev partial-write case/domain (18 dev total, proposed cap291 with reserve),
restoring an explicit±25% native-operation ratio threshold/depth, and checking
that the scorer refuses actor-only truth and observer reads are separately metered.
Those changes were not silently folded into the authorship fallback.

No new model experiment, control campaign or optional catalogue extension has
started. Existing OAuth file presence does not establish provider validity or
quota. Existing source and experiments remain unchanged. No commit or upload
was made.

For detailed design: [revision report](README.md),
[observer proof](OBSERVER_SEPARATION.md),
[threshold proposal](PREDICTIONS_AND_THRESHOLDS.md),
[budgets and estimates](BUDGETS_AND_ESTIMATES.md).
