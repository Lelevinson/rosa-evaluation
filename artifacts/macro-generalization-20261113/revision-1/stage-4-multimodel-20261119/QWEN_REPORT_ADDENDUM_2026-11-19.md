# Qwen report addendum: exploratory write-task split and prediction IDs

Date: **2026-11-19**. Retrospective descriptive review. Original reports, raw trials, scores and ZIPs remain unchanged.

## Prediction-ID discrepancy in the extension request

The requested relabeling is not supported by the adopted freeze. The owner-approved
[November 14 amendment](../stage-3/predictions-amendment-20261114/PREDICTIONS_AMENDMENT_2026-11-14.md)
defines **P3 = dropped horizon-dependent reliability**, **P4 = Qwen selection versus catalogue size**.
P1-prime is the Sol absolute-call-saving contrast across native depths; P2 is native-operation equality.
The older prediction numbering differs and was explicitly superseded before held-out execution.

Thus the original Qwen report's “P3 dropped; P4 catalogue probe not run” is correct for revision1.
It will not be changed to the older numbering. The amendment SHA256 is
f103e6e49c4e6596399418efb21513679ff00b77d9491c66e41c34e98b14325e.
The scorer SHA256 remains90b0edd6d898ac749d121de29197a669593e022160503414413e0126766e8e4d.

## Post-hoc subgroup split

“Write-bearing” here means the three write cases and one partial-write fault per domain.
Missing-prerequisite requests are in the other group, exactly as specified for this hypothesis;
this classification must not be changed after additional model outcomes are seen.

| Known-goal group | Cases per arm | Primitive passes | Macro passes | Macro-minus-primitive |
|---|---:|---:|---:|---:|
| Write and partial-write fault | 8 | 2 | 6 | +4 |
| Inspection, missing prerequisite, unavailable source | 28 | 24 | 24 | 0 |
| All known-goal cases | 36 | 26 | 30 | +4 |

This is a **post-hoc Qwen pattern**, not an independently confirmed finding, a new frozen P-prediction,
or proof of its mechanism. Equal aggregate performance in the other28 cases does not mean the
same cases passed: paired outcomes must remain visible. Case groups are small and related.

The external assessment's approximately0.13 Fisher p-value treats arms as independent;
these trials are paired and grouped. The whole known-goal discordant count is5 macro-only
and1 primitive-only (exact ungrouped sign-test p=0.21875). Neither calculation establishes
a reliability benefit, and neither is a substitute for group-aware uncertainty.

## What the extension can test

H-write is now specified before the additional backend trials. Every new backend remains
**exploratory, added after Sol and Qwen results**, on the same already examined AI-authored cases.
It tests backend/model generality on this catalogue, not independent case generalization.

The owner confirmed a write-arm floor/ceiling override: any write-bearing arm with0/8 or8/8
makes H-write Uninformative; otherwise compare raw pass-count differences between the8 and28 groups.
Incomplete/censored comparisons remain Uninformative. The fixed new-model sample is
Ministral, Granite, then Llama; no performance-based exclusions or substitutions.

## Remaining limits

The lab's roughly90 decode tokens/s versus the earlier laptop measurement is useful context.
These workloads and execution configurations are not a controlled hardware experiment.
It does not quantify how much of the old hosted/local task-time gap was caused by VRAM/offload.

Qwen's four new clarification ratings remain outstanding; three primary outcomes are undecided,
and one already fails structural/runtime checks. This addendum creates no ratings or final verdict.
The new pooled packet will be separate from Qwen Batch B and from the completed Sol review.
