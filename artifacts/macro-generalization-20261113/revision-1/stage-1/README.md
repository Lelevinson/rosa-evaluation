# G1 Stage 1 — current progress

Updated: **2026-11-14**.

**COMPLETE: scripted engineering gate passed. Stage 2 has not started.**

Read [STAGE1_REPORT.md](STAGE1_REPORT.md) for the shareable report and
[analysis.json](analysis.json) for counts and structural rows. The machine
checkpoint is [status.json](status.json).

- 9/9 observer/world unit tests.
- 20/20 structural controls, then 112/112 fixture controls.
- 132/132 local and persisted Phoenix trace audits; 5,544 matching span IDs.
- 132 actor-only scorer rejections and 276 counterfactual scoring checks.
- 700 independent evaluator reads excluded from 372 agent-native attempts.
- 2,186 protected historical files and 13 pre-run frozen files unchanged.
- Zero live inference requests, OAuth operations, Gazebo actions or uploads.

This is an AI-authored exploratory study without independent teammate authorship
or semantic-novelty review. Scripted selection is an oracle. These results
validate execution and scoring plumbing; they do not establish model accuracy,
generalization, or real-model savings. The observer shares an authoritative
mock world with the actor but has separate channels, state and records.

The next gate is owner-confirmed **Sol dev**, with 18 cases in two conditions
(36 trials) and a proposed maximum of 291 charged requests including reserve.
It is not running. The later held-out and first-turn probe stages retain their
separate confirmation gates. No stage automatically advances from this result.

Earlier Stage 0, revision and authorship records are historical sealed snapshots;
their old pending status is preserved. This file reflects the completed Stage 1.
